"""
Spatial Grid Module for Ant Colony Simulation

This module handles spatial partitioning for efficient collision detection and entity management.
"""

import pygame
from collections import defaultdict

class SpatialGrid:
    def __init__(self, game):
        self.game = game
        self.cell_size = ((game.width + game.height) // 2) // 100
        self.grid = defaultdict(list)
        self.most_populated_cell = None

    def update_grid(self):
        """Update spatial partitioning grid and track the most populated cell."""
        self.grid.clear()
        self.most_populated_cell = None

        for item in self.game.onscreen:
            if hasattr(item, "position"):
                cell_x = int(item.position[0] // self.cell_size)
                cell_y = int(item.position[1] // self.cell_size)
                cell = (cell_x, cell_y)
                self.grid[cell].append(item)

    def get_items_in_polygon(self, polygon):
        """Find all simulation entities within a given polygon using spatial partitioning."""
        min_x = min(p[0] for p in polygon)
        max_x = max(p[0] for p in polygon)
        min_y = min(p[1] for p in polygon)
        max_y = max(p[1] for p in polygon)

        # Get relevant grid cells
        start_cell_x = int(min_x // self.cell_size)
        start_cell_y = int(min_y // self.cell_size)
        end_cell_x = int(max_x // self.cell_size)
        end_cell_y = int(max_y // self.cell_size)

        # Create collision mask once
        width = int(max_x - min_x + 1)
        height = int(max_y - min_y + 1)
        mask_surface = pygame.Surface((width, height))
        adjusted_polygon = [(x - min_x, y - min_y) for x, y in polygon]
        pygame.draw.polygon(mask_surface, (255, 255, 255), adjusted_polygon)
        mask = pygame.mask.from_surface(mask_surface)

        items_in_polygon = []
        # Check only items in relevant grid cells
        for cell_x in range(start_cell_x, end_cell_x + 1):
            for cell_y in range(start_cell_y, end_cell_y + 1):
                for item in self.grid.get((cell_x, cell_y), []):
                    pos = getattr(item, "position", None)
                    if pos is None and hasattr(item, "visual"):
                        pos = item.visual()["position"]

                    if pos:
                        # Quick bounding box check
                        if min_x <= pos[0] <= max_x and min_y <= pos[1] <= max_y:
                            # Precise polygon check using mask
                            rel_x = int(pos[0] - min_x)
                            rel_y = int(pos[1] - min_y)
                            if 0 <= rel_x < width and 0 <= rel_y < height:
                                if mask.get_at((rel_x, rel_y)):
                                    items_in_polygon.append(item)

        return items_in_polygon

    def consolidate_dots(self):
        """Optimize the number of dots by consolidating dots in close proximity."""
        if len(self.game.dots) < 200:
            return  # Not enough dots to consolidate

        # Use spatial partitioning to group dots into nearby pairs
        consolidated_dots = []
        visited = set()

        for dot in self.game.dots:
            if dot in visited:
                continue

            # Find the closest dot in the same cell or adjacent cells
            cell_x = int(dot.position[0] // self.cell_size)
            cell_y = int(dot.position[1] // self.cell_size)
            
            closest_dot = None
            closest_distance = float("inf")

            # Check current and adjacent cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    cell = (cell_x + dx, cell_y + dy)
                    for other_dot in self.grid.get(cell, []):
                        if (other_dot in visited or other_dot == dot or 
                            not hasattr(other_dot, "type") or 
                            other_dot.type != dot.type):
                            continue

                        # Calculate distance
                        dx = dot.position[0] - other_dot.position[0]
                        dy = dot.position[1] - other_dot.position[1]
                        distance = (dx * dx + dy * dy) ** 0.5

                        if distance < closest_distance:
                            closest_distance = distance
                            closest_dot = other_dot

            # If a close dot is found, consolidate them
            if closest_dot and closest_distance < self.cell_size:
                new_position = [
                    (dot.position[0] + closest_dot.position[0]) / 2,
                    (dot.position[1] + closest_dot.position[1]) / 2,
                ]
                new_dot = self.game.entity_manager._get_dot_from_pool(
                    new_position, dot.type, dot.time
                )
                consolidated_dots.append(new_dot)
                visited.add(dot)
                visited.add(closest_dot)
            else:
                # Keep the dot as is if no close pair is found
                consolidated_dots.append(dot)

        # Replace the current dots with the consolidated list
        self.game.dots = consolidated_dots
