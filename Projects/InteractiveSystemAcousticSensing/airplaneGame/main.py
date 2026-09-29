import pygame

from clap_detector import ClapDetector
from game import Game


SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700

FPS = 60


def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
    )

    pygame.display.set_caption(
        "Acoustic Airplane"
    )

    clock = pygame.time.Clock()

    # ==================================================
    # MICROPHONE
    # ==================================================

    detector = ClapDetector(
        sample_rate=48_000,
        block_size=1024,
        fft_size=4096,
        input_device=None,
    )

    detector.start()

    # ==================================================
    # GAME
    # ==================================================

    game = Game(
        screen,
        detector
    )

    # ==================================================
    # INPUT
    # ==================================================

    pygame.key.start_text_input()

    running = True

    try:

        while running:

            # ==========================================
            # EVENTS
            # ==========================================

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                else:

                    game.handle_event(
                        event
                    )

            # ==========================================
            # UPDATE
            # ==========================================

            dt = (
                clock.tick(FPS)
                / 1000.0
            )

            game.update(dt)

            # ==========================================
            # DRAW
            # ==========================================

            game.draw()

            pygame.display.flip()

    finally:

        pygame.key.stop_text_input()

        detector.stop()

        pygame.quit()


if __name__ == "__main__":
    main()