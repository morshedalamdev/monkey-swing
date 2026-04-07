"""
PlayScene — the main monkey-swing gameplay scene.

Controls
--------
SPACE   : Release from vine (when swinging) / Restart (when game-over)
ESC     : Return to main menu

Mechanics
---------
- The monkey hangs from vine anchors at the top of the screen.
- Pendulum physics drive the swing.
- Press SPACE to release; the monkey flies through the air.
- The monkey automatically grabs the nearest vine anchor when close enough.
- Avoid tree obstacles and the ground.
- Collect bananas for bonus score.
"""

import math
import random

import pygame

from Scene.Scene import AbstractScene
from Sprites.Monkey import Monkey
from Sprites.Obstacle import Obstacle
from Sprites.Banana import Banana
from Components.Button import Button

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
SKY_TOP    = (100, 180, 255)
SKY_BOT    = (180, 230, 255)
GROUND_COL = (101, 67, 33)
GRASS_COL  = (34, 120, 34)
VINE_COL   = (34, 120, 34)
VINE_DARK  = (20, 80, 20)
ANCHOR_COL = (80, 45, 10)
TEXT_DARK  = (30, 20, 10)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
ANCHOR_Y     = 0      # vines attach at very top of screen
GROUND_FRAC  = 0.88   # fraction of screen height where ground starts
VINE_SPACING = 210    # average world-x gap between vine anchors
VINE_MIN_LEN = 160
VINE_MAX_LEN = 200
GRAB_X_RADIUS = 100   # horizontal grab window around vine anchor (generous = forgiving)
SCROLL_SPEED = 4      # px/frame for obstacles / bananas


