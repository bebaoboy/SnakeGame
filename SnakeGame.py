import math
import time

import pygame
import random
from display_ingame_text import display_ingame_text

PNG_SIZE = 32

dir_table = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d
}


class Background:
    def __init__(self):
        self._background_img = None
        self._background_rect = None

    def load_img(self, img_path, size, location=(0, 0)):
        self._background_img = pygame.image.load(img_path).convert_alpha()
        self._background_img = pygame.transform.scale(self._background_img, size)
        self._background_rect = self._background_img.get_rect()
        self._background_rect.topleft = location

    def blit(self, screen: pygame.surface.Surface):
        self._background_img.set_alpha(220)
        screen.blit(self._background_img, self._background_rect.topleft)


class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, speed):
        super().__init__()
        self.image = pygame.image.load('assets/snake.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PNG_SIZE + 2, PNG_SIZE))
        self.rect = self.image.get_rect()
        self.direction = None
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, dt, d=None):
        dt = math.floor(dt)
        direction = {
            dir_table['left']: -90,
            dir_table['right']: 90,
            dir_table['up']: 180,
            dir_table['down']: 0
        }
        if d in direction:
            if self.direction:
                self.image = pygame.transform.rotate(self.image, -direction[self.direction])
            self.direction = d
            self.image = pygame.transform.rotate(self.image, direction[d])

        if self.direction == dir_table['left']:
            self.rect.centerx -= dt * self.speed
        elif self.direction == dir_table['right']:
            self.rect.centerx += dt * self.speed
        elif self.direction == dir_table['down']:
            self.rect.centery += dt * self.speed
        elif self.direction == dir_table['up']:
            self.rect.centery -= dt * self.speed

        if self.rect.midright[0] < 0:
            self.rect.midleft = (self.screen_width, self.rect.midleft[1])
        if self.rect.midleft[0] > self.screen_width:
            self.rect.midright = (0, self.rect.midright[1])
        if self.rect.midbottom[1] < 0:
            self.rect.midtop = (self.rect.midtop[0], self.screen_height)
        if self.rect.midtop[1] > self.screen_height:
            self.rect.midbottom = (self.rect.midbottom[0], 0)


class SnakeBody(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/body.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PNG_SIZE, PNG_SIZE))
        self.rect = self.image.get_rect()


class Apple(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/apple.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PNG_SIZE + 10, PNG_SIZE + 10))
        self.rect = self.image.get_rect()
        self.rect.center = pos


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/wall.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PNG_SIZE + 5, PNG_SIZE - 5))
        self.rect = self.image.get_rect()
        self.rect.center = pos


