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
	