import pygame
import sys
import os
import random

pygame.init()

screen = pygame.display.set_mode((750, 750))
pygame.display.set_caption("Главное окно игры")

background_window1 = pygame.image.load('data/background/background_window1.png')
background1 = pygame.image.load('data/background/background1.png')
background2 = pygame.image.load('data/background/background2.png')

cursor = pygame.image.load('data/cursor.png')
cursor_rect = cursor.get_rect()

pygame.mouse.set_visible(False)


def load_images_from_folder(folder):
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Папка '{folder}' не найдена.")
    images = []
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            images.append(pygame.image.load(os.path.join(folder, filename)))
    if not images:
        raise FileNotFoundError(f"Нет изображений в папке '{folder}'.")
    return images


tile_images = {
    'wall': load_images_from_folder('data/walls'),
    'empty': load_images_from_folder('data/empty')
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
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = random.choice(tile_images[tile_type])
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.type = tile_type
        if tile_type == 'wall':
            walls_group.add(self)  # Добавляем в группу стен


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.images = player_images
        self.image = self.images[0]
        # Смещаем персонажа на половину ширины и высоты спрайта
        self.rect = self.image.get_rect().move(tile_width * pos_x + tile_width // 2 - self.image.get_width() // 2,
                                               tile_height * pos_y + tile_height // 2 - self.image.get_height() // 2)
        self.frame = 0
        self.animation_speed = 0.05
        self.direction = 'idle'
        self.move_delay = 30

    def update(self):
        keys = pygame.key.get_pressed()
        if self.move_delay == 0:
            new_rect = self.rect.copy()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                new_rect.y -= tile_height
                self.direction = 'up'
                self.move_delay = 30
                print("Движение вверх")
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                new_rect.y += tile_height
                self.direction = 'down'
                self.move_delay = 30
                print("Движение вниз")
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                new_rect.x -= tile_width
                self.direction = 'left'
                self.move_delay = 30
                print("Движение влево")
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                new_rect.x += tile_width
                self.direction = 'right'
                self.move_delay = 30
                print("Движение вправо")
            else:
                self.direction = 'idle'

            # Проверка на столкновение только со спрайтами стен
            collision = any(new_rect.colliderect(wall.rect) for wall in walls_group if wall.type == 'wall')
            if collision:
                print("Столкновение со стеной")
            else:
                # Проверка границ экрана
                if 0 <= new_rect.left and new_rect.right <= screen.get_width() and \
                        0 <= new_rect.top and new_rect.bottom <= screen.get_height():
                    self.rect = new_rect
                else:
                    print("Выход за границы экрана")

        if self.direction != 'idle':
            self.frame += self.animation_speed
            if self.frame >= len(self.images):
                self.frame = 1
            self.image = self.images[int(self.frame)]
        else:
            self.image = self.images[0]

        if self.move_delay > 0:
            self.move_delay -= 1


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def create_level_window():
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Уровень")
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)

    player, level_x, level_y = generate_level(load_level('level1.txt'))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player_group.update()
        cursor_rect.topleft = pygame.mouse.get_pos()
        new_screen.fill((200, 200, 200))
        tiles_group.draw(new_screen)
        player_group.draw(new_screen)
        new_screen.blit(cursor, cursor_rect)
        pygame.display.flip()


def create_new_window():
    new_screen = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Выбор уровня")
    background_window2 = pygame.image.load('data/background/background_window2.png')
    cursor = pygame.image.load('data/cursor.png')
    cursor_rect = cursor.get_rect()
    pygame.mouse.set_visible(False)

    button_image = pygame.image.load('data/button.png')
    button_image = pygame.transform.scale(button_image, (200, 100))

    font = pygame.font.Font(None, 36)

    level1_text = font.render("Уровень 1", True, (255, 255, 255))
    level2_text = font.render("Уровень 2", True, (255, 255, 255))

    level1_button_rect = pygame.Rect(100, 200, button_image.get_width(), button_image.get_height())
    level2_button_rect = pygame.Rect(100, 320, button_image.get_width(), button_image.get_height())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if level1_button_rect.collidepoint(event.pos):
                    create_level_window()
                elif level2_button_rect.collidepoint(event.pos):
                    create_level_window()

        cursor_rect.topleft = pygame.mouse.get_pos()

        new_screen.blit(background_window2, (0, 0))
        new_screen.blit(button_image, level1_button_rect.topleft)
        new_screen.blit(button_image, level2_button_rect.topleft)
        new_screen.blit(level1_text, (level1_button_rect.x + (button_image.get_width() - level1_text.get_width()) // 2,
                                      level1_button_rect.y + (
                                              button_image.get_height() - level1_text.get_height()) // 2))
        new_screen.blit(level2_text, (level2_button_rect.x + (button_image.get_width() - level2_text.get_width()) // 2,
                                      level2_button_rect.y + (
                                              button_image.get_height() - level2_text.get_height()) // 2))
        new_screen.blit(cursor, cursor_rect)
        pygame.display.flip()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
