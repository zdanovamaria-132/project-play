import pygame
import sys
import os
import random
from PyQt6 import QtWidgets, uic
import sqlite3
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox

login = ""  # переменная для хранения имя пользователя
level_list = []  # для хранения прогресса уровня: 0 не пройден, 1 пройден
pygame.init()
level = ''
screen = None  # для экрана

background_window1 = pygame.image.load('data/background/background_window1.png')
background1 = pygame.image.load('data/background/background1.png')
background2 = pygame.image.load('data/background/background2.png')

cursor = pygame.image.load('data/cursor.png')
cursor_rect = cursor.get_rect()

pygame.mouse.set_visible(False)


def load_images_from_folder(folder):
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Папка '{folder}' не найдена.")
    images = {}
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            images[filename] = pygame.image.load(os.path.join(folder, filename))
    if not images:
        raise FileNotFoundError(f"Нет изображений в папке '{folder}'.")
    return images


tile_images = {
    'wall': load_images_from_folder('data/walls'),
    'empty': load_images_from_folder('data/empty'),
    'l': load_images_from_folder('data'),
    'teleport_e': load_images_from_folder('data/teleport_e'),
    'teleport_q': load_images_from_folder('data/teleport_q')
}

player_images = [
    pygame.image.load('data/player_walk1.png'),
    pygame.image.load('data/player_walk2.png'),
    pygame.image.load('data/player_walk3.png')
]

tile_width = tile_height = 50

# Определение групп спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()  # Группа для стен
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, image_file=None):
        super().__init__(tiles_group, all_sprites)
        if image_file:
            self.image = tile_images[tile_type][image_file]
        else:
            self.image = random.choice(list(tile_images[tile_type].values()))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.type = tile_type
        if tile_type == 'wall':
            walls_group.add(self)  # Добавляем в группу стен
        self.image_file = image_file  # Сохраняем имя файла изображения


# Загрузка изображения empty.png
empty_image = pygame.image.load('data/empty/empty.png')

# Загрузка изображений empty1.png, empty2.png и т.д.
empty_images = [pygame.image.load(f'data/empty/empty{i}.png') for i in range(1, 10)]
empty_replacement_image = pygame.image.load('data/empty/empty.png')


def load_sprite_sheet(sheet, frame_width, frame_height, num_frames, row):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    for x in range(num_frames):
        if x * frame_width < sheet_width and row * frame_height < sheet_height:
            frame = sheet.subsurface(pygame.Rect(x * frame_width, row * frame_height, frame_width, frame_height))
            frames.append(frame)
        else:
            raise ValueError("Subsurface rectangle outside surface area")
    return frames


# Загрузка спрайтового листа
sprite_sheet = pygame.image.load('data/sprite_sheet.png')

# Разделение на кадры для каждого направления
walk_down_frames = load_sprite_sheet(sprite_sheet, frame_width=50, frame_height=50, num_frames=6,
                                     row=0)  # Кадры для движения вниз
walk_left_frames = load_sprite_sheet(sprite_sheet, frame_width=50, frame_height=50, num_frames=6,
                                     row=1)  # Кадры для движения влево
walk_up_frames = load_sprite_sheet(sprite_sheet, frame_width=50, frame_height=50, num_frames=6,
                                   row=2)  # Кадры для движения вверх
