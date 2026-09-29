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

        self.width = screen.get_width()
        self.height = screen.get_height()

        self.clap_detector = clap_detector

        # ==================================================
        # STATE
        # ==================================================

        self.state = "NAME"

        self.state_start_time = time.monotonic()

        # ==================================================
        # NAME
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
        # MESSAGE
        # ==================================================

        self.message = ""

        # ==================================================
        # FONTS
        # ==================================================

        self.font_title = pygame.font.Font(
            None,
            56
        )

        self.font_large = pygame.font.Font(
            None,
            44
        )

        self.font_medium = pygame.font.Font(
            None,
            30
        )

        self.font_small = pygame.font.Font(
            None,
            22
        )

        # ==================================================
        # RESULTS
        # ==================================================

        self.results_file = (
            "flight_results.csv"
        )

        self.result_saved = False

    # ======================================================
    # BEGIN POWER-UP
    # ======================================================

    def start_power_up(self):

        self.state = "POWER_UP"

        self.state_start_time = (
            time.monotonic()
        )

        self.power = 0.0

        self.double_claps = 0

        print()
        print(
            f"Welcome, {self.player_name}!"
        )
        print(
            "POWER-UP STARTED"
        )
        print(
            "You have 5 seconds."
        )
        print(
            "DOUBLE CLAP as many times as possible."
        )
        print()

    # ======================================================
    # UPDATE
    # ======================================================

    def update(self, dt):

        self.clap_detector.update()

        events = (
            self.clap_detector.get_events()
        )

        # ==================================================
        # NAME INPUT
        # ==================================================

        if self.state == "NAME":
            return

        # ==================================================
        # POWER-UP
        # ==================================================

        if self.state == "POWER_UP":

            for event, strength in events:

                if event == "double_clap":

                    self.double_claps += 1

                    power_gain = (
                        strength * 2.0
                    )

                    self.power += power_gain

                    print(
                        f"DOUBLE CLAP"
                        f" | strength={strength:.2f}"
                        f" | +{power_gain:.2f}"
                        f" power"
                        f" | total={self.power:.2f}"
                    )

            elapsed = (
                time.monotonic()
                - self.state_start_time
            )

            if elapsed >= self.POWER_UP_TIME:

                self.state = "COUNTDOWN"

                self.state_start_time = (
                    time.monotonic()
                )

                print()
                print(
                    "POWER-UP COMPLETE"
                )
                print(
                    f"Power: {self.power:.2f}"
                )
                print(
                    "GET READY TO FLY"
                )

        # ==================================================
        # COUNTDOWN
        # ==================================================

        elif self.state == "COUNTDOWN":

            elapsed = (
                time.monotonic()
                - self.state_start_time
            )

            if elapsed >= self.COUNTDOWN_TIME:

                self.state = "FLIGHT"

                self.state_start_time = (
                    time.monotonic()
                )

                self.airplane.angle = 45

                print()
                print(
                    "FLY!"
                )
                print(
                    "CLAP WHEN YOU WANT TO LAUNCH."
                )
                print()

        # ==================================================
        # FLIGHT
        # ==================================================

        elif self.state == "FLIGHT":

            # ------------------------------------------------
            # Update angle BEFORE processing clap.
            # This means the clap captures the current angle.
            # ------------------------------------------------

            elapsed = (
                time.monotonic()
                - self.state_start_time
            )

            if not self.airplane.launched:

                self.airplane.update_angle(
                    elapsed
                )

                for event, strength in events:

                    if event == "clap":

                        print(
                            f"LAUNCH CLAP"
                            f" | strength={strength:.2f}"
                            f" | angle="
                            f"{self.airplane.angle:.2f}"
                        )

                        self.airplane.launch(
                            self.power,
                            strength
                        )

            else:

                self.airplane.update_physics(
                    dt
                )

                if self.airplane.landed:

                    self.state = "RESULT"

                    self.state_start_time = (
                        time.monotonic()
                    )

                    self.save_result()

        # ==================================================
        # RESULT
        # ==================================================

        elif self.state == "RESULT":

            pass

    # ======================================================
    # KEYBOARD INPUT
    # ======================================================

    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        # ==================================================
        # NAME SCREEN
        # ==================================================

        if self.state == "NAME":

            if event.key == pygame.K_RETURN:

                if self.player_name.strip():

                    self.player_name = (
                        self.player_name.strip()
                    )

                    self.start_power_up()

            elif event.key == pygame.K_BACKSPACE:

                self.player_name = (
                    self.player_name[:-1]
                )

            else:

                # Only add normal printable characters.
                if event.unicode.isprintable():

                    self.player_name += (
                        event.unicode
                    )

    # ======================================================
    # DRAW
    # ======================================================

    def draw(self):

        # ==================================================
        # SKY
        # ==================================================

        self.screen.fill(
            (135, 206, 235)
        )

        # ==================================================
        # CLOUDS
        # ==================================================

        self.draw_cloud(
            150,
            120
        )

        self.draw_cloud(
            550,
            150
        )

        self.draw_cloud(
            900,
            100
        )

        # ==================================================
        # OCEAN
        # ==================================================

        sea_level = (
            self.height * 0.75
        )

        pygame.draw.rect(
            self.screen,
            (45, 145, 205),
            (
                0,
                int(sea_level),
                self.width,
                self.height
                - int(sea_level)
            )
        )

        # ==================================================
        # STATE DRAW
        # ==================================================

        if self.state == "NAME":

            self.draw_name_screen()

        elif self.state == "POWER_UP":

            self.draw_power_up()

        elif self.state == "COUNTDOWN":

            self.draw_countdown()

        elif self.state == "FLIGHT":

            self.draw_flight()

        elif self.state == "RESULT":

            self.draw_result()

        # ==================================================
        # AIRPLANE
        # ==================================================

        if self.state in (
            "COUNTDOWN",
            "FLIGHT",
        ):

            self.airplane.draw(
                self.screen
            )

    # ======================================================
    # NAME SCREEN
    # ======================================================

    def draw_name_screen(self):

        title = self.font_title.render(
            "ACOUSTIC AIRPLANE",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    150
                )
            )
        )

        instruction = self.font_medium.render(
            "ENTER YOUR NAME",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    self.width // 2,
                    250
                )
            )
        )

        # Input box
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (
                self.width // 2 - 250,
                300,
                500,
                60
            ),
            border_radius=8
        )

        name_text = self.font_medium.render(
            self.player_name,
            True,
            (30, 30, 30)
        )

        self.screen.blit(
            name_text,
            (
                self.width // 2 - 230,
                315
            )
        )

        enter = self.font_small.render(
            "Press ENTER to start",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            enter,
            enter.get_rect(
                center=(
                    self.width // 2,
                    410
                )
            )
        )

    # ======================================================
    # POWER-UP DRAW
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

        title = self.font_title.render(
            "POWER UP!",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    80
                )
            )
        )

        timer = self.font_large.render(
            f"{remaining:.1f}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            timer,
            timer.get_rect(
                center=(
                    self.width // 2,
                    160
                )
            )
        )

        instructions = self.font_medium.render(
            "DOUBLE CLAP AS MANY TIMES AS YOU CAN",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            instructions,
            instructions.get_rect(
                center=(
                    self.width // 2,
                    230
                )
            )
        )

        power = self.font_medium.render(
            f"POWER: {self.power:.2f}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            power,
            power.get_rect(
                center=(
                    self.width // 2,
                    300
                )
            )
        )

        claps = self.font_medium.render(
            f"DOUBLE CLAPS: {self.double_claps}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            claps,
            claps.get_rect(
                center=(
                    self.width // 2,
                    345
                )
            )
        )

    # ======================================================
    # COUNTDOWN DRAW
    # ======================================================

    def draw_countdown(self):

        elapsed = (
            time.monotonic()
            - self.state_start_time
        )

        remaining = max(
            0,
            self.COUNTDOWN_TIME
            - elapsed
        )

        number = int(
            remaining
        ) + 1

        if number > 3:
            number = 3

        # DIFFERENT COLOR FROM POWER-UP
        # Orange/yellow countdown
        countdown_color = (
            255,
            180,
            40
        )

        title = self.font_title.render(
            "GET READY!",
            True,
            countdown_color
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    140
                )
            )
        )

        number_text = self.font_title.render(
            str(number),
            True,
            countdown_color
        )

        self.screen.blit(
            number_text,
            number_text.get_rect(
                center=(
                    self.width // 2,
                    280
                )
            )
        )

        instruction = self.font_medium.render(
            "CLAP TO LAUNCH",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    self.width // 2,
                    390
                )
            )
        )

    # ======================================================
    # FLIGHT DRAW
    # ======================================================

    def draw_flight(self):

        # --------------------------------------------------
        # HUD
        # --------------------------------------------------

        power = self.font_small.render(
            f"POWER: {self.power:.2f}",
            True,
            (255, 255, 255)
        )

        angle = self.font_small.render(
            f"ANGLE: "
            f"{self.airplane.angle:.1f}°",
            True,
            (255, 255, 255)
        )

        distance = self.font_small.render(
            f"DISTANCE: "
            f"{self.airplane.flight_distance:.0f}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            power,
            (20, 20)
        )

        self.screen.blit(
            angle,
            (20, 50)
        )

        self.screen.blit(
            distance,
            (20, 80)
        )

        # --------------------------------------------------
        # Waiting for clap
        # --------------------------------------------------

        if not self.airplane.launched:

            instruction = self.font_medium.render(
                "CLAP TO LAUNCH",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                instruction,
                instruction.get_rect(
                    center=(
                        self.width // 2,
                        50
                    )
                )
            )

            self.draw_angle_indicator()

    # ======================================================
    # ANGLE INDICATOR
    # ======================================================

    def draw_angle_indicator(self):

        x = self.width - 50

        top = int(
            self.height * 0.20
        )

        bottom = int(
            self.height * 0.75
        )

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (x, top),
            (x, bottom),
            4
        )

        ratio = (
            self.airplane.angle / 90.0
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
            (255, 80, 80),
            (
                x,
                marker_y
            ),
            14
        )

    # ======================================================
    # RESULT
    # ======================================================

    def draw_result(self):

        title = self.font_title.render(
            "FLIGHT COMPLETE",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    120
                )
            )
        )

        distance = self.font_large.render(
            (
                f"DISTANCE: "
                f"{self.airplane.flight_distance:.1f}"
            ),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            distance,
            distance.get_rect(
                center=(
                    self.width // 2,
                    230
                )
            )
        )

        angle = self.font_medium.render(
            (
                f"Launch angle: "
                f"{self.airplane.launch_angle:.1f}°"
            ),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            angle,
            angle.get_rect(
                center=(
                    self.width // 2,
                    290
                )
            )
        )

        power = self.font_medium.render(
            f"Power: {self.power:.2f}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            power,
            power.get_rect(
                center=(
                    self.width // 2,
                    335
                )
            )
        )

        player = self.font_medium.render(
            self.player_name,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            player,
            player.get_rect(
                center=(
                    self.width // 2,
                    390
                )
            )
        )

        saved = self.font_small.render(
            "Result saved to flight_results.csv",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            saved,
            saved.get_rect(
                center=(
                    self.width // 2,
                    450
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
            "flight_results.csv"
        )

        now = datetime.now()

        row = {
            "name": self.player_name,
            "date": now.strftime(
                "%Y-%m-%d"
            ),
            "time": now.strftime(
                "%H:%M:%S"
            ),
            "distance": round(
                self.airplane.flight_distance,
                2
            ),
            "power": round(
                self.power,
                2
            ),
            "double_claps": self.double_claps,
            "launch_angle": round(
                self.airplane.launch_angle,
                2
            ),
            "launch_clap_strength": round(
                self.airplane.launch_strength,
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

            writer.writerow(row)

    # ======================================================
    # CLOUD
    # ======================================================

    def draw_cloud(self, x, y):

        white = (
            255,
            255,
            255
        )

        pygame.draw.circle(
            self.screen,
            white,
            (x, y),
            35
        )

        pygame.draw.circle(
            self.screen,
            white,
            (
                x + 35,
                y - 15
            ),
            45
        )

        pygame.draw.circle(
            self.screen,
            white,
            (
                x + 70,
                y
            ),
            35
        )

        pygame.draw.rect(
            self.screen,
            white,
            (
                x - 5,
                y,
                80,
                30
            )
        )