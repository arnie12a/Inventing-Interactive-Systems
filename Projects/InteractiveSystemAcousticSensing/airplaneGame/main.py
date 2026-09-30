import pygame

from clap_detector import ClapDetector
from game import Game


FPS = 60


def main():
    pygame.init()

    # Use the MacBook's current display resolution
    display_info = pygame.display.Info()

    screen_width = display_info.current_w
    screen_height = display_info.current_h

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        pygame.FULLSCREEN
    )

    pygame.display.set_caption("Acoustic Airplane")

    clock = pygame.time.Clock()

    # Microphone / clap detector
    detector = ClapDetector(
        sample_rate=48_000,
        block_size=1024,
        fft_size=4096,
        input_device=None,
    )

    detector.start()

    # Game
    game = Game(
        screen,
        detector
    )

    print()
    print("==============================")
    print("ACOUSTIC AIRPLANE")
    print("==============================")
    print()
    print("POWER-UP:")
    print("Double clap to build power.")
    print()
    print("LAUNCH:")
    print("Single clap to launch.")
    print()
    print("BOOST:")
    print("Double clap once during flight.")
    print()
    print("Press ESC to quit.")
    print()

    running = True

    try:
        while running:

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

            dt = clock.tick(FPS) / 1000.0

            game.update(dt)
            game.draw()

            pygame.display.flip()

    finally:
        detector.stop()
        pygame.quit()


if __name__ == "__main__":
    main()