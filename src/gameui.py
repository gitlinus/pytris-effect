import sys
import pygame
import pyautogui
import time
import numpy as np
import math
import os

from . import loader
from .utils import config, constants
from .pane import Pane
from .bots.controller import BotController
<<<<<<< HEAD
from .utils.logger import logger
=======
>>>>>>> da9228960829ef7bb9160916e13c32bae04a3696

# hack:
default_state_dict = {
    'its_per_sec': 1.0,
    'sec_per_tick': 10,
}

class GameUI:

    def __init__(self, 
                 graphics_mode=True,
                 game_mode=constants.GameMode.ZEN,
                 **kwargs):
        # (TODO): load pane hierarchy from config file
        self.panes = []

        pygame.init()

        self.screen_width, self.screen_height = pyautogui.size()
        self.vertical_offset = 50
        self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
        self.screen = pygame.display.set_mode(size=self.screen_size, flags=pygame.SCALED)
        self.game_mode = game_mode
        
        pygame.display.set_caption('Pytris Effect')

        # for testing music only
        pygame.mixer.stop() # stop all previous music channels
        self.bgm_path = os.path.abspath('./src/sounds/bgm/bgm_02.ogg')
        if os.path.isfile(self.bgm_path): 
            self.bgm = pygame.mixer.Sound(self.bgm_path)
            self.bgm.set_volume(0.5)

        # for now, we replicate the original game using one pane that takes up the entire screen
        if game_mode != constants.GameMode.VERSUS:
            self.panes.append(Pane(
                pygame,
                (0, 0, self.screen_size[0], self.screen_size[1]),
                self.screen,
                player=False,
                game_mode=game_mode,
                **default_state_dict
            ))
        else:
            self.panes.append(Pane( # player controlls left matrix only
                pygame,
                (0, 0, self.screen_size[0]//2, self.screen_size[1]),
                self.screen,
                game_mode=game_mode
            ))
            self.panes.append(Pane(
                pygame,
                (self.screen_size[0]//2, 0, self.screen_size[0]//2, self.screen_size[1]),
                self.screen,
                game_mode=game_mode
            ))

        # attach a bot controller to the right pane
        self.ctrl = BotController(bot="HeuristicBot", pps=4.)
        self.ctrl.bind(self.panes[0].state)
<<<<<<< HEAD

    def updateConfig(self):
        self.das = config.das
        self.arr = config.arr
        self.soft_drop_speed = config.soft_drop_speed
=======
>>>>>>> da9228960829ef7bb9160916e13c32bae04a3696

    def procKey(self, key_event, key_press):
        if key_event == pygame.KEYDOWN:
            if key_press in config.key2action:
                if config.key2action[key_press] == constants.Action.PAUSE and self.game_mode != constants.GameMode.VERSUS:
                    logger.info("PAUSE")
                    pygame.mixer.pause()
                    loader.Loader(scene="PAUSE", prev="PAUSE").run()
                    self.panes[0].updateGameStateConfig()
                    pygame.mixer.unpause()
                

    def run(self):
        self.bgm.play(loops=-1) # loop music indefinitely
        self.ctrl.start() # start bots

        player_board = self.panes[0].state
        while not (player_board.gameOver() or player_board.objectiveMet()):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.procKey(event.type, event.key)

            for i in range(len(self.panes)):
                if False: # i==0:
                    self.panes[i].render(events) # only pass events to first matrix
                else: # hack: just control all panes with the bot
                    with self.ctrl.lock:
                        bot_events = self.ctrl.queue
                        self.ctrl.queue = []
<<<<<<< HEAD
=======
                    
                    # for ctl in bot_events:
                    #     print(ctl)
                    #     getattr(self.panes[i].state.m, ctl)()
                    #     # self.panes[i].processEvents([ctl])
>>>>>>> da9228960829ef7bb9160916e13c32bae04a3696

                    # self.panes[i].state.getMoveStatus(True)
                    # self.panes[i].render()
                    self.panes[i].render(bot_events)

            pygame.display.flip()

        # (TODO): refactor loader into a pane
        logger.info("GAME OVER")
        self.bgm.stop() # stop music
        self.ctrl.end() # end bots
        if player_board.gameOver():
            loader.Loader(scene="GAME OVER",game_mode=player_board.m.game_mode,objective=str(player_board.m.score)).run()
        elif player_board.objectiveMet() or self.panes[-1].state.gameOver():
            objective = ""
            if player_board.m.game_mode == constants.GameMode.SPRINT:
                objective = player_board.sprint_time
            elif player_board.m.game_mode == constants.GameMode.JOURNEY:
                objective = str(player_board.m.score)
            loader.Loader(scene="END SCREEN",game_mode=player_board.m.game_mode,objective=objective).run()



    # (TODO): move gym-api into GameState
    """Gym-like api. Need to have graphics_mode=False to use properly"""
    def reset(self):
        self.score, self.ticks, self.phase = 0, 0, 0
        self.m.resetMatrix()
        self.m.addTetromino()
        return self.drawMatrix()

    def get_obs(self, done=False):
        sc = self.score
        self.score = self.m.getLines()
        return (
            self.drawMatrix(),
            self.score - sc - 0.001 if not done else -0.001 * (500-self.ticks),
            done,
            ''
        )

    def step(self, action):
        if action == 0:  # NO-OP
            pass
        elif action == 1:  # HARD-DROP
            self.getFixedInput(pygame.KEYDOWN, pygame.K_SPACE)
            self.phase = 0
        elif action == 2:  # ROTATE_CW
            self.getFixedInput(pygame.KEYDOWN, pygame.K_UP)
        elif action == 3:  # ROTATE_CCW
            self.getFixedInput(pygame.KEYDOWN, pygame.K_z)
        elif action == 4:  # SHIFT_LEFT
            self.getFixedInput(pygame.KEYDOWN, pygame.K_LEFT)
            self.getFixedInput(pygame.KEYUP, pygame.K_LEFT)
        elif action == 5:  # SHIFT_RIGHT
            self.getFixedInput(pygame.KEYDOWN, pygame.K_RIGHT)
            self.getFixedInput(pygame.KEYUP, pygame.K_RIGHT)
        elif action == 6:  # SOFT_DROP
            self.getFixedInput(pygame.KEYDOWN, pygame.K_DOWN)
            self.getFixedInput(pygame.KEYUP, pygame.K_DOWN)

        if self.m.game_over:
            return self.get_obs(True)
        self.advancePhase()
        return self.get_obs(self.m.game_over)

    def advancePhase(self):
        self.phase += 1
        self.ticks += 1
        self.enforceAutoLock()
        while self.phase >= self.its_per_tick:  # handles fractional values
            self.m.enforceGravity()
            self.phase -= self.its_per_tick

    def render(self):
        # for rendering
        from PIL import Image
        from IPython import display
        display.clear_output(wait=True)
        board = self.drawMatrix()
        scale = 20
        board = np.repeat(board, scale, axis=0)
        board = np.repeat(board, scale, axis=1)
        display.display(Image.fromarray(board.astype(np.uint8)))
