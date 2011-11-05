import pygame
import spyral
import random
import math
import fractions
from os import path

MOVES_PER_SECOND = 5
TICKS_PER_SECOND = 15
TICKS_PER_MOVE = TICKS_PER_SECOND/MOVES_PER_SECOND
HEIGHT = 900
WIDTH = 1200
SCALE = 1.5
BLOCK_SIZE = 60
APPLE_SIZE = 40
APPLE_D = BLOCK_SIZE - APPLE_SIZE
STEP = float(BLOCK_SIZE/TICKS_PER_MOVE)

operators = ["+","-","*","/"]
directionChars = ['N','S','E','W']
directions = {}
directions['up'] = 0
directions['down'] = 1
directions['right'] = 2
directions['left'] = 3

# locations are in terms of the discrete grid, with indexing beginning at 0. top-left is origin.
# pixel_x is grid_x*BLOCK_SIZE + BLOCK_SIZE/2, which corresponds to the centers of sprites

fonts = {}
geom = {}
images = {}
colors = {}
strings = {}

# snake is a list of SnakeNodes, head is the location of the head
def openSpace(foodItems,snake,head):
	taken = True
	while taken:
		taken = False
		loc = (random.randrange(0,20),random.randrange(0,14))
		for item in foodItems:
			if item.location == loc:
				taken = True
		for s in snake:
			if s.location == loc:
				taken = True
		if head == loc:
			taken = True
	return loc

def step(sprite,inc,count):
	if sprite.direction == directions['up']:
		sprite.rect.center = (sprite.oldLocation[0]*BLOCK_SIZE + BLOCK_SIZE/2,
			sprite.oldLocation[1]*BLOCK_SIZE + BLOCK_SIZE/2 - int(inc*count))
	elif sprite.direction == directions['down']:
		sprite.rect.center = (sprite.oldLocation[0]*BLOCK_SIZE + BLOCK_SIZE/2,
			sprite.oldLocation[1]*BLOCK_SIZE + BLOCK_SIZE/2 + int(inc*count))
	elif sprite.direction == directions['left']:
		sprite.rect.center = (sprite.oldLocation[0]*BLOCK_SIZE + BLOCK_SIZE/2 - int(inc*count),
			sprite.oldLocation[1]*BLOCK_SIZE + BLOCK_SIZE/2)
	else:
		sprite.rect.center = (sprite.oldLocation[0]*BLOCK_SIZE + BLOCK_SIZE/2 + int(inc*count),
			sprite.oldLocation[1]*BLOCK_SIZE + BLOCK_SIZE/2)
	
	if type(sprite).__name__ == 'SnakeNode':
		yoffset = (BLOCK_SIZE/4)*math.cos(.02*sprite.rect.center[0])
		xoffset = (BLOCK_SIZE/4)*math.cos(.02*sprite.rect.center[1])
		if sprite.direction == directions['right'] or sprite.direction == directions['left']:
			sprite.rect.center = (sprite.rect.center[0],sprite.rect.center[1]+yoffset)
		else:
			sprite.rect.center = (sprite.rect.center[0]+xoffset,sprite.rect.center[1])

class Menu(spyral.scene.Scene):
	"""Menu Scene shows the game title, buttons to start game, select
	characters or view achievements."""

	def __init__(self):
		spyral.scene.Scene.__init__(self)
		self.root_camera = spyral.director.get_camera()
		self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))		
		self.camera.set_background(images['background'])
		
		menu = spyral.sprite.Sprite()
		menu.image = images['menu']
		menu.rect.topleft = (0,0)
		self.group = spyral.sprite.Group(self.camera)
		self.group.add(menu)

	def render(self):
		"""Render the current scene"""
		self.group.draw()   # draw group of sprites
		self.root_camera.draw()  # draw the current frame

	def update(self, tick):
		"""Update the current scene based on user input"""
		
		# get events (keyboard, mouse, etc.)
		for event in pygame.event.get():
			
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if geom['menu_start'].collidepoint(event.pos):
					# Start button clicked
					# move to Game scene
					spyral.director.push(Game())
					
				elif geom['menu_character'].collidepoint(event.pos):
					# Character Select button clicked 
					# move to CharacterSelect scene
					spyral.director.push(CharacterSelect())
					
				elif geom['menu_unlock'].collidepoint(event.pos):
					# Achievements/Unlocks button clicked
					# move to Achievements scene
					#spyral.director.push(Achievements())
					pass

				elif geom['menu_quit'].collidepoint(event.pos):
					# Quit button clicked
					exit(0)
				
			elif event.type == pygame.QUIT:
				# for QUIT event, terminate the program
				exit(0)

