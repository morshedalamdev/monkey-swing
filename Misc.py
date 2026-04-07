import pygame


def draw_text(text, font, text_col, x, y, screen):
    """Render text onto the screen at the given position."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
