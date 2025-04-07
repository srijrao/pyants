"""
Input Handler Module for Ant Colony Simulation

This module handles keyboard events and input processing.
"""

import pygame
from ants import Ant

class InputHandler:
    def __init__(self, game):
        self.game = game
        self.active_keys = set()

    def handle_keydown(self, event):
        """Handle keyboard press events."""
        actions = {
            pygame.K_q: self.game.quitter,
            pygame.K_s: self.game.cut_dots_population,
            pygame.K_a: self.game.add_new_anthill,  # 'a' key for new anthill
            pygame.K_f: self.game.add_new_food,  # 'f' key for new food source
            pygame.K_r: self.game.reset_simulation,  # 'r' key for reset
            pygame.K_k: self.game.cut_ant_population,
            pygame.K_p: lambda: setattr(self.game, "paused", not self.game.paused),
            pygame.K_d: lambda: setattr(self.game, "debug", not self.game.debug),
            pygame.K_SPACE: lambda: self.game.create_ant_from_anthill(),
            pygame.K_c: lambda: setattr(self.game, "see_dots", not self.game.see_dots),
            pygame.K_UP: lambda: self.game.ants.append(
                Ant(position=self.game.anthills[0].position, anthill=self.game.anthills[0])
            ),
        }
        action = actions.get(event.key)
        if action:
            action()
        else:
            self.active_keys.add(event.key)

    def handle_keyup(self, event):
        """Handle keyboard release events."""
        if event.key in self.active_keys:
            self.active_keys.remove(event.key)
