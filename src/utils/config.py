import pygame
from . import constants

# possible actions
actions = [
			constants.Action.ROTATE_CW, 
			constants.Action.ROTATE_CCW, 
			constants.Action.ROTATE_180, 
			constants.Action.SHIFT_LEFT, 
			constants.Action.SHIFT_RIGHT,
			constants.Action.SOFT_DROP,
			constants.Action.HARD_DROP,
			constants.Action.SWAP_HOLD, 
			constants.Action.RESET,
			constants.Action.ACTIVATE_ZONE,
			constants.Action.PAUSE
		]

# default control mappping
key2action = { 
	pygame.K_UP:constants.Action.ROTATE_CW,
	pygame.K_z:constants.Action.ROTATE_CCW,
	pygame.K_x:constants.Action.ROTATE_180,
	pygame.K_LEFT:constants.Action.SHIFT_LEFT,
	pygame.K_RIGHT:constants.Action.SHIFT_RIGHT,
	pygame.K_DOWN:constants.Action.SOFT_DROP,
	pygame.K_SPACE:constants.Action.HARD_DROP,
	pygame.K_LSHIFT:constants.Action.SWAP_HOLD,
	pygame.K_r:constants.Action.RESET,
	pygame.K_c:constants.Action.ACTIVATE_ZONE,
	pygame.K_p:constants.Action.PAUSE
}

action2key = {
	constants.Action.ROTATE_CW:None,
	constants.Action.ROTATE_CCW:None,
	constants.Action.ROTATE_180:None,
	constants.Action.SHIFT_LEFT:None, 
	constants.Action.SHIFT_RIGHT:None,
	constants.Action.SOFT_DROP:None,
	constants.Action.HARD_DROP:None,
	constants.Action.SWAP_HOLD:None,
	constants.Action.RESET:None,
	constants.Action.ACTIVATE_ZONE:None,
	constants.Action.PAUSE:None
}

gravity = 1
das = 100
arr = 4
soft_drop_speed = 20
MAX_ARR = 3000
MAX_DAS = 3000
MAX_SOFT_DROP_SPEED = 1000

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

def key2str(key):
	return pygame.key.name(key)

getKeyAssignments()

# colours
black = 0, 0, 0
white = 255, 255, 255
grey = 128, 128, 128
yellow = 255, 255, 0
purple = 255, 0, 255
light_blue = 0, 127, 255

# (TODO): create separate configs for different classes
# game related configs
