import pygame
import sys
import random
from PyQt6 import QtWidgets, uic
import sqlite3
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox
from finish_window import finish_window
from create_special_window import create_special_window
from create_new_window import create_new_window
from load import load_level, load_images_from_folder, load_sprite_sheet, load_monster_spritesheets

login = ""  # переменная для хранения имя пользователя
level_list = []  # для хранения прогресса уровня: 0 не пройден, 1 пройден
pygame.init()
levelg = ''
screen = None  # для экрана

background_window1 = pygame.image.load('data/background/background_window1.png')
background1 = pygame.image.load('data/background/background1.png')
background2 = pygame.image.load('data/background/background2.png')

cursor = pygame.image.load('data/cursor.png')
cursor_rect = cursor.get_rect()

pygame.mouse.set_visible(False)


tile_images = {
    'wall': load_images_from_folder('data/walls'),
    'empty': load_images_from_folder('data/empty'),
    'l': load_images_from_folder('data'),
    'teleport_e': load_images_from_folder('data/teleport_e'),
    'teleport_q': load_images_from_folder('data/teleport_q')
}

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
        self.speed = 1  # Начальная скорость
        self.default_speed = 1  # Сохранение начальной скорости
        print('создан персонаж')

    def update(self, message):
        keys = pygame.key.get_pressed()
        move_multiplier = self.speed  # Используем текущую скорость для умножения

        if self.move_delay == 0:
            new_rect = self.rect.copy()
            step_size = tile_width
            c = load_level(levelg)
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


# Загрузка спрайтовых листов для монстров
monster_spritesheets = load_monster_spritesheets()


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.frames = random.choice(monster_spritesheets)
        self.image = self.frames['down'][0]  # Начальная анимация вниз
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.speed = 1
        self.frame = 0
        self.animation_speed = 0.1
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        print(f"Монстр создан на позиции ({pos_x}, {pos_y})")

    def update(self, player):
        new_rect = self.rect.copy()

        if self.direction == 'left':
            new_rect.x -= self.speed
        elif self.direction == 'right':
            new_rect.x += self.speed
        elif self.direction == 'up':
            new_rect.y -= self.speed
        elif self.direction == 'down':
            new_rect.y += self.speed

        # Проверка на столкновение со стенами
        collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
        if collision:
            self.direction = random.choice(['left', 'right', 'up', 'down'])  # Меняем направление при столкновении
        else:
            self.rect = new_rect

        # Анимация монстра в зависимости от направления
        self.frame += self.animation_speed
        if self.direction == 'left':
            if self.frame >= len(self.frames['left']):
                self.frame = 0
            self.image = self.frames['left'][int(self.frame)]
        elif self.direction == 'right':
            if self.frame >= len(self.frames['right']):
                self.frame = 0
            self.image = self.frames['right'][int(self.frame)]
        elif self.direction == 'up':
            if self.frame >= len(self.frames['up']):
                self.frame = 0
            self.image = self.frames['up'][int(self.frame)]
        elif self.direction == 'down':
            if self.frame >= len(self.frames['down']):
                self.frame = 0
            self.image = self.frames['down'][int(self.frame)]


def generate_level(level):
    new_player, x, y = None, None, None
    teleport_points = {}
    win_point = None
    monster = []
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
                m = Monster(x, y)
                monster.append(m)
                all_sprites.add(m)  # Добавляем монстра в группу спрайтов
                print("Монстр добавлен в группу спрайтов")
    print(f"Монстр: {monster}")
    return new_player, teleport_points, win_point, monster, l_points


