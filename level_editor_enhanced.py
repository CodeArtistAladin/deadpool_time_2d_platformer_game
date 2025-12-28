import pygame
import pickle
from os import path, listdir
import copy

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Game window
tile_size = 50
cols = 20
margin = 100
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption('Level Editor - Enhanced with Player Preview')

# Load images
sun_img = pygame.image.load('img/deadpool head.png')
bg_img = pygame.image.load('img/sky.png')
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')
platform_x_img = pygame.image.load('img/platform_x.png')
platform_y_img = pygame.image.load('img/platform_y.png')
lava_img = pygame.image.load('img/lava.png')
coin_img = pygame.image.load('img/golden gun .png')
exit_img = pygame.image.load('img/exit.png')

# Load player images
try:
	player_img = pygame.image.load('img/deadpool char/frame idol_image.png')
	player_img = pygame.transform.scale(player_img, (40, 80))
	player_img_loaded = True
except:
	player_img = None
	player_img_loaded = False
	print("ERROR: Could not load player image")

# Load game element images
enemy_images = []
try:
	# Load alien enemy animation frames
	for num in range(0, 36):
		img = pygame.image.load(f'img/enemy alien  new/frame_{num:03d}.png')
		img = pygame.transform.scale(img, (60, 60))
		enemy_images.append(img)
except:
	print("ERROR: Could not load alien enemy images")

try:
	platform_img = pygame.image.load('img/platform.png')
	lava_img_single = pygame.image.load('img/lava.png')
	coin_img_single = pygame.image.load('img/golden gun .png')
	exit_img_single = pygame.image.load('img/exit.png')
except:
	print("ERROR: Could not load game element images")

# Game variables
clicked = False
level = 1
level_name = f"level{level}"
dragging = False
last_tile_pos = None
show_file_browser = False
selected_file_index = 0
available_levels = []

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

# Undo/Redo functionality
undo_stack = []
redo_stack = []
max_undo_steps = 50

# Text input for filename
input_active = False
input_text = ""

# Preview mode toggle
preview_mode = False
preview_enemies = []
preview_platforms = []
preview_coins = []
preview_lava = []
preview_exits = []
preview_initial_data = None

# Game element classes for preview mode
class PreviewEnemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = enemy_images
		self.image = self.images[0]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0
		self.initial_x = x
		self.animation_index = 0
		self.animation_cooldown = 3

	def update(self):
		# Update position
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

	def reset(self):
		self.rect.x = self.initial_x
		self.move_direction = 1
		self.move_counter = 0
		self.animation_index = 0

