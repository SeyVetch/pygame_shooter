import pygame, os, random, game_data

scale = 1
width = height = 600
screen = pygame.display.set_mode((600, 600))


all_sprites = pygame.sprite.Group()
solid = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
items = pygame.sprite.Group()
players = pygame.sprite.Group()
data_shown = pygame.sprite.Group()


def refresh():
    global all_sprites, solid, projectiles, enemies
    for i in all_sprites:
        i.kill()
        del i
    for i in data_shown:
        i.kill()
        del i
    

refresh()

clock = pygame.time.Clock()
    
FPS = 60

pygame.time.set_timer(31, 1000)
pygame.time.set_timer(30, 900)


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # Ð½Ð°Ñ‡Ð¸Ð½Ð°ÐµÐ¼ Ð¸Ð³Ñ€Ñƒ
        pygame.display.flip()
        clock.tick(FPS)  


def StartGame(WIDTH, HEIGHT, lvl):
    global width, height, player, all_sprites, solid, \
           projectiles, enemies, players, items, data_shown
    
    refresh()
    
    width = WIDTH
    height = HEIGHT
    
    pygame.init()
    
    load_level('level' + str(lvl))
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    player = Player((WIDTH//2, HEIGHT//2), [all_sprites, players])

    running = True
    camera = Camera()
    
    while running:
        z = 1
        
        if pygame.key.get_pressed()[pygame.K_SPACE] == 1:
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == 31:
                for i in enemies:
                    i.AI()
            if event.type == 30:
                player.AI()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    player.items.changeActive(-1)
                elif event.button == 5:
                    player.items.changeActive(1) 
                    
        camera.update(player)
                
        for sprite in all_sprites:
            camera.apply(sprite)
            sprite.update()
        
        player.control()    
        player.items.show()
                
        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        data_shown.draw(screen)
        data_shown.update()
        
        enemies_display()
        
        pygame.display.flip()
        
        clock.tick(FPS)
    
    StartGame(WIDTH, HEIGHT, lvl)


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
    def __init__(self, pos, team, vel=(0, 0, 1)):
        groups = [all_sprites, projectiles]
        super().__init__(groups[0])
        for group in groups[1:]:        
            self.add(group)
        image = load_image('bullet.png')
        self.image = image
        self.mainImage = image
        self.rect = self.image.get_rect().move(pos[0], pos[1])
        c = self.rect.center
        self.image = pygame.transform.scale(self.mainImage, 
                                            (int(self.rect.w*0.6), 
                                             int(self.rect.h*0.6)))
        self.rect.center = c
        self.vel = vel
        self.pos = pos
        self.maxDistance = 300
        self.damage = 20
        self.team = team
        
    
    def update(self):
        x, y = self.rect.x, self.rect.y
        self.image = pygame.transform.scale(self.mainImage, 
                                            (int(self.rect.w*self.vel[2]), 
                                             int(self.rect.h*self.vel[2])))
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
        self.rect = self.image.get_rect()
        self.speed = 1.5
        self.team = 0
        self.health = self.maxHealth = 100 
        self.tile = False
        
    def update(self):
        pass
        
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
                
    def heal(self, hp):
        self.health += hp
        if self.health > self.maxHelath*1.1:
            self.health = self.maxHelath*1.1
                   
                            
class Tile(Entity):
    def __init__(self, pos, t, groups):
        image = image = load_image(os.path.join('tiles', 'tile' + t))
        image = pygame.transform.scale(image, (60, 60))
        super().__init__(image, groups)
        self.rect = self.image.get_rect().move(pos[0], pos[1])   
        self.tile = True
    
    
class Ground(Tile):
    def __init__(self, pos):
        super().__init__(pos, '0.jpg', [all_sprites])
                            
                            
class Pedestal(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'p.png', [all_sprites])                            
                            
                            
class Solid(Tile):
    def __init__(self, pos, n):
        super().__init__(pos, str(game_data.solid[n]) + '.jpg', [all_sprites, solid])
     
     
class Creature(Entity):
    def __init__(self, pos, groups, image):
        super().__init__(image, groups)
        self.frames = []
        self.cut_sheet(image, 3, 1)
        self.cur_frame = 0
        frame = self.frames[self.cur_frame]        
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (60, 60))
        self.rect = self.image.get_rect().move(pos[0], pos[1])  
        self.items = Inventory(self)
        i = Item(game_data.ItemStats['Bgun'], ('onGround', (60, 60)))
        i.showcase.kill()
        self.items.add(i)
        
    def AI(self):
        vel = [0, 0, 1]
        while vel == [0, 0, 1]:
            vel = [random.randint(-1, 1), random.randint(-1, 1), 1]
        self.shoot(vel, 0)
            
    def move(self, vel):
        self.rect.x += vel[0] * self.speed
        self.rect.y += vel[1] * self.speed
        
    def shoot(self, vel, team):
        self.items.use(vel)
        
    def update(self): 
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        frame = self.frames[self.cur_frame]        
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (60, 60))  
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
            self.onDeath()
            
    def onDeath(self):
        self.kill()
        del self        
                            
        
