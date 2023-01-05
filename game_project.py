import pygame
import os
import random
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SOLO RAIDER')

#load images
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

#create function for drawing background
def draw_bag():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(4):
		screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


#lODING BIRD IMAGE
birds= [pygame.image.load(os.path.join("img/birds", "1.png")),
        pygame.image.load(os.path.join("img/birds", "2.png")),
        pygame.image.load(os.path.join("img/birds", "3.png")),
        pygame.image.load(os.path.join("img/birds", "4.png")),
        pygame.image.load(os.path.join("img/birds", "5.png"))]
#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
ROWS = 16
COLS = 150
scroll = 0
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 1

#define player action variables
moving_left = False
moving_right = False
shoot = False


#load images
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# pick up boxes
heal_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
item_boxes={
	'Health': heal_box_img,
	'Ammo' : ammo_box_img
}
#define colours
BG = (14, 50, 50)
RED = (255, 0, 0)
WHITE=(255, 255, 255)

font= pygame.font.SysFont('futura',30)
#for showing heatlh and ammo status
def draw_text(text, font, color, x, y):
	img=font.render(text, True, color)
	screen.blit(img,(x,y))

# def draw_bg():
# 	screen.fill(BG)
# 	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))



class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
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
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#variables odf ai
		self.move_counter =0
		self.idling= False
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling_counter=0
		#load all images for the players
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			#reset temporary list of images
			temp_list = []
			#count number of files in the folder
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		#reset movement variables
		dx = 0
		dy = 0

		#assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		#apply gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check collision with floor
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_air = False

		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy


	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1

	def ai(self):
		if self.alive and player.alive:
			if random.randint(1,200)==5 and self.idling== False:
				self.update_action(0) # standing animation
				self.idling= True
				self.idling_counter =50
			#Check if hero is near to enemy
			if self.vision.colliderect(player.rect):
				#stop and shot
				self.update_action(0) # idle
				self.shoot()
			else:
				if self.idling == False:
					if self.direction ==1:
						ai_moving_right= True
					else:
						ai_moving_right = False
					ai_moving_left =not ai_moving_right
					self.move(ai_moving_left,ai_moving_right)
					self.update_action(1)# for run
					self.move_counter +=1
					#Ai hero detection
					self.vision.center=(self.rect.centerx +75* self.direction, self.rect.centery)
					#pygame.draw.rect(screen,RED,self.vision)
					if self.move_counter>TILE_SIZE:
						self.direction *=-1
						self.move_counter *=-1
				else:
					self.idling_counter -=1
					if self.idling_counter <=0:
						self.idling= False


	def update_animation(self):
		#update animation
		ANIMATION_COOLDOWN = 100
		#update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >=0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					# elif tile >=9 and tile <= 10:
					# 	water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
					# 	water_group.add(water)
					# elif tile >= 11 and tile <= 14:
					# 	decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
					# 	decoration_group.add(decoration)
					elif tile == 15: #create player
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20)
					elif tile == 16: #create enemies
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 3, 20)
						enemy_group.add(enemy)
					elif tile == 17: # create ammo box
						item_box = Iteambox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19: #create health box
						item_box = Iteambox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20: #create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
		return player
	def draw(self):
		for tile in self.obstacle_list:
			screen.blit(tile[0], tile[1])

# class Decoration(pygame.sprite.Sprite):
# 	def __init__(self, img, x, y):
# 		pygame.sprite.Sprite.__init__(self)
# 		self.image = img
# 		self.rect = self.image.get_rect()
# 		self.rect.midtop = ((x + TILE_SIZE) // 2, y + (TILE_SIZE - self.image.get_height()))

# class Water(pygame.sprite.Sprite):
# 	def __init__(self, img, x, y):
# 		pygame.sprite.Sprite.__init__(self)
# 		self.image = img
# 		self.rect = self.image.get_rect()
# 		self.rect.midtop = (x + TILE_SIZE) // 2, y + (TILE_SIZE - self.image.get_height())

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE) // 2, y + (TILE_SIZE - self.image.get_height())


class Iteambox(pygame.sprite.Sprite):
	def __init__(self,item_type,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image=item_boxes[self.item_type]
		self.rect=self.image.get_rect()
		self.rect.midtop= (x +TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
	def update(self):
		#check if the player has picked up  boxes
		if pygame.sprite.collide_rect(self,player):
			#type of box
			if self.item_type =='Health':
				player.health +=25
				#maintain max health
				if player.health >=100:
					player.health=100
			#for ammo
			elif self.item_type =='Ammo':
				player.ammo +=25
				#maintain max health
				if player.ammo >=50:
					player.health=50

			print(player.health)
			self.kill()
class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed)
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		if pygame.sprite.spritecollide(enemy, bullet_group, False):
			if enemy.alive:
				enemy.health -= 25
				self.kill()
#class for flying bird
class cl_bird:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.stepIndex=1
    def step(self):
        if self.stepIndex >16:
            self.stepIndex =1
    def draw(self,win):
        self.step()
        #print(self.stepIndex)
        win.blit(birds[self.stepIndex//4 ],(self.x, self.y))
        self.stepIndex +=1
    def fly(self):
        self.x +=5
        if self.x==820:
            self.x=0
# Draw Game


pygame.time.delay(30)
pygame.display.update()
#instance of bird
birds_list=[]

#create sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
# decoration_group = pygame.sprite.Group()
# water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
# temp item box

#using solder class add hero and enemy


#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player = world.process_data(world_data)

run = True
while run:

	clock.tick(FPS)
	#update background
	#draw_bg()
	draw_bag()
	#draw world map
	world.draw()
	#show ammo
	draw_text(f'AMM0: {player.ammo}' , font, WHITE, 10, 35 )
	draw_text(f'HEALTH: {player.health}', font, WHITE, 10, 10)

	player.update()
	player.draw()

	# bird motoin
	if len(birds_list) == 0:
		bird = cl_bird(0, 120)
		bird1 = cl_bird(35, 140)
		birds_list.append(bird)
		birds_list.append(bird1)
	for bird in birds_list:
		bird.fly()
	for bird in birds_list:
		bird.draw(screen)
		bird1.draw(screen)
	for enemy in enemy_group:
		enemy.update()
		enemy.draw()
		enemy.ai()

	#update and draw groups
	bullet_group.update()
	item_box_group.update()
	# decoration_group.update()
	# water_group.update()
	exit_group.update()
	item_box_group.draw(screen)
	bullet_group.draw(screen)
	# decoration_group.draw(screen)
	# water_group.draw(screen)
	exit_group.draw(screen)


	#update player actions
	if player.alive:
		#shoot bullets
		if shoot:
			player.shoot()
		if player.in_air:
			player.update_action(2)#2: jump
		elif moving_left or moving_right:
			player.update_action(1)#1: run
		else:
			player.update_action(0)#0: idle
		player.move(moving_left, moving_right)


	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False


	pygame.display.update()

pygame.quit()
