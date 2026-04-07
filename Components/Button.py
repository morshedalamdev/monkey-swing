import pygame


class Button:
    """A simple text button rendered with pygame."""

    def __init__(self, text, pos, font_size=36, bg=(70, 70, 200)):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.bg = bg
        self.text_str = text
        self._build(text, bg)

    def _build(self, text, bg):
        self.text_surf = self.font.render(text, True, (255, 255, 255))
        pad_x, pad_y = 18, 10
        w = self.text_surf.get_width() + pad_x * 2
        h = self.text_surf.get_height() + pad_y * 2
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, bg, (0, 0, w, h), border_radius=8)
        pygame.draw.rect(self.surface, (255, 255, 255), (0, 0, w, h), 2, border_radius=8)
        self.surface.blit(self.text_surf, (pad_x, pad_y))
        self.rect = pygame.Rect(self.x, self.y, w, h)

    def render(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def click(self, events):
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(mx, my)
            ):
                return True
        return False
