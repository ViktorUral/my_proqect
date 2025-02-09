import json
import os
import random
import sqlite3
import pygame
import sys

pygame.init()
pygame.mixer.init()

size = width, height = 1000, 500
game_screen = pygame.Surface((width, height))
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

game_ratio = width / height
screen_ratio = screen_width / screen_height

if screen_ratio > game_ratio:
    scaled_height = screen_height
    scaled_width = int(scaled_height * game_ratio)
    x_offset = (screen_width - scaled_width) // 2
    y_offset = 0
else:
    scaled_width = screen_width
    scaled_height = int(scaled_width / game_ratio)
    x_offset = 0
    y_offset = (screen_height - scaled_height) // 2

all_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()
blocks_sprites = pygame.sprite.Group()
left_blocks_sprites = pygame.sprite.Group()
right_blocks_sprites = pygame.sprite.Group()
down_blocks_sprites = pygame.sprite.Group()
up_blocks_sprites = pygame.sprite.Group()
triger_sprites = pygame.sprite.Group()
partigle_sprites = pygame.sprite.Group()
ship_sprites = []

SPEED_X = 0.25
SPEED_Y = 3
GRAVITY = 1
screen_rect = (0, 0, width, height)
n = 1

lvl_db = sqlite3.connect('levels.sqlite3')
lvl_cursor = lvl_db.cursor()
stats_db = sqlite3.connect('stats.sqlite3')
stats_cursor = stats_db.cursor()

level = stats_cursor.execute("""SELECT tk_level FROM Choise""").fetchone()[0]
skin = stats_cursor.execute("""SELECT skin FROM Choise""").fetchone()[0]
pygame.mixer.music.load('music/fon_music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)
sound_jump = pygame.mixer.Sound('music/jump.mp3')
sound_jump.set_volume(0.1)
time = 0
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)
font = pygame.font.Font(None, 36)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Particle(pygame.sprite.Sprite):
    fire = [load_image("particle.png")]
    for scale in (2, 4, 6):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy, up_y):
        super().__init__(partigle_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.up_y = up_y
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        if self.up_y >= 0:
            self.rect.y += -self.velocity[1]
            self.up_y -= 1
        else:
            self.rect.y += self.velocity[1]
        if pygame.sprite.spritecollideany(self, blocks_sprites):
            self.kill()


def create_particles(position):
    particle_count = 1
    numbers = range(-3, 3)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), 1)


