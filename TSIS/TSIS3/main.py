"""
main.py
Entry point for Racer – Arcade Edition.

Top-level loop:
  Main Menu
    ├── Play → Username Entry → Game loop → Game Over → (retry or back)
    ├── Leaderboard screen
    ├── Settings screen  (saves to settings.json)
    └── Quit

Run from the TSIS3/ directory:
    python main.py
"""
import pygame
import sys

from persistence import load_settings
from ui import (MainMenuScreen, UsernameScreen, SettingsScreen,
                LeaderboardScreen, GameOverScreen)
from racer import Game

SW, SH = 400, 600


def main() -> None:
    pygame.init()

    # initialise audio; continue silently if no audio device is available
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Racer – Arcade Edition")
    clock = pygame.time.Clock()

    # load persisted settings (falls back to defaults if file is missing)
    settings = load_settings()
    username = "Player"

    # ── top-level navigation loop ──────────────────────────────────────────────
    while True:
        choice = MainMenuScreen(screen, clock).run()

        if choice == "play":
            # ask for player name once per play session
            username = UsernameScreen(screen, clock).run()

            # inner retry loop – keeps the same username until they go to menu
            while True:
                result  = Game(screen, clock, settings, username).run()
                outcome = GameOverScreen(screen, clock, result, username).run()
                if outcome != "retry":
                    break    # back to main menu

        elif choice == "leaderboard":
            LeaderboardScreen(screen, clock).run()

        elif choice == "settings":
            # SettingsScreen returns the (possibly updated) settings dict
            # and has already saved it to settings.json
            settings = SettingsScreen(screen, clock, settings).run()

        elif choice == "quit":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