class PreviewPlatform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(platform_img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y
		self.initial_x = x
		self.initial_y = y

	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

	def reset(self):
		self.rect.x = self.initial_x
		self.rect.y = self.initial_y
		self.move_direction = 1
		self.move_counter = 0

class PreviewLava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(lava_img_single, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class PreviewCoin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(coin_img_single, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

class PreviewExit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(exit_img_single, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

# Player variables for editor
class EditorPlayer:
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		self.direction = 1
		
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
		
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.in_air = True
	
	def update(self, world_data):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20
		
		# Get keypresses
		key = pygame.key.get_pressed()
		if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
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
		
		# Handle animation
		if self.counter > walk_cooldown:
			self.counter = 0
			self.index += 1
			if self.index >= len(self.images_right):
				self.index = 0
			if self.direction == 1:
				self.image = self.images_right[self.index]
			if self.direction == -1:
				self.image = self.images_left[self.index]
		
		# Add gravity
		self.vel_y += 1
		if self.vel_y > 10:
			self.vel_y = 10
		dy += self.vel_y
		
		# Check for collision in x direction
		self.in_air = True
		for row in range(20):
			for col in range(20):
				if world_data[row][col] > 0:
					tile_rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
					
					# Check collision in x direction
					if tile_rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
						dx = 0
					
					# Check collision in y direction
					if tile_rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
						# Check if below the ground (jumping)
						if self.vel_y < 0:
							dy = tile_rect.bottom - self.rect.top
							self.vel_y = 0
						# Check if above the ground (falling)
						elif self.vel_y >= 0:
							dy = tile_rect.top - self.rect.bottom
							self.vel_y = 0
							self.in_air = False
		
		# Update player coordinates
		self.rect.x += dx
		self.rect.y += dy
		
		# Keep player in bounds
		if self.rect.y > 1000:
			self.rect.y = 0
	
	def draw(self):
		screen.blit(self.image, (self.rect.x, self.rect.y))
		# Draw yellow border for visibility
		pygame.draw.rect(screen, (255, 255, 0), (self.rect.x, self.rect.y, self.width, self.height), 3)

player = EditorPlayer(100, 700)

# Colors
white = (255, 255, 255)
green = (144, 201, 120)
blue = (100, 150, 255)
dark_gray = (50, 50, 50)
light_gray = (200, 200, 200)
red = (255, 0, 0)

font = pygame.font.SysFont('Futura', 24)
font_small = pygame.font.SysFont('Futura', 18)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

# Create empty tile list
world_data = []
for row in range(20):
	r = [0] * 20
	world_data.append(r)

# Create boundary
for tile in range(0, 20):
	world_data[19][tile] = 2
	world_data[0][tile] = 1
	world_data[tile][0] = 1
	world_data[tile][19] = 1

undo_stack.append(copy.deepcopy(world_data))

def get_level_files():
	files = []
	try:
		for f in listdir('.'):
			if f.startswith('level') and f.endswith('_data'):
				files.append(f)
		files.sort()
	except:
		pass
	return files

def draw_grid():
	for c in range(21):
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))

def draw_world():
	for row in range(20):
		for col in range(20):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				elif world_data[row][col] == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				elif world_data[row][col] == 3:
					img = pygame.transform.scale(enemy_images[0], (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				elif world_data[row][col] == 4:
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				elif world_data[row][col] == 5:
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				elif world_data[row][col] == 6:
					img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				elif world_data[row][col] == 7:
					img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				elif world_data[row][col] == 8:
					img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))

def save_state():
	global undo_stack, redo_stack
	undo_stack.append(copy.deepcopy(world_data))
	if len(undo_stack) > max_undo_steps:
		undo_stack.pop(0)
	redo_stack.clear()

def undo():
	global world_data, undo_stack, redo_stack
	if len(undo_stack) > 1:
		redo_stack.append(copy.deepcopy(world_data))
		undo_stack.pop()
		world_data = copy.deepcopy(undo_stack[-1])

def redo():
	global world_data, redo_stack, undo_stack
	if redo_stack:
		undo_stack.append(copy.deepcopy(world_data))
		world_data = copy.deepcopy(redo_stack.pop())

def save_level():
	global input_active, input_text
	input_active = True
	input_text = level_name

def draw_input_box():
	box_width = min(400, screen_width - 40)
	box_height = 150
	box_x = (screen_width - box_width) // 2
	box_y = (screen_height - box_height) // 2
	
	pygame.draw.rect(screen, dark_gray, (box_x, box_y, box_width, box_height))
	pygame.draw.rect(screen, white, (box_x, box_y, box_width, box_height), 2)
	
	draw_text("Save As:", font, white, box_x + 20, box_y + 20)
	
	input_box_rect = pygame.Rect(box_x + 20, box_y + 60, box_width - 40, 40)
	pygame.draw.rect(screen, light_gray, input_box_rect)
	pygame.draw.rect(screen, white, input_box_rect, 2)
	
	draw_text(input_text, font, dark_gray, box_x + 25, box_y + 68)
	
	draw_text("Press ENTER to save, ESC to cancel", font_small, white, box_x + 20, box_y + 115)

def draw_file_browser():
	browser_width = 300
	browser_height = 400
	browser_x = (screen_width - browser_width) // 2
	browser_y = (screen_height - browser_height) // 2
	
	pygame.draw.rect(screen, dark_gray, (browser_x, browser_y, browser_width, browser_height))
	pygame.draw.rect(screen, white, (browser_x, browser_y, browser_width, browser_height), 2)
	
	draw_text("SELECT LEVEL TO LOAD", font, white, browser_x + 20, browser_y + 10)
	
	for i, level_file in enumerate(available_levels):
		y_pos = browser_y + 50 + (i * 30)
		
		if i == selected_file_index:
			pygame.draw.rect(screen, blue, (browser_x + 10, y_pos, browser_width - 20, 25))
			draw_text(f"> {level_file}", font_small, white, browser_x + 20, y_pos + 3)
		else:
			draw_text(level_file, font_small, light_gray, browser_x + 20, y_pos + 3)
	
	draw_text("UP/DOWN: Navigate | ENTER: Load | ESC: Cancel", font_small, light_gray, browser_x - 50, browser_y + browser_height + 20)

def enable_preview_mode():
	"""Activate preview mode - load all game elements"""
	global preview_mode, preview_enemies, preview_platforms, preview_coins, preview_lava, preview_exits, preview_initial_data
	preview_mode = True
	preview_initial_data = copy.deepcopy(world_data)
	preview_enemies.clear()
	preview_platforms.clear()
	preview_coins.clear()
	preview_lava.clear()
	preview_exits.clear()
	
	# Create all game elements from world_data
	for row in range(20):
		for col in range(20):
			tile = world_data[row][col]
			x = col * tile_size
			y = row * tile_size
			
			if tile == 3:  # Enemy
				enemy = PreviewEnemy(x, y)
				preview_enemies.append(enemy)
			elif tile == 4:  # Horizontal moving platform
				platform = PreviewPlatform(x, y, 1, 0)
				preview_platforms.append(platform)
			elif tile == 5:  # Vertical moving platform
				platform = PreviewPlatform(x, y, 0, 1)
				preview_platforms.append(platform)
			elif tile == 6:  # Lava
				lava = PreviewLava(x, y + (tile_size // 2))
				preview_lava.append(lava)
			elif tile == 7:  # Coin
				coin = PreviewCoin(x + (tile_size // 2), y + (tile_size // 2))
				preview_coins.append(coin)
			elif tile == 8:  # Exit
				exit = PreviewExit(x, y - (tile_size // 2))
				preview_exits.append(exit)

def disable_preview_mode():
	"""Deactivate preview mode and reset all elements"""
	global preview_mode
	preview_mode = False
	
	# Reset all enemies and platforms
	for enemy in preview_enemies:
		enemy.reset()
	for platform in preview_platforms:
		platform.reset()

def update_preview_elements():
	"""Update all moving elements in preview mode"""
	for enemy in preview_enemies:
		enemy.update()
	for platform in preview_platforms:
		platform.update()

def draw_preview_elements():
	"""Draw all preview elements on screen"""
	# Draw lava
	for lava in preview_lava:
		screen.blit(lava.image, (lava.rect.x, lava.rect.y))
	
	# Draw platforms
	for platform in preview_platforms:
		screen.blit(platform.image, (platform.rect.x, platform.rect.y))
	
	# Draw enemies
	for enemy in preview_enemies:
		screen.blit(enemy.image, (enemy.rect.x, enemy.rect.y))
	
	# Draw coins
	for coin in preview_coins:
		screen.blit(coin.image, (coin.rect.center[0] - coin.rect.width // 2, coin.rect.center[1] - coin.rect.height // 2))
	
	# Draw exits
	for exit in preview_exits:
		screen.blit(exit.image, (exit.rect.x, exit.rect.y))

# Main loop
run = True
while run:
	clock.tick(fps)
	
	screen_width, screen_height = screen.get_size()
	
	sun_scaled = pygame.transform.scale(sun_img, (tile_size, tile_size))
	bg_scaled = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
	
	screen.fill(green)
	screen.blit(bg_scaled, (0, 0))
	screen.blit(sun_scaled, (tile_size * 2, tile_size * 2))
	
	if input_active:
		draw_grid()
		draw_world()
		draw_input_box()
	elif show_file_browser:
		draw_grid()
		draw_world()
		draw_file_browser()
	else:
		draw_grid()
		draw_world()
		
		# Update and draw preview elements if preview mode is active
		if preview_mode:
			update_preview_elements()
			draw_preview_elements()
		
		player.update(world_data)
		player.draw()
		
		# Draw tile palette/toolbar at bottom
		palette_y = screen_height - margin + 5
		palette_items = [
			("0: Empty", white),
			("1: Dirt", white),
			("2: Grass", white),
			("3: Enemy", white),
			("4: Plat-H", white),
			("5: Plat-V", white),
			("6: Lava", white),
			("7: Coin", white),
			("8: Exit", white)
		]
		
		palette_x = 10
		for label, color in palette_items:
			draw_text(label, font_small, color, palette_x, palette_y)
			palette_x += 130
			if palette_x > screen_width - 150:
				palette_x = 10
				palette_y += 25
		
		draw_text(f'File: {level_name}', font, white, tile_size, screen_height - 90)
		draw_text('Ctrl+S: Save | Ctrl+Z: Undo | Ctrl+Y: Redo | L: Load | P: Preview', font_small, white, tile_size, screen_height - 65)
		draw_text('Left Click: Next Block | Right Click: Prev Block | LEFT/RIGHT: Move | UP: Jump | ESC: Close', font_small, white, tile_size, screen_height - 40)
		
		undo_info_text = f'Undo: {len(undo_stack)-1} | Redo: {len(redo_stack)}'
		undo_surface = font_small.render(undo_info_text, True, white)
		screen.blit(undo_surface, (screen_width - undo_surface.get_width() - 20, screen_height - 90))
		
		preview_status = "Preview: ON" if preview_mode else "Preview: OFF"
		preview_color = (0, 255, 0) if preview_mode else (255, 0, 0)
		draw_text(preview_status, font_small, preview_color, screen_width - 200, screen_height - 40)
		
		draw_text(f'Player: X={int(player.rect.x)} Y={int(player.rect.y)}', font_small, white, screen_width - 250, screen_height - 65)
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		
		if event.type == pygame.VIDEORESIZE:
			screen_width = event.w
			screen_height = event.h
			screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
		
		if input_active:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					level_name = input_text if input_text else f"level{level}"
					pickle_out = open(f'{level_name}_data', 'wb')
					pickle.dump(world_data, pickle_out)
					pickle_out.close()
					print(f"Saved as: {level_name}_data")
					input_active = False
				elif event.key == pygame.K_ESCAPE:
					input_active = False
				elif event.key == pygame.K_BACKSPACE:
					input_text = input_text[:-1]
				else:
					if len(input_text) < 30:
						if event.unicode.isalnum() or event.unicode in ['_', '-']:
							input_text += event.unicode
		
		elif show_file_browser:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					selected_file_index = max(0, selected_file_index - 1)
				elif event.key == pygame.K_DOWN:
					selected_file_index = min(len(available_levels) - 1, selected_file_index + 1)
				elif event.key == pygame.K_RETURN:
					if available_levels:
						selected_file = available_levels[selected_file_index]
						pickle_in = open(selected_file, 'rb')
						world_data = pickle.load(pickle_in)
						pickle_in.close()
						level_name = selected_file.replace('_data', '')
						level = int(level_name.replace('level', ''))
						save_state()
						show_file_browser = False
						player = EditorPlayer(100, 700)
						print(f"Loaded: {selected_file}")
				elif event.key == pygame.K_ESCAPE:
					show_file_browser = False
		
		else:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					run = False
				
				elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
					save_level()
				
				elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
					undo()
				elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
					redo()
				
				elif event.key == pygame.K_l:
					available_levels = get_level_files()
					show_file_browser = True
					selected_file_index = 0
				
				elif event.key == pygame.K_p:
					# Toggle preview mode
					if preview_mode:
						disable_preview_mode()
					else:
						enable_preview_mode()
			
			if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
				clicked = True
				dragging = True
				pos = pygame.mouse.get_pos()
				x = pos[0] // tile_size
				y = pos[1] // tile_size
				
				if x < 20 and y < 20:
					last_tile_pos = (x, y)
					
					# Right-click: Decrement tile type (previous block)
					if pygame.mouse.get_pressed()[2] == 1:
						world_data[y][x] -= 1
						if world_data[y][x] < 0:
							world_data[y][x] = 9
						save_state()
					
					# Left-click: Increment tile type (next block/forward)
					elif pygame.mouse.get_pressed()[0] == 1:
						world_data[y][x] += 1
						if world_data[y][x] > 9:
							world_data[y][x] = 0
						save_state()
			
			if event.type == pygame.MOUSEBUTTONUP:
				clicked = False
				dragging = False
				last_tile_pos = None
	
	if dragging and not input_active and not show_file_browser:
		pos = pygame.mouse.get_pos()
		x = pos[0] // tile_size
		y = pos[1] // tile_size
		
		if x < 20 and y < 20 and (x, y) != last_tile_pos:
			last_tile_pos = (x, y)
			
			# Right-click dragging: Continue decrementing blocks
			if pygame.mouse.get_pressed()[2] == 1 and pygame.mouse.get_pressed()[0] == 0:
				world_data[y][x] -= 1
				if world_data[y][x] < 0:
					world_data[y][x] = 9
			
			# Left-click dragging: Continue incrementing blocks
			elif pygame.mouse.get_pressed()[0] == 1 and pygame.mouse.get_pressed()[2] == 0:
				world_data[y][x] += 1
				if world_data[y][x] > 9:
					world_data[y][x] = 0
	
	pygame.display.update()

pygame.quit()
