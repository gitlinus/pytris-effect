import sys
import pygame 
import pyautogui
from . import gameui
#Loading scenes

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

class Loader():

	BG_COLOR = pygame.Color('gray12')
	BLUE = pygame.Color('dodgerblue')
	WHITE = 255,255,255
	BLACK = 0,0,0
	GREY = 128,128,128
	
	def __init__(self):
		pygame.init()
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
		self.goback = None

		self.buttonList = None

		self.titleScreen()
	
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
		self.goback = Button(self.BLACK,self.title.rect.centerx-self.button_width*1.5,
									self.screen_height-3*self.button_height,
									self.button_width/2,self.button_height,self.button_font,self.WHITE,"BACK")
		self.buttonList = [self.journey, self.sprint, self.zen, self.goback]

	def handle_event(self, event):
		if self.play in self.buttonList and self.play.isOver(pygame.mouse.get_pos()):
			self.buttonList.clear()
			self.gameSelectionScreen()
		elif self.settings in self.buttonList and self.settings.isOver(pygame.mouse.get_pos()):
			print("Coming soon")
		elif self.goback in self.buttonList and self.goback.isOver(pygame.mouse.get_pos()):
			self.buttonList.clear()
			self.titleScreen()
		elif self.journey in self.buttonList and self.journey.isOver(pygame.mouse.get_pos()):
			print("Coming soon")
		elif self.sprint in self.buttonList and self.sprint.isOver(pygame.mouse.get_pos()):
			print("Coming soon")
		elif self.zen in self.buttonList and self.zen.isOver(pygame.mouse.get_pos()):
			game = gameui.GameUI(True,"ZEN")
			game.run()
		
	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.handle_event(event)

			self.screen.fill(self.BG_COLOR)
			self.title.draw(self.screen)

			for button in self.buttonList:
				if button.isOver(pygame.mouse.get_pos()):
					button.button_colour = self.GREY
				else:
					button.button_colour = self.BLACK

			for button in self.buttonList:
				button.draw(self.screen,self.WHITE)
			
			pygame.display.flip()
