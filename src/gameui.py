import sys
import pygame
import pyautogui
import time
import numpy as np
import math

from . import loader
from .utils import config
from .pane import Pane


class GameUI:

    def __init__(self, 
                 graphics_mode=True,
                 game_mode="ZEN",
                 **kwargs):
        # (TODO): load pane hierarchy from config file
        self.panes = []

        pygame.init()

        self.screen_width, self.screen_height = pyautogui.size()
        self.vertical_offset = 0
        self.offset = 0
        self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
        self.screen = pygame.display.set_mode(size=self.screen_size, flags=pygame.SCALED)
        
        pygame.display.set_caption('Pytris Effect')

        # for now, we replicate the original game using one pane that takes up the entire screen
        self.panes.append(Pane(
            pygame,
            (0, 0, self.screen_width, self.screen_height),
            self.screen,
            game_mode=game_mode
        ))

    def updateConfig(self):
        self.das = config.das
        self.arr = config.arr
        self.soft_drop_speed = config.soft_drop_speed

    def procKey(self, key_event, key_press):
        if key_event == pygame.KEYDOWN:
            if key_press in config.key2action:  # (TODO): use enums instead of string constants
                if config.key2action[key_press] == "PAUSE":
                    print("PAUSE")
                    loader.Loader(scene="PAUSE", prev="PAUSE").run()
                    self.updateConfig()
                

    def run(self):
        player_board = self.panes[0].state
        while not (player_board.gameOver() or player_board.objectiveMet()):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.procKey(event.type, event.key)

            for pane in self.panes:
                pane.render(events)
            pygame.display.flip()

        # (TODO): refactor loader into a pane
        print("GAME OVER")
        if player_board.gameOver():
            loader.Loader(scene="GAME OVER",game_mode=player_board.m.game_mode,objective=str(player_board.m.score)).run()
        elif player_board.objectiveMet():
            objective = ""
            if player_board.m.game_mode == "SPRINT":
                objective = player_board.sprint_time
            elif player_board.m.game_mode == "JOURNEY":
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
