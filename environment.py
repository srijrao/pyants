"""
Environment Module for Ant Colony Simulation

This module defines the Game class which manages the entire ant colony simulation.
It handles the simulation loop, rendering, input processing, and maintains the state
of all entities including ants, food sources, anthills, and pheromone trails.
"""

import pygame
import sys
import random

import settings
from dots import Dot
from ants import Ant
from antcolony import Anthill
from food import Food

WHITE = settings.WHITE
BROWN = settings.BROWN

class Game:
    """
    Main game class that manages the ant colony simulation.
    
    This class is responsible for initializing the pygame environment,
    managing all simulation entities (ants, food, anthills, dots),
    handling user input, updating the simulation state, and rendering
    the simulation to the screen.

    Attributes:
        debug (bool): Enable/disable debug visualization
        width (int): Window width in pixels
        height (int): Window height in pixels
        targetfps (int): Target frames per second
        frame_count (int): Current frame number
        start_time (int): Simulation start time in milliseconds
        secs (float): Total elapsed time in seconds
        active_keys (set): Currently pressed keys
        lastframetime (int): Time of last frame for delta time calculation
        info_lines (list): Debug information to display
        actual_fps (float): Current frames per second
        dots (list): Active pheromone markers
        ants (list): Active ants in simulation
        anthills (list): Anthills in simulation
        food (list): Food sources in simulation
        onscreen (list): All visible entities
        paused (bool): Simulation pause state
        screen (pygame.Surface): Main display surface
        clock (pygame.time.Clock): Game clock for timing
        font (pygame.font.Font): Font for debug text
        running (bool): Main loop control flag
    """

    def __init__(self, debug=False):
        """
        Initialize the game environment.

        Args:
            debug (bool, optional): Enable debug visualization. Defaults to False.
        """
        pygame.init()
        self.debug = debug
        self.width = settings.width
        self.height = settings.height
        self.targetfps = settings.targetfps
        self.frame_count = 0
        self.start_time = pygame.time.get_ticks()
        self.secs = 0
        self.active_keys = set()
        self.lastframetime = None
        self.info_lines = []
        self.actual_fps = 1
        self.dots = []
        self.ants = []
        self.anthills = []
        self.onscreen = []
        self.paused = False
        self.create_population()
        # Render Screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings.name)
        # Clock
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 16)
        self.running = True

    def timepiece(self):
        """
        Updates the elapsed time for the environment.

        This method calculates the time elapsed since the last frame and adds it to
        the total elapsed time (self.secs). It also updates lastframetime to the
        current time for use in the next frame.
        """
        if not self.lastframetime:
            self.lastframetime = self.start_time
        if self.lastframetime:
            self.secs += (pygame.time.get_ticks() - self.lastframetime) / 1000
        self.lastframetime = pygame.time.get_ticks()

    def create_population(self):
        """
        Initialize the simulation entities.

        Creates the initial anthills, ants, and food sources with appropriate
        positioning within the simulation boundaries.
        """
        barrier = settings.Anthill_size * 2
        self.anthills = [
            Anthill(
                position=[
                    random.randint(barrier, self.width - barrier),
                    random.randint(barrier, self.height - barrier),
                ]
            )
        ]
        self.ants = [Ant(position=self.anthills[0].position) for _ in range(1)]
        self.food = [Food() for _ in range(1)]

    def create_ant_from_anthill(self, anthill):
        """
        Creates new ants at a specified anthill's position.

        Args:
            anthill (Anthill): The anthill from which to spawn new ants.
        """
        for _ in range(2):
            self.ants.append(Ant(position=anthill.position))

    def population_control(self):
        """
        Manages the population of entities in the simulation.

        This method handles the creation of new ants and cleanup of inactive
        entities based on performance metrics and simulation rules.
        """
        try:
            if self.frame_count == 0:
                if self.actual_fps > (self.targetfps // 3):
                    self.create_ant_from_anthill(self.anthills[0])
                if self.actual_fps < (self.targetfps // 3):
                    for _ in range(len(self.ants)*2):
                        self.dots.pop()
        except Exception as e:
            print(e)
            self.create_population()

        # Clean up inactive entities
        self.dots = [dot for dot in self.dots if dot.active]
        self.ants = [ant for ant in self.ants if ant.alive]
        # Randomize order for fairness
        random.shuffle(self.ants)
        random.shuffle(self.dots)

    def update_simulation(self):
        """
        Update the state of all simulation entities.

        Updates each ant's state and handles the creation of new pheromone dots.
        Also manages population control based on performance metrics.
        """
        for ant in self.ants:
            try:
                dot_type, dottime = ant.act(self)
                if dot_type:
                    self.dots.append(Dot(ant.position, dot_type, dottime))
            except Exception as e:
                print(e)

        self.population_control()

    def run(self):
        """
        Main game loop.

        Handles the core simulation loop including:
        - Event processing
        - State updates
        - Rendering
        - Frame timing
        """
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
                    self.handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self.handle_keyup(event)
                    
            # Update simulation state
            if self.paused is False:
                self.update_simulation()

            # Render frame
            self.screen.fill(BROWN)
            self.draw()
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(settings.targetfps)

        pygame.quit()
        sys.exit()

    def quitter(self):
        """Stop the simulation."""
        self.running = False
        
    def cut_dots_population(self):
        """
        Reduce the number of pheromone dots by half.
        
        Used as a performance optimization when needed.
        """
        dots_to_remove = len(self.dots) // 2
        self.dots = self.dots[dots_to_remove:]

    def handle_keydown(self, event):
        """
        Handle keyboard press events.

        Args:
            event (pygame.event.Event): Keyboard event to process
        """
        actions = {
            pygame.K_q: self.quitter,
            pygame.K_s: self.cut_dots_population,
        }
        action = actions.get(event.key)
        if action:
            action()
        else:
            self.active_keys.add(event.key)

    def handle_keyup(self, event):
        """
        Handle keyboard release events.

        Args:
            event (pygame.event.Event): Keyboard event to process
        """
        if event.key in self.active_keys:
            self.active_keys.remove(event.key)

    def info_lines_calc(self):
        """
        Calculate debug information for display.

        Updates FPS counter and generates status information about
        the current simulation state.
        """
        self.actual_fps = self.clock.get_fps()
        self.info_lines = [
            f"FPS: {self.actual_fps:.2f}",
            f"Time: {self.secs:.2f} secs",
            f"Frame: {self.frame_count}",
            f"Ants: {len(self.ants)}",
            f"Dots: {len(self.dots)}",
            f"Anthills: {len(self.anthills)}",
        ]

    def draw(self):
        """
        Render the current simulation state.

        Draws all visible entities to the screen including:
        - Anthills
        - Food sources
        - Pheromone dots (with transparency)
        - Ants
        - Debug information (if enabled)
        """
        self.onscreen = (
            [anthill for anthill in self.anthills]
            + [dots for dots in self.dots if dots.active]
            + [ants for ants in self.ants if ants.alive]
            + [food for food in self.food]
        )
        
        # Draw Anthills
        for anthill in self.anthills:
            visualpacket = anthill.visual()
            pygame.draw.circle(
                self.screen,
                visualpacket["color"],
                visualpacket["position"],
                visualpacket["size"],
            )
            
        # Draw Food
        for food in self.food:
            visualpacket = food.visual()
            pygame.draw.circle(
                self.screen,
                visualpacket["color"],
                visualpacket["position"],
                visualpacket["size"],
            )
            
        # Draw Dots with transparency
        for dot in self.dots:
            visualpacket = dot.visual()
            temp_surface = pygame.Surface(
                (visualpacket["size"] * 2, visualpacket["size"] * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                temp_surface,
                visualpacket["color"],
                (visualpacket["size"], visualpacket["size"]),
                visualpacket["size"],
            )
            self.screen.blit(
                temp_surface,
                (
                    visualpacket["position"][0] - visualpacket["size"],
                    visualpacket["position"][1] - visualpacket["size"],
                ),
            )

        # Draw Ants
        for ant in self.ants:
            visualpacket = ant.visual()
            pygame.draw.polygon(
                self.screen, visualpacket["color"], visualpacket["points"]
            )
            if self.debug is True:
                pygame.draw.polygon(self.screen, WHITE, ant.calculate_view_triangle())

        # Draw debug information
        self.info_lines_calc()
        y_offset = 10
        for line in self.info_lines:
            if line:
                text_surface = self.font.render(line, True, WHITE)
                self.screen.blit(text_surface, (10, y_offset))
            y_offset += 18

    def get_items_in_polygon(self, polygon):
        """
        Find all simulation entities within a given polygon.

        This method is used primarily for ant vision calculations to determine
        what entities an ant can "see" within its field of view.

        Args:
            polygon (list): List of (x, y) tuples defining the polygon vertices

        Returns:
            list: All entities (dots, ants, food, etc.) within the polygon
        """
        items_in_polygon = []
        for item in self.onscreen:
            if isinstance(item, Dot):
                if pygame.draw.polygon(self.screen, (0, 0, 0), polygon, 1).collidepoint(
                    item.position
                ):
                    items_in_polygon.append(item)
            elif isinstance(item, Ant):
                if pygame.draw.polygon(self.screen, (0, 0, 0), polygon, 1).collidepoint(
                    item.position
                ):
                    items_in_polygon.append(item)
            else:
                try:
                    if pygame.draw.polygon(
                        self.screen, (0, 0, 0), polygon, 1
                    ).collidepoint(
                        item.position
                    ):
                        items_in_polygon.append(item)
                except AttributeError:
                    visual_packet = item.visual()
                    if pygame.draw.polygon(
                        self.screen, (0, 0, 0), polygon, 1
                    ).collidepoint(visual_packet["position"]):
                        items_in_polygon.append(item)

        return items_in_polygon


if __name__ == "__main__":
    game = Game()
    game.run()
