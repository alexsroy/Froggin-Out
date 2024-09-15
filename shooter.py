#Created by Alex Roy
import pygame, sys
import time
import random
import os
import csv

from pygame.sprite import Group
from button import Button

pygame.font.init()
pygame.init()

WIDTH = 800
HEIGHT = 800 * 0.8
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

#set framerate
clock = pygame.time.Clock()
#game constants
FPS = 60
GRAVITY = 0.5
SCROLL_THRESH = 150
ROWS = 16
COLS = 150
TILE_SIZE = HEIGHT // ROWS
TILE_TYPES = 21 #TODO correctly set tile types

#screen_scroll = 0

#TODO: fix accessing the screen scroll variable
#STOPPED AT 11:23 part 11

level = 1

#load main menu background
BG = pygame.image.load("img/background/bg_0.png").convert_alpha()
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))

bg_colour = (25, 64, 63)

OPTIONSBG = pygame.image.load("img/background/bg_0.png").convert_alpha()
OPTIONSBG = pygame.transform.scale(OPTIONSBG, (WIDTH, HEIGHT))

#load level background
pine1_img = pygame.image.load("img/background/pine.png").convert_alpha()
sky_img = pygame.image.load("img/background/sky.png").convert_alpha()
mountains_img = pygame.image.load("img/background/mountains.png").convert_alpha()

#play button images
exit_img = pygame.image.load('img/buttons/exit.png').convert_alpha()
restart_img = pygame.image.load('img/buttons/restart.png').convert_alpha()




#load world images into a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/world/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#FINISHED AT 17:48 PART 9 
#TODO: NEED TO FIX World Class
    

#game assets
#red spitball
ball_img = pygame.image.load('img/projectile/ball.png').convert_alpha()
#pesticide
pesticide_img = pygame.image.load('img/projectile/pesticide.png').convert_alpha()
#collectible items
health_box_img = pygame.image.load('img/icons/health_pack.png').convert_alpha()
health_box_img = pygame.transform.scale(health_box_img, (30, 30))
ammo_box_img = pygame.image.load('img/icons/ammo_pack.png').convert_alpha()
ammo_box_img = pygame.transform.scale(ammo_box_img, (30, 30))

pesticide_box_img = pygame.image.load('img/icons/pesticide_pack.png').convert_alpha()
pesticide_box_img = pygame.transform.scale(pesticide_box_img, (30, 30))

item_boxes = {
    'health'    : health_box_img,
    'ammo'      : ammo_box_img,
    'pesticide' : pesticide_box_img
}


PLAYER_WIDTH = 22
PLAYER_HEIGHT = 28
PLAYER_OFFSET = 40
PLAYER_VEL = 2

FONT = pygame.font.SysFont("TimesNewRoman", 30)
BIG_FONT = pygame.font.SysFont("Silkscreen", 40, "Bold")
HUGE_FONT = pygame.font.SysFont("Silkscreen", 100)
DARK_RED = (185, 36, 56)
NORMAL_RED = (220, 40, 40)
EMERALD_GREEN = (80, 200, 120)
GREY_RED = (133, 75, 75)
PURPLE = (43, 13, 45)
BLACK = (20, 20, 20)

pygame.display.set_caption("Shooter Game")

BACK_BUTTON_POS = (WIDTH - 10,10)

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


#define font 
font = pygame.font.SysFont('Futura', 30)
def draw_text(text, font, col, x, y):
    img = font.render(text, True, col)
    SCREEN.blit(img, (x, y))

class Background():
    def __init__(self):
        self.bg_scroll = 0

    def draw_bg(self):
        SCREEN.fill(bg_colour)
        #TODO: fix mountain background alignment
        SCREEN.blit(mountains_img, (0, 0))



