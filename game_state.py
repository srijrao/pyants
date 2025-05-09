"""
Game State Module for Ant Colony Simulation

This module manages the core game state and main loop, coordinating between all other modules.
"""

import pygame
import sys
import json
import random
import settings
from graphics import Graphics
from input_handler import InputHandler
from entity_manager import EntityManager
from spatial_grid import SpatialGrid

class Game:
    """Main game class that manages the ant colony simulation."""

    def __init__(self, debug=False):
        pygame.init()
        self.debug = debug
        self.see_dots = debug
        self.getsettings()
        
        # Initialize core attributes
        self.frame_count = 0
        self.start_time = pygame.time.get_ticks()
        self.secs = 0
        self.lastframetime = None
        self.info_lines = []
        self.actual_fps = 1
        self.paused = False
        self.running = True

        # Initialize entity lists
        self.dots = []
        self.ants = []
        self.anthills = []
        self.food = []
        self.onscreen = []

        # Initialize display first
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.name)
        self.clock = pygame.time.Clock()

        # Initialize managers
        self.entity_manager = EntityManager(self)
        self.input_handler = InputHandler(self)
        self.graphics = Graphics(self)
        self.spatial_grid = SpatialGrid(self)

        # Create initial population
        self.entity_manager.create_population()

    def getsettings(self):
        """Get the current settings."""
        try:
            with open("settings.json", "r") as f:
                self.settings_data = json.load(f)
        except FileNotFoundError:
            print("Settings file not found. Using default settings.")
            self.settings_data = {}

        # Load settings with defaults
        self.width = self.settings_data.get("width", settings.width)
        self.height = self.settings_data.get("height", settings.height) 
        self.targetfps = self.settings_data.get("targetfps", settings.targetfps)
        self.popmin = self.settings_data.get("popmin", settings.popmin)
        self.name = self.settings_data.get("name", settings.name)
        self.anthill_size = self.settings_data.get("Anthill_size", settings.Anthill_size)
        self.dot_size = self.settings_data.get("dot_size", settings.dot_size)
        self.dot_time = self.settings_data.get("dot_time", settings.dot_time)
        self.dot_death_rate = self.settings_data.get("dot_death_rate", settings.dot_death_rate)
        self.dot_color_food = self.settings_data.get("PURPLE", settings.PURPLE)
        self.dot_color_home = self.settings_data.get("WHITE", settings.WHITE)
        self.background_color = self.settings_data.get("BROWN", settings.BROWN)
        self.ui_color = self.settings_data.get("WHITE", settings.WHITE)
        self.dot_fade_decay = self.settings_data.get("dot_fade_decay", settings.dot_fade_decay)

        # Update settings data
        self.settings_data.update({
            "width": self.width,
            "height": self.height,
            "targetfps": self.targetfps,
            "popmin": self.popmin,
            "name": self.name,
            "Anthill_size": self.anthill_size,
            "dot_size": self.dot_size,
            "dot_time": self.dot_time,
            "dot_death_rate": self.dot_death_rate,
            "PURPLE": self.dot_color_food,
            "WHITE": self.dot_color_home,
            "BROWN": self.background_color,
            "WHITE": self.ui_color,  # noqa: F601
            "dot_fade_decay": self.dot_fade_decay
        })

        self.savesettings()

    def savesettings(self):
        """Save the current settings to a JSON file."""
        with open("settings.json", "w") as f:
            json.dump(self.settings_data, f, indent=4)
        print("Settings saved to settings.json")

    def timepiece(self):
        """Updates the elapsed time for the environment."""
        current_time = pygame.time.get_ticks()
        if not self.lastframetime:
            self.lastframetime = self.start_time
        if self.lastframetime:
            self.secs += (current_time - self.lastframetime) / 1000
        self.lastframetime = current_time

    def info_lines_calc(self):
        """Calculate debug information for display."""
        self.actual_fps = self.clock.get_fps()
        self.info_lines = [
            f"FPS: {self.actual_fps:.2f}",
            f"Time: {self.secs:.2f} secs",
            f"Frame: {self.frame_count}",
            f"Ants: {len(self.ants)}",
            f"Dots: {len(self.dots)}",
            f"Anthills: {len(self.anthills)}",
        ]

    def update_simulation(self):
        """Update the state of all simulation entities."""
        if random.random() * self.targetfps > self.actual_fps:
            self.spatial_grid.consolidate_dots()

        self.entity_manager.update_entities()

    def run(self):
        """Main game loop."""
        while self.running:
            self.frame_count += 1
            self.timepiece()
            if self.frame_count >= self.actual_fps:
                self.frame_count = 0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.input_handler.handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self.input_handler.handle_keyup(event)

            # Update simulation state
            if not self.paused:
                try:
                    self.update_simulation()
                except Exception as e:
                    import traceback
                    print("\nError occurred during simulation update:")
                    traceback.print_exc()
                    print(f"\nError details: {str(e)}")
                    if not self.debug:
                        raise  # Re-raise in non-debug mode

            # Render frame
            self.screen.fill(self.background_color)
            self.graphics.draw()
            pygame.display.flip()

            self.clock.tick(1000000)

        pygame.quit()
        sys.exit()

    def quitter(self):
        """Stop the simulation."""
        self.running = False

    def reset_simulation(self):
        """Performs a complete reset of the simulation."""
        self.entity_manager.reset_simulation()

    def add_new_anthill(self):
        """Creates a new anthill at a random non-overlapping position."""
        self.entity_manager.add_new_anthill()

    def add_new_food(self):
        """Creates a new food source at a random non-overlapping position."""
        self.entity_manager.add_new_food()

    def cut_dots_population(self):
        """Reduce the number of pheromone dots based on death rate."""
        self.entity_manager.cut_dots_population()

    def cut_ant_population(self, howmany: int = 1):
        """Reduce the number of ants."""
        self.entity_manager.cut_ant_population(howmany)

    def create_ant_from_anthill(self, anthill=None, create: int = None):
        """Creates new ants at each anthill's position."""
        self.entity_manager.create_ant_from_anthill(anthill, create)

    def get_items_in_polygon(self, polygon):
        """Find all simulation entities within a given polygon."""
        return self.spatial_grid.get_items_in_polygon(polygon)
