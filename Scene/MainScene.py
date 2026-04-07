"""
Main menu scene — title screen with Play and Quit buttons.
"""
import math
import pygame

from Scene.Scene import AbstractScene
from Components.Button import Button

# Colours
BG_TOP    = (30, 60, 30)
BG_BOT    = (50, 120, 50)
TITLE_COL = (255, 220, 0)
SHADOW_COL = (80, 50, 0)

MONKEY_BODY  = (139, 90, 43)
MONKEY_FACE  = (205, 133, 63)
EYE_COL      = (50, 30, 10)
VINE_COL     = (34, 120, 34)


class MainScene(AbstractScene):
    def __init__(self):
        super().__init__()

        self.play_btn = Button("🐒  Play", (0, 0), font_size=42, bg=(34, 140, 34))
        self.quit_btn = Button("Quit",      (0, 0), font_size=32, bg=(160, 40, 40))

        self.anim_tick = 0   # drives monkey swing animation
        self.swing_angle = 0.4

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def handle(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.handler.go("PLAY_SCENE")
        if self.play_btn.click(events):
            self.handler.go("PLAY_SCENE")
        if self.quit_btn.click(events):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self):
        self.anim_tick += 1
        # Gentle pendulum for the title monkey
        self.swing_angle = 0.45 * math.sin(self.anim_tick * 0.04)

    def render(self, screen):
        sw, sh = screen.get_size()

        # Background gradient (jungle green)
        for y in range(sh):
            t = y / sh
            r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
            g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
            b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (sw, y))

        # Decorative background trees
        self._draw_trees(screen, sw, sh)

        # Animated swinging monkey + vine
        self._draw_monkey_vine(screen, sw, sh)

        # Title text
        self._draw_title(screen, sw)

        # Buttons — centred
        btn_x = sw // 2 - self.play_btn.rect.width // 2
        self.play_btn.rect.x = self.play_btn.x = btn_x
        self.play_btn.rect.y = self.play_btn.y = sh // 2 + 60
        self.play_btn.render(screen)

        qx = sw // 2 - self.quit_btn.rect.width // 2
        self.quit_btn.rect.x = self.quit_btn.x = qx
        self.quit_btn.rect.y = self.quit_btn.y = sh // 2 + 140
        self.quit_btn.render(screen)

        # Subtitle hint
        font = pygame.font.SysFont("Arial", 24)
        hint = font.render("Press SPACE to play instantly", True, (200, 230, 200))
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh // 2 + 210))

        # Score
        if hasattr(self, "handler") and self.handler.score > 0:
            sc = font.render(f"High Score: {self.handler.score}", True, (255, 230, 100))
            screen.blit(sc, (sw // 2 - sc.get_width() // 2, sh - 48))

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_trees(self, screen, sw, sh):
        for i, (x, scale) in enumerate([(60, 1.0), (sw - 80, 0.9), (sw // 2 + 170, 0.7)]):
            h = int(120 * scale)
            tw = int(24 * scale)
            cr = int(55 * scale)
            # Trunk
            pygame.draw.rect(screen, (70, 45, 15),
                             (x - tw // 2, sh - h - 20, tw, h + 20))
            # Canopy
            pygame.draw.circle(screen, (20, 90, 20), (x, sh - h - 20), cr + 8)
            pygame.draw.circle(screen, (34, 120, 34), (x, sh - h - 26), cr)

    def _draw_monkey_vine(self, screen, sw, sh):
        anchor_x = sw // 2 + 80
        anchor_y = 30
        vine_len = 180
        angle = self.swing_angle

        monkey_x = int(anchor_x + vine_len * math.sin(angle))
        monkey_y = int(anchor_y + vine_len * math.cos(angle))

        # Vine
        pygame.draw.line(screen, VINE_COL, (anchor_x, anchor_y), (monkey_x, monkey_y), 5)
        pygame.draw.line(screen, (20, 80, 20), (anchor_x, anchor_y), (monkey_x, monkey_y), 2)

        # Anchor
        pygame.draw.rect(screen, (80, 45, 10), (anchor_x - 12, 0, 24, 18))

        # Monkey body
        pygame.draw.ellipse(screen, MONKEY_BODY,
                            (monkey_x - 14, monkey_y - 8, 28, 32))
        # Head
        pygame.draw.circle(screen, MONKEY_BODY, (monkey_x, monkey_y - 14), 18)
        pygame.draw.ellipse(screen, MONKEY_FACE,
                            (monkey_x - 10, monkey_y - 12, 20, 14))
        # Eyes
        for ex in (-5, 5):
            pygame.draw.circle(screen, EYE_COL, (monkey_x + ex, monkey_y - 18), 4)
            pygame.draw.circle(screen, (255, 255, 255), (monkey_x + ex + 1, monkey_y - 19), 2)
        # Arms raised
        pygame.draw.line(screen, MONKEY_BODY,
                         (monkey_x - 12, monkey_y - 2),
                         (monkey_x - 22, monkey_y - 18), 5)
        pygame.draw.line(screen, MONKEY_BODY,
                         (monkey_x + 12, monkey_y - 2),
                         (monkey_x + 22, monkey_y - 18), 5)
        # Tail
        pygame.draw.arc(screen, MONKEY_BODY,
                        (monkey_x + 10, monkey_y + 14, 26, 16), 0, math.pi, 5)
        # Legs
        pygame.draw.line(screen, MONKEY_BODY,
                         (monkey_x - 6, monkey_y + 24), (monkey_x - 10, monkey_y + 38), 5)
        pygame.draw.line(screen, MONKEY_BODY,
                         (monkey_x + 6, monkey_y + 24), (monkey_x + 10, monkey_y + 38), 5)

    def _draw_title(self, screen, sw):
        font_big = pygame.font.SysFont("Arial", 62, bold=True)
        font_sub = pygame.font.SysFont("Arial", 30, italic=True)

        title = "Swing Monkey Swing!"
        # Shadow
        shadow_surf = font_big.render(title, True, SHADOW_COL)
        screen.blit(shadow_surf, (sw // 2 - shadow_surf.get_width() // 2 + 3, 63))
        # Main
        title_surf = font_big.render(title, True, TITLE_COL)
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 60))

        sub = font_sub.render("Swing from vine to vine — avoid the trees!", True, (180, 240, 180))
        screen.blit(sub, (sw // 2 - sub.get_width() // 2, 140))
