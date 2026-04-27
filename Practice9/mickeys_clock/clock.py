import pygame
import sys
import datetime

class Clock:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("Mickey Clock")

        self.bg_image = pygame.image.load("images/background.PNG")
        self.minute_hand_image = pygame.image.load("images/minute.PNG")
        self.second_hand_image = pygame.image.load("images/second.PNG")

        self.center = (250, 250)

        self.clock = pygame.time.Clock()

    def rotate(self, image, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        rect = rotated_image.get_rect(center=self.center)
        return rotated_image, rect

    def get_time_angles(self):
        now = datetime.datetime.now()

        minute = now.minute
        second = now.second

        minute_angle = -minute * 6
        second_angle = -second * 6

        return minute_angle, second_angle

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.bg_image, (0, 0))

            minute_angle, second_angle = self.get_time_angles()

            rotated_minute_hand_image, min_rect = self.rotate(self.minute_hand_image, minute_angle)
            rotated_second_hand_image, sec_rect = self.rotate(self.second_hand_image, second_angle) 

            self.screen.blit(rotated_minute_hand_image, min_rect)
            self.screen.blit(rotated_second_hand_image, sec_rect)

            pygame.display.flip()
            self.clock.tick(60)