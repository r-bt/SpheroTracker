import cv2
from util import Color
import numpy as np

class BaseFilter(object):
    def get_mask(self, img):
        return img


class ColorFilter(BaseFilter):
    def __init__(self):
        self.lower = Color()
        self.upper = Color()

    def hsv_lower_filter(self, data_size=np.uint8):
        return ColorFilter.to_np_array(self.lower.hsv, data_size)

    def hsv_upper_filter(self, data_size=np.uint8):
        return ColorFilter.to_np_array(self.upper.hsv, data_size)

    @staticmethod
    def to_np_array(color_tuple, data_size):
        return np.array(list(color_tuple), data_size)

    def get_mask(self, img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_lower_limit = self.hsv_lower_filter()
        hsv_upper_limit = self.hsv_upper_filter()
        return cv2.inRange(hsv_img, hsv_lower_limit, hsv_upper_limit)
    
class FilterSpheroBlueCover(ColorFilter):
    def __init__(self):
        ColorFilter.__init__(self)
        self.lower.hsv = (100, 100, 100)
        self.upper.hsv = (120, 255, 255)

class Tracker():

    def __init__(self) -> None:
        self.cam = cv2.VideoCapture(-1)

        if not self.cam.isOpened():
            self.cam.open()

    def get_video_frame(self):
        _, frame = self.cam.read()
        return frame
    
    def track_objects(self):
        image = self.get_video_frame()

        blue_filter = FilterSpheroBlueCover()

        mask = blue_filter.get_mask(image)

        cv2.imshow("img_no_mask", image)
        cv2.imshow("img", mask)
    
if __name__ == "__main__":
    tracker = Tracker()

    while True:
        tracker.track_objects()
        cv2.waitKey(5)


