import copy
import numpy as np
import random
from . import tetromino
from . import rotations
from . import scoring
from . import constants
from .logger import logger

class Matrix:
	# colour and index assignment
	index2rgb = {0:(0,0,0),1:(0,255,255),2:(0,0,255),3:(255,128,0),4:(255,255,0),5:(0,255,0),6:(255,0,255),7:(255,0,0),8:(64,64,64)}
	tetromino2rgb = {'I':(0,255,255),'J':(0,0,255),'L':(255,128,0),'O':(255,255,0),'S':(0,255,0),'T':(255,0,255),'Z':(255,0,0)}
	tetromino2index = {'I':1,'J':2,'L':3,'O':4,'S':5,'T':6,'Z':7}

	tetromino2matrix = {
		'I':np.array([[1,1,1,1]],dtype=int),
		'J':np.array([[2,0,0],
						[2,2,2]],dtype=int),
		'L':np.array([[0,0,3],
						[3,3,3]],dtype=int),
		'O':np.array([[4,4],
						[4,4]],dtype=int),
		'S':np.array([[0,5,5],
						[5,5,0]],dtype=int),
		'T':np.array([[0,6,0],
						[6,6,6]],dtype=int),
		'Z':np.array([[7,7,0],
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

	def __init__(self, game_mode=constants.GameMode.ZEN, screen_dim=None, matrix=None):

		if matrix is not None:
			game_mode = matrix.game_mode
			screen_dim = matrix.screen_dim
		
		if screen_dim is not None:
			self.screen_dim = screen_dim
			self.mino_dim = 2 * screen_dim[1] // 60 # dimensions in number of pixels (only used for GUI) # matrix height should be roughly 2/3 of screen height
			self.width = self.mino_dim * 10 # dimensions in number of pixels (only used for GUI)
			self.height = self.mino_dim * 20 # dimensions in number of pixels (only used for GUI)
			self.topleft = (screen_dim[0] - self.width) // 2, (screen_dim[1] - self.height) // 2 # position of the topleft coordinates of the matrix (only used for GUI)
		self.matrix = matrix.matrix.copy() if matrix is not None else np.zeros((22,10),dtype=int)
		self.level = matrix.level if matrix is not None else None
		self.score = matrix.score if matrix is not None else 0
		self.lines_cleared = matrix.lines_cleared if matrix is not None else 0
		self.tetrominos = matrix.tetrominos.copy() if matrix is not None else tetromino.Tetromino()
		self.current_tetromino = matrix.current_tetromino if matrix is not None else ""
		self.mino_locations = copy.copy(matrix.mino_locations) if matrix is not None else []
		self.tetromino_orientation = matrix.tetromino_orientation if matrix is not None else 0 # keeps track of orientation of current tetromino (0 to 3)
		self.hold_available = matrix.hold_available if matrix is not None else False
		self.placed_tetromino = matrix.placed_tetromino if matrix is not None else False # keeps track whether tetromino was placed into matrix yet
		self.combo = matrix.combo if matrix is not None else 0
		self.b2b = matrix.b2b if matrix is not None else False
		self.prev2moves = copy.copy(matrix.prev2moves) if matrix is not None else []
		self.prev_clear_text = copy.copy(matrix.prev_clear_text) if matrix is not None else []
		self.prev_move_score = copy.copy(matrix.prev_move_score) if matrix is not None else 0 # score of previous move
		self.prev_lines_cleared = copy.copy(matrix.prev_lines_cleared) if matrix is not None else 0 # number of lines cleared by previous move
		self.cur_score_incr = copy.copy(matrix.cur_score_incr) if matrix is not None else 0 # score of current sequence of moves
		self.clear_text = copy.copy(matrix.clear_text) if matrix is not None else [] # used by gameui
		self.track_clear_text = copy.copy(matrix.track_clear_text) if matrix is not None else [] # used by gameui
		self.clear_flag = matrix.clear_flag if matrix is not None else None # used by gameui
		self.current_zone = matrix.current_zone if matrix is not None else 0
		self.full_zone = matrix.full_zone if matrix is not None else 40
		self.zone_state = matrix.zone_state if matrix is not None else False
		self.game_over = matrix.game_over if matrix is not None else False
		self.game_mode = game_mode
		self.objective = matrix.objective if matrix is not None else None
		self.objective_met = matrix.objective_met if matrix is not None else None
		if matrix is None:
			self.setup()

	def setup(self):
		if self.game_mode == constants.GameMode.ZEN:
			self.objective = None
		elif self.game_mode == constants.GameMode.SPRINT:
			self.objective = 40
		elif self.game_mode == constants.GameMode.JOURNEY:
			self.objective = 150
			self.level = 1
		elif self.game_mode == constants.GameMode.VERSUS:
			self.objective = None
		else:
			raise Exception("Unknown Game Mode")

	def gameOverProcess(self):
		if self.game_over:
			if self.game_mode == constants.GameMode.ZEN:
				self.resetMatrix(False,False)
				self.addTetromino()
			elif self.game_mode == constants.GameMode.SPRINT:
				pass
			elif self.game_mode == constants.GameMode.JOURNEY:
				pass

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
			self.cur_score_incr += score_incr
			self.score += self.cur_score_incr
			self.b2b = b2b_next
			self.prev_clear_text = clear_text
			self.prev_move_score = self.cur_score_incr
			self.cur_score_incr = 0

			self.clearLines() # clear any filled lines before adding next tetromino
			self.tetrominos.nextTetromino()
			self.current_tetromino = self.tetrominos.getCurrentTetromino()
			self.tetromino_orientation = 0
			self.mino_locations.clear()
			self.mino_locations = self.spawnLocations[self.current_tetromino].copy()

			for i in self.mino_locations: # topping out determined if piece can spawn
				if self.matrix[i[0],i[1]] != 0:
					# print("Topped out", file=sys.stderr)
					self.game_over = True
					self.gameOverProcess()
					return
					# raise Exception("Topped out")

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
				if self.matrix[i[0],i[1]] != 0: # check for topping out
					self.leaveZone(topped_out=True)

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
					self.game_over = True
					self.gameOverProcess()
					return
					# raise Exception("Topped out")
		else:
			for i in self.mino_locations: 
				if self.matrix[i[0],i[1]] != 0:
					self.leaveZone(topped_out=True)

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
		self.cur_score_incr += 2*dist
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
		self.cur_score_incr += 1
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
		self.prev_lines_cleared = cnt
		if self.game_mode == constants.GameMode.JOURNEY:
			self.level = self.lines_cleared//10 + 1
		if self.objective is not None:
			if self.lines_cleared >= self.objective:
				self.objective_met = True
		self.current_zone = min(self.current_zone+cnt,self.full_zone)
		self.combo = self.combo+1 if cnt > 0 else 0
		self.cur_score_incr += (self.combo-1) * 50 * self.level if self.combo > 1 and self.level != None else (self.combo-1) * 50 if self.combo > 1 else 0
		if self.combo > 1:
			self.prev_clear_text.append(str(self.combo-1)+" COMBO")
		logger.info(self.prev_clear_text)
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

	def leaveZone(self, topped_out=False):
		if self.zone_state:
			self.current_zone = 0
			self.zone_state = False
			score_incr, clear_text = scoring.zoneScore(self.matrix)
			self.cur_score_incr += score_incr
			self.prev_clear_text = clear_text
			self.prev_move_score = self.cur_score_incr
			self.cur_score_incr = 0
			logger.info(self.prev_clear_text)
			if not topped_out:
				self.removeTetromino()
			res = []
			for i in range(self.matrix.shape[0]): # remove zone lines
				if not np.all((self.matrix[i] > 0)): 
					res.append(self.matrix[i][:])
			while len(res) < self.matrix.shape[0]:
				res.insert(0,np.zeros(self.matrix.shape[1]))
			self.matrix = np.asarray(res,dtype=int)
			if not topped_out:
				self.placeTetromino()

	def appendGarbage(self, numLines):
		prev_hole_pos = None
		if self.matrix[21].sum() == 72: # last row is a garbage line (yucky but works for now)
			for i in range(10):
				if self.matrix[21,i] == 0:
					prev_hole_pos = i
		hole_candidates = [0,1,2,3,4,5,6,7,8,9] # 0 to 9 inclusive
		if prev_hole_pos is not None:
			hole_candidates.remove(prev_hole_pos)
		random.shuffle(hole_candidates)
		hole_pos = hole_candidates[0]
		garbage = np.ones(self.matrix.shape[1]) * 8
		garbage[hole_pos] = 0
		res = []
		for i in range(numLines):
			res.append(garbage)
		for i in reversed(self.matrix):
			res.insert(0,i)
			if len(res) == self.matrix.shape[0]:
				break
		self.matrix = np.asarray(res,dtype=int)

	def resetMatrix(self,clear_lines=True,clear_score=True):
		temp1 = 0
		temp2 = 0
		if not clear_lines:
			temp1 = self.lines_cleared
		if not clear_score:
			temp2 = self.score
		self.__init__(game_mode=self.game_mode,screen_dim=self.screen_dim)
		self.lines_cleared = temp1
		self.score = temp2
		
	def copy(self):
		return Matrix(matrix=self)
