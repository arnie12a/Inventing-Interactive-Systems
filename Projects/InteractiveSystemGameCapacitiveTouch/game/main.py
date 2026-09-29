import pygame
import csv

from pathlib import Path
from datetime import datetime

from serial_controller import SerialController

from obstacles import (
    get_random_course,
    create_finish_line,
    draw_course
)


# =====================================================
# GAME SETTINGS
# =====================================================

WIDTH = 1000
HEIGHT = 700

PLAYER_SIZE = 35

SPEED = 5


# =====================================================
# COLORS
# =====================================================

BACKGROUND_COLOR = (240, 240, 240)

PLAYER_COLOR = (0, 100, 255)

TEXT_COLOR = (20, 20, 20)


# =====================================================
# SCORE FILE
# =====================================================

SCORE_FILE = (
    Path(__file__).resolve().parent
    / "scores.csv"
)


# =====================================================
# SERIAL
# =====================================================

serial_controller = SerialController(
    port="/dev/cu.usbserial-0001",
    baud_rate=115200
)


# =====================================================
# PYGAME
# =====================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "ESP32 Obstacle Course"
)

clock = pygame.time.Clock()


# =====================================================
# FONTS
# =====================================================

title_font = pygame.font.Font(
    None,
    64
)

large_font = pygame.font.Font(
    None,
    48
)

font = pygame.font.Font(
    None,
    36
)

small_font = pygame.font.Font(
    None,
    28
)


# =====================================================
# CURRENT COURSE
# =====================================================

obstacles = get_random_course()

finish_line = create_finish_line()


# =====================================================
# GAME STATES
# =====================================================

NAME_ENTRY = "NAME_ENTRY"
COUNTDOWN = "COUNTDOWN"
PLAYING = "PLAYING"
FINISHED = "FINISHED"

game_state = NAME_ENTRY


# =====================================================
# PLAYER
# =====================================================

player_x = WIDTH // 2 - PLAYER_SIZE // 2
player_y = HEIGHT - 80


# =====================================================
# PLAYER NAME
# =====================================================

player_name = ""


# =====================================================
# TIMER
# =====================================================

start_time = None
finish_time = None
final_score = None


# =====================================================
# COUNTDOWN
# =====================================================

countdown_start = None

COUNTDOWN_LENGTH = 3


# =====================================================
# CURRENT COMMAND
# =====================================================

command = "NONE"


# =====================================================
# GET PLAYER RECT
# =====================================================

def get_player_rect():

    return pygame.Rect(
        int(player_x),
        int(player_y),
        PLAYER_SIZE,
        PLAYER_SIZE
    )


# =====================================================
# RESET PLAYER
# =====================================================

def reset_player():

    global player_x
    global player_y

    player_x = (
        WIDTH // 2
        - PLAYER_SIZE // 2
    )

    player_y = HEIGHT - 80


# =====================================================
# START NEW GAME
# =====================================================

def start_game():

    global game_state
    global countdown_start
    global start_time
    global finish_time
    global final_score

    global obstacles
    global finish_line

    # -----------------------------------------------
    # Choose a NEW random course
    # -----------------------------------------------

    obstacles = get_random_course()

    finish_line = create_finish_line()

    # -----------------------------------------------
    # Reset player
    # -----------------------------------------------

    reset_player()

    # -----------------------------------------------
    # Reset timer
    # -----------------------------------------------

    start_time = None
    finish_time = None
    final_score = None

    # -----------------------------------------------
    # Start countdown
    # -----------------------------------------------

    countdown_start = pygame.time.get_ticks()

    game_state = COUNTDOWN


# =====================================================
# SAVE SCORE
# =====================================================

def save_score():

    file_exists = SCORE_FILE.exists()

    with open(
        SCORE_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "name",
                "date",
                "score_seconds"
            ])

        writer.writerow([
            player_name,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            f"{final_score:.2f}"
        ])


    print(
        f"Score saved to {SCORE_FILE}"
    )


# =====================================================
# COLLISION
# =====================================================

