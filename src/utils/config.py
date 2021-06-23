import pygame

# possible actions
actions = ["ROTATE_CW", "ROTATE_CCW", "ROTATE_180", "SHIFT_LEFT", 
			"SHIFT_RIGHT", "SOFT_DROP", "HARD_DROP", "SWAP_HOLD", 
			"RESET", "ACTIVATE_ZONE"]

# default control mappping
key2action = { 
	pygame.K_UP:"ROTATE_CW",
	pygame.K_z:"ROTATE_CCW",
	pygame.K_x:"ROTATE_180",
	pygame.K_LEFT:"SHIFT_LEFT",
	pygame.K_RIGHT:"SHIFT_RIGHT",
	pygame.K_DOWN:"SOFT_DROP",
	pygame.K_SPACE:"HARD_DROP",
	pygame.K_LSHIFT:"SWAP_HOLD",
	pygame.K_r:"RESET",
	pygame.K_c:"ACTIVATE_ZONE"
}

action2key = {
	"ROTATE_CW":None, "ROTATE_CCW":None, "ROTATE_180":None, "SHIFT_LEFT":None, 
	"SHIFT_RIGHT":None, "SOFT_DROP":None, "HARD_DROP":None, "SWAP_HOLD":None,
	"RESET":None, "ACTIVATE_ZONE":None
}

def getKeyAssignments(): # reverse of key2action 
	for i in key2action.items():
		action2key[i[1]] = i[0]

def addControl(key,action):
	if action in actions:
		if key not in key2action and action2key[action]==None:
			key2action[key] = action
			action2key[action] = key
			return True
	return False

def deleteControl(key):
	if key in key2action:
		action2key[key2action[key]] = None
		del key2action[key]	
		return True
	return False

getKeyAssignments()
