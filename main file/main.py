import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import os
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

# ADJUSTABLE DISPLAY SETTINGS - Resizable window
screen_width = 800  # Initial window width
screen_height = 600  # Initial window height
max_screen_width = 1000  # Maximum width (20 columns × 50 pixels)
max_screen_height = 950  # Maximum height (17 rows × 50 pixels + 100 pixels margin)

# Create resizable window
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
score = 0
secret_code = ""  # Track keyboard input for cheat code

# Auto-detect maximum levels by scanning for level files
def get_max_levels():
	"""Automatically detect the highest level number available"""
	max_level = 1
	for i in range(1, 100):  # Check up to 100 levels
		if path.exists(f'level{i}_data'):
			max_level = i
		else:
			break
	return max_level

max_levels = get_max_levels()


#define colours
white = (255, 255, 255)
blue = (0, 0, 255)


class Camera():
	"""Camera system that handles viewport and world-to-screen coordinate conversion"""
	def __init__(self, width, height, world_width, world_height):
		self.width = width  # Camera width (matches screen width)
		self.height = height  # Camera height (matches screen height)
		self.world_width = world_width  # Total world width in pixels
		self.world_height = world_height  # Total world height in pixels
		self.x = 0  # Camera x position in world space
		self.y = 0  # Camera y position in world space
	
	def update(self, target_x, target_y):
		"""
		Update camera to follow target (player), keeping them centered
		Prevents camera from going outside world bounds
		"""
		# Center camera on target
		self.x = target_x - self.width // 2
		self.y = target_y - self.height // 2
		
		# Clamp camera to world bounds
		if self.x < 0:
			self.x = 0
		if self.x + self.width > self.world_width:
			self.x = self.world_width - self.width
		if self.y < 0:
			self.y = 0
		if self.y + self.height > self.world_height:
			self.y = self.world_height - self.height
	
	def apply(self, x, y):
		"""Convert world coordinates to screen coordinates"""
		return (int(x - self.x), int(y - self.y))
	
	def is_in_view(self, rect):
		"""Check if a pygame rect (in world space) is within camera viewport"""
		return not (rect.right < self.x or 
		           rect.left > self.x + self.width or 
		           rect.bottom < self.y or 
		           rect.top > self.y + self.height)