def collides_with_obstacle(rect):

    for obstacle in obstacles:

        if rect.colliderect(obstacle):

            return True

    return False


# =====================================================
# MOVE PLAYER
# =====================================================

def move_player(dx, dy):

    global player_x
    global player_y


    # -----------------------------------------------
    # Horizontal movement
    # -----------------------------------------------

    new_x = player_x + dx

    test_rect = pygame.Rect(
        int(new_x),
        int(player_y),
        PLAYER_SIZE,
        PLAYER_SIZE
    )

    if not collides_with_obstacle(test_rect):

        player_x = new_x


    # -----------------------------------------------
    # Vertical movement
    # -----------------------------------------------

    new_y = player_y + dy

    test_rect = pygame.Rect(
        int(player_x),
        int(new_y),
        PLAYER_SIZE,
        PLAYER_SIZE
    )

    if not collides_with_obstacle(test_rect):

        player_y = new_y


# =====================================================
# DRAW CENTERED TEXT
# =====================================================

def draw_centered_text(
    text,
    font,
    y,
    color=TEXT_COLOR
):

    surface = font.render(
        text,
        True,
        color
    )

    x = (
        WIDTH
        - surface.get_width()
    ) // 2

    screen.blit(
        surface,
        (x, y)
    )


# =====================================================
# MAIN LOOP
# =====================================================

running = True


