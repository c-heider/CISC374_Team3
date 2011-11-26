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
BLOCK_SIZE = 60
APPLE_SIZE = 40
APPLE_D = BLOCK_SIZE - APPLE_SIZE
STEP = float(BLOCK_SIZE/TICKS_PER_MOVE)

operators = ["+","-","*","/"]
directionChars = ['N','E','S','W']
directions = {}
directions['up'] = 0
directions['down'] = 2
directions['right'] = 1
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


class Score(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self._set_layer('other')
		self.val = 0
		self.render()

	def render(self):
		self.image = fonts['score'].render("SCORE: %d" % self.val,True,colors['score'])
		self.rect.midtop = (geom['scorex'],geom['text_height'])

# self.express is a list of strings, each of which is a number or operator
class Expression(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self._set_layer('other')
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
		self._set_layer('other')
		self.val = random.randrange(0,20,1)
		self.render()

	def render(self):
		self.image = fonts['goal'].render("Goal: %d" % self.val,True,colors['goal'])
		self.rect.midtop = (geom['goalx'],geom['text_height'])

class Length(spyral.sprite.Sprite):
	def __init__(self):
		spyral.sprite.Sprite.__init__(self)
		self._set_layer('other')
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
		self._set_layer('food')
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
		self.image0 = images['Apple10'].copy()
		self.image0.blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2 - APPLE_D/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2 - APPLE_D/2))
		self.image1 = images['Apple11'].copy()
		self.image1.blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2 - APPLE_D/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2 - APPLE_D/2))
		self.image = self.image1
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)

	def render(self, numNext, divLastOp):
		if numNext or (divLastOp and (self.val == '/' or self.val == '*')):
			self.image = self.image1
		else:
			self.image = self.image0
		

class Number(spyral.sprite.Sprite):
	def __init__(self,foodItems,snake,head):
		spyral.sprite.Sprite.__init__(self)
		self._set_layer('food')
		self.location = openSpace(foodItems,snake,head)
		self.val = random.randrange(1,15,1)
		self.valImage = fonts['node'].render(str(self.val),True,colors['bodynode'])
		self.image0 = images['Apple00'].copy()
		self.image0.blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2 - APPLE_D/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2 - APPLE_D/2))
		self.image1 = images['Apple01'].copy()
		self.image1.blit(self.valImage,((BLOCK_SIZE - self.valImage.get_size()[0])/2 - APPLE_D/2,(BLOCK_SIZE - self.valImage.get_size()[1])/2 - APPLE_D/2))
		self.image = self.image0
#		self.image = fonts['number'].render("%d" % self.val,True,colors['number'])
		self.rect.center = (self.location[0]*BLOCK_SIZE + BLOCK_SIZE/2,self.location[1]*BLOCK_SIZE + BLOCK_SIZE/2)

	def render(self, numNext, divLastOp):
		if numNext:
			self.image = self.image0
		else:
			self.image = self.image1

