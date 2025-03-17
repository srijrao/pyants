import settings
import math
import random


class Ant:
    def __init__(self, position=[0, 0], direction=[0, 0]):
        self.position = position
        self.direction = direction
        self.setup()

    def setup(self):
        self.alive = True
        self.color = settings.PURPLE
        self.organism_height = 10
        self.organism_width = 5
        self.num_sides = 3
        self.angle = 0
        self.position = [settings.width / 2, settings.height / 2]
        self.screen_w = settings.width
        self.screen_h = settings.height
        self.collision_distance = settings.collision_distance
        self.barrier_distance = self.collision_distance * 2
        self.rotation_speed = 10
        self.movement_speed = settings.ant_speed
        self.foodbool = False
        self.timeawareness = 0

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
        position = self.position
        x, y = position[0], position[1]
        collision_angle = None
        if x < self.barrier_distance:  # Hits left edge
            collision_angle = 180
        elif x > self.screen_w - self.barrier_distance:  # Hits right edge
            collision_angle = 0
        elif y < self.barrier_distance:  # Hits top edge
            collision_angle = 90
        elif y > self.screen_h - self.barrier_distance:  # Hits bottom edge
            collision_angle = 270

        if collision_angle is not None:
            self.screen_clamp()
            self.bounce(angle=collision_angle)

    def bounce(self, angle=None):
        """
        Bounce the organism off the screen edges.
        """
        current_angle = self.angle
        if angle is not None:
            angle = angle % 360
            # Reflect the angle around the collision angle
            self.angle = (2 * angle - current_angle) % 360
        else:
            # Reflect the angle around the vertical axis
            self.angle = (180 - current_angle) % 360

        # Move the ant slightly away from the edge to prevent repetitive flipping
        self.move(forward=True)
        self.screen_clamp()

    def screen_clamp(self):
        """
        Ensure the ants's position stays within the screen bounds.
        """
        position = self.position
        new_x = max(
            self.collision_distance,
            min(position[0], self.screen_w - self.collision_distance),
        )
        new_y = max(
            self.collision_distance,
            min(position[1], self.screen_h - self.collision_distance),
        )
        self.position = [new_x, new_y]

    def drop_dot(self):
        """
        Drop a dot at the current position of the ant.
        """
        if self.foodbool:
            dot_type = "to home"
        else:
            dot_type = "to food"
        return dot_type

    def random_walk(self):
        """
        Simulate a random walk by adjusting the angle and moving forward.
        """
        self.rotate(clockwise=random.choice([True, False]))
        self.move(forward=True)

    def calculate_view_triangle(self, vision_distance=None):
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
        half_fov_rad = math.radians(
            45
        )  # 90 degrees field of vision, so 45 degrees on each side

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

    def act(self, timesecs):
        """ "
        go
        """
        dot_type = None
        if self.timeawareness != timesecs:
            dot_type = self.drop_dot()
        self.random_walk()
        self.check_edge_collision()
        self.timeawareness = timesecs
        return dot_type
