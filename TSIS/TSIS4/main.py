
import pygame
import sys

import config
import db
from game import load_settings, save_settings, GameScreen

# ── shared UI palette ──────────────────────────────────────────────────────────
BG_COLOR    = (10,  15,  25)
PANEL_COLOR = (25,  32,  52)
BTN_COLOR   = (50,  75, 150)
BTN_HOVER   = (75, 110, 200)
BTN_BORDER  = (90, 140, 240)
TEXT_COLOR  = (225, 230, 255)
ACCENT      = (90,  200, 255)
DANGER      = (240, 70,  70)
SUCCESS     = (70,  215, 110)


# ── shared helpers ─────────────────────────────────────────────────────────────

def draw_bg(surface: pygame.Surface) -> None:
    surface.fill(BG_COLOR)


def draw_text(surface: pygame.Surface, text: str, size: int, color,
              cx: int, cy: int, bold: bool = False) -> None:
    """Render text centred at (cx, cy)."""
    font = pygame.font.SysFont("Verdana", size, bold=bold)
    surf = font.render(text, True, color)
    surface.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))


class Button:
    """Hover-sensitive clickable rectangle."""

    def __init__(self, cx: int, cy: int, w: int, h: int,
                 label: str, font_size: int = 18) -> None:
        self.rect        = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.label       = label
        self._font       = pygame.font.SysFont("Verdana", font_size, bold=True)

    def draw(self, surface: pygame.Surface) -> None:
        hov = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surface, BTN_HOVER if hov else BTN_COLOR,
                         self.rect, border_radius=7)
        pygame.draw.rect(surface, BTN_BORDER, self.rect, 2, border_radius=7)
        lbl = self._font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()  // 2,
                           self.rect.centery - lbl.get_height() // 2))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ══════════════════════════════════════════════════════════════════════════════
# Main Menu  (includes username entry)
# ══════════════════════════════════════════════════════════════════════════════

