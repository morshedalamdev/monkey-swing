import pygame


def draw_text(text, font, text_col, x, y, screen):
    """
    Render text onto the screen at the given position.

    Kept as a shared utility matching the reference project's API so that
    any scene that wants to render HUD text can call it without duplicating
    the font-rendering boilerplate.
    """
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
