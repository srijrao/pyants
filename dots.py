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
        # Initialize color attribute first since setup() uses it
        self.color = None
        self.reset(position, type, time)

    def reset(self, position=[0, 0], type="to home", time=0):
        """
        Reset the dot's state for reuse (supports object pooling).

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
        self.size = settings.dot_size
        
        # Set color based on type
        if self.type == "to food":
            self.color = settings.PURPLE
        elif self.type == "to home":
            self.color = settings.WHITE
        else:
            self.color = settings.BLACK
            
        # Initialize visual packet cache
        self.visual_packet = {
            "position": self.position,
            "size": self.size,
            "color": (self.color[0], self.color[1], self.color[2], 255),
        }

    def visual(self):
        """
        Prepare the visual representation data for rendering.

    Returns:
            dict: Contains position, size, and RGBA color information for rendering.
        """
        self.visual_packet["color"] = (
            self.color[0], 
            self.color[1], 
            self.color[2], 
            255
        )
        return self.visual_packet