class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, pesticides):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.pesticides = pesticides
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.screen_scroll = 0

        self.update_time = pygame.time.get_ticks()

        #ai specific variables
        self.move_counter = 0
        self.line_of_sight = pygame.Rect(0,0, 150, 20)
        self.idling = False
        self.idling_counter = 0


        #load all images for the players
        animation_types = ['idle', 'run', 'death']
        for animation in animation_types:
        #reset temporary list of images
            temp_list = []
            #count number of frames (files) in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                temp = scale
                   
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                scale = temp

                temp_list.append(img)
            self.animation_list.append(temp_list)

        temp_list = []

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    
    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0
        #assign movement variables if moving left/right
        self.screen_scroll = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision
        for tile in world.obstacle_list:
            #check horizontal collision
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if  the ai has hit the wall, then have it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground(jumping)
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground(falling)
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                    
        #check collision with water
                    
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #check if fallen off the map
        if self.rect.bottom + 10 > HEIGHT:
            self.health = 0

        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
                dx = 0


                #update position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player collision
        if self.char_type == 'player':
            if self.rect.right > WIDTH - SCROLL_THRESH or self.rect.left < SCROLL_THRESH:
                self.rect.x -= dx
                player.screen_scroll = -dx
        return player.screen_scroll

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            ball = Ball(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            ball_group.add(ball)
            self.ammo -= 1


    #Stopped at end of Part 8
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,300) == 1:
                self.update_action(0) #0 = idle
                self.idling = True
                self.idling_counter = 40

            #check if the ai sees the player
            if self.line_of_sight.colliderect(player.rect):
                #stop running and face player
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False: 
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    #update ai line of sight as enemy moves
                    self.line_of_sight.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1

                else:
                    self.idling_counter -= 1
                    if self.idling_counter <=0:
                        self.idling = False
        self.rect.x += player.screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        #update image depending on the current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out, reset back to the start
        if self.frame_index > len(self.animation_list[self.action]) - 1:
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else: 
                self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)


    def draw(self):
        SCREEN.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(SCREEN, DARK_RED, self.rect, 1)

class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate through each vlue in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >=9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >=11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)

                    elif tile == 15: #create player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.4, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)

                    elif tile == 16: #create enemies
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.4, 5, 20, 0)
                        enemy_group.add(enemy)

                    elif tile == 17: #create ammo box
                        item_box = ItemBox('health', 100, 300)
                        item_box_group.add(item_box)
    
                    elif tile == 18: #create ammo box
                        item_box2 = ItemBox('ammo', 200, 300)
                        item_box_group.add(item_box2)

                    elif tile == 19:
                        item_box3 = ItemBox('pesticide', 300, 300)
                        item_box_group.add(item_box3)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += player.screen_scroll
            SCREEN.blit(tile[0], tile[1])

        
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calc health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(SCREEN, BLACK, (self.x - 2, self.y - 2, 154, 34))

        pygame.draw.rect(SCREEN, NORMAL_RED, (self.x, self.y, 150, 30))
        pygame.draw.rect(SCREEN, EMERALD_GREEN, (self.x, self.y, 150 * ratio, 30))

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += player.screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += player.screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += player.screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        
        self.rect.x += player.screen_scroll
        #only check if the player picks up box
        pygame.draw.rect(SCREEN, DARK_RED, self.rect, 1)
        
        if pygame.sprite.collide_rect(self, player):
            #check what item picked up
            if self.item_type == "health":
                player.health += 25
                if player.health > player.max_health:
                   player.health = player.max_health
            elif self.item_type == "ammo":
                player.ammo += 15
            elif self.item_type == "pesticide":
                player.pesticides += 3
            #delete item box
            self.kill()
            

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = ball_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    
    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + player.screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, ball_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, ball_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Pesticide(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = pesticide_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            
            #check collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        
        #update grenade position
        self.rect.x += dx + player.screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <=0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.02)
            explosion_group.add(explosion)

            #do damage to nearby frogs
            #TODO: change to closer frogs take more damage
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -=50
            
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -=50