class CharacterSelect(spyral.scene.Scene):

	def __init__(self):
		"""Construct the Menu scene which shows the game title and 
		instructions."""
		
		# Init from the super class
		spyral.scene.Scene.__init__(self)
		
		# get default camera
		self.root_camera = spyral.director.get_camera()
		self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))
		
		# set camera's background 
		self.camera.set_background(images['background'])

		self.group = spyral.sprite.Group(self.camera)

		# character select sprite
		character_select = spyral.sprite.Sprite()
		character_select.image = images['character_select']
		character_select.rect.topleft = (0,0)
		self.group.add(character_select)
		
		self.characters = []
		self.names = []
		for i in range(3):
			character = spyral.sprite.Sprite()
			character.image = spyral.util.load_image("images/Adder/CharSelect/" + str(i) + ".png") 
			character.rect.center = geom['character_center']
			
			name = spyral.sprite.Sprite()
			name.image = fonts['character_name'].render(strings['characters'][i],
									True,colors['character_name'])
			name.rect.center = geom['character_name_center']
			
			self.characters.append(character)
			self.names.append(name)
			
		self.selected_character = 0
		self.group.add(self.characters[self.selected_character], 
					self.names[self.selected_character])

	def render(self):
		"""Render the current scene"""
		self.group.draw()   # draw group of sprites
		self.root_camera.draw()  # draw the current frame
	
	def update(self, tick):
		"""Update the current scene based on user input"""

		# get events (keyboard, mouse, etc.)
		for event in pygame.event.get():

			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if geom['character_prev'].collidepoint(event.pos):

					self.group.remove(self.characters[self.selected_character], 
									self.names[self.selected_character])

					if self.selected_character == 0:
						self.selected_character = len(self.characters) - 1
					else: 
						self.selected_character -= 1

					self.group.add(self.characters[self.selected_character], 
								self.names[self.selected_character])

				elif geom['character_next'].collidepoint(event.pos):

					self.group.remove(self.characters[self.selected_character], 
									self.names[self.selected_character])

					if self.selected_character == len(self.characters) - 1:
						self.selected_character = 0
					else: 
						self.selected_character += 1

					self.group.add(self.characters[self.selected_character], 
								self.names[self.selected_character])

				elif geom['character_back'].collidepoint(event.pos):
					# Back button clicked
					spyral.director.pop()
					
			elif event.type == pygame.QUIT:
				# for QUIT event, terminate the program
				exit(0)

class Score(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self.val = 0
		self.render()

	def render(self):
		self.image = fonts['score'].render("SCORE: %d" % self.val,True,colors['score'])
		self.rect.midtop = (geom['scorex'],geom['text_height'])

# self.express is a list of strings, each of which is a number or operator
class Expression(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self.express = []
		self.oldExpress = [0]
		self.render()

	def render(self):
		if self.express != self.oldExpress:
			self.image = fonts['expression'].render( " ".join(self.express),True,colors['expression'])
			self.rect.midtop = (geom['expressionx'],geom['text_height_bottom'])
			self.oldExpress = self.express

	def findExpression(self,s):
		self.express = []
		for n in s.nodes:
			self.express.append(str(n.value))

class Goal(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self.val = random.randrange(0,20,1)
		self.render()

	def render(self):
		self.image = fonts['goal'].render("Goal: %d" % self.val,True,colors['goal'])
		self.rect.midtop = (geom['goalx'],geom['text_height'])

class Length(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self.val = 0
		self.oldVal = 1
		self.render()

	def render(self):
		if self.val != self.oldVal:
			self.image = fonts['length'].render("Length: %d" % self.val,True,colors['length'])
			self.rect.midtop = (geom['lengthx'],geom['text_height_bottom'])
			self.oldVal = self.val

class Operator(spyral.sprite.Sprite):
	def __init__(self,foodItems,snake,head):
		spyral.sprite.Sprite.__init__(self)
		self.location = openSpace(foodItems,snake,head)
		used = False
		for f in foodItems:
			if f.val == "*" or f.val == "/":
				used = True
		if len(snake) > 0:
			if snake[len(snake)-1].value == "/":
				used = True
		if used == False:
			self.val = operators[random.randrange(0,4,1)]
		else:
			self.val = operators[random.randrange(0,2,1)]
		self.valImage = fonts['node'].render(str(self.val),True,colors['bodynode'])
		self.image = images['Apple1'].copy()
		self.image.blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2 - APPLE_D/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2 - APPLE_D/2))
#		self.image = fonts['number'].render("%d" % self.val,True,colors['number'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + (BLOCK_SIZE - APPLE_D) /2,self.location[1]*BLOCK_SIZE + (BLOCK_SIZE - APPLE_D)/2)

class Number(spyral.sprite.Sprite):
	def __init__(self,foodItems,snake,head):
		spyral.sprite.Sprite.__init__(self)
		self.location = openSpace(foodItems,snake,head)
		self.val = random.randrange(1,15,1)
		self.valImage = fonts['node'].render(str(self.val),True,colors['bodynode'])
		self.image = images['Apple0'].copy()
		self.image.blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2 - APPLE_D/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2 - APPLE_D/2))