def create_level_window(map_level, level, level_file):
    global levelg
    levelg = level_file
    new_screen = pygame.display.set_mode((850, 850))
    pygame.display.set_caption("Уровень")
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)
    start_time = None

    # Очистка всех групп спрайтов перед загрузкой нового уровня
    all_sprites.empty()
    tiles_group.empty()
    walls_group.empty()
    player_group.empty()

    player, teleport_points, win_point, monster, l_point = generate_level(load_level(map_level))
    count_l = 0

    speed_bar = SpeedBar(max_speed=100, fill_time=7, drain_time=4, width=200, height=20, x=325, y=800)
    accelerating = False

    global level_list

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (
                        pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT,
                        pygame.K_a, pygame.K_t):
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        player.update('up')
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        player.update('down')
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.update('right')
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        player.update('left')
                    if event.key == pygame.K_t:
                        print('нажата t')
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

                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    if speed_bar.current_speed > 0:
                        accelerating = True
                        player.speed = 2
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    accelerating = False
                    player.speed = player.default_speed

        if start_time is not None:
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time >= 3000:
                print('время вышло')
                for i in l_point:
                    tile_file = f'empty{(i[0] + i[1]) % 10}.png'
                    Tile('empty', i[0], i[1], tile_file)
                start_time = None

        player_group.update('')
        for i in monster:
            if i:
                i.update(player)

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
                level_list[int(level[-1]) - 1] = 1
            finish_window('win', draw_multiline_text, login, level_list, create_level_window, create_new_window,
                  create_special_window)

        for i in monster:
            if i and player.rect.colliderect(i.rect):
                print('вас убил монстр')
                finish_window('loss_m', draw_multiline_text, login, level_list, create_level_window, create_new_window,
                  create_special_window)

        for i in l_point:
            if player.rect.colliderect(pygame.Rect(i[0] * tile_width, i[1] * tile_height, tile_width, tile_height)):
                print('вы попали в ловушку')
                finish_window('loss_l', draw_multiline_text, login, level_list, create_level_window, create_new_window,
                  create_special_window)

        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.fill((200, 200, 200))
        tiles_group.draw(new_screen)
        player_group.draw(new_screen)
        for i in monster:
            if i:
                new_screen.blit(i.image, i.rect.topleft)
        new_screen.blit(cursor, cursor_rect)

        # Обновляем шкалу ускорения
        speed_bar.update(accelerating)

        # Проверяем и обновляем состояние ускорения
        if accelerating and speed_bar.current_speed > 0:
            speed_bar.update(True)  # Понижаем шкалу ускорения
        else:
            player.speed = player.default_speed  # Возвращаем нормальную скорость, если не ускоряемся

        # Рисуем шкалу ускорения
        speed_bar.draw(new_screen)

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


class SpeedBar:
    def __init__(self, max_speed, fill_time, drain_time, width, height, x, y):
        self.max_speed = max_speed
        self.current_speed = max_speed  # Начальная шкала заполнена
        self.fill_time = fill_time
        self.drain_time = drain_time
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.fill_rate = max_speed / (fill_time * 60)  # Переводим время в кадры (при 60 FPS)
        self.drain_rate = max_speed / (drain_time * 60)

    def update(self, accelerating):
        if accelerating and self.current_speed > 0:
            self.current_speed -= self.drain_rate
        elif not accelerating and self.current_speed < self.max_speed:
            self.current_speed += self.fill_rate

    def draw(self, screen):
        # Рисуем рамку шкалы
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height), 2)
        # Заполняем шкалу в зависимости от текущего уровня скорости
        inner_width = (self.current_speed / self.max_speed) * self.width
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, inner_width, self.height))


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
                        create_new_window(login, level_list, create_level_window, draw_multiline_text,
                                          create_special_window)
                    elif (560 < cursor_rect.x < 605 and 305 < cursor_rect.y < 395 or
                          552 < cursor_rect.x < 630 and 395 < cursor_rect.y < 485):
                        # Код для открытия нового окна
                        create_special_window(login, level_list, create_level_window, draw_multiline_text,
                                              create_new_window)

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
                font = pygame.font.Font(None, 24)
                text_surface = font.render('Наведите курсор на дорогу или домик', True, (255, 255, 255))
                screen.blit(text_surface, (10, 10))
                pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = StartForm()
    sys.exit(app.exec())