class SnakeNode(spyral.sprite.Sprite):
	def __init__(self,val):
		spyral.sprite.Sprite.__init__(self)
		self.value = val
		if val == "+" or val == "-" or val == "*" or val == "/":
			self._set_layer('operatorNodes')
		else:
			self._set_layer('numberNodes')
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
		self._set_layer('head')
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
	def __init__(self, snakeType, colorInt):
		spyral.scene.Scene.__init__(self)

		#Init Images
		self.colorInt = colorInt
		self.snakeType = snakeType

		self.clock.ticks_per_second = TICKS_PER_SECOND
		self.root_camera = spyral.director.get_camera()
		self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT),layers=['other','food','operatorNodes','numberNodes','head'])		
		self.group = spyral.sprite.Group(self.camera)
		
		
	def on_enter(self):
 		self.camera.set_background(images['background'])
		size = 60
		for direction in range(4):
			bodyImageString = 'body' + directionChars[direction]
			url = "games/snake/Images/" + str(self.snakeType) + "/"+ str(size) +"/"+ str(self.colorInt) + "/Body_" + str(directionChars[direction]) + ".png"
			images[bodyImageString] = spyral.util.load_image(url)
			for frame in range(7):
				headImageString= 'head' + str(frame) + directionChars[direction]
				url = "games/snake/Images/" + str(self.snakeType) + "/" + str(size) +"/"+ str(self.colorInt) + "/Head_" + str(directionChars[direction]) + str(frame)+ ".png"
				images[headImageString] = spyral.util.load_image(url)

		for apple in range(2):
			for clear in range(2):
				url = "games/snake/Images/Other/Apple"+str(apple)+str(clear)+".png"
				images['Apple'+str(apple)+str(clear)] = spyral.util.load_image(url)

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
		self.expandLocations = []
		self.expandDirections = []
		self.expanding = False
		self.expandIndex = 0
		self.oldFrac = None
		self.newInt = 0
		pygame.event.set_allowed(None)
		pygame.event.set_allowed(pygame.KEYDOWN)
		pygame.event.set_allowed(pygame.KEYUP)
		pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
		pygame.mouse.set_visible(False)
	
			
	#get two empty spaces and corresponding directions for expansion. Return False if such do not exist
	def findExpansion(self):
		self.expandLocations = []
		self.expandDirections = []
		for i in range(0,4):
		
			#get new possible location
			newDirection = (self.snake.direction + i)%4
			if newDirection == directions['up']:
				newloc = (self.snake.location[0],self.snake.location[1]-1)
			elif newDirection == directions['down']:
				newloc = (self.snake.location[0],self.snake.location[1]+1)
			elif newDirection == directions['right']:
				newloc = (self.snake.location[0]+1,self.snake.location[1])
			elif newDirection == directions['left']:
				newloc = (self.snake.location[0]-1,self.snake.location[1])
				
			#reject if location is outside board
			if newloc[0] < 0 or newloc[0] > 19 or newloc[1] < 0 or newloc[1] > 13:
				continue
			
			conflict = False
			for n in self.snake.nodes:
				if newloc == n.location:	
					conflict = True
					break
			
			if conflict:
				continue
			else:
				for j in range(0,4):
					
					secondDir = (newDirection + j)%4
					if secondDir == directions['up']:
						secondloc = (newloc[0],newloc[1]-1)
					elif secondDir == directions['down']:
						secondloc = (newloc[0],newloc[1]+1)
					elif secondDir == directions['right']:
						secondloc = (newloc[0]+1,newloc[1])
					elif secondDir == directions['left']:
						secondloc = (newloc[0]-1,newloc[1])	
						
					if secondloc[0] < 0 or secondloc[0] > 19 or secondloc[1] < 0 or secondloc[1] > 13:
						continue

					if secondloc == newloc:
						continue
					
					conflict = False
					for n in self.snake.nodes:
						if secondloc == n.location:	
							conflict = True
							break
							
					if conflict:
						continue
					else:
					
						self.expandLocations.append(newloc)
						self.expandLocations.append(secondloc)
						self.expandDirections.append(newDirection)
						self.expandDirections.append(secondDir)
						return True
		return False
		
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
			elif n.value == "/" and len(self.snake.nodes) > 3:
				if len(self.snake.nodes) > 5 and self.snake.nodes[5].value == "/":
					self.collapseCase = 4
					self.operatorNode = self.snake.nodes[3]
					return
				else:
					self.collapseCase = 3
					self.operatorNode = self.snake.nodes[3]
					return
		for n in self.snake.nodes:
			if n.value == "/":
				if self.snake.nodes[0].value%self.snake.nodes[2].value == 0:
					self.collapseCase = 5
					self.operatorNode = self.snake.nodes[1]
					return
				elif fractions.gcd(self.snake.nodes[0].value,self.snake.nodes[2].value) != 1:
					self.collapseCase = 6
					self.operatorNode = self.snake.nodes[1]
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
			
	def expand(self):
		if self.expandIndex == 0:
			if self.findExpansion() == False:
				self.expanding = False
				return
			self.oldFrac = fractions.Fraction(self.snake.nodes[0].value,self.snake.nodes[2].value)
			newFrac = fractions.Fraction(self.oldFrac.numerator%self.oldFrac.denominator,self.oldFrac.denominator)
			tempFrac = self.oldFrac - newFrac
			self.newInt = tempFrac.numerator
			newNum = SnakeNode(self.oldFrac.numerator%self.oldFrac.denominator)
			newNum.location = self.snake.nodes[0].location
			newNum.direction = self.snake.nodes[0].direction
			newNum.oldLocation = self.snake.nodes[0].location
			self.snake.nodes[0].kill()
			self.snake.nodes.remove(self.snake.nodes[0])
			self.snake.nodes.insert(0,newNum)
			self.group.add(newNum)
			newNum.render()
			
			newOp = SnakeNode("+")
			newOp.location = self.snake.location
			newOp.direction = self.snake.direction
			newOp.oldLocation = self.snake.location
			
			self.snake.nodes.append(newOp)
			self.group.add(newOp)
			
			self.snake.location = self.expandLocations[0]
			self.snake.direction = self.expandDirections[0]
			
			self.snake.image = images['head0' + directionChars[self.snake.direction]]
			
			#newOp.render()
			
			self.expandIndex = 1
			return
			
		elif self.expandIndex == 1:
			newNode = SnakeNode(self.newInt)
			newNode.location = self.snake.location
			newNode.oldLocation = self.snake.location
			newNode.direction = self.snake.direction 
			
			self.snake.nodes.append(newNode)
			self.group.add(newNode)
			
			#newNode.render()
			
			self.snake.location = self.expandLocations[1]
			self.snake.direction = self.expandDirections[1]
			
			self.snake.image = images['head0' + directionChars[self.snake.direction]]

			
			self.expandIndex = 0
			self.expanding = False
			return
				
			

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
				
		elif self.collapseCase == 4:
		
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
		
		elif self.collapseCase == 5:
		
			if self.collapseIndex == 1:
				for i in range(0,3):
					self.collapseNodes.append(self.snake.nodes[i])
				for n in self.collapseNodes:
					n.kill()				
				for n in self.collapseNodes:
					self.snake.nodes.remove(n)
					
				f = fractions.Fraction(self.collapseNodes[0].value,self.collapseNodes[2].value)
				
				newNode = SnakeNode(f.numerator)
				self.group.add(newNode)
				self.snake.nodes.insert(0,newNode)
				
				newNode.location = self.collapseNodes[1].location
				newNode.oldLocation = self.collapseNodes[1].oldLocation
				newNode.direction = self.collapseNodes[1].direction
				newNode.render()
				
				self.collapseIndex = 2
				
				return
			
			elif self.collapseIndex == 2:
				
				self.snake.nodes[0].location = self.collapseNodes[2].location
				self.snake.nodes[0].direction = self.collapseNodes[2].direction
				
				self.collapseIndex = 3
				
				return
				
			elif self.collapseIndex == 3:
			
				self.collapseIndex = 0
				return
				
		elif self.collapseCase == 6:
			if self.collapseIndex == 1:
			
				for i in range(0,3):
					self.collapseNodes.append(self.snake.nodes[i])
				for n in self.collapseNodes:
					n.kill()				
				for n in self.collapseNodes:
					self.snake.nodes.remove(n)
					
				f = fractions.Fraction(self.collapseNodes[0].value,self.collapseNodes[2].value)
				
				newNum = SnakeNode(f.numerator)
				newOp = SnakeNode("/")
				newDenom = SnakeNode(f.denominator)
				
				self.group.add(newNum)
				self.group.add(newDenom)
				self.group.add(newOp)

				self.snake.nodes.insert(0,newDenom)
				self.snake.nodes.insert(0,newOp)
				self.snake.nodes.insert(0,newNum)
				
				newNum.location = self.collapseNodes[0].location
				newNum.oldLocation = self.collapseNodes[0].oldLocation
				newNum.direction = self.collapseNodes[0].direction
				
				newOp.location = self.collapseNodes[1].location
				newOp.oldLocation = self.collapseNodes[1].oldLocation
				newOp.direction = self.collapseNodes[1].direction
				
				newDenom.location = self.collapseNodes[2].location
				newDenom.oldLocation = self.collapseNodes[2].oldLocation
				newDenom.direction = self.collapseNodes[2].direction
				
				newOp.render()
				newNum.render()
				newDenom.render()
				
				self.collapseIndex = 2
				
				return
		
			elif self.collapseIndex == 2:
			
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

		#render apples
		for f in self.foodItems:
			if len(self.snake.nodes) < 3:
				f.render(self.snake.lastType == 'Operator', False)
			else:
				f.render(self.snake.lastType == 'Operator', self.snake.nodes[len(self.snake.nodes)-2].value == "/")

		if self.eating == False and self.clearing == False:
			self.count += 1
			self.count %= TICKS_PER_MOVE		

			if self.count == 0 and (self.collapsing == False and self.expanding == False):
				if self.snake.location != self.snake.oldLocation:
					self.snake.render()

				self.snake.oldLocation = self.snake.location
				for n in self.snake.nodes:
					n.oldLocation = n.location

				#get keyboard input
				newDirection = self.snake.direction
				for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_e:
							if (len(self.snake.nodes)==3 and self.snake.nodes[1].value == "/"
									and (self.snake.nodes[0].value%self.snake.nodes[2].value != 0 and 
									fractions.gcd(self.snake.nodes[0].value,self.snake.nodes[2].value) == 1) and
									math.fabs(self.snake.nodes[0].value) > self.snake.nodes[2].value):
								self.expanding = True
								return
						if event.key == pygame.K_q:
							spyral.director.pop()
						if event.key == pygame.K_c and (len(self.snake.nodes) > 1) and len(self.snake.nodes)%2 == 1:
							if (len(self.snake.nodes)==3 and self.snake.nodes[1].value == "/"
									and (self.snake.nodes[0].value%self.snake.nodes[2].value != 0 and 
									fractions.gcd(self.snake.nodes[0].value,self.snake.nodes[2].value) == 1)):
							
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
						if f.location == newloc and type(f).__name__ != self.snake.lastType and self.moving and self.clearing == False:
							if (f.val == "/" or f.val == "*") and self.snake.nodes[len(self.snake.nodes)-2].value == "/":
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
			if (self.collapsing or self.expanding) and self.count == 0:
				self.snake.render()
				self.snake.oldLocation = self.snake.location
				for n in self.snake.nodes:
					n.oldLocation = n.location
				if self.collapsing:
					self.collapse()
				elif self.expanding:
					self.expand()


			#break out of the collapse when it's finished
			if (self.collapsing and self.collapseIndex == 0 and self.count == 0 and 
					(len(self.snake.nodes) == 1 or (len(self.snake.nodes)==3 and self.snake.nodes[1].value == "/" and
					(self.snake.nodes[0].value%self.snake.nodes[2].value != 0 and
					fractions.gcd(self.snake.nodes[0].value,self.snake.nodes[2].value) == 1)))):
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
			if self.count == 0:
				n = self.snake.nodes[0]
				n.kill()
				self.snake.nodes.remove(n)
			if len(self.snake.nodes) == 0:
				self.clearing = False
				self.snake.lastType = 'Operator'
			return