#load images
frontpage_img = pygame.image.load('img/deadpool_game_frontpage.png')
load_background_img = pygame.image.load('img/deadpool head.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
start_hover_img = pygame.image.load('img/start_btn hover .png')
exit_img = pygame.image.load('img/exit_btn.png')
exit_hover_img = pygame.image.load('img/start_btn hover.png')
game_over_img = pygame.image.load('img/game over.png')
winner_img = pygame.image.load('img/winner.png')

# Get all available backgrounds and shuffle them
bg_folder = 'img/background/Untitled design/'
if path.exists(bg_folder):
	available_backgrounds = [f for f in os.listdir(bg_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
	random.shuffle(available_backgrounds)
	bg_index = 0
else:
	available_backgrounds = []
	bg_index = 0

# Function to load background - randomly cycles through available backgrounds
def load_background():
	"""Load a random background from available backgrounds"""
	global bg_index, available_backgrounds
	
	if not available_backgrounds:
		# Fallback to default if no backgrounds found
		return pygame.image.load('img/sky.png')
	
	# Get current background and move to next index
	current_bg = available_backgrounds[bg_index]
	bg_index = (bg_index + 1) % len(available_backgrounds)  # Loop back to start when reaching end
	
	bg_path = path.join(bg_folder, current_bg)
	return pygame.image.load(bg_path)

bg_img = load_background()  # Load initial background

#load sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)
# Hit sound effect for projectile impacts
hit_fx = pygame.mixer.Sound('img/coin.wav')  # Reuse coin sound, can be changed
hit_fx.set_volume(0.3)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#function to reset level
def reset_level(level):
	global bg_img
	#load in level data first
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	else:
		world_data = []
	
	# Load background for this level (randomly selected)
	bg_img = load_background()
	
	# Calculate ground position: world_height - player_height (80px) - ground offset
	world_height = len(world_data) * tile_size if world_data else 20 * tile_size
	ground_y = world_height - 80 - 50
	
	player.reset(100, ground_y)
	blob_group.empty()
	platform_group.empty()
	coin_group.empty()
	lava_group.empty()
	exit_group.empty()

	world = World(world_data)
	#create dummy coin for showing the score
	score_coin = Coin(tile_size // 2, tile_size // 2)
	coin_group.add(score_coin)
	return world, world_data


class Button():
	def __init__(self, x, y, image, hover_image=None):
		self.image = image
		self.hover_image = hover_image if hover_image else image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button with hover effect
		if self.rect.collidepoint(pos):
			screen.blit(self.hover_image, self.rect)
		else:
			screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_UP] == False:
				self.jumped = False
			
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1


			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			if self.rect.y > 200:
				self.rect.y -= 5

		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		# Load idle image first
		img_right = pygame.image.load('img/deadpool char/frame idol_image.png')
		img_right = pygame.transform.scale(img_right, (40, 80))
		img_left = pygame.transform.flip(img_right, True, False)
		self.images_right.append(img_right)
		self.images_left.append(img_left)
		# Load walking animation frames
		for num in range(0, 16):
			img_right = pygame.image.load(f'img/deadpool char/frame_{num:03d}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True
		
		# Health system
		self.max_health = 100
		self.health = self.max_health



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/grass.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size - 6)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
	
	def draw_with_camera(self, camera):
		"""Draw only tiles that are visible in the camera viewport"""
		for tile in self.tile_list:
			# Check if tile is within camera view before drawing
			if camera.is_in_view(tile[1]):
				# Convert world coordinates to screen coordinates
				screen_x, screen_y = camera.apply(tile[1].x, tile[1].y)
				screen.blit(tile[0], (screen_x, screen_y))



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		# Load all alien animation frames
		self.images = []
		for num in range(0, 36):
			img = pygame.image.load(f'img/enemy alien  new/frame_{num:03d}.png')
			img = pygame.transform.scale(img, (60, 60))
			self.images.append(img)
		self.image = self.images[0]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0
		self.animation_index = 0
		self.animation_cooldown = 3

	def update(self):
		# Update position - crab walking movement
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1
		
		# Update animation
		self.animation_index += 1
		if self.animation_index >= len(self.images) * self.animation_cooldown:
			self.animation_index = 0
		self.image = self.images[self.animation_index // self.animation_cooldown]


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1





class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/golden gun .png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


player = Player(100, (20 * tile_size) - 80 - 50)  # Start on ground level at bottom of world

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

#load in level data and create world
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)

# Calculate world dimensions based on level data
world_width = len(world_data[0]) * tile_size  # 20 columns × 50 pixels
world_height = len(world_data) * tile_size    # 20 rows × 50 pixels

# Initialize camera with current screen size and world size
camera = Camera(screen_width, screen_height, world_width, world_height)


#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img, start_hover_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img, exit_hover_img)



run = True
while run:

	clock.tick(fps)

	if main_menu == True:
		# Use frontpage image for main menu - scale to fit display
		frontpage_scaled = pygame.transform.scale(frontpage_img, (screen_width, screen_height))
		screen.blit(frontpage_scaled, (0, 0))
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		# Use game level backgrounds during gameplay - scale to fit display
		bg_scaled = pygame.transform.scale(bg_img, (screen_width, screen_height))
		screen.blit(bg_scaled, (0, 0))
		
		# Apply camera offset to background element
		bg_x, bg_y = camera.apply(100, 100)
		if camera.is_in_view(pygame.Rect(100, 100, 100, 100)):
			screen.blit(load_background_img, (bg_x, bg_y))
		
		# Update camera to follow player
		camera.update(player.rect.centerx, player.rect.centery)
		
		world.draw_with_camera(camera)

		if game_over == 0:
			blob_group.update()
			platform_group.update()
			
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
		draw_text('SCORE: ' + str(score), font_score, white, tile_size - 10, 10)
		
		# Draw level number with proper positioning to ensure visibility
		level_text = f'LEVEL: {level}'
		level_surface = font_score.render(level_text, True, white)
		screen.blit(level_surface, (screen_width - level_surface.get_width() - 20, 10))
		
		# Draw sprites with camera offset
		for blob in blob_group:
			screen_x, screen_y = camera.apply(blob.rect.x, blob.rect.y)
			screen.blit(blob.image, (screen_x, screen_y))
		
		for platform in platform_group:
			screen_x, screen_y = camera.apply(platform.rect.x, platform.rect.y)
			screen.blit(platform.image, (screen_x, screen_y))
		
		for lava in lava_group:
			screen_x, screen_y = camera.apply(lava.rect.x, lava.rect.y)
			screen.blit(lava.image, (screen_x, screen_y))
		
		for coin in coin_group:
			screen_x, screen_y = camera.apply(coin.rect.x, coin.rect.y)
			screen.blit(coin.image, (screen_x, screen_y))
		
		for exit_sprite in exit_group:
			screen_x, screen_y = camera.apply(exit_sprite.rect.x, exit_sprite.rect.y)
			screen.blit(exit_sprite.image, (screen_x, screen_y))

		game_over = player.update(game_over)
		# Draw player with camera offset
		screen_x, screen_y = camera.apply(player.rect.x, player.rect.y)
		screen.blit(player.image, (screen_x, screen_y))

		#if player has died
		if game_over == -1:
			screen.blit(game_over_img, (screen_width // 2 - game_over_img.get_width() // 2, screen_height // 2 - game_over_img.get_height() // 2))
			if restart_button.draw():
				world, world_data = reset_level(level)
				game_over = 0
				score = 0

		#if player has completed the level
		if game_over == 1:
			# Check if this is the final level (level 10)
			if level == 10:
				# Show congratulations screen
				screen.blit(winner_img, (screen_width // 2 - winner_img.get_width() // 2, screen_height // 2 - winner_img.get_height() // 2 - 50))
				if restart_button.draw():
					level = 1
					#reset level
					world, world_data = reset_level(level)
					world_width = len(world_data[0]) * tile_size
					world_height = len(world_data) * tile_size
					camera = Camera(screen_width, screen_height, world_width, world_height)
					game_over = 0
					score = 0
			else:
				#reset game and go to next level
				level += 1
				# Recalculate max levels in case new levels were added
				max_levels = get_max_levels()
				if level <= max_levels:
					#reset level
					world, world_data = reset_level(level)
					world_width = len(world_data[0]) * tile_size
					world_height = len(world_data) * tile_size
					camera = Camera(screen_width, screen_height, world_width, world_height)
					game_over = 0


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		# Handle window resize
		if event.type == pygame.VIDEORESIZE:
			screen_width = event.w
			screen_height = event.h
			screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
			# Update camera to new screen size if camera exists
			if 'camera' in globals():
				camera.width = screen_width
				camera.height = screen_height
		# Track keyboard input for secret cheat codes
		if event.type == pygame.KEYDOWN:
			if event.unicode.isdigit():
				secret_code += event.unicode
				# Keep only last 5 characters
				if len(secret_code) > 5:
					secret_code = secret_code[-5:]
			
			# Check for cheat code: 4321 - Jump to level 10 (final level)
			if secret_code.endswith("4321"):
				# Jump to level 10
				level = 10
				world, world_data = reset_level(level)
				world_width = len(world_data[0]) * tile_size
				world_height = len(world_data) * tile_size
				camera = Camera(screen_width, screen_height, world_width, world_height)
				game_over = 0
				secret_code = ""  # Reset code
			
			# Check for cheat code: 3211 - Jump to next level
			elif secret_code.endswith("3211"):
				# Jump to next level, or back to 1 if on final level
				max_levels = get_max_levels()
				level += 1
				if level > max_levels:
					level = 1
				world, world_data = reset_level(level)
				world_width = len(world_data[0]) * tile_size
				world_height = len(world_data) * tile_size
				camera = Camera(screen_width, screen_height, world_width, world_height)
				game_over = 0
				secret_code = ""  # Reset code

	pygame.display.update()

pygame.quit()