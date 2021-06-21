import numpy as np

scoringTable = {
	"":0,
	"SINGLE":100,
	"MINI T-SPIN":100,
	"MINI T-SPIN SINGLE":200,
	"DOUBLE":300,
	"T-SPIN":400,
	"MINI T-SPIN DOUBLE":400,
	"TRIPLE":500,
	"B2B MINI T-SPIN DOUBLE":600,
	"QUADRUPLE":800,
	"T-SPIN SINGLE":800,
	"B2B T-SPIN SINGLE":1200,
	"B2B QUADRUPLE":1200,
	"T-SPIN DOUBLE":1200,
	"T-SPIN TRIPLE":1600,
	"B2B T-SPIN DOUBLE":1800,
	"B2B T-SPIN TRIPLE":2400,
	"PERFECT CLEAR":3000
}

def filledLines(matrix): # returns number of filled lines, total lines
	cnt = 0
	total = 0
	for i in range(matrix.shape[0]):
		if np.all((matrix[i] > 0)): 
			cnt += 1
		if not np.all((matrix[i] == 0)):
			total += 1
	return cnt, total

def isRotationMini(prev2moves):
	print(prev2moves)
	if prev2moves[1][0] == "AUTOLOCK" or (prev2moves[1][0] == "TRANSLATION" and prev2moves[1][1]==0):
		if prev2moves[0][1] != None:
			return prev2moves[0][0] == "ROTATION", prev2moves[0][1] < 2
	else:
		return False, False

def isTspin(matrix, mino_locations, prev2moves):
	isRotation, isMini = isRotationMini(prev2moves)
	if not isRotation:
		return False, False

	mino_locations = sorted(mino_locations)
	center = mino_locations[1] # find center mino of T piece
	if not (center[0] == mino_locations[0][0] or center[1] == mino_locations[0][1]):
		center = mino_locations[2]
	front = None # find front mino of T piece
	for i in range(4):
		cur = mino_locations[0]
		if cur[0] != mino_locations[1][0] and mino_locations[1][0] == mino_locations[2][0] and mino_locations[2][0] == mino_locations[3][0]:
			front = cur
			break
		elif cur[1] != mino_locations[1][1] and mino_locations[1][1] == mino_locations[2][1] and mino_locations[2][1] == mino_locations[3][1]:
			front = cur
			break
		mino_locations.pop(0)
		mino_locations.append(cur)

	front_cnt = 0 # count number of squares diagonally adjacent to center that are occupied
	back_cnt = 0
	check = [(center[0]-1,center[1]-1),(center[0]-1,center[1]+1),(center[0]+1,center[1]-1),(center[0]+1,center[1]+1)]
	for pos in check:
		if pos[0] >= 0:
			if pos[0] >= matrix.shape[0] or pos[1] < 0 or pos[1] >= matrix.shape[1]:
				back_cnt += 1
			else:
				if pos[0] == front[0]+1 or pos[0] == front[0]-1 or pos[1] == front[1]+1 or pos[1] == front[1]-1:
					front_cnt += 1 if matrix[pos[0],pos[1]] else 0
				else:
					back_cnt += 1 if matrix[pos[0],pos[1]] else 0
	return front_cnt + back_cnt >= 3, back_cnt == 2 and front_cnt == 1 and isMini

def clearType(matrix, tetromino, mino_locations, b2b, prev2moves):
	lines_cleared, total_lines = filledLines(matrix)
	clearText = []
	b2b_next = False

	if lines_cleared == total_lines and lines_cleared > 0:
		clearText.append("PERFECT CLEAR")

	res = ""
	if lines_cleared == 4: 
		res += "B2B " if b2b else ""
		res += "QUADRUPLE"
		b2b_next = True
		clearText.append(res)
		return clearText, b2b_next
		
	mini = False
	tspin = False
	if tetromino == "T":
		tspin, mini = isTspin(matrix,mino_locations,prev2moves)
		if tspin and lines_cleared>0:
			b2b_next = True

	res += "B2B " if b2b and tspin and lines_cleared > 0 else ""
	res += "MINI " if mini else ""
	res += "T-SPIN " if tspin and lines_cleared > 0 else "T-SPIN" if tspin and lines_cleared == 0 else ""
	res += "TRIPLE" if lines_cleared == 3 else "DOUBLE" if lines_cleared == 2 else "SINGLE" if lines_cleared == 1 else ""
	clearText.append(res)
	
	if lines_cleared == 0:
		return clearText, b2b
	return clearText, b2b_next

def calcScore(matrix, tetromino, mino_locations, level, b2b, prev2moves): # combo, soft drop, and hard drop scores should be implemented in matrix.py
	score = 0
	clearText, b2b_next = clearType(matrix,tetromino,mino_locations,b2b,prev2moves)
	if level != None:
		for i in clearText:
			score += scoringTable[i] * level
	else:
		for i in clearText:
			score += scoringTable[i]
	return score, clearText, b2b_next