class Player(pygame.sprite.Sprite):
    image = load_image(f"pl_{skin}_1.png")

    def __init__(self, coord):
        super().__init__(all_sprites)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = coord[0] + 10
        self.rect.y = coord[1]
        self.jump = False
        self.dx = 0
        self.dy = 0
        self.time_for_after_jump = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        Player.image = load_image(f"pl_{skin}_1.png")
        if keys[pygame.K_a]:
            if self.dx > -5:
                self.dx -= SPEED_X
                Player.image = load_image(f"pl_{skin}_4b.png")
            else:
                self.dx += SPEED_X
            if pygame.sprite.spritecollideany(self, up_blocks_sprites):
                create_particles([self.rect.x + 3 * self.rect.width // 4, self.rect.y + 4 * self.rect.height // 5])
        elif keys[pygame.K_d]:
            if self.dx < 5:
                self.dx += SPEED_X
                Player.image = load_image(f"pl_{skin}_4a.png")
            else:
                self.dx -= SPEED_X
            if pygame.sprite.spritecollideany(self, up_blocks_sprites):
                create_particles([self.rect.x + 1 * self.rect.width // 4, self.rect.y + 4 * self.rect.height // 5])
        else:
            if self.dx != 0:
                self.dx -= 0.0625 * abs(self.dx) / self.dx
        if (keys[pygame.K_SPACE] and (pygame.sprite.spritecollideany(self, up_blocks_sprites) or
                                      pygame.sprite.spritecollideany(self, right_blocks_sprites) or
                                      pygame.sprite.spritecollideany(self, left_blocks_sprites))):
            self.jump = True
            self.dy = 0
            self.time_for_after_jump = 0
            sound_jump.play()
        if self.jump:
            if self.dx > 0:
                Player.image = load_image(f"pl_{skin}_2a.png")
            else:
                Player.image = load_image(f"pl_{skin}_2b.png")
            self.dy -= SPEED_Y
            self.rect.y -= SPEED_Y
        if self.dy <= -180:
            self.jump = False
        elif pygame.sprite.spritecollideany(self, down_blocks_sprites):
            self.jump = False
            self.rect.y += SPEED_Y / 2
        if not pygame.sprite.spritecollideany(self, blocks_sprites) and not self.jump:
            if self.dy and self.time_for_after_jump < 1:
                self.time_for_after_jump += 0.25
            else:
                if self.dx > 0:
                    Player.image = load_image(f"pl_{skin}_3a.png")
                else:
                    Player.image = load_image(f"pl_{skin}_3b.png")
                self.rect.y += SPEED_Y
            if pygame.sprite.spritecollideany(self, blocks_sprites):
                # тут частицы должны быть
                self.rect.y -= 1
        self.rect.x += self.dx
        if pygame.sprite.spritecollideany(self, left_blocks_sprites):
            self.rect.x -= 1
            self.dx = 0
        elif pygame.sprite.spritecollideany(self, right_blocks_sprites):
            self.rect.x += 1
            self.dx = 0
        if pygame.sprite.spritecollideany(self, triger_sprites):
            global level
            self.kill()
            stats_db.execute('UPDATE stats SET time = (?), completed = (?) WHERE level = ?',
                             (time, True, level))
            level += 1
            stats_db.execute('UPDATE Choise SET tk_level = (?)', (level,))
            stats_db.commit()
            new_game(level)

        self.mask = pygame.mask.from_surface(self.image)
        for i in ship_sprites:
            if pygame.sprite.collide_mask(self, i):
                new_game(level)
                break

        self.image = Player.image


class Hitbox(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, name):
        super().__init__(all_sprites)
        dict_name = {'left': left_blocks_sprites, 'right': right_blocks_sprites, 'down': down_blocks_sprites,
                     'up': up_blocks_sprites}
        self.image = pygame.Surface([1, y2])
        self.add(dict_name[name])
        self.rect = pygame.Rect(x1, y1, x2, y2)


class Triger(pygame.sprite.Sprite):
    """Переходы между уровнями"""
    image = load_image('flag.png')

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Triger.image
        self.rect = self.image.get_rect(topleft=(x, y))


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, up_bl):
        super().__init__(all_sprites)
        if up_bl != 1 and up_bl != 3:
            self.image = load_image(f"block{n}_1.png")
        else:
            self.image = load_image(f"block{n}_2.png")
        self.rect = self.image.get_rect(topleft=(x, y))
        left = Hitbox(x, y + 2, 1, self.rect.height - 3, 'left')
        right = Hitbox(x + self.rect.width - 1, y + 2, 1, self.rect.height - 3, 'right')
        up = Hitbox(x + 1, y, self.rect.width - 2, 1, 'up')
        down = Hitbox(x + 1, y + self.rect.height - 1, self.rect.width - 2, 1, 'down')


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image("ship.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y + 25)
        self.mask = pygame.mask.from_surface(self.image)
    def end(self):
        self.mask.clear()


class Environment(pygame.sprite.Sprite):
    """Окружение"""

    def __init__(self, x, y, image):
        super().__init__(all_sprites)
        self.image = load_image(image)
        self.rect = self.image.get_rect(topleft=(x, y))


def kill_matrix():
    all_sprites.empty()


class Pole:
    """Поля для создании блоков и игроков"""

    def __init__(self, width, height, board):
        self.coords_player = []
        self.width = width
        self.height = height
        self.board = board

    def render(self):
        for j in range(len(self.board)):
            for i in range(len(self.board[j])):
                if self.board[j][i] == 1:
                    if j > 0:
                        a = self.board[j - 1][i]
                    else:
                        a = 1

                    block = Block(i * self.width, j * self.height, a)
                    blocks_sprites.add(block)
                elif self.board[j][i] == 2:
                    self.coords_player = [i * self.width, j * self.height]
                elif self.board[j][i] == 3:
                    s = Ship(i * self.width, j * self.height)
                    ship_sprites.append(s)
                elif self.board[j][i] == 9:
                    triger = Triger(i * self.width, j * self.height)
                    triger_sprites.add(triger)
                elif self.board[j][i] == 11:
                    Environment(i * self.width, j * self.height, 'fence.png')
                elif self.board[j][i] == 12:
                    Environment(i * self.width, j * self.height, 'sign_1.png')
                elif self.board[j][i] == 13:
                    Environment(i * self.width, j * self.height, 'exit.png')
                elif self.board[j][i] == 14:
                    Environment(i * self.width, j * self.height, 'bush_1.png')
                elif self.board[j][i] == 15:
                    Environment(i * self.width, j * self.height, 'bush_2.png')


pole, player = '', ''


def new_game(lvl):
    global pole, player, time, n
    if level in [1, 2, 3]:
        n = 1
    elif level in [4, 5, 6]:
        n = 2
    elif level in [7, 8, 9]:
        n = 3
    else:
        n = 4
    lvl_cursor.execute("SELECT id, matrix FROM my_table WHERE id=(?)", (lvl,))
    rows = lvl_cursor.fetchall()
    matrix = json.loads(rows[0][1])

    all_sprites.empty()
    blocks_sprites.empty()
    right_blocks_sprites.empty()
    down_blocks_sprites.empty()
    left_blocks_sprites.empty()
    up_blocks_sprites.empty()
    triger_sprites.empty()
    for _ in ship_sprites:
        _.end()
    
    pole = Pole(50, 50, matrix)
    time = 0
    pole.render()
    player = Player(pole.coords_player)


new_game(level)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == TIMER_EVENT:
            time += 1

    keys = pygame.key.get_pressed()
    player.update(keys)
    partigle_sprites.update()

    if player.rect.y > 600:
        new_game(level)
        
    image = load_image(f"fon_{n}.png")
    image_rect = image.get_rect()
    game_screen.blit(image, image_rect)
    blocks_sprites.draw(game_screen)
    all_sprites.draw(game_screen)
    partigle_sprites.draw(game_screen)
    text = font.render(f"Время: {time} c", True, 'white')
    text_rect = text.get_rect()
    text_rect.x = width - text_rect.width
    text_rect.y = 0
    game_screen.blit(text, text_rect)

    scaled_surface = pygame.transform.scale(game_screen, (scaled_width, scaled_height))
    screen.blit(scaled_surface, (x_offset, y_offset))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
lvl_db.close()
