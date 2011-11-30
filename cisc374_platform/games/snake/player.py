class Player(object):
	def __init__(self,name = "Adder",color = 0,level = 0):
		self.name = name
		self.color = color
		self.level = level
		
	def changeColor(self,newColor):
		self.color = newColor
	
	def changeName(self,newName):
		self.name = newName
	
	def increaseLevel(self):
		self.level += 1
	
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
	