#		self.image = fonts['number'].render("%d" % self.val,True,colors['number'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)

class SnakeNode(spyral.sprite.Sprite):
	def __init__(self,val):
		spyral.sprite.Sprite.__init__(self)
		self.value = val
		self.direction = directions['right']
		self.valImage = fonts['node'].render(str(self.value),True,colors['bodynode'])
		self.bodyImages = []
		for ii in range(4):
			self.bodyImages.append( images['body'+directionChars[ii]].copy())
			if directions['up'] == ii:
				temp = pygame.transform.rotate(self.valImage,90).copy()
				self.bodyImages[ii].blit(temp,((BLOCK_SIZE - temp.get_size()[0])/2,(BLOCK_SIZE - temp.get_size()[1])/2))
			elif directions['down'] == ii:
				temp = pygame.transform.rotate(self.valImage,-90).copy()
				self.bodyImages[ii].blit(temp,((BLOCK_SIZE - temp.get_size()[0])/2,(BLOCK_SIZE - temp.get_size()[1])/2))  
			elif directions['left'] == ii:
				temp = pygame.transform.rotate(self.valImage,180).copy()
				self.bodyImages[ii].blit(temp,((BLOCK_SIZE - temp.get_size()[0])/2,(BLOCK_SIZE - temp.get_size()[1])/2))
			elif directions['right'] == ii:
				self.bodyImages[ii].blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2))
		self.image = self.bodyImages[self.direction] 
		self.location = (-10,-10)
		self.oldLocation = (-10,-10)
		self.render()

	def render(self):
		#for moving sprites in this game, the image changes every time the direction does
		self.image = self.bodyImages[self.direction]
		#self.image = fonts['node'].render(str(self.value),True,colors['node'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)
		yoffset = (BLOCK_SIZE/4)*math.cos(.02*self.rect.center[0])
		xoffset = (BLOCK_SIZE/4)*math.cos(.02*self.rect.center[1])
		if self.direction == directions['right'] or self.direction == directions['left']:
			self.rect.center = (self.rect.center[0],self.rect.center[1]+yoffset)
		else:
			self.rect.center = (self.rect.center[0]+xoffset,self.rect.center[1])
			



class Snake(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self.location = (9,7)
		self.oldLocation = self.location
		self.nodes = []
		self.clearing = False
		self.collapsing = False
		self.length = 0
		self.direction = directions['right']
		self.image = images['head' + str(0) + directionChars[self.direction]]
		self.lastType = 'Operator'
		self.eaten = False
		self.eaten2 = False
		self.render()

	#only call when the snake reaches the new location, which gets stored to oldLocation, where the sprites are drawn
	def render(self):
		#render the nodes
		for n in self.nodes:
			n.render()
		#render the head
		if self.eaten or self.eaten2:
			self.image = images['head5' + directionChars[self.direction]]
			if self.eaten:
				self.eaten = False
			else:
				self.eaten2 = False
		else:
			self.image = images['head0' + directionChars[self.direction]]
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)

	def findLength(self):
		self.length = 0
		for n in self.nodes:
			self.length = self.length+1

