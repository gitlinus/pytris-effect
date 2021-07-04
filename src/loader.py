import sys
import pygame 
import pyautogui
from . import gameui
from .utils import config
#Loading scenes

pygame.init()

keyList = [
pygame.K_BACKSPACE,
pygame.K_TAB,
pygame.K_CLEAR,
pygame.K_RETURN,
pygame.K_PAUSE,
pygame.K_ESCAPE,
pygame.K_SPACE,
pygame.K_EXCLAIM,
pygame.K_QUOTEDBL,
pygame.K_HASH,
pygame.K_DOLLAR,
pygame.K_AMPERSAND,
pygame.K_QUOTE,
pygame.K_LEFTPAREN,
pygame.K_RIGHTPAREN,
pygame.K_ASTERISK,
pygame.K_PLUS,
pygame.K_COMMA,
pygame.K_MINUS,
pygame.K_PERIOD,
pygame.K_SLASH,
pygame.K_0,
pygame.K_1,
pygame.K_2,
pygame.K_3,
pygame.K_4,
pygame.K_5,
pygame.K_6,
pygame.K_7,
pygame.K_8,
pygame.K_9,
pygame.K_COLON,
pygame.K_SEMICOLON,
pygame.K_LESS,
pygame.K_EQUALS,
pygame.K_GREATER,
pygame.K_QUESTION,
pygame.K_AT,
pygame.K_LEFTBRACKET,
pygame.K_BACKSLASH,
pygame.K_RIGHTBRACKET,
pygame.K_CARET,
pygame.K_UNDERSCORE,
pygame.K_BACKQUOTE,
pygame.K_a,
pygame.K_b,
pygame.K_c,
pygame.K_d,
pygame.K_e,
pygame.K_f,
pygame.K_g,
pygame.K_h,
pygame.K_i,
pygame.K_j,
pygame.K_k,
pygame.K_l,
pygame.K_m,
pygame.K_n,
pygame.K_o,
pygame.K_p,
pygame.K_q,
pygame.K_r,
pygame.K_s,
pygame.K_t,
pygame.K_u,
pygame.K_v,
pygame.K_w,
pygame.K_x,
pygame.K_y,
pygame.K_z,
pygame.K_DELETE,
pygame.K_KP0,
pygame.K_KP1,
pygame.K_KP2,
pygame.K_KP3,
pygame.K_KP4,
pygame.K_KP5,
pygame.K_KP6,
pygame.K_KP7,
pygame.K_KP8,
pygame.K_KP9,
pygame.K_KP_PERIOD,
pygame.K_KP_DIVIDE,
pygame.K_KP_MULTIPLY,
pygame.K_KP_MINUS,
pygame.K_KP_PLUS,
pygame.K_KP_ENTER,
pygame.K_KP_EQUALS,
pygame.K_UP,
pygame.K_DOWN,
pygame.K_RIGHT,
pygame.K_LEFT,
pygame.K_INSERT,
pygame.K_HOME,
pygame.K_END,
pygame.K_PAGEUP,
pygame.K_PAGEDOWN,
pygame.K_F1,
pygame.K_F2,
pygame.K_F3,
pygame.K_F4,
pygame.K_F5,
pygame.K_F6,
pygame.K_F7,
pygame.K_F8,
pygame.K_F9,
pygame.K_F10,
pygame.K_F11,
pygame.K_F12,
pygame.K_F13,
pygame.K_F14,
pygame.K_F15,
pygame.K_NUMLOCK,
pygame.K_CAPSLOCK,
pygame.K_SCROLLOCK,
pygame.K_RSHIFT,
pygame.K_LSHIFT,
pygame.K_RCTRL,
pygame.K_LCTRL,
pygame.K_RALT,
pygame.K_LALT,
pygame.K_RMETA,
pygame.K_LMETA,
pygame.K_LSUPER,
pygame.K_RSUPER,
pygame.K_MODE,
pygame.K_HELP,
pygame.K_PRINT,
pygame.K_SYSREQ,
pygame.K_BREAK,
pygame.K_MENU,
pygame.K_POWER,
pygame.K_EURO
]

