import pygame
import sys

# Инициализация Pygame
pygame.init()

# Установите размеры окна
screen = pygame.display.set_mode((1024, 1024))

# Установите заголовок окна
pygame.display.set_caption("Главное окно игры")

# Загрузите изображение фона из папки data
background = pygame.image.load('data/background.png')

# Основной цикл игры
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Отобразите изображение фона
    screen.blit(background, (0, 0))

    # Обновите экран
    pygame.display.flip()
