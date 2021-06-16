import random

class Tetromino:

	# controls piece generation
	index2rgb = {0:(0,0,0),1:(0,255,255),2:(0,0,255),3:(255,128,0),4:(255,255,0),5:(0,255,0),6:(255,0,255),7:(255,0,0)}
	tetromino2index = {'I':1,'J':2,'L':3,'O':4,'S':5,'T':6,'Z':7}
	tetromino2rgb = {'I':(0,255,255),'J':(0,0,255),'L':(255,128,0),'O':(255,255,0),'S':(0,255,0),'T':(255,0,255),'Z':(255,0,0)}
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
