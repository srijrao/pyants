"""
Graphics Module for Ant Colony Simulation

This module handles rendering and surface caching for the simulation.
"""

import pygame
import random


class Graphics:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 16)
        self._surface_cache = {}
        self._init_surface_cache()

    def _init_surface_cache(self):
        """Pre-render commonly used surfaces."""

        # Cache dot surfaces for both colors
        for size in range(1, self.game.dot_size + 1):
            # "to food" dots (purple)
            food_key = f"dot_food_{size}"
            food_surf = pygame.Surface(
                (size * 2, size * 2)
            ).convert_alpha()  # Convert for better performance
            food_surf.fill((0, 0, 0, 0))  # Fill with transparent black
            pygame.draw.circle(
                food_surf, (*self.game.dot_color_food, 255), (size, size), size
            )
            self._surface_cache[food_key] = food_surf

            # For "to home" (white) dots
            home_key = f"dot_home_{size}"
            home_surf = pygame.Surface(
                (size * 2, size * 2)
            ).convert_alpha()  # Convert for better performance
            home_surf.fill((0, 0, 0, 0))  # Fill with transparent black
            pygame.draw.circle(
                home_surf, (*self.game.dot_color_home, 255), (size, size), size
            )
            self._surface_cache[home_key] = home_surf

    def draw(self):
        """Optimized rendering with cached surfaces."""
        # Update visible entities list and spatial grid
        self.game.onscreen = (
            self.game.anthills
            + self.game.dots
            + [ant for ant in self.game.ants if ant.alive]
            + self.game.food
        )
        self.game.spatial_grid.update_grid()
    
        # Draw anthills
        for anthill in self.game.anthills:
            visual = anthill.visual()
            pygame.draw.circle(
                self.game.screen,
                visual["color"],
                visual["position"],
                visual["size"],
            )
            
        for food in self.game.food:
            visual = food.visual()
            pygame.draw.circle(
                self.game.screen, visual["color"], visual["position"], visual["size"]
            )

        if self.game.see_dots is True:
            # Draw dots with alpha transparency
            for dot in self.game.dots:
                visual = dot.visual()
                dot_surface = pygame.Surface(
                    (visual["size"] * 2, visual["size"] * 2), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    dot_surface,
                    visual["color"],  # Color includes alpha from visual()
                    (visual["size"], visual["size"]),
                    visual["size"],
                )
                pos = (
                    visual["position"][0] - visual["size"],
                    visual["position"][1] - visual["size"],
                )
                self.game.screen.blit(dot_surface, pos)

        # Draw ants
        for ant in self.game.ants:
            visual = ant.visual()
            pygame.draw.polygon(self.game.screen, visual["color"], visual["points"])
            if self.game.debug:
                pygame.draw.polygon(
                    self.game.screen,
                    self.game.dot_color_home,
                    ant.calculate_view_triangle(),
                )

        # Draw debug information
        self.game.info_lines_calc()
        y_offset = 10
        for line in self.game.info_lines:
            if line:
                text_surface = self.font.render(line, True, self.game.ui_color)
                self.game.screen.blit(text_surface, (10, y_offset))
            y_offset += 18
