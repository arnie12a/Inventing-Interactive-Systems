import pygame

from clap_detector import ClapDetector
from game import Game


FPS = 60


def main():
    pygame.init()

    # ======================================================
    # WINDOW
    # ======================================================

    display_info = pygame.display.Info()

    screen_width = display_info.current_w
    screen_height = display_info.current_h

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        pygame.FULLSCREEN
    )

    pygame.display.set_caption(
        "Acoustic Airplane"
    )

    clock = pygame.time.Clock()

    # ======================================================
    # CLAP DETECTOR
    # ======================================================

    detector = ClapDetector(
        sample_rate=48_000,
        block_size=1024,
        fft_size=4096,
        input_device=None,
    )

    detector.start()

    # ======================================================
    # GAME
    # ======================================================

    game = Game(
        screen,
        detector
    )

    print()
    print("==============================")
    print("ACOUSTIC AIRPLANE")
    print("==============================")
    print()
    print("POWER-UP")
    print("Double clap to build power.")
    print()
    print("LAUNCH")
    print("Single clap to launch.")
    print()
    print("BOOST")
    print("Double clap once during flight.")
    print()
    print("ESC = Quit")
    print()

    running = True

    try:
        while running:

            # ==================================================
            # PYGAME EVENTS
            # ==================================================

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False

                else:
                    game.handle_event(event)

            # ==================================================
            # TIME
            # ==================================================

            dt = (
                clock.tick(FPS)
                / 1000.0
            )

            # ==================================================
            # UPDATE
            # ==================================================

            game.update(dt)

            # ==================================================
            # DRAW
            # ==================================================

            game.draw()

            pygame.display.flip()

    finally:
        detector.stop()
        pygame.quit()


if __name__ == "__main__":
    main()