"""
Environment Module for Ant Colony Simulation

This module defines the Game class which manages the entire ant colony simulation.
It handles the simulation loop, rendering, input processing, and maintains the state
of all entities including ants, food sources, anthills, and pheromone trails.
"""

import pygame
import sys
import random
from collections import defaultdict

import settings
from dots import Dot
from ants import Ant
from antcolony import Anthill
from food import Food

WHITE = settings.WHITE
BROWN = settings.BROWN


class Game:
    """Main game class that manages the ant colony simulation."""

    def __init__(self, debug=False, see_dots=False):
        pygame.init()
        self.debug = debug
        self.see_dots = see_dots
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
        self.popmin = settings.popmin

        # Object pooling for dots
        self._dot_pool = []
        self.dots = []
        self.ants = []
        self.anthills = []
        self.food = []
        self.onscreen = []
        self.paused = False

        # Spatial partitioning (grid-based)
        self.cell_size = ((settings.width+settings.height)//2) // 100
        self.grid = defaultdict(list)

        # Pre-rendered surfaces cache
        self._surface_cache = {}

        # Performance optimization flags
        self.update_skip_counter = 0
        self.UPDATE_SKIP_FRAMES = 2  # Update every N frames

        self.create_population()

        # Render Screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings.name)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 16)
        self.running = True

        # Initialize cached surfaces
        self._init_surface_cache()

    def _init_surface_cache(self):
        """Pre-render commonly used surfaces."""
        # Cache anthill surface
        anthill_size = settings.Anthill_size * 2
        anthill_surf = pygame.Surface((anthill_size, anthill_size), pygame.SRCALPHA)
        pygame.draw.circle(
            anthill_surf,
            (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255),
            ),
            (settings.Anthill_size, settings.Anthill_size),
            settings.Anthill_size,
        )
        self._surface_cache["anthill"] = anthill_surf

        # Cache dot surfaces for both colors
        for size in range(1, settings.dot_size + 1):
            # "to food" dots (purple)
            # For "to food" (purple) dots
            food_key = f"dot_food_{size}"
            food_surf = pygame.Surface(
                (size * 2, size * 2)
            ).convert_alpha()  # Convert for better performance
            food_surf.fill((0, 0, 0, 0))  # Fill with transparent black
            pygame.draw.circle(food_surf, (*settings.PURPLE, 255), (size, size), size)
            self._surface_cache[food_key] = food_surf

            # For "to home" (white) dots
            home_key = f"dot_home_{size}"
            home_surf = pygame.Surface(
                (size * 2, size * 2)
            ).convert_alpha()  # Convert for better performance
            home_surf.fill((0, 0, 0, 0))  # Fill with transparent black
            pygame.draw.circle(home_surf, (*settings.WHITE, 255), (size, size), size)
            self._surface_cache[home_key] = home_surf

    def _get_dot_from_pool(self, position, dot_type, dot_time):
        """Get a dot from the object pool or create new if pool is empty."""
        if self._dot_pool:
            dot = self._dot_pool.pop()
            dot.reset(position, dot_type, dot_time)
        else:
            dot = Dot(position, dot_type, dot_time)
        if not isinstance(dot, Dot):
            raise TypeError("Only Dot objects can be returned from the pool.")
        return dot

    def _return_dot_to_pool(self, dot):
        """Return a dot to the object pool."""
        if len(self._dot_pool) < 1000:  # Limit pool size
            self._dot_pool.append(dot)

    def constantconsolidation(self):
        """Optimize the number of dots by consolidating dots in the most populated cell."""
        # Ensure the spatial grid is updated
        self._update_spatial_grid()
        if random.random() < 0.005:
                self.cut_dots_population()
        return
        if random.random() < 0.5:
            # Get the most populated cell
            if not self.most_populated_cell:
                return  # No populated cell to process
            cell_dots = self.grid.get(self.most_populated_cell, [])
        else:
            if random.random() < 0.15:
                self.cut_dots_population()
            return

        if len(cell_dots) < 2:
            return  # Not enough dots in the cell to consolidate

        # Track dots to remove
        dots_to_remove = set()

        # Consolidate dots in the most populated cell
        for dot in cell_dots[:]:  # Use a copy of the list to avoid modification issues
            if not isinstance(dot, Dot):  # Ensure only Dot objects are processed
                continue
            if dot in dots_to_remove:
                continue

            for other_dot in cell_dots:
                if not isinstance(
                    other_dot, Dot
                ):  # Ensure only Dot objects are processed
                    continue
                if dot == other_dot or other_dot in dots_to_remove:
                    continue
                
                # Calculate distance
                dx = dot.position[0] - other_dot.position[0]
                dy = dot.position[1] - other_dot.position[1]
                distance = (dx * dx + dy * dy) ** 0.5

                if distance < settings.collision_distance / 4:
                    # Consolidate the two dots
                    new_dot = self.consolidate_two_dots(dot, other_dot)
                    if new_dot:
                        self.dots.append(new_dot)
                        dots_to_remove.add(dot)
                        dots_to_remove.add(other_dot)
                    break  # Exit inner loop to avoid further processing of `dot`

        # Remove the marked dots
        self.dots = [dot for dot in self.dots if dot not in dots_to_remove]

    def consolidate_two_dots(self, dot, other_dot):
        """Consolidate two dots into one."""
        if not isinstance(dot, Dot) or not isinstance(other_dot, Dot):
            raise TypeError("Only Dot objects can be consolidated.")
        if not dot.type == other_dot.type:
            return False  # Different types, keep the original dot

        new_position = [
            (dot.position[0] + other_dot.position[0]) / 2,
            (dot.position[1] + other_dot.position[1]) / 2,
        ]
        new_timeleft = (dot.timeleft + other_dot.timeleft) // 2
        new_dot = self._get_dot_from_pool(new_position, dot.type, dot.time)
        new_dot.timeleft = new_timeleft
        return new_dot

    def dot_consolidate_handler(self):
        """Consolidate nearby dots to reduce the total number of dots."""
        if len(self.dots) < 200:
            return  # Not enough dots to consolidate

        # Use spatial partitioning to group dots into nearby pairs
        consolidated_dots = []
        visited = set()

        for dot in self.dots:
            if dot in visited or not dot.active:
                continue

            # Find the closest dot
            closest_dot = None
            closest_distance = float("inf")
            for other_dot in self.dots:
                if other_dot in visited or not other_dot.active or other_dot == dot:
                    continue

                # Calculate distance
                dx = dot.position[0] - other_dot.position[0]
                dy = dot.position[1] - other_dot.position[1]
                distance = (dx * dx + dy * dy) ** 0.5

                if distance < closest_distance:
                    closest_distance = distance
                    closest_dot = other_dot

            # If a close dot is found, consolidate them
            if (
                closest_dot and closest_distance < self.cell_size
            ):  # Threshold for consolidation
                new_dot = self.consolidate_two_dots(dot, closest_dot)
                consolidated_dots.append(new_dot)
                visited.add(dot)
                visited.add(closest_dot)
            else:
                # Keep the dot as is if no close pair is found
                consolidated_dots.append(dot)

        # Replace the current dots with the consolidated list
        self.dots = consolidated_dots

    def _update_spatial_grid(self):
        """Update spatial partitioning grid and track the most populated cell."""
        self.grid.clear()
        self.most_populated_cell = None
        max_population = 0

        for item in self.onscreen:
            if hasattr(item, "position"):
                cell_x = int(item.position[0] // self.cell_size)
                cell_y = int(item.position[1] // self.cell_size)
                cell = (cell_x, cell_y)
                self.grid[cell].append(item)

                # Track the most populated cell
                if len(self.grid[cell]) > max_population:
                    max_population = len(self.grid[cell])
                    self.most_populated_cell = cell

    def timepiece(self):
        """Updates the elapsed time for the environment."""
        current_time = pygame.time.get_ticks()
        if not self.lastframetime:
            self.lastframetime = self.start_time
        if self.lastframetime:
            self.secs += (current_time - self.lastframetime) / 1000
        self.lastframetime = current_time

    def create_population(self):
        """Initialize the simulation entities."""
        barrier = settings.Anthill_size * 2
        self.anthills = [
            Anthill(
                position=[
                    random.randint(barrier, self.width - barrier),
                    random.randint(barrier, self.height - barrier),
                ]
            )
        ]
        self.ants = [
            Ant(position=self.anthills[0].position) for _ in range(self.popmin)
        ]
        self.food = [Food() for _ in range(1)]

    def create_ant_from_anthill(self, anthill, create: int = 2):
        """Creates new ants at a specified anthill's position."""
        for _ in range(random.randint(1, create)):
            self.ants.append(Ant(position=anthill.position))

    def population_control(self):
        """Manages the population of entities in the simulation."""
        try:
            if self.frame_count == 0:
                if self.actual_fps > (self.targetfps // 3):
                    self.create_ant_from_anthill(self.anthills[0])
                if self.actual_fps < (self.targetfps // 3):
                    # Return removed dots to pool
                    dots_to_remove = len(self.ants) * 2
                    for _ in range(min(dots_to_remove, len(self.dots))):
                        dot = self.dots.pop()
                        self._return_dot_to_pool(dot)
        except Exception as e:
            print(e)
            self.create_population()

        # Clean up inactive entities and return dots to pool
        active_dots = []
        for dot in self.dots:
            if dot.active:
                active_dots.append(dot)
            else:
                self._return_dot_to_pool(dot)
        self.dots = active_dots
        if len(self.ants) <= 1:
            self.create_ant_from_anthill(self.anthills[0], create=self.popmin)
        self.ants = [ant for ant in self.ants if ant.alive]

    def update_simulation(self):
        """Update the state of all simulation entities."""
        # Skip updates based on performance needs
        self.update_skip_counter = (
            self.update_skip_counter + 1
        ) % self.UPDATE_SKIP_FRAMES
        if self.update_skip_counter != 0:
            return
        # Update dots
        for dot in self.dots:
            dot.update()
        try:
            self.constantconsolidation()
        except Exception as e:
            if self.debug:
                print(e)

        # Update ants and create new dots
        for ant in self.ants:
            try:
                dot_type, dottime = ant.act(self)
                if dot_type:
                    dot = self._get_dot_from_pool(ant.position, dot_type, dottime)
                    self.dots.append(dot)
            except Exception as e:
                print(e)

        self.population_control()

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
                    self.handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self.handle_keyup(event)

            # Update simulation state
            if not self.paused:
                self.update_simulation()

            # Render frame
            self.screen.fill(BROWN)
            self.draw()
            pygame.display.flip()

            self.clock.tick(1000000)

        pygame.quit()
        sys.exit()

    def quitter(self):
        """Stop the simulation."""
        self.running = False

    def cut_dots_population(self):
        """Reduce the number of pheromone dots by half."""
        random.shuffle(self.dots)
        dots_to_remove = int(len(self.dots) * 0.9)
        removed_dots = self.dots[dots_to_remove:]
        self.dots = self.dots[:dots_to_remove]
        # Return removed dots to pool
        for dot in removed_dots:
            self._return_dot_to_pool(dot)

    def cut_ant_population(self, howmany: int = 1):
        """Reduce the number of ants by one."""
        """eliminate one ant"""
        for _ in range(howmany):
            random.shuffle(self.ants)
            self.ants[0].alive = False

    def reset_simulation(self):
        """Performs a complete reset of the simulation."""
        # Clear all entities
        self.dots.clear()
        self.ants.clear()
        self.anthills.clear()
        self.food.clear()
        self._dot_pool.clear()

        # Start fresh
        self.create_population()

    def check_position_overlap(self, position, size):
        """Check if a position would overlap with existing anthills or food sources."""
        # Check overlap with anthills
        for anthill in self.anthills:
            dx = position[0] - anthill.position[0]
            dy = position[1] - anthill.position[1]
            min_distance = size + settings.Anthill_size
            if (dx * dx + dy * dy) < (min_distance * min_distance):
                return True

        # Check overlap with food sources
        for food in self.food:
            dx = position[0] - food.position[0]
            dy = position[1] - food.position[1]
            min_distance = size + food.size
            if (dx * dx + dy * dy) < (min_distance * min_distance):
                return True

        return False

    def get_valid_position(self, size):
        """Get a random position that doesn't overlap with existing objects."""
        barrier = size * 2
        max_attempts = 100  # Prevent infinite loop

        for _ in range(max_attempts):
            position = [
                random.randint(barrier, self.width - barrier),
                random.randint(barrier, self.height - barrier),
            ]
            if not self.check_position_overlap(position, size):
                return position

        # If no valid position found after max attempts, find position with maximum separation
        best_position = None
        max_min_distance = 0

        for attempt in range(20):  # Try 20 positions
            position = [
                random.randint(barrier, self.width - barrier),
                random.randint(barrier, self.height - barrier),
            ]
            min_distance = float("inf")

            # Check distance to all objects
            for anthill in self.anthills:
                dx = position[0] - anthill.position[0]
                dy = position[1] - anthill.position[1]
                distance = (dx * dx + dy * dy) ** 0.5
                min_distance = min(min_distance, distance)

            for food in self.food:
                dx = position[0] - food.position[0]
                dy = position[1] - food.position[1]
                distance = (dx * dx + dy * dy) ** 0.5
                min_distance = min(min_distance, distance)

            if min_distance > max_min_distance:
                max_min_distance = min_distance
                best_position = position

        return best_position

    def add_new_anthill(self):
        """Creates a new anthill at a random non-overlapping position."""
        position = self.get_valid_position(settings.Anthill_size)
        new_anthill = Anthill(position=position)
        self.anthills.append(new_anthill)
        self.create_ant_from_anthill(new_anthill)

    def add_new_food(self):
        """Creates a new food source at a random non-overlapping position."""
        food_size = settings.Anthill_size * 2  # Food size is 2x anthill size
        position = self.get_valid_position(food_size)
        self.food.append(Food(position=position))

    def handle_keydown(self, event):
        """Handle keyboard press events."""
        actions = {
            pygame.K_q: self.quitter,
            pygame.K_s: self.cut_dots_population,
            pygame.K_a: self.add_new_anthill,  # 'a' key for new anthill
            pygame.K_f: self.add_new_food,  # 'f' key for new food source
            pygame.K_r: self.reset_simulation,  # 'r' key for reset
            pygame.K_k: self.cut_ant_population,
            pygame.K_p: lambda: setattr(self, "paused", not self.paused),
            pygame.K_d: lambda: setattr(self, "debug", not self.debug),
            pygame.K_SPACE: lambda: self.create_ant_from_anthill(self.anthills[0]),
            pygame.K_c: lambda: setattr(self, "see_dots", not self.see_dots),
            # add ant to self.ants
            pygame.K_UP: lambda: self.ants.append(
                Ant(position=self.anthills[0].position)
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

    def draw(self):
        """Optimized rendering with cached surfaces."""
        # Update visible entities list and spatial grid
        self.onscreen = (
            self.anthills
            + [dot for dot in self.dots if dot.active]
            + [ant for ant in self.ants if ant.alive]
            + self.food
        )
        self._update_spatial_grid()

        # Draw using cached surfaces where possible
        for anthill in self.anthills:
            visual = anthill.visual()
            pos = (
                visual["position"][0] - settings.Anthill_size,
                visual["position"][1] - settings.Anthill_size,
            )
            self.screen.blit(self._surface_cache["anthill"], pos)

        for food in self.food:
            visual = food.visual()
            pygame.draw.circle(
                self.screen, visual["color"], visual["position"], visual["size"]
            )
        if self.see_dots is True:
            # Draw dots with alpha transparency
            for dot in self.dots:
                if dot.active:
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
                    self.screen.blit(dot_surface, pos)
            # if len(self.dots) > 10000:
            #   self.cut_dots_population()
            # Draw ants
        for ant in self.ants:
            visual = ant.visual()
            pygame.draw.polygon(self.screen, visual["color"], visual["points"])
            if self.debug:
                pygame.draw.polygon(self.screen, WHITE, ant.calculate_view_triangle())

        # Draw debug information
        self.info_lines_calc()
        y_offset = 10
        for line in self.info_lines:
            if line:
                text_surface = self.font.render(line, True, WHITE)
                self.screen.blit(text_surface, (10, y_offset))
            y_offset += 18


if __name__ == "__main__":
    game = Game(debug=True)
    game.run()