class Player(Creature):
    image = load_image('hero.png')
    def __init__(self, pos, groups):
        super().__init__(pos, groups, Player.image)
        self.team = 1     
        self.vel = 1
        self.items = PlayerInventory(self)
        
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
        if vel != [0, 0, 1] and bool(self.vel):
            self.items.use(vel)
        
    def control(self):
        vel = [0, 0]
        if pygame.key.get_pressed()[pygame.K_a] == 1:
            vel[0] = -1 * self.vel
        if pygame.key.get_pressed()[pygame.K_d] == 1:
            vel[0] = 1 * self.vel
        if pygame.key.get_pressed()[pygame.K_w] == 1:
            vel[1] = -1 * self.vel
        if pygame.key.get_pressed()[pygame.K_s] == 1:
            vel[1] = 1 * self.vel
        self.move(vel)
        
    def onDeath(self):
        self.vel = 0
        
        
class Enemie(Creature):
    def __init__(self, pos, t):
        super().__init__(pos, [all_sprites, solid, enemies], Player.image)
        
 
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
                        Enemie((j*60, i*60), c[1])
                        #e = Entity(load_image('enemy1.png'), [all_sprites, solid, enemies])
                        #e.rect.x, e.rect.y = (j*60, i*60)


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
    def __init__(self, stats, state, parent):
        super().__init__(all_sprites)
        self.add(items)
        self.stats = stats
        self.imageChange(state)
        self.a = 'default'
        self.parent = parent
        
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
        if pygame.sprite.spritecollideany(self, players):
            self.pickup(pygame.sprite.spritecollideany(self, players))
        
    def pickup(self, p):
        p.items.add(self.parent)
        
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
                
                
class InventorySlot(pygame.sprite.Sprite):
    image = [load_image('itemslot.png'), load_image('itemslotActive.png')]
    def __init__(self, n):
        super().__init__(data_shown)
        if n == 0:
            self.image = InventorySlot.image[1]
        else:
            self.image = InventorySlot.image[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = height - 20
        if n == 0:
            self.rect.x = 20
        else:
            self.rect.x = 120 + 20 * n + 60 * (n-1)
        
        
class Inventory:
    def __init__(self, host):
        self.host = host
        self.items = []
        self.inUse = None
        
    def add(self, item):
        if len(self.items) < 6:
            self.items.append(item)
            item.host = self
            self.change()
                
    def change(self):
        if len(self.items) > 0:
            self.inUse = self.items[0]
        else:
            self.inUSe = None
                
    def reset(self):
        for i in items:
            i.reset()
            
    def use(self, data):
        try:
            c = self.inUse.use()
            self.change()
            if c[0] == 'Heal':
                self.host.heal(c[1])
            elif c[0] == 'Shoot':
                Projectile((self.host.rect.x, self.host.rect.y), self.host.team, data)
        except Exception as e:
            pass
                

class PlayerInventory(Inventory):
    def __init__(self, host):
        super().__init__(host)
        self.slots = [InventorySlot(i) for i in range(6)]
        
    def changeActive(self, offset):
        try:
            if offset < 0:
                a = self.items.pop(-1)
                self.items = [a] + self.items
            else:
                a = self.items.pop(0)
                self.items.append(a)
        except:
            pass
        self.show()
        self.change()
        
    def add(self, item):
        super().add(item)
        item.showcase.add(data_shown)
        self.show()
        
    def show(self):
        for i in range(len(self.items)):
            self.items[i].showcase.rect.center = self.slots[i].rect.center
        

class Item:
    def __init__(self, stats, state):
        self.stats = stats
        self.showcase = ItemShowcase(stats, state, self)
        self.host = None
        
    def reset(self):
        try:
            self.host.items.pop(0)
        except:
            pass
        self.showcase.kill()
        del self
        
    def use(self):
        if self.stats['OnUse'][-1]:
            self.host.change()
            self.reset()
        return list(self.stats['OnUse'])[:-1]
        

def enemies_display():
    font = pygame.font.Font(None, 100)
    text = font.render(str(len(enemies)), 1, (255, 0, 0))
    screen.blit(text, (75, 0))    


start_screen()
StartGame(600, 600, 1)