import subprocess
from subprocess import CalledProcessError
from typing import TypedDict, Literal, Optional
import re

class V4L2Control(TypedDict):
    """
    A control from v4l2
    """

    name: str
    type: Literal['int', 'bool', 'menu']
    min: Optional[int]
    max: Optional[int]
    default: int
    value: int

class C920:
    """
    An interface to control a Logitech C920 webcam

    :param device: the address of the device to control
    """

    _control_regex = b"([^\s]*)\s[^\s]*\s\(([^\s]*)\)\s*:\s(?:min=(-?\d*)\s)?(?:max=(-?\d*)\s)?(?:step=-?\d*\s)?default=(-?\d*)\svalue=(-?\d*)"

    def __init__(self, device: str):
        self.device = device

    def __set_control(self, param: str, value: int):
        """
        Sets a parameter using v4l2-ctl command line executable

        :param param: the name of the parameter to be set
        :param value: the value to set the parameter to
        """
        try:
            subprocess.check_output(["v4l2-ctl", "-d", self.device, f"--set-ctrl={param}={value}"])
        except CalledProcessError as e:
            print("Process error")

    def __get_control(self, param: str) -> V4L2Control:
        """
        Gets the value of a parameter

        :param param: the name of the param to get
        """
        result = subprocess.check_output(["v4l2-ctl", "-d", self.device, f"--get-ctrl={param}"]).decode("utf-8")
        control_match = re.match(self._control_regex, result)
        if control_match:
            control_info = {
                "name": control_match.group(1),
                "type": control_match.group(2),
                "min": int(control_match.group(3)) if control_match.group(3) else None,
                "max": int(control_match.group(4)) if control_match.group(4) else None,
                "default": int(control_match.group(5)),
                "value": int(control_match.group(6))
            }
            return control_info
        else:
            raise ValueError(f"Control '{param}' not found")

    def get_controls(self) -> list[V4L2Control]:
        """
        Returns data about all available controls
        """
        result = subprocess.check_output(["v4l2-ctl", "-d", self.device, f"--list-ctrls"])
        matches = re.finditer(self._control_regex, result, re.MULTILINE)
        controls = []
        for match in matches:
            controls.append({
                "name": match.group(1).decode("utf-8"),
                "type": match.group(2).decode("utf-8"),
                "min": int(match.group(3)) if match.group(3) else None,
                "max": int(match.group(4)) if match.group(4) else None,
                "default": int(match.group(5)),
                "value": int(match.group(6))
            })
        return controls

    """
    FOCUS METHODS
    """

    def enable_auto_focus(self):
        """
        Enables auto focus
        """
        self.__set_control("focus_automatic_continuous", 1)
    
    def disable_auto_focus(self):
        """
        Disables auto focus
        """
        self.__set_control("focus_automatic_continuous", 0)

    def set_focus(self, value: int):
        """
        Sets the focus value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Focus value must be between 0 and 255")
        self.__set_control("focus_absolute", value)
    
    """
    GAIN METHODS
    """

    def set_gain(self, value: int):
        """
        Sets the gain value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Gain value must be between 0 and 255")
        self.__set_control("gain", value)

    """
    EXPOSURE METHODS
    """

    def set_exposure(self, value: int):
        """
        Sets the exposure value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Exposure value must be between 0 and 255")
        self.__set_control("exposure_absolute", value)

    def enable_auto_exposure(self):
        """
        Enables auto exposure
        """
        self.__set_control("exposure_auto", 3)
    
    def disable_auto_exposure(self):
        """
        Disables auto exposure
        """
        self.__set_control("exposure_auto", 1)

    """
    ADDITIONAL CONTROLS
    """

    def set_brightness(self, value: int):
        """
        Sets the brightness value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Brightness value must be between 0 and 255")
        self.__set_control("brightness", value)

    def set_contrast(self, value: int):
        """
        Sets the contrast value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Contrast value must be between 0 and 255")
        self.__set_control("contrast", value)

    def set_saturation(self, value: int):
        """
        Sets the saturation value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Saturation value must be between 0 and 255")
        self.__set_control("saturation", value)

    def enable_auto_white_balance(self):
        """
        Enables auto white balance
        """
        self.__set_control("white_balance_automatic", 1)
    
    def disable_auto_white_balance(self):
        """
        Disables auto white balance
        """
        self.__set_control("white_balance_automatic", 0)

    def set_white_balance_temperature(self, value: int):
        """
        Sets the white balance temperature value

        :param value: an int between 2000 and 7500
        """
        if value < 2000 or value > 7500:
            raise ValueError("White balance temperature value must be between 2000 and 7500")
        self.__set_control("white_balance_temperature", value)

    def set_sharpness(self, value: int):
        """
        Sets the sharpness value

        :param value: an int between 0 and 255
        """
        if value < 0 or value > 255:
            raise ValueError("Sharpness value must be between 0 and 255")
        self.__set_control("sharpness", value)

    def set_backlight_compensation(self, value: int):
        """
        Sets the backlight compensation value

        :param value: an int between 0 and 1
        """
        if value < 0 or value > 1:
            raise ValueError("Backlight compensation value must be between 0 and 1")
        self.__set_control("backlight_compensation", value)

    def set_auto_exposure(self, value: int):
        """
        Sets the auto exposure value

        :param value: an int between 0 and 3
        """
        if value < 0 or value > 3:
            raise ValueError("Auto exposure value must be between 0 and 3")
        self.__set_control("auto_exposure", value)

    def set_exposure_time_absolute(self, value: int):
        """
        Sets the exposure time absolute value

        :param value: an int between 3 and 2047
        """
        if value < 3 or value > 2047:
            raise ValueError("Exposure time absolute value must be between 3 and 2047")
        self.__set_control("exposure_time_absolute", value)

    def enable_exposure_dynamic_framerate(self):
        """
        Enables exposure dynamic framerate
        """
        self.__set_control("exposure_dynamic_framerate", 1)
    
    def disable_exposure_dynamic_framerate(self):
        """
        Disables exposure dynamic framerate
        """
        self.__set_control("exposure_dynamic_framerate", 0)

    def set_pan(self, value: int):
        """
        Sets the pan value

        :param value: an int between -36000 and 36000
        """
        if value < -36000 or value > 36000:
            raise ValueError("Pan value must be between -36000 and 36000")
        self.__set_control("pan_absolute", value)

    def set_tilt(self, value: int):
        """
        Sets the tilt value

        :param value: an int between -36000 and 36000
        """
        if value < -36000 or value > 36000:
            raise ValueError("Tilt value must be between -36000 and 36000")
        self.__set_control("tilt_absolute", value)

    def set_zoom(self, value: int):
        """
        Sets the zoom value

        :param value: an int between 100 and 400
        """
        if value < 100 or value > 400:
            raise ValueError("Zoom value must be between 100 and 400")
        self.__set_control("zoom_absolute", value)
