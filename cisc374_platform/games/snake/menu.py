import pygame
import spyral
import player
from game import *

class Text(spyral.sprite.Sprite):
	
	def __init__(self, pos, label, font, color, align='left'):
		spyral.sprite.Sprite.__init__(self)
		self.label = label
		self.font = font
		self.color = color
		self.anchor_pos = pos
		self.align = align
		
		self.render()
		
	def render(self):
		self.images = [self.render_text(self.color), self.render_text(colors['menu_text_hightlight'])]
		self.image = self.images[0]
		self.rect.width = self.image.get_width()
		self.rect.height = self.image.get_height()
		
		if self.align == 'right':
			self.rect.midright = self.anchor_pos
		elif self.align == 'center':
			self.rect.center = self.anchor_pos
		else:
			self.rect.midleft = self.anchor_pos
		
	def focus(self, focus=True):
		if focus:
			self.image = self.images[1]
		else:
			self.image = self.images[0]
			
	def set_label(self, label):
		self.label = label
		self.render()
		
	def render_text(self, color):
		width = 0
		height = 0
		lines = []
		for s in self.label.split("\n"):
			img = self.font.render(s, True, color)
			lines.append(img)
			
			if width < img.get_width():
				width = img.get_width()
			height += img.get_height()
		
		image = pygame.Surface((width, height), flags=pygame.SRCALPHA)
		y = 0
		for img in lines:
			dest = img.get_rect()
			image.blit(img, (dest.left, y))
			y += dest.height
			
		return image


class Button(spyral.sprite.Sprite):
	
	def __init__(self, pos, label, font, color):
		spyral.sprite.Sprite.__init__(self)
		self.label = label
		self.font = font
		self.color = color
		self.highlight = False 

		self.render_text()
		self.render()
		self.rect.center = pos
		
	def render(self):
		if self.highlight:
			self.image = images['button_highlight'].copy()
		else:
			self.image = images['button_normal'].copy()
		
		dest = self.text.get_rect()
		dest.center = self.image.get_rect().center
		
		self.image.blit(self.text, dest)
		
		
	def render_text(self):
		width = 0
		height = 0
		lines = []
		for s in self.label.split("\n"):
			img = self.font.render(s, True, self.color)
			lines.append(img)
			
			if width < img.get_width():
				width = img.get_width()
			height += img.get_height()
		
		self.text = pygame.Surface((width, height), flags=pygame.SRCALPHA)
		y = 0
		for img in lines:
			dest = img.get_rect()
			dest.centerx = width/2
			self.text.blit(img, (dest.left, y))
			y += dest.height
		
	def focus(self, focus=True):
		self.highlight = focus
		self.render()
		
class ImageButton(spyral.sprite.Sprite):
	
	def __init__(self, pos, images):
		spyral.sprite.Sprite.__init__(self)

		self.images = images
		self.highlight = False 

		self.render()
		self.rect.center = pos
		
	def render(self):
		if self.highlight:
			self.image = self.images[1]
		else:
			self.image = self.images[0]
		
	def focus(self, focus=True):
		self.highlight = focus
		self.render()

class Menu(spyral.scene.Scene):
	"""Menu Scene shows the game title, buttons to start game, select
	characters or view achievements."""
		
	def __init__(self,player):
		"""Construct the Menu scene"""
		spyral.scene.Scene.__init__(self)
		
		self.root_camera = spyral.director.get_camera()
		self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))    
		self.group = spyral.sprite.Group(self.camera)
		self.player = player

		center_x = self.camera.get_rect().centerx
		
		# start button
		start = ImageButton((center_x, geom['menu_start_y']),images['button_start'])
		
		# character select button
		character = ImageButton((center_x, geom['menu_character_y']),images['button_charselect'])
		
		# quit button
		quit = ImageButton((center_x, geom['menu_quit_y']),images['button_quit'])
		
		self.buttons = [start, character, quit]
		self.selected_button = 0
		self.buttons[self.selected_button].focus()
		
		self.group.add(start, character, quit)

	def on_enter(self):
		self.camera.set_background(images['menu_background'])

	def render(self):
		"""Render the current scene"""
		self.group.draw()   # draw group of sprites
		self.root_camera.draw()  # draw the current frame
	
	def update(self, tick):
		"""Update the current scene based on user input"""
		
		for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
			
			if event.type == pygame.KEYDOWN:
				if (event.key == pygame.K_DOWN or event.key ==  pygame.K_KP2):
					self.buttons[self.selected_button].focus(False)
					self.selected_button = (self.selected_button + 1) % len(self.buttons)
					self.buttons[self.selected_button].focus()
				
				elif (event.key == pygame.K_UP or event.key ==  pygame.K_KP8):
					self.buttons[self.selected_button].focus(False)
					self.selected_button = (self.selected_button - 1) % len(self.buttons)
					self.buttons[self.selected_button].focus()
					
				elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key ==  pygame.K_KP3:
					if self.selected_button == 0:
						# Start button clicked
						# move to Game scene
						spyral.director.push(Game(self.player))
					
					elif self.selected_button == 1:
						# Character Select button clicked 
						# move to CharacterSelect scene
						spyral.director.push(CharacterSelect(self.player))
						
					elif self.selected_button == 2:
						# Quit button clicked
						pygame.mouse.set_visible(True)
						exit(0)
		pygame.event.clear()

