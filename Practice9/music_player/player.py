import pygame
import sys

class Player:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() 

        self.font = pygame.font.Font(None, 25)

        self.playlist = ['music/One More Love Song.mp3', 'music/Erikpe.mp3', 'music/Askim cok pardon.mp3', 'music/Another One.mp3']
        self.current_track = 0
        pygame.mixer.music.set_volume(0.5)

        self.screen = pygame.display.set_mode((500, 500))

        self.song_length_seconds = 0

        self.clock = pygame.time.Clock()

    def play_song(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

        current_audio = pygame.mixer.Sound(path)
        self.song_length_seconds = current_audio.get_length()

    def play_next_song(self):
        self.current_track += 1

        if self.current_track >= len(self.playlist):
            self.current_track = 0
        
        self.play_song(self.playlist[self.current_track])

    def play_previous_song(self):
        self.current_track -= 1

        if self.current_track < 0:
            self.current_track = len(self.playlist) - 1

        self.play_song(self.playlist[self.current_track])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit() 

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.play_song(self.playlist[self.current_track])
                    if event.key == pygame.K_n:
                        self.play_next_song()
                    if event.key == pygame.K_b:
                        self.play_previous_song()
                    if event.key == pygame.K_q:
                        pygame.mixer.music.stop()
                        pygame.quit()
                        sys.exit()

            self.screen.fill((255, 255, 255))

            current_path = self.playlist[self.current_track]

            if current_path == 'music/One More Love Song.mp3':
                text_surface = self.font.render("One More Love Song - Mac DeMarco", True, (0, 0, 0))
                self.screen.blit(text_surface, (50, 200))

            if current_path == 'music/Erikpe.mp3':
                text_surface = self.font.render("Erikpe - Darkhan Juzz", True, (0, 0, 0))
                self.screen.blit(text_surface, (50, 200))

            if current_path == 'music/Askim cok pardon.mp3':
                text_surface = self.font.render("Askim cok pardon - No Name", True, (0, 0, 0))
                self.screen.blit(text_surface, (50, 200))

            if current_path == 'music/Another One.mp3':
                text_surface = self.font.render("Another one - Mac DeMarco", True, (0, 0, 0))
                self.screen.blit(text_surface, (50, 200))
            
            time_ms = pygame.mixer.music.get_pos()

            if time_ms > 0:
                total_seconds = time_ms // 1000
                minutes = total_seconds // 60
                seconds = total_seconds % 60
            else:
                minutes = 0
                seconds = 0

            timer_string = f"{minutes}:{seconds:02d}"

            timer_surface = self.font.render(timer_string, True, (100, 100, 100))
            timer_rect = timer_surface.get_rect(center=(250, 250))
            self.screen.blit(timer_surface, timer_rect)

            if self.song_length_seconds > 0:
                progress_ratio = total_seconds / self.song_length_seconds

                pygame.draw.rect(self.screen, (200, 200, 200), (100, 230, 300, 10))

                current_bar_width = 300 * progress_ratio
                pygame.draw.rect(self.screen, (50, 150, 250), (100, 230, current_bar_width, 10))

            pygame.display.flip()
            self.clock.tick(60) 