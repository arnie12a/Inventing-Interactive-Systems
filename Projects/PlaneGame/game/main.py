import pygame

from serial_controller import CapacitiveController


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 800
HEIGHT = 600

FPS = 60

# Change this to your ESP32's serial port.
# On Mac it often looks like:
# /dev/cu.usbserial-XXXX
# /dev/cu.SLAB_USBtoUART
#
# On Windows it may look like:
# COM3
SERIAL_PORT = "/dev/cu.usbserial-XXXX"

BAUD_RATE = 115200

# How much the airplane moves after a swipe
MOVE_DISTANCE = 50


# ============================================================
# INITIALIZE PYGAME
# ============================================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Capacitive Airplane Game")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)


# ============================================================
# INITIALIZE ESP32 CONTROLLER
# ============================================================

controller = CapacitiveController(
    SERIAL_PORT,
    BAUD_RATE
)


# ============================================================
# AIRPLANE
# ============================================================

plane_x = WIDTH // 2
plane_y = 100

plane_width = 50
plane_height = 30


# ============================================================
# RUNWAY
# ============================================================

runway_width = 200
runway_height = 60

runway_x = (WIDTH - runway_width) // 2
runway_y = HEIGHT - 120


# ============================================================
# GAME VARIABLES
# ============================================================

running = True

last_gesture = "NO_SWIPE"


# ============================================================
# MAIN GAME LOOP
# ============================================================

while running:

    # --------------------------------------------------------
    # HANDLE PYGAME EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    # --------------------------------------------------------
    # READ ESP32
    # --------------------------------------------------------

    data = controller.get_data()

    if data is not None:

        gesture = data["gesture"]

        # Print sensor information in terminal
        print(
            f"Left: {data['left']} | "
            f"Center: {data['center']} | "
            f"Right: {data['right']} | "
            f"Gesture: {gesture}"
        )

        # ----------------------------------------------------
        # MOVE AIRPLANE
        # ----------------------------------------------------

        if gesture == "LEFT_SWIPE":

            plane_x -= MOVE_DISTANCE
            last_gesture = "LEFT_SWIPE"

        elif gesture == "RIGHT_SWIPE":

            plane_x += MOVE_DISTANCE
            last_gesture = "RIGHT_SWIPE"

        else:

            last_gesture = "NO_SWIPE"


    # --------------------------------------------------------
    # KEEP AIRPLANE INSIDE SCREEN
    # --------------------------------------------------------

    if plane_x < plane_width // 2:
        plane_x = plane_width // 2

    if plane_x > WIDTH - plane_width // 2:
        plane_x = WIDTH - plane_width // 2


    # --------------------------------------------------------
    # DRAW BACKGROUND
    # --------------------------------------------------------

    screen.fill((135, 206, 235))


    # --------------------------------------------------------
    # DRAW RUNWAY
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        (70, 70, 70),
        (
            runway_x,
            runway_y,
            runway_width,
            runway_height
        )
    )


    # Draw runway center line
    pygame.draw.line(
        screen,
        (255, 255, 0),
        (
            WIDTH // 2,
            runway_y
        ),
        (
            WIDTH // 2,
            runway_y + runway_height
        ),
        5
    )


    # --------------------------------------------------------
    # DRAW AIRPLANE
    # --------------------------------------------------------

    # Main body
    plane_rect = pygame.Rect(
        plane_x - plane_width // 2,
        plane_y - plane_height // 2,
        plane_width,
        plane_height
    )

    pygame.draw.rect(
        screen,
        (255, 255, 255),
        plane_rect
    )

    # Wings
    pygame.draw.polygon(
        screen,
        (255, 255, 255),
        [
            (plane_x, plane_y),
            (plane_x - 25, plane_y + 20),
            (plane_x + 25, plane_y + 20)
        ]
    )


    # --------------------------------------------------------
    # DISPLAY CURRENT GESTURE
    # --------------------------------------------------------

    gesture_text = font.render(
        f"Gesture: {last_gesture}",
        True,
        (0, 0, 0)
    )

    screen.blit(
        gesture_text,
        (20, 20)
    )


    # --------------------------------------------------------
    # DISPLAY INSTRUCTIONS
    # --------------------------------------------------------

    instruction_text = font.render(
        "Swipe LEFT or RIGHT to move the airplane",
        True,
        (0, 0, 0)
    )

    screen.blit(
        instruction_text,
        (20, 55)
    )


    # --------------------------------------------------------
    # UPDATE DISPLAY
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(FPS)


# ============================================================
# CLEAN UP
# ============================================================

controller.close()

pygame.quit()