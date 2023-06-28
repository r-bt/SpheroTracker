from util import Vector2D

class TrackingSample():

    def __init__(self) -> None:
        self.pos = None
        self.timestamp = None
        self.valid = False

        self.prev_sample = None
    
    def distance_vector(self) -> Vector2D:
        """
        :return: Vector2D
        """
        try:
            return self.pos - self.prev_sample.pos
        except (AttributeError, TypeError):
            pass
    
    @property
    def speed(self):
        """
        Calculates the linear speed from this sample to the given sample
        :return: The given speed in pixels per second
        :rtype: float
        """
        try:
            distance = self.distance_vector().magnitude
            time_diff = abs(self.timestamp - self.prev_sample.timestamp)
            return distance / time_diff
        except (ZeroDivisionError, AttributeError, ValueError) as e:
            return None