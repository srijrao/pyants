"""
Ant Colony Module for Ant Colony Simulation

This module defines the Anthill class which represents the home base for the ant colony.
The anthill serves as the origin point for ants and the destination for food collection.
"""

import settings
import random

class Anthill:
    """
    Represents an anthill in the simulation.
    
    The anthill is the central structure of the ant colony, serving as both
    the spawning point for new ants and the destination for ants carrying food.
    It can be positioned at specific coordinates or randomly placed within the
    simulation boundaries.

    Attributes:
        position (list): [x, y] coordinates of the anthill
        size (int): Diameter of the anthill
        color (tuple): RGB color value for rendering (white)
        visual_packet (dict): Cached visual rendering information
    """

    def __init__(self, position=None, size=settings.Anthill_size):
        """
        Initialize an anthill.

        Args:
            position (list, optional): [x, y] coordinates for the anthill.
                If None, position is set randomly within simulation bounds.
            size (int, optional): Diameter of the anthill in pixels.
                Defaults to the size defined in settings.
        """
        if position is None:
            self.randompositionsetter()
        else:
            self.position = position
        self.size = size
        self.color = settings.WHITE
        self.visual_packet = None
            
    def randompositionsetter(self):
        """
        Set a random position for the anthill within simulation bounds.
        
        The position is set with a barrier from the edges equal to the anthill size
        to prevent the anthill from being partially off-screen.
        """
        barrier = settings.Anthill_size
        position = [
            random.randint(barrier, settings.width - barrier),
            random.randint(barrier, settings.height - barrier),
        ]
        self.position = position

    def visual(self):
        """
        Prepare the visual representation data for rendering.

        Returns:
            dict: Contains position, size, and color information for rendering.
        """
        self.visual_packet = {"position": self.position, "size": self.size, "color": self.color}
        return self.visual_packet