while running:

    # =================================================
    # EVENTS
    # =================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # ---------------------------------------------
        # NAME ENTRY
        # ---------------------------------------------

        if game_state == NAME_ENTRY:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    if player_name.strip():

                        start_game()


                elif event.key == pygame.K_BACKSPACE:

                    player_name = (
                        player_name[:-1]
                    )


                else:

                    if event.unicode.isprintable():

                        player_name += (
                            event.unicode
                        )


        # ---------------------------------------------
        # FINISHED
        # ---------------------------------------------

        elif game_state == FINISHED:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    player_name = ""

                    game_state = NAME_ENTRY


                elif event.key == pygame.K_ESCAPE:

                    running = False


    # =================================================
    # COUNTDOWN
    # =================================================

    if game_state == COUNTDOWN:

        elapsed = (
            pygame.time.get_ticks()
            - countdown_start
        ) / 1000


        if elapsed >= COUNTDOWN_LENGTH:

            start_time = (
                pygame.time.get_ticks()
            )

            game_state = PLAYING


    # =================================================
    # PLAYING
    # =================================================

    if game_state == PLAYING:

        # ---------------------------------------------
        # Get ESP32 command
        # ---------------------------------------------

        command = (
            serial_controller.get_command()
        )


        # ---------------------------------------------
        # Movement
        # ---------------------------------------------

        if command == "LEFT":

            move_player(
                -SPEED,
                0
            )


        elif command == "RIGHT":

            move_player(
                SPEED,
                0
            )


        elif command == "FORWARD":

            move_player(
                0,
                -SPEED
            )


        elif command == "DIAGONAL_LEFT":

            move_player(
                -SPEED * 0.707,
                -SPEED * 0.707
            )


        elif command == "DIAGONAL_RIGHT":

            move_player(
                SPEED * 0.707,
                -SPEED * 0.707
            )


        # ---------------------------------------------
        # Screen boundaries
        # ---------------------------------------------

        if player_x < 0:

            player_x = 0


        if player_x > WIDTH - PLAYER_SIZE:

            player_x = (
                WIDTH - PLAYER_SIZE
            )


        if player_y < 0:

            player_y = 0


        if player_y > HEIGHT - PLAYER_SIZE:

            player_y = (
                HEIGHT - PLAYER_SIZE
            )


        # ---------------------------------------------
        # Check finish line
        # ---------------------------------------------

        player_rect = get_player_rect()

        if player_rect.colliderect(
            finish_line
        ):

            finish_time = (
                pygame.time.get_ticks()
            )

            final_score = (
                finish_time
                - start_time
            ) / 1000

            save_score()

            game_state = FINISHED


    # =================================================
    # DRAW BACKGROUND
    # =================================================

    screen.fill(
        BACKGROUND_COLOR
    )


    # =================================================
    # NAME ENTRY
    # =================================================

    if game_state == NAME_ENTRY:

        draw_centered_text(
            "ESP32 OBSTACLE COURSE",
            title_font,
            120
        )


        draw_centered_text(
            "Enter your name",
            large_font,
            240
        )


        name_box = pygame.Rect(
            250,
            320,
            500,
            60
        )


        pygame.draw.rect(
            screen,
            (255, 255, 255),
            name_box
        )


        pygame.draw.rect(
            screen,
            (0, 0, 0),
            name_box,
            2
        )


        name_surface = font.render(
            player_name,
            True,
            TEXT_COLOR
        )


        screen.blit(
            name_surface,
            (
                name_box.x + 15,
                name_box.y + 12
            )
        )


        draw_centered_text(
            "Press ENTER to start",
            small_font,
            440
        )


        draw_centered_text(
            "Navigate using the ESP32 sensors",
            small_font,
            500
        )


    # =================================================
    # COUNTDOWN
    # =================================================

    elif game_state == COUNTDOWN:

        elapsed = (
            pygame.time.get_ticks()
            - countdown_start
        ) / 1000


        remaining = (
            COUNTDOWN_LENGTH
            - int(elapsed)
        )


        if remaining > 0:

            countdown_text = str(
                remaining
            )

        else:

            countdown_text = "GO!"


        draw_centered_text(
            countdown_text,
            title_font,
            250
        )


        draw_centered_text(
            player_name,
            font,
            340
        )


    # =================================================
    # PLAYING
    # =================================================

    elif game_state == PLAYING:

        # ---------------------------------------------
        # Course
        # ---------------------------------------------

        draw_course(
            screen,
            obstacles,
            finish_line
        )


        # ---------------------------------------------
        # Finish label
        # ---------------------------------------------

        finish_text = small_font.render(
            "FINISH",
            True,
            (255, 255, 255)
        )


        screen.blit(
            finish_text,
            (
                WIDTH // 2
                - finish_text.get_width() // 2,
                finish_line.y + 2
            )
        )


        # ---------------------------------------------
        # Player
        # ---------------------------------------------

        pygame.draw.rect(
            screen,
            PLAYER_COLOR,
            get_player_rect()
        )


        # ---------------------------------------------
        # Timer
        # ---------------------------------------------

        current_time = (
            pygame.time.get_ticks()
            - start_time
        ) / 1000


        timer_text = font.render(
            f"Time: {current_time:.2f}s",
            True,
            TEXT_COLOR
        )


        screen.blit(
            timer_text,
            (20, 20)
        )


        # ---------------------------------------------
        # Name
        # ---------------------------------------------

        name_text = small_font.render(
            f"Player: {player_name}",
            True,
            TEXT_COLOR
        )


        screen.blit(
            name_text,
            (20, 60)
        )


        # ---------------------------------------------
        # Current command
        # ---------------------------------------------

        command_text = small_font.render(
            f"Command: {command}",
            True,
            TEXT_COLOR
        )


        screen.blit(
            command_text,
            (20, 95)
        )


    # =================================================
    # FINISHED
    # =================================================

    elif game_state == FINISHED:

        draw_centered_text(
            "COURSE COMPLETE!",
            title_font,
            140
        )


        draw_centered_text(
            player_name,
            large_font,
            250
        )


        draw_centered_text(
            f"Time: {final_score:.2f} seconds",
            large_font,
            320
        )


        draw_centered_text(
            "Score saved!",
            font,
            400
        )


        draw_centered_text(
            "Press ENTER to race again",
            small_font,
            500
        )


        draw_centered_text(
            "Press ESC to quit",
            small_font,
            540
        )


    # =================================================
    # UPDATE
    # =================================================

    pygame.display.flip()

    clock.tick(60)


# =====================================================
# CLEANUP
# =====================================================

serial_controller.close()

pygame.quit()