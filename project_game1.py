import os
import sys
import pygame

pygame.init()
pygame.key.set_repeat(200, 70)
FPS = 60
WIDTH = 1000
width = 1000
HEIGHT = 700
height = 700
STEP = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_group2 = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ['']

    fon = pygame.transform.scale(load_image('fon2.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
            pygame.display.flip()
            clock.tick(FPS)


def load_level(filename):
    filename = 'data/' + filename
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
            elif level[y][x] == 'o':
                Tile('empty', x, y)
                new_player2 = Player2(x, y)
    return new_player, new_player2, x, y


def draw():
    pygame.draw.line(screen, (255, 255, 255), (300, 5), (width - 300, 5), 1)
    pygame.draw.line(screen, (255, 255, 255), (300, height - 5), (width - 300, height - 5), 1)
    pygame.draw.line(screen, (255, 255, 255), (300, 5), (300, height - 5), 1)
    pygame.draw.line(screen, (255, 255, 255), (width - 300, 5), (width - 300, height - 5), 1)


start_screen()
tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
player_image = load_image('player.png')
player_image2 = load_image('player1.png')
tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


class Player2(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group2, all_sprites)
        self.image = player_image2
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y - 35)


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y):
        super().__init__(ball_group, all_sprites)
        self.radius = radius
        self.x = x
        self.y = y
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("pink"), (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = 3
        self.vy = 3
        self.pl1 = 0
        self.pl2 = 0
        self.win = ''

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        count_game1 = pygame.font.Font(None, 50).render('Счёт', True, (255, 255, 255))
        count_game = pygame.font.Font(None, 50).render(str(self.pl1) + ' : ' + str(self.pl2), True, (255, 255, 255))
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            if self.vy > 0:
                self.pl1 += 1
                self.rect = pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)
            else:
                self.pl2 += 1
                self.rect = pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)
            self.vy = -self.vy
        elif pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        elif pygame.sprite.spritecollideany(self, player_group):
            self.vy = -self.vy
        elif pygame.sprite.spritecollideany(self, player_group2):
            self.vy = -self.vy
        screen.blit(count_game1, (90, 60))
        screen.blit(count_game, (100, 100))


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


Border(300, 5, width - 300, 5)
Border(300, height - 5, width - 300, height - 5)
Border(300, 5, 300, height - 5)
Border(width - 300, 5, width - 300, height - 5)
Ball(15, 500, 350)
player, player2, level_x, level_y = generate_level(load_level('level1.txt'))

running = True
PAUSED = False
text_paused = pygame.font.Font(None, 50).render("PAUSED", True, (255, 0, 0))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_q:
                PAUSED = not PAUSED
            elif event.key == pygame.K_SPACE:
                pygame.display.iconify()

        if not PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    if player.rect.x == 275:
                        player.rect.x = 645
                    else:
                        player.rect.x -= STEP
                elif event.key == pygame.K_d:
                    if player.rect.x == 645:
                        player.rect.x = 275
                    else:
                        player.rect.x += STEP
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if player2.rect.x == 275:
                        player2.rect.x = 645
                    else:
                        player2.rect.x -= STEP
                elif event.key == pygame.K_RIGHT:
                    if player2.rect.x == 645:
                        player2.rect.x = 275
                    else:
                        player2.rect.x += STEP
    if PAUSED:
        screen.blit(text_paused, (450, 300))
        pygame.display.flip()
    elif pygame.display.get_active():
        screen.fill(pygame.Color(0, 0, 0))
        all_sprites.draw(screen)
        player_group.draw(screen)
        player_group2.draw(screen)
        ball_group.draw(screen)
        ball_group.update()
        draw()
        pygame.display.flip()
        clock.tick(FPS)
    else:
        PAUSED = True
terminate()
