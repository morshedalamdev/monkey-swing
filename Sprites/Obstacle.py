import pygame
import math

TRUNK_COLOR = (101, 67, 33)
LEAF_DARK = (20, 90, 20)
LEAF_LIGHT = (34, 140, 34)


class Obstacle(pygame.sprite.Sprite):
    """
    A tree obstacle drawn programmatically.
    Scrolls from right to left.
    """

    def __init__(self, world_x, ground_y, scroll_speed=4):
        super().__init__()
        self.world_x = float(world_x)
        self.ground_y = ground_y
        self.scroll_speed = scroll_speed

        # Randomise size slightly via fixed seed per position
        rng = int(world_x) % 7
        self.trunk_w = 28 + rng * 4
        self.trunk_h = 90 + rng * 10
        self.canopy_r = 45 + rng * 5

        self.width = max(self.trunk_w, self.canopy_r * 2) + 20
        self.height = self.trunk_h + self.canopy_r * 2

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect(
            midbottom=(int(self.world_x), int(self.ground_y))
        )

    def _draw(self):
        cx = self.width // 2
        # Trunk
        trunk_x = cx - self.trunk_w // 2
        pygame.draw.rect(
            self.image, TRUNK_COLOR,
            (trunk_x, self.height - self.trunk_h, self.trunk_w, self.trunk_h),
        )
        # Canopy layers
        top_y = self.height - self.trunk_h - self.canopy_r
        pygame.draw.circle(self.image, LEAF_DARK, (cx, top_y + 5), self.canopy_r + 6)
        pygame.draw.circle(self.image, LEAF_LIGHT, (cx, top_y), self.canopy_r)
        pygame.draw.circle(self.image, (50, 160, 50), (cx - 10, top_y - 8), self.canopy_r - 12)

    def update(self, scroll_speed=None):
        if scroll_speed is not None:
            self.scroll_speed = scroll_speed
        self.world_x -= self.scroll_speed
        self.rect.midbottom = (int(self.world_x), int(self.ground_y))
        if self.rect.right < 0:
            self.kill()

    def collides_with(self, world_x, world_y, radius=18):
        """Check collision against world-space coordinates."""
        cx = int(self.world_x)
        left = cx - self.width // 2
        right = cx + self.width // 2
        top = self.ground_y - self.trunk_h
        bottom = self.ground_y
        return (left - radius < world_x < right + radius and
                top - radius < world_y < bottom + radius)
