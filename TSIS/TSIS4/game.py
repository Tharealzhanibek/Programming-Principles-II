import pygame
import random
import json
import os
import config

def load_settings() -> dict:
    """Load settings.json and merge with defaults (new keys get default values)."""
    if os.path.exists(config.SETTINGS_FILE):
        try:
            with open(config.SETTINGS_FILE) as f:
                data = json.load(f)
            return {**config.DEFAULT_SETTINGS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(config.DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    """Write the settings dict to settings.json."""
    try:
        with open(config.SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError as exc:
        print(f"[settings] Could not save: {exc}")


# ── custom pygame event fired every time the snake should take a step ──────────
SNAKE_MOVE = pygame.USEREVENT + 1


def _set_move_timer(steps_per_sec: int) -> None:
    """Reconfigure the SNAKE_MOVE timer to the given steps-per-second rate."""
    interval_ms = max(50, 1000 // max(1, steps_per_sec))
    pygame.time.set_timer(SNAKE_MOVE, interval_ms)


# ══════════════════════════════════════════════════════════════════════════════
# GameScreen
# ══════════════════════════════════════════════════════════════════════════════

class GameScreen:
    """
    Runs one Snake game session and returns a result dict when it ends.

    The rendering loop runs at RENDER_FPS (60 fps).  Snake movement is driven
    by a separate SNAKE_MOVE timer event whose interval changes with level /
    power-up effects — this separates display smoothness from game logic speed.
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 settings: dict, personal_best: int) -> None:
        self.screen        = screen
        self.clock         = clock
        self.settings      = settings
        self.personal_best = personal_best

        # ── snake ──────────────────────────────────────────────────────────────
        # All positions use pixel coordinates that are multiples of CELL.
        # snake_body[0] is the head.
        self.snake_pos  = [100, 50]
        self.snake_body = [[100,50],[90,50],[80,50],[70,50]]
        self.direction  = "RIGHT"
        self.change_to  = "RIGHT"   # buffered from key press; applied each step

        # ── score / level ──────────────────────────────────────────────────────
        self.score       = 0
        self.level       = 1
        self.foods_eaten = 0        # running count toward the next level-up

        # ── snake step speed ───────────────────────────────────────────────────
        self.base_steps = config.BASE_STEPS   # increases each level-up
        _set_move_timer(self.base_steps)

        # ── normal food ────────────────────────────────────────────────────────
        self.food_pos        = None   # [x, y] pixel position, or None
        self.food_type       = None   # entry from config.FOOD_TYPES
        self.food_spawn_tick = 0      # pygame.time.get_ticks() at spawn
        self._spawn_food()

        # ── poison food ────────────────────────────────────────────────────────
        self.poison_pos        = None
        self.poison_spawn_tick = 0
        self.next_poison_tick  = pygame.time.get_ticks() + config.POISON_SPAWN_MS

        # ── power-up on the field ──────────────────────────────────────────────
        self.field_pu_pos    = None   # [x, y] or None
        self.field_pu_kind   = None   # "speed" | "slow" | "shield"
        self.field_pu_tick   = 0
        self.next_pu_tick    = pygame.time.get_ticks() + config.PU_SPAWN_MS

        # ── active power-up effect ─────────────────────────────────────────────
        self.active_effect   = None   # "speed" | "slow" | "shield" | None
        self.effect_end_tick = 0      # tick when speed/slow expires
        self.shield_armed    = False  # True = next fatal collision is absorbed

        # ── obstacle wall blocks ───────────────────────────────────────────────
        self.obstacles: set = set()   # set of (x, y) pixel tuples

        # ── fonts (created once) ───────────────────────────────────────────────
        self._f_big   = pygame.font.SysFont("Verdana", 52)
        self._f_med   = pygame.font.SysFont("Verdana", 20)
        self._f_small = pygame.font.SysFont("Verdana", 14)

    # ══════════════════════════════════════════════════════════════════════════
    # Coordinate / placement helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _occupied(self, extra: set = None) -> set:
        """Return the set of all pixel (x, y) positions currently in use."""
        used = {(b[0], b[1]) for b in self.snake_body}
        used |= self.obstacles
        if self.food_pos:
            used.add((self.food_pos[0],   self.food_pos[1]))
        if self.poison_pos:
            used.add((self.poison_pos[0], self.poison_pos[1]))
        if self.field_pu_pos:
            used.add((self.field_pu_pos[0], self.field_pu_pos[1]))
        if extra:
            used |= extra
        return used

    def _free_cell(self, extra: set = None):
        """Return a random free [x, y] pixel position, or None if the board is full."""
        blocked = self._occupied(extra)
        free = [
            [c * config.CELL, r * config.CELL]
            for c in range(config.COLS)
            for r in range(config.ROWS)
            if (c * config.CELL, r * config.CELL) not in blocked
        ]
        return random.choice(free) if free else None

    # ══════════════════════════════════════════════════════════════════════════
    # Spawn helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _spawn_food(self) -> None:
        """Pick a weighted food type and place it at a random free cell."""
        weights         = [ft["weight"] for ft in config.FOOD_TYPES]
        self.food_type  = random.choices(config.FOOD_TYPES, weights=weights, k=1)[0]
        pos = self._free_cell()
        if pos:
            self.food_pos        = pos
            self.food_spawn_tick = pygame.time.get_ticks()

    def _spawn_poison(self) -> None:
        """Place poison food at a random free cell."""
        pos = self._free_cell()
        if pos:
            self.poison_pos        = pos
            self.poison_spawn_tick = pygame.time.get_ticks()

    def _spawn_powerup(self) -> None:
        """Place a random power-up at a random free cell."""
        kind = random.choice(["speed", "slow", "shield"])
        pos  = self._free_cell()
        if pos:
            self.field_pu_pos  = pos
            self.field_pu_kind = kind
            self.field_pu_tick = pygame.time.get_ticks()

    # ══════════════════════════════════════════════════════════════════════════
    # Obstacle generation  (BFS safety check)
    # ══════════════════════════════════════════════════════════════════════════

    def _flood_fill(self, start: list, extra_blocked: set) -> int:
        """
        BFS from start pixel position; count cells reachable without crossing
        snake body or extra_blocked (candidate obstacle pixels).
        Returns the number of reachable distinct grid cells.
        """
        body_px = {(b[0], b[1]) for b in self.snake_body}
        blocked = body_px | extra_blocked
        visited = set()
        queue   = [(start[0], start[1])]
        C = config.CELL
        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited or (x, y) in blocked:
                continue
            if not (0 <= x < config.SCREEN_WIDTH and 0 <= y < config.SCREEN_HEIGHT):
                continue
            visited.add((x, y))
            for dx, dy in [(C, 0), (-C, 0), (0, C), (0, -C)]:
                queue.append((x + dx, y + dy))
        return len(visited)

    def _generate_obstacles(self) -> None:
        """
        Randomly place obstacle blocks for the current level (from level 3).
        Uses BFS to guarantee the snake can still reach ≥ OBS_MIN_REACH cells.
        Falls back to no obstacles if a safe layout cannot be found in 30 tries.
        """
        if self.level < config.OBS_START_LEVEL:
            self.obstacles = set()
            return

        count   = (config.OBS_BASE_COUNT
                   + (self.level - config.OBS_START_LEVEL) * config.OBS_PER_LEVEL)
        hx, hy  = self.snake_pos

        for _ in range(30):
            candidates: set = set()
            tries = 0
            while len(candidates) < count and tries < 300:
                tries += 1
                x = random.randrange(config.COLS) * config.CELL
                y = random.randrange(config.ROWS) * config.CELL
                # keep obstacles away from the snake's current head position
                if (abs(x - hx) + abs(y - hy)) // config.CELL < 5:
                    continue
                if any(b[0] == x and b[1] == y for b in self.snake_body):
                    continue
                candidates.add((x, y))

            if len(candidates) < count:
                continue

            # BFS check: snake must still be able to reach enough cells
            if self._flood_fill(self.snake_pos, candidates) >= config.OBS_MIN_REACH:
                self.obstacles = candidates
                return

        # no safe layout found → place no obstacles this level
        self.obstacles = set()

    # ══════════════════════════════════════════════════════════════════════════
    # Speed / level helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _apply_speed(self) -> None:
        """Recalculate and set the SNAKE_MOVE timer based on current state."""
        if self.active_effect == "speed":
            _set_move_timer(self.base_steps * 2)
        elif self.active_effect == "slow":
            _set_move_timer(max(2, self.base_steps // 2))
        else:
            _set_move_timer(self.base_steps)

    def _level_up(self) -> None:
        """Advance to the next level: faster speed, new obstacles."""
        self.level      += 1
        self.foods_eaten = 0
        self.base_steps  = config.BASE_STEPS + (self.level - 1) * config.STEPS_PER_LVL
        self._apply_speed()
        self._generate_obstacles()

    # ══════════════════════════════════════════════════════════════════════════
    # One step of snake logic  (called on each SNAKE_MOVE event)
    # ══════════════════════════════════════════════════════════════════════════

    def _step(self) -> bool:
        """
        Move the snake one cell in the current direction, then handle all
        collisions and timed events.
        Returns True if the run has ended (game over).
        """
        now = pygame.time.get_ticks()

        # ── apply buffered direction (block 180° reversals) ────────────────────
        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if self.change_to != opposites.get(self.direction):
            self.direction = self.change_to

        # ── move head ─────────────────────────────────────────────────────────
        deltas = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        dx, dy = deltas[self.direction]
        self.snake_pos = [
            self.snake_pos[0] + dx * config.CELL,
            self.snake_pos[1] + dy * config.CELL,
        ]

        # ── fatal collision check (wall / self / obstacle) ─────────────────────
        x, y = self.snake_pos
        hit_wall     = not (0 <= x < config.SCREEN_WIDTH and 0 <= y < config.SCREEN_HEIGHT)
        hit_self     = any(b[0] == x and b[1] == y for b in self.snake_body[1:])
        hit_obstacle = (x, y) in self.obstacles

        if hit_wall or hit_self or hit_obstacle:
            if self.shield_armed:
                # shield absorbs one fatal collision – revert head position
                self.snake_pos  = list(self.snake_body[0])
                self.shield_armed   = False
                self.active_effect  = None
            else:
                return True     # game over

        # ── insert new head ────────────────────────────────────────────────────
        self.snake_body.insert(0, list(self.snake_pos))
        grow = False

        # ── normal food ────────────────────────────────────────────────────────
        if self.food_pos and self.snake_pos == self.food_pos:
            self.score       += self.food_type["value"]
            self.foods_eaten += 1
            self.food_pos     = None
            grow              = True
            self._spawn_food()
            if self.foods_eaten >= config.FOODS_PER_LVL:
                self._level_up()

        # ── poison food ────────────────────────────────────────────────────────
        elif self.poison_pos and self.snake_pos == self.poison_pos:
            self.poison_pos = None
            # shorten snake by 2 segments (never remove the head)
            for _ in range(min(2, len(self.snake_body) - 1)):
                self.snake_body.pop()
            if len(self.snake_body) <= 1:
                return True     # snake too short → game over

        # ── power-up ───────────────────────────────────────────────────────────
        elif self.field_pu_pos and self.snake_pos == self.field_pu_pos:
            kind = self.field_pu_kind
            self.field_pu_pos  = None
            self.field_pu_kind = None

            if kind == "shield":
                self.shield_armed    = True
                self.active_effect   = "shield"
                self.effect_end_tick = now + config.PU_EFFECT_MS   # HUD timer only
            else:
                self.active_effect   = kind          # "speed" | "slow"
                self.effect_end_tick = now + config.PU_EFFECT_MS
                self._apply_speed()

        # ── tail: pop unless growing ───────────────────────────────────────────
        if not grow:
            self.snake_body.pop()

        # ── expire speed / slow effects ────────────────────────────────────────
        if self.active_effect in ("speed", "slow") and now > self.effect_end_tick:
            self.active_effect = None
            self._apply_speed()

        # ── expire field items ─────────────────────────────────────────────────
        if self.food_pos:
            if now - self.food_spawn_tick > self.food_type["lifetime_ms"]:
                self.food_pos = None
                self._spawn_food()

        if self.poison_pos:
            if now - self.poison_spawn_tick > config.POISON_FIELD_MS:
                self.poison_pos = None

        if self.field_pu_pos:
            if now - self.field_pu_tick > config.PU_FIELD_MS:
                self.field_pu_pos  = None
                self.field_pu_kind = None

        # ── timed spawns ───────────────────────────────────────────────────────
        if not self.poison_pos and now >= self.next_poison_tick:
            self._spawn_poison()
            self.next_poison_tick = now + config.POISON_SPAWN_MS

        if not self.field_pu_pos and now >= self.next_pu_tick:
            self._spawn_powerup()
            self.next_pu_tick = now + config.PU_SPAWN_MS

        return False    # still alive

    # ══════════════════════════════════════════════════════════════════════════
    # Drawing
    # ══════════════════════════════════════════════════════════════════════════

    def _draw(self) -> None:
        now = pygame.time.get_ticks()
        self.screen.fill(config.BLACK)

        # ── optional grid overlay ──────────────────────────────────────────────
        if self.settings.get("grid"):
            for col in range(config.COLS):
                pygame.draw.line(self.screen, config.GRID_LN,
                                 (col * config.CELL, 0),
                                 (col * config.CELL, config.SCREEN_HEIGHT))
            for row in range(config.ROWS):
                pygame.draw.line(self.screen, config.GRID_LN,
                                 (0, row * config.CELL),
                                 (config.SCREEN_WIDTH, row * config.CELL))

        # ── obstacle wall blocks ───────────────────────────────────────────────
        for ox, oy in self.obstacles:
            pygame.draw.rect(self.screen, config.OBS_C,
                             (ox, oy, config.CELL, config.CELL))
            pygame.draw.rect(self.screen, config.GREY,
                             (ox, oy, config.CELL, config.CELL), 1)

        # ── snake body ─────────────────────────────────────────────────────────
        snake_color = tuple(self.settings.get("snake_color", [0, 200, 0]))
        # head is slightly brighter than the body
        head_color  = tuple(min(255, c + 55) for c in snake_color)
        for i, seg in enumerate(self.snake_body):
            col = head_color if i == 0 else snake_color
            pygame.draw.rect(self.screen, col,
                             (seg[0], seg[1], config.CELL, config.CELL))

        # blue outline on head when shield is armed
        if self.shield_armed:
            h = self.snake_body[0]
            pygame.draw.rect(self.screen, config.BLUE,
                             (h[0] - 1, h[1] - 1, config.CELL + 2, config.CELL + 2), 2)

        # ── normal food ────────────────────────────────────────────────────────
        if self.food_pos and self.food_type:
            pygame.draw.rect(self.screen, self.food_type["color"],
                             (self.food_pos[0], self.food_pos[1],
                              config.CELL, config.CELL))

            # countdown timer label (colour shifts green → red)
            elapsed   = now - self.food_spawn_tick
            remaining = max(0, self.food_type["lifetime_ms"] - elapsed)
            ratio     = remaining / self.food_type["lifetime_ms"]
            r = int(255 * (1 - ratio));  g = int(255 * ratio)
            t = self._f_small.render(f"{remaining // 1000}s", True, (r, g, 0))
            self.screen.blit(t, (self.food_pos[0], self.food_pos[1] - 12))

            # point value label
            v = self._f_small.render(f"+{self.food_type['value']}", True,
                                     self.food_type["color"])
            self.screen.blit(v, (self.food_pos[0] + config.CELL + 2, self.food_pos[1]))

        # ── poison food ────────────────────────────────────────────────────────
        if self.poison_pos:
            pygame.draw.rect(self.screen, config.POISON_C,
                             (self.poison_pos[0], self.poison_pos[1],
                              config.CELL, config.CELL))
            pygame.draw.rect(self.screen, config.RED,
                             (self.poison_pos[0], self.poison_pos[1],
                              config.CELL, config.CELL), 1)
            lbl = self._f_small.render("-2", True, config.RED)
            self.screen.blit(lbl, (self.poison_pos[0], self.poison_pos[1] - 12))

        # ── field power-up ─────────────────────────────────────────────────────
        if self.field_pu_pos and self.field_pu_kind:
            pu_col  = {"speed": config.YELLOW, "slow": config.BLUE,
                       "shield": (40, 200, 200)}[self.field_pu_kind]
            pu_icon = {"speed": "S+", "slow": "S-", "shield": "SH"}[self.field_pu_kind]

            pygame.draw.rect(self.screen, pu_col,
                             (self.field_pu_pos[0], self.field_pu_pos[1],
                              config.CELL, config.CELL))

            icon_surf = self._f_small.render(pu_icon, True, config.BLACK)
            self.screen.blit(icon_surf,
                             (self.field_pu_pos[0] - 4, self.field_pu_pos[1] - 14))

            # shrinking timeout bar above the power-up cell
            elapsed  = now - self.field_pu_tick
            ratio    = max(0.0, 1.0 - elapsed / config.PU_FIELD_MS)
            bar_w    = int(config.CELL * ratio)
            pygame.draw.rect(self.screen, pu_col,
                             (self.field_pu_pos[0], self.field_pu_pos[1] - 4,
                              bar_w, 3))

        # ── HUD ────────────────────────────────────────────────────────────────
        self._draw_hud(now)

    def _draw_hud(self, now: int) -> None:
        """Render score, level, personal best, and active effect indicator."""
        # score – top left
        sc = self._f_med.render(f"Score: {self.score}", True, config.WHITE)
        self.screen.blit(sc, (4, 2))

        # level – top centre
        lv = self._f_med.render(f"Level {self.level}", True, config.YELLOW)
        self.screen.blit(lv, (config.SCREEN_WIDTH // 2 - lv.get_width() // 2, 2))

        # personal best – top right
        pb = self._f_med.render(f"Best: {self.personal_best}", True, config.SILVER)
        self.screen.blit(pb, (config.SCREEN_WIDTH - pb.get_width() - 4, 2))

        # active power-up effect – bottom left
        if self.active_effect:
            pu_col = {"speed":  config.YELLOW,
                      "slow":   config.BLUE,
                      "shield": (40, 200, 200)}[self.active_effect]
            if self.active_effect == "shield":
                tag = "[SHIELD] ARMED"
            else:
                remaining_s = max(0, (self.effect_end_tick - now) // 1000)
                tag = f"[{self.active_effect.upper()}] {remaining_s}s"
            ef = self._f_small.render(tag, True, pu_col)
            self.screen.blit(ef, (4, config.SCREEN_HEIGHT - 18))

        # level-up progress bar – bottom right
        foods_left = config.FOODS_PER_LVL - self.foods_eaten
        prog = self._f_small.render(f"Next lvl: {foods_left} food", True, config.GREY)
        self.screen.blit(prog, (config.SCREEN_WIDTH - prog.get_width() - 4,
                                config.SCREEN_HEIGHT - 18))

    # ══════════════════════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════════════════════

    def run(self) -> dict:
        """Block until the game session ends; return the result dict."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys; sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:     self.change_to = "UP"
                    if event.key == pygame.K_DOWN:   self.change_to = "DOWN"
                    if event.key == pygame.K_LEFT:   self.change_to = "LEFT"
                    if event.key == pygame.K_RIGHT:  self.change_to = "RIGHT"
                    if event.key == pygame.K_ESCAPE:
                        # ESC counts as a voluntary exit (score still saved)
                        return {"score": self.score, "level": self.level}

                # snake logic fires only on SNAKE_MOVE, not every render frame
                if event.type == SNAKE_MOVE:
                    if self._step():
                        return {"score": self.score, "level": self.level}

            self._draw()
            pygame.display.flip()
            self.clock.tick(config.RENDER_FPS)
