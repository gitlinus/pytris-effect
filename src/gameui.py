import sys
import pygame
import pyautogui
import time
import numpy as np
import math
from .utils import matrix, config


# text labels beside matrix
class Label:
    def __init__(self, font, text, colour, position, anchor="topleft"):
        self.image = font.render(text, True, colour)
        self.rect = self.image.get_rect()
        setattr(self.rect, anchor, position)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class GameUI:
    # (TODO) load static members from config file
    black = 0, 0, 0
    white = 255, 255, 255
    grey = 128, 128, 128
    yellow = 255, 255, 0
    purple = 255, 0, 255
    light_blue = 0, 127, 255

    def __init__(self,
                 graphic_mode=True,
                 game_mode="ZEN",
                 **kwargs):

        self.gravity = 1  # number of blocks per second at which the tetromino falls
        self.das = 100  # (delayed auto-shift) number of milleseconds before arr sets in
        self.arr = 4  # (auto repeat rate) number of milleseconds in between each time the tetromino is shifted
        self.soft_drop_speed = 10  # rate (minos per second) at which soft drop makes the tetromino fall

        self.das_direction = None
        self.left_das_tick = None
        self.right_das_tick = None
        self.left_arr_tick = None
        self.right_arr_tick = None
        self.soft_drop_tick = None
        self.shift_once = False
        self.cancel_das = True  # leave true by default

        self.game_start_tick = None
        self.start_zone_tick = None

        self.ghostPiece = True
        self.showGrid = True

        self.enforce_auto_lock = True  # turns on auto locking of pieces when they touch the stack if True
        self.move_reset = 15  # the maximum number of moves the player can make after the tetromino touches the stack
        self.lock_delay = 500  # maximum of milleseconds in between moves after the tetromino touches the stack before it is locked in place
        self.prev_move_tick = None
        self.move_cnt = 0
        self.enforce_lock_delay = False

        self.clear_flag = None
        self.clear_text = []
        self.track_clear_text = []

        self.use_graphics = graphic_mode
        if self.use_graphics:
            pygame.init()

            self.screen_width, self.screen_height = pyautogui.size()
            self.m = matrix.Matrix(2 * self.screen_height // 60,game_mode)  # matrix height should be roughly 2/3 of screen height
            self.vertical_offset = 50
            self.offset = 50
            self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
            self.screen = pygame.display.set_mode(size=self.screen_size, flags=pygame.SCALED)
            self.matrix_left_top = (self.screen_width - self.m.width) // 2, (self.screen_height - self.m.height) // 2

            pygame.display.set_caption('Pytris Effect')

            self.font_size = self.m.mino_dim  # font_size should be the same as the width of a single mino
            self.font = pygame.font.Font(None, self.font_size)

            self.zone_colour = pygame.Color('dodgerblue')

            self.visited = np.zeros((self.m.matrix.shape[0], self.m.matrix.shape[1]), dtype=int)

            self.time_label = Label(self.font, "TIME", self.yellow,
                (self.matrix_left_top[0] + self.m.width + self.offset, self.matrix_left_top[1] + 2 * self.m.height // 3))
            self.score_label = Label(self.font, "SCORE", self.yellow,
                (self.matrix_left_top[0] + self.m.width + self.offset, self.matrix_left_top[1] + 2 * self.m.height // 3 + 3 * self.font_size))
            self.lines_label = Label(self.font, "LINES", self.yellow,
                (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + 2 * self.m.height // 3), "topright")
            self.zone_label = Label(self.font, "ZONE", self.yellow,
                (self.matrix_left_top[0] - self.offset - 2 * self.font_size, self.matrix_left_top[1] + self.m.height - 2 * self.font_size), "center")
            
            # zone shape is a square diamond, diagonal length = 4*font_size
            self.zone_points = [
                (self.matrix_left_top[0] - self.offset - 2 * self.font_size,self.matrix_left_top[1] + self.m.height - 4 * self.font_size),
                (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + self.m.height - 2 * self.font_size),
                (self.matrix_left_top[0] - self.offset - 2 * self.font_size, self.matrix_left_top[1] + self.m.height),
                (self.matrix_left_top[0] - self.offset - 4 * self.font_size,self.matrix_left_top[1] + self.m.height - 2 * self.font_size)
            ]  # top, right, bottom, left
            self.zone_center = (
                self.matrix_left_top[0] - self.offset - 2 * self.font_size,
                self.matrix_left_top[1] + self.m.height - 2 * self.font_size)
        else:
            self.m = matrix.Matrix()
            self.visited = np.zeros((self.m.matrix.shape[0], self.m.matrix.shape[1]), dtype=int)
            self.its_per_tick = kwargs['its_per_sec'] * kwargs['sec_per_tick']
            self.its_for_lock = kwargs['its_per_sec'] * self.lock_delay / 1000.0
            self.phase = 0
            self.score = 0
            self.ticks = 0

    def drawMatrix(self):
        """When using graphics, draw the board. When using api, return the board"""
        if self.use_graphics:
            pygame.draw.rect(self.screen, self.white, pygame.Rect(self.matrix_left_top, self.m.dim()))

            # draw piece spawn area:
            for i in range(2):
                for j in range(10):
                    if self.m.matrix[i, j] != 0:
                        pygame.draw.rect(
                            self.screen,
                            self.m.index2rgb[self.m.matrix[i, j]],
                            pygame.Rect((self.matrix_left_top[0] + j * self.m.mino_dim,
                                         self.matrix_left_top[1] - (2 - i) * self.m.mino_dim),
                                        (self.m.mino_dim, self.m.mino_dim))
                        )

            # draw the actual matrix area:
            for i in range(20):
                for j in range(10):
                    if self.m.matrix[i + 2, j] != 0:
                        pygame.draw.rect(
                            self.screen,
                            self.m.index2rgb[self.m.matrix[i + 2, j]],
                            pygame.Rect((self.matrix_left_top[0] + j * self.m.mino_dim,
                                         self.matrix_left_top[1] + i * self.m.mino_dim),
                                        (self.m.mino_dim, self.m.mino_dim))
                        )
        else:
            res = []
            for i in range(20): # (TODO) this might be too slow for a gym-api, try vectorizing later
                line = []
                for j in range(10):
                    line.append(self.m.index2rgb[self.m.matrix[i+2, j]])
                res.append(line)
            return np.array(res)

    def drawQueue(self, length=5):  # max queue length of 5
        if length > 5:
            length = 5
        queue = self.m.getQueue()
        drawingSpace = np.zeros((3, 4), dtype=int)

        for i in range(length):
            tetr = queue[i]
            tetr_mat = self.m.tetromino2matrix[tetr]
            drawingSpace[0:tetr_mat.shape[0], 0:tetr_mat.shape[1]] += tetr_mat

            for row in range(drawingSpace.shape[0]):
                for col in range(drawingSpace.shape[1]):
                    if drawingSpace[row, col] != 0:
                        pygame.draw.rect(
                            self.screen,
                            self.m.index2rgb[drawingSpace[row, col]],
                            pygame.Rect((self.matrix_left_top[0] + self.m.width + self.offset + col * self.m.mino_dim,
                                         self.matrix_left_top[1] + (3 * i + row - 2) * self.m.mino_dim),
                                        (self.m.mino_dim, self.m.mino_dim))
                        )
                        drawingSpace[row, col] = 0

    def drawHold(self):
        tetr = self.m.getHold()
        if tetr != "":
            drawingSpace = np.zeros((3, 4), dtype=int)
            tetr_mat = self.m.tetromino2matrix[tetr]
            if tetr != 'I':
                drawingSpace[0:tetr_mat.shape[0], 1:tetr_mat.shape[1] + 1] += tetr_mat
            else:
                drawingSpace[0:tetr_mat.shape[0], 0:tetr_mat.shape[1]] += tetr_mat

            for row in range(drawingSpace.shape[0]):
                for col in range(drawingSpace.shape[1]):
                    if drawingSpace[row, col] != 0:
                        pygame.draw.rect(
                            self.screen,
                            self.m.index2rgb[drawingSpace[row, col]],
                            pygame.Rect((self.matrix_left_top[0] - self.offset + (col - 4) * self.m.mino_dim,
                                         self.matrix_left_top[1] + (row - 2) * self.m.mino_dim),
                                        (self.m.mino_dim, self.m.mino_dim))
                        )
                        drawingSpace[row, col] = 0

    def drawGhost(self):  # draws ghost piece
        if self.ghostPiece:
            dist = 0
            found = False
            for r in range(21):  # at most drop by a distance of 20
                for i in self.m.mino_locations:
                    if i[0] + r >= self.m.matrix.shape[0] or (
                            self.m.matrix[i[0] + r, i[1]] != 0 and (i[0] + r, i[1]) not in self.m.mino_locations):
                        found = True
                        break
                if found:
                    break
                else:
                    dist = r
            for pos in self.m.mino_locations:  # draw ghost piece darker then actual piece colour
                if (dist + pos[0], pos[1]) not in self.m.mino_locations:  # don't cover actual piece
                    pygame.draw.rect(
                        self.screen,
                        (lambda a: (a[0] // 3, a[1] // 3, a[2] // 3))(self.m.tetromino2rgb[self.m.current_tetromino]),
                        pygame.Rect((self.matrix_left_top[0] + pos[1] * self.m.mino_dim,
                                     self.matrix_left_top[1] + (dist + pos[0] - 2) * self.m.mino_dim),
                                    (self.m.mino_dim, self.m.mino_dim))
                    )

    def drawGrid(self):
        # draw grid
        if self.showGrid:
            for i in range(11):  # vertical lines
                pygame.draw.line(self.screen, self.grey,
                                 (self.matrix_left_top[0] + i * self.m.mino_dim, self.matrix_left_top[1] - 2 * self.m.mino_dim),
                                 (self.matrix_left_top[0] + i * self.m.mino_dim, self.matrix_left_top[1] + self.m.height)
                                )
            for i in range(22):  # horizontal lines
                pygame.draw.line(self.screen, self.grey,
                                 (self.matrix_left_top[0], self.matrix_left_top[1] + (i - 1) * self.m.mino_dim),
                                 (self.matrix_left_top[0] + self.m.width, self.matrix_left_top[1] + (i - 1) * self.m.mino_dim)
                                )

    def drawText(self):
        self.time_label.draw(self.screen)
        Label(self.font, self.getTimer(), self.yellow,
              (self.matrix_left_top[0] + self.m.width + self.offset,
               self.matrix_left_top[1] + 2 * self.m.height // 3 + self.font_size)).draw(self.screen)
        self.score_label.draw(self.screen)
        Label(self.font, self.getScore(), self.yellow, (
            self.matrix_left_top[0] + self.m.width + self.offset,
            self.matrix_left_top[1] + 2 * self.m.height // 3 + 4 * self.font_size)).draw(self.screen)
        self.lines_label.draw(self.screen)
        Label(self.font, self.getStats(), self.yellow,
              (self.matrix_left_top[0] - self.offset,
                self.matrix_left_top[1] + 2 * self.m.height // 3 + self.font_size),"topright").draw(self.screen)

    def drawZoneMeter(self):
        self.getZoneTimer()
        percentage_filled = self.m.current_zone / self.m.full_zone
        if 0 < percentage_filled < 0.5:  # draw triangle
            height = math.sqrt(percentage_filled * 8 * self.font_size * self.font_size)
            shift = math.tan(math.pi / 4) * height
            right_point = (self.zone_center[0] + shift, self.zone_points[2][1] - height)
            left_point = (self.zone_center[0] - shift, self.zone_points[2][1] - height)
            pygame.draw.polygon(self.screen, self.zone_colour, [right_point, self.zone_points[2], left_point])
        elif percentage_filled == 0.5:
            pygame.draw.polygon(self.screen, self.zone_colour,
                                [self.zone_points[1], self.zone_points[2], self.zone_points[3]])
        elif 0.5 < percentage_filled < 1:
            height = math.sqrt((1 - percentage_filled) * 8 * self.font_size * self.font_size)
            shift = math.tan(math.pi / 4) * height
            right_point = (self.zone_center[0] + shift, self.zone_points[0][1] + height)
            left_point = (self.zone_center[0] - shift, self.zone_points[0][1] + height)
            pygame.draw.polygon(self.screen, self.zone_colour, self.zone_points)
            pygame.draw.polygon(self.screen, self.black, [left_point, self.zone_points[0], right_point])
        elif percentage_filled >= 1:
            pygame.draw.polygon(self.screen, self.zone_colour, self.zone_points)
        if percentage_filled >= 1:  # self.yellow border if filled
            pygame.draw.polygon(self.screen, self.yellow, self.zone_points, width=5)
        else:
            pygame.draw.polygon(self.screen, self.grey, self.zone_points, width=5)
        self.zone_label.draw(self.screen)

        # draw border around matrix for zone
        if self.m.zone_state:
            pygame.draw.polygon(self.screen, self.zone_colour, [self.matrix_left_top, (self.matrix_left_top[0]+self.m.width,self.matrix_left_top[1]), 
                                                                    (self.matrix_left_top[0]+self.m.width,self.matrix_left_top[1]+self.m.height),
                                                                    (self.matrix_left_top[0],self.matrix_left_top[1]+self.m.height)], width=10)

    def drawClearText(self):
        if self.m.prev_clear_text != [''] and self.m.prev_clear_text != self.track_clear_text:
            self.track_clear_text = self.m.prev_clear_text
            self.clear_text.clear()
            self.clear_flag = self.getTick()
            for i in range(len(self.m.prev_clear_text)):
                if self.m.prev_clear_text[i].find("PERFECT CLEAR") != -1:
                    self.clear_text.append(Label(self.font, self.m.prev_clear_text[i], self.yellow, 
                        (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                elif self.m.prev_clear_text[i].find("T-SPIN") != -1:
                    self.clear_text.append(Label(self.font, self.m.prev_clear_text[i], self.purple, 
                        (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                elif self.m.prev_clear_text[i].find("B2B") != -1:
                    self.clear_text.append(Label(self.font, self.m.prev_clear_text[i], self.light_blue, 
                        (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                elif self.m.prev_clear_text[i].find("TRIS") != -1:
                    self.clear_text.append(Label(self.font, self.m.prev_clear_text[i], self.zone_colour, 
                        (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                else:
                    self.clear_text.append(Label(self.font, self.m.prev_clear_text[i], self.white, 
                        (self.matrix_left_top[0] - self.offset, self.matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
            for msg in self.clear_text:
                msg.draw(self.screen)
        else:
            if self.clear_flag is not None:
                if self.getTick() - self.clear_flag <= 2000:  # show for 2 seconds max
                    for msg in self.clear_text:
                        msg.draw(self.screen)
                else:
                    self.clear_flag = None
            if self.m.prev_clear_text == ['']:
                self.track_clear_text.clear()

    def getZoneTimer(self):
        if self.m.zone_state:
            current_tick = self.getTick()
            if self.m.current_zone == 0:
                self.m.leaveZone()
                self.start_zone_tick = None
                return
            if current_tick - self.start_zone_tick >= 500: # full zone (40 lines) -> 20 zone seconds
                self.m.current_zone -= 1
                self.start_zone_tick = current_tick
                return

    def getStats(self):  # number of lines cleared
        return str(self.m.getLines())

    def getTimer(self):  # time elapsed
        time_passed = self.getTick() - self.game_start_tick
        hours = time_passed // 1000 // 60 // 60
        minutes = time_passed // 1000 // 60 % 60
        seconds = time_passed // 1000 % 60
        time_str = ""
        time_str += str(hours) + ":" if hours != 0 else ""
        time_str += str(minutes) + ":" if minutes >= 10 else "0" + str(minutes) + ":"
        time_str += str(seconds) if seconds >= 10 else "0" + str(seconds)
        return time_str

    def getScore(self):  # current score
        return str(self.m.getScore())
    
    def getTick(self):
        if self.use_graphics:
            return pygame.time.get_ticks()
        else:
            return self.ticks

    def getLockDelay(self):
        if self.use_graphics:
            return self.lock_delay
        else:
            return self.its_for_lock

    def getFixedInput(self, key_event, key_press):  # for single actions (hard drop, rotations, swap hold)

        if key_event == pygame.KEYDOWN:
            if key_press in config.key2action:
                if config.key2action[key_press] == "HARD_DROP":
                    self.m.hardDrop()
                    print("HARD_DROP")
                    self.getMoveStatus(True)
                elif config.key2action[key_press] == "ROTATE_CW":
                    self.m.rotateCW()
                    print("ROTATE_CW")
                    self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == "ROTATE_CCW":
                    self.m.rotateCCW()
                    print("ROTATE_CCW")
                    self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == "ROTATE_180":
                    self.m.rotate180()
                    print("ROTATE_180")
                    self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == "SWAP_HOLD":
                    # note: remember to implement way to stop swap_hold being executed consecutively
                    self.m.swapHold()
                    print("SWAP_HOLD")
                    self.getMoveStatus(True)
                elif config.key2action[key_press] == "SHIFT_LEFT":
                    print("SHIFT_LEFT")
                    self.shift_once = True
                    self.das_direction = "LEFT"
                    self.left_das_tick = self.getTick()
                    self.right_arr_tick = None
                    if self.cancel_das:
                        self.right_das_tick = None
                    else:
                        if self.right_das_tick is not None:
                            self.left_das_tick = self.right_das_tick
                elif config.key2action[key_press] == "SHIFT_RIGHT":
                    print("SHIFT_RIGHT")
                    self.shift_once = True
                    self.das_direction = "RIGHT"
                    self.right_das_tick = self.getTick()
                    self.left_arr_tick = None
                    if self.cancel_das:
                        self.left_das_tick = None
                    else:
                        if self.left_das_tick is not None:
                            self.right_das_tick = self.left_das_tick
                elif config.key2action[key_press] == "SOFT_DROP":
                    print("SOFT_DROP")
                    self.soft_drop_tick = self.getTick()
                elif config.key2action[key_press] == "RESET":
                    print("RESET")
                    self.m.resetMatrix()
                    self.m.addTetromino()
                    if not self.m.game_mode == "ZEN":
                        self.game_start_tick = self.getTick()
                elif config.key2action[key_press] == "ACTIVATE_ZONE":
                    print("ACTIVATE_ZONE")
                    if self.m.zoneReady():
                        self.m.activateZone()
                        self.start_zone_tick = self.getTick()

        elif key_event == pygame.KEYUP:  # reset das, arr, and soft drop
            if key_press in config.key2action:
                if config.key2action[key_press] == "SHIFT_LEFT":
                    self.left_das_tick = None
                    self.left_arr_tick = None
                elif config.key2action[key_press] == "SHIFT_RIGHT":
                    self.right_das_tick = None
                    self.right_arr_tick = None
                elif config.key2action[key_press] == "SOFT_DROP":
                    self.soft_drop_tick = None

    def getContinuousInput(self):  # for continuous actions (shift left, shift right, soft drop)
        keys = pygame.key.get_pressed()

        current_tick = self.getTick()

        if not keys[config.action2key["SHIFT_LEFT"]] and not keys[config.action2key["SHIFT_RIGHT"]]:  # reset direction
            self.das_direction = None

        if self.cancel_das:
            if self.left_das_tick is None and (keys[config.action2key["SHIFT_LEFT"]] and not keys[config.action2key["SHIFT_RIGHT"]]):  # das was cancelled but key was held down still
                self.left_das_tick = current_tick
                self.das_direction = "LEFT"
            if self.right_das_tick is None and (keys[config.action2key["SHIFT_RIGHT"]] and not keys[config.action2key["SHIFT_LEFT"]]):  # das was cancelled but key was held down still
                self.right_das_tick = current_tick
                self.das_direction = "RIGHT"
        else:
            if self.das_direction == "RIGHT" and (keys[config.action2key["SHIFT_LEFT"]] and not keys[config.action2key["SHIFT_RIGHT"]]):  # direction changed but no das cancellation
                self.das_direction = "LEFT"
            if self.das_direction == "LEFT" and (keys[config.action2key["SHIFT_RIGHT"]] and not keys[config.action2key["SHIFT_LEFT"]]):  # direction changed but no das cancellation
                self.das_direction = "RIGHT"

        if self.das_direction == "LEFT" and self.left_das_tick is not None:  # das was already started
            if current_tick - self.left_das_tick >= self.das and keys[config.action2key["SHIFT_LEFT"]]:
                # if pressed for das duration, set in arr
                if self.left_arr_tick is None:
                    self.left_arr_tick = current_tick
                else:  # set in arr
                    if current_tick - self.left_arr_tick >= self.arr:
                        self.m.shiftLeft()
                        self.left_arr_tick = current_tick
                        self.getMoveStatus(tick=current_tick)
            elif self.shift_once:  # das duration not met, only shift tetromino once
                self.shift_once = False
                self.m.shiftLeft()
                self.getMoveStatus(tick=current_tick)

        elif self.das_direction == "RIGHT" and self.right_das_tick is not None:
            if current_tick - self.right_das_tick >= self.das and keys[config.action2key["SHIFT_RIGHT"]]:
                if self.right_arr_tick is None:
                    self.right_arr_tick = current_tick
                else:  # set in arr
                    if current_tick - self.right_arr_tick >= self.arr:
                        self.m.shiftRight()
                        self.right_arr_tick = current_tick
                        self.getMoveStatus(tick=current_tick)
            elif self.shift_once:
                self.shift_once = False
                self.m.shiftRight()
                self.getMoveStatus(tick=current_tick)

        if self.soft_drop_tick is not None and keys[config.action2key["SOFT_DROP"]]:  # treat soft drop like faster gravity
            if (current_tick - self.soft_drop_tick) >= 1000 // self.soft_drop_speed:
                self.m.softDrop()
                self.soft_drop_tick = current_tick
                self.getMoveStatus(tick=current_tick)

    def getMoveStatus(self, reset=False, tick=None):
        if self.enforce_auto_lock:
            if reset:
                self.visited.fill(0)  # reset visited array
                self.prev_move_tick = None
                self.enforce_lock_delay = False
                self.move_cnt = 0
            else:
                self.prev_move_tick = tick
                self.move_cnt += 1 if self.enforce_lock_delay else 0

    def updateVisited(self):
        for i in self.m.mino_locations:
            self.visited[i[0], i[1]] = 1

    def alreadyVisited(self):
        for i in self.m.mino_locations:
            if not self.visited[i[0], i[1]]:
                return False
        return True

    def enforceAutoLock(self):
        """
            if touchedStack
                get current tick and tick of last move
                if lock delay reached -> freeze tetromino
                else
                    if location not visited -> reset move counter
                    else -> turn on enforce_lock_delay
                        if move_reset equals move counter -> freeze tetromino
        """
        current_tick = self.getTick()
        if self.enforce_auto_lock and self.m.touchedStack() and self.prev_move_tick is not None:
            if current_tick - self.prev_move_tick >= self.getLockDelay():
                self.m.freezeTetromino()
                self.getMoveStatus(True)
            else:
                if not self.alreadyVisited():
                    self.move_cnt = 0
                    self.enforce_lock_delay = False
                    self.updateVisited()
                else:
                    self.enforce_lock_delay = True
                    if self.move_cnt >= self.move_reset:
                        self.m.freezeTetromino()
                        self.getMoveStatus(True)

    def run(self):
        self.m.addTetromino()
        self.game_start_tick = self.getTick()
        start_tick = self.getTick()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.getFixedInput(event.type, event.key)

            self.getContinuousInput()
            self.enforceAutoLock()
            self.screen.fill(self.black)
            self.drawMatrix()
            self.drawGhost()
            self.drawGrid()
            self.drawQueue()
            self.drawHold()
            self.drawText()
            self.drawClearText()
            self.drawZoneMeter()
            pygame.display.flip()

            end_tick = self.getTick()
            if (end_tick - start_tick) >= 1000 // self.gravity:
                start_tick = end_tick
                self.m.enforceGravity()
                self.getMoveStatus(tick=end_tick)
                # print(m.matrix)

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
            self.score - sc if not done else -1,
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
        while self.phase >= self.its_per_tick:  # handles fractional values
            self.m.enforceGravity()
            self.phase -= self.its_per_tick
