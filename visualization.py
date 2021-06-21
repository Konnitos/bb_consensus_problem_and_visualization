import pygame
import os 

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)

FPS = 60

def draw_background():
    WIN.fill(WHITE)
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    draw_background()
    run = True

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


main()