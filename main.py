import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((750, 750))

pygame.display.set_caption("Главное окно игры")

background = pygame.image.load('data/background.png')
background1 = pygame.image.load('data/background1.png')
background2 = pygame.image.load('data/background2.png')


cursor = pygame.image.load('data/cursor.png')
cursor_rect = cursor.get_rect()

pygame.mouse.set_visible(False)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    cursor_rect.topleft = pygame.mouse.get_pos()

    if (249 < cursor_rect.x < 319 and 510 < cursor_rect.y < 560 or
            178 < cursor_rect.x < 313 and 560 < cursor_rect.y < 615 or
            165 < cursor_rect.x < 460 and 615 < cursor_rect.y < 750):
        screen.blit(background1, (0, 0))
    elif (560 < cursor_rect.x < 605 and 305 < cursor_rect.y < 395 or
            552 < cursor_rect.x < 630 and 395 < cursor_rect.y < 485):
        screen.blit(background2, (0, 0))
    else:
        screen.blit(background, (0, 0))

    screen.blit(cursor, cursor_rect)

    pygame.display.flip()