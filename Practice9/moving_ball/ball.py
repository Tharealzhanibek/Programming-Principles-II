import pygame

class Ball:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((500, 500))

        self.x = 250
        self.y = 250

        self.clock = pygame.time.Clock()


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit() 
                
            
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_UP] and self.y >= 45: self.y -= 20
            if pressed[pygame.K_DOWN] and self.y <= 455: self.y += 20
            if pressed[pygame.K_LEFT] and self.x >= 45: self.x -= 20
            if pressed[pygame.K_RIGHT] and self.x <= 455: self.x += 20
        
            self.screen.fill((255, 255, 255))
            pygame.draw.circle(self.screen, (200, 0, 0), (self.x, self.y), 25)

            pygame.display.flip()
            self.clock.tick(60)