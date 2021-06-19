import numpy as np 

# single cw rotation:
"""
Mark center of all rotation states as a relative origin 
Translate relative origin to (0,0)
Rotate minos cw 90 degrees (x,y) -> (y,-x)
Translate back 
"""

rotationStates = {
	'I':[
		np.asarray([[0,0,0,0],
					[1,1,1,1],
					[0,0,0,0],
					[0,0,0,0]],dtype=int)],
	'J':[
		np.asarray([[2,0,0],
					[2,2,2],
					[0,0,0],],dtype=int)],
	'L':[
		np.asarray([[0,0,3],
					[3,3,3],
					[0,0,0]],dtype=int)],
	'O':[
		np.asarray([[4,4],
					[4,4]],dtype=int)],
	'S':[
		np.asarray([[0,5,5],
					[5,5,0],
					[0,0,0]],dtype=int)],
	'T':[
		np.asarray([[0,6,0],
					[6,6,6],
					[0,0,0]],dtype=int)],
	'Z':[
		np.asarray([[7,7,0],
					[0,7,7],
					[0,0,0]],dtype=int)]
}

kickTable = { # kick values in (x,y) -> (col, row)
	'I':{
		"0>>1":[(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
		"1>>2":[(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
		"2>>3":[(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
		"3>>0":[(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
		"0>>3":[(0,0),(-1,0),(2,0),(-1,2),(2,-1)]
		},
	'J':{
		"0>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>2":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"2>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"3>>0":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"0>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)]
		},
	'L':{
		"0>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>2":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"2>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"3>>0":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"0>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)]
		},
	'O':{ # for the sake of redundancy 
		"0>>1":[(0,0)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0)],
		"1>>2":[(0,0)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0)],
		"2>>3":[(0,0)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0)],
		"3>>0":[(0,0)],
		"0>>3":[(0,0)]
		},
	'S':{
		"0>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>2":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"2>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"3>>0":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"0>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)]
		},
	'T':{
		"0>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>2":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"2>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"3>>0":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"0>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)]
		},
	'Z':{
		"0>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"0>>2":[(0,0)],
		"1>>0":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>2":[(0,0),(1,0),(1,-1),(0,2),(1,2)],
		"1>>3":[(0,0)],
		"2>>0":[(0,0)],
		"2>>1":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
		"2>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
		"3>>1":[(0,0)],
		"3>>2":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"3>>0":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
		"0>>3":[(0,0),(1,0),(1,1),(0,-2),(1,-2)]
		}
}

def genOrientations(): # rotation states generated according to srs.png (indexed from 0 to 3)
	for i in rotationStates.keys():
		for state in range(3):
			rotationStates[i].append(np.rot90(rotationStates[i][state],-1))

def translate(position, dx, dy):
	return position[0]+dx, position[1]+dy

def rot90cw(position):
	return position[1], -position[0]

def rot90ccw(position):
	return -position[1], position[0]

def getRelativeOrigin(tetromino, mino_locations, orientation):
	rotationBox = rotationStates[tetromino][orientation]
	positions = sorted(mino_locations)
	origin = None
	for i in range(rotationBox.shape[0]): # use coordinate of top left corner of box to find center
		for j in range(rotationBox.shape[1]):
			if rotationBox[i,j] != 0:
				origin = positions[0][0]-i + (rotationBox.shape[0]-1) / 2, positions[0][1]-j + (rotationBox.shape[1]-1) / 2
				return origin

def validPosition(matrix, mino_locations):
	for i in mino_locations:
		if matrix[i[0],i[1]] != 0 and (i[0],i[1]) not in mino_locations:
			return False
	return True

def getKicks(matrix, tetromino, mino_locations, state_begin, state_end):
	kicks = kickTable[tetromino][str(state_begin)+">>"+str(state_end)]
	for kick in kicks:
		for pos in mino_locations:
			mino_locations.append((pos[0]+kick[1],pos[1]+kick[0]))
		for i in range(4):
			mino_locations.pop(0)
		if validPosition(matrix,mino_locations):
			return True
	return False

def rotateCW(matrix, tetromino, mino_locations, orientation):
	candidates = mino_locations.copy()
	origin = getRelativeOrigin(tetromino,candidates,orientation)
	for i in range(4):
		res = translate(rot90cw(translate(candidates,-origin[0],-origin[1])),origin[0],origin[1])
		candidates.append((int(res[0]),int(res[1])))
	for i in range(4):
		candidates.pop(0)
	if getKicks(matrix, candidates, orientation, (orientation+1)%4):
		orientation += 1
		orientation %= 4
		mino_locations = candidates
	return orientation

def rotateCCW(matrix, tetromino, mino_locations, orientation):
	candidates = mino_locations.copy()
	origin = getRelativeOrigin(tetromino,candidates,orientation)
	for i in range(4):
		res = translate(rot90ccw(translate(candidates,-origin[0],-origin[1])),origin[0],origin[1])
		candidates.append((int(res[0]),int(res[1])))
	for i in range(4):
		candidates.pop(0)
	if getKicks(matrix, candidates, orientation, (orientation-1)%4):
		orientation -= 1
		orientation %= 4
		mino_locations = candidates
	return orientation

def rotate180(matrix, tetromino, mino_locations, orientation):
	candidates = mino_locations.copy()
	for i in range(2): # do 2 cw rotations
		origin = getRelativeOrigin(tetromino,candidates,orientation+i)
		for i in range(4):
			res = translate(rot90cw(translate(candidates,-origin[0],-origin[1])),origin[0],origin[1])
			candidates.append((int(res[0]),int(res[1])))
		for i in range(4):
			candidates.pop(0)
	if validPosition(matrix,candidates):
		orientation += 2
		orientation %= 4
		mino_locations = candidates
	return orientation

genOrientations()
