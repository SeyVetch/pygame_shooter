import pygame, os, random, game_data

scale = 1
width = height = 600
screen = pygame.display.set_mode((600, 600))
    
all_sprites = pygame.sprite.Group()
solid = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()

pygame.time.set_timer(31, 1000)
pygame.time.set_timer(30, 900)


def StartGame(WIDTH, HEIGHT):
    global width, height, player, all_sprites, solid, projectiles
    width = WIDTH
    height = HEIGHT
    
    pygame.init()
    
    load_level('level1')
    
    FPS = 60
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    player = Player((WIDTH//2, HEIGHT//2), [all_sprites])

    running = True
    camera = Camera()
    
    while running:
        z = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == 31:
                for i in enemies:
                    i.AI()
            if event.type == 30:
                player.AI()
                    
        camera.update(player)
                
        for sprite in all_sprites:
            camera.apply(sprite)
            sprite.update()
        
        player.control()    
                
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
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
 
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
 
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)

        
        
class Projectile(pygame.sprite.Sprite):
    def __init__(self, groups, pos, team, vel=(0, 0, 1)):
        super().__init__(groups[0])
        for group in groups[1:]:        
            self.add(group)
        image = load_image('bullet.png')
        self.image = image
        self.mainImage = image
        self.rect = self.image.get_rect().move(pos[0], pos[1])
        self.vel = vel
        self.pos = pos
        self.maxDistance = 300
        self.damage = 20
        self.team = team
    
    def update(self):
        x, y = self.rect.x, self.rect.y
        self.image = pygame.transform.scale(self.image, 
                                            (self.rect.w*self.vel[2], self.rect.h*self.vel[2]))
        x += self.vel[0]
        y += self.vel[1]
        self.rect.x, self.rect.y = x, y
        f = pygame.sprite.spritecollideany(self, solid) 
        if f and f.tile:
            self.kill()
        if (x - self.pos[0])**2 + (y - self.pos[1])**2 > (scale * self.maxDistance)**2:
            self.kill()
         
        
class Entity(pygame.sprite.Sprite):
    def __init__(self, image, groups):
        super().__init__(groups[0])
        for group in groups[1:]:        
            self.add(group)
        self.image = image
        self.mainImage = image
        self.rect = self.image.get_rect()
        self.speed = 1.5
        self.team = 0
        self.health = 100 
        self.tile = False
        
    def update(self): 
        if pygame.sprite.spritecollideany(self, solid):
            wall = pygame.sprite.spritecollideany(self, solid)
            if wall != self:
                self.rect.x, self.rect.y = collide(self, wall)
        if pygame.sprite.spritecollideany(self, projectiles):
            p = pygame.sprite.spritecollideany(self, projectiles)
            if p.team != self.team:
                self.health -= p.damage
                p.kill()
        if self.health > 0: 
            pygame.draw.rect(screen, (200, 30, 30), pygame.Rect(self.rect.x, self.rect.y+55, int(self.health*60/100), 7))
        else:
            self.kill()
            del self
            
    def move(self, vel):
        self.rect.x += vel[0] * self.speed
        self.rect.y += vel[1] * self.speed
        
    def shoot(self, vel, team):
        Projectile([all_sprites, projectiles], (self.rect.x, self.rect.y), team, vel)   
        
    def AI(self):
        vel = [0, 0, 1]
        while vel == [0, 0, 1]:
            vel = [random.randint(-1, 1), random.randint(-1, 1), 1]
        self.shoot(vel, 0)
                            
                            
class Tile(Entity):
    def __init__(self, pos, t, groups):
        image = image = load_image(os.path.join('tiles', 'tile' + t))
        image = pygame.transform.scale(image, (60, 60))
        super().__init__(image, groups)
        self.rect = self.image.get_rect().move(pos[0], pos[1])   
        self.tile = True
        
    def update(self):
        pass
    
    
class Ground(Tile):
    def __init__(self, pos):
        super().__init__(pos, '0.jpg', [all_sprites])
                            
                            
class Pedestal(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'p.png', [all_sprites])                            
                            
                            
class Solid(Tile):
    def __init__(self, pos, n):
        super().__init__(pos, str(game_data.solid[n]) + '.jpg', [all_sprites, solid])
                            
        
class Player(Entity):
    image = load_image('player.png')
    def __init__(self, pos, groups):
        super().__init__(Player.image, groups)
        self.rect = self.image.get_rect().move(pos[0], pos[1])
        self.team = 1
        
    def AI(self):
        vel = [0, 0, 1]
        if pygame.key.get_pressed()[pygame.K_LEFT] == 1:
            vel[0] = -1
        if pygame.key.get_pressed()[pygame.K_RIGHT] == 1:
            vel[0] = 1
        if pygame.key.get_pressed()[pygame.K_UP] == 1:
            vel[1] = -1
        if pygame.key.get_pressed()[pygame.K_DOWN] == 1:
            vel[1] = 1
        if vel != [0, 0, 1]:
            self.shoot(vel, 1)
        
    def control(self):
        vel = [0, 0]
        if pygame.key.get_pressed()[pygame.K_a] == 1:
            vel[0] = -1
        if pygame.key.get_pressed()[pygame.K_d] == 1:
            vel[0] = 1
        if pygame.key.get_pressed()[pygame.K_w] == 1:
            vel[1] = -1
        if pygame.key.get_pressed()[pygame.K_s] == 1:
            vel[1] = 1
        self.move(vel)
        
 
def load_level(filename):
    #filename = "data/" + filename
    #with open(filename, 'r') as mapFile:
    #    level_map = [line.strip() for line in mapFile]
    #max_width = max(map(len, level_map)) 
    #lvl = list(map(lambda x: x.ljust(max_width, '0'), level_map))
    lvl = game_data.level[filename]
    for i in range(len(lvl)):
        for j in range(len(lvl[i])):
            b = game_data.tiles[lvl[i][j]]
            for stat in b:
                if stat == 'tile':
                    Ground((j*60, i*60))
                elif stat == 'solid':
                    a = []
                    try: 
                        a.append(game_data.tiles[lvl[i-1][j]][0])
                    except:
                        a.append('solid')
                    try: 
                        a.append(game_data.tiles[lvl[i][j+1]][0])
                    except:
                        a.append('solid')
                    try: 
                        a.append(game_data.tiles[lvl[i+1][j]][0])
                    except:
                        a.append('solid')
                    try: 
                        a.append(game_data.tiles[lvl[i][j-1]][0])
                    except:
                        a.append('solid')
                    Solid((j*60, i*60), tuple(a))
                elif stat == 'pedestal':
                    Pedestal((j*60, i*60))
                elif stat.find(' ') > -1:
                    c = stat.split()
                    if c[0] == 'item':
                        Item(game_data.ItemStats[c[1]], ('onGround', (j*60, i*60)))
                    elif c[0] == 'enemie':
                        #Enemie(c[1])
                        e = Entity(load_image('enemy1.png'), [all_sprites, solid, enemies])
                        e.rect.x, e.rect.y = (j*60, i*60)


def collide(obj, wall):
    x1, y1 = obj.rect.x, obj.rect.y
    x2, y2 = wall.rect.x, wall.rect.y
    x = x2 - x1
    y = y2 - y1
    newx = newy = 0
    a = smallest(- obj.rect.left + wall.rect.right, obj.rect.right - wall.rect.left)
    b = smallest(obj.rect.bottom - wall.rect.top, - obj.rect.top + wall.rect.bottom)
    if abs(a) < abs(b):
        if x < 0:
            newx = -obj.rect.width
        elif x > 0:
            newx = wall.rect.width
        newy = y
    else:
        if y < 0:
            newy = -obj.rect.height
        elif y > 0:
            newy = wall.rect.height
        newx = x
    newx = - newx + wall.rect.x
    newy = - newy + wall.rect.y
    
    return (newx, newy)


def smallest(a, b):
    if a < b:
        return a
    return b


class ItemShowcase(pygame.sprite.Sprite):
    def __init__(self, stats, state):
        super().__init__(all_sprites)
        self.stats = stats
        self.imageChange(state)
        self.a = 'default'
        
    def imageChange(self, state):
        a = state[0]
        if state[0] not in self.stats['ImageStates'].keys():
            a = 'default'
        self.a = a
        name = os.path.join(self.stats['ImageFold'], self.stats['ImageStates'][a][0])
        name = os.path.join('items', name)
        image = load_image(name)
        self.frames = []
        columns, rows = self.stats['ImageStates'][a][2]
        self.cut_sheet(image, columns, rows)
        self.cur_frame = [0, columns * rows]
        frame = self.frames[self.cur_frame[0]]
        n = self.stats['ImageStates'][a][1]
        self.image = pygame.transform.scale(frame, n)
        self.rect = self.image.get_rect()
        n = ((60-n[0])//2, (60-n[1])//2)
        self.rect.x = state[1][0] + n[0]
        self.rect.y = state[1][1] + n[1]
        
    def update(self):
        self.cur_frame[0] += 1
        self.cur_frame[0] %= self.cur_frame[1]
        frame = self.frames[self.cur_frame[0]]
        self.image = pygame.transform.scale(frame, self.stats['ImageStates'][self.a][1])
        x, y = self.rect.centerx, self.rect.centery
        self.rect = self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = x, y 
        
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        

class Item:
    def __init__(self, stats, state):
        self.showcase = ItemShowcase(stats, state)
        


StartGame(600, 600)