def init():
	
	colors['background'] = (222, 152, 254)
	colors['head'] = (255,255,255)
	colors['node'] = (255,255,255)
	colors['bodynode'] = (0,0,0)
	colors['number'] = (255,255,255)
	colors['operator'] = (255,255,255)
	colors['length'] = (0,0,0)
	colors['expression'] = (255,0,0)
	
	colors['menu_start'] = (255,255,255)
	colors['menu_character'] = (231,237,26)
	colors['menu_unlock'] = (231,237,26)
	colors['menu_quit'] = (184,144,21)
	colors['menu_text_hightlight'] = (240,101,50)
	
	colors['character_unlock'] = (231,237,26)
	colors['character_back'] = (184,144,21)
	colors['character_name'] = (255,255,255)
	colors['character_color'] = (0,0,0)
	
	strings['characters'] = ["< Adder Adam >", "< Sal Amander >", "< Darryl Diamondback >", "< Colonel Caterpillar >"]
	strings['char_sources'] = ["Adder","Anaconda","Diamondback","Caterpillar"]
	
	images['background'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'background.png'))
	images['menu_background'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'TitleScreen.png'))
	
	images['menu_title'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'menu_title.png'))
	images['character_title'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'character_title.png'))
	images['button_normal'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'Button0.png'))
	images['button_highlight'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'Button2.png'))
	images['color_select'] = spyral.util.load_image(path.join('games/snake/Images/Other', 'color_select.png'))

	images['button_start'] = (spyral.util.load_image(path.join('games/snake/Images/Other/Buttons', 'Play0.png')),
							  spyral.util.load_image(path.join('games/snake/Images/Other/Buttons', 'Play1.png')))
	images['button_charselect'] = (spyral.util.load_image(path.join('games/snake/Images/Other/Buttons', 'CharSelect0.png')),
							 	   spyral.util.load_image(path.join('games/snake/Images/Other/Buttons', 'CharSelect1.png')))
	images['button_quit'] = (spyral.util.load_image(path.join('games/snake/Images/Other/Buttons', 'Quit0.png')),
						     spyral.util.load_image(path.join('games/snake/Images/Other/Buttons', 'Quit1.png')))
	
	
	images['adderColors'] = []
	for i in range(3):
		images['adderColors'].append(spyral.util.load_image(path.join('games/snake/Images/Adder/CharSelect', '%d.png' % i)))
	
	images['condaColors'] = []
	for i in range(3):
		images['condaColors'].append(spyral.util.load_image(path.join('games/snake/Images/Anaconda/CharSelect', '%d.png' % i)))
	
	images['diamondColors'] = []
	for i in range(3):
		images['diamondColors'].append(spyral.util.load_image('games/snake/Images/Diamondback/CharSelect/0.png'))

	images['caterpillarColors'] = []
	for i in range(3):
		images['caterpillarColors'].append(spyral.util.load_image('games/snake/Images/Caterpillar/CharSelect/'+str(i)+'.png'))
	
	images['characters'] = [images['adderColors'],images['condaColors'],images['diamondColors'],images['caterpillarColors']]
	
	fonts['node'] = pygame.font.SysFont(None,3*BLOCK_SIZE/5)
	fonts['number'] = pygame.font.SysFont(None,BLOCK_SIZE)
	fonts['operator'] = pygame.font.SysFont(None,BLOCK_SIZE)
	fonts['length'] = pygame.font.SysFont(None,3*BLOCK_SIZE/5)
	fonts['expression'] = pygame.font.SysFont(None,3*BLOCK_SIZE/5)
	
	fonts['menu_start'] = pygame.font.SysFont(None,2*images['button_normal'].get_height() / 3)
	fonts['menu_character'] = pygame.font.SysFont(None,images['button_normal'].get_height() / 2)
	fonts['menu_unlock'] = pygame.font.SysFont(None,images['button_normal'].get_height() / 3)
	fonts['menu_quit'] = pygame.font.SysFont(None,2*images['button_normal'].get_height() / 3)
	fonts['character_unlock'] = pygame.font.SysFont(None,images['button_normal'].get_height() / 4)
	fonts['character_back'] = pygame.font.SysFont(None,2*images['button_normal'].get_height() / 3)
	fonts['character_name'] = pygame.font.Font('games/snake/MangaTemple.ttf',images['button_normal'].get_height() / 3)
	fonts['character_color'] = pygame.font.Font('games/snake/MangaTemple.ttf',images['button_normal'].get_height() / 3)

	geom['lengthx'] = WIDTH - BLOCK_SIZE*2
	geom['expressionx'] = 0
	geom['text_height'] = 0
	geom['text_height_bottom'] = HEIGHT - BLOCK_SIZE
	
	geom['menu_start'] = pygame.Rect(300, 240, 200, 48)
	geom['menu_character'] = pygame.Rect(300, 325, 200, 70)
	geom['menu_unlock'] = pygame.Rect(24, 518, 210, 54)
	geom['menu_quit'] = pygame.Rect(684, 542, 85, 28)
		 
	geom['menu_title_y'] = HEIGHT / 6
	geom['menu_start_y'] = HEIGHT / 2 - images['button_start'][0].get_height()/8
	geom['menu_character_y'] = geom['menu_start_y'] + images['button_start'][0].get_height()
	geom['menu_quit_y'] = geom['menu_character_y'] + images['button_charselect'][0].get_height()
	
	geom['character_title_y'] = HEIGHT / 6
	geom['character_unlock_x'] = WIDTH * 2/100
	geom['character_unlock_y'] = 13*HEIGHT/14 - images['button_normal'].get_height()/2
	geom['character_back_x'] = 40
	geom['character_back_y'] = geom['menu_quit_y']
	geom['character_image_y'] = HEIGHT/2
	geom['character_name_y'] = HEIGHT/2 + 3*images['characters'][0][0].get_height()/4
	geom['character_color_y'] = geom['character_name_y'] + images['button_normal'].get_height()/2
	geom['character_color_select_y'] = geom['character_color_y'] + images['color_select'].get_height()
	
	geom['total_colors'] = 3
	

	#images['head'] = pygame.image.load("games/snake/Images/Adder/Adder_Head_E0.png")
	#images['head'].fill(colors['head'])