class PlayScene(AbstractScene):
    """
    difficulty (int): 1 = easy (wider grab radius, slower camera),
                      2 = medium, 3 = hard (tighter grab radius, faster scroll).
    """

    # Per-difficulty tuning
    _DIFFICULTY_GRAB   = {1: 110, 2: 90, 3: 70}   # GRAB_X_RADIUS per level
    _DIFFICULTY_OMEGA  = {1: 1.5, 2: 1.8, 3: 2.1}  # initial swing energy per level

    def __init__(self, screen_w, screen_h, difficulty=1):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.difficulty = max(1, min(3, difficulty))
        self.grab_radius = self._DIFFICULTY_GRAB[self.difficulty]
        self.init_omega  = self._DIFFICULTY_OMEGA[self.difficulty]
        self.ground_y = int(screen_h * GROUND_FRAC)

        self.back_btn = Button("← Menu", (10, 10), font_size=24, bg=(60, 60, 160))

        self._build_bg()
        self.reset()

    # ------------------------------------------------------------------
    # Background surface (drawn once)
    # ------------------------------------------------------------------

    def _build_bg(self):
        self.bg = pygame.Surface((self.screen_w, self.screen_h))
        # Sky gradient
        for y in range(self.ground_y):
            t = y / self.ground_y
            r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
            pygame.draw.line(self.bg, (r, g, b), (0, y), (self.screen_w, y))
        # Ground
        pygame.draw.rect(self.bg, GROUND_COL,
                         (0, self.ground_y, self.screen_w, self.screen_h - self.ground_y))
        pygame.draw.rect(self.bg, GRASS_COL,
                         (0, self.ground_y - 8, self.screen_w, 12))

    # ------------------------------------------------------------------
    # Reset / initialise game state
    # ------------------------------------------------------------------

    def reset(self):
        self.score         = 0
        self.game_over     = False
        self.started       = False   # waiting for first SPACE press
        self.camera_x      = 0.0
        self.camera_vel    = 0.0
        self.scroll_offset = 0       # for bg trees parallax

        # Sprite groups
        self.obstacle_group = pygame.sprite.Group()
        self.banana_group   = pygame.sprite.Group()

        # Generate vine anchors in world space
        self.vines = self._gen_vines(30)
        self.current_vine  = 0       # index of vine monkey is on / last grabbed
        self.grabbed_vines = {0}     # vines already scored

        # Monkey starts attached to vine 0
        self.monkey = Monkey(
            self.vines[0]["x"],
            self.vines[0]["y"] + self.vines[0]["len"] // 2,
        )
        # Start with monkey on the LEFT of anchor, swinging RIGHTWARD.
        # Releasing at ~angle=+0.3 sends monkey forward-and-up to next vine.
        self._attach_monkey(0, initial_angle=-0.4, initial_omega=self.init_omega)

        # Pre-populate obstacles and bananas
        self._gen_obstacles(20)
        self._gen_bananas(25)

        # Particles
        self.particles = []

    # ------------------------------------------------------------------
    # World generation
    # ------------------------------------------------------------------

    def _gen_vines(self, n):
        vines = []
        x = self.screen_w // 4   # start vines near left quarter so monkey swings right
        for _ in range(n):
            length = random.randint(VINE_MIN_LEN, VINE_MAX_LEN)
            vines.append({"x": float(x), "y": float(ANCHOR_Y), "len": length})
            x += random.randint(int(VINE_SPACING * 0.85), int(VINE_SPACING * 1.2))
        return vines

    def _gen_obstacles(self, n):
        for i in range(n):
            # Obstacles start well to the right of the first vine
            wx = self.vines[1]["x"] + 150 + i * random.randint(280, 420)
            self.obstacle_group.add(Obstacle(wx, self.ground_y, scroll_speed=0))

    def _gen_bananas(self, n):
        for i in range(n):
            wx = self.vines[0]["x"] + 200 + i * random.randint(200, 350)
            wy = random.randint(int(self.screen_h * 0.25), int(self.screen_h * 0.65))
            self.banana_group.add(Banana(wx, wy, scroll_speed=0))

    # ------------------------------------------------------------------
    # Attach monkey to a vine
    # ------------------------------------------------------------------

    def _attach_monkey(self, vine_idx, initial_angle=None, initial_omega=None):
        v = self.vines[vine_idx]
        if initial_angle is None:
            # Calculate angle from current monkey position relative to anchor
            dx = self.monkey.world_x - v["x"]
            dy = self.monkey.world_y - v["y"]
            dist = math.hypot(dx, dy)
            # Use the actual distance as the new vine length (clamped)
            grab_len = max(80.0, min(float(v["len"]), dist if dist > 0 else float(v["len"])))
            if dist > 0:
                initial_angle = math.atan2(dx, dy)
            else:
                initial_angle = 0.0
            # Convert linear velocity → angular velocity at this rope length
            if dist > 0:
                # Tangential velocity component (perpendicular to vine)
                tangential_v = (self.monkey.vx * math.cos(initial_angle)
                                - self.monkey.vy * math.sin(initial_angle))
                initial_omega = tangential_v / grab_len
            else:
                initial_omega = -1.5
            self.monkey.attach(v["x"], v["y"], grab_len, initial_angle, initial_omega)
        else:
            self.monkey.attach(v["x"], v["y"], v["len"], initial_angle, initial_omega)
        self.current_vine = vine_idx

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def handle(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.handler.go("MAIN_SCENE")
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    elif not self.started:
                        self.started = True
                    elif self.monkey.on_vine:
                        self._release()
        if self.back_btn.click(events):
            self.handler.go("MAIN_SCENE")

    def update(self):
        if not self.started or self.game_over:
            return

        dt = 1 / 60.0
        self.monkey.update(dt)

        mx, my = self.monkey.world_x, self.monkey.world_y

        # --- Check vine grab (only when in free flight) ---
        if not self.monkey.on_vine:
            for i, v in enumerate(self.vines):
                if i <= self.current_vine:
                    continue
                # Grab when monkey passes through the vine's horizontal band.
                # Use 1.5× vine length as vertical buffer (forgiving grab zone).
                dx = abs(mx - v["x"])
                in_vine_zone = my < v["y"] + v["len"] * 1.5
                if dx < self.grab_radius and in_vine_zone and mx > v["x"] - self.grab_radius:
                    self._attach_monkey(i)
                    if i not in self.grabbed_vines:
                        self.grabbed_vines.add(i)
                        self.score += 1
                        if hasattr(self, "handler"):
                            self.handler.score += 1
                        self._spawn_particles(mx, my, (34, 200, 34))
                    break

        # --- Ground collision ---
        if my >= self.ground_y - Monkey.RADIUS:
            self.game_over = True
            return

        # --- Screen top collision ---
        if my <= ANCHOR_Y + 5:
            self.game_over = True
            return

        # --- Obstacle collision ---
        for obs in self.obstacle_group.sprites():
            if obs.collides_with(mx, my, Monkey.RADIUS):
                self.game_over = True
                return

        # --- Banana collection ---
        for banana in list(self.banana_group.sprites()):
            if banana.collides_with(mx, my):
                banana.kill()
                if hasattr(self, "handler"):
                    self.handler.banana += 1
                self.score += 1
                self._spawn_particles(mx, my, (255, 225, 0))

        # --- Camera: smooth follow, keep monkey in left third ---
        target_cam = mx - self.screen_w // 3
        self.camera_x += (target_cam - self.camera_x) * 0.08

        # --- Update parallax scroll offset ---
        self.scroll_offset = int(self.camera_x * 0.3) % (self.screen_w + 200)

        # --- Update particles ---
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 400 * dt   # gravity on particles
            p["life"] -= dt

    def render(self, screen):
        # Background
        screen.blit(self.bg, (0, 0))

        # Parallax background trees
        self._draw_bg_trees(screen)

        cam = self.camera_x

        # Obstacles
        for obs in self.obstacle_group.sprites():
            sx = obs.world_x - cam - obs.width // 2
            if -obs.width < sx < self.screen_w + obs.width:
                screen.blit(obs.image, (int(sx), int(self.ground_y - obs.height)))

        # Bananas
        for banana in self.banana_group.sprites():
            sx = banana.world_x - cam
            if -40 < sx < self.screen_w + 40:
                screen.blit(banana.image, (int(sx - banana.SIZE // 2),
                                           int(banana.world_y - banana.SIZE // 2)))

        # Vines and anchors
        self._draw_vines(screen, cam)

        # Particles
        for p in self.particles:
            sx = int(p["x"] - cam)
            sy = int(p["y"])
            alpha = int(255 * max(p["life"] / p["max_life"], 0))
            col = (*p["color"], alpha)
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (4, 4), 4)
            screen.blit(surf, (sx - 4, sy - 4))

        # Monkey
        mx_s = int(self.monkey.world_x - cam)
        my_s = int(self.monkey.world_y)
        # Blit monkey image centred on monkey position
        img = self.monkey.image
        screen.blit(img, (mx_s - img.get_width() // 2,
                           my_s - img.get_height() // 2))

        # HUD
        self._draw_hud(screen)

        # Overlays
        if not self.started:
            self._draw_start_overlay(screen)
        if self.game_over:
            self._draw_gameover_overlay(screen)

        self.back_btn.render(screen)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_bg_trees(self, screen):
        """Simple parallax background trees."""
        cols = [(20, 80, 20), (30, 100, 30)]
        for i in range(12):
            base_x = (i * 220 - int(self.camera_x * 0.2)) % (self.screen_w + 200) - 100
            h = 90 + (i % 3) * 30
            pygame.draw.rect(screen, (70, 45, 15), (base_x + 12, self.ground_y - h, 16, h))
            pygame.draw.circle(screen, cols[i % 2], (base_x + 20, self.ground_y - h), 35)

    def _draw_vines(self, screen, cam):
        m = self.monkey
        for i, v in enumerate(self.vines):
            sx = v["x"] - cam
            if -50 > sx or sx > self.screen_w + 50:
                continue

            # Draw anchor bracket
            pygame.draw.rect(screen, ANCHOR_COL, (int(sx) - 12, 0, 24, 16))
            pygame.draw.rect(screen, (60, 30, 5), (int(sx) - 8, 12, 16, 6))

            if i == self.current_vine and m.on_vine:
                # Draw actual vine to monkey
                end_x = m.world_x - cam
                end_y = m.world_y
                self._draw_vine_line(screen, sx, 0, end_x, end_y)
            else:
                # Show hanging vine tip
                tip_y = v["len"] * 0.45
                self._draw_vine_line(screen, sx, 0, sx, tip_y)
                # Small loop at tip
                pygame.draw.circle(screen, VINE_DARK, (int(sx), int(tip_y)), 5)

    def _draw_vine_line(self, screen, x1, y1, x2, y2):
        """Draw a catenary-ish vine with small segments."""
        segs = 10
        pts = []
        for k in range(segs + 1):
            t = k / segs
            ix = x1 + (x2 - x1) * t
            iy = y1 + (y2 - y1) * t
            # Add slight sag
            sag = math.sin(t * math.pi) * 12
            pts.append((ix, iy + sag))
        if len(pts) >= 2:
            pygame.draw.lines(screen, VINE_COL, False, pts, 4)
            pygame.draw.lines(screen, VINE_DARK, False, pts, 2)

    def _draw_hud(self, screen):
        font_lg = pygame.font.SysFont("Arial", 38, bold=True)
        font_sm = pygame.font.SysFont("Arial", 26, bold=True)

        # Score
        score_surf = font_lg.render(str(self.score), True, TEXT_DARK)
        screen.blit(score_surf, (self.screen_w // 2 - score_surf.get_width() // 2, 14))

        # Banana count
        bcount = self.handler.banana if hasattr(self, "handler") else 0
        b_surf = font_sm.render(f"🍌 {bcount}", True, (200, 160, 0))
        screen.blit(b_surf, (self.screen_w - b_surf.get_width() - 14, 14))

        # Hint
        if self.started and not self.game_over and self.monkey.on_vine:
            hint = font_sm.render("SPACE = Release!", True, (60, 60, 60))
            screen.blit(hint, (self.screen_w // 2 - hint.get_width() // 2,
                                self.screen_h - 36))

    def _draw_start_overlay(self, screen):
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("Arial", 54, bold=True)
        font_med = pygame.font.SysFont("Arial", 32)

        t1 = font_big.render("Swing Monkey Swing!", True, (255, 220, 0))
        t2 = font_med.render("Press SPACE to start swinging", True, (255, 255, 255))
        t3 = font_med.render("Press SPACE again to release the vine", True, (200, 255, 200))

        cx = self.screen_w // 2
        screen.blit(t1, (cx - t1.get_width() // 2, 180))
        screen.blit(t2, (cx - t2.get_width() // 2, 270))
        screen.blit(t3, (cx - t3.get_width() // 2, 316))

    def _draw_gameover_overlay(self, screen):
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("Arial", 68, bold=True)
        font_med = pygame.font.SysFont("Arial", 36)
        font_sm  = pygame.font.SysFont("Arial", 28)

        cx = self.screen_w // 2

        t1 = font_big.render("Game Over!", True, (255, 80, 80))
        t2 = font_med.render(f"Score: {self.score}", True, (255, 255, 255))
        t3 = font_sm.render("Press SPACE to try again", True, (200, 200, 200))
        t4 = font_sm.render("Press ESC or ← Menu to quit", True, (180, 180, 180))

        screen.blit(t1, (cx - t1.get_width() // 2, 180))
        screen.blit(t2, (cx - t2.get_width() // 2, 275))
        screen.blit(t3, (cx - t3.get_width() // 2, 340))
        screen.blit(t4, (cx - t4.get_width() // 2, 384))

    # ------------------------------------------------------------------
    # Particle helpers
    # ------------------------------------------------------------------

    def _spawn_particles(self, wx, wy, color, n=12):
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 180)
            life  = random.uniform(0.4, 0.8)
            self.particles.append({
                "x": wx, "y": wy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 80,
                "life": life, "max_life": life,
                "color": color,
            })

    def _release(self):
        self.monkey.release()
        self._spawn_particles(self.monkey.world_x, self.monkey.world_y,
                              (34, 180, 34), n=6)
