import pygame
import sys
from pygame.locals import *
import random
import time

pygame.init()

FPS = 30
FramePerSec = pygame.time.Clock()

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED   = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE  = pygame.Color(0, 0, 255)
GOLD  = pygame.Color(255, 215, 0)

SCREEN_WIDTH  = 720
SCREEN_HEIGHT = 480
SPEED = 5
SCORE = 0

GROW_AMOUNT = 5   

font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(BLACK)
pygame.display.set_caption("Game")

snake_position = [100, 50]
snake_body = [
    [100, 50],
    [90,  50],
    [80,  50],
    [70,  50],
]

grow_pending = 0

fruit_position  = [random.randrange(0, SCREEN_WIDTH  // 10) * 10,
                   random.randrange(0, SCREEN_HEIGHT // 10) * 10]
is_fruit_exists = False

def spawn_a_fruit():
    global fruit_position, is_fruit_exists

    def generate_random_coordinate():
        coord = [random.randrange(0, SCREEN_WIDTH  // 10) * 10,
                 random.randrange(0, SCREEN_HEIGHT // 10) * 10]
        for block in snake_body:
            if block[0] == coord[0] and block[1] == coord[1]:
                return generate_random_coordinate()
        return coord

    fruit_position  = generate_random_coordinate()
    is_fruit_exists = True

spawn_a_fruit()

DIRECTION = 'RIGHT'
CHANGE_TO  = DIRECTION

def show_score(color, size):
    surf = font_small.render('Score : ' + str(SCORE), True, color)
    DISPLAYSURF.blit(surf, surf.get_rect())

def game_over():
    surf = font.render("Game Over", True, BLACK)
    rect = surf.get_rect()
    rect.midtop = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    DISPLAYSURF.blit(surf, rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:    CHANGE_TO = "UP"
            if event.key == pygame.K_DOWN:  CHANGE_TO = "DOWN"
            if event.key == pygame.K_RIGHT: CHANGE_TO = "RIGHT"
            if event.key == pygame.K_LEFT:  CHANGE_TO = "LEFT"

    if CHANGE_TO == 'UP'    and DIRECTION != 'DOWN':  DIRECTION = 'UP'
    if CHANGE_TO == 'DOWN'  and DIRECTION != 'UP':    DIRECTION = 'DOWN'
    if CHANGE_TO == 'RIGHT' and DIRECTION != 'LEFT':  DIRECTION = 'RIGHT'
    if CHANGE_TO == 'LEFT'  and DIRECTION != 'RIGHT': DIRECTION = 'LEFT'

    if DIRECTION == 'UP':    snake_position[1] -= 10
    if DIRECTION == 'DOWN':  snake_position[1] += 10
    if DIRECTION == 'LEFT':  snake_position[0] -= 10
    if DIRECTION == 'RIGHT': snake_position[0] += 10

    snake_body.insert(0, list(snake_position))

    if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
        SCORE          += 10
        is_fruit_exists = False
        grow_pending   += GROW_AMOUNT  

    if grow_pending > 0:
        grow_pending -= 1   
    else:
        snake_body.pop()    

    if not is_fruit_exists:
        spawn_a_fruit()

    DISPLAYSURF.fill(BLACK)

    for pos in snake_body:
        pygame.draw.rect(DISPLAYSURF, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(DISPLAYSURF, WHITE,
                     pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

    if snake_position[0] < 0 or snake_position[0] > SCREEN_WIDTH  - 10: game_over()
    if snake_position[1] < 0 or snake_position[1] > SCREEN_HEIGHT - 10: game_over()

    for block in snake_body[1:]:
        if snake_position[0] == block[0] and snake_position[1] == block[1]:
            game_over()

    show_score(WHITE, 20)
    pygame.display.update()
    FramePerSec.tick(FPS)