#Finished at start of part 8
                    

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,13):
            img = pygame.image.load(f'img/projectile/explosion/{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += player.screen_scroll
        EXPLOSION_SPEED = 4
        #update explosion animation
        self.counter += 1
        
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >=len(self.images):
                self.kill()
            else: self.image = self.images[self.frame_index]




enemy_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
pesticide_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#create empty tile list
world_data = []
for row in range(ROWS): 
    r = [-1] * COLS
    world_data.append(r)

#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)
   
def play():
    #define player action variables
    moving_left = False
    moving_right = False
    shoot = False
    pesticide = False
    pesticide_thrown = False
    run  = True
    SCREEN.fill("black")

    #new code for scroller
    while run:
        clock.tick(FPS)
        #draw background
        background = Background()
        background.draw_bg()
        #draw world map
        world.draw()
        health_bar.draw(player.health)

        draw_text(f'Ammo: ', font, DARK_RED, 10, 35)
        for x in range(player.ammo):
            SCREEN.blit(ball_img, (110 + (x * 10), 55))

        draw_text(f'Pesticides: ', font, DARK_RED, 10, 60)
        for x in range(player.pesticides):
            SCREEN.blit(pesticide_img, (140 + (x * 15), 60))


        #SCREEN.fill("black")

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        ball_group.update()
        pesticide_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        ball_group.draw(SCREEN)
        pesticide_group.draw(SCREEN)
        explosion_group.draw(SCREEN)
        item_box_group.draw(SCREEN)
        decoration_group.draw(SCREEN)
        water_group.draw(SCREEN)
        exit_group.draw(SCREEN)
        
        if player.alive: 
            if shoot:
                player.shoot()
            #throw pesticide
            elif pesticide and pesticide_thrown == False and player.pesticides > 0:
                pesticide = Pesticide(player.rect.centerx + (0.5 + player.rect.size[0] * player.direction), player.rect.top, player.direction)
                
                player.pesticides -=1
                pesticide_thrown = True
                pesticide_group.add(pesticide)
            #woooo
            #make jumping animation
            #if player.in_air:
              #  player.update_action(2)
            if moving_left or moving_right:
                player.update_action(1) #1 means run


            else:
                player.update_action(0)
               # restart_button.update(SCREEN)
                #exit_button.update(SCREEN)
                
            if not player.alive:
                restart_button = Button(image=None, pos=(WIDTH/2, 300), text_input="RESTART", font=BIG_FONT, base_color=EMERALD_GREEN, hovering_color=NORMAL_RED)
                exit_button = Button(image=None, pos=(WIDTH/2, 500), text_input="EXIT", font=BIG_FONT, base_color=DARK_RED, hovering_color=NORMAL_RED)
                
               



            player.screen_scroll = player.move(moving_left, moving_right)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
                #FIX BUTTONS

            if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.checkForInput(pygame.mouse.get_pos()):
                        play()
                    if exit_button.checkForInput(pygame.mouse.get_pos()):
                        main_menu()



        #key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_x:
                    pesticide = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                if event.key == pygame.K_ESCAPE:
                    main_menu()
        #key button released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_x:
                    pesticide = False
                    pesticide_thrown = False
            
        pygame.display.update()


def options():
    while True:
        global num_stars
        global star_add_increment
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(OPTIONSBG, (0,0))

        OPTIONS_TEXT = get_font(45).render("OPTIONS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(WIDTH/2, 300))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        EASYDIFF = Button(image=None, pos=(WIDTH/2, 375), 
                            text_input="EASY", font=BIG_FONT, base_color=DARK_RED, hovering_color=NORMAL_RED)
        MEDDIFF = Button(image=None, pos=(WIDTH/2, 450), 
                            text_input="MEDIUM", font=BIG_FONT, base_color=DARK_RED, hovering_color=NORMAL_RED)
        HARDDIFF = Button(image=None, pos=(WIDTH/2, 525), 
                            text_input="HARD", font=BIG_FONT, base_color=DARK_RED, hovering_color=NORMAL_RED)
        OPTIONS_BACK = Button(image=None, pos=(WIDTH/2, 625), 
                            text_input="BACK", font=BIG_FONT, base_color=DARK_RED, hovering_color=NORMAL_RED)
        
        for button in [EASYDIFF, MEDDIFF, HARDDIFF, OPTIONS_BACK]:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
                if EASYDIFF.checkForInput(OPTIONS_MOUSE_POS):
                    num_stars = 3
                    star_add_increment = 1400
                if MEDDIFF.checkForInput(OPTIONS_MOUSE_POS):
                    num_stars = 4
                    star_add_increment = 1200
                if HARDDIFF.checkForInput(OPTIONS_MOUSE_POS):
                    star_add_increment = 1000
                    num_stars = 5

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = HUGE_FONT.render("Froggin Out", True, BLACK)
        MENU_RECT = MENU_TEXT.get_rect(center=(WIDTH/2, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(WIDTH/2, 250), 
                            text_input="PLAY", font=HUGE_FONT, base_color= DARK_RED, hovering_color=NORMAL_RED)
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(WIDTH/2, 400), 
                            text_input="OPTIONS", font=HUGE_FONT, base_color= DARK_RED, hovering_color=NORMAL_RED)
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(WIDTH/2, 550), 
                            text_input="QUIT", font=HUGE_FONT, base_color= DARK_RED, hovering_color=NORMAL_RED)

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()