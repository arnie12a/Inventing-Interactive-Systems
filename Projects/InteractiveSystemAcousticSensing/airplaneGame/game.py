import csv
import os
import time
from datetime import datetime

import pygame

from airplane import Airplane


class Game:

    POWER_UP_TIME = 5.0
    COUNTDOWN_TIME = 3.0

    def __init__(
        self,
        screen,
        clap_detector
    ):
        self.screen = screen

        self.width = (
            screen.get_width()
        )

        self.height = (
            screen.get_height()
        )

        self.clap_detector = (
            clap_detector
        )

        # ==================================================
        # STATE
        # ==================================================

        self.state = "NAME"

        self.state_start_time = (
            time.monotonic()
        )

        # ==================================================
        # PLAYER
        # ==================================================

        self.player_name = ""

        # ==================================================
        # POWER
        # ==================================================

        self.power = 0.0
        self.double_claps = 0

        # ==================================================
        # AIRPLANE
        # ==================================================

        self.airplane = Airplane(
            self.width,
            self.height
        )

        # ==================================================
        # RESULTS
        # ==================================================

        self.results_file = (
            "flight_results.csv"
        )

        self.result_saved = False

        self.leaderboard = []

        # ==================================================
        # RESPONSIVE FONT SIZES
        # ==================================================

        scale = (
            self.height / 1000
        )

        self.font_title = pygame.font.Font(
            None,
            max(
                42,
                int(64 * scale)
            )
        )

        self.font_large = pygame.font.Font(
            None,
            max(
                34,
                int(48 * scale)
            )
        )

        self.font_medium = pygame.font.Font(
            None,
            max(
                24,
                int(32 * scale)
            )
        )

        self.font_small = pygame.font.Font(
            None,
            max(
                18,
                int(24 * scale)
            )
        )

        # ==================================================
        # COLORS
        # ==================================================

        self.sky = (
            125,
            195,
            235
        )

        self.ocean = (
            38,
            125,
            180
        )

        self.water_line = (
            65,
            155,
            205
        )

        self.white = (
            245,
            248,
            250
        )

        self.dark = (
            18,
            30,
            45
        )

        self.panel = (
            24,
            40,
            60
        )

        self.accent = (
            80,
            190,
            255
        )

        self.warning = (
            255,
            185,
            60
        )

        self.success = (
            80,
            220,
            140
        )

        self.muted = (
            175,
            195,
            210
        )

    # ======================================================
    # START POWER UP
    # ======================================================

    def start_power_up(self):

        self.state = (
            "POWER_UP"
        )

        self.state_start_time = (
            time.monotonic()
        )

        self.power = 0.0

        self.double_claps = 0

        self.result_saved = False

        self.leaderboard = []

        self.airplane.reset()

        print()
        print(
            f"Welcome, "
            f"{self.player_name}!"
        )
        print(
            "POWER-UP STARTED"
        )
        print()

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        dt
    ):
        # Process microphone
        self.clap_detector.update()

        events = (
            self.clap_detector
            .get_events()
        )

        # ==================================================
        # NAME
        # ==================================================

        if self.state == "NAME":
            return

        # ==================================================
        # POWER UP
        # ==================================================

        if self.state == "POWER_UP":

            for event, strength in events:

                if (
                    event
                    == "double_clap"
                ):
                    self.double_claps += 1

                    power_gain = (
                        strength
                        * 2.0
                    )

                    self.power += (
                        power_gain
                    )

                    print(
                        f"DOUBLE CLAP"
                        f" | strength="
                        f"{strength:.2f}"
                        f" | +"
                        f"{power_gain:.2f}"
                        f" power"
                        f" | total="
                        f"{self.power:.2f}"
                    )

            elapsed = (
                time.monotonic()
                - self.state_start_time
            )

            if (
                elapsed
                >= self.POWER_UP_TIME
            ):
                self.state = (
                    "COUNTDOWN"
                )

                self.state_start_time = (
                    time.monotonic()
                )

                print()
                print(
                    "POWER-UP COMPLETE"
                )
                print(
                    f"Power: "
                    f"{self.power:.2f}"
                )
                print()

        # ==================================================
        # COUNTDOWN
        # ==================================================

        elif self.state == "COUNTDOWN":

            elapsed = (
                time.monotonic()
                - self.state_start_time
            )

            if (
                elapsed
                >= self.COUNTDOWN_TIME
            ):
                self.state = (
                    "FLIGHT"
                )

                self.state_start_time = (
                    time.monotonic()
                )

                print(
                    "CLAP TO LAUNCH"
                )

        # ==================================================
        # FLIGHT
        # ==================================================

        elif self.state == "FLIGHT":

            # ==============================================
            # BEFORE LAUNCH
            # ==============================================

            if not self.airplane.launched:

                elapsed = (
                    time.monotonic()
                    - self.state_start_time
                )

                self.airplane.update_angle(
                    elapsed
                )

                for event, strength in events:

                    # Single clap launches
                    if event == "clap":

                        print(
                            f"LAUNCH CLAP"
                            f" | angle="
                            f"{self.airplane.angle:.2f}"
                            f" | strength="
                            f"{strength:.2f}"
                        )

                        self.airplane.launch(
                            self.power,
                            strength
                        )

            # ==============================================
            # AFTER LAUNCH
            # ==============================================

            else:

                # Double clap gives ONE boost.
                for event, strength in events:

                    if (
                        event
                        == "double_clap"
                    ):
                        boosted = (
                            self.airplane
                            .boost()
                        )

                        if boosted:

                            print(
                                f"Double clap "
                                f"boost strength: "
                                f"{strength:.2f}"
                            )

                # Physics continues regardless
                # of whether the player boosted.
                self.airplane.update_physics(
                    dt
                )

                # ==========================================
                # LANDING
                # ==========================================

                if self.airplane.landed:

                    self.save_result()

                    self.load_leaderboard()

                    self.state = (
                        "RESULT"
                    )

                    self.state_start_time = (
                        time.monotonic()
                    )

    # ======================================================
    # KEYBOARD EVENTS
    # ======================================================

    def handle_event(
        self,
        event
    ):
        if (
            event.type
            != pygame.KEYDOWN
        ):
            return

        # ==================================================
        # NAME INPUT
        # ==================================================

        if self.state == "NAME":

            if (
                event.key
                == pygame.K_RETURN
            ):
                if (
                    self.player_name
                    .strip()
                ):
                    self.player_name = (
                        self.player_name
                        .strip()
                    )

                    self.start_power_up()

            elif (
                event.key
                == pygame.K_BACKSPACE
            ):
                self.player_name = (
                    self.player_name[:-1]
                )

            else:

                if (
                    event.unicode
                    .isprintable()
                ):
                    # Limit name length
                    if (
                        len(
                            self.player_name
                        )
                        < 24
                    ):
                        self.player_name += (
                            event.unicode
                        )

        # ==================================================
        # RESULT
        # ==================================================

        elif self.state == "RESULT":

            if (
                event.key
                == pygame.K_RETURN
            ):
                self.player_name = ""

                self.state = "NAME"

                self.state_start_time = (
                    time.monotonic()
                )

    # ======================================================
    # DRAW
    # ======================================================

    def draw(self):

        self.screen.fill(
            self.sky
        )

        self.draw_background()

        # ==================================================
        # NAME
        # ==================================================

        if self.state == "NAME":

            self.draw_name()

            return

        # ==================================================
        # POWER UP
        # ==================================================

        if self.state == "POWER_UP":

            self.draw_power_up()

        # ==================================================
        # COUNTDOWN
        # ==================================================

        elif self.state == "COUNTDOWN":

            self.draw_countdown()

        # ==================================================
        # FLIGHT
        # ==================================================

        elif self.state == "FLIGHT":

            self.draw_flight()

        # ==================================================
        # RESULT
        # ==================================================

        elif self.state == "RESULT":

            self.draw_result()

        # ==================================================
        # AIRPLANE
        # ==================================================

        if self.state in (
            "COUNTDOWN",
            "FLIGHT"
        ):
            self.airplane.draw(
                self.screen
            )

    # ======================================================
    # BACKGROUND
    # ======================================================

    def draw_background(self):

        sea_level = int(
            self.height
            * 0.75
        )

        # Ocean
        pygame.draw.rect(
            self.screen,
            self.ocean,
            (
                0,
                sea_level,
                self.width,
                self.height
                - sea_level
            )
        )

        # Water lines
        for y in range(
            sea_level + 25,
            self.height,
            35
        ):
            pygame.draw.line(
                self.screen,
                self.water_line,
                (
                    0,
                    y
                ),
                (
                    self.width,
                    y
                ),
                2
            )

        # Clouds relative to screen size
        cloud_positions = [
            (
                int(
                    self.width * 0.10
                ),
                int(
                    self.height * 0.15
                )
            ),
            (
                int(
                    self.width * 0.35
                ),
                int(
                    self.height * 0.20
                )
            ),
            (
                int(
                    self.width * 0.62
                ),
                int(
                    self.height * 0.12
                )
            ),
            (
                int(
                    self.width * 0.82
                ),
                int(
                    self.height * 0.18
                )
            ),
        ]

        for x, y in cloud_positions:

            self.draw_cloud(
                x,
                y
            )

    # ======================================================
    # NAME SCREEN
    # ======================================================

    def draw_name(self):

        panel_width = int(
            self.width * 0.55
        )

        panel_height = int(
            self.height * 0.60
        )

        panel = pygame.Rect(
            (
                self.width
                - panel_width
            ) // 2,
            (
                self.height
                - panel_height
            ) // 2,
            panel_width,
            panel_height
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            panel,
            border_radius=24
        )

        title = (
            self.font_title.render(
                "ACOUSTIC AIRPLANE",
                True,
                self.white
            )
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.18
                    )
                )
            )
        )

        subtitle = (
            self.font_small.render(
                (
                    "Clap. Launch. "
                    "Boost. Fly."
                ),
                True,
                self.muted
            )
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.29
                    )
                )
            )
        )

        prompt = (
            self.font_medium.render(
                "ENTER YOUR NAME",
                True,
                self.accent
            )
        )

        self.screen.blit(
            prompt,
            prompt.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.42
                    )
                )
            )
        )

        input_width = int(
            panel.width * 0.65
        )

        input_height = max(
            55,
            int(
                self.height
                * 0.065
            )
        )

        input_box = pygame.Rect(
            (
                self.width
                - input_width
            ) // 2,
            panel.y
            + int(
                panel.height
                * 0.50
            ),
            input_width,
            input_height
        )

        pygame.draw.rect(
            self.screen,
            self.white,
            input_box,
            border_radius=10
        )

        name_surface = (
            self.font_medium.render(
                self.player_name,
                True,
                self.dark
            )
        )

        self.screen.blit(
            name_surface,
            (
                input_box.x + 20,
                input_box.centery
                - (
                    name_surface
                    .get_height()
                    // 2
                )
            )
        )

        enter = (
            self.font_small.render(
                "Press ENTER to begin",
                True,
                self.muted
            )
        )

        self.screen.blit(
            enter,
            enter.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.75
                    )
                )
            )
        )

    # ======================================================
    # POWER-UP SCREEN
    # ======================================================

    def draw_power_up(self):

        elapsed = (
            time.monotonic()
            - self.state_start_time
        )

        remaining = max(
            0.0,
            self.POWER_UP_TIME
            - elapsed
        )

        panel_width = int(
            self.width * 0.60
        )

        panel_height = int(
            self.height * 0.58
        )

        panel = pygame.Rect(
            (
                self.width
                - panel_width
            ) // 2,
            int(
                self.height
                * 0.10
            ),
            panel_width,
            panel_height
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            panel,
            border_radius=24
        )

        title = (
            self.font_title.render(
                "POWER UP",
                True,
                self.white
            )
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.13
                    )
                )
            )
        )

        timer = (
            self.font_title.render(
                f"{remaining:.1f}",
                True,
                self.accent
            )
        )

        self.screen.blit(
            timer,
            timer.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.29
                    )
                )
            )
        )

        instruction = (
            self.font_medium.render(
                (
                    "DOUBLE CLAP "
                    "TO BUILD POWER"
                ),
                True,
                self.white
            )
        )

        self.screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.43
                    )
                )
            )
        )

        # ==================================================
        # POWER BAR
        # ==================================================

        bar_width = int(
            panel.width * 0.65
        )

        bar_height = max(
            20,
            int(
                self.height
                * 0.025
            )
        )

        bar = pygame.Rect(
            (
                self.width
                - bar_width
            ) // 2,
            panel.y
            + int(
                panel.height
                * 0.54
            ),
            bar_width,
            bar_height
        )

        pygame.draw.rect(
            self.screen,
            (
                45,
                58,
                72
            ),
            bar,
            border_radius=bar_height // 2
        )

        # Visual bar caps at power 10.
        power_ratio = min(
            self.power / 10.0,
            1.0
        )

        fill_width = int(
            bar.width
            * power_ratio
        )

        if fill_width > 0:

            pygame.draw.rect(
                self.screen,
                self.accent,
                (
                    bar.x,
                    bar.y,
                    fill_width,
                    bar.height
                ),
                border_radius=(
                    bar_height // 2
                )
            )

        power_text = (
            self.font_medium.render(
                (
                    f"POWER  "
                    f"{self.power:.2f}"
                ),
                True,
                self.white
            )
        )

        self.screen.blit(
            power_text,
            power_text.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.68
                    )
                )
            )
        )

        clap_text = (
            self.font_small.render(
                (
                    f"DOUBLE CLAPS  "
                    f"{self.double_claps}"
                ),
                True,
                self.muted
            )
        )

        self.screen.blit(
            clap_text,
            clap_text.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.78
                    )
                )
            )
        )

        hint = (
            self.font_small.render(
                (
                    "Stronger claps "
                    "generate more power"
                ),
                True,
                self.muted
            )
        )

        self.screen.blit(
            hint,
            hint.get_rect(
                center=(
                    self.width // 2,
                    panel.y
                    + int(
                        panel.height
                        * 0.87
                    )
                )
            )
        )

    # ======================================================
    # COUNTDOWN
    # ======================================================

    def draw_countdown(self):

        elapsed = (
            time.monotonic()
            - self.state_start_time
        )

        remaining = max(
            0.0,
            self.COUNTDOWN_TIME
            - elapsed
        )

        number = min(
            int(remaining) + 1,
            3
        )

        # Semi-transparent overlay
        overlay = pygame.Surface(
            (
                self.width,
                self.height
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (
                10,
                20,
                35,
                130
            )
        )

        self.screen.blit(
            overlay,
            (
                0,
                0
            )
        )

        title = (
            self.font_title.render(
                "GET READY",
                True,
                self.warning
            )
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    int(
                        self.height
                        * 0.28
                    )
                )
            )
        )

        number_surface = (
            self.font_title.render(
                str(number),
                True,
                self.warning
            )
        )

        self.screen.blit(
            number_surface,
            number_surface.get_rect(
                center=(
                    self.width // 2,
                    int(
                        self.height
                        * 0.43
                    )
                )
            )
        )

        instruction = (
            self.font_medium.render(
                "SINGLE CLAP TO LAUNCH",
                True,
                self.white
            )
        )

        self.screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    self.width // 2,
                    int(
                        self.height
                        * 0.57
                    )
                )
            )
        )

    # ======================================================
    # FLIGHT
    # ======================================================

    def draw_flight(self):

        # ==================================================
        # HUD
        # ==================================================

        hud_height = max(
            90,
            int(
                self.height
                * 0.12
            )
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            (
                0,
                0,
                self.width,
                hud_height
            )
        )

        padding = int(
            self.width
            * 0.02
        )

        power_surface = (
            self.font_small.render(
                (
                    f"POWER  "
                    f"{self.power:.2f}"
                ),
                True,
                self.white
            )
        )

        angle_surface = (
            self.font_small.render(
                (
                    f"ANGLE  "
                    f"{self.airplane.angle:.1f}°"
                ),
                True,
                self.white
            )
        )

        current_distance = max(
            0.0,
            self.airplane.x
            - self.airplane.start_x
        )

        distance_surface = (
            self.font_small.render(
                (
                    f"DISTANCE  "
                    f"{current_distance:.0f}"
                ),
                True,
                self.white
            )
        )

        self.screen.blit(
            power_surface,
            (
                padding,
                15
            )
        )

        self.screen.blit(
            angle_surface,
            (
                padding,
                42
            )
        )

        self.screen.blit(
            distance_surface,
            (
                padding,
                69
            )
        )

        # ==================================================
        # BEFORE LAUNCH
        # ==================================================

        if not self.airplane.launched:

            launch = (
                self.font_medium.render(
                    "SINGLE CLAP TO LAUNCH",
                    True,
                    self.white
                )
            )

            self.screen.blit(
                launch,
                launch.get_rect(
                    center=(
                        self.width // 2,
                        hud_height // 3
                    )
                )
            )

            boost_hint = (
                self.font_small.render(
                    (
                        "After launch: "
                        "DOUBLE CLAP for "
                        "one boost"
                    ),
                    True,
                    self.warning
                )
            )

            self.screen.blit(
                boost_hint,
                boost_hint.get_rect(
                    center=(
                        self.width // 2,
                        int(
                            hud_height
                            * 0.72
                        )
                    )
                )
            )

            self.draw_angle_indicator()

        # ==================================================
        # AFTER LAUNCH
        # ==================================================

        else:

            if (
                self.airplane
                .boost_available
            ):
                boost_text = (
                    self.font_small.render(
                        (
                            "BOOST READY  •  "
                            "DOUBLE CLAP"
                        ),
                        True,
                        self.warning
                    )
                )

            else:

                boost_text = (
                    self.font_small.render(
                        "BOOST USED",
                        True,
                        self.muted
                    )
                )

            self.screen.blit(
                boost_text,
                boost_text.get_rect(
                    center=(
                        self.width // 2,
                        hud_height // 2
                    )
                )
            )

    # ======================================================
    # ANGLE INDICATOR
    # ======================================================

    def draw_angle_indicator(self):

        x = int(
            self.width
            * 0.96
        )

        top = int(
            self.height
            * 0.18
        )

        bottom = int(
            self.height
            * 0.75
        )

        pygame.draw.line(
            self.screen,
            self.white,
            (
                x,
                top
            ),
            (
                x,
                bottom
            ),
            3
        )

        ratio = (
            self.airplane.angle
            / 90.0
        )

        marker_y = int(
            bottom
            - (
                bottom - top
            )
            * ratio
        )

        pygame.draw.circle(
            self.screen,
            (
                255,
                90,
                90
            ),
            (
                x,
                marker_y
            ),
            12
        )

        label_90 = (
            self.font_small.render(
                "90°",
                True,
                self.white
            )
        )

        label_0 = (
            self.font_small.render(
                "0°",
                True,
                self.white
            )
        )

        self.screen.blit(
            label_90,
            (
                x - 55,
                top - 10
            )
        )

        self.screen.blit(
            label_0,
            (
                x - 45,
                bottom - 10
            )
        )

    # ======================================================
    # RESULT
    # ======================================================

    def draw_result(self):

        overlay = pygame.Surface(
            (
                self.width,
                self.height
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (
                10,
                20,
                35,
                175
            )
        )

        self.screen.blit(
            overlay,
            (
                0,
                0
            )
        )

        card_width = int(
            self.width * 0.70
        )

        card_height = int(
            self.height * 0.80
        )

        card = pygame.Rect(
            (
                self.width
                - card_width
            ) // 2,
            (
                self.height
                - card_height
            ) // 2,
            card_width,
            card_height
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            card,
            border_radius=24
        )

        title = (
            self.font_title.render(
                "FLIGHT COMPLETE",
                True,
                self.success
            )
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    card.y
                    + int(
                        card.height
                        * 0.09
                    )
                )
            )
        )

        name_surface = (
            self.font_medium.render(
                self.player_name,
                True,
                self.white
            )
        )

        self.screen.blit(
            name_surface,
            name_surface.get_rect(
                center=(
                    self.width // 2,
                    card.y
                    + int(
                        card.height
                        * 0.17
                    )
                )
            )
        )

        # ==================================================
        # DISTANCE
        # ==================================================

        distance_surface = (
            self.font_title.render(
                (
                    f"{self.airplane.flight_distance:.1f}"
                ),
                True,
                self.accent
            )
        )

        self.screen.blit(
            distance_surface,
            distance_surface.get_rect(
                center=(
                    self.width // 2,
                    card.y
                    + int(
                        card.height
                        * 0.28
                    )
                )
            )
        )

        distance_label = (
            self.font_small.render(
                "DISTANCE",
                True,
                self.muted
            )
        )

        self.screen.blit(
            distance_label,
            distance_label.get_rect(
                center=(
                    self.width // 2,
                    card.y
                    + int(
                        card.height
                        * 0.34
                    )
                )
            )
        )

        # ==================================================
        # STATS
        # ==================================================

        stats = (
            self.font_small.render(
                (
                    f"ANGLE  "
                    f"{self.airplane.launch_angle:.1f}°"
                    f"     "
                    f"POWER  "
                    f"{self.power:.2f}"
                    f"     "
                    f"CLAP STRENGTH  "
                    f"{self.airplane.launch_strength:.2f}"
                ),
                True,
                self.white
            )
        )

        self.screen.blit(
            stats,
            stats.get_rect(
                center=(
                    self.width // 2,
                    card.y
                    + int(
                        card.height
                        * 0.41
                    )
                )
            )
        )

        # ==================================================
        # LEADERBOARD
        # ==================================================

        leaderboard_title = (
            self.font_medium.render(
                "LEADERBOARD",
                True,
                self.warning
            )
        )

        self.screen.blit(
            leaderboard_title,
            leaderboard_title.get_rect(
                center=(
                    self.width // 2,
                    card.y
                    + int(
                        card.height
                        * 0.50
                    )
                )
            )
        )

        start_y = (
            card.y
            + int(
                card.height
                * 0.57
            )
        )

        row_spacing = max(
            30,
            int(
                self.height
                * 0.04
            )
        )

        for index, row in enumerate(
            self.leaderboard[:5]
        ):
            current = (
                row["name"]
                == self.player_name
                and
                abs(
                    float(
                        row["distance"]
                    )
                    - self.airplane
                    .flight_distance
                )
                < 0.02
            )

            color = (
                self.warning
                if current
                else self.white
            )

            row_surface = (
                self.font_small.render(
                    (
                        f"{index + 1}.  "
                        f"{row['name']}"
                        f"     "
                        f"{float(row['distance']):.1f}"
                    ),
                    True,
                    color
                )
            )

            self.screen.blit(
                row_surface,
                row_surface.get_rect(
                    center=(
                        self.width // 2,
                        start_y
                        + (
                            index
                            * row_spacing
                        )
                    )
                )
            )

        continue_surface = (
            self.font_small.render(
                (
                    "Press ENTER "
                    "to play again"
                ),
                True,
                self.muted
            )
        )

        self.screen.blit(
            continue_surface,
            continue_surface.get_rect(
                center=(
                    self.width // 2,
                    card.bottom
                    - int(
                        card.height
                        * 0.06
                    )
                )
            )
        )

    # ======================================================
    # SAVE RESULT
    # ======================================================

    def save_result(self):

        if self.result_saved:
            return

        self.result_saved = True

        file_exists = os.path.exists(
            self.results_file
        )

        now = datetime.now()

        row = {
            "name":
                self.player_name,

            "date":
                now.strftime(
                    "%Y-%m-%d"
                ),

            "time":
                now.strftime(
                    "%H:%M:%S"
                ),

            "distance":
                round(
                    self.airplane
                    .flight_distance,
                    2
                ),

            "power":
                round(
                    self.power,
                    2
                ),

            "double_claps":
                self.double_claps,

            "launch_angle":
                round(
                    self.airplane
                    .launch_angle,
                    2
                ),

            "launch_clap_strength":
                round(
                    self.airplane
                    .launch_strength,
                    3
                ),
        }

        with open(
            self.results_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=row.keys()
            )

            if not file_exists:

                writer.writeheader()

            writer.writerow(
                row
            )

    # ======================================================
    # LEADERBOARD
    # ======================================================

    def load_leaderboard(self):

        self.leaderboard = []

        if not os.path.exists(
            self.results_file
        ):
            return

        with open(
            self.results_file,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                try:
                    row["distance"] = (
                        float(
                            row[
                                "distance"
                            ]
                        )
                    )

                    self.leaderboard.append(
                        row
                    )

                except (
                    ValueError,
                    KeyError
                ):
                    continue

        self.leaderboard.sort(
            key=lambda row: (
                row["distance"]
            ),
            reverse=True
        )

    # ======================================================
    # CLOUD
    # ======================================================

    def draw_cloud(
        self,
        x,
        y
    ):
        scale = max(
            0.7,
            self.height / 1000
        )

        r1 = int(
            30 * scale
        )

        r2 = int(
            38 * scale
        )

        pygame.draw.circle(
            self.screen,
            self.white,
            (
                x,
                y
            ),
            r1
        )

        pygame.draw.circle(
            self.screen,
            self.white,
            (
                x + r1,
                y - int(
                    12 * scale
                )
            ),
            r2
        )

        pygame.draw.circle(
            self.screen,
            self.white,
            (
                x + r1 * 2,
                y
            ),
            r1
        )

        pygame.draw.rect(
            self.screen,
            self.white,
            (
                x - r1,
                y,
                r1 * 4,
                r1
            )
        )