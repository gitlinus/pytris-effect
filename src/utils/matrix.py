import numpy as np 
from . import tetromino

class Matrix:

	# colour assignment
	index2rgb = {0:(0,0,0),1:(0,255,255),2:(0,0,255),3:(255,128,0),4:(255,255,0),5:(0,255,0),6:(255,0,255),7:(255,0,0)}
	tetromino2rgb = {'I':(0,255,255),'J':(0,0,255),'L':(255,128,0),'O':(255,255,0),'S':(0,255,0),'T':(255,0,255),'Z':(255,0,0)}
	
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
