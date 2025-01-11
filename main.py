import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((750, 750))
pygame.display.set_caption("Главное окно игры")

background_window1 = pygame.image.load('data/background_window1.png')
background1 = pygame.image.load('data/background1.png')
background2 = pygame.image.load('data/background2.png')

cursor = pygame.image.load('data/cursor.png')
cursor_rect = cursor.get_rect()

pygame.mouse.set_visible(False)


def create_new_window():
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Новое окно")
    background_window2 = pygame.image.load('data/background_window2.png')
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.blit(background_window2, (0, 0))
        new_screen.blit(cursor, cursor_rect)
        pygame.display.flip()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            if (249 < cursor_rect.x < 319 and 510 < cursor_rect.y < 560 or
                    178 < cursor_rect.x < 313 and 560 < cursor_rect.y < 615 or
                    165 < cursor_rect.x < 460 and 615 < cursor_rect.y < 750):
                create_new_window()

    cursor_rect.topleft = pygame.mouse.get_pos()

    if (249 < cursor_rect.x < 319 and 510 < cursor_rect.y < 560 or
            178 < cursor_rect.x < 313 and 560 < cursor_rect.y < 615 or
            165 < cursor_rect.x < 460 and 615 < cursor_rect.y < 750):
        screen.blit(background1, (0, 0))
    elif (560 < cursor_rect.x < 605 and 305 < cursor_rect.y < 395 or
          552 < cursor_rect.x < 630 and 395 < cursor_rect.y < 485):
        screen.blit(background2, (0, 0))
    else:
        screen.blit(background_window1, (0, 0))

    screen.blit(cursor, cursor_rect)
    pygame.display.flip()
