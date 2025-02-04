import pygame
import sys
import sqlite3

text_ability = ('''Способности:
1.Обнаружение ловушек: возможно 5 раз(клавиша t)
2.Увеличение скорости: возможно несколько секунд, 
                    самовостанавливается(клавиша SHIFT)
3.Телепорация: фиолетовый телепорт кнопка Q, синий Е''')

def create_special_window(login, level_list, create_level_window, draw_multiline_text, create_new_window):
    special_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Специальное окно")
    background_special = pygame.image.load('data/фон.jpg')
    cursor_image = pygame.image.load('data/cursor.png')
    avatar_image = pygame.image.load('data/аватарка.png')
    cursor_rect = cursor_image.get_rect()
    pygame.mouse.set_visible(False)

    font = pygame.font.Font(None, 36)
    font_gild = pygame.font.Font(None, 42)
    large_font = pygame.font.Font(None, 48)

    level_texts = []
    score = 0

    conn = sqlite3.connect('data/project_play_bd.db')
    cur = conn.cursor()
    cur.execute('SELECT score FROM players WHERE player = ?', (login,))
    row = cur.fetchone()

    if row:
        score = row[0]

    if score >= 700:
        text_rang = font.render('Ранг: A, мастер', True, (0, 0, 0))
    elif score >= 500:
        text_rang = font.render('Ранг: B, опытный', True, (0, 0, 0))
    elif score >= 200:
        text_rang = font.render('Ранг: C, продвинутый', True, (0, 0, 0))
    else:
        text_rang = font.render('Ранг: D, новичок', True, (0, 0, 0))


    score_image = pygame.image.load('data/score_image.png')

    for i, status in enumerate(level_list, 1):
        if i <= 5:
            status_text = 'Выполнено' if status == 1 else 'Не выполнено'
            level_texts.append(f'Задание {i}: {status_text}')

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
        special_screen.blit(avatar_image, (15, 55))
        pygame.draw.rect(special_screen, '#38130cff', (10, 45, 170, 170), 3)
        text_gild = font_gild.render('Гильдия хранителей леса', True, (0, 0, 0))
        text_surface = font.render(f'Имя пользователя: {login}', True, (0, 0, 0))
        text_flowers = font.render('Собрано: ', True, (0, 0, 0))

        special_screen.blit(text_gild, (190, 10))
        special_screen.blit(text_surface, (190, 85))
        special_screen.blit(text_rang, (210, 170))
        draw_multiline_text(text_ability, 10, 230, font, (0, 0, 0))

        y_offset = 400
        for line in level_texts:
            text_surface = font.render(line, True, (0, 0, 0))
            special_screen.blit(text_surface, (10, y_offset))
            y_offset += text_surface.get_height() + 15

        special_screen.blit(text_flowers, (10, y_offset))
        special_screen.blit(score_image, (50, y_offset + 40))
        text_surface = large_font.render(f': {score}', True, (0, 0, 0))

        special_screen.blit(text_surface, (50 + score_image.get_width() + 10, y_offset + 40))
        y_offset += score_image.get_height() + 10

        # Отображение уменьшенной кнопки "Начать игру"
        special_screen.blit(button_image, button_rect.topleft)
        button_text = font.render("Начать игру", True, (0, 0, 0))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        special_screen.blit(button_text, button_text_rect.topleft)

        special_screen.blit(cursor_image, cursor_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()