walk_right_frames = load_sprite_sheet(sprite_sheet, frame_width=50, frame_height=50, num_frames=6,
                                      row=3)  # Кадры для движения вправо


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.walk_down_frames = walk_down_frames
        self.walk_left_frames = walk_left_frames
        self.walk_up_frames = walk_up_frames
        self.walk_right_frames = walk_right_frames
        self.image = self.walk_down_frames[0]  # Начальная позиция (смотрит вниз)
        self.rect = self.image.get_rect().move(tile_width * pos_x + tile_width // 2 - self.image.get_width() // 2,
                                               tile_height * pos_y + tile_height // 2 - self.image.get_height() // 2)
        self.frame = 0
        self.animation_speed = 0.1
        self.direction = 'down'
        self.move_delay = 30
        self.moving = False
        self.score = 0  # Добавляем атрибут score для учета очков
        print('создан персонаж')

    def update(self, message):
        keys = pygame.key.get_pressed()
        move_multiplier = 1

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            move_multiplier = 2

        if self.move_delay == 0:
            new_rect = self.rect.copy()
            step_size = tile_width
            c = load_level(level)
            a = c[new_rect.y // 50][new_rect.x // 50]
            self.moving = False

            if keys[pygame.K_q] and a == '1':
                coordinates_p = []
                for row_index, line in enumerate(c):
                    for col_index, char in enumerate(line):
                        if char == '2':
                            coordinates_p.append((row_index, col_index))
                new_rect.x, new_rect.y = coordinates_p[0][1] * 50, coordinates_p[0][0] * 50
            elif keys[pygame.K_e] and a == '2':
                coordinates_m = []
                for row_index, line in enumerate(c):
                    for col_index, char in enumerate(line):
                        if char == '1':
                            coordinates_m.append((row_index, col_index))
                new_rect.x, new_rect.y = coordinates_m[0][1] * 50, coordinates_m[0][0] * 50

            if message == 'up':
                step_size = -tile_height * move_multiplier
                for step in range(abs(step_size)):
                    new_rect.y += int(step_size / abs(step_size))
                    collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
                    if collision:
                        new_rect.y -= int(step_size / abs(step_size))
                        break
                self.direction = 'up'
                self.moving = True
                self.move_delay = 30
            elif message == 'down':
                step_size = tile_height * move_multiplier
                for step in range(abs(step_size)):
                    new_rect.y += int(step_size / abs(step_size))
                    collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
                    if collision:
                        new_rect.y -= int(step_size / abs(step_size))
                        break
                self.direction = 'down'
                self.moving = True
                self.move_delay = 30
            elif message == 'left':
                step_size = -tile_width * move_multiplier
                for step in range(abs(step_size)):
                    new_rect.x += int(step_size / abs(step_size))
                    collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
                    if collision:
                        new_rect.x -= int(step_size / abs(step_size))
                        break
                self.direction = 'left'
                self.moving = True
                self.move_delay = 30
            elif message == 'right':
                step_size = tile_width * move_multiplier
                for step in range(abs(step_size)):
                    new_rect.x += int(step_size / abs(step_size))
                    collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
                    if collision:
                        new_rect.x -= int(step_size / abs(step_size))
                        break
                self.direction = 'right'
                self.moving = True
                self.move_delay = 30

            if 0 <= new_rect.left and new_rect.right <= screen.get_width() and \
                    0 <= new_rect.top and new_rect.bottom <= screen.get_height():
                self.rect = new_rect

                for tile in tiles_group:
                    if self.rect.colliderect(tile.rect) and tile.image_file and tile.image_file.startswith(
                            'empty') and tile.image_file.endswith('.png'):
                        if tile.image != empty_replacement_image:
                            tile.image = empty_replacement_image
                            self.score += 1
                            conn = sqlite3.connect('data/project_play_bd.db')
                            cursor = conn.cursor()
                            cursor.execute('UPDATE players SET score = score + 1 WHERE player = ?', (login,))
                            conn.commit()
                            conn.close()

        if self.moving:
            self.frame += self.animation_speed
            if self.direction == 'up':
                if self.frame >= len(self.walk_up_frames):
                    self.frame = 0
                self.image = self.walk_up_frames[int(self.frame)]
            elif self.direction == 'down':
                if self.frame >= len(self.walk_down_frames):
                    self.frame = 0
                self.image = self.walk_down_frames[int(self.frame)]
            elif self.direction == 'left':
                if self.frame >= len(self.walk_left_frames):
                    self.frame = 0
                self.image = self.walk_left_frames[int(self.frame)]
            elif self.direction == 'right':
                if self.frame >= len(self.walk_right_frames):
                    self.frame = 0
                self.image = self.walk_right_frames[int(self.frame)]
        else:
            if self.direction == 'up':
                self.image = self.walk_up_frames[0]
            elif self.direction == 'down':
                self.image = self.walk_down_frames[0]
            elif self.direction == 'left':
                self.image = self.walk_left_frames[0]
            elif self.direction == 'right':
                self.image = self.walk_right_frames[0]

        if self.move_delay > 0:
            self.move_delay -= 1


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r', encoding='utf-8') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = pygame.image.load('data/monster.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.speed = 0.5
        print(f"Монстр создан на позиции ({pos_x}, {pos_y})")

    def update(self, player):
        new_rect = self.rect.copy()
        if abs(self.rect.x - player.rect.x) > abs(self.rect.y - player.rect.y):
            if self.rect.x < player.rect.x:
                new_rect.x += self.speed
            elif self.rect.x > player.rect.x:
                new_rect.x -= self.speed
        elif abs(self.rect.x - player.rect.x) < abs(self.rect.y - player.rect.y):
            if self.rect.y < player.rect.y:
                new_rect.y += self.speed
            elif self.rect.y > player.rect.y:
                new_rect.y -= self.speed
        else:
            if self.rect.x < player.rect.x:
                new_rect.x += self.speed
            elif self.rect.x > player.rect.x:
                new_rect.x -= self.speed
            if self.rect.y < player.rect.y:
                new_rect.y += self.speed
            elif self.rect.y > player.rect.y:
                new_rect.y -= self.speed

        # Проверка на столкновение со стенами
        collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
        if not collision:
            self.rect = new_rect


def generate_level(level):
    new_player, x, y = None, None, None
    teleport_points = {}
    win_point = None
    monster = None
    l_points = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                tile_file = f'empty{(x + y) % 10}.png'
                Tile('empty', x, y, tile_file)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'L':
                tile_file = f'empty{(x + y) % 10}.png'
                Tile('empty', x, y, tile_file)
                l_points.append((x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '1':
                Tile('teleport_e', x, y)
                teleport_points['1'] = (x, y)
            elif level[y][x] == '2':
                Tile('teleport_q', x, y)
                teleport_points['2'] = (x, y)
            elif level[y][x] == '%':
                Tile('empty', x, y)
                win_point = (x, y)
            elif level[y][x] == 'M':
                Tile('empty', x, y)
                monster = Monster(x, y)
                all_sprites.add(monster)  # Добавляем монстра в группу спрайтов
                print("Монстр добавлен в группу спрайтов")
    print(f"Монстр: {monster}")
    return new_player, teleport_points, win_point, monster, l_points


def create_level_window(map_level, level):
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Уровень")
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)
    start_time = None
    count_l = 0
    player, teleport_points, win_point, monster, l_point = generate_level(load_level(map_level))
    win_text = 'win'
    lose_text = "loss"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.update('up')
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    player.update('down')
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.update('right')
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.update('left')
                if event.key == pygame.K_t:
                    if count_l != 5:
                        start_time = pygame.time.get_ticks()
                        for i in l_point:
                            if ((i[0] * 50 >= player.rect.x - 200 and i[0] * 50 <= player.rect.x + 200)
                                    and (i[1] * 50 >= player.rect.y - 200 and i[1] * 50 <= player.rect.y + 200)):
                                Tile('l', i[0], i[1], 'emptyl.png')
                            else:
                                tile_file = f'empty{(i[0] + i[1]) % 10}.png'
                                Tile('empty', i[0], i[1], tile_file)
                        count_l += 1
                    else:
                        print('лимит исчерпан')

        if start_time is not None:
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time >= 3000:
                print('время вышло')
                # Здесь можно делать то, что нужно каждые 5 секунд
                for i in l_point:
                    tile_file = f'empty{(i[0] + i[1]) % 10}.png'
                    Tile('empty', i[0], i[1], tile_file)
                start_time = None  # Сбрасываем время, чтобы не выполнять заново

        player_group.update('')
        if monster:
            monster.update(player)

        # Логика победы
        if player.rect.colliderect(
                pygame.Rect(win_point[0] * tile_width, win_point[1] * tile_height, tile_width, tile_height)):
            if level_list[int(level[-1]) - 1] == 0:
                conn = sqlite3.connect('data/project_play_bd.db')
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE players
                    SET {level} = 1
                    WHERE player = '{login}'
                ''')
                conn.commit()
                conn.close()
            finih_window(win_text)

        # Логика проигрыша
        if monster and player.rect.colliderect(monster.rect):
            finih_window(lose_text)

        for i in l_point:
            if player.rect.colliderect(pygame.Rect(i[0] * tile_width, i[1] * tile_height, tile_width, tile_height)):
                finih_window(lose_text)

        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.fill((200, 200, 200))
        tiles_group.draw(new_screen)
        player_group.draw(new_screen)
        if monster:
            new_screen.blit(monster.image, monster.rect.topleft)
        new_screen.blit(cursor, cursor_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


def draw_multiline_text(text, x, y, font, color):
    # Делим текст на строки
    lines = text.splitlines()
    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x, y))
        y += text_surface.get_height()  # Смещаем Y координату вниз на высоту строки


def finih_window(text):
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Результат уровня")
    background_window = None
    text_result = ''
    color = None
    prof = None
    if text == 'win':
        text_result = ('Поздравляем, вы успешно завершили задание :)')
        background_window = pygame.image.load('data/win_photo.jpeg')
        prof = pygame.image.load('data/иконка профиля черная.png')
        color = (0, 0, 255)
    elif text == 'loss':
        background_window = pygame.image.load('data/lose_background.jpeg')  # Используем правильное имя файла
        text_result = ('К сожалению, вы не справились с заданием :(')
        prof = pygame.image.load('data/иконка профиля белая.png')
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
                    create_new_window()
                elif finish.collidepoint(event.pos):
                    # Завершение Pygame
                    pygame.quit()
                    sys.exit()
                elif prof_btn.collidepoint(event.pos):
                    create_special_window()
        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.blit(background_window, (0, 0))
        new_screen.blit(prof, (690, 5))

        # Отображение текста
        font = pygame.font.Font(None, 36)
        draw_multiline_text(text_result, 100, 750 // 2, font, color)
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


def create_new_window():
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
            list_level_text.append(font.render('Не пройден', True, (0, 0, 0)))
        elif i == 1:
            list_level_text.append(font.render('Пройден', True, (0, 0, 0)))

    list_button_rect = [pygame.Rect(500, 60, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 200, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 340, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 475, button_image.get_width(), button_image.get_height()),
                        pygame.Rect(500, 615, button_image.get_width(), button_image.get_height())]
    prof_btn = pygame.Rect(690, 5, prof.get_width(), prof.get_height())
    global level
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if list_button_rect[0].collidepoint(event.pos):
                    level = 'level1.txt'
                    create_level_window('level1.txt', 'level1')
                elif list_button_rect[1].collidepoint(event.pos):
                    level = 'level2.txt'
                    create_level_window('level2.txt', 'level2')
                elif list_button_rect[2].collidepoint(event.pos):
                    level = 'level3.txt'
                    create_level_window('level3.txt', 'level3')
                elif prof_btn.collidepoint(event.pos):
                    create_special_window()
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


def create_special_window():
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
                    create_new_window()

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


class RegistrationForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):  # открываем окно и загружаем картинку
        uic.loadUi('data/Registration.ui', self)

        pixmap = QPixmap('data/background/first_window.jpeg')
        self.label_photo.setPixmap(pixmap)

        self.btn_ok.clicked.connect(self.create_new_player)

        # Показать окно
        self.show()

    def startform(self):
        self.startform = StartForm()
        self.startform.show()

    def create_new_player(self):
        text_login = self.textEdit_login.toPlainText()
        text_password = self.textEdit_password.toPlainText()
        conn = sqlite3.connect('data/project_play_bd.db')
        cursor = conn.cursor()
        if text_login and text_password:
            cursor.execute('SELECT player FROM players')
            rows = cursor.fetchall()
            names = [i[0] for i in rows]
            if text_login in names:
                QMessageBox.warning(self, "Ошибка", 'Такое имя уже существует')
            elif len(text_password) >= 3:
                cursor.execute('INSERT INTO players (player, password, level1, level2, level3, level4, level5)'
                               ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (text_login, text_password, 0, 0, 0, 0, 0))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Информация", f"Вы успешно зарегистрированы")
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", 'Пароль не подходит')
        else:
            QMessageBox.warning(self, "Ошибка", 'Введите логин и пароль')


class StartForm(QtWidgets.QWidget):  # окно авторизации
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):  # открываем окно и загружаем картинку
        uic.loadUi('data/Enter.ui', self)

        pixmap = QPixmap('data/background/first_window.jpeg')
        self.label.setPixmap(pixmap)

        self.btn_further.clicked.connect(self.check_player)
        self.btn_registration.clicked.connect(self.registration)

        # Показать окно
        self.show()

    def registration(self):
        self.registration_form = RegistrationForm()
        self.registration_form.show()

    def check_player(self):  # при нажатии на кнопку проверяем корректность логина и пароля
        # если все правильно запускаем игру
        text_login = self.textEdit_login.toPlainText()
        text_password = self.textEdit_password.toPlainText()
        conn = sqlite3.connect('data/project_play_bd.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM players')
        rows = cursor.fetchall()
        conn.close()
        print(rows)
        for i in range(len(rows)):
            if rows[i][0] == text_login and rows[i][1] == text_password:
                global login
                login = text_login
                print("логин и пароль правильные")
                # записываем из БД прогресс уровней
                for j in rows[i][2:]:
                    level_list.append(j)
                self.start_pygame()
        QMessageBox.warning(self, "Ошибка", 'Неправильный логин или пароль')

    def start_pygame(self):  # сам игровой цикл
        self.close()
        print('login ' + login)
        screen_s = pygame.display.set_mode((750, 750))

        global screen
        screen = screen_s

        pygame.display.set_caption("Главное окно игры")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (249 < cursor_rect.x < 319 and 510 < cursor_rect.y < 560 or
                            178 < cursor_rect.x < 313 and 560 < cursor_rect.y < 615 or
                            165 < cursor_rect.x < 460 and 615 < cursor_rect.y < 750):
                        create_new_window()
                    elif (560 < cursor_rect.x < 605 and 305 < cursor_rect.y < 395 or
                          552 < cursor_rect.x < 630 and 395 < cursor_rect.y < 485):
                        # Код для открытия нового окна
                        create_special_window()

                cursor_rect.topleft = pygame.mouse.get_pos()

                if (249 < cursor_rect.x < 319 and 510 < cursor_rect.y < 560 or
                        178 < cursor_rect.x < 313 and 560 < cursor_rect.y < 615 or
                        165 < cursor_rect.x < 460 and 615 < cursor_rect.y < 750):
                    screen_s.blit(background1, (0, 0))
                elif (560 < cursor_rect.x < 605 and 305 < cursor_rect.y < 395 or
                      552 < cursor_rect.x < 630 and 395 < cursor_rect.y < 485):
                    screen_s.blit(background2, (0, 0))
                else:
                    screen_s.blit(background_window1, (0, 0))

                screen.blit(cursor, cursor_rect)
                pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = StartForm()
    sys.exit(app.exec())
