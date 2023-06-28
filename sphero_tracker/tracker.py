import cv2
import time
from util import Vector2D, Color
from trackable_object import TrackableObject

class Tracker():
    """
    Accepts trackable objects and tracks them in a video stream
    """

    def __init__(self) -> None:
        self.cam = cv2.VideoCapture(-1)

        if not self.cam.isOpened():
            self.cam.open(-1)

        self._masks = None

    def track_objects(self, trackable_objects: list[TrackableObject]):
        image = self._get_video_frame()
        timestamp = time.time()

        for trackable_object in trackable_objects:
            x,y = self._find_trackable_in_image(image, trackable_object)

            trackable_object.add_tracking(Vector2D(x, y), timestamp)

            trackable_object.draw_name(self._masks)
            trackable_object.draw_name(image)
            trackable_object.draw_graphics(image)

        return image 

    """
    Private class methods
    """

    def _get_video_frame(self):
        """
        Returns the latest frame from camera
        """
        _, frame = self.cam.read()
        return frame
    
    def _find_trackable_in_image(self, image, trackable_object, ADD_MASK=True):
        mask = trackable_object.filter.get_mask(image)

        if ADD_MASK:
            self._add_mask(mask)

        x,y = self.find_largest_contour_in_image(mask)

        return x,y

    def _add_mask(self, mask):
        if self._masks is None:
            self._masks = mask
        else:
            self._masks = self.merge_masks(self._masks, mask)
    
    def clear_masks(self):
        self._masks = None
    
    """
    Static Methods to support functions
    """
    
    @staticmethod
    def find_largest_contour_in_image(img) -> tuple[int, int]:
        contours = Tracker.find_all_contours(img)
        largest_contour = Tracker.find_largest_contour(contours)

        cx, cy = Tracker.get_contour_coordinates(largest_contour)

        return cx, cy

    @staticmethod
    def find_all_contours(img):
        contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    @staticmethod
    def find_largest_contour(contours):
        max_area = 0
        max_contour = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if max_area < area:
                max_area = area
                max_contour = contour
        return max_contour
    
    @staticmethod
    def get_contour_coordinates(contour) -> tuple[int, int]:
        cx, cy = None, None
        if contour is not None:
            try:
                m = cv2.moments(contour)
                cx, cy = int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])
            except ZeroDivisionError:
                pass
        return cx, cy
    
    @staticmethod
    def merge_masks(mask_a, mask_b):
        return cv2.bitwise_or(src1=mask_a, src2=mask_b)


