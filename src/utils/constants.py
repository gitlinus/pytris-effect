from enum import Enum

class GameMode(Enum):
	JOURNEY = 1
	SPRINT = 2
	ZEN = 3
	VERSUS = 4

class Action(Enum):
	ROTATE_CW = 1 
	ROTATE_CCW = 2
	ROTATE_180 = 3 
	SHIFT_LEFT = 4
	SHIFT_RIGHT = 5
	SOFT_DROP = 6
	HARD_DROP = 7
	SWAP_HOLD = 8
	RESET = 9
	ACTIVATE_ZONE = 10
	PAUSE = 11
