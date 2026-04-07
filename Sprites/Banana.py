import pygame

BANANA_COLOR = (255, 225, 0)
BANANA_DARK = (200, 170, 0)


class Banana(pygame.sprite.Sprite):
    """Collectible banana drawn programmatically."""

    SIZE = 28

    def __init__(self, world_x, world_y, scroll_speed=4):
        super().__init__()
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.scroll_speed = scroll_speed

        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect(center=(int(self.world_x), int(self.world_y)))

    def _draw(self):
        s = self.SIZE
        # Crescent shape via two arcs
        pygame.draw.arc(self.image, BANANA_COLOR, (2, 4, s - 4, s - 4), 0, 3.14159, 8)
        pygame.draw.arc(self.image, BANANA_DARK, (6, 8, s - 12, s - 12), 0, 3.14159, 4)
        # Tip dots
        pygame.draw.circle(self.image, BANANA_COLOR, (2, s // 2), 4)
        pygame.draw.circle(self.image, BANANA_COLOR, (s - 2, s // 2), 4)

    def update(self, scroll_speed=None):
        if scroll_speed is not None:
            self.scroll_speed = scroll_speed
        self.world_x -= self.scroll_speed
        self.rect.center = (int(self.world_x), int(self.world_y))
        if self.rect.right < 0:
            self.kill()

    def collides_with(self, world_x, world_y, radius=22):
        dx = self.world_x - world_x
        dy = self.world_y - world_y
        return (dx * dx + dy * dy) < radius * radius
