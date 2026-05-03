import pygame
import sys
from pygame.locals import *
import random
import time

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()


BLACK  = pygame.Color(0,   0,   0)
WHITE  = pygame.Color(255, 255, 255)
RED    = pygame.Color(255, 0,   0)
GREEN  = pygame.Color(0,   255, 0)
BLUE   = pygame.Color(0,   0,   255)
GOLD   = pygame.Color(255, 215, 0)
SILVER = pygame.Color(192, 192, 192)
BRONZE = pygame.Color(205, 127, 50)


SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED         = 5    
SCORE         = 0


SPEED_UP_EVERY = 5   

COIN_TYPES = [
    {"value": 1,  "color": BRONZE, "weight": 60, "label": "bronze"},  # common,   1 pt
    {"value": 3,  "color": SILVER, "weight": 30, "label": "silver"},  # uncommon, 3 pts
    {"value": 5,  "color": GOLD,   "weight": 10, "label": "gold"},    # rare,     5 pts
]


font        = pygame.font.SysFont("Verdana", 60)
font_small  = pygame.font.SysFont("Verdana", 20)
font_tiny   = pygame.font.SysFont("Verdana", 14)
game_over   = font.render("Game Over", True, BLACK)


background = pygame.image.load("images/AnimatedStreet.png")


DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(BLACK)
pygame.display.set_caption("Game")



class Enemy(pygame.sprite.Sprite):
    

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/Enemy.png")
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SPEED
    
        self.rect.move_ip(0, SPEED)

        
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.top = 0
            self.rect.center = (random.randint(30, 370), 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)



class Player(pygame.sprite.Sprite):
    

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/Player.png")
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ══════════════════════════════════════════════════════════════════════════════
class Coin(pygame.sprite.Sprite):
    

    def __init__(self):
        super().__init__()

        
        weights   = [ct["weight"] for ct in COIN_TYPES]
        coin_type = random.choices(COIN_TYPES, weights=weights, k=1)[0]

        self.value = coin_type["value"]    
        self.label = coin_type["label"]    

        
        base_image = pygame.image.load("images/Coin.png").convert_alpha()
        base_image = pygame.transform.scale(base_image, (50, 50))

        
        tint = pygame.Surface((50, 50), flags=pygame.SRCALPHA)
        tint.fill((*coin_type["color"][:3], 160))   # semi-transparent tint
        base_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = base_image

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

        
        self._label_surf = font_tiny.render(f"+{self.value}", True, WHITE)

    def move(self):
        
        self.rect.move_ip(0, 5)
        if self.rect.bottom > SCREEN_HEIGHT:
            self._respawn()

    def _respawn(self):
        
        self.rect.top = 0
        self.rect.center = (random.randint(30, 370), 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        surface.blit(self._label_surf,
                     (self.rect.centerx - self._label_surf.get_width() // 2,
                      self.rect.top - 16))

    def collect(self):
        
        self._respawn()
        return self.value


P1 = Player()
E1 = Enemy()
C  = Coin()           

enemies     = pygame.sprite.Group()
enemies.add(E1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, C)


INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


next_speed_threshold = SPEED_UP_EVERY   


while True:

    
    for event in pygame.event.get():

    
        if event.type == INC_SPEED:
            SPEED += 0.5

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    
    DISPLAYSURF.blit(background, (0, 0))

    
    scores = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    
    speed_text = font_tiny.render(f"speed {SPEED:.1f}", True, BLACK)
    DISPLAYSURF.blit(speed_text, (SCREEN_WIDTH - speed_text.get_width() - 10, 10))

    
    milestone_text = font_tiny.render(
        f"next boost at {next_speed_threshold} coins", True, BLACK)
    DISPLAYSURF.blit(milestone_text,
                     (SCREEN_WIDTH - milestone_text.get_width() - 10, 28))

    
    for entity in all_sprites:
        entity.move()
        entity.draw(DISPLAYSURF)

    
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('sounds/crash.wav').play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))

        
        final_score = font_small.render(f"Score: {SCORE}", True, BLACK)
        DISPLAYSURF.blit(final_score, (160, 330))

        pygame.display.update()
        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    
    if pygame.sprite.collide_rect(P1, C):
        pygame.mixer.Sound('sounds/coin_received.mp3').play()

        
        points_earned = C.collect()
        SCORE += points_earned

        
        if SCORE >= next_speed_threshold:
            SPEED += 1                              
            next_speed_threshold += SPEED_UP_EVERY  

    pygame.display.update()
    FramePerSec.tick(FPS)