class Label:
	def __init__(self, font, text, colour, position, anchor="topleft"):
		self.image = font.render(text, True, colour)
		self.rect = self.image.get_rect()
		setattr(self.rect, anchor, position)

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class Button:
	def __init__(self, button_colour, x, y, width, height, font, text_colour, text=""):
		self.button_colour = button_colour
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = font.render(text, True, text_colour)
		self.text_rect = self.text.get_rect()
		setattr(self.text_rect,"center",(x+width/2,y+height/2))

	def draw(self, surface, outline_colour=None):
		if outline_colour: 
			pygame.draw.rect(surface, outline_colour, (self.x-2,self.y-2,self.width+4,self.height+4))
		pygame.draw.rect(surface, self.button_colour, (self.x,self.y,self.width,self.height))
		surface.blit(self.text, self.text_rect)

	def isOver(self, pos):
		#pos is the mouse position
		return pos[0] > self.x and pos[0] < self.x + self.width and pos[1] > self.y and pos[1] < self.y + self.height

class InputBox:

	COLOUR_INACTIVE = 255,255,255
	COLOUR_ACTIVE = pygame.Color('dodgerblue')

	def __init__(self, x, y, width, height, font_size=32, text='', config_attr=None):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.FONT = pygame.font.Font(None, font_size)
		self.rect = pygame.Rect(x, y, width, height)
		self.colour = self.COLOUR_INACTIVE
		self.text = text
		self.txt_surface = self.FONT.render(text, True, self.colour)
		self.active = False
		self.text_rect = self.txt_surface.get_rect()
		setattr(self.text_rect,"center",(x+width/2,y+height/2))
		self.config_attr = config_attr

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			# If the user clicked on the input_box rect.
			if self.rect.collidepoint(event.pos):
				# Toggle the active variable.
				self.active = not self.active

			else:
				self.active = False
			# Change the current colour of the input box.
			self.colour = self.COLOUR_ACTIVE if self.active else self.COLOUR_INACTIVE
			# Re-render the text.
			self.txt_surface = self.FONT.render(self.text, True, self.colour)
			self.text_rect = self.txt_surface.get_rect()
			setattr(self.text_rect,"center",(self.x+self.width/2,self.y+self.height/2))
			
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					if self.config_attr == "DAS":
						config.das = max(min(config.MAX_DAS,int(self.text)),0)
						self.text = str(config.das)
					elif self.config_attr == "ARR":
						config.arr = max(min(config.MAX_ARR,int(self.text)),0)
						self.text = str(config.arr)
					elif self.config_attr == "SOFT_DROP_SPEED":
						config.soft_drop_speed = max(min(config.MAX_SOFT_DROP_SPEED,int(self.text)),1)
						self.text = str(config.soft_drop_speed)
					self.active = False
					self.colour = self.COLOUR_ACTIVE if self.active else self.COLOUR_INACTIVE
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					if event.unicode.isnumeric():
						self.text += event.unicode
				# Re-render the text.
				self.txt_surface = self.FONT.render(self.text, True, self.colour)
				self.text_rect = self.txt_surface.get_rect()
				setattr(self.text_rect,"center",(self.x+self.width/2,self.y+self.height/2))

	def update(self):
		# Resize the box if the text is too long.
		width = max(50, self.txt_surface.get_width()+10)
		self.rect.w = width

	def draw(self, screen):
		# Blit the text.
		screen.blit(self.txt_surface, self.text_rect)
		# Blit the rect.
		pygame.draw.rect(screen, self.colour, self.rect, 2)

