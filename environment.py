import pygame
import settings
from dots import Dot
from ants import Ant
import sys

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
        self.dots = [Dot() for _ in range(10)]
        self.ants = [Ant() for _ in range(1)]

    def update_simulation(self):
        for dot in self.dots:
            dot.update()
        # Remove dots that are not active
        self.dots = [dot for dot in self.dots if dot.active]

        for ant in self.ants:

            dot_type = ant.act(int(self.secs))
            if dot_type:
                self.dots.append(Dot(ant.position, dot_type))
        # Remove ants that are not active
        self.ants = [ant for ant in self.ants if ant.alive]

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

    # """ Key Handling Functions"""

    def handle_keydown(self, event):
        actions = {
            pygame.K_q: self.quitter,
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
        ]

    def draw(self):
        # """ Draw Dots """
        for dot in self.dots:
            coloralpha = dot.get_alpha()
            colornow = (dot.color[0], dot.color[1], dot.color[2], coloralpha)

            # Create a temporary surface with per-pixel alpha
            temp_surface = pygame.Surface((dot.size * 2, dot.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, colornow, (dot.size, dot.size), dot.size)

            # Blit the temporary surface onto the main screen
            self.screen.blit(
                temp_surface, (dot.position[0] - dot.size, dot.position[1] - dot.size)
            )

        # """ Draw Ants """
        for ant in self.ants:
            pygame.draw.polygon(self.screen, ant.color, ant.calculate_draw_points())
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

        # Check dots
        for dot in self.dots:
            if pygame.draw.polygon(self.screen, (0, 0, 0), polygon, 1).collidepoint(
                dot.position
            ):
                items_in_polygon.append(dot)

        # Check ants
        for ant in self.ants:
            if pygame.draw.polygon(self.screen, (0, 0, 0), polygon, 1).collidepoint(
                ant.position
            ):
                items_in_polygon.append(ant)

        return items_in_polygon


if __name__ == "__main__":
    game = Game()
    game.run()
