"""
Pheromone Dot Module for Ant Colony Simulation

This module defines the Dot class which represents pheromone trails that ants
use to communicate and navigate. Ants leave these dots as markers to indicate
paths to food or back to the anthill.
"""

import settings

class Dot:
    """
    Represents a pheromone marker in the ant colony simulation.
    
    Pheromone dots are temporary markers that ants leave behind to communicate
    with other ants. They can indicate paths to food sources ('to food' type)
    or paths back to the anthill ('to home' type). Dots gradually fade over
    time and eventually disappear.

    Attributes:
        position (list): [x, y] coordinates of the dot
        type (str): Type of pheromone - either 'to home' or 'to food'
        time (float): Time when the dot was created
        size (int): Size of the dot in pixels
        timeleft (int): Remaining lifetime of the dot in frames
        active (bool): Whether the dot is still valid
        color (tuple): RGB color based on type (purple for 'to food', white for 'to home')
        visual_packet (dict): Cached visual rendering information
    """

    def __init__(self, position=[0, 0], type="to home", time=0):
        """
        Initialize a pheromone dot.

        Args:
            position (list, optional): [x, y] coordinates for the dot.
                Defaults to [0, 0].
            type (str, optional): Type of pheromone marker - 'to home' or 'to food'.
                Defaults to 'to home'.
            time (float, optional): Time when the dot was created.
                Used to determine the newest dot. Defaults to 0.
        """
        self.position = position
        self.type = type
        self.time = time
        self.setup()

    def setup(self):
        """
        Initialize the dot's properties.

        Sets up the dot's size, lifetime, activity status, and color based on its type.
        The color is purple for 'to food' dots and white for 'to home' dots.
        """
        self.size = settings.dot_size
        self.timeleft = settings.dot_time
        self.active = True
        if self.type == "to food":
            self.color = settings.PURPLE
        elif self.type == "to home":
            self.color = settings.WHITE
        else:
            self.color = settings.BLACK
        
    def update(self):
        """
        Update the dot's state.

        Decrements the dot's remaining lifetime and deactivates it when
        the lifetime reaches zero.
        """
        self.timeleft -= 1
        if self.timeleft <= 0:
            self.active = False

    def get_alpha(self):
        """
        Calculate the dot's transparency based on its remaining lifetime.

        Returns:
            int: Alpha value (0-255) where 255 is fully opaque and 0 is fully transparent.
                The dot becomes more transparent as it gets closer to disappearing.
        """
        return int((self.timeleft / settings.dot_time) * 255)

    def visual(self):
        """
        Prepare the visual representation data for rendering.

        Returns:
            dict: Contains position, size, and RGBA color information for rendering.
                The alpha channel is calculated based on remaining lifetime.
        """
        self.visual_packet = {
            "position": self.position,
            "size": self.size,
            "color": (self.color[0], self.color[1], self.color[2], self.get_alpha()),
        }
        return self.visual_packet
