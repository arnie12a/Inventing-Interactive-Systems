import math
import pygame


class Airplane:

    def __init__(self, screen_width, screen_height):

        self.screen_width = screen_width
        self.screen_height = screen_height

        # ==================================================
        # START POSITION
        # ==================================================

        self.start_x = 150.0
        self.start_y = screen_height * 0.75

        self.x = self.start_x
        self.y = self.start_y

        # ==================================================
        # AIMING ANGLE
        # ==================================================

        self.angle = 45.0

        self.angle_speed = 2.0

        # ==================================================
        # PHYSICS
        # ==================================================

        self.vx = 0.0
        self.vy = 0.0

        # Pixels per second squared
        self.gravity = 350.0

        self.launched = False
        self.landed = False

        # ==================================================
        # FLIGHT DATA
        # ==================================================

        self.launch_angle = 0.0

        self.launch_strength = 0.0

        self.launch_power = 0.0

        # This is the value game.py was looking for.
        self.flight_distance = 0.0

        self.max_height = self.start_y

    # ======================================================
    # UPDATE AIMING ANGLE
    # ======================================================

    def update_angle(self, elapsed):

        # Do not change angle after launch
        if self.launched:
            return

        # Oscillate continuously:
        #
        # 0 -> 90 -> 0 -> 90...
        #
        self.angle = (
            45.0
            + 45.0
            * math.sin(
                elapsed * self.angle_speed
            )
        )

        # ==================================================
        # Convert angle into screen position
        # ==================================================

        sea_level = (
            self.screen_height * 0.75
        )

        top_level = (
            self.screen_height * 0.20
        )

        ratio = self.angle / 90.0

        self.y = (
            sea_level
            - (
                sea_level - top_level
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

        # Prevent launching twice
        if self.launched:
            return

        self.launched = True

        self.landed = False

        # --------------------------------------------------
        # Save launch information
        # --------------------------------------------------

        self.launch_angle = self.angle

        self.launch_strength = clap_strength

        self.launch_power = power

        # --------------------------------------------------
        # Starting velocity
        # --------------------------------------------------

        base_speed = 250.0

        initial_speed = (
            base_speed
            * power
            * clap_strength
        )

        # --------------------------------------------------
        # Convert angle into velocity components
        # --------------------------------------------------

        radians = math.radians(
            self.launch_angle
        )

        # Horizontal velocity
        self.vx = (
            initial_speed
            * math.cos(radians)
        )

        # Vertical velocity
        #
        # Pygame's Y axis increases downward,
        # so upward velocity is negative.
        #
        self.vy = (
            -initial_speed
            * math.sin(radians)
        )

        # Reset flight measurements
        self.flight_distance = 0.0

        self.max_height = self.y

        print()
        print("==============================")
        print("AIRPLANE LAUNCHED")
        print(
            f"Angle: "
            f"{self.launch_angle:.2f} degrees"
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
            f"Initial velocity: "
            f"{initial_speed:.2f}"
        )
        print("==============================")
        print()

    # ======================================================
    # PHYSICS UPDATE
    # ======================================================

    def update_physics(self, dt):

        if not self.launched:
            return

        if self.landed:
            return

        # ==================================================
        # APPLY GRAVITY
        # ==================================================

        self.vy += self.gravity * dt

        # ==================================================
        # UPDATE POSITION
        # ==================================================

        self.x += self.vx * dt

        self.y += self.vy * dt

        # ==================================================
        # TRACK MAX HEIGHT
        # ==================================================

        if self.y < self.max_height:

            self.max_height = self.y

        # ==================================================
        # CHECK FOR LANDING
        # ==================================================

        sea_level = (
            self.screen_height * 0.75
        )

        if self.y >= sea_level:

            self.y = sea_level

            self.landed = True

            # ----------------------------------------------
            # Final distance
            # ----------------------------------------------

            self.flight_distance = (
                self.x - self.start_x
            )

            print()
            print("==============================")
            print("LANDED")
            print(
                f"Flight distance: "
                f"{self.flight_distance:.2f}"
            )
            print(
                f"Launch angle: "
                f"{self.launch_angle:.2f}"
            )
            print("==============================")
            print()

    # ======================================================
    # DRAW
    # ======================================================

    def draw(self, screen):

        # --------------------------------------------------
        # Create airplane surface
        # --------------------------------------------------

        plane = pygame.Surface(
            (120, 100),
            pygame.SRCALPHA
        )

        # --------------------------------------------------
        # Body
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Top wing
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Bottom wing
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Rotation
        # --------------------------------------------------

        if not self.launched:

            # During aiming, use selected angle
            rotation = self.angle

        else:

            # During flight, point airplane in direction
            # of travel.
            rotation = math.degrees(
                math.atan2(
                    -self.vy,
                    self.vx
                )
            )

        rotated = pygame.transform.rotate(
            plane,
            rotation
        )

        rect = rotated.get_rect(
            center=(
                int(self.x),
                int(self.y)
            )
        )

        screen.blit(
            rotated,
            rect
        )