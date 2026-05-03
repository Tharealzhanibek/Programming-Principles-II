"""
ui.py
All non-gameplay Pygame screens.
Each class has a run() method that blocks until the player makes a choice,
then returns a result value (string or updated dict depending on screen).

Screens:
  MainMenuScreen    → returns "play" | "leaderboard" | "settings" | "quit"
  UsernameScreen    → returns the entered name (str)
  SettingsScreen    → returns the updated settings dict
  LeaderboardScreen → returns None (just displays then goes back)
  GameOverScreen    → returns "retry" | "menu"
"""
import pygame
import sys
from persistence import load_leaderboard, save_settings

# ── colour palette ─────────────────────────────────────────────────────────────
BG_COLOR    = (15,  20,  35)
PANEL_COLOR = (30,  38,  60)
BTN_COLOR   = (55,  80,  160)
BTN_HOVER   = (80,  110, 210)
BTN_BORDER  = (100, 140, 255)
TEXT_COLOR  = (230, 235, 255)
ACCENT      = (100, 200, 255)
DANGER      = (255, 80,  80)
SUCCESS     = (80,  220, 120)

# Car colour swatches used in the settings preview
CAR_COLOR_MAP = {
    "blue":   (40,  140, 255),
    "red":    (255, 60,  60),
    "green":  (60,  220, 80),
    "yellow": (255, 220, 40),
}


# ── shared helpers ─────────────────────────────────────────────────────────────

def draw_bg(surface: pygame.Surface) -> None:
    """Fill the screen with the standard dark background."""
    surface.fill(BG_COLOR)


def draw_text(surface: pygame.Surface, text: str, size: int, color,
              cx: int, cy: int, bold: bool = False) -> int:
    """Render text centred at (cx, cy). Returns the rendered surface height."""
    font = pygame.font.SysFont("Verdana", size, bold=bold)
    surf = font.render(text, True, color)
    surface.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))
    return surf.get_height()


# ── Button ─────────────────────────────────────────────────────────────────────

class Button:
    """
    Clickable rectangle with hover highlight.
    Centred at (cx, cy) with explicit width and height.
    """

    def __init__(self, cx: int, cy: int, w: int, h: int,
                 label: str, font_size: int = 20):
        self.rect        = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.label       = label
        self._font       = pygame.font.SysFont("Verdana", font_size, bold=True)

    def draw(self, surface: pygame.Surface) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        bg      = BTN_HOVER if hovered else BTN_COLOR
        pygame.draw.rect(surface, bg,         self.rect, border_radius=8)
        pygame.draw.rect(surface, BTN_BORDER, self.rect, 2, border_radius=8)
        lbl = self._font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()  // 2,
                           self.rect.centery - lbl.get_height() // 2))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ══════════════════════════════════════════════════════════════════════════════
# Main Menu
# ══════════════════════════════════════════════════════════════════════════════

