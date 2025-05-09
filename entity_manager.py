"""
Entity Manager Module for Ant Colony Simulation

This module manages game entities including ants, dots, food, and anthills.
"""

import random
from ants import Ant
from antcolony import Anthill
from food import Food
from dots import Dot

class EntityManager:
    def __init__(self, game):
        self.game = game
        self._dot_pool = []

    def create_population(self):
        """Initialize the simulation entities."""
        barrier = self.game.anthill_size * 2
        self.game.anthills = [
            Anthill(
                position=[
                    random.randint(barrier, self.game.width - barrier),
                    random.randint(barrier, self.game.height - barrier),
                ]
            )
        ]
        self.game.ants = [
            Ant(position=self.game.anthills[0].position, anthill=self.game.anthills[0])
            for _ in range(self.game.popmin)
        ]
        self.game.food = [Food() for _ in range(1)]

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
        if self.game.actual_fps < 15:  # Limit pool size
            self._dot_pool.append(dot)

    def create_ant_from_anthill(self, anthill=None, create: int = None):
        """Creates new ants at each anthill's position."""
        if create is None:
            create = len(self.game.ants) // 2
        if create < 1:
            create = 1
        if create > 10:
            create = 10
        if anthill is None:
            anthill = random.choice(self.game.anthills)
        for anthill in self.game.anthills:
            for _ in range(random.randint(1, create)):
                self.game.ants.append(Ant(position=anthill.position, anthill=anthill))

    def check_position_overlap(self, position, size):
        """Check if a position would overlap with existing anthills or food sources."""
        # Check overlap with anthills
        for anthill in self.game.anthills:
            dx = position[0] - anthill.position[0]
            dy = position[1] - anthill.position[1]
            min_distance = size + self.game.anthill_size
            if (dx * dx + dy * dy) < (min_distance * min_distance):
                return True

        # Check overlap with food sources
        for food in self.game.food:
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
                random.randint(barrier, self.game.width - barrier),
                random.randint(barrier, self.game.height - barrier),
            ]
            if not self.check_position_overlap(position, size):
                return position

        # If no valid position found after max attempts, find position with maximum separation
        best_position = None
        max_min_distance = 0

        for attempt in range(20):  # Try 20 positions
            position = [
                random.randint(barrier, self.game.width - barrier),
                random.randint(barrier, self.game.height - barrier),
            ]
            min_distance = float("inf")

            # Check distance to all objects
            for anthill in self.game.anthills:
                dx = position[0] - anthill.position[0]
                dy = position[1] - anthill.position[1]
                distance = (dx * dx + dy * dy) ** 0.5
                min_distance = min(min_distance, distance)

            for food in self.game.food:
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
        position = self.get_valid_position(self.game.anthill_size)
        new_anthill = Anthill(position=position)
        self.game.anthills.append(new_anthill)
        self.create_ant_from_anthill(new_anthill)

    def add_new_food(self):
        """Creates a new food source at a random non-overlapping position."""
        food_size = self.game.anthill_size * 2  # Food size is 2x anthill size
        position = self.get_valid_position(food_size)
        self.game.food.append(Food(position=position))

    def cut_dots_population(self):
        """Reduce the number of pheromone dots based on death rate."""
        random.shuffle(self.game.dots)
        dots_to_remove = int(len(self.game.dots) * self.game.dot_death_rate)
        removed_dots = self.game.dots[dots_to_remove:]
        self.game.dots = self.game.dots[:dots_to_remove]
        # Return removed dots to pool
        for dot in removed_dots:
            self._return_dot_to_pool(dot)

    def cut_ant_population(self, howmany: int = 1):
        """Reduce the number of ants."""
        for _ in range(howmany):
            random.shuffle(self.game.ants)
            self.game.ants[0].alive = False

    def reset_simulation(self):
        """Performs a complete reset of the simulation."""
        # Clear all entities
        self.game.dots.clear()
        self.game.ants.clear()
        self.game.anthills.clear()
        self.game.food.clear()
        self._dot_pool.clear()
        self.game.secs = 0

        # Start fresh
        self.create_population()

    def update_entities(self):
        """Update the state of all entities."""
        # Update ants and create new dots
        for ant in self.game.ants:
            try:
                dot_type, dottime = ant.act(self.game)
                if dot_type:
                    dot = self._get_dot_from_pool(ant.position, dot_type, dottime)
                    self.game.dots.append(dot)
            except Exception as e:
                print(e)
        # Update all dots (increment age for fading)
        # Remove dots that are fully faded (alpha == 0)
        alive_dots = []
        for dot in self.game.dots:
            dot.update()
            if dot.get_alpha() > 0:
                alive_dots.append(dot)
        self.game.dots = alive_dots
        self.population_control()

    def population_control(self):
        """Manages the population of entities in the simulation."""
        try:
            if self.game.frame_count == 0:
                if self.game.actual_fps > (self.game.targetfps // 3):
                    self.create_ant_from_anthill()
                if self.game.actual_fps < (self.game.targetfps // 3):
                    # Return removed dots to pool
                    dots_to_remove = len(self.game.ants) * 2
                    for _ in range(min(dots_to_remove, len(self.game.dots))):
                        dot = self.game.dots.pop()
                        self._return_dot_to_pool(dot)
        except Exception as e:
            print(e)
            self.create_population()

        if len(self.game.ants) <= 1:
            self.create_ant_from_anthill(create=self.game.popmin)
        self.game.ants = [ant for ant in self.game.ants if ant.alive]
