import random

class Tetromino:

	# controls piece generation
	tetrominos = ['I','J','L','O','S','T','Z']

	def __init__(self,bagged=True):
		self.hold = ""
		self.current_tetromino = ""
		self.queue = []
		self.bagged = False
		if bagged: # 7-bag system by default
			self.bagged = True
		self.initQueue()

	def initQueue(self): # start with two bags generated
		if self.bagged:
			self.genNextBag()
			self.genNextBag()	
		elif not self.bagged:
			self.genRandomTetromino()

	def genNextBag(self): # 7-bag system
		random.shuffle(self.tetrominos)
		self.queue += self.tetrominos

	def genRandomTetromino(self): # pseudo-random system
		idx = random.randint(0,6)
		self.queue.append(self.tetrominos[idx])

	def nextTetromino(self):
		self.current_tetromino = self.queue.pop(0)
		if len(self.queue)<=7 and self.bagged: 
			self.genNextBag()
		elif not self.bagged:
			self.genRandomTetromino()

	def swapHold(self):
		if self.hold=="":
			self.hold = self.current_tetromino
			self.nextTetromino()
		else:
			temp = self.hold
			self.hold = self.current_tetromino
			self.current_tetromino = temp

	def getQueue(self):
		return self.queue
	
	def getHold(self):
		return self.hold

	def getCurrentTetromino(self):
		return self.current_tetromino		
