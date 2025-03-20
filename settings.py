"""
Global Settings for the Ant Colony Simulation

This module contains all the global configuration settings for the ant colony simulation,
including display settings, colors, and simulation parameters.

Display Settings:
    - width: Screen width in pixels
    - height: Screen height in pixels
    - targetfps: Target frames per second for the simulation
    - name: Window title

Colors (RGB):
    - WHITE: Used for general UI elements and anthill
    - BROWN: Background color
    - GREEN: Food color
    - RED: (Currently unused)
    - PURPLE: Color for "to food" pheromone dots
    - BLACK: Default color

Simulation Parameters:
    - dot_size: Size of pheromone dots in pixels
    - dot_time: Lifetime of pheromone dots in frames
    - collision_distance: Distance threshold for collision detection
    - ant_speed: Movement speed of ants
    - Anthill_size: Size of anthill in pixels
"""

width = 800
height = 600
targetfps = 60
name = "Pyants"
WHITE = (245, 245, 245)
BROWN = (42, 21, 3)
GREEN = (8, 113, 57)
RED = (184, 13, 20)
PURPLE = (154, 11, 160)
BLACK = (10, 10, 10)
dot_size = 2
dot_time = 1000
collision_distance = 10
ant_speed = 2
Anthill_size = 10