class SnakeGame:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 600, 600
        self.cell_size = PNG_SIZE
        self._clock = pygame.time.Clock()
        self._FPS = 60
        self._dt = 1
        self._font = 'Courier New Bold'

        self._move_timer = 0
        self._last_time = 0

        self.score = 0
        self._game_over = False
        self._game_start = False

        self._background = Background()

        self._snake = None
        self._body = []
        self._apple = None
        self._last_apple_pos = (0, 0)
        self._wall = []

    # noinspection PyTypeChecker
    def on_init(self):
        pygame.init()

        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._background.load_img('assets/grass.png', self.size)

        self._running = True

    def start(self):
        self._snake = pygame.sprite.GroupSingle()

        self._body = [pygame.sprite.GroupSingle()
                      ]
        self._apple = pygame.sprite.GroupSingle()

        self._wall = []
        y_pos = random.randint(100, self.width - self.cell_size)
        x_pos = random.randint(100, self.height - self.cell_size)
        direction = random.choice([dir_table['right'], dir_table['left']])
        print(direction)

        self._snake.add(SnakeHead(self.width, self.height, PNG_SIZE - 2))
        self._snake.update(0, direction)
        self._snake.sprite.rect.center = (y_pos, x_pos)

        self.place_body(x_pos, y_pos, direction)
        self.place_wall()

        self._move_timer = pygame.time.get_ticks()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if self._game_start:
                if event.key in list(dir_table.values()):
                    self._snake.update(0, event.key)
            else:
                if event.key == pygame.K_RETURN:
                    self._game_start = True
                    self._game_over = False
                    self.score = 0
                    self.start()

    def on_update(self):
        current_time = pygame.time.get_ticks()

        if self._game_start:
            if current_time - self._move_timer >= 300:
                self._move_timer = current_time
                self.move_snake()

            self.main_logic()

    def on_render(self):
        self._display_surf.fill('black')
        self._background.blit(self._display_surf)

        if self._snake is not None:
            self.draw_snake()
            self._apple.draw(self._display_surf)
            for wall in self._wall:
                wall.draw(self._display_surf)

        display_ingame_text(self._display_surf, self._font, f'Score: {self.score}', self.width / 2, 20, font_size=35)

        if not self._game_start:
            display_ingame_text(self._display_surf, self._font, 'Press enter to start',
                                self.width / 2, self.height / 2 + 40,
                                font_size=30)

        if self._game_over:
            self._game_start = False
            display_ingame_text(self._display_surf, self._font, 'Game over', self.width / 2, self.height / 2 - 20,
                                font_size=35)

        pygame.display.flip()

    def on_cleanup(self):
        self.size = 0
        pygame.quit()

    def on_execute(self):
        self.on_init()
        self._last_time = time.time()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            now = time.time()
            self._dt = now - self._last_time
            self._last_time = now
            self._dt *= self._FPS
            self._dt += 1
            # print(self._dt)
            if self._game_start:
                self.on_update()
            self.on_render()

        self.on_cleanup()

    def main_logic(self):
        if not self._apple.sprite:
            self._last_apple_pos = self.place_apple()

        self.check_collision()

    def move_snake(self):
        tmp = self._snake.sprite.rect.center
        for i in range(0, len(self._body)):
            cur = self._body[i].sprite.rect.center
            self._body[i].sprite.rect.center = tmp
            tmp = cur
        self._snake.update(self._dt)

    def draw_snake(self):
        self._snake.draw(self._display_surf)
        self._body[len(self._body) - 1].sprite.image.set_alpha(128)
        for body in self._body:
            body.draw(self._display_surf)

    def place_apple(self):
        x_pos = random.randint(20, self.width - 10)
        y_pos = random.randint(20, self.height - 10)
        apple = Apple((x_pos, y_pos))
        cl = False
        while True:
            for wall in self._wall:
                if pygame.sprite.spritecollide(apple, wall, False):
                    x_pos = random.randint(20, self.width - 10)
                    y_pos = random.randint(20, self.height - 10)
                    apple = Apple((x_pos, y_pos))
                    cl = True
                    break
                else:
                    cl = False

            while abs(x_pos - self._last_apple_pos[0]) < 100 and abs(y_pos - self._last_apple_pos[1]) < 100:
                x_pos = random.randint(20, self.width - 10)
                y_pos = random.randint(20, self.height - 10)
                apple = Apple((x_pos, y_pos))

            if not cl:
                break

        self._apple.add(apple)
        return x_pos, y_pos

    def place_wall(self):
        min_space_between = 90
        max_space_between = 135
        num_of_wall = random.randint(3, 8)
        # print(f'num of wall={num_of_wall}')
        wall_list = [random.randint(10, 12) for _ in range(num_of_wall)]
        w = Wall((0, 0))
        wall_length = w.image.get_width()
        wall_height = w.image.get_height()
        # print(wall_list)
        y_pos = random.randint(0, 70)

        for wall in wall_list:
            walls = pygame.sprite.Group()
            direction = random.randint(1, 2)
            # print(f'dir={direction}')

            if direction == 1:  # left to right
                x_pos = random.choice([random.randint(wall * wall_length + wall_length // 2, self.width),
                                       self.width, self.width, self.width])
                # x_pos = self.width
                initial_center = x_pos - wall_length // 2
                walls.add(Wall((initial_center, y_pos)))
                for adj_wall in range(wall):
                    if y_pos < self.height - wall_length // 2:
                        if not self._snake.sprite.rect.top - wall_height // 2 <= y_pos \
                               <= self._snake.sprite.rect.bottom + wall_height // 2:
                            initial_center -= wall_length
                            if initial_center >= wall_length // 2:
                                # print(f'x={initial_center}, y={y_pos}')
                                walls.add(Wall((initial_center, y_pos)))
                            else:
                                break
                        else:
                            walls = None
                            break
                    else:
                        walls = None
                        break

            else:  # right to left
                x_pos = random.choice([random.randint(0, self.width - wall * wall_length), 0, 0, 0])
                # x_pos = 0
                initial_center = x_pos + wall_length // 2
                walls.add(Wall((initial_center, y_pos)))
                for adj_wall in range(wall):
                    if y_pos < self.height - wall_length // 2:
                        if not self._snake.sprite.rect.top - wall_height // 2 <= y_pos \
                               <= self._snake.sprite.rect.bottom + wall_height // 2:
                            initial_center += wall_length
                            if initial_center <= self.width - wall_length // 2:
                                # print(f'x={initial_center}, y={y_pos}')
                                walls.add(Wall((initial_center, y_pos)))
                            else:
                                break
                        else:
                            walls = None
                            break
                    else:
                        walls = None
                        break
            y_pos += random.randint(min_space_between, max_space_between)
            if walls:
                # print(f'len={len(walls)}\n')
                self._wall.append(walls)

    def place_body(self, x_pos, y_pos, direction):
        self._body[0].add(SnakeBody())

        if direction == dir_table['up']:
            self._body[0].sprite.rect.center = (y_pos + self.cell_size, x_pos)
        elif direction == dir_table['down']:
            self._body[0].sprite.rect.center = (y_pos - self.cell_size, x_pos)
        elif direction == dir_table['right']:
            self._body[0].sprite.rect.center = (y_pos, x_pos - self.cell_size)
        elif direction == dir_table['left']:
            self._body[0].sprite.rect.center = (y_pos, x_pos + self.cell_size)

        tmp_rect = self._body[0].sprite.rect
        for _ in range(0, 4):
            tmp = SnakeBody()
            tmp.rect.midright = tmp_rect.midleft
            tmp_rect = tmp.rect
            self._body.append(pygame.sprite.GroupSingle(tmp))

    def check_collision(self):
        if pygame.sprite.groupcollide(self._snake, self._apple, False, True):
            new_block = SnakeBody()
            new_block.rect.center = self._body[len(self._body) - 1].sprite.rect.center
            self._body[len(self._body) - 1].sprite.image.set_alpha(255)
            self._body.append(pygame.sprite.GroupSingle(new_block))

            self.score += 1

        for wall in self._wall:
            if pygame.sprite.groupcollide(self._snake, wall, True, False):
                self._game_over = True


def main():
    s = SnakeGame()
    s.on_execute()


if __name__ == '__main__':
    main()
