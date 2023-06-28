from tracking_sample import TrackingSample
from graphics import ImageGraphics as Ig, DrawError
from util import Color, Vector2D
import pdb

class TrackableObject():
    """
    A single trackable object.

    Holds the filter to use for tracking the object, samples tracked, and methods for handling data
    """

    def __init__(self, name="untitled") -> None:
        self.name = name

        # Filter used to find the object
        self.filter = None

        #Tracking
        self.tracking_samples = []

        #Config
        self.max_samples_in_memory = 20
        self.max_samples_speed_determination = 1

        self.is_moving_threshold = 1.0

        #Graphics 
        self.color = Color((255, 0, 0))
        self.direction_length = 20
    
    def add_tracking(self, pos, timestamp):
        sample = TrackingSample()
        self.last_tracking_successful = False
        if pos:
            self.last_tracking_successful = True
            sample.valid = True
        elif not self.store_invalid_samples:
            return
        sample.pos = pos
        sample.timestamp = timestamp
        self._save_tracking(sample)

    def _save_tracking(self, tracking_sample: TrackingSample) -> None:
        """
        Add a new tracking sample to saved samples

        :param tracking_sample
        """
        self.tracking_samples.insert(0, tracking_sample)
        try:
            self.tracking_samples[0].prev_sample = self.tracking_samples[1]
        except IndexError:
            pass
        if len(self.tracking_samples) > self.max_samples_in_memory:
            self.tracking_samples.pop(-1)
            self.tracking_samples[-1].prev_sample = None

    def get_valid_samples(self, max_samples=-1):
        """
        Return a list of the all the valid samples currently stored in the traceable.

        :param max_samples: The maximum number of samples to return
        :type max_samples: int
        :return: list of the valid samples
        :rtype: list
        """
        valid_samples = []
        for tracking_sample in self.tracking_samples:
            if tracking_sample.valid:
                valid_samples.append(tracking_sample)
                max_samples -= 1
            if max_samples == 0:
                break
        return valid_samples


    @property
    def pos(self):
        """
        Return the last tracked position. Position is set to none if the tracking was not successful
        Returns None if objects has now tracked samples

        :return: Vector2D of last tracked position (x and y are set not None if object was not succesfully tracked)
        :rtype: Vector2D or None
        """
        if self.tracking_samples and self.last_tracking_successful:
            return self.tracking_samples[0].pos
        return None
    
    @property 
    def direction(self):
        """
        Returns a vector with the tracked direction of the object
        :return: The direction vector
        :rtype: Vector2D
        """
        samples = self.get_valid_samples(max_samples=5)
        num_samples = len(samples)
        direction = Vector2D(0.0,0.0)
        
        for sample in samples:
            try:
                direction += sample.distance_vector()
            except (TypeError, AttributeError):
                num_samples -= 1
        
        if not num_samples:
            return Vector2D(None, None)
        
        ## COME BACK AND FIGURE OUT WHAT THIS DOES!
        try:
            direction.angle -= 2*direction.get_offset(samples[0].distance_vector())
        except AttributeError:
            print("ATTR ERROR")
        return direction
    
    @property
    def speed(self):
        """
        Liner speed between the two last successful samples

        :return: The linear speed, None if only one sample
        :rtype: float or None
        """
        speed = 0.0
        samples = self.get_valid_samples(max_samples=self.max_samples_speed_determination)
        num_samples = len(samples)
        try:
            for sample in samples:
                try:
                    speed += sample.speed
                except TypeError as e:
                    num_samples -= 1
            return speed / num_samples
        except ZeroDivisionError:
            return None

    @property
    def is_moving(self):
        """
        Returns true if the tracked movement is larger than the is_moving_threshold.s

        :return: True if moving False else
         :rtype: bool
        """
        try:
            return self.speed >= self.is_moving_threshold
        except:
            return False

    """
    Graphics
    """

    def draw_direction_vector(self, image, pos):
        if self.direction:
            try:
                label = round(self.direction.angle, 2)
                if self.is_moving:
                    vector = self.direction.set_length(self.direction_length)
                    Ig.draw_vector_with_label(image, str(label), pos, vector, self.color)
                Ig.draw_circle(image, pos, 2, self.color)
            except DrawError:
                pass

    def draw_graphics(self, image):
        """
        Draw graphics after tracking

        :param image: The image to draw the image on. (Numpy Vector)
        """
        if self.pos and self.pos.is_valid:
            self.draw_direction_vector(image, self.pos)

    def draw_name(self, image):
        """
        Draws the name of the object to the given image at the objects latest successfully traced position

        :param image:
        """
        try:
            Ig.draw_text(image, self.name, self.pos + (15, 5), 0.35, Color((255, 255, 255)))
        except TypeError:
            pass

    
    


    