class Game(spyral.scene.Scene):
	def __init__(self, colorInt):
		spyral.scene.Scene.__init__(self)

		#Init Images
		colorInt = colorInt
		size = 60
		for direction in range(4):
			bodyImageString = 'body' + directionChars[direction]
			url = "Images/Adder/"+ str(size) +"/"+ str(colorInt) + "/Body_" + str(directionChars[direction]) + ".png"
			images[bodyImageString] = pygame.image.load(url)
			for frame in range(7):
				headImageString= 'head' + str(frame) + directionChars[direction]
				url = "Images/Adder/"+ str(size) +"/"+ str(colorInt) + "/Head_" + str(directionChars[direction]) + str(frame)+ ".png"
				images[headImageString] = pygame.image.load(url)

		for apple in range(2):
			url = "Images/Other/Apple"+str(apple)+".png"
			images['Apple'+str(apple)] = pygame.image.load(url)

		
		self.clock.ticks_per_second = TICKS_PER_SECOND
		self.root_camera = spyral.director.get_camera()
		self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))		
		self.group = spyral.sprite.Group(self.camera)
		background = spyral.util.new_surface((WIDTH,HEIGHT))
		background.fill(colors['background'])
		self.camera.set_background(background)
		self.goal = 15
		self.snake = Snake()
		self.foodItems = [Operator([],[],self.snake.location)]
		for n in range(0,3):
			self.foodItems.append(Number(self.foodItems,[],self.snake.location))
		for n in range(0,2):
			self.foodItems.append(Operator(self.foodItems,[],self.snake.location))
		for i in self.foodItems:
			self.group.add(i,)
		self.moving = False
		self.collapsing = False
		self.collapseIndex = 0
		self.collapseNodes = []
		self.collapseCase = 1
		self.operatorNode = None
		self.newNode = None
		self.count = 0
		self.eating = False
		self.eatIndex = 0
		#self.score = Score()
		#self.group.add(self.score)
		self.length = Length()
		self.group.add(self.length)
		self.expression = Expression()
		self.group.add(self.expression)
		self.clearing = False
		self.group.add(self.snake)

	def findNextOp(self):
		for n in self.snake.nodes:
			if n.value == "*":
				self.collapseCase = 1
				self.operatorNode = n
				return
		for n in self.snake.nodes:
			if n.value == "+" or n.value == "-":
				if len(self.snake.nodes) <= 3 or (self.snake.nodes[3].value == "+" or self.snake.nodes[3].value == "-"):
					self.collapseCase = 1
					self.operatorNode = n
					return
				elif self.snake.nodes[3].value == "/":
					self.collapseCase = 2
					self.operatorNode = n
					return
			elif n.value == "/":
				if len(self.snake.nodes) > 5 and self.snake.nodes[5].value == "/":
					self.collapseCase = 4
					self.operatorNode = self.snake.nodes[3]
					return
				else:
					self.collapseCase = 3
					self.operatorNode = self.snake.nodes[3]
					return


	def exprEval(self):
		if self.collapseNodes[1].value == "+":
			return (self.collapseNodes[0].value+self.collapseNodes[2].value)
		elif self.collapseNodes[1].value == "-":
			return (self.collapseNodes[0].value-self.collapseNodes[2].value)
		elif self.collapseNodes[1].value == "/":
			return float(self.collapseNodes[0].value/self.collapseNodes[2].value)
		elif self.collapseNodes[1].value == "*":
			return (self.collapseNodes[0].value*self.collapseNodes[2].value)

	def collapse(self):
		if self.collapseIndex == 0:
			for n in self.collapseNodes[:]:
				self.collapseNodes.remove(n)
			self.findNextOp()
			self.collapseIndex = 1
			self.moving = False
			return
		
		if self.collapseCase == 1:
			if self.collapseIndex == 1:
				opIndex = self.snake.nodes.index(self.operatorNode)
				self.collapseNodes.append(self.snake.nodes[opIndex-1])
				self.collapseNodes.append(self.snake.nodes[opIndex])
				self.collapseNodes.append(self.snake.nodes[opIndex+1])
				for n in self.collapseNodes:
					n.kill()
				newNode = SnakeNode(self.exprEval())
				self.group.add(newNode)
				newNode.location = self.snake.nodes[opIndex].location
				newNode.oldLocation = newNode.location
				newNode.direction = self.snake.nodes[opIndex].direction
				self.snake.nodes.insert(opIndex,newNode)
				for n in self.collapseNodes:
					self.snake.nodes.remove(n)
				self.collapseIndex = 2
				self.newNode = newNode
				newNode.render()
				return

			elif self.collapseIndex == 2:
				#self.snake.render()
				newIndex = self.snake.nodes.index(self.newNode)
				self.snake.nodes[newIndex].location = self.collapseNodes[2].location
				self.snake.nodes[newIndex].direction = self.collapseNodes[2].direction
				for i in range(0,newIndex-1):
					self.snake.nodes[i].location = self.snake.nodes[i+1].location
					self.snake.nodes[i].direction = self.snake.nodes[i+1].direction
				if newIndex > 0:
					self.snake.nodes[newIndex-1].location = self.collapseNodes[0].location
					self.snake.nodes[newIndex-1].direction = self.collapseNodes[0].direction
				self.collapseIndex = 3
				return

			elif self.collapseIndex == 3:
				#self.snake.render()
				newIndex = self.snake.nodes.index(self.newNode)
				for i in range(0,newIndex-1):
					self.snake.nodes[i].location = self.snake.nodes[i+1].location
					self.snake.nodes[i].direction = self.snake.nodes[i+1].direction
				if newIndex > 0:
					self.snake.nodes[newIndex-1].location = self.collapseNodes[1].location
					self.snake.nodes[newIndex-1].direction = self.collapseNodes[1].direction

				self.collapseIndex = 0
				return
				
		elif self.collapseCase == 2 or self.collapseCase == 3:
			
			if self.collapseIndex == 1:
			
				for i in range(0,5):
					self.collapseNodes.append(self.snake.nodes[i])
				for n in self.collapseNodes:
					n.kill()				
				for n in self.collapseNodes:
					self.snake.nodes.remove(n)
					
				if self.collapseCase == 2:
					f = fractions.Fraction(self.collapseNodes[2].value,self.collapseNodes[4].value)
					if self.collapseNodes[1].value == "+":
						f = f + self.collapseNodes[0].value
					elif self.collapseNodes[1].value == "-":
						f = self.collapseNodes[0].value - f
				elif self.collapseCase == 3:
					f = fractions.Fraction(self.collapseNodes[0].value,self.collapseNodes[2].value)
					if self.collapseNodes[3].value == "+":
						f = f + self.collapseNodes[4].value
					elif self.collapseNodes[3].value == "-":
						f = f - self.collapseNodes[4].value
				
				newNum = SnakeNode(f.numerator)
				newOp = SnakeNode("/")
				newDenom = SnakeNode(f.denominator)
				
				self.group.add(newNum)
				self.group.add(newDenom)
				self.group.add(newOp)

				self.snake.nodes.insert(0,newDenom)
				self.snake.nodes.insert(0,newOp)
				self.snake.nodes.insert(0,newNum)
				
				newNum.location = self.collapseNodes[1].location
				newNum.oldLocation = self.collapseNodes[1].oldLocation
				newNum.direction = self.collapseNodes[1].direction
				
				newOp.location = self.collapseNodes[2].location
				newOp.oldLocation = self.collapseNodes[2].oldLocation
				newOp.direction = self.collapseNodes[2].direction
				
				newDenom.location = self.collapseNodes[3].location
				newDenom.oldLocation = self.collapseNodes[3].oldLocation
				newDenom.direction = self.collapseNodes[3].direction
				
				newOp.render()
				newNum.render()
				newDenom.render()
				
				self.collapseIndex = 2
				
				return
				
			elif self.collapseIndex == 2:
				for i in range(0,3):
					self.snake.nodes[i].location = self.collapseNodes[i+2].location
					self.snake.nodes[i].direction = self.collapseNodes[i+2].direction
					
				self.collapseIndex = 3
				return
				
			elif self.collapseIndex == 3:
				self.collapseIndex = 0
				return
				
		if self.collapseCase == 4:
		
			if self.collapseIndex == 1:
			
				for i in range(0,7):
					self.collapseNodes.append(self.snake.nodes[i])
				for n in self.collapseNodes:
					n.kill()				
				for n in self.collapseNodes:
					self.snake.nodes.remove(n)
					
				f1 = fractions.Fraction(self.collapseNodes[0].value,self.collapseNodes[2].value)
				f2 = fractions.Fraction(self.collapseNodes[4].value,self.collapseNodes[6].value)
				if self.collapseNodes[3].value == "+":
					f = f1+f2
				else:
					f = f1-f2
					
				newNum = SnakeNode(f.numerator)
				newOp = SnakeNode("/")
				newDenom = SnakeNode(f.denominator)
				
				self.group.add(newNum)
				self.group.add(newDenom)
				self.group.add(newOp)

				self.snake.nodes.insert(0,newDenom)
				self.snake.nodes.insert(0,newOp)
				self.snake.nodes.insert(0,newNum)
				
				newNum.location = self.collapseNodes[2].location
				newNum.oldLocation = self.collapseNodes[2].oldLocation
				newNum.direction = self.collapseNodes[2].direction
				
				newOp.location = self.collapseNodes[3].location
				newOp.oldLocation = self.collapseNodes[3].oldLocation
				newOp.direction = self.collapseNodes[3].direction
				
				newDenom.location = self.collapseNodes[4].location
				newDenom.oldLocation = self.collapseNodes[4].oldLocation
				newDenom.direction = self.collapseNodes[4].direction
				
				newOp.render()
				newNum.render()
				newDenom.render()				
				
				self.collapseIndex = 2
				return
				
			elif self.collapseIndex == 2:
				for i in range(0,3):
					self.snake.nodes[i].location = self.collapseNodes[i+3].location
					self.snake.nodes[i].direction = self.collapseNodes[i+3].direction
					
				self.collapseIndex = 3
				return
			
			elif self.collapseIndex == 3:
				for i in range(0,3):
					self.snake.nodes[i].location = self.collapseNodes[i+4].location
					self.snake.nodes[i].direction = self.collapseNodes[i+4].direction
					
				self.collapseIndex = 4
				return
				
			elif self.collapseIndex == 4:
				self.collapseIndex = 0
				return
				
	def render(self):
		self.group.draw()
		self.root_camera.draw()

	def update(self,tick):

		#render length of the snake
		self.snake.findLength()
		self.length.val = self.snake.length
		self.length.render()

		#render the expression on the bottom
		self.expression.findExpression(self.snake)
		self.expression.render()

		if self.eating == False and self.clearing == False:
			self.count += 1
			self.count %= TICKS_PER_MOVE		

			if self.count == 0 and self.collapsing == False:
				if self.snake.location != self.snake.oldLocation:
					self.snake.render()

				self.snake.oldLocation = self.snake.location
				for n in self.snake.nodes:
					n.oldLocation = n.location

				#get keyboard input
				newDirection = self.snake.direction
				for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_q:
							spyral.director.pop()
						if event.key == pygame.K_c and (len(self.snake.nodes) > 1) and len(self.snake.nodes)%2 == 1:
							if len(self.snake.nodes)==3 and self.snake.nodes[1].value == "/":
								return
							self.collapsing = True
							return
						if event.key == pygame.K_UP and (self.snake.direction != directions['down'] or len(self.snake.nodes) == 0):
							self.moving = True
							oldDirection = self.snake.direction
							newDirection = directions['up']
							self.snake.direction = newDirection
							eaten = self.snake.eaten
							self.snake.render()
							self.snake.eaten = eaten
							self.snake.direction = oldDirection
						elif event.key == pygame.K_DOWN and (self.snake.direction != directions['up'] or len(self.snake.nodes) == 0):
							self.moving = True
							oldDirection = self.snake.direction
							newDirection = directions['down']
							self.snake.direction = newDirection
							eaten = self.snake.eaten
							self.snake.render()
							self.snake.eaten = eaten
							self.snake.direction = oldDirection
						elif event.key == pygame.K_RIGHT and (self.snake.direction != directions['left'] or len(self.snake.nodes) == 0):
							self.moving = True
							oldDirection = self.snake.direction
							newDirection = directions['right']
							self.snake.direction = newDirection
							eaten = self.snake.eaten
							self.snake.render()
							self.snake.eaten = eaten
							self.snake.direction = oldDirection
						elif event.key == pygame.K_LEFT and (self.snake.direction != directions['right'] or len(self.snake.nodes) == 0):
							self.moving = True
							oldDirection = self.snake.direction
							newDirection = directions['left']
							self.snake.direction = newDirection
							eaten = self.snake.eaten
							self.snake.render()
							self.snake.eaten = eaten
							self.snake.direction = oldDirection
					elif event.type == pygame.KEYUP:
						if event.key == pygame.K_UP and newDirection == directions['up']:
							self.moving = False
						elif event.key == pygame.K_DOWN and newDirection == directions['down']:
							self.moving = False
						elif event.key == pygame.K_RIGHT and newDirection == directions['right']:
							self.moving = False
						elif event.key == pygame.K_LEFT and newDirection == directions['left']:
							self.moving = False
				pygame.event.clear()


				if self.moving == True:


					#get new location
					if newDirection == directions['up']:
						newloc = (self.snake.location[0],self.snake.location[1]-1)
					elif newDirection == directions['down']:
						newloc = (self.snake.location[0],self.snake.location[1]+1)
					elif newDirection == directions['right']:
						newloc = (self.snake.location[0]+1,self.snake.location[1])
					elif newDirection == directions['left']:
						newloc = (self.snake.location[0]-1,self.snake.location[1])


					#test if we've hit a wall or self		
					if newloc[0] < 0 or newloc[0] > 19 or newloc[1] < 0 or newloc[1] > 13:
						if len(self.snake.nodes) > 0:
							self.clearing = True
						self.moving = False
						return

					for i in range(1,len(self.snake.nodes)):
						if newloc == self.snake.nodes[i].location:
							self.clearing = True
							self.moving = False
							return


					#test for target
					found = False
					for f in self.foodItems:
						if f.location == newloc and type(f).__name__ != self.snake.lastType:
							if f.val == "/" and self.snake.nodes[len(self.snake.nodes)-2].value == "/":
								continue
							
							found = True
							newNode = SnakeNode(f.val)
							newNode.location = self.snake.location
							newNode.oldLocation = newNode.location
							self.snake.nodes.append(newNode)
							self.group.add(newNode)



							itemName = type(f).__name__
							self.snake.lastType = itemName
							self.foodItems.remove(f)
							f.kill()

							#self.snake.render()
							newNode.render()

							break


					#move the nodes			
					if found == False: #move all of the nodes except the one closest to the head, and only if there's not a new node 
						if len(self.snake.nodes) > 1:#but only if there are nodes to move
							for i in range(0,len(self.snake.nodes)-1):
								self.snake.nodes[i].direction = self.snake.nodes[i+1].direction
								self.snake.nodes[i].render()
								self.snake.nodes[i].location = self.snake.nodes[i+1].location

					if len(self.snake.nodes) > 0:#if there is a node next to the head, move it
						self.snake.nodes[len(self.snake.nodes)-1].direction = self.snake.direction
						self.snake.nodes[len(self.snake.nodes)-1].render()						
						self.snake.nodes[len(self.snake.nodes)-1].location = self.snake.location

					if found == True:
						self.snake.nodes[len(self.snake.nodes)-1].oldLocation = self.snake.location


					#move the head
					self.snake.location = newloc
					self.snake.direction = newDirection



					#get new FoodItem if necessary
					if found:
						if itemName == 'Operator':
							newItem = Operator(self.foodItems,self.snake.nodes,self.snake.location)
							self.foodItems.append(newItem)
							self.group.add(newItem)
						else:
							newItem = Number(self.foodItems,self.snake.nodes,self.snake.location)
							self.foodItems.append(newItem)
							self.group.add(newItem)



					#start eating animation
					if found == True:
						self.eating = True
						return		

			#if we're in a collapse, collapse the next operator
			if self.collapsing and self.count == 0:
				self.snake.render()
				self.snake.oldLocation = self.snake.location
				for n in self.snake.nodes:
					n.oldLocation = n.location
				self.collapse()

			#break out of the collapse when it's finished
			if (self.collapsing and self.collapseIndex == 0 and self.count == 0 and 
					(len(self.snake.nodes) == 1 or (len(self.snake.nodes)==3 and self.snake.nodes[1].value == "/"))):
				self.collapsing = False

			#step each Sprite towards its new location
			if self.count != 0 and self.eating == False:
				if self.snake.location != self.snake.oldLocation:
					step(self.snake,STEP,self.count)
				for n in self.snake.nodes:
					if n.location != n.oldLocation:
						step(n,STEP,self.count)	
			self.group.update()

		#eating animation
		elif self.eating:
			self.eatIndex += 1
			inc = float(BLOCK_SIZE/5)			
			step(self.snake,inc,self.eatIndex)
			self.snake.image = images['head' + str(self.eatIndex) + directionChars[self.snake.direction]]
			if self.eatIndex == 4:
				self.eatIndex = 0
				self.eating = False
				self.count = TICKS_PER_MOVE-1
				self.snake.eaten = True
				self.snake.eaten2 = True #render "eaten" image twice
				return

		elif self.clearing:
			self.snake.image = images['head' + str(6) + directionChars[self.snake.direction]]
			self.count += 1
			self.count %= TICKS_PER_MOVE
			self.snake.image = images['head' + str(6) + directionChars[self.snake.direction]]
			if self.count == 0:
				n = self.snake.nodes[0]
				n.kill()
				self.snake.nodes.remove(n)
			if len(self.snake.nodes) == 0:
				self.clearing = False
				self.snake.lastType = 'Operator'
			return


		#drawing order
		for i in range(0,len(self.snake.nodes)):
			self.snake.nodes[i].kill()
			self.group.add(self.snake.nodes[i])
			self.snake.kill()
			self.group.add(self.snake)

