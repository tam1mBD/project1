import pygame
import os
import random
pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SOLO RAIDER')

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
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 1

#define player action variables
moving_left = False
moving_right = False
shoot = False


#load images
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

def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))



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
item_box_group=pygame.sprite.Group()
# temp item box
item_box= Iteambox('Health',100,260)
item_box_group.add(item_box)
item_box= Iteambox('Ammo',300,260)
item_box_group.add(item_box)
#using solder class add hero and enemy
player = Soldier('player', 200, 200, 1.65, 5, 20)

enemy = Soldier('enemy', 400, 200, 1.65, 3, 20)
enemy2 = Soldier('enemy', 300, 300, 1.65, 3, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)



run = True
while run:

	clock.tick(FPS)

	draw_bg()
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
	item_box_group.draw(screen)
	bullet_group.draw(screen)


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