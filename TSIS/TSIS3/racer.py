"""
racer.py
Core gameplay for a single run.

Entities:
  Road          – scrolling lane markers, kerbs, grass
  Player        – player car; shield and slow state
  TrafficCar    – enemy vehicle; collision = game over (or shield absorbs)
  Coin          – weighted collectible (bronze/silver/gold)
  Obstacle      – oil spill (slow), barrier / pothole (deadly without shield)
  RoadEvent     – nitro strip, speed bump, slow zone painted on the road
  PowerUp       – Nitro / Shield / Repair collectible

Game class orchestrates spawning, collision, HUD, difficulty scaling,
and saves the run result to the leaderboard via persistence.add_score().
"""
import pygame
import random
import time
import sys
from persistence import add_score

# ── palette ────────────────────────────────────────────────────────────────────
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)

ROAD_COLOR  = (45,  45,  55)
GRASS_COLOR = (30,  90,  30)
LANE_COLOR  = (200, 200, 200)
KERB_RED    = (210, 50,  50)
KERB_WHITE  = (240, 240, 240)

# ── car colour options (mapped from settings string) ──────────────────────────
CAR_COLOR_MAP = {
    "blue":   (40,  140, 255),
    "red":    (255, 60,  60),
    "green":  (60,  220, 80),
    "yellow": (255, 220, 40),
}

# ── screen layout ──────────────────────────────────────────────────────────────
SW = 400          # screen width
SH = 600          # screen height

ROAD_LEFT  = 50              # x of left road edge
ROAD_RIGHT = 350             # x of right road edge
ROAD_W     = ROAD_RIGHT - ROAD_LEFT   # 300 px road width

# Centres of the three lanes
LANE_CENTERS = [
    ROAD_LEFT + ROAD_W // 6,         # ~100
    ROAD_LEFT + ROAD_W // 2,         # ~200
    ROAD_LEFT + 5 * ROAD_W // 6,     # ~300
]

# ── difficulty presets ─────────────────────────────────────────────────────────
DIFFICULTY_CFG = {
    "easy":   {"base_speed": 4, "traffic_ms": 3000, "max_traffic": 1, "obs_ms": 5000},
    "normal": {"base_speed": 5, "traffic_ms": 2000, "max_traffic": 2, "obs_ms": 3500},
    "hard":   {"base_speed": 7, "traffic_ms": 1200, "max_traffic": 4, "obs_ms": 2000},
}

# ── coin definitions ───────────────────────────────────────────────────────────
COIN_TYPES = [
    {"value": 1, "color": (205, 127, 50),  "weight": 60, "label": "bronze"},
    {"value": 3, "color": (192, 192, 192), "weight": 30, "label": "silver"},
    {"value": 5, "color": (255, 215,   0), "weight": 10, "label": "gold"},
]

# ── power-up definitions ───────────────────────────────────────────────────────
POWERUP_TYPES    = ["nitro", "shield", "repair"]
POWERUP_COLORS   = {"nitro":  (255, 220,  40),
                    "shield": ( 40, 180, 255),
                    "repair": ( 60, 220, 100)}
POWERUP_DURATION = {"nitro": 4.0, "shield": 9999, "repair": 0}
POWERUP_TIMEOUT  = 8.0      # seconds before uncollected power-up vanishes


# ══════════════════════════════════════════════════════════════════════════════
# Drawing helper
# ══════════════════════════════════════════════════════════════════════════════

