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
		self.tetrominos = tetromino.Tetromino()
		self.current_tetromino = ""
		self.mino_locations = []

	def dim(self):
		return self.width, self.height

	def getScore(self):
		return self.score

	def addTetromino(self): # set piece spawn location
		self.tetrominos.nextTetromino()
		self.current_tetromino = self.tetrominos.getCurrentTetromino()
		self.mino_locations.clear()
		self.mino_locations = self.spawnLocations[self.current_tetromino]

		for i in self.mino_locations: 
			if self.matrix[i[0],i[1]] != 0:
				raise Exception("Topped out")

		for i in self.mino_locations:
			self.matrix[i[0],i[1]] = self.tetromino2index[self.current_tetromino]

	def enforceGravity(self):
		"""
		shift mino locations down by 1, check for collisions, 
		clear old locations, store new locations
		"""
		for i in self.mino_locations:
			if i[0]+1 == 22 or (self.matrix[i[0]+1,i[1]] != 0 and (i[0]+1,i[1]) not in self.mino_locations): # cannot shift down further
				if i[0]==0 or i[0]==1:
					raise Exception("Topped out")
				return False

		temp = []
		for i in self.mino_locations:
			self.matrix[i[0],i[1]] = 0
			temp.append((i[0]+1,i[1]))

		for i in temp:
			self.matrix[i[0],i[1]] = self.tetromino2index[self.current_tetromino]

		self.mino_locations = temp

		return True
