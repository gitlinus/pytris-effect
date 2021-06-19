import numpy as np 
from . import tetromino

class Matrix:
	# colour and index assignment
	index2rgb = {0:(0,0,0),1:(0,255,255),2:(0,0,255),3:(255,128,0),4:(255,255,0),5:(0,255,0),6:(255,0,255),7:(255,0,0)}
	tetromino2rgb = {'I':(0,255,255),'J':(0,0,255),'L':(255,128,0),'O':(255,255,0),'S':(0,255,0),'T':(255,0,255),'Z':(255,0,0)}
	tetromino2index = {'I':1,'J':2,'L':3,'O':4,'S':5,'T':6,'Z':7}

	tetromino2matrix = {
		'I':np.asarray([[1,1,1,1]],dtype=int),
		'J':np.asarray([[2,0,0],
						[2,2,2]],dtype=int),
		'L':np.asarray([[0,0,3],
						[3,3,3]],dtype=int),
		'O':np.asarray([[4,4],
						[4,4]],dtype=int),
		'S':np.asarray([[0,5,5],
						[5,5,0]],dtype=int),
		'T':np.asarray([[0,6,0],
						[6,6,6]],dtype=int),
		'Z':np.asarray([[7,7,0],
						[0,7,7]],dtype=int)
	}

	spawnLocations = {
		'I':[(1,3),(1,4),(1,5),(1,6)],
		'J':[(0,3),(1,3),(1,4),(1,5)],
		'L':[(0,5),(1,3),(1,4),(1,5)],
		'O':[(0,4),(0,5),(1,4),(1,5)],
		'S':[(0,4),(0,5),(1,3),(1,4)],
		'T':[(0,4),(1,3),(1,4),(1,5)],
		'Z':[(0,3),(0,4),(1,4),(1,5)]
	}

	def __init__(self, mino_dim=30):
		self.mino_dim = mino_dim
		self.width = mino_dim * 10
		self.height = mino_dim * 20
		self.matrix = np.zeros((22,10),dtype=int)
		self.score = 0
		self.lines_cleared = 0
		self.tetrominos = tetromino.Tetromino()
		self.current_tetromino = ""
		self.mino_locations = []
		self.hold_available = False
		self.placed_tetromino = False # keeps track whether tetromino was placed into matrix yet

	def dim(self):
		return self.width, self.height

	def getHold(self):
		return self.tetrominos.getHold()

	def getQueue(self):
		return self.tetrominos.getQueue()

	def getScore(self):
		return self.score

	def getLines(self):
		return self.lines_cleared

	def removeTetromino(self): # removes current tetromino from matrix
		for i in self.mino_locations:
			self.matrix[i[0],i[1]] = 0
		self.placed_tetromino = False

	def placeTetromino(self): # emplaces current tetromino into matrix
		for i in self.mino_locations:
			self.matrix[i[0],i[1]] = self.tetromino2index[self.current_tetromino]
		self.placed_tetromino = True

	def translateTetromino(self, drow, dcol): # translate current tetromino by drow and dcol
		temp = []
		self.removeTetromino()
		for i in self.mino_locations:
			temp.append((i[0]+drow,i[1]+dcol))
		self.mino_locations = temp
		self.placeTetromino()

	def addTetromino(self): # set piece spawn location
		self.clearLines() # clear any filled lines before adding next tetromino
		self.tetrominos.nextTetromino()
		self.current_tetromino = self.tetrominos.getCurrentTetromino()
		self.mino_locations.clear()
		self.mino_locations = self.spawnLocations[self.current_tetromino].copy()

		for i in self.mino_locations: 
			if self.matrix[i[0],i[1]] != 0:
				raise Exception("Topped out")

		self.placeTetromino()
		self.hold_available = True # make hold available again

	def swapHold(self):
		if not self.hold_available: # check if hold is available first
			return False

		self.removeTetromino()
		self.tetrominos.swapHold()
		self.current_tetromino = self.tetrominos.getCurrentTetromino()
		self.mino_locations.clear()
		self.mino_locations = self.spawnLocations[self.current_tetromino].copy()

		for i in self.mino_locations: 
			if self.matrix[i[0],i[1]] != 0:
				raise Exception("Topped out")

		self.placeTetromino()
		self.hold_available = False
		return True

	def hardDrop(self):
		self.removeTetromino()
		# find largest distance that all minos can shift down by
		dist = 0 
		found = False
		for r in range(21): # at most drop by a distance of 20
			for i in self.mino_locations:
				if i[0]+r >= 22 or (self.matrix[i[0]+r,i[1]] != 0 and (i[0]+r,i[1]) not in self.mino_locations):
					found = True
					break
			if found: break
			else: dist = r
		self.translateTetromino(dist,0)
		self.addTetromino()

	def rotateCW(self):
		pass

	def rotateCCW(self):
		pass

	def rotate180(self):
		pass

	def shiftLeft(self):
		# check if shift is possible, then shift 1 mino left
		for i in self.mino_locations:
			if i[1]-1 < 0 or (self.matrix[i[0],i[1]-1] != 0 and (i[0],i[1]-1) not in self.mino_locations):
				return False
		self.translateTetromino(0,-1)
		return True

	def shiftRight(self):
		for i in self.mino_locations:
			if i[1]+1 >= 10 or (self.matrix[i[0],i[1]+1] != 0 and (i[0],i[1]+1) not in self.mino_locations):
				return False
		self.translateTetromino(0,1)
		return True

	def softDrop(self): # should be basically the same as gravity
		for i in self.mino_locations:
			if i[0]+1 == 22 or (self.matrix[i[0]+1,i[1]] != 0 and (i[0]+1,i[1]) not in self.mino_locations): # cannot shift down further
				return False
		self.translateTetromino(1,0)
		return True

	def freezeTetromino(self): # freezes tetromino at current position
		pass

	def enforceGravity(self):
		"""
		shift mino locations down by 1, check for collisions, 
		clear old locations, store new locations
		"""
		for i in self.mino_locations:
			if i[0]+1 == 22 or (self.matrix[i[0]+1,i[1]] != 0 and (i[0]+1,i[1]) not in self.mino_locations): # cannot shift down further
				if i[0]==0 or i[0]==1:
					raise Exception("Topped out")
				else:
					self.addTetromino()
				return False
		self.translateTetromino(1,0)
		return True

	def clearLines(self): # clears filled lines, adapted from tetris-bot/board.py
		# remove current tetromino from board, clear lines, put current tetromino back
		res, cnt = [], 0 # resultant matrix, number of lines cleared
		for i in range(self.matrix.shape[0]):
			if not np.all((self.matrix[i] > 0)): 
				res.append(self.matrix[i][:])
			else:
				cnt += 1
		while len(res) < self.matrix.shape[0]:
			res.insert(0,np.zeros(self.matrix.shape[1]))
		self.matrix = np.asarray(res,dtype=int)
		self.lines_cleared += cnt
		return cnt > 0
		