class MainMenuScreen:
    """Four buttons: Play, Leaderboard, Settings, Quit."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock  = clock
        W = screen.get_width()

        # build buttons centred horizontally
        self.buttons = {
            "play":        Button(W // 2, 260, 230, 50, "   Play"),
            "leaderboard": Button(W // 2, 325, 230, 50, "   Leaderboard"),
            "settings":    Button(W // 2, 390, 230, 50, "   Settings"),
            "quit":        Button(W // 2, 455, 230, 50, "   Quit"),
        }

    def run(self) -> str:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                for key, btn in self.buttons.items():
                    if btn.is_clicked(event):
                        return key

            draw_bg(self.screen)
            draw_text(self.screen, "RACER",          62, ACCENT,      200, 110, bold=True)
            draw_text(self.screen, "Arcade Edition", 20, TEXT_COLOR,  200, 168)
            for btn in self.buttons.values():
                btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Username Entry
# ══════════════════════════════════════════════════════════════════════════════

class UsernameScreen:
    """Text-input screen that asks the player for their name before the race."""

    MAX_LEN = 16

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen  = screen
        self.clock   = clock
        self.name    = ""
        W = screen.get_width()
        self.confirm = Button(W // 2, 390, 210, 48, "Start Racing")
        self._font   = pygame.font.SysFont("Verdana", 26, bold=True)
        self._hint   = pygame.font.SysFont("Verdana", 14)

    def run(self) -> str:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.name.strip():
                        return self.name.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif len(self.name) < self.MAX_LEN and event.unicode.isprintable():
                        self.name += event.unicode

                if self.confirm.is_clicked(event) and self.name.strip():
                    return self.name.strip()

            draw_bg(self.screen)
            draw_text(self.screen, "Enter Your Name", 30, ACCENT, 200, 130, bold=True)

            # text input box
            box = pygame.Rect(60, 225, 280, 52)
            pygame.draw.rect(self.screen, PANEL_COLOR, box, border_radius=8)
            pygame.draw.rect(self.screen, BTN_BORDER,  box, 2,  border_radius=8)
            name_surf = self._font.render(self.name + "|", True, TEXT_COLOR)
            self.screen.blit(name_surf, (box.x + 12, box.y + 10))

            hint = self._hint.render("Type name, then press Enter or click below",
                                     True, (140, 150, 180))
            self.screen.blit(hint, (200 - hint.get_width() // 2, 292))

            self.confirm.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Settings Screen
# ══════════════════════════════════════════════════════════════════════════════

class SettingsScreen:
    """
    Three toggleable rows:
      Sound      – on / off
      Car Colour – blue / red / green / yellow
      Difficulty – easy / normal / hard
    Changes are written to settings.json when the player clicks Back.
    """

    DIFFICULTIES = ["easy", "normal", "hard"]
    COLORS       = ["blue", "red", "green", "yellow"]

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 settings: dict):
        self.screen   = screen
        self.clock    = clock
        self.settings = dict(settings)          # copy so caller's dict is untouched
        W = screen.get_width()
        self.back = Button(W // 2, 530, 210, 46, "Back & Save")

        # row definitions: label shown, settings key, type
        self._rows = [
            {"label": "Sound",      "key": "sound",      "type": "bool"},
            {"label": "Car Colour", "key": "car_color",  "type": "cycle",
             "opts": self.COLORS},
            {"label": "Difficulty", "key": "difficulty", "type": "cycle",
             "opts": self.DIFFICULTIES},
        ]
        # clickable rects for each row
        self._rects = [pygame.Rect(50, 210 + i * 86, 300, 56)
                       for i in range(len(self._rows))]

        self._lbl_font = pygame.font.SysFont("Verdana", 18, bold=True)
        self._val_font = pygame.font.SysFont("Verdana", 18)

    def _cycle(self, key: str, options: list) -> None:
        idx = options.index(self.settings[key])
        self.settings[key] = options[(idx + 1) % len(options)]

    def run(self) -> dict:
        W = self.screen.get_width()
        while True:
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # check row clicks
                    for i, rect in enumerate(self._rects):
                        if rect.collidepoint(event.pos):
                            row = self._rows[i]
                            if row["type"] == "bool":
                                self.settings[row["key"]] = not self.settings[row["key"]]
                            else:
                                self._cycle(row["key"], row["opts"])

                if self.back.is_clicked(event):
                    save_settings(self.settings)
                    return self.settings

            draw_bg(self.screen)
            draw_text(self.screen, "Settings", 34, ACCENT, W // 2, 110, bold=True)
            draw_text(self.screen, "Click a row to change its value", 14,
                      (140, 150, 180), W // 2, 158)

            for i, row in enumerate(self._rows):
                rect    = self._rects[i]
                hovered = rect.collidepoint(mouse)
                pygame.draw.rect(self.screen,
                                 BTN_HOVER if hovered else PANEL_COLOR,
                                 rect, border_radius=8)
                pygame.draw.rect(self.screen, BTN_BORDER, rect, 1, border_radius=8)

                # left: label
                lbl = self._lbl_font.render(row["label"], True, TEXT_COLOR)
                self.screen.blit(lbl, (rect.x + 14,
                                       rect.centery - lbl.get_height() // 2))

                # right: current value + optional colour swatch
                val = self.settings[row["key"]]
                if row["type"] == "bool":
                    val_str = "ON"  if val else "OFF"
                    val_col = SUCCESS if val else DANGER
                else:
                    val_str = str(val).capitalize()
                    val_col = ACCENT

                val_surf = self._val_font.render(val_str, True, val_col)
                self.screen.blit(val_surf,
                                 (rect.right - val_surf.get_width() - (54 if row["key"] == "car_color" else 14),
                                  rect.centery - val_surf.get_height() // 2))

                # small colour swatch for car_color row
                if row["key"] == "car_color":
                    sw = pygame.Rect(rect.right - 34, rect.centery - 11, 22, 22)
                    pygame.draw.rect(self.screen,
                                     CAR_COLOR_MAP.get(val, (200, 200, 200)),
                                     sw, border_radius=4)
                    pygame.draw.rect(self.screen, (200, 200, 200), sw, 1, border_radius=4)

            self.back.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Leaderboard Screen
# ══════════════════════════════════════════════════════════════════════════════

class LeaderboardScreen:
    """Displays the saved top-10 scores: rank, name, score, distance, coins."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen  = screen
        self.clock   = clock
        self.back    = Button(screen.get_width() // 2, 562, 190, 44, "Back")
        self.entries = load_leaderboard()
        self._hfont  = pygame.font.SysFont("Verdana", 13, bold=True)
        self._rfont  = pygame.font.SysFont("Verdana", 13)

    def run(self) -> None:
        W = self.screen.get_width()
        # column x-positions: rank, name, score, dist, coins
        cols = [28, 72, 200, 278, 346]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.back.is_clicked(event):
                    return

            draw_bg(self.screen)
            draw_text(self.screen, "Leaderboard", 32, ACCENT, W // 2, 52, bold=True)

            # header row
            for x, h in zip(cols, ["#", "Name", "Score", "Dist", "Coins"]):
                s = self._hfont.render(h, True, ACCENT)
                self.screen.blit(s, (x, 102))
            pygame.draw.line(self.screen, BTN_BORDER, (20, 122), (W - 20, 122), 1)

            if self.entries:
                for rank, entry in enumerate(self.entries[:10], 1):
                    y   = 128 + (rank - 1) * 34
                    # alternating row background
                    bg  = PANEL_COLOR if rank % 2 == 0 else BG_COLOR
                    pygame.draw.rect(self.screen, bg,
                                     (20, y, W - 40, 32), border_radius=4)

                    col = (255, 220, 40) if rank == 1 else TEXT_COLOR   # gold for 1st
                    vals = [
                        str(rank),
                        entry.get("name", "?")[:13],
                        str(entry.get("score", 0)),
                        f"{entry.get('distance', 0)}m",
                        str(entry.get("coins", 0)),
                    ]
                    for x, v in zip(cols, vals):
                        s = self._rfont.render(v, True, col)
                        self.screen.blit(s, (x, y + 7))
            else:
                draw_text(self.screen, "No scores yet — go race!", 18,
                          (140, 150, 180), W // 2, 300)

            self.back.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Game Over Screen
# ══════════════════════════════════════════════════════════════════════════════

class GameOverScreen:
    """
    Shows run stats (score, distance, coins, bonus) and offers
    Retry / Main Menu.  Returns "retry" or "menu".
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 result: dict, username: str):
        self.screen   = screen
        self.clock    = clock
        self.result   = result
        self.username = username
        W = screen.get_width()
        self.retry = Button(W // 2 - 108, 478, 190, 48, "Retry")
        self.menu  = Button(W // 2 + 108, 478, 190, 48, "Main Menu")

    def run(self) -> str:
        W = self.screen.get_width()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.retry.is_clicked(event):
                    return "retry"
                if self.menu.is_clicked(event):
                    return "menu"

            draw_bg(self.screen)
            draw_text(self.screen, "GAME OVER", 50, DANGER,     W // 2, 108, bold=True)
            draw_text(self.screen, f"Driver: {self.username}", 20,
                      TEXT_COLOR, W // 2, 170)

            # stats panel
            panel = pygame.Rect(48, 200, 304, 248)
            pygame.draw.rect(self.screen, PANEL_COLOR, panel, border_radius=10)
            pygame.draw.rect(self.screen, BTN_BORDER,  panel, 1,  border_radius=10)

            stats = [
                ("Final Score",    str(self.result.get("score",    0)), ACCENT),
                ("Distance",  f"{self.result.get('distance', 0)} m",    TEXT_COLOR),
                ("Coins Collected", str(self.result.get("coins",   0)), (255, 220, 40)),
                ("Power-up Bonus", f"+{self.result.get('bonus',    0)}", SUCCESS),
            ]
            for i, (lbl, val, col) in enumerate(stats):
                y = 218 + i * 52
                draw_text(self.screen, lbl, 15, (160, 170, 210), W // 2 - 52, y)
                draw_text(self.screen, val, 22, col,             W // 2 + 68, y, bold=True)

            self.retry.draw(self.screen)
            self.menu.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
