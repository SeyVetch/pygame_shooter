import pygame, os

scale = 1
width = height = 600
screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)


def StartGame(WIDTH, HEIGHT):
    global width, height, player
    width = WIDTH
    height = HEIGHT
    
    pygame.init()
    
    FPS = 60
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    
    all_sprites = pygame.sprite.Group()
    
    player = Player((WIDTH//2, HEIGHT//2), [all_sprites])
    tile = Entity(load_image('tile.png'), [all_sprites])

    running = True
    fullScreen = False
    camera = Camera()
    
    while running:
        z = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.VIDEORESIZE:
                camera.zoomFix(WIDTH, HEIGHT, event.w, event.h, all_sprites, player)
                WIDTH = event.w
                HEIGHT = event.h
                if not fullScreen:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN + pygame.HWSURFACE) 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    z = 0.4
                elif event.button == 4:
                    z = 1/0.4
                
        for sprite in all_sprites:
            camera.apply(sprite)
            camera.update(player)
            camera.zoom(z, sprite, player)
            sprite.update()

        if pygame.key.get_pressed()[pygame.K_f] == 1:
            if fullScreen:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            else:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN + pygame.HWSURFACE)
            fullScreen = not fullScreen
        
        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
    
        clock.tick(FPS)
    
    pygame.quit()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.offx = 0
        self.offy = 0
        
    def zoomFix(self, W, H, w, h, group, target):
        global scale
        if W > H:
            a = H
        else:
            a = W
        a = a
        if w > h:
            b = h
        else:
            b = w
        b = (w - b, h - b, b)
        if b[0] == 0 and b[1] != 0:
            self.offx = 0
            self.offy = b[2]
        elif b[0] != 0 and b[1] == 0:
            self.offy = 0
            self.offx = b[2]
        else:
            self.offx = 0
            self.offy = 0
        z = b[2]/a
        scale *= z
        for sprite in group:
            self.zoom(scale, sprite, target)
        
 
    def apply(self, obj):
        obj.rect.x += self.dx + self.offx
        obj.rect.y += self.dy + self.offy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        
    def zoom(self, val, obj, target):
        x = player.rect.x - obj.rect.x
        y = player.rect.y - obj.rect.y
        x *= val
        y *= val
        obj.image = pygame.transform.scale(obj.image, (int(obj.rect.w*val), int(obj.rect.h*val)))
        obj.rect = obj.image.get_rect()
        obj.rect.x += x
        obj.rect.y += y
        
        
class Projectile(pygame.sprite.Sprite):
    def __init__(self, groups, pos, image, vel=(0, 0, 1)):
        super().__init__(groups[0])
        for group in groups[1:]:        
            self.add(group)
        self.image = image
        self.rect = self.image.get_rect().move(pos[0], pos[1])
        self.vel = vel
        self.pos = pos
        self.maxDistance = 300
    
    def update(self):
        x, y = self.rect.x, self.rect.y
        self.image = pygame.transform.scale(self.image, (self.rect.w*vel[2], self.rect.h*vel[2]))
        x += vel[0]
        y += vel[1]
        self.rect.x, self.rect.y = x, y
        if (x - self.pos[0])**2 + (y - self.pos[1])**2 > (scale * self.maxDistance)**2:
            self.kill()
         
        
class Entity(pygame.sprite.Sprite):
    def __init__(self, image, groups):
        super().__init__(groups[0])
        for group in groups[1:]:        
            self.add(group)
        self.image = image
        self.rect = self.image.get_rect()
        
    def update(self):
        pass
                 
        
class Player(Entity):
    image = load_image('player.png')
    def __init__(self, pos, groups):
        super().__init__(Player.image, groups)
        self.rect = self.image.get_rect().move(pos[0], pos[1])
        
 
def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


StartGame(600, 600)