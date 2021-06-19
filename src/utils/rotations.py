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

def checkValidPosition(matrix, mino_locations):
	pass

def rotateCW(matrix, tetromino, mino_locations, orientation):
	origin = getRelativeOrigin(tetromino,mino_locations,orientation)
	for j in range(4):
		res = translate(rot90cw(translate(mino_locations[j],-origin[0],-origin[1])),origin[0],origin[1])
		mino_locations.append((int(res[0]),int(res[1])))
	for j in range(4):
		mino_locations.pop(0)
	orientation += 1
	orientation %= 4
	return mino_locations, orientation

def rotateCCW(matrix, tetromino, mino_locations, orientation):
	origin = getRelativeOrigin(tetromino,mino_locations,orientation)
	for j in range(4):
		res = translate(rot90ccw(translate(mino_locations[j],-origin[0],-origin[1])),origin[0],origin[1])
		mino_locations.append((int(res[0]),int(res[1])))
	for j in range(4):
		mino_locations.pop(0)
	orientation -= 1
	orientation %= 4
	return mino_locations, orientation

def rotate180(matrix, tetromino, mino_locations, orientation):
	orientation = rotateCW(matrix, tetromino, mino_locations, orientation)[1]
	orientation = rotateCW(matrix, tetromino, mino_locations, orientation)[1]
	return mino_locations, orientation

genOrientations()
