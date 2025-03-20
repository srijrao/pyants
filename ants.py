import settings
import math
import random


class Ant:
    def __init__(self, position=[settings.width / 2, settings.height / 2]):
        self.position = position
        self.setup()

    def setup(self):
        self.alive = True
        self.color = (
            random.randint(10, 200),
            random.randint(10, 200),
            random.randint(10, 200),
        )
        self.organism_height = 10
        self.organism_width = 5
        self.num_sides = random.randint(3, 8)
        self.angle = random.randint(0, 360)
        self.screen_w = settings.width
        self.screen_h = settings.height
        self.collision_distance = settings.collision_distance
        self.barrier_distance = self.collision_distance * 2
        self.rotation_speed = 10
        self.movement_speed = settings.ant_speed
        self.foodbool = False
        self.timeawareness = 0
        self.dropbool = True

    def calculate_draw_points(self):
        """
        Compute the vertices of the polygon for graphical representation on a rotated oval.
        Returns:
            tuple: Color and vertices of the polygon.
        """
        # Get standard values with defaults
        angle = self.angle
        position = self.position
        x_radius = self.organism_height
        y_radius = self.organism_width
        sides = max(self.num_sides, 3)
        angle_rad = math.radians(angle)
        points = []
        interior_angle = (2 * math.pi) / sides
        for i in range(sides):
            current_angle = i * interior_angle
            x_oval = x_radius * math.cos(current_angle)
            y_oval = y_radius * math.sin(current_angle)
            x_rotated = x_oval * math.cos(angle_rad) - y_oval * math.sin(angle_rad)
            y_rotated = x_oval * math.sin(angle_rad) + y_oval * math.cos(angle_rad)
            x = position[0] + x_rotated
            y = position[1] - y_rotated
            points.append((x, y))
        return points

    def visual(self):
        points = self.calculate_draw_points()
        self.visual_packet = {
            "position": self.position,
            "points": points,
            "color": self.color,
        }
        return self.visual_packet

    def distance_to(self, target_position):
        """
        Calculate Euclidean distance to a target position.
        """
        if not isinstance(self.state, dict):
            return float("inf")
        position = self.position
        dx = position[0] - target_position[0]
        dy = position[1] - target_position[1]
        return math.hypot(dx, dy)

    def rotate(self, clockwise=True, angle=None):
        """
        Rotate the ant by a specified angle or default to the rotation speed.
        """
        current_angle = self.angle
        if angle is not None:
            self.angle = angle % 360
        else:
            rotation_speed = self.rotation_speed
            delta_angle = (
                rotation_speed  # Positive if clockwise
                if clockwise
                else -rotation_speed  # Negative if counter-clockwise
            )
            self.angle = (current_angle + delta_angle) % 360

    def turn_towards(self, target):
        """
        Adjust the organism's angle to face a target position.
        """
        position = self.position
        current_angle = self.angle
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        target_angle = math.degrees(math.atan2(-dy, dx))
        angle_diff = (target_angle - current_angle + 360) % 360
        if angle_diff > 180:
            self.rotate(clockwise=False)
        else:
            self.rotate(clockwise=True)

    def shake_shiver(self):
        """
        Simulate a random shake or shiver by adjusting position randomly.
        """
        position = self.position
        jitter = 1
        deltas = [
            random.uniform(-jitter, jitter),
            random.uniform(-jitter, jitter),
        ]
        self.position = [position[0] + deltas[0], position[1] + deltas[1]]

    def move(self, forward=True):
        """
        Move the organism forward or backward.
        """
        mvm = self.movement_speed
        current_angle = self.angle
        position = self.position
        movement = mvm if forward else -mvm
        # Update position with safe defaults
        new_x = position[0] + movement * math.cos(math.radians(current_angle))
        new_y = position[1] - movement * math.sin(math.radians(current_angle))
        self.position = [new_x, new_y]

    def check_edge_collision(self, constraint=False):
        """
        Check if the organism is near screen edges and handle accordingly.
        """
        distance = self.collision_distance
        position = self.position
        x, y = position[0], position[1]
        collision_angle = None
        if x < distance:  # Hits left edge
            collision_angle = 180
        elif x > self.screen_w - distance:  # Hits right edge
            collision_angle = 0
        elif y < distance:  # Hits top edge
            collision_angle = 90
        elif y > self.screen_h - distance:  # Hits bottom edge
            collision_angle = 270

        if collision_angle is not None:
            self.screen_clamp()
            self.bounce(angle=collision_angle)

    def bounce(self, angle=None):
        """
        Bounce the organism off the screen edges.
        """
        self.angle = self.angle + 180 if angle is None else angle + 90
        # Move the ant slightly away from the edge to prevent repetitive flipping
        self.move(forward=True)
        self.screen_clamp()

    def screen_clamp(self):
        """
        Ensure the ants's position stays within the screen bounds.
        """
        distance = self.barrier_distance
        position = self.position
        new_x = max(
            distance,
            min(position[0], self.screen_w - distance),
        )
        new_y = max(
            distance,
            min(position[1], self.screen_h - distance),
        )
        self.position = [new_x, new_y]

    def drop_dot(self):
        """
        Drop a dot at the current position of the ant.
        When not carrying food: Drop 'to home' dots
        When carrying food: Drop 'to food' dots
        """
        if self.foodbool:
            dot_type = "to food"
        else:
            dot_type = "to home"
        return dot_type

    def random_walk(self):
        """
        Simulate a random walk by adjusting the angle and moving forward.
        """
        self.rotate(clockwise=random.choice([True, False]))
        self.move(forward=True)

    def calculate_view_triangle(self, vision_distance=None, fieldofvision=90):
        """
        Calculate the vertices of the view triangle representing the ant's field of vision.
        Args:
            vision_distance (float): The distance the ant can see in front of it.
        Returns:
            list: A list of three tuples representing the vertices of the triangle.
        """
        if vision_distance is None:
            vision_distance = self.collision_distance * 5
        angle_rad = math.radians(self.angle)
        half_fov_rad = math.radians(fieldofvision / 2)  # half on each side

        # Calculate the front vertex of the triangle
        front_x = self.position[0] + vision_distance * math.cos(angle_rad)
        front_y = self.position[1] - vision_distance * math.sin(angle_rad)

        # Calculate the left vertex of the triangle
        left_x = self.position[0] + vision_distance * math.cos(angle_rad - half_fov_rad)
        left_y = self.position[1] - vision_distance * math.sin(angle_rad - half_fov_rad)

        # Calculate the right vertex of the triangle
        right_x = self.position[0] + vision_distance * math.cos(
            angle_rad + half_fov_rad
        )
        right_y = self.position[1] - vision_distance * math.sin(
            angle_rad + half_fov_rad
        )

        return [
            (self.position[0], self.position[1]),
            (left_x, left_y),
            (front_x, front_y),
            (right_x, right_y),
        ]

    def find_newest_visible_dot(self, environment):
        """
        Find the newest (highest timeleft) dot in the ant's field of vision.
        Only perceives dots of appropriate type based on foodbool state.
        """
        view_triangle = self.calculate_view_triangle()
        visible_items = environment.get_items_in_polygon(view_triangle)

        # Only perceive dots of appropriate type
        target_type = "to home" if self.foodbool else "to food"
        visible_dots = [
            item
            for item in visible_items
            if isinstance(item, type(environment.dots[0])) and item.type == target_type
        ]

        if not visible_dots:
            return None

        # Sort by timeleft (newest first)
        newest_dot = max(visible_dots, key=lambda dot: dot.timeleft)
        return newest_dot

    def act(self, environment=None):
        """
        Act based on environment and time.
        """
        dot_type = None
        self.dropbool = not self.dropbool
        if self.dropbool is True:
            dot_type = self.drop_dot()
        self.timeawareness +=0.001

        if environment:
            # Check for food if not carrying any
            if not self.foodbool:
                view_triangle = self.calculate_view_triangle()
                visible_items = environment.get_items_in_polygon(view_triangle)
                visible_food = [
                    item
                    for item in visible_items
                    if isinstance(item, type(environment.food[0]))
                ]
                if visible_food:
                    # Found food - pick it up and set foodbool
                    self.foodbool = True
                    self.timeawareness = 0
                    self.turn_towards(visible_food[0].position)
                    self.move(forward=True)
                    return dot_type

            # Look for newest appropriate dot
            nearest_dot = self.find_newest_visible_dot(environment)
            if nearest_dot:
                # Follow the newest dot of appropriate type
                newest_dot = nearest_dot
                self.turn_towards(newest_dot.position)
                self.move(forward=True)
            else:
                self.random_walk()
        else:
            self.random_walk()

        self.check_edge_collision()
        return dot_type,self.timeawareness
