import pygame
import spyral
import random
import math

MOVES_PER_SECOND = 5
TICKS_PER_SECOND = 15
TICKS_PER_MOVE = TICKS_PER_SECOND/MOVES_PER_SECOND
HEIGHT = 600
WIDTH = 800
BLOCK_SIZE = 32
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
		loc = (random.randrange(0,25),random.randrange(0,18))
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
		self.render()
		
	def render(self):
		self.image = fonts['Expression'].render( " ".join(self.express),True,colors['expression'])
		self.rect.midtop = (geom['expressionx'],geom['text_height'])
		
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
		self.render()
		
	def render(self):
		self.image = fonts['length'].render("Length: %d" % self.val,True,colors['length'])
		self.rect.midtop = (geom['lengthx'],geom['text_height'])
		
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
			self.val = operators[random.randrange(0,3,1)]
		else:
			self.val = operators[random.randrange(0,2,1)]
		self.image = fonts['operator'].render(self.val,True,colors['operator'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)

class Number(spyral.sprite.Sprite):
	def __init__(self,foodItems,snake,head):
		spyral.sprite.Sprite.__init__(self)
		self.location = openSpace(foodItems,snake,head)
		self.val = random.randrange(1,15,1)
		self.image = fonts['number'].render("%d" % self.val,True,colors['number'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)

class SnakeNode(spyral.sprite.Sprite):
	def __init__(self,val):
		spyral.sprite.Sprite.__init__(self)
		self.value = val
		self.location = (-10,-10)
		self.oldLocation = (-10,-10)
		self.render()
	
	def render(self):
		#for moving sprites in this game, the image changes every time the direction does
		self.image = fonts['node'].render(str(self.value),True,colors['node'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)
		

		
class Snake(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self.location = (11,8)
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
		
class Game(spyral.scene.Scene):
	def __init__(self):
		spyral.scene.Scene.__init__(self)
		self.camera = spyral.director.get_camera()
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
		self.group.add(self.snake)
		self.moving = False
		self.collapsing = False
		self.collapseIndex = 0
		self.collapseNodes = []
		self.newNode = None
		self.count = 0
		self.eating = False
		self.eatIndex = 0
		self.clearing = False
		
	def findNextOp(self):
		for n in self.snake.nodes:
			if n.value == "/" or n.value == "*":
				return n
		for n in self.snake.nodes:
			if n.value == "+" or n.value == "-":
				return n
	
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
			operatorNode = self.findNextOp()
			opIndex = self.snake.nodes.index(operatorNode)
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
			self.collapseIndex = 1
			self.newNode = newNode
			newNode.render()
			return
				
		elif self.collapseIndex == 1:
			newIndex = self.snake.nodes.index(self.newNode)
			self.snake.nodes[newIndex].location = self.collapseNodes[2].location
			self.snake.nodes[newIndex].direction = self.collapseNodes[2].direction
			for i in range(0,newIndex-1):
				self.snake.nodes[i].location = self.snake.nodes[i+1].location
				self.snake.nodes[i].direction = self.snake.nodes[i+1].direction
			if newIndex > 0:
				self.snake.nodes[newIndex-1].location = self.collapseNodes[0].location
				self.snake.nodes[newIndex-1].direction = self.collapseNodes[0].direction
			self.collapseIndex = 2
			return
	
		else:
			newIndex = self.snake.nodes.index(self.newNode)
			for i in range(0,newIndex-1):
				self.snake.nodes[i].location = self.snake.nodes[i+1].location
				self.snake.nodes[i].direction = self.snake.nodes[i+1].direction
			if newIndex > 0:
				self.snake.nodes[newIndex-1].location = self.collapseNodes[1].location
				self.snake.nodes[newIndex-1].direction = self.collapseNodes[1].direction
			for n in self.collapseNodes[:]:
				self.collapseNodes.remove(n)
			self.collapseIndex = 0
	
	def render(self):
		self.group.draw()
		self.camera.draw()
	
	def update(self,tick):
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
						if event.key == pygame.K_SPACE:
							spyral.director.pop()
						if event.key == pygame.K_c and len(self.snake.nodes) > 1 and len(self.snake.nodes)%2 == 1:
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
					if newloc[0] < 0 or newloc[0] > 24 or newloc[1] < 0 or newloc[1] > 17:
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
							found = True
							newNode = SnakeNode(f.val)
							newNode.location = self.snake.location
							newNode.oldLocation = newNode.location
							self.snake.nodes.append(newNode)
							self.group.add(newNode)
							
							#so that the head is always drawn first
							self.snake.kill()
							self.group.add(self.snake)
							
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
								self.snake.nodes[i].location = self.snake.nodes[i+1].location
								self.snake.nodes[i].direction = self.snake.nodes[i+1].direction

					if len(self.snake.nodes) > 0:#if there is a node next to the head, move it
						self.snake.nodes[len(self.snake.nodes)-1].location = self.snake.location
						self.snake.nodes[len(self.snake.nodes)-1].direction = self.snake.direction
					
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
			if self.collapsing and self.collapseIndex == 0 and self.count == 0 and len(self.snake.nodes) == 1:
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
			self.count += 1
			self.count %= TICKS_PER_MOVE
			if self.count == 0:
				n = self.snake.nodes[0]
				n.kill()
				self.snake.nodes.remove(n)
			if len(self.snake.nodes) == 0:
				self.clearing = False
				self.snake.lastType = 'Operator'
			return
			
				




if __name__ == "__main__":
	spyral.init()
	
	colors['background'] = (0, 0, 0)
	colors['head'] = (255,255,255)
	colors['node'] = (255,255,255)
	colors['number'] = (255,255,255)
	colors['operator'] = (255,255,255)

	for direction in range(4):
		for frame in range(6):
			imageString= 'head' + str(frame) + directionChars[direction]
			print imageString
			url = "Images/Adder/Adder_Head_" + str(directionChars[direction]) + str(frame)+ ".png"
			images[imageString] = pygame.image.load(url)
			
	#images['head'] = pygame.image.load("Images/Adder/Adder_Head_E0.png")
	#images['head'].fill(colors['head'])
	
	fonts['node'] = pygame.font.SysFont(None,BLOCK_SIZE)
	fonts['number'] = pygame.font.SysFont(None,BLOCK_SIZE)
	fonts['operator'] = pygame.font.SysFont(None,BLOCK_SIZE)
	
	spyral.director.init((WIDTH,HEIGHT), ticks_per_second=TICKS_PER_SECOND)
	spyral.director.push(Game())
	spyral.director.clock.use_wait = False
	pygame.event.set_allowed(None)
	pygame.event.set_allowed(pygame.KEYDOWN)
	pygame.event.set_allowed(pygame.KEYUP)
	spyral.director.run()