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
    def __init__(self, debug=False):
        pygame.init()
        self.debug = debug
        self.width = settings.width
        self.height = settings.height
        self.targetfps = settings.targetfps
        self.frame_count = 0
        self.start_time = pygame.time.get_ticks()  # Store the start time
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

        This method calculates the time elapsed since the last frame and adds it to the total elapsed time (`self.secs`).
        It also updates `self.lastframetime` to the current time for use in the next frame.

        If `self.lastframetime` is None, it initializes it with `self.start_time`.

        Attributes:
            self.lastframetime (int or None): The time of the last frame in milliseconds.
            self.start_time (int): The start time of the environment in milliseconds.
            self.secs (float): The total elapsed time in seconds.
        """
        if not self.lastframetime:
            self.lastframetime = self.start_time
        if self.lastframetime:  # If lastframetime is not None # Update the elapsed time
            self.secs += (pygame.time.get_ticks() - self.lastframetime) / 1000
        # Stores the current time for the next frame
        self.lastframetime = pygame.time.get_ticks()

    def create_population(self):
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
        Creates an ant at the position of the given anthill.

        Args:
            anthill (Anthill): The anthill from which to create the ant.
        """
        for _ in range(2):
            self.ants.append(Ant(position=anthill.position))

    def population_control(self):
        """
        Controls the population of dots and ants in the environment.
        """
        try:
            if self.frame_count == 0:
                if self.actual_fps > (self.targetfps // 3):
                    self.create_ant_from_anthill(self.anthills[0])
                if self.actual_fps < (self.targetfps // 3):
                    for _ in range(len(self.ants)*2):
                        self.dots.pop()
                        '''for _ in range(1):
                        if self.ants[0].foodbool is False:
                            self.ants[0].alive = False'''

        except Exception as e:
            print(e)
            self.create_population()

        self.dots = [dot for dot in self.dots if dot.active]
        self.ants = [ant for ant in self.ants if ant.alive]
        random.shuffle(self.ants)
        random.shuffle(self.dots)

    def update_simulation(self):
        for ant in self.ants:
            try:
                dot_type, dottime = ant.act(self)
                if dot_type:
                    self.dots.append(Dot(ant.position, dot_type,dottime))
            except Exception as e:
                print(e)

        self.population_control()

    def run(self):
        while self.running:
            self.frame_count += 1
            self.timepiece()
            if self.frame_count >= self.actual_fps:
                self.frame_count = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # """ Key Handling"""
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self.handle_keyup(event)
            if self.paused is False:
                self.update_simulation()

            self.screen.fill(BROWN)  # Dark brown color
            self.draw()
            pygame.display.flip()
            # Limit the frame rate
            self.clock.tick(settings.targetfps)

        pygame.quit()
        sys.exit()

    # """ Modifiers Functions"""

    def quitter(self):
        self.running = False
        
    def cut_dots_population(self):
        """Cuts the dot population in half"""
        dots_to_remove = len(self.dots) // 2
        self.dots = self.dots[dots_to_remove:]

    # """ Key Handling Functions"""

    def handle_keydown(self, event):
        actions = {
            pygame.K_q: self.quitter,
            pygame.K_s: self.cut_dots_population,
        }
        action = actions.get(event.key)
        if action:
            action()
        else:
            # Add key to active keys for continuous actions
            self.active_keys.add(event.key)

    def handle_keyup(self, event):
        # Remove key from active keys when released
        if event.key in self.active_keys:
            self.active_keys.remove(event.key)

    # """ Rendering Functions"""

    def info_lines_calc(self):
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
        self.onscreen = (
            [anthill for anthill in self.anthills]
            + [dots for dots in self.dots if dots.active]
            + [ants for ants in self.ants if ants.alive]
            + [food for food in self.food]
        )
        # """ Draw Anthills """
        for anthill in self.anthills:
            visualpacket = anthill.visual()
            pygame.draw.circle(
                self.screen,
                visualpacket["color"],
                visualpacket["position"],
                visualpacket["size"],
            )
        # """ Draw Food """
        for food in self.food:
            visualpacket = food.visual()
            pygame.draw.circle(
                self.screen,
                visualpacket["color"],
                visualpacket["position"],
                visualpacket["size"],
            )
        # """ Draw Dots """
        for dot in self.dots:
            visualpacket = dot.visual()

            # Create a temporary surface with per-pixel alpha
            temp_surface = pygame.Surface(
                (visualpacket["size"] * 2, visualpacket["size"] * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                temp_surface,
                visualpacket["color"],
                (visualpacket["size"], visualpacket["size"]),
                visualpacket["size"],
            )

            # Blit the temporary surface onto the main screen
            self.screen.blit(
                temp_surface,
                (
                    visualpacket["position"][0] - visualpacket["size"],
                    visualpacket["position"][1] - visualpacket["size"],
                ),
            )

        # """ Draw Ants """
        for ant in self.ants:
            visualpacket = ant.visual()
            pygame.draw.polygon(
                self.screen, visualpacket["color"], visualpacket["points"]
            )
            if self.debug is True:
                pygame.draw.polygon(self.screen, WHITE, ant.calculate_view_triangle())

        # Draw UI text
        self.info_lines_calc()
        y_offset = 10
        for line in self.info_lines:
            if line:
                text_surface = self.font.render(line, True, WHITE)
                self.screen.blit(text_surface, (10, y_offset))
            y_offset += 18

    def get_items_in_polygon(self, polygon):
        """
        Returns a list of all items (dots and ants) within the given polygon.

        Args:
            polygon (list of tuples): A list of (x, y) tuples representing the vertices of the polygon.

        Returns:
            list: A list of items (dots and ants) within the polygon.
        """
        items_in_polygon = []
        for item in self.onscreen:
            if isinstance(item, Dot):
                if pygame.draw.polygon(self.screen, (0, 0, 0), polygon, 1).collidepoint(
                    item.position
                ):  # Check if the dot is within the polygon
                    items_in_polygon.append(item)
            elif isinstance(item, Ant):
                if pygame.draw.polygon(self.screen, (0, 0, 0), polygon, 1).collidepoint(
                    item.position
                ):  # Check if the ant is within the polygon
                    items_in_polygon.append(item)
            else:
                try:
                    if pygame.draw.polygon(
                        self.screen, (0, 0, 0), polygon, 1
                    ).collidepoint(
                        item.position
                    ):  # Check if the item is within the polygon
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