class Loader():

	BG_COLOR = pygame.Color('gray12')
	BLUE = pygame.Color('dodgerblue')
	WHITE = 255,255,255
	BLACK = 0,0,0
	GREY = 128,128,128
	RED = 255,0,0
	
	def __init__(self, scene="TITLE", game_mode=None, objective=None, prev=None):
		self.screen_width, self.screen_height = pyautogui.size()
		self.vertical_offset = 50
		self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
		self.screen = pygame.display.set_mode(size=self.screen_size, flags=pygame.SCALED)
		pygame.display.set_caption('Pytris Effect')

		self.title = None
		self.button_width = None
		self.button_height = None
		self.title_font = pygame.font.Font(None, self.screen_width//16)
		self.button_font = pygame.font.Font(None, self.screen_width//24)

		# title screen buttons
		self.play = None
		self.settings = None

		# game selection screen buttons
		self.journey = None
		self.sprint = None
		self.zen = None
		self.versus = None
		self.goback = None

		# pause screen buttons
		self.resume = None
		self.gohome = None

		# start over screen
		self.restart = None
		self.game_mode = game_mode

		# end screen
		self.objective = objective

		# settings screen
		self.rotate_cw = None
		self.rotate_ccw = None
		self.rotate_180 = None
		self.shift_left = None
		self.shift_right = None
		self.hard_drop = None
		self.soft_drop = None
		self.swap_hold = None
		self.reset = None
		self.activate_zone = None
		self.pause = None
		self.das = None
		self.arr = None
		self.soft_drop_speed = None

		self.buttonList = []
		self.labelList = []
		self.inputBoxList = []
		self.exit_loop = False
		self.prev_screen = prev

		if scene == "TITLE":
			self.titleScreen()
		elif scene == "GAME SELECTION":
			self.gameSelectionScreen()
		elif scene == "PAUSE":
			self.pauseScreen()
		elif scene == "GAME OVER":
			self.gameOverScreen()
		elif scene == "END SCREEN":
			self.endScreen()
		elif scene == "SETTINGS":
			self.settingsScreen()
	
	def titleScreen(self):
		self.title = Label(self.title_font, "PYTRIS", self.BLUE, (self.screen_width/2, self.screen_height/3), "center")
		self.button_width = self.title.rect.width
		self.button_height = self.title.rect.height
		self.play = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*0.5+self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"PLAY")
		self.settings = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*1.5+2*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"SETTINGS")
		self.buttonList = [self.play, self.settings]
	
	def gameSelectionScreen(self):
		self.title = Label(self.title_font, "GAME MODES", self.BLUE, (self.screen_width/2, self.screen_height/4), "center")
		self.button_width = self.title.rect.width
		self.button_height = self.title.rect.height
		self.journey = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*0.5+self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"JOURNEY")
		self.sprint = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*1.5+2*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"SPRINT")
		self.zen = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*2.5+3*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"ZEN")
		self.versus = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*3.5+4*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"VERSUS")
		self.goback = Button(self.BLACK,self.title.rect.centerx-self.button_width*1.5,
									self.screen_height-3*self.button_height,
									self.button_width/2,self.button_height,self.button_font,self.WHITE,"BACK")
		self.buttonList = [self.journey, self.sprint, self.zen, self.versus, self.goback]

	def pauseScreen(self):
		self.title = Label(self.title_font, "PAUSED", self.BLUE, (self.screen_width/2, self.screen_height/4), "center")
		self.button_width = self.title.rect.width
		self.button_height = self.title.rect.height
		self.resume = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*0.5+self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"RESUME")
		self.settings = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*1.5+2*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"SETTINGS")
		self.gohome = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*2.5+3*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"HOME")
		self.buttonList = [self.resume, self.settings, self.gohome]

	def gameOverScreen(self):
		self.title = Label(self.title_font, "GAME OVER", self.BLUE, (self.screen_width/2, self.screen_height/4), "center")
		self.button_width = self.title.rect.width
		self.button_height = self.title.rect.height

		if self.game_mode == "JOURNEY":
			self.labelList.append(Label(self.title_font, "SCORE: "+self.objective, self.BLUE, (self.screen_width/2, self.title.rect.centery+self.button_height*0.5+self.vertical_offset), "center"))

		self.restart = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*1.5+2*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"RESTART")
		self.gohome = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*2.5+3*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"HOME")
		self.buttonList = [self.restart, self.gohome]

	def endScreen(self):
		self.title = Label(self.title_font, "GAME COMPLETED", self.BLUE, (self.screen_width/2, self.screen_height/4), "center")
		self.button_width = self.title.rect.width
		self.button_height = self.title.rect.height

		if self.game_mode == "JOURNEY":
			self.labelList.append(Label(self.title_font, "SCORE: "+self.objective, self.BLUE, (self.screen_width/2, self.title.rect.centery+self.button_height*0.5+self.vertical_offset), "center"))
		elif self.game_mode == "SPRINT":
			self.labelList.append(Label(self.title_font, "TIME: "+self.objective, self.BLUE, (self.screen_width/2, self.title.rect.centery+self.button_height*0.5+self.vertical_offset), "center"))

		self.restart = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*1.5+2*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"RESTART")
		self.gohome = Button(self.BLACK,self.title.rect.centerx-self.button_width/2,
									self.title.rect.centery+self.button_height*2.5+3*self.vertical_offset,
									self.button_width,self.button_height,self.button_font,self.WHITE,"HOME")
		self.buttonList = [self.restart, self.gohome]

	def settingsScreen(self):
		self.title = Label(self.title_font, "SETTINGS", self.BLUE, (self.screen_width/2, self.screen_height/8), "center")
		self.button_width = self.title.rect.width
		self.button_height = self.title.rect.height
		j=0
		meow = True
		for i in config.actions:
			if meow:
				self.labelList.append(Label(self.button_font, i, self.WHITE, (self.title.rect.topleft[0]-1.5*self.button_width, self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2)))
				self.buttonList.append(Button(self.BLACK,self.title.rect.topleft[0]-0.5*self.button_width,self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2,self.button_width*3/4,self.labelList[0].rect.height,self.button_font,self.WHITE,config.key2str(config.action2key[i])))
				meow = False
			else:
				self.labelList.append(Label(self.button_font, i, self.WHITE, (self.title.rect.centerx, self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2)))
				self.buttonList.append(Button(self.BLACK,self.title.rect.centerx+1.2*self.button_width,self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2,self.button_width*3/4,self.labelList[0].rect.height,self.button_font,self.WHITE,config.key2str(config.action2key[i])))
				meow = True
				j += 1
			if i=="ROTATE_CW":
				self.rotate_cw = self.buttonList[-1]
			elif i=="ROTATE_CCW":
				self.rotate_ccw = self.buttonList[-1]
			elif i=="ROTATE_180":
				self.rotate_180 = self.buttonList[-1]
			elif i=="SHIFT_LEFT":
				self.shift_left = self.buttonList[-1]
			elif i=="SHIFT_RIGHT":
				self.shift_right = self.buttonList[-1]
			elif i=="SOFT_DROP":
				self.soft_drop = self.buttonList[-1]
			elif i=="HARD_DROP":
				self.hard_drop = self.buttonList[-1]
			elif i=="SWAP_HOLD":
				self.swap_hold = self.buttonList[-1]
			elif i=="RESET":
				self.reset = self.buttonList[-1]
			elif i=="ACTIVATE_ZONE":
				self.activate_zone = self.buttonList[-1]
			elif i=="PAUSE":
				self.pause = self.buttonList[-1]

		self.goback = Button(self.BLACK,self.title.rect.topleft[0]-1.5*self.button_width,
									self.title.rect.topleft[1],
									self.button_width/2,self.button_height,self.button_font,self.WHITE,"BACK")
		self.buttonList.append(self.goback)

		# das, arr, soft_drop_speed
		self.labelList.append(Label(self.button_font, "DAS", self.WHITE, (self.title.rect.centerx, self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2)))
		self.das = InputBox(self.title.rect.centerx+1.2*self.button_width,self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2,self.button_width*3/4,self.labelList[0].rect.height,font_size=self.screen_width//48,text=str(config.das),config_attr="DAS")
		self.inputBoxList.append(self.das)
		j+=1
		self.labelList.append(Label(self.button_font, "ARR", self.WHITE, (self.title.rect.topleft[0]-1.5*self.button_width, self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2)))
		self.arr = InputBox(self.title.rect.topleft[0]-0.5*self.button_width,self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2,self.button_width*3/4,self.labelList[0].rect.height,font_size=self.screen_width//48,text=str(config.arr),config_attr="ARR")
		self.inputBoxList.append(self.arr)
		self.labelList.append(Label(self.button_font, "SOFT_DROP_VEL", self.WHITE, (self.title.rect.centerx, self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2)))
		self.soft_drop_speed = InputBox(self.title.rect.centerx+1.2*self.button_width,self.title.rect.centery+self.button_height*(0.5+j)+(j+1)*self.vertical_offset/2,self.button_width*3/4,self.labelList[0].rect.height,font_size=self.screen_width//48,text=str(config.soft_drop_speed),config_attr="SOFT_DROP_SPEED")
		self.inputBoxList.append(self.soft_drop_speed)

	def changeControl(self, button, control):
		button.button_colour = self.RED
		self.iter()
		new_key = self.getKey()
		while (new_key is None):
			new_key = self.getKey()
		config.deleteControl(config.action2key[control])
		config.addControl(new_key,control)
		self.buttonList.clear()
		self.labelList.clear()
		self.settingsScreen()

	def getKey(self):
		keys = None
		done = False
		while not done:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					keys = pygame.key.get_pressed()
					done = True
					break
		for key in keyList:
			if keys[key] and key not in config.key2action:
				return key
		return None

	def resetLists(self):
		self.buttonList.clear()
		self.labelList.clear()
		self.inputBoxList.clear()

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			for box in self.inputBoxList:
				box.handle_event(event)
			if self.play in self.buttonList and self.play.isOver(pygame.mouse.get_pos()):
				self.resetLists()
				self.gameSelectionScreen()
			elif self.settings in self.buttonList and self.settings.isOver(pygame.mouse.get_pos()):
				self.resetLists()
				self.settingsScreen()
			elif self.goback in self.buttonList and self.goback.isOver(pygame.mouse.get_pos()):
				self.resetLists()
				if self.prev_screen is None:
					self.titleScreen()
				elif self.prev_screen == "PAUSE":
					self.pauseScreen()
			elif self.journey in self.buttonList and self.journey.isOver(pygame.mouse.get_pos()):
				gameui.GameUI(True,"JOURNEY").run()
			elif self.sprint in self.buttonList and self.sprint.isOver(pygame.mouse.get_pos()):
				gameui.GameUI(True,"SPRINT").run()
			elif self.zen in self.buttonList and self.zen.isOver(pygame.mouse.get_pos()):
				gameui.GameUI(True,"ZEN").run()
			elif self.versus in self.buttonList and self.versus.isOver(pygame.mouse.get_pos()):
				gameui.GameUI(True,"VERSUS").run()
			elif self.gohome in self.buttonList and self.gohome.isOver(pygame.mouse.get_pos()):
				self.resetLists()
				self.titleScreen()
			elif self.resume in self.buttonList and self.resume.isOver(pygame.mouse.get_pos()):
				self.resetLists()
				self.exit_loop = True
			elif self.restart in self.buttonList and self.restart.isOver(pygame.mouse.get_pos()):
				gameui.GameUI(True,self.game_mode).run()
			elif self.rotate_cw in self.buttonList and self.rotate_cw.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.rotate_cw,"ROTATE_CW")
			elif self.rotate_ccw in self.buttonList and self.rotate_ccw.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.rotate_ccw,"ROTATE_CCW")
			elif self.rotate_180 in self.buttonList and self.rotate_180.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.rotate_180,"ROTATE_180")
			elif self.shift_left in self.buttonList and self.shift_left.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.shift_left,"SHIFT_LEFT")
			elif self.shift_right in self.buttonList and self.shift_right.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.shift_right,"SHIFT_RIGHT")
			elif self.soft_drop in self.buttonList and self.soft_drop.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.soft_drop,"SOFT_DROP")
			elif self.hard_drop in self.buttonList and self.hard_drop.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.hard_drop,"HARD_DROP")
			elif self.swap_hold in self.buttonList and self.swap_hold.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.swap_hold,"SWAP_HOLD")
			elif self.reset in self.buttonList and self.reset.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.reset,"RESET")
			elif self.activate_zone in self.buttonList and self.activate_zone.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.activate_zone,"ACTIVATE_ZONE")
			elif self.pause in self.buttonList and self.pause.isOver(pygame.mouse.get_pos()):
				self.changeControl(self.pause,"PAUSE")
		elif event.type == pygame.KEYDOWN:
			for box in self.inputBoxList:
				box.handle_event(event)

	def iter(self): #run but one frame only
		self.screen.fill(self.BG_COLOR)
		self.title.draw(self.screen)

		for label in self.labelList:
			label.draw(self.screen)

		for button in self.buttonList:
			button.draw(self.screen,self.WHITE)

		for box in self.inputBoxList:
			box.draw(self.screen)
		
		pygame.display.flip()
	
	def run(self):
		while True and not self.exit_loop:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
					self.handle_event(event)

			self.screen.fill(self.BG_COLOR)
			self.title.draw(self.screen)

			for label in self.labelList:
				label.draw(self.screen)

			for button in self.buttonList:
				if button.isOver(pygame.mouse.get_pos()):
					button.button_colour = self.GREY
				else:
					button.button_colour = self.BLACK

			for button in self.buttonList:
				button.draw(self.screen,self.WHITE)

			for box in self.inputBoxList:
				box.draw(self.screen)
			
			pygame.display.flip()
