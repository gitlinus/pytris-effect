import copy
import random

class Tetromino:

	# controls piece generation
	tetrominos = ['I','J','L','O','S','T','Z']

	def __init__(self,bagged=True,tetromino=None):
		# init and copy constructor
		self.hold = tetromino.hold if tetromino is not None else ""
		self.current_tetromino = tetromino.current_tetromino if tetromino is not None else ""
		self.queue = copy.copy(tetromino.queue) if tetromino is not None else []
		self.bagged = True  # 7-bag system by default
		if tetromino is None:
			self.initQueue()

	def initQueue(self): # start with two bags generated
		if self.bagged:
			self.genNextBag()
			self.genNextBag()	
		elif not self.bagged:
			self.genRandomTetromino()

	def genNextBag(self): # 7-bag system
		random.shuffle(self.tetrominos)
		# hack for deterministic ordering
		self.queue += self.tetrominos
		# self.queue += ['J', 'L', 'O', 'S', 'T', 'Z', 'I']

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

	def copy(self):
		return Tetromino(tetromino=self)
