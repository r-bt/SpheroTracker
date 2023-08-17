import cv2
from VideoStream import VideoStream
from tracker_filters import ColorFilter
import multiprocessing
import threading
import numpy as np
import imutils
from similari import Sort, BoundingBox, PositionalMetricType
from collections import deque
import time
import server
import uuid

class Tracker():
    """
    Accepts trackable objects and tracks them in a video stream
    """

    def __init__(self) -> None:
        # Opens stream and set some properites
        self.stream = VideoStream(-1).start()

        self._outputFrame = None
        self._detectFrame = None
        self._lock = threading.Lock()
        self._tracking = False

        self._trackable_objects = 0

        self._maxlen = 1
        self._manager = multiprocessing.Manager()
        self._positions = self._manager.list()
        self._lock = self._manager.Lock()

        # Variables for inter-thread communication
        self._outputFrame = None
        self._image_lock = threading.Lock()
        self._tracking_thread = None

        # Get scale factors
        frame = self._get_processed_frame()[1]
        self.height, self.width = frame.shape[:2]

        self.scale_factor = 2.0 / min(self.width, self.height)

        self._tracking_process = None
    
    def __del__(self):
        self.stop_tracking_objects()

    def start_tracking_objects(self, run_server=False):
        self._tracking = True

        self._tracking_process = multiprocessing.Process(target=self._setup_process, args=(run_server,))
        self._tracking_process.daemon = True
        self._tracking_process.start()
    
    def stop_tracking_objects(self):
        self._tracking = False

        if self._tracking_process:
            self._tracking_process.join()
    
    def get_current_frame(self):
        with self._image_lock:
            if self._outputFrame is None:
                return
            
            (flag, encodedImage) = cv2.imencode(".jpg", self._outputFrame)
            if not flag:
                return
        
        return encodedImage
    
    def set_trackable_count(self, count: int):
        self._trackable_objects = count

    def get_positions(self):
        with self._image_lock:
            try:
                pos = self._positions.pop()
                return pos
            except:
                return None
       
    def find_color(self, color):
        for i in range(0,10):
            frame = self.stream.read()

            color_filter = ColorFilter(color)

            mask = color_filter.get_mask(frame)

            cv2.imwrite("images/frame{i}.jpg".format(i=i), frame)
            cv2.imwrite("images/mask{i}.jpg".format(i=i), mask)

            contours = self._find_all_contours(mask)
            
            if (len(contours) == 0):
                continue
            
            contour = contours[0]

            x,y,w,h = cv2.boundingRect(contour)
            box = BoundingBox(x, y, w, h).as_xyaah()

            return box

        raise RuntimeError("No contours found!")

    """
    Private class methods
    """

    def _detect_objects(self, frame):
        contours = self._find_all_contours(frame)
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

        endIndex = min(self._trackable_objects, len(contours))

        dets = []

        for contour in contours[:endIndex]:
            x,y,w,h = cv2.boundingRect(contour)
            det = np.array([x,y,w,h])
            dets.append(det)
        
        return np.array(dets)

    def _setup_process(self, run_server=False):
        self._tracking_thread = threading.Thread(target=self._track_objects)
        self._tracking_thread.daemon = True
        self._tracking_thread.start()

        if run_server:
            server.set_callback(self.get_current_frame)
            server.start_server()

    def _track_objects(self):
        sort_tracker = Sort(shards=4, bbox_history=1, max_idle_epochs=50, method=PositionalMetricType.iou(threshold=0.1))

        while self._tracking:

            frame, thresh = self._get_processed_frame()   

            dets = self._detect_objects(thresh)

            boxes = []
            for (x,y,w,h) in dets:
                box = BoundingBox(x, y, w, h).as_xyaah()
                boxes.append((box, None))
            
            frame = self._update_tracker(sort_tracker, boxes, frame)

            with self._image_lock:
                self._outputFrame = frame.copy()
                
    def _update_tracker(self, tracker, boxes, frame = None):
        active_tracks = tracker.predict(boxes)
        idle_tracks = tracker.idle_tracks()
        active_tracks.extend(idle_tracks)

        pos = np.empty((len(active_tracks), 3))

        for i, p in enumerate(active_tracks):
            box = p.predicted_bbox.as_ltwh()

            center_x, center_y = self._normalize_coordinates(box.left + box.width / 2, box.top + box.height / 2)

            pos[i] = np.array([center_x, center_y, p.id])

            if frame is not None:
                cv2.rectangle(frame,
                    (int(box.left), int(box.top)),
                    (int(box.left + box.width), int(box.top + box.height)),
                    color=(0, 255, 0), thickness=2)

                # cv2.putText(frame, '#{}'.format(p.id), (int(box.left), int(box.top) - 10),
                #     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

                print("Put text!")

                cv2.putText(frame, '#{}'.format(time.time()), (int(box.left), int(box.top) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                cv2.imwrite("images/{uuid}.jpg".format(uuid=uuid.uuid1()), frame)
                
        sorted_indices = np.argsort(pos[:, 2])

        with self._lock:
            if len(self._positions) >= self._maxlen:
                self._positions.pop(0)
            self._positions.append(pos[sorted_indices])

        return frame

    def _get_processed_frame(self):
        now = time.time()
        frame = self.stream.read()
        cv2.imwrite("images/frame.jpg", frame)
        elapsed = time.time() - now
        if(elapsed > 1):
            print("Took too long to read frame: {0}".format(elapsed))

        return self._process_frame(frame)

    def _normalize_coordinates(self, x, y):
        normalized_x = self.scale_factor * (x - self.width / 2)
        normalized_y = self.scale_factor * (y - self.height / 2)
        return normalized_x, -normalized_y

    def _normalize_bbox(self, bbox):
        x, y, w, h = bbox
        normalized_x, normalized_y = self._normalize_coordinates(x, y)
        normalized_w = self.scale_factor * w
        normalized_h = self.scale_factor * h
        return normalized_x, normalized_y, normalized_w, normalized_h
    
    """
    Static Methods to support functions
    """

    @staticmethod
    def _find_all_contours(img):
        contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    @staticmethod
    def _process_frame(frame):
        frame = imutils.resize(frame, width=500)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)

        cv2.imwrite("frame.jpeg", thresh)

        return frame, thresh


