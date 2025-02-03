import sqlite3
import sys

import pygame
import subprocess

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('music/menu_music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

# Размеры экрана
WIDTH, HEIGHT = 1000, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

stats_db = sqlite3.connect('stats.sqlite3')
stats_cursor = stats_db.cursor()

# Шрифт
font = pygame.font.Font(None, 36)
selected_index = stats_cursor.execute("""SELECT tk_level FROM Choise""").fetchone()[0]
selected_skin = stats_cursor.execute("""SELECT skin FROM Choise""").fetchone()[0]
time = stats_cursor.execute("""SELECT time FROM stats WHERE level = 1""").fetchone()[0]


# Класс для кнопки (с изображениями)
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None, image=None, hover_image=None,
                 play_bt=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = font
        self.text_surface = self.font.render(self.text, True, BLACK) if self.text else None
        self.text_rect = self.text_surface.get_rect(center=self.rect.center) if self.text_surface else None
        self.image = image
        self.hover_image = hover_image
        self.current_image = self.image

        if self.image:
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

        if self.hover_image:
            self.hover_image = pygame.transform.scale(self.hover_image, (self.rect.width, self.rect.height))

    def draw(self, surface):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color

        if self.image or self.hover_image:
            if self.rect.collidepoint(pygame.mouse.get_pos()) and self.hover_image:
                self.current_image = self.hover_image
            else:
                self.current_image = self.image
            surface.blit(self.current_image, self.rect)
        else:
            pygame.draw.rect(surface, color, self.rect)

        if self.text_surface:
            surface.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos) and self.action:
                if play_button:
                    if not (selected_index == 1 or
                            stats_cursor.execute("""SELECT completed FROM stats WHERE level = ?""",
                                                 (selected_index - 1,)).fetchone()[0]):
                        return
                self.action()


def png_img(path, x, y, screen, convert=None):
    image = pygame.image.load(path).convert_alpha()
    if convert is not None:
        image = pygame.transform.scale(image, convert)

    image_rect = image.get_rect()
    image_rect.center = (x, y)
    screen.blit(image, image_rect)


def run_another_python_script(script_path):
    try:
        python_executable = sys.executable  # Путь к интерпретатору текущего скрипта
        process = subprocess.run([python_executable, script_path], capture_output=True, text=True, check=True)
        print(process.stdout)
        print(process.stderr)


    except subprocess.CalledProcessError as e:
        print(f"Error running script: {script_path}")
        print(f"Return code: {e.returncode}")
        print(f"Error output:\n{e.stderr}")


# Функции для кнопок
def start_game():
    pygame.mixer.music.pause()
    script_to_run = "code.py"
    run_another_python_script(script_to_run)


def exit_game():
    pygame.quit()
    quit()


def button1_action():
    global selected_skin
    selected_skin = 1
    stats_db.execute('UPDATE Choise SET skin = (?)', (selected_skin,))
    stats_db.commit()


def button2_action():
    global selected_skin
    selected_skin = 2
    stats_db.execute('UPDATE Choise SET skin = (?)', (selected_skin,))
    stats_db.commit()


def button3_action():
    global selected_skin
    selected_skin = 3
    stats_db.execute('UPDATE Choise SET skin = (?)', (selected_skin,))
    stats_db.commit()


# Создание кнопок
play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Играть", GRAY, BLUE, start_game,
                     pygame.image.load("data/button/green_button.png"),
                     pygame.image.load("data/button/red_button.png"), play_bt=True)

exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 15, 200, 50, "Выход", GRAY, BLUE, exit_game,
                     pygame.image.load("data/button/green_button.png"),
                     pygame.image.load("data/button/red_button.png"))

button_left_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 - 100, 50, 50, )
button_right_rect = pygame.Rect(WIDTH // 2 + 60, HEIGHT // 2 - 100, 50, 50, )

# Создание трех кнопок в ряд
button_width = 50
button_height = 50
button_spacing = 20
start_x = 50
buttons_row = [
    Button(start_x, HEIGHT - 100, button_width, button_height, None, GRAY, BLUE, button1_action,
           pygame.image.load("data/button/pl_1_button.png")),
    Button(start_x + button_width + button_spacing, HEIGHT - 100, button_width, button_height, None, GRAY, BLUE,
           button2_action, pygame.image.load("data/button/pl_2_button.png")),
    Button(start_x + button_width * 2 + button_spacing * 2, HEIGHT - 100, button_width, button_height, None, GRAY,
           BLUE,
           button3_action, pygame.image.load("data/button/pl_3_button.png"))
]

# Основной цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = event.pos
                if button_left_rect.collidepoint(mouse_pos):
                    if selected_index > 1:  # Проверка, чтобы индекс не был меньше 1
                        selected_index -= 1
                        stats_db.execute('UPDATE Choise SET tk_level = (?)', (selected_index,))
                        time = stats_cursor.execute('SELECT time FROM stats WHERE level = (?)',
                                                    (selected_index,)).fetchone()[0]
                        stats_db.commit()
                elif button_right_rect.collidepoint(mouse_pos):
                    if selected_index < 12:  # Проверка, чтобы индекс не был больше 20
                        selected_index += 1
                        stats_db.execute('UPDATE Choise SET tk_level = (?)', (selected_index,))
                        time = stats_cursor.execute('SELECT time FROM stats WHERE level = (?)',
                                                    (selected_index,)).fetchone()[0]
                        stats_db.commit()
        play_button.handle_event(event)
        exit_button.handle_event(event)
        for button in buttons_row:
            button.handle_event(event)
    pygame.mixer.music.unpause()
    # Отрисовка
    screen.fill(WHITE)
    if selected_index in [1, 2, 3]:
        n = 1
    elif selected_index in [4, 5, 6]:
        n = 2
    elif selected_index in [7, 8, 9]:
        n = 3
    else:
        n = 4
    png_img(f'data/fon_{n}.png', WIDTH // 2, HEIGHT // 2, screen)
    png_img(f'data/pl_{selected_skin}_1.png', start_x + 75, 250, screen, (149, 200))
    play_button.draw(screen)
    exit_button.draw(screen)
    text_left = font.render("<", True, BLACK)
    text_right = font.render(">", True, BLACK)
    screen.blit(text_left, text_left.get_rect(center=button_left_rect.center))
    screen.blit(text_right, text_right.get_rect(center=button_right_rect.center))

    level_text = f"Уровень {selected_index}"
    text_surface = font.render(level_text, True, BLACK)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
    screen.blit(text_surface, text_rect)

    level_time = f"Время: {time}"
    time_surface = font.render(level_time, True, BLACK)
    time_rect = time_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(time_surface, time_rect)

    for button in buttons_row:
        button.draw(screen)
    pygame.display.flip()

pygame.quit()
stats_db.close()
