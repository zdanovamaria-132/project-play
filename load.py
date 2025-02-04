import pygame
import os


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r', encoding='utf-8') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


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


def load_monster_spritesheets():
    monster_spritesheets = []
    for i in range(1, 3):  # Загружаем только два файла
        spritesheet = pygame.image.load(f'data/monster_spritesheet_{i}.png')
        if i == 1:
            frames = {
                'down': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=4, row=0),
                'left': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=4, row=1),
                'right': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=4, row=2),
                'up': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=4, row=3)
            }
        else:
            frames = {
                'down': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=3, row=0),
                'left': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=3, row=1),
                'right': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=3, row=2),
                'up': load_sprite_sheet(spritesheet, frame_width=50, frame_height=50, num_frames=3, row=3)
            }
        monster_spritesheets.append(frames)
    return monster_spritesheets
