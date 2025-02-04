import pygame
import sys
import sqlite3

def create_special_window(login, level_list, create_level_window, draw_multiline_text, create_new_window):
    special_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Специальное окно")
    background_special = pygame.image.load('data/фон.jpg')
    cursor_image = pygame.image.load('data/cursor.png')
    cursor_rect = cursor_image.get_rect()
    pygame.mouse.set_visible(False)

    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 48)

    level_texts = []
    score = 0

    conn = sqlite3.connect('data/project_play_bd.db')
    cur = conn.cursor()
    cur.execute('SELECT score FROM players WHERE player = ?', (login,))
    row = cur.fetchone()
    if row:
        score = row[0]

    score_image = pygame.image.load('data/score_image.png')

    for i, status in enumerate(level_list, 1):
        if i <= 5:
            status_text = 'Пройден' if status == 1 else 'Не пройден'
            level_texts.append(f'Уровень {i}: {status_text}')

    # Загрузка изображения кнопки и уменьшение её размера
    button_image = pygame.image.load('data/button_start.png')
    button_image = pygame.transform.scale(button_image, (200, 60))  # Уменьшение кнопки
    button_rect = button_image.get_rect(topleft=(275, 650))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    create_new_window(login, level_list, create_level_window, draw_multiline_text, create_special_window)

        cursor_rect.topleft = pygame.mouse.get_pos()
        special_screen.blit(background_special, (0, 0))

        text_surface = font.render(f'Имя пользователя: {login}', True, (0, 0, 0))
        special_screen.blit(text_surface, (50, 20))

        y_offset = 70
        for line in level_texts:
            text_surface = font.render(line, True, (0, 0, 0))
            special_screen.blit(text_surface, (50, y_offset))
            y_offset += text_surface.get_height() + 10

        special_screen.blit(score_image, (50, y_offset))
        text_surface = large_font.render(f': {score}', True, (0, 0, 0))
        special_screen.blit(text_surface, (50 + score_image.get_width() + 10, y_offset + 5))
        y_offset += score_image.get_height() + 10

        # Отображение уменьшенной кнопки "Начать игру"
        special_screen.blit(button_image, button_rect.topleft)
        button_text = font.render("Начать игру", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        special_screen.blit(button_text, button_text_rect.topleft)

        special_screen.blit(cursor_image, cursor_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()