import pygame
import settings
import sys

WHITE = settings.WHITE
BGBROWN = settings.BGBROWN


class Game:
    def __init__(self):
        pygame.init()
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

        # Render Screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings.name)
        # Clock
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 16)
        self.running = True

    def timepiece(self):
        if not self.lastframetime:
            self.lastframetime = self.start_time
        if self.lastframetime:  # If lastframetime is not None # Update the elapsed time
            self.secs += (pygame.time.get_ticks() - self.lastframetime) / 1000
        # Stores the current time for the next frame
        self.lastframetime = pygame.time.get_ticks()

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

            self.screen.fill(BGBROWN)  # Dark brown color
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
        # Draw UI text
        self.info_lines_calc()
        y_offset = 10
        for line in self.info_lines:
            if line:
                text_surface = self.font.render(line, True, WHITE)
                self.screen.blit(text_surface, (10, y_offset))
            y_offset += 18


if __name__ == "__main__":
    game = Game()
    game.run()
