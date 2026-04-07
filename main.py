"""
Swing Monkey Swing — entry point.

Run:
    python main.py
"""
import sys
import pygame
from Scene.SceneHandler import SceneHandler


def main():
    pygame.init()

    SCREEN_W, SCREEN_H = 800, 600
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Swing Monkey Swing!")

    clock = pygame.time.Clock()
    handler = SceneHandler(SCREEN_H, SCREEN_W)

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        handler.scene.handle(events)
        handler.scene.update()
        handler.scene.render(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
