import pygame
import serial
import time

# =====================================================
# SERIAL SETTINGS
# =====================================================

SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 115200

# =====================================================
# GAME SETTINGS
# =====================================================

WIDTH = 1000
HEIGHT = 700

PLAYER_SIZE = 40
SPEED = 5

# =====================================================
# CONNECT TO ESP32
# =====================================================

try:
    arduino = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=0.01
    )

    # ESP32 often resets when serial connects
    time.sleep(2)

    print("Connected to ESP32")

except serial.SerialException as e:
    print("Could not connect to ESP32:")
    print(e)
    exit()

# =====================================================
# INITIALIZE PYGAME
# =====================================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ESP32 Gesture Game")

clock = pygame.time.Clock()

# =====================================================
# PLAYER
# =====================================================

player_x = WIDTH // 2
player_y = HEIGHT // 2

# Current command from ESP32
command = "NONE"

# =====================================================
# FONT
# =====================================================

font = pygame.font.Font(None, 36)

# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:

    # -------------------------------------------------
    # HANDLE PYGAME EVENTS
    # -------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # -------------------------------------------------
    # READ SERIAL DATA
    # -------------------------------------------------

    # Default to NONE every frame
    command = "NONE"

    while arduino.in_waiting:

        line = arduino.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if line:

            print("ESP32:", line)

            if line in [
                "LEFT",
                "RIGHT",
                "FORWARD",
                "NONE"
            ]:
                command = line

    # -------------------------------------------------
    # MOVE PLAYER
    # -------------------------------------------------

    if command == "LEFT":

        player_x -= SPEED

    elif command == "RIGHT":

        player_x += SPEED

    elif command == "FORWARD":

        player_y -= SPEED

    elif command == "NONE":

        # No movement
        pass

    # -------------------------------------------------
    # KEEP PLAYER INSIDE WINDOW
    # -------------------------------------------------

    if player_x < 0:
        player_x = 0

    if player_x > WIDTH - PLAYER_SIZE:
        player_x = WIDTH - PLAYER_SIZE

    if player_y < 0:
        player_y = 0

    if player_y > HEIGHT - PLAYER_SIZE:
        player_y = HEIGHT - PLAYER_SIZE

    # -------------------------------------------------
    # DRAW BACKGROUND
    # -------------------------------------------------

    screen.fill((255, 255, 255))

    # -------------------------------------------------
    # DRAW PLAYER
    # -------------------------------------------------

    pygame.draw.rect(
        screen,
        (0, 100, 255),
        (
            player_x,
            player_y,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
    )

    # -------------------------------------------------
    # DISPLAY COMMAND
    # -------------------------------------------------

    command_text = font.render(
        f"Command: {command}",
        True,
        (0, 0, 0)
    )

    screen.blit(
        command_text,
        (20, 20)
    )

    # -------------------------------------------------
    # DISPLAY PLAYER POSITION
    # -------------------------------------------------

    position_text = font.render(
        f"Position: ({player_x}, {player_y})",
        True,
        (0, 0, 0)
    )

    screen.blit(
        position_text,
        (20, 60)
    )

    # -------------------------------------------------
    # UPDATE SCREEN
    # -------------------------------------------------

    pygame.display.flip()

    # Run game at 60 FPS
    clock.tick(60)

# =====================================================
# CLEANUP
# =====================================================

arduino.close()
pygame.quit()