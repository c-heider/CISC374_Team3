import random

class Level(object):
	def __init__(self):
		self.levelScores = []
		self.currLevel = 0
		self.tempLevel = 0
	
	def makeLevelGoal(self):
		if self.currLevel == 0:
			return random.randint(-20,20)
		elif self.currLevel == 1:
			return random.randint(-40,40)
		elif self.currLevel == 2:
			return random.randint(-40,40)
		else:
			return random.randint(-100,100)
	
	def increase(self):
		self.tempLevel += 1
		if self.tempLevel % 3 == 0:
			if self.currLevel < 2:
				self.currLevel += 1

class Player(object):
	def __init__(self,name = "Adder",color = 0,level = Level()):
		self.name = name
		self.color = color
		self.level = level
		self.totalScore = 0
		
	def changeColor(self,newColor):
		self.color = newColor
	
	def changeName(self,newName):
		self.name = newName
	
	def increaseLevel(self):
		self.level.increase()
	
	def nameToInt(self):
		if self.name == "Adder":
			return 0
		elif self.name == "Anaconda":
			return 1
		elif self.name == "Diamondback":
			return 2
		elif self.name == "Caterpillar":
			return 3
		else:
			return 0