class MainMenuScreen:
    """
    Shows the game title, a text input for the username, and four buttons.
    run() returns:
        ("play", username_str)  |  "leaderboard"  |  "settings"  |  "quit"
    """
    MAX_NAME = 16

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock  = clock
        self.name   = ""
        W, H = screen.get_size()
        self.buttons = {
            "play":        Button(W // 2, 300, 210, 46, "Play"),
            "leaderboard": Button(W // 2, 356, 210, 46, "Leaderboard"),
            "settings":    Button(W // 2, 412, 210, 46, "Settings"),
            "quit":        Button(W // 2, 468, 210, 46, "Quit"),
        }
        self._input_font = pygame.font.SysFont("Verdana", 22, bold=True)
        self._hint_font  = pygame.font.SysFont("Verdana", 13)

    def run(self):
        W, H = self.screen.get_size()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key == pygame.K_RETURN and self.name.strip():
                        return ("play", self.name.strip())
                    elif (len(self.name) < self.MAX_NAME
                          and event.unicode.isprintable()):
                        self.name += event.unicode

                for key, btn in self.buttons.items():
                    if btn.is_clicked(event):
                        if key == "play" and self.name.strip():
                            return ("play", self.name.strip())
                        elif key != "play":
                            return key

            draw_bg(self.screen)
            draw_text(self.screen, "SNAKE", 56, ACCENT, W // 2, 78, bold=True)
            draw_text(self.screen, "Advanced Edition", 18, TEXT_COLOR, W // 2, 124)

            # username label
            draw_text(self.screen, "Enter username:", 16, (160, 170, 200),
                      W // 2, 174)

            # text input box
            box = pygame.Rect(W // 2 - 155, 186, 310, 46)
            pygame.draw.rect(self.screen, PANEL_COLOR, box, border_radius=7)
            pygame.draw.rect(self.screen, BTN_BORDER,  box, 2,  border_radius=7)
            name_surf = self._input_font.render(self.name + "|", True, TEXT_COLOR)
            self.screen.blit(name_surf, (box.x + 10, box.y + 9))

            hint = self._hint_font.render(
                "Type name, press Enter or click Play",
                True, (120, 130, 160))
            self.screen.blit(hint, (W // 2 - hint.get_width() // 2, 242))

            for btn in self.buttons.values():
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Game Over Screen
# ══════════════════════════════════════════════════════════════════════════════

class GameOverScreen:
    """
    Shows final score, level reached, personal best, and a new-best badge.
    run() returns "retry" | "menu".
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 result: dict, personal_best: int) -> None:
        self.screen        = screen
        self.clock         = clock
        self.result        = result
        self.personal_best = personal_best
        W, H = screen.get_size()
        self.retry = Button(W // 2 - 115, H - 120, 200, 46, "Retry")
        self.menu  = Button(W // 2 + 115, H - 120, 200, 46, "Main Menu")

    def run(self) -> str:
        W, H = self.screen.get_size()
        is_new_best = self.result["score"] > self.personal_best

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.retry.is_clicked(event): return "retry"
                if self.menu.is_clicked(event):  return "menu"

            draw_bg(self.screen)
            draw_text(self.screen, "GAME  OVER", 46, DANGER, W // 2, 95, bold=True)

            # stats panel
            panel = pygame.Rect(W // 2 - 175, 140, 350, 250)
            pygame.draw.rect(self.screen, PANEL_COLOR, panel, border_radius=10)
            pygame.draw.rect(self.screen, BTN_BORDER,  panel, 1,  border_radius=10)

            if is_new_best:
                draw_text(self.screen, "★ New Personal Best! ★", 17,
                          (255, 220, 40), W // 2, 158)

            stats = [
                ("Score",         str(self.result["score"]),  ACCENT),
                ("Level reached", str(self.result["level"]),  TEXT_COLOR),
                ("Personal best", str(self.personal_best),    SUCCESS),
            ]
            for i, (lbl, val, col) in enumerate(stats):
                y = 185 + i * 62
                draw_text(self.screen, lbl, 15, (160, 170, 210), W // 2 - 60, y)
                draw_text(self.screen, val, 24, col, W // 2 + 75, y, bold=True)

            self.retry.draw(self.screen)
            self.menu.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Leaderboard Screen
# ══════════════════════════════════════════════════════════════════════════════

class LeaderboardScreen:
    """
    Fetches the top-10 scores from PostgreSQL and renders them in a table.
    Shows an "offline" notice if the DB is unavailable.
    run() returns None.
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock  = clock
        W, H = screen.get_size()
        self.back   = Button(W // 2, H - 36, 190, 42, "Back")
        self._hfont = pygame.font.SysFont("Verdana", 13, bold=True)
        self._rfont = pygame.font.SysFont("Verdana", 13)

    def run(self) -> None:
        entries = db.get_leaderboard()     # list of (username, score, level, date)
        W, H    = self.screen.get_size()
        # column x positions: rank, username, score, level, date
        cols_x  = [18, 58, 220, 340, 450]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.back.is_clicked(event):
                    return

            draw_bg(self.screen)
            draw_text(self.screen, "Leaderboard", 30, ACCENT, W // 2, 42, bold=True)

            # header row
            for x, h in zip(cols_x, ["#", "Username", "Score", "Level", "Date"]):
                s = self._hfont.render(h, True, ACCENT)
                self.screen.blit(s, (x, 82))
            pygame.draw.line(self.screen, BTN_BORDER, (10, 100), (W - 10, 100), 1)

            if entries:
                for rank, row in enumerate(entries[:10], 1):
                    username, score, level, date = row
                    y   = 105 + (rank - 1) * 32
                    bg  = PANEL_COLOR if rank % 2 == 0 else BG_COLOR
                    pygame.draw.rect(self.screen, bg,
                                     (10, y, W - 20, 30), border_radius=4)
                    col = (255, 220, 40) if rank == 1 else TEXT_COLOR
                    vals = [str(rank), str(username)[:16],
                            str(score), str(level), str(date)]
                    for x, v in zip(cols_x, vals):
                        s = self._rfont.render(v, True, col)
                        self.screen.blit(s, (x, y + 7))
            else:
                draw_text(self.screen, "No scores yet — go play!", 18,
                          (140, 150, 180), W // 2, 260)
                draw_text(self.screen, "(Database may be offline)", 14,
                          (100, 110, 140), W // 2, 292)

            self.back.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Settings Screen
# ══════════════════════════════════════════════════════════════════════════════

class SettingsScreen:
    """
    Three clickable rows:
        Grid overlay  – on / off
        Sound         – on / off
        Snake colour  – cycle through SNAKE_COLOR_PRESETS
    Saves settings.json on exit.
    run() returns the (possibly updated) settings dict.
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 settings: dict) -> None:
        self.screen   = screen
        self.clock    = clock
        self.settings = dict(settings)       # work on a copy
        W, H = screen.get_size()
        self.save_btn  = Button(W // 2, H - 52, 220, 46, "Save & Back")
        self._lbl_font = pygame.font.SysFont("Verdana", 17, bold=True)
        self._val_font = pygame.font.SysFont("Verdana", 17)

        self._rows = [
            {"label": "Grid overlay", "key": "grid",       "type": "bool"},
            {"label": "Sound",        "key": "sound",      "type": "bool"},
            {"label": "Snake colour", "key": "snake_color","type": "color"},
        ]
        self._rects = [
            pygame.Rect(W // 2 - 175, 165 + i * 86, 350, 56)
            for i in range(len(self._rows))
        ]

    def run(self) -> dict:
        W, H = self.screen.get_size()
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(self._rects):
                        if rect.collidepoint(event.pos):
                            row = self._rows[i]
                            if row["type"] == "bool":
                                self.settings[row["key"]] = \
                                    not self.settings[row["key"]]
                            elif row["type"] == "color":
                                # cycle to next preset colour
                                cur = self.settings["snake_color"]
                                presets = config.SNAKE_COLOR_PRESETS
                                try:
                                    idx = presets.index(cur)
                                except ValueError:
                                    idx = 0
                                self.settings["snake_color"] = \
                                    presets[(idx + 1) % len(presets)]

                if self.save_btn.is_clicked(event):
                    save_settings(self.settings)
                    return self.settings

            draw_bg(self.screen)
            draw_text(self.screen, "Settings", 32, ACCENT, W // 2, 82, bold=True)
            draw_text(self.screen, "Click a row to toggle / cycle",
                      14, (140, 150, 180), W // 2, 126)

            for i, row in enumerate(self._rows):
                rect = self._rects[i]
                hov  = rect.collidepoint(mouse)
                pygame.draw.rect(self.screen,
                                 BTN_HOVER if hov else PANEL_COLOR,
                                 rect, border_radius=7)
                pygame.draw.rect(self.screen, BTN_BORDER, rect, 1, border_radius=7)

                lbl = self._lbl_font.render(row["label"], True, TEXT_COLOR)
                self.screen.blit(lbl, (rect.x + 14,
                                       rect.centery - lbl.get_height() // 2))

                val = self.settings[row["key"]]
                if row["type"] == "bool":
                    val_str = "ON"  if val else "OFF"
                    val_col = SUCCESS if val else DANGER
                    vs = self._val_font.render(val_str, True, val_col)
                    self.screen.blit(vs, (rect.right - vs.get_width() - 14,
                                          rect.centery - vs.get_height() // 2))
                elif row["type"] == "color":
                    # draw a colour swatch on the right side of the row
                    sw = pygame.Rect(rect.right - 46, rect.centery - 13, 34, 26)
                    pygame.draw.rect(self.screen, tuple(val), sw, border_radius=5)
                    pygame.draw.rect(self.screen, (200, 200, 200), sw, 1, border_radius=5)

            self.save_btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass    # audio device absent — game still runs

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Snake – Advanced Edition")
    clock  = pygame.time.Clock()

    # initialise the database (graceful no-op if PostgreSQL is offline)
    if not db.init_db():
        print("[main] PostgreSQL unavailable — leaderboard disabled for this session.")

    settings  = load_settings()   # load from settings.json (or defaults)
    username  = "Player"
    player_id = None

    while True:
        choice = MainMenuScreen(screen, clock).run()

        # ── navigation ────────────────────────────────────────────────────────
        if choice == "leaderboard":
            LeaderboardScreen(screen, clock).run()
            continue

        if choice == "settings":
            settings = SettingsScreen(screen, clock, settings).run()
            continue

        if choice == "quit":
            pygame.quit()
            sys.exit()

        if isinstance(choice, tuple) and choice[0] == "play":
            username  = choice[1]
            player_id = db.get_or_create_player(username)

        # ── inner retry loop ──────────────────────────────────────────────────
        while True:
            personal_best = db.get_personal_best(username)

            # run one game session
            result = GameScreen(screen, clock, settings, personal_best).run()

            # persist the result (no-op if DB offline)
            db.save_session(player_id, result["score"], result["level"])

            # update personal best for the game-over screen
            new_best = max(personal_best, result["score"])

            outcome = GameOverScreen(screen, clock, result, new_best).run()
            if outcome != "retry":
                break           # back to main menu


if __name__ == "__main__":
    main()
