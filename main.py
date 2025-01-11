import pygame
import sys
import os
import random

pygame.init()

screen = pygame.display.set_mode((750, 750))
pygame.display.set_caption("Главное окно игры")

background_window1 = pygame.image.load('data/background_window1.png')
background1 = pygame.image.load('data/background1.png')
background2 = pygame.image.load('data/background2.png')

cursor = pygame.image.load('data/cursor.png')
cursor_rect = cursor.get_rect()

pygame.mouse.set_visible(False)


def load_wall_images():
    wall_images = []
    for filename in os.listdir('data/walls'):
        if filename.endswith('.png'):
            wall_images.append(pygame.image.load(os.path.join('data/walls', filename)))
    if not wall_images:
        raise FileNotFoundError("No wall images found in 'data/walls' directory.")
    return wall_images


tile_images = {
    'wall': load_wall_images(),
    'empty': pygame.image.load('data/empty.png')
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
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'wall':
            self.image = random.choice(tile_images[tile_type])
        else:
            self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.images = player_images
        self.image = self.images[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.frame = 0
        self.animation_speed = 0.1

    def update(self):
        self.frame += self.animation_speed
        if self.frame >= len(self.images):
            self.frame = 0
        self.image = self.images[int(self.frame)]


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
    background_window2 = pygame.image.load('data/background_window2.png')
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
