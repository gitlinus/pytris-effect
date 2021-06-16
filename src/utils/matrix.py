import numpy as np 

class Matrix:

	def __init__(self, mino_dim=30):
		self.mino_dim = mino_dim
		self.width = mino_dim * 10
		self.height = mino_dim * 20
		self.matrix = np.zeros((22,10),dtype=int)
		self.score = 0

	def dim(self):
		return self.width, self.height

	def getScore(self):
		return self.score
