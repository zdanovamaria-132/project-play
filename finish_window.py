import pygame
import sys


def finish_window(text, draw_multiline_text, login, level_list, create_level_window, create_new_window,
                  create_special_window):
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Результат уровня")
    background_window = None
    text_result = ''
    color = None
    prof = pygame.image.load('data/иконка профиля белая.png')
    if text == 'win':
        text_result = ('''
          Поздравляем, вы успешно 
            справились с заданием.
         Гильдия зачтет вам это задание.
        Пожалуйста хорошо отдохните и 
                восстановите силы.
        А затем приходите за новым 
                    заданием.''')
        background_window = pygame.image.load('data/win.jpg')
        color = (0, 0, 0)
    elif text == 'loss_m':
        background_window = pygame.image.load('data/lose_background.jpeg')  # Используем правильное имя файла
        text_result = ('''
        К сожалению, 
        вы не справились с заданием.
        Вы попали на монстра и 
        ваших сил не хватило победить его. 
        К счастью, вы успели воспользоваться 
        свитком перемещения и 
        укрыться в безопасном месте.''')
        color = (255, 255, 255)
    elif text == 'loss_l':
        background_window = pygame.image.load('data/lose_background.jpeg')  # Используем правильное имя файла
        text_result = ('''
            К сожалению, 
          вы не справились 
            с заданием.
          Вы попали в ловушку. 
          Вас спасли другие 
             члены гильдии. ''')
        color = (255, 255, 255)
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)

    button_image = pygame.image.load('data/кнопка_финиша.png')
    button_image = pygame.transform.scale(button_image, (200, 50))
    prof = pygame.transform.scale(prof, (50, 50))

    font = pygame.font.Font(None, 22)

    back_text = font.render('Вернуться к заданиям', True, (255, 255, 255))
    finish_text = font.render('Завершить игру', True, (255, 255, 255))

    back = pygame.Rect(500, 575, button_image.get_width(), button_image.get_height())
    finish = pygame.Rect(500, 675, button_image.get_width(), button_image.get_height())
    prof_btn = pygame.Rect(690, 5, prof.get_width(), prof.get_height())

    # Основной игровой цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Устанавливаем флаг, что окно закрылось
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    create_new_window(login, level_list, create_level_window, draw_multiline_text,
                                      create_special_window)
                elif finish.collidepoint(event.pos):
                    # Завершение Pygame
                    pygame.quit()
                    sys.exit()
                elif prof_btn.collidepoint(event.pos):
                    create_special_window(login, level_list, create_level_window, draw_multiline_text,
                                          create_new_window)
        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.blit(background_window, (0, 0))
        new_screen.blit(prof, (690, 5))

        # Отображение текста
        font = pygame.font.Font(None, 36)
        draw_multiline_text(text_result, 120, 200, font, color)
        new_screen.blit(button_image, back.topleft)
        new_screen.blit(button_image, finish.topleft)

        new_screen.blit(back_text, (back.x + (button_image.get_width() - back_text.get_width()) // 2,
                                    back.y + (button_image.get_height() - back_text.get_height()) // 2))
        new_screen.blit(finish_text, (finish.x + (button_image.get_width() - finish_text.get_width()) // 2,
                                      finish.y + (button_image.get_height() - finish_text.get_height()) // 2))
        new_screen.blit(cursor, cursor_rect)
        pygame.display.flip()
    pygame.quit()
    sys.exit()
