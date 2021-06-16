import numpy as np 
from . import tetromino

class Matrix:

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

	def __init__(self, mino_dim=30):
		self.mino_dim = mino_dim
		self.width = mino_dim * 10
		self.height = mino_dim * 20
		self.matrix = np.zeros((22,10),dtype=int)
		self.score = 0
		self.tetrominos = tetromino.Tetromino()
		self.current_tetromino = ""

	def dim(self):
		return self.width, self.height

	def getScore(self):
		return self.score

	def addTetromino(self): # set piece spawn location
		self.tetrominos.nextTetromino()
		self.current_tetromino = self.tetrominos.getCurrentTetromino()
		spawn = self.tetromino2matrix[self.current_tetromino]
		self.matrix[(2-spawn.shape[0]):2,
		((10-spawn.shape[1])//2):((10-spawn.shape[1])//2)+spawn.shape[1]] += spawn
