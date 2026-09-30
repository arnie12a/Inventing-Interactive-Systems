import math

import pygame


class Airplane:

    def __init__(
        self,
        screen_width,
        screen_height
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # ==================================================
        # START POSITION
        # ==================================================

        self.start_x = (
            screen_width * 0.08
        )

        self.start_y = (
            screen_height * 0.75
        )

        self.x = self.start_x
        self.y = self.start_y

        # ==================================================
        # AIMING
        # ==================================================

        self.angle = 45.0
        self.angle_speed = 2.0

        # ==================================================
        # PHYSICS
        # ==================================================

        self.vx = 0.0
        self.vy = 0.0

        self.gravity = 300.0

        self.launched = False
        self.landed = False

        # ==================================================
        # BOOST
        # ==================================================

        self.boost_available = True

        self.boost_strength = 180.0

        # ==================================================
        # FLIGHT DATA
        # ==================================================

        self.launch_angle = 0.0
        self.launch_strength = 0.0
        self.launch_power = 0.0

        self.flight_distance = 0.0

        self.max_height = self.start_y

        # ==================================================
        # TRAJECTORY
        # ==================================================

        self.trajectory = []

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.x = self.start_x
        self.y = self.start_y

        self.angle = 45.0

        self.vx = 0.0
        self.vy = 0.0

        self.launched = False
        self.landed = False

        self.boost_available = True

        self.launch_angle = 0.0
        self.launch_strength = 0.0
        self.launch_power = 0.0

        self.flight_distance = 0.0

        self.max_height = self.start_y

        self.trajectory = []

    # ======================================================
    # AIMING
    # ======================================================

    def update_angle(
        self,
        elapsed
    ):
        if self.launched:
            return

        # 0 -> 90 -> 0 -> 90
        self.angle = (
            45.0
            + 45.0
            * math.sin(
                elapsed
                * self.angle_speed
            )
        )

        sea_level = (
            self.screen_height
            * 0.75
        )

        top_level = (
            self.screen_height
            * 0.20
        )

        ratio = (
            self.angle
            / 90.0
        )

        self.y = (
            sea_level
            - (
                sea_level
                - top_level
            )
            * ratio
        )

    # ======================================================
    # LAUNCH
    # ======================================================

    def launch(
        self,
        power,
        clap_strength
    ):
        if self.launched:
            return

        self.launched = True
        self.landed = False

        self.launch_angle = (
            self.angle
        )

        self.launch_strength = (
            clap_strength
        )

        self.launch_power = power

        # Keep flight within screen.
        effective_power = min(
            power,
            5.0
        )

        base_speed = 140.0

        initial_speed = (
            base_speed
            * effective_power
            * clap_strength
        )

        initial_speed = max(
            initial_speed,
            25.0
        )

        radians = math.radians(
            self.launch_angle
        )

        self.vx = (
            initial_speed
            * math.cos(radians)
        )

        # Negative is upward in Pygame.
        self.vy = (
            -initial_speed
            * math.sin(radians)
        )

        self.trajectory = [
            (
                self.x,
                self.y
            )
        ]

        self.max_height = self.y

        print()
        print("==============================")
        print("AIRPLANE LAUNCHED")
        print(
            f"Angle: "
            f"{self.launch_angle:.2f}°"
        )
        print(
            f"Clap strength: "
            f"{self.launch_strength:.2f}"
        )
        print(
            f"Power: "
            f"{self.launch_power:.2f}"
        )
        print(
            f"Initial speed: "
            f"{initial_speed:.2f}"
        )
        print("==============================")
        print()

    # ======================================================
    # ONE-TIME BOOST
    # ======================================================

    def boost(self):

        if not self.launched:
            return False

        if self.landed:
            return False

        if not self.boost_available:
            return False

        self.boost_available = False

        # Give airplane an upward impulse.
        self.vy -= (
            self.boost_strength
        )

        print()
        print("==============================")
        print("BOOST ACTIVATED!")
        print("==============================")
        print()

        return True

    # ======================================================
    # PHYSICS
    # ======================================================

    def update_physics(
        self,
        dt
    ):
        if not self.launched:
            return

        if self.landed:
            return

        # ==================================================
        # GRAVITY
        # ==================================================

        self.vy += (
            self.gravity
            * dt
        )

        # ==================================================
        # POSITION
        # ==================================================

        self.x += (
            self.vx
            * dt
        )

        self.y += (
            self.vy
            * dt
        )

        # ==================================================
        # TRAJECTORY
        # ==================================================

        self.trajectory.append(
            (
                self.x,
                self.y
            )
        )

        if len(self.trajectory) > 3000:

            self.trajectory.pop(0)

        # ==================================================
        # MAX HEIGHT
        # ==================================================

        if self.y < self.max_height:

            self.max_height = self.y

        # ==================================================
        # LANDING
        # ==================================================

        sea_level = (
            self.screen_height
            * 0.75
        )

        if self.y >= sea_level:

            self.y = sea_level

            self.landed = True

            self.flight_distance = (
                self.x
                - self.start_x
            )

            print()
            print("==============================")
            print("LANDED")
            print(
                f"Distance: "
                f"{self.flight_distance:.2f}"
            )
            print("==============================")
            print()

    # ======================================================
    # DRAW TRAJECTORY
    # ======================================================

    def draw_trajectory(
        self,
        screen
    ):
        if len(
            self.trajectory
        ) < 2:
            return

        points = [
            (
                int(x),
                int(y)
            )
            for x, y
            in self.trajectory
        ]

        pygame.draw.lines(
            screen,
            (255, 255, 255),
            False,
            points,
            3
        )

    # ======================================================
    # DRAW AIRPLANE
    # ======================================================

    def draw(
        self,
        screen
    ):
        # Draw flight path
        if self.launched:

            self.draw_trajectory(
                screen
            )

        # Transparent airplane canvas
        plane = pygame.Surface(
            (120, 100),
            pygame.SRCALPHA
        )

        # ==================================================
        # BODY
        # ==================================================

        body = [
            (90, 50),
            (25, 35),
            (38, 50),
            (25, 65),
        ]

        pygame.draw.polygon(
            plane,
            (245, 245, 245),
            body
        )

        pygame.draw.polygon(
            plane,
            (25, 25, 25),
            body,
            2
        )

        # ==================================================
        # TOP WING
        # ==================================================

        top_wing = [
            (50, 50),
            (28, 15),
            (62, 40),
        ]

        pygame.draw.polygon(
            plane,
            (180, 210, 240),
            top_wing
        )

        # ==================================================
        # BOTTOM WING
        # ==================================================

        bottom_wing = [
            (50, 50),
            (28, 85),
            (62, 60),
        ]

        pygame.draw.polygon(
            plane,
            (180, 210, 240),
            bottom_wing
        )

        # ==================================================
        # ROTATION
        # ==================================================

        if not self.launched:

            rotation = self.angle

        else:

            rotation = math.degrees(
                math.atan2(
                    -self.vy,
                    self.vx
                )
            )

        rotated = (
            pygame.transform.rotate(
                plane,
                rotation
            )
        )

        rect = (
            rotated.get_rect(
                center=(
                    int(self.x),
                    int(self.y)
                )
            )
        )

        screen.blit(
            rotated,
            rect
        )