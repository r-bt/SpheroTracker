from threading import Thread
import cv2
import time

class VideoStream:

    def __init__(self, device):
        self.stream = cv2.VideoCapture(device)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.stream.isOpened():
            self.stream.open(device)
        
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False
        self.FPS = 1/30
    
    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()
            time.sleep(self.FPS)
        
    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

    

    
    

