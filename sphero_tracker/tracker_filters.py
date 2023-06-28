import numpy as np
import cv2
import colorsys

from util.color import Color


class BaseFilter():
    def get_mask(self, img):
        return img


class ColorFilter(BaseFilter):
    def __init__(self, rgb):
        hsv = colorsys.rgb_to_hsv(*rgb)
        self.lower = Color()
        self.lower.hsv = [hsv[0] * self.lower.max_deg_value - 10, 100, 100]
        self.upper = Color()
        self.upper.hsv = [hsv[0] * self.upper.max_deg_value + 10, 255, 255]

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
