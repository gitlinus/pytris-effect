import numpy as np 
from . import tetromino
from . import rotations
from . import scoring

class Matrix:
	# colour and index assignment
	index2rgb = {0:(0,0,0),1:(0,255,255),2:(0,0,255),3:(255,128,0),4:(255,255,0),5:(0,255,0),6:(255,0,255),7:(255,0,0),8:(64,64,64)}
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
		self.mino_dim = mino_dim # dimensions in number of pixels (only used for GUI)
		self.width = mino_dim * 10 # dimensions in number of pixels (only used for GUI)
		self.height = mino_dim * 20 # dimensions in number of pixels (only used for GUI)
		self.matrix = np.zeros((22,10),dtype=int)
		self.level = None
		self.score = 0
		self.lines_cleared = 0
		self.tetrominos = tetromino.Tetromino()
		self.current_tetromino = ""
		self.mino_locations = []
		self.tetromino_orientation = 0 # keeps track of orientation of current tetromino (0 to 3)
		self.hold_available = False
		self.placed_tetromino = False # keeps track whether tetromino was placed into matrix yet
		self.combo = 0
		self.b2b = False
		self.prev2moves = []
		self.prev_clear_text = []
		self.current_zone = 0
		self.full_zone = 40
		self.zone_state = False

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

	def appendPrevMoves(self, action, dist):
		self.prev2moves.append((action,dist))
		if len(self.prev2moves) > 2:
			self.prev2moves.pop(0)

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
		self.appendPrevMoves("TRANSLATION",abs(drow)+abs(dcol))

	def addTetromino(self): # set piece spawn location
		if not self.zone_state:
			# scoring
			score_incr, clear_text, b2b_next = scoring.calcScore(self.matrix,self.current_tetromino,self.mino_locations,self.level,self.b2b,self.prev2moves)
			self.score += score_incr
			self.b2b = b2b_next
			self.prev_clear_text = clear_text

			self.clearLines() # clear any filled lines before adding next tetromino
			self.tetrominos.nextTetromino()
			self.current_tetromino = self.tetrominos.getCurrentTetromino()
			self.tetromino_orientation = 0
			self.mino_locations.clear()
			self.mino_locations = self.spawnLocations[self.current_tetromino].copy()

			for i in self.mino_locations: # topping out determined if piece can spawn
				if self.matrix[i[0],i[1]] != 0:
					raise Exception("Topped out")

			self.placeTetromino()
			self.hold_available = True # make hold available again
			self.prev2moves.clear() # clear previous moves list
		else:
			self.clearZone() # clear any filled lines before adding next tetromino
			self.tetrominos.nextTetromino()
			self.current_tetromino = self.tetrominos.getCurrentTetromino()
			self.tetromino_orientation = 0
			self.mino_locations.clear()
			self.mino_locations = self.spawnLocations[self.current_tetromino].copy()

			for i in self.mino_locations: 
				if self.matrix[i[0],i[1]] != 0:
					self.leaveZone()

			self.placeTetromino()
			self.hold_available = True # make hold available again
			self.prev2moves.clear() # clear previous moves list

	def swapHold(self):
		if not self.hold_available: # check if hold is available first
			return False

		self.appendPrevMoves("SWAPHOLD",None)

		self.removeTetromino()
		self.tetrominos.swapHold()
		self.current_tetromino = self.tetrominos.getCurrentTetromino()
		self.mino_locations.clear()
		self.mino_locations = self.spawnLocations[self.current_tetromino].copy()

		if not self.zone_state:
			for i in self.mino_locations: 
				if self.matrix[i[0],i[1]] != 0:
					raise Exception("Topped out")
		else:
			for i in self.mino_locations: 
				if self.matrix[i[0],i[1]] != 0:
					self.leaveZone()

		self.placeTetromino()
		self.hold_available = False
		return True

	def hardDrop(self):
		# find largest distance that all minos can shift down by
		dist = 0 
		found = False
		for r in range(self.matrix.shape[0]-1): # range(21) at most drop by a distance of 20
			for i in self.mino_locations:
				if i[0]+r >= self.matrix.shape[0] or (self.matrix[i[0]+r,i[1]] != 0 and (i[0]+r,i[1]) not in self.mino_locations):
					found = True
					break
			if found: break
			else: dist = r
		self.translateTetromino(dist,0)
		self.score += 2*dist
		self.addTetromino()

	def rotateCW(self):
		self.removeTetromino()
		self.mino_locations, self.tetromino_orientation, kick_dist = rotations.rotateCW(self.matrix,self.current_tetromino,self.mino_locations,self.tetromino_orientation)
		self.appendPrevMoves("ROTATION",kick_dist)
		self.placeTetromino()
		
	def rotateCCW(self):
		self.removeTetromino()
		self.mino_locations, self.tetromino_orientation, kick_dist = rotations.rotateCCW(self.matrix,self.current_tetromino,self.mino_locations,self.tetromino_orientation)
		self.appendPrevMoves("ROTATION",kick_dist)
		self.placeTetromino()

	def rotate180(self):
		self.removeTetromino()
		self.mino_locations, self.tetromino_orientation, kick_dist = rotations.rotate180(self.matrix,self.current_tetromino,self.mino_locations,self.tetromino_orientation)
		self.appendPrevMoves("ROTATION",kick_dist)
		self.placeTetromino()

	def shiftLeft(self):
		# check if shift is possible, then shift 1 mino left
		for i in self.mino_locations:
			if i[1]-1 < 0 or (self.matrix[i[0],i[1]-1] != 0 and (i[0],i[1]-1) not in self.mino_locations):
				return False
		self.translateTetromino(0,-1)
		return True

	def shiftRight(self):
		for i in self.mino_locations:
			if i[1]+1 >= self.matrix.shape[1] or (self.matrix[i[0],i[1]+1] != 0 and (i[0],i[1]+1) not in self.mino_locations):
				return False
		self.translateTetromino(0,1)
		return True

	def softDrop(self): # should be basically the same as gravity
		for i in self.mino_locations:
			if i[0]+1 == self.matrix.shape[0] or (self.matrix[i[0]+1,i[1]] != 0 and (i[0]+1,i[1]) not in self.mino_locations): # cannot shift down further
				return False
		self.translateTetromino(1,0)
		self.score += 1
		return True

	def touchedStack(self): # checks whether tetromino has touched the matrix stack
		for i in self.mino_locations:
			if i[0]+1 == self.matrix.shape[0] or (self.matrix[i[0]+1,i[1]] != 0 and (i[0]+1,i[1]) not in self.mino_locations): # cannot shift down further
				return True
		return False

	def freezeTetromino(self): # freezes tetromino at current position
		while(self.enforceGravity()):
			pass
		self.appendPrevMoves("AUTOLOCK",None)
		self.addTetromino()

	def enforceGravity(self):
		for i in self.mino_locations:
			if i[0]+1 == self.matrix.shape[0] or (self.matrix[i[0]+1,i[1]] != 0 and (i[0]+1,i[1]) not in self.mino_locations): # cannot shift down further
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
		self.current_zone = min(self.current_zone+cnt,self.full_zone)
		self.combo = self.combo+1 if cnt > 0 else 0
		self.score += (self.combo-1) * 50 * self.level if self.combo > 1 and self.level != None else (self.combo-1) * 50 if self.combo > 1 else 0
		if self.combo > 1:
			self.prev_clear_text.append(str(self.combo-1)+" COMBO")
		print(self.prev_clear_text)
		return cnt > 0

	def clearZone(self): # basically clearLines but for zone
		res, cnt = [], 0 # resultant matrix, number of lines cleared
		for i in range(self.matrix.shape[0]):
			if not np.all((self.matrix[i] > 0)): 
				res.append(self.matrix[i][:])
			else:
				cnt += 1
		for i in range(cnt):
			res.append(np.ones(self.matrix.shape[1])*8) # append cleared lines to bottom of stack
		while len(res) < self.matrix.shape[0]:
			res.insert(0,np.zeros(self.matrix.shape[1]))
		self.matrix = np.asarray(res,dtype=int)

	def zoneReady(self):
		return self.current_zone >= self.full_zone

	def activateZone(self):
		if self.zoneReady() and not self.zone_state:
			self.zone_state = True
			self.prev_clear_text.clear()

	def leaveZone(self):
		if self.zone_state:
			self.current_zone = 0
			self.zone_state = False
			score_incr, clear_text = scoring.zoneScore(self.matrix)
			self.score += score_incr
			self.prev_clear_text = clear_text
			self.removeTetromino()
			res = []
			for i in range(self.matrix.shape[0]): # remove zone lines
				if not np.all((self.matrix[i] > 0)): 
					res.append(self.matrix[i][:])
			while len(res) < self.matrix.shape[0]:
				res.insert(0,np.zeros(self.matrix.shape[1]))
			self.matrix = np.asarray(res,dtype=int)
			self.placeTetromino()

	def resetMatrix(self,clear_lines=True,clear_score=True):
		temp1 = 0
		temp2 = 0
		if not clear_lines:
			temp1 = self.lines_cleared
		if not clear_score:
			temp2 = self.score
		self.__init__()
		self.lines_cleared = temp1
		self.score = temp2
		