def scale_graphics():

	# scale images
	for k in ('background', 'menu', 'character_select'):
		v = images[k]
		w, h = v.get_size()
		images[k] = pygame.transform.smoothscale(v, (int(w*SCALE), int(h*SCALE)))
  
	# scale geom
	for k, r in geom.items():
		if isinstance(r, pygame.Rect):
			geom[k] = pygame.Rect(r.left * SCALE, r.top * SCALE, 
								r.width * SCALE, r.height * SCALE)
				
		elif isinstance(r, tuple):
			geom[k] = tuple([i*SCALE for i in r])


def launch():
	spyral.init()


	colors['background'] = (222, 152, 254)
	colors['head'] = (255,255,255)
	colors['node'] = (255,255,255)
	colors['bodynode'] = (0,0,0)
	colors['number'] = (255,255,255)
	colors['operator'] = (255,255,255)
	colors['length'] = (0,0,0)
	colors['expression'] = (255,0,0)
	colors['character_name'] = (0,0,0)

	fonts['character_name'] = pygame.font.SysFont(None, BLOCK_SIZE)
	fonts['node'] = pygame.font.SysFont(None,3*BLOCK_SIZE/5)
	fonts['number'] = pygame.font.SysFont(None,BLOCK_SIZE)
	fonts['operator'] = pygame.font.SysFont(None,BLOCK_SIZE)
	fonts['length'] = pygame.font.SysFont(None,3*BLOCK_SIZE/5)
	fonts['expression'] = pygame.font.SysFont(None,3*BLOCK_SIZE/5)

	geom['lengthx'] = WIDTH - BLOCK_SIZE*2
	geom['expressionx'] = 0
	geom['text_height'] = 0
	geom['text_height_bottom'] = HEIGHT - BLOCK_SIZE
	
	geom['menu_start'] = pygame.Rect(300, 240, 200, 48)
	geom['menu_character'] = pygame.Rect(300, 325, 200, 70)
	geom['menu_unlock'] = pygame.Rect(24, 518, 210, 54)
	geom['menu_quit'] = pygame.Rect(684, 542, 85, 28)
	
	 
	# Geometry for the Character Select scene
	geom['character_prev'] = pygame.Rect(240, 170, 34, 56)
	geom['character_next'] = pygame.Rect(525, 170, 34, 56)
	geom['character_colors'] = [pygame.Rect(230, 392, 46, 46),
                               pygame.Rect(284, 392, 46, 46),
                               pygame.Rect(338, 392, 46, 46),
                               pygame.Rect(392, 392, 46, 46),
                               pygame.Rect(446, 392, 46, 46),
                               pygame.Rect(500, 392, 46, 46)]
	geom['character_back'] = pygame.Rect(680, 538, 70, 24)
	geom['character_center'] = (342, 200)
	geom['character_name_center'] = (400, 280)

	strings['characters'] = ["Adder Adam", "Boa Benny", "Cobra Carl",
                             "Python Perry", "Rattler Rebecca", "Sam Salamander"]
						 
	images['background'] = spyral.util.load_image(path.join('Images/Other', 'background.png'))
	images['menu'] = spyral.util.load_image(path.join('Images/Other', 'menu.png'))
	images['character_select'] = spyral.util.load_image(path.join('Images/Other', 'character_select.png'))

	#images['head'] = pygame.image.load("Images/Adder/Adder_Head_E0.png")
	#images['head'].fill(colors['head'])
	scale_graphics()

	spyral.director.push(Game(2))
	pygame.event.set_allowed(None)
	pygame.event.set_allowed(pygame.KEYDOWN)
	pygame.event.set_allowed(pygame.KEYUP)
	pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
