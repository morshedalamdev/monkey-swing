import pygame
import math

# Monkey colour palette
BODY_COLOR = (139, 90, 43)
FACE_COLOR = (205, 133, 63)
EYE_COLOR = (50, 30, 10)
HIGHLIGHT = (255, 255, 255)


class Monkey(pygame.sprite.Sprite):
    """
    Monkey sprite drawn programmatically.

    The Monkey supports two movement modes:
      - on_vine: pendulum physics around an anchor point
      - free flight: projectile motion with gravity
    """

    GRAVITY = 300  # px / s² — tuned for satisfying arc length
    RADIUS = 22     # collision/draw radius

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        # Physics state
        self.world_x = float(x)
        self.world_y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        # Pendulum state
        self.on_vine = False
        self.anchor_x = 0.0
        self.anchor_y = 0.0
        self.vine_length = 200.0
        self.angle = 0.0          # radians from vertical
        self.angular_vel = 0.0   # rad/s

        # Visuals
        self.rotation = 0.0
        self.frame = 0
        self.frame_timer = 0

        self._redraw()

    # ------------------------------------------------------------------
    # Pendulum helpers
    # ------------------------------------------------------------------

    def attach(self, anchor_x, anchor_y, vine_length, initial_angle=0.4, initial_omega=-1.8):
        """Attach the monkey to a vine anchor."""
        self.on_vine = True
        self.anchor_x = float(anchor_x)
        self.anchor_y = float(anchor_y)
        self.vine_length = float(vine_length)
        self.angle = initial_angle
        self.angular_vel = initial_omega
        self._sync_position_from_pendulum()

    def release(self):
        """Let go of vine and enter free-flight."""
        if not self.on_vine:
            return
        # Convert angular velocity → linear velocity
        L = self.vine_length
        omega = self.angular_vel
        # velocity is tangential: perpendicular to the vine
        # vine direction: (sin θ, cos θ)  → tangent: (cos θ, −sin θ) for CCW
        self.vx = omega * L * math.cos(self.angle)
        self.vy = -omega * L * math.sin(self.angle)
        self.on_vine = False

    def _sync_position_from_pendulum(self):
        self.world_x = self.anchor_x + self.vine_length * math.sin(self.angle)
        self.world_y = self.anchor_y + self.vine_length * math.cos(self.angle)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt=1 / 60.0):
        if self.on_vine:
            # Pendulum: θ'' = -(g/L) sin(θ)
            alpha = -(self.GRAVITY / self.vine_length) * math.sin(self.angle)
            self.angular_vel += alpha * dt
            # Gentle damping so it stays lively but not forever
            self.angular_vel *= 0.999
            self.angle += self.angular_vel * dt
            self._sync_position_from_pendulum()
            self.rotation = math.degrees(-self.angle) * 0.5
        else:
            self.vy += self.GRAVITY * dt
            self.world_x += self.vx * dt
            self.world_y += self.vy * dt
            # Tilt by velocity direction
            speed = math.hypot(self.vx, self.vy)
            if speed > 0:
                self.rotation = math.degrees(math.atan2(-self.vy, self.vx)) * 0.3

        # Sync rect (camera applied externally)
        self.frame_timer += 1
        if self.frame_timer > 8:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 3

        self._redraw()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _redraw(self):
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        cx, cy = 30, 40
        sway = math.sin(self.frame * 2.1) * 3

        # Tail
        pygame.draw.arc(
            self.image, BODY_COLOR,
            (cx + 10, cy + 15, 25, 18), 0, math.pi, 5,
        )

        # Body
        pygame.draw.ellipse(self.image, BODY_COLOR, (cx - 13, cy - 8, 26, 32))

        # Head
        pygame.draw.circle(self.image, BODY_COLOR, (cx + int(sway), cy - 18), 18)
        # Face patch
        pygame.draw.ellipse(self.image, FACE_COLOR, (cx - 9 + int(sway), cy - 16, 18, 13))

        # Eyes
        for ex in (-5, 5):
            pygame.draw.circle(self.image, EYE_COLOR, (cx + ex + int(sway), cy - 22), 4)
            pygame.draw.circle(self.image, HIGHLIGHT, (cx + ex + 1 + int(sway), cy - 23), 2)

        # Nose
        pygame.draw.ellipse(self.image, (160, 90, 40), (cx - 3 + int(sway), cy - 12, 6, 4))

        # Arms (swing toward anchor when on vine)
        arm_raise = -20 if self.on_vine else 0
        pygame.draw.line(self.image, BODY_COLOR, (cx - 12, cy - 2), (cx - 28, cy - 12 + arm_raise), 5)
        pygame.draw.line(self.image, BODY_COLOR, (cx + 12, cy - 2), (cx + 28, cy - 12 + arm_raise), 5)

        # Legs
        pygame.draw.line(self.image, BODY_COLOR, (cx - 6, cy + 24), (cx - 10, cy + 40), 5)
        pygame.draw.line(self.image, BODY_COLOR, (cx + 6, cy + 24), (cx + 10, cy + 40), 5)

        # Feet
        pygame.draw.ellipse(self.image, BODY_COLOR, (cx - 15, cy + 37, 12, 6))
        pygame.draw.ellipse(self.image, BODY_COLOR, (cx + 6, cy + 37, 12, 6))

        self.rect = self.image.get_rect(center=(int(self.world_x), int(self.world_y)))