class Character(spyral.sprite.Sprite):
	
	def __init__(self, center, character,color):
		spyral.sprite.Sprite.__init__(self)
		self.set_character(character,color)
		self.rect.center = center
		
	def set_character(self, character, color):
		self.image = images['characters'][character][color]
	

class ColorSelect(spyral.sprite.Sprite):
	
	def __init__(self, center):
		spyral.sprite.Sprite.__init__(self)
		self.image = images['color_select']
		self.rect.center = center

class CharacterSelect(spyral.scene.Scene):
	
	def __init__(self,player):
		"""Construct the Menu scene which shows the game title and 
		instructions."""
		
		# Init from the super class
		spyral.scene.Scene.__init__(self)
		
		self.root_camera = spyral.director.get_camera()
		self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))    
		self.group = spyral.sprite.Group(self.camera)
		self.player = player
		
		center_x = self.camera.get_rect().centerx

		# title sprite
#       title = spyral.sprite.Sprite()
#       title.image = images['character_title']
#       title.rect.center = (center_x, geom['character_title_y'])
		
		# character name
		self.selected_character = self.player.nameToInt()
		self.character_name = Text((center_x, geom['character_name_y']), strings['characters'][self.selected_character],fonts['character_name'], colors['character_color'], 'center')
		self.character = Character((center_x, geom['character_image_y']), self.selected_character,0)

		# select color
		self.character_color = Text((center_x, geom['character_color_y']), "Color Select",fonts['character_color'], colors['character_color'], 'center')
		self.selected_color = self.player.color
		#self.color_select = ColorSelect((center_x, geom['character_color_select_y']))
		
		# back button
		#back = Text((geom['character_back_x'], geom['character_back_y']), "BACK",
					#fonts['character_back'], colors['character_back'], 'left')
		
		
		# achievements/unlock
#        unlock = Text((geom['character_unlock_x'], geom['character_unlock_y']), 
#                      "Players select different\ncharacters, unlocked\nwith achievements",
#                      fonts['character_unlock'], colors['character_unlock'])

		self.buttons = [self.character_name, self.character_color]
		self.selected_button = 0
		self.buttons[self.selected_button].focus()
		
		self.group.add(self.character_name, self.character, self.character_color)

	def on_enter(self):
		self.camera.set_background(images['menu_background'])
	
	def render(self):
		"""Render the current scene"""
		self.group.draw()   # draw group of sprites
		self.root_camera.draw()  # draw the current frame
	
	def update(self, tick):
		"""Update the current scene based on user input"""
		
		# get events (keyboard, mouse, etc.)
		for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_DOWN or event.key ==  pygame.K_KP2:
					self.buttons[self.selected_button].focus(False)
					self.selected_button = (self.selected_button + 1) % len(self.buttons)
					self.buttons[self.selected_button].focus()
				
				elif event.key == pygame.K_UP or event.key ==  pygame.K_KP8:
					self.buttons[self.selected_button].focus(False)
					self.selected_button = (self.selected_button - 1) % len(self.buttons)
					self.buttons[self.selected_button].focus()
					
				elif event.key == pygame.K_LEFT or event.key ==  pygame.K_KP4:
					if self.selected_button == 0:
						# change character
						self.selected_character = (self.selected_character - 1) % len(strings['char_sources'])
						self.character_name.set_label(strings['characters'][self.selected_character])
						self.character_name.focus()
						
						self.player.changeName(strings['char_sources'][self.selected_character])
						self.player.changeColor(0)
						self.character.set_character((self.selected_character % len(images['characters'])), self.player.color)
					
					elif self.selected_button == 1:
						# change color
						self.player.changeColor((self.player.color - 1) % geom['total_colors'])
						self.character.set_character((self.selected_character % len(images['characters'])), self.player.color)
				
				elif event.key == pygame.K_RIGHT or event.key ==  pygame.K_KP6:
					if self.selected_button == 0:
						# change character
						self.selected_character = (self.selected_character + 1) % len(strings['char_sources'])
						self.character_name.set_label(strings['characters'][self.selected_character])
						self.character_name.focus()
						
						self.player.changeName((strings['char_sources'][self.selected_character]))
						self.player.changeColor(0)
						self.character.set_character((self.selected_character % len(images['characters'])), self.player.color)
						
					elif self.selected_button == 1:
						# change color
						self.player.changeColor((self.player.color + 1) % geom['total_colors'])
						self.character.set_character((self.selected_character % len(images['characters'])), self.player.color)
					
				elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key ==  pygame.K_KP3:
					spyral.director.pop()
		pygame.event.clear()

def launch():
	spyral.init()
	
	#this function is in game.py
	init()
	spyral.director.push(Menu(player.Player()))
	
	pygame.event.set_allowed(None)
	pygame.event.set_allowed(pygame.KEYDOWN)
	pygame.event.set_allowed(pygame.KEYUP)
	pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
	pygame.mouse.set_visible(False)
