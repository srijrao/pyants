"""
Food Source Module for Ant Colony Simulation

This module defines the Food class which represents food sources that ants can discover
and collect from in the simulation. Food sources are stationary objects that ants
can locate and interact with.
"""

import settings
import random

class Food:
    """
    Represents a food source in the ant colony simulation.
    
    Food sources are stationary objects that ants can find and collect from.
    They are positioned either at specified coordinates or randomly placed
    within the simulation boundaries.

    Attributes:
        size (int): The diameter of the food source (2x the anthill size)
        position (list): [x, y] coordinates of the food source
        color (tuple): RGB color value for rendering (green)
        visual_packet (dict): Cached visual rendering information
    """

    def __init__(self, position=None):
        """
        Initialize a food source.

        Args:
            position (list, optional): [x, y] coordinates for the food source.
                If None, position is set randomly within simulation bounds.
        """
        self.size = settings.Anthill_size * 2
        if position is None:
            self.randompositionsetter()
        else:
            self.position = position
        self.color = settings.GREEN
        self.visual_packet = None
        
    def visual(self):
        """
        Prepare the visual representation data for rendering.

        Returns:
            dict: Contains position, color, and size information for rendering.
        """
        self.visual_packet = {
            "position": self.position,
            "color": self.color,
            "size": self.size,
        }
        return self.visual_packet

    def randompositionsetter(self):
        """
        Set a random position for the food source within simulation bounds.
        
        The position is set with a barrier from the edges equal to the food size
        to prevent the food from being partially off-screen.
        """
        barrier = self.size
        position = [
            random.randint(barrier, settings.width - barrier),
            random.randint(barrier, settings.height - barrier),
        ]
        self.position = position