def draw_car(surface: pygame.Surface, cx: int, cy: int,
             w: int, h: int, body_color, window_color=(160, 200, 255)) -> None:
    """
    Draw a simple top-down car silhouette centred at (cx, cy).
    body_color  – main paint colour
    window_color – windshield tint
    """
    x, y = cx - w // 2, cy - h // 2

    pygame.draw.rect(surface, body_color,   (x,    y,       w,    h),    border_radius=6)
    pygame.draw.rect(surface, window_color, (x+4,  y+4,     w-8,  h//4), border_radius=3)
    pygame.draw.rect(surface, window_color, (x+4,  y+h-h//4-4, w-8, h//4), border_radius=3)

    # four wheels
    ww, wh = max(6, w // 5), max(4, h // 8)
    for wx, wy in [(x - ww//2,   y + 6),
                   (x + w - ww//2, y + 6),
                   (x - ww//2,   y + h - wh - 6),
                   (x + w - ww//2, y + h - wh - 6)]:
        pygame.draw.rect(surface, (20, 20, 20), (wx, wy, ww, wh), border_radius=2)


# ══════════════════════════════════════════════════════════════════════════════
# Road
# ══════════════════════════════════════════════════════════════════════════════

class Road:
    """
    Scrolling road background.
    Draws: grass → kerb strips → road surface → dashed lane dividers.
    The scroll offsets update every frame with the current speed so
    all markings appear to move toward the player.
    """

    DASH_LEN   = 40
    DASH_GAP   = 30
    DASH_TOTAL = DASH_LEN + DASH_GAP
    KERB_SEG   = 20     # height of each alternating kerb segment

    def __init__(self) -> None:
        self.scroll      = 0      # lane-dash phase (pixels)
        self.kerb_scroll = 0     # kerb-stripe phase (pixels)

    def update(self, speed: float) -> None:
        self.scroll      = (self.scroll      + speed) % self.DASH_TOTAL
        self.kerb_scroll = (self.kerb_scroll + speed) % self.KERB_SEG

    def draw(self, surface: pygame.Surface) -> None:
        # grass strips on both sides
        pygame.draw.rect(surface, GRASS_COLOR, (0,          0, ROAD_LEFT,          SH))
        pygame.draw.rect(surface, GRASS_COLOR, (ROAD_RIGHT, 0, SW - ROAD_RIGHT,    SH))

        # main road surface
        pygame.draw.rect(surface, ROAD_COLOR,  (ROAD_LEFT,  0, ROAD_W, SH))

        # alternating kerb strips (red/white, 8 px wide each side)
        kw = 8
        for i in range(SH // self.KERB_SEG + 2):
            y   = i * self.KERB_SEG - int(self.kerb_scroll)
            col = KERB_RED if i % 2 == 0 else KERB_WHITE
            pygame.draw.rect(surface, col, (ROAD_LEFT,          y, kw, self.KERB_SEG))
            pygame.draw.rect(surface, col, (ROAD_RIGHT - kw,    y, kw, self.KERB_SEG))

        # dashed lane dividers at 1/3 and 2/3 of road width
        for lx in [ROAD_LEFT + ROAD_W // 3, ROAD_LEFT + 2 * ROAD_W // 3]:
            y = -(self.DASH_TOTAL - int(self.scroll) % self.DASH_TOTAL)
            while y < SH:
                pygame.draw.rect(surface, LANE_COLOR, (lx - 2, int(y), 4, self.DASH_LEN))
                y += self.DASH_TOTAL


# ══════════════════════════════════════════════════════════════════════════════
# Player
# ══════════════════════════════════════════════════════════════════════════════

class Player:
    """
    The player's car.  Moves left/right within road boundaries.
    State flags:
      shield  – True while shield power-up protects the car
      slowed  – True while on an oil spill / slow zone
    """

    W, H       = 36, 56
    MOVE_SPEED = 5

    def __init__(self, color=(40, 140, 255)) -> None:
        self.color      = color
        self.cx         = SW // 2
        self.cy         = SH - 90
        self.shield     = False
        self.slowed     = False
        self.slow_until = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.cx - self.W // 2, self.cy - self.H // 2,
                           self.W, self.H)

    def move(self, keys) -> None:
        spd = max(2, self.MOVE_SPEED - (2 if self.slowed else 0))
        if keys[pygame.K_LEFT]  and self.cx - self.W // 2 > ROAD_LEFT  + 10:
            self.cx -= spd
        if keys[pygame.K_RIGHT] and self.cx + self.W // 2 < ROAD_RIGHT - 10:
            self.cx += spd

        # expire the slow effect when its timer is up
        if self.slowed and time.time() > self.slow_until:
            self.slowed = False

    def draw(self, surface: pygame.Surface) -> None:
        draw_car(surface, self.cx, self.cy, self.W, self.H, self.color)

        # blue glow ring when shield is active
        if self.shield:
            r = max(self.W, self.H) // 2 + 8
            s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (40, 180, 255,  70), (r + 2, r + 2), r)
            pygame.draw.circle(s, (40, 180, 255, 200), (r + 2, r + 2), r, 2)
            surface.blit(s, (self.cx - r - 2, self.cy - r - 2))


# ══════════════════════════════════════════════════════════════════════════════
# Traffic Car
# ══════════════════════════════════════════════════════════════════════════════

class TrafficCar:
    """
    Enemy vehicle that spawns above the screen and falls downward.
    Safe spawn: never placed directly above the player's current lane.
    Collision ends the run unless the player has a shield.
    """

    W, H = 34, 52
    COLORS = [
        (160, 60,  60), (60,  80, 160), (160, 140, 60),
        (100, 100, 100), (80, 150, 80),
    ]

    def __init__(self, base_speed: float, player_cx: int) -> None:
        self.color = random.choice(self.COLORS)

        # pick a lane not directly over the player (safe spawn)
        lane = random.choice(LANE_CENTERS)
        attempts = 0
        while abs(lane - player_cx) < 50 and attempts < 10:
            lane = random.choice(LANE_CENTERS)
            attempts += 1

        self.cx     = lane + random.randint(-18, 18)
        self.cy     = -self.H
        self.speed  = base_speed + random.uniform(-0.5, 1.8)
        self.active = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.cx - self.W // 2, self.cy - self.H // 2,
                           self.W, self.H)

    def update(self) -> None:
        self.cy += self.speed
        if self.cy > SH + self.H:
            self.active = False     # scrolled off screen – remove quietly

    def draw(self, surface: pygame.Surface) -> None:
        draw_car(surface, self.cx, self.cy, self.W, self.H,
                 self.color, window_color=(220, 230, 240))


# ══════════════════════════════════════════════════════════════════════════════
# Coin  (weighted)
# ══════════════════════════════════════════════════════════════════════════════

class Coin:
    """
    Collectible coin drawn as a coloured circle.
    bronze (common) = 1 pt  ·  silver = 3 pts  ·  gold (rare) = 5 pts
    Selected by weighted random choice from COIN_TYPES.
    """

    R = 12

    def __init__(self, base_speed: float) -> None:
        weights   = [ct["weight"] for ct in COIN_TYPES]
        coin_type = random.choices(COIN_TYPES, weights=weights, k=1)[0]
        self.value  = coin_type["value"]
        self.color  = coin_type["color"]
        self.cx     = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
        self.cy     = -self.R
        self.speed  = base_speed * 0.8
        self.active = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.cx - self.R, self.cy - self.R,
                           self.R * 2, self.R * 2)

    def update(self) -> None:
        self.cy += self.speed
        if self.cy > SH + self.R:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, (int(self.cx), int(self.cy)), self.R)
        pygame.draw.circle(surface, WHITE,      (int(self.cx), int(self.cy)), self.R, 1)
        font = pygame.font.SysFont("Verdana", 10, bold=True)
        lbl  = font.render(f"+{self.value}", True, BLACK)
        surface.blit(lbl, (int(self.cx) - lbl.get_width()  // 2,
                           int(self.cy) - lbl.get_height() // 2))


# ══════════════════════════════════════════════════════════════════════════════
# Obstacle  (lane hazard)
# ══════════════════════════════════════════════════════════════════════════════

class Obstacle:
    """
    Static road hazard that falls from the top.

    oil     – dark ellipse; slows the player for 3 s on contact
    barrier – red rectangle; ends the run (or removes shield)
    pothole – grey ellipse; same effect as barrier
    """

    def __init__(self, kind: str, base_speed: float) -> None:
        self.kind  = kind
        self.cx    = random.randint(ROAD_LEFT + 22, ROAD_RIGHT - 22)
        self.cy    = -30
        self.speed = base_speed * 0.7
        self.w, self.h = (54, 22) if kind == "oil" else (42, 20)
        self.active = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.cx - self.w // 2, self.cy - self.h // 2,
                           self.w, self.h)

    def update(self) -> None:
        self.cy += self.speed
        if self.cy > SH + 40:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        bx = self.cx - self.w // 2
        by = self.cy - self.h // 2

        if self.kind == "oil":
            s = pygame.Surface((self.w + 4, self.h + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (10,  10,  10, 200), (2, 2, self.w, self.h))
            pygame.draw.ellipse(s, (60,  60,  80, 180), (2, 2, self.w, self.h), 2)
            surface.blit(s, (bx - 2, by - 2))

        elif self.kind == "barrier":
            pygame.draw.rect(surface, (210, 50,  50), (bx, by, self.w, self.h), border_radius=4)
            pygame.draw.rect(surface, (255, 200, 40), (bx, by, self.w, self.h), 2, border_radius=4)
            font = pygame.font.SysFont("Verdana", 9, bold=True)
            lbl  = font.render("BARRIER", True, WHITE)
            surface.blit(lbl, (self.cx - lbl.get_width()  // 2,
                               self.cy - lbl.get_height() // 2))

        elif self.kind == "pothole":
            pygame.draw.ellipse(surface, (25, 25, 25), (bx, by, self.w, self.h))
            pygame.draw.ellipse(surface, (70, 70, 70), (bx, by, self.w, self.h), 2)


# ══════════════════════════════════════════════════════════════════════════════
# Road Event  (dynamic track feature)
# ══════════════════════════════════════════════════════════════════════════════

class RoadEvent:
    """
    Painted road feature that scrolls with the track.

    nitro_strip – yellow stripe across one lane; short nitro burst on crossing
    speed_bump  – grey stripe across full road; brief slowdown
    slow_zone   – red-tinted lane area; player slows while inside
    """

    def __init__(self, kind: str, base_speed: float) -> None:
        self.kind      = kind
        self.speed     = base_speed * 0.75
        self.active    = True
        self.triggered = False   # prevent re-triggering each frame

        if kind == "nitro_strip":
            lane = random.choice(LANE_CENTERS)
            self.rect = pygame.Rect(lane - 32, -16, 64, 16)
        elif kind == "speed_bump":
            self.rect = pygame.Rect(ROAD_LEFT + 10, -14, ROAD_W - 20, 14)
        else:  # slow_zone
            lane = random.choice(LANE_CENTERS)
            self.rect = pygame.Rect(lane - 42, -110, 84, 110)

    def update(self) -> None:
        self.rect.y += int(self.speed)
        if self.rect.top > SH:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.kind == "nitro_strip":
            s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 220, 40, 210), s.get_rect(), border_radius=2)
            surface.blit(s, self.rect.topleft)
            font = pygame.font.SysFont("Verdana", 9, bold=True)
            lbl  = font.render("NITRO", True, BLACK)
            surface.blit(lbl, (self.rect.centerx - lbl.get_width()  // 2,
                               self.rect.centery - lbl.get_height() // 2))

        elif self.kind == "speed_bump":
            pygame.draw.rect(surface, (100, 100, 120), self.rect, border_radius=3)
            pygame.draw.rect(surface, (160, 160, 180), self.rect, 1,  border_radius=3)
            font = pygame.font.SysFont("Verdana", 8, bold=True)
            lbl  = font.render("BUMP", True, WHITE)
            surface.blit(lbl, (self.rect.centerx - lbl.get_width()  // 2,
                               self.rect.centery - lbl.get_height() // 2))

        else:  # slow_zone
            s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (210, 50, 50, 55), s.get_rect())
            surface.blit(s, self.rect.topleft)
            font = pygame.font.SysFont("Verdana", 9, bold=True)
            lbl  = font.render("SLOW ZONE", True, (220, 80, 80))
            ty   = max(self.rect.top + 2, 4)
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2, ty))


# ══════════════════════════════════════════════════════════════════════════════
# Power-Up
# ══════════════════════════════════════════════════════════════════════════════

class PowerUp:
    """
    Collectible power-up icon that scrolls down.
    Disappears after POWERUP_TIMEOUT seconds if the player never touches it.

    nitro  (N, yellow) – boosts road speed for 4 s
    shield (S, blue)   – absorbs the next collision
    repair (R, green)  – instantly clears any active slow/obstacle effect
    """

    R = 15

    def __init__(self, kind: str, base_speed: float) -> None:
        self.kind       = kind
        self.color      = POWERUP_COLORS[kind]
        self.cx         = random.randint(ROAD_LEFT + 28, ROAD_RIGHT - 28)
        self.cy         = -self.R
        self.speed      = base_speed * 0.65
        self.active     = True
        self.spawn_time = time.time()

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.cx - self.R, self.cy - self.R,
                           self.R * 2, self.R * 2)

    def update(self) -> None:
        self.cy += self.speed
        if self.cy > SH + self.R:
            self.active = False
        if time.time() - self.spawn_time > POWERUP_TIMEOUT:
            self.active = False     # timed out

    def draw(self, surface: pygame.Surface) -> None:
        ix, iy = int(self.cx), int(self.cy)
        pygame.draw.circle(surface, self.color, (ix, iy), self.R)
        pygame.draw.circle(surface, WHITE,      (ix, iy), self.R, 2)

        icon = {"nitro": "N", "shield": "S", "repair": "R"}[self.kind]
        font = pygame.font.SysFont("Verdana", 14, bold=True)
        lbl  = font.render(icon, True, BLACK)
        surface.blit(lbl, (ix - lbl.get_width()  // 2, iy - lbl.get_height() // 2))

        # shrinking timer bar above the icon
        elapsed  = time.time() - self.spawn_time
        ratio    = max(0.0, 1.0 - elapsed / POWERUP_TIMEOUT)
        bar_w    = int(self.R * 2 * ratio)
        pygame.draw.rect(surface, self.color,
                         (ix - self.R, iy - self.R - 6, bar_w, 4))


# ══════════════════════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════════════════════

def draw_hud(surface, score, coins, distance, active_pu, pu_end, shield,
             font_s, font_t) -> None:
    """
    Semi-transparent top bar: score | distance | coins
    Bottom strip: active power-up timer | shield indicator
    """
    # top HUD strip
    hud = pygame.Surface((SW, 40), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 165))
    surface.blit(hud, (0, 0))

    sc = font_s.render(f"Score: {score}", True, WHITE)
    surface.blit(sc, (8, 10))

    dm = font_s.render(f"{distance} m", True, (170, 215, 255))
    surface.blit(dm, (SW // 2 - dm.get_width() // 2, 10))

    co = font_s.render(f"Coins: {coins}", True, (255, 220, 40))
    surface.blit(co, (SW - co.get_width() - 8, 10))

    # bottom HUD strip
    bot = pygame.Surface((SW, 30), pygame.SRCALPHA)
    bot.fill((0, 0, 0, 130))
    surface.blit(bot, (0, SH - 30))

    if active_pu:
        remaining = max(0.0, pu_end - time.time())
        col = POWERUP_COLORS.get(active_pu, WHITE)
        tag = (f"[{active_pu.upper()}] ACTIVE"
               if remaining > 900
               else f"[{active_pu.upper()}] {remaining:.1f}s")
        ps = font_t.render(tag, True, col)
        surface.blit(ps, (8, SH - 22))

    if shield:
        ss = font_t.render("SHIELD ACTIVE", True, (40, 180, 255))
        surface.blit(ss, (SW - ss.get_width() - 8, SH - 22))


# ══════════════════════════════════════════════════════════════════════════════
# Game
# ══════════════════════════════════════════════════════════════════════════════

class Game:
    """
    Runs one complete race until the player crashes or presses Escape.
    Returns a result dict: {score, distance, coins, bonus}.
    """

    # milliseconds between spawn attempts
    COIN_MS    = 1800
    POWERUP_MS = 15000
    EVENT_MS   = 6000
    SCALE_MS   = 8000    # difficulty scaling cadence

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 settings: dict, username: str) -> None:
        self.screen   = screen
        self.clock    = clock
        self.settings = settings
        self.username = username

        # apply difficulty preset
        diff = settings.get("difficulty", "normal")
        cfg  = DIFFICULTY_CFG[diff]
        self.base_speed    = cfg["base_speed"]
        self.traffic_ms    = cfg["traffic_ms"]
        self.max_traffic   = cfg["max_traffic"]
        self.obs_ms        = cfg["obs_ms"]

        # player colour from settings
        color_name = settings.get("car_color", "blue")
        self.player = Player(color=CAR_COLOR_MAP.get(color_name, (40, 140, 255)))

        self.road = Road()

        # entity lists
        self.traffic   = []
        self.coins     = []
        self.obstacles = []
        self.events    = []
        self.powerups  = []

        # score tracking
        self.score       = 0     # points from coins only (distance bonus added at end)
        self.coin_count  = 0
        self.scroll_dist = 0     # total pixels scrolled
        self.bonus       = 0     # bonus from power-up interactions

        # active power-up state
        self.active_pu  = None   # name string or None
        self.pu_end     = 0.0    # time.time() expiry
        self.nitro_on   = False

        # sound toggle
        self.sound_on = settings.get("sound", True)

        # fonts (created once, reused every frame)
        self.font_s = pygame.font.SysFont("Verdana", 16)
        self.font_t = pygame.font.SysFont("Verdana", 13)

        # spawn timers (pygame ms)
        now = pygame.time.get_ticks()
        self.t_traffic = now
        self.t_coin    = now
        self.t_obs     = now
        self.t_event   = now
        self.t_powerup = now
        self.t_scale   = now

    # ── speed property ─────────────────────────────────────────────────────────
    @property
    def speed(self) -> float:
        """Current road scroll speed, boosted 50 % during nitro."""
        return self.base_speed * (1.5 if self.nitro_on else 1.0)

    # ── helpers ────────────────────────────────────────────────────────────────

    def _play(self, path: str) -> None:
        """Play a sound file if sound is enabled and the file exists."""
        if not self.sound_on:
            return
        try:
            pygame.mixer.Sound(path).play()
        except Exception:
            pass

    def _activate_pu(self, kind: str) -> None:
        """Apply the effect of a collected power-up."""
        self.active_pu = kind
        if kind == "nitro":
            self.nitro_on = True
            self.pu_end   = time.time() + POWERUP_DURATION["nitro"]
            self.bonus   += 10
        elif kind == "shield":
            self.player.shield = True
            self.pu_end        = time.time() + 9999     # until hit
            self.bonus        += 5
        elif kind == "repair":
            # instant: clear slow effect
            self.player.slowed = False
            self.active_pu     = None
            self.bonus        += 5

    def _tick_pu(self) -> None:
        """Expire the nitro effect when its timer runs out."""
        if self.active_pu == "nitro" and time.time() > self.pu_end:
            self.nitro_on  = False
            self.active_pu = None

    # ── spawning ───────────────────────────────────────────────────────────────

    def _spawn(self, now: int) -> None:
        """Check all spawn timers and create new entities as needed."""

        # traffic cars – respect max count for current difficulty
        if now - self.t_traffic >= self.traffic_ms:
            if len(self.traffic) < self.max_traffic:
                self.traffic.append(TrafficCar(self.speed, self.player.cx))
            self.t_traffic = now

        # coins – one at a time, falling continuously
        if now - self.t_coin >= self.COIN_MS:
            self.coins.append(Coin(self.speed))
            self.t_coin = now

        # road obstacles
        if now - self.t_obs >= self.obs_ms:
            kind = random.choices(["oil", "barrier", "pothole"],
                                  weights=[50, 25, 25], k=1)[0]
            self.obstacles.append(Obstacle(kind, self.speed))
            self.t_obs = now

        # road events (nitro strip, speed bump, slow zone)
        if now - self.t_event >= self.EVENT_MS:
            kind = random.choices(["nitro_strip", "speed_bump", "slow_zone"],
                                  weights=[40, 30, 30], k=1)[0]
            self.events.append(RoadEvent(kind, self.speed))
            self.t_event = now

        # power-ups – at most one on screen at a time
        if now - self.t_powerup >= self.POWERUP_MS and not self.powerups:
            kind = random.choice(POWERUP_TYPES)
            self.powerups.append(PowerUp(kind, self.speed))
            self.t_powerup = now

    # ── difficulty scaling ─────────────────────────────────────────────────────

    def _scale(self, now: int) -> None:
        """Gradually tighten spawn intervals and increase speed over time."""
        if now - self.t_scale >= self.SCALE_MS:
            self.traffic_ms  = max(500,  self.traffic_ms  - 100)
            self.obs_ms      = max(800,  self.obs_ms      - 150)
            self.max_traffic = min(6,    self.max_traffic + 1)
            self.base_speed += 0.3
            self.t_scale     = now

    # ── collision detection ────────────────────────────────────────────────────

    def _collisions(self) -> bool:
        """
        Check all entity collisions.
        Returns True if the run should end (fatal collision).
        """
        pr = self.player.rect

        # ── traffic cars ──────────────────────────────────────────────────────
        for car in self.traffic:
            if pr.colliderect(car.rect):
                if self.player.shield:
                    self.player.shield = False
                    self.active_pu     = None
                    car.active         = False
                    self.bonus        += 20    # shield-absorb bonus
                else:
                    return True                # fatal

        # ── road obstacles ────────────────────────────────────────────────────
        for obs in self.obstacles:
            if pr.colliderect(obs.rect):
                if obs.kind == "oil":
                    # slows the player for 3 seconds, then disappears
                    self.player.slowed    = True
                    self.player.slow_until = time.time() + 3.0
                    obs.active            = False
                elif obs.kind in ("barrier", "pothole"):
                    if self.player.shield:
                        self.player.shield = False
                        self.active_pu     = None
                        obs.active         = False
                        self.bonus        += 20
                    else:
                        return True            # fatal

        # ── coins ─────────────────────────────────────────────────────────────
        for coin in self.coins:
            if pr.colliderect(coin.rect):
                self.score      += coin.value
                self.coin_count += 1
                coin.active      = False
                self._play("sounds/coin_received.mp3")

        # ── power-ups ─────────────────────────────────────────────────────────
        for pu in self.powerups:
            if pr.colliderect(pu.rect):
                self._activate_pu(pu.kind)
                pu.active = False

        # ── road events (trigger once on first contact) ───────────────────────
        for ev in self.events:
            if not ev.triggered and pr.colliderect(ev.rect):
                ev.triggered = True
                if ev.kind == "nitro_strip" and not self.nitro_on:
                    self.nitro_on = True
                    self.pu_end   = time.time() + 2.0
                elif ev.kind == "speed_bump":
                    self.player.slowed    = True
                    self.player.slow_until = time.time() + 1.0
                elif ev.kind == "slow_zone":
                    self.player.slowed    = True
                    self.player.slow_until = time.time() + 2.5

        return False    # no fatal collision

    # ── result builder ─────────────────────────────────────────────────────────

    def _build_result(self) -> dict:
        """Compute the final score, save to leaderboard, return the result dict."""
        dist_m    = int(self.scroll_dist / 10)
        dist_pts  = int(self.scroll_dist / 200)
        total     = self.score + dist_pts + self.bonus
        add_score(self.username, total, dist_m, self.coin_count)
        return {
            "score":    total,
            "distance": dist_m,
            "coins":    self.coin_count,
            "bonus":    self.bonus,
        }

    # ── main loop ──────────────────────────────────────────────────────────────

    def run(self) -> dict:
        """Block until the run ends; return the result dict."""
        while True:
            now  = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()

            # ── events ────────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return self._build_result()    # voluntary quit

            # ── game logic ────────────────────────────────────────────────────
            self._spawn(now)
            self._scale(now)

            self.player.move(keys)
            self.road.update(self.speed)
            self.scroll_dist += self.speed
            self._tick_pu()

            for obj in self.traffic   + self.coins + \
                        self.obstacles + self.events + self.powerups:
                obj.update()

            # prune objects that moved off-screen or were collected
            self.traffic   = [o for o in self.traffic   if o.active]
            self.coins     = [o for o in self.coins     if o.active]
            self.obstacles = [o for o in self.obstacles if o.active]
            self.events    = [o for o in self.events    if o.active]
            self.powerups  = [o for o in self.powerups  if o.active]

            # ── fatal collision check ─────────────────────────────────────────
            if self._collisions():
                self._play("sounds/crash.wav")
                return self._build_result()

            # ── draw ──────────────────────────────────────────────────────────
            self.road.draw(self.screen)

            # draw order: road events → obstacles → coins → power-ups → traffic → player
            for ev  in self.events:    ev.draw(self.screen)
            for obs in self.obstacles: obs.draw(self.screen)
            for c   in self.coins:     c.draw(self.screen)
            for pu  in self.powerups:  pu.draw(self.screen)
            for car in self.traffic:   car.draw(self.screen)
            self.player.draw(self.screen)

            draw_hud(
                self.screen,
                score    = self.score + int(self.scroll_dist / 200) + self.bonus,
                coins    = self.coin_count,
                distance = int(self.scroll_dist / 10),
                active_pu = self.active_pu,
                pu_end   = self.pu_end,
                shield   = self.player.shield,
                font_s   = self.font_s,
                font_t   = self.font_t,
            )

            pygame.display.flip()
            self.clock.tick(60)
