import pygame
import sqlite3
import sys

def create_new_window(login, level_list, create_level_window, draw_multiline_text, create_special_window):
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Выбор уровня")
    background_window2 = pygame.image.load('data/фон.jpg')
    prof = pygame.image.load('data/иконка профиля черная.png')
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)
    num_rectangles = 5  # количество рамочек
    rect_width, rect_height = 720, 125  # размеры рамочек
    start_y, spacing = 50, 12  # начальная позиция и промежуток между рамками
    conn = sqlite3.connect('data/project_play_bd.db')
    cur = conn.cursor()
    cur.execute('SELECT description FROM levels')
    rows = cur.fetchall()
    long_text = [i[0] for i in rows]

    button_image = pygame.image.load('data/кнопка.png')
    button_image = pygame.transform.scale(button_image, (200, 100))

    font = pygame.font.Font(None, 36)
    # заносим прогресс прохождения уровней в список
    list_level_text = []
    for i in level_list:
        if i == 0:
            list_level_text.append(font.render('Не выполнено', True, (0, 0, 0)))
        elif i == 1:
            list_level_text.append(font.render('Выполнено', True, (0, 0, 0)))

    list_button_rect = [pygame.Rect(500, 60, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 200, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 340, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 475, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 615, button_image.get_width(), button_image.get_height())]
    prof_btn = pygame.Rect(690, 5, prof.get_width(), prof.get_height())
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if list_button_rect[0].collidepoint(event.pos):
                    level = 'level1.txt'
                    create_level_window('level1.txt', 'level1', level)
                elif list_button_rect[1].collidepoint(event.pos):
                    level = 'level2.txt'
                    create_level_window('level2.txt', 'level2', level)
                elif list_button_rect[2].collidepoint(event.pos):
                    level = 'level3.txt'
                    create_level_window('level3.txt', 'level3', level)
                elif list_button_rect[3].collidepoint(event.pos):
                    level = 'level4.txt'
                    create_level_window('level4.txt', 'level4', level)
                elif list_button_rect[4].collidepoint(event.pos):
                    level = 'level5.txt'
                    create_level_window('level5.txt', 'level5', level)
                elif prof_btn.collidepoint(event.pos):
                    create_special_window(login, level_list, create_level_window, draw_multiline_text,
                                          create_new_window)
        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.blit(background_window2, (0, 0))
        draw_multiline_text('Прежде чем отправиться в путь выбери задание', 20, 5, font,
                            (0, 0, 0))
        new_screen.blit(prof, (690, 5))
        coord = []
        for i in range(num_rectangles):
            # Вычисляем позицию рамки
            x = (750 - rect_width) // 2  # Центруем по горизонтали
            y = start_y + i * (rect_height + spacing)

            # Рисуем рамку
            pygame.draw.rect(new_screen, '#38130cff', (x, y, rect_width, rect_height), 2)
            coord.append((x + 5, y + 3))
        for i in range(len(coord)):
            draw_multiline_text(long_text[i], coord[i][0], coord[i][1], font, (0, 0, 0))

        for i in range(5):
            new_screen.blit(button_image, list_button_rect[i].topleft)
            new_screen.blit(list_level_text[i],
                            (list_button_rect[i].x + (button_image.get_width() - list_level_text[i].get_width()) // 2,
                             list_button_rect[i].y + (
                                     button_image.get_height() - list_level_text[i].get_height()) // 2))
        new_screen.blit(cursor, cursor_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()