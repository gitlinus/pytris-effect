import sys
import pygame
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
        self.das = config.das  # (delayed auto-shift) number of milleseconds before arr sets in
        self.arr = config.arr  # (auto repeat rate) number of milleseconds in between each time the tetromino is shifted
        self.soft_drop_speed = config.soft_drop_speed  # rate (minos per second) at which soft drop makes the tetromino fall

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
        self.sprint_time = None

        self.ghostPiece = True
        self.showGrid = True

        self.enforce_auto_lock = True  # turns on auto locking of pieces when they touch the stack if True
        self.move_reset = 15  # the maximum number of moves the player can make after the tetromino touches the stack
        self.lock_delay = 500  # maximum of milleseconds in between moves after the tetromino touches the stack before it is locked in place
        self.prev_move_tick = None
        self.move_cnt = 0
        self.enforce_lock_delay = False

        # self.clear_flag = None
        # self.clear_text = []
        # self.track_clear_text = []

        self.use_graphics = graphic_mode
        if self.use_graphics:
            
            import pyautogui
            global loader
            from . import loader
            pygame.init()

            self.screen_width, self.screen_height = pyautogui.size()
            self.vertical_offset = 50
            self.offset = 50
            self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
            self.screen = pygame.display.set_mode(size=self.screen_size, flags=pygame.SCALED)
            self.m = matrix.Matrix(game_mode, (self.screen_width, self.screen_height)) # initialize matrix object
            self.matrix_left_top = self.m.topleft

            pygame.display.set_caption('Pytris Effect')

            self.font_size = self.m.mino_dim  # font_size should be the same as the width of a single mino
            self.font = pygame.font.Font(None, self.font_size)

            self.zone_colour = pygame.Color('dodgerblue')

            self.visited = np.zeros((self.m.matrix.shape[0], self.m.matrix.shape[1]), dtype=int)
            
        else:
            self.m = matrix.Matrix()
            self.visited = np.zeros((self.m.matrix.shape[0], self.m.matrix.shape[1]), dtype=int)
            self.its_per_tick = kwargs['its_per_sec'] * kwargs['sec_per_tick']
            self.its_for_lock = kwargs['its_per_sec'] * self.lock_delay / 1000.0
            self.phase = 0
            self.score = 0
            self.ticks = 0
            colour_map = lambda x: self.m.index2rgb[x]
            self.vec_map = np.vectorize(colour_map)

    def drawMatrix(self, m):
        """When using graphics, draw the board. When using api, return the board"""

        matrix_left_top = m.topleft

        if self.use_graphics:
            pygame.draw.rect(self.screen, self.white, pygame.Rect(matrix_left_top, m.dim()))

            # draw piece spawn area:
            for i in range(2):
                for j in range(10):
                    if m.matrix[i, j] != 0:
                        pygame.draw.rect(
                            self.screen,
                            m.index2rgb[m.matrix[i, j]],
                            pygame.Rect((matrix_left_top[0] + j * m.mino_dim,
                                         matrix_left_top[1] - (2 - i) * m.mino_dim),
                                        (m.mino_dim, m.mino_dim))
                        )

            # draw the actual matrix area:
            for i in range(20):
                for j in range(10):
                    if m.matrix[i + 2, j] != 0:
                        pygame.draw.rect(
                            self.screen,
                            m.index2rgb[m.matrix[i + 2, j]],
                            pygame.Rect((matrix_left_top[0] + j * m.mino_dim,
                                         matrix_left_top[1] + i * m.mino_dim),
                                        (m.mino_dim, m.mino_dim))
                        )
        else:
            visible = m.matrix[2:,:]
            visible = self.vec_map(visible)
            return np.moveaxis(visible, 0, -1)

    def drawQueue(self, m, length=5):  # max queue length of 5

        matrix_left_top = m.topleft

        if length > 5:
            length = 5
        queue = m.getQueue()
        drawingSpace = np.zeros((3, 4), dtype=int)

        for i in range(length):
            tetr = queue[i]
            tetr_mat = m.tetromino2matrix[tetr]
            drawingSpace[0:tetr_mat.shape[0], 0:tetr_mat.shape[1]] += tetr_mat

            for row in range(drawingSpace.shape[0]):
                for col in range(drawingSpace.shape[1]):
                    if drawingSpace[row, col] != 0:
                        pygame.draw.rect(
                            self.screen,
                            m.index2rgb[drawingSpace[row, col]],
                            pygame.Rect((matrix_left_top[0] + m.width + self.offset + col * m.mino_dim,
                                         matrix_left_top[1] + (3 * i + row - 2) * m.mino_dim),
                                        (m.mino_dim, m.mino_dim))
                        )
                        drawingSpace[row, col] = 0

    def drawHold(self, m):

        matrix_left_top = m.topleft

        tetr = m.getHold()
        if tetr != "":
            drawingSpace = np.zeros((3, 4), dtype=int)
            tetr_mat = m.tetromino2matrix[tetr]
            if tetr != 'I':
                drawingSpace[0:tetr_mat.shape[0], 1:tetr_mat.shape[1] + 1] += tetr_mat
            else:
                drawingSpace[0:tetr_mat.shape[0], 0:tetr_mat.shape[1]] += tetr_mat

            for row in range(drawingSpace.shape[0]):
                for col in range(drawingSpace.shape[1]):
                    if drawingSpace[row, col] != 0:
                        pygame.draw.rect(
                            self.screen,
                            m.index2rgb[drawingSpace[row, col]],
                            pygame.Rect((matrix_left_top[0] - self.offset + (col - 4) * m.mino_dim,
                                         matrix_left_top[1] + (row - 2) * m.mino_dim),
                                        (m.mino_dim, m.mino_dim))
                        )
                        drawingSpace[row, col] = 0

    def drawGhost(self, m):  # draws ghost piece

        matrix_left_top = m.topleft

        if self.ghostPiece:
            dist = 0
            found = False
            for r in range(21):  # at most drop by a distance of 20
                for i in m.mino_locations:
                    if i[0] + r >= m.matrix.shape[0] or (
                            m.matrix[i[0] + r, i[1]] != 0 and (i[0] + r, i[1]) not in m.mino_locations):
                        found = True
                        break
                if found:
                    break
                else:
                    dist = r
            for pos in m.mino_locations:  # draw ghost piece darker then actual piece colour
                if (dist + pos[0], pos[1]) not in m.mino_locations:  # don't cover actual piece
                    pygame.draw.rect(
                        self.screen,
                        (lambda a: (a[0] // 3, a[1] // 3, a[2] // 3))(m.tetromino2rgb[m.current_tetromino]),
                        pygame.Rect((matrix_left_top[0] + pos[1] * m.mino_dim,
                                     matrix_left_top[1] + (dist + pos[0] - 2) * m.mino_dim),
                                    (m.mino_dim, m.mino_dim))
                    )

    def drawGrid(self, m):

        matrix_left_top = m.topleft

        # draw grid
        if self.showGrid:
            for i in range(11):  # vertical lines
                pygame.draw.line(self.screen, self.grey,
                                 (matrix_left_top[0] + i * m.mino_dim, matrix_left_top[1] - 2 * m.mino_dim),
                                 (matrix_left_top[0] + i * m.mino_dim, matrix_left_top[1] + m.height)
                                )
            for i in range(22):  # horizontal lines
                pygame.draw.line(self.screen, self.grey,
                                 (matrix_left_top[0], matrix_left_top[1] + (i - 1) * m.mino_dim),
                                 (matrix_left_top[0] + m.width, matrix_left_top[1] + (i - 1) * m.mino_dim)
                                )

    def drawText(self, m):

        matrix_left_top = m.topleft

        time_label = Label(self.font, "TIME", self.yellow,
            (matrix_left_top[0] + m.width + self.offset, matrix_left_top[1] + 2 * m.height // 3))
        score_label = Label(self.font, "SCORE", self.yellow,
            (matrix_left_top[0] + m.width + self.offset, matrix_left_top[1] + 2 * m.height // 3 + 3 * self.font_size))
        lines_label = Label(self.font, "LINES", self.yellow,
            (matrix_left_top[0] - self.offset, matrix_left_top[1] + 2 * m.height // 3), "topright")
        level_label = Label(self.font, "LEVEL", self.yellow,
            (matrix_left_top[0] - self.offset, matrix_left_top[1] + 2 * m.height // 3 - 3 * self.font_size), "topright")

        time_label.draw(self.screen)
        Label(self.font, self.getTimer(), self.yellow,
              (matrix_left_top[0] + m.width + self.offset,
               matrix_left_top[1] + 2 * m.height // 3 + self.font_size)).draw(self.screen)

        score_label.draw(self.screen)
        Label(self.font, self.getScore(), self.yellow, 
            (matrix_left_top[0] + m.width + self.offset,
            matrix_left_top[1] + 2 * m.height // 3 + 4 * self.font_size)).draw(self.screen)
        
        lines_label.draw(self.screen)
        num_lines = self.getStats()
        if m.objective is not None:
            num_lines += "/" + str(m.objective)
        Label(self.font, num_lines, self.yellow,
              (matrix_left_top[0] - self.offset,
                matrix_left_top[1] + 2 * m.height // 3 + self.font_size),"topright").draw(self.screen)
        
        if m.game_mode == "JOURNEY":
            level_label.draw(self.screen)
            Label(self.font, str(m.level), self.yellow,
              (matrix_left_top[0] - self.offset,
                matrix_left_top[1] + 2 * m.height // 3 - 2 * self.font_size),"topright").draw(self.screen)

    def drawZoneMeter(self, m):

        matrix_left_top = m.topleft

        zone_label = Label(self.font, "ZONE", self.yellow,
            (matrix_left_top[0] - self.offset - 2 * self.font_size, matrix_left_top[1] + m.height - 2 * self.font_size), "center")

        # zone shape is a square diamond, diagonal length = 4*font_size
        zone_points = [
            (matrix_left_top[0] - self.offset - 2 * self.font_size, matrix_left_top[1] + m.height - 4 * self.font_size),
            (matrix_left_top[0] - self.offset, matrix_left_top[1] + m.height - 2 * self.font_size),
            (matrix_left_top[0] - self.offset - 2 * self.font_size, matrix_left_top[1] + m.height),
            (matrix_left_top[0] - self.offset - 4 * self.font_size, matrix_left_top[1] + m.height - 2 * self.font_size)
        ]  # top, right, bottom, left
        zone_center = (
            matrix_left_top[0] - self.offset - 2 * self.font_size,
            matrix_left_top[1] + m.height - 2 * self.font_size)

        self.getZoneTimer()
        percentage_filled = m.current_zone / m.full_zone
        if 0 < percentage_filled < 0.5:  # draw triangle
            height = math.sqrt(percentage_filled * 8 * self.font_size * self.font_size)
            shift = math.tan(math.pi / 4) * height
            right_point = (zone_center[0] + shift, zone_points[2][1] - height)
            left_point = (zone_center[0] - shift, zone_points[2][1] - height)
            pygame.draw.polygon(self.screen, self.zone_colour, [right_point, zone_points[2], left_point])
        elif percentage_filled == 0.5:
            pygame.draw.polygon(self.screen, self.zone_colour,
                                [zone_points[1], zone_points[2], zone_points[3]])
        elif 0.5 < percentage_filled < 1:
            height = math.sqrt((1 - percentage_filled) * 8 * self.font_size * self.font_size)
            shift = math.tan(math.pi / 4) * height
            right_point = (zone_center[0] + shift, zone_points[0][1] + height)
            left_point = (zone_center[0] - shift, zone_points[0][1] + height)
            pygame.draw.polygon(self.screen, self.zone_colour, zone_points)
            pygame.draw.polygon(self.screen, self.black, [left_point, zone_points[0], right_point])
        elif percentage_filled >= 1:
            pygame.draw.polygon(self.screen, self.zone_colour, zone_points)
        if percentage_filled >= 1:  # self.yellow border if filled
            pygame.draw.polygon(self.screen, self.yellow, zone_points, width=5)
        else:
            pygame.draw.polygon(self.screen, self.grey, zone_points, width=5)
        
        zone_label.draw(self.screen)

        # draw border around matrix for zone
        if m.zone_state:
            pygame.draw.polygon(self.screen, self.zone_colour, [matrix_left_top, (matrix_left_top[0]+m.width,matrix_left_top[1]), 
                                                                    (matrix_left_top[0]+m.width,matrix_left_top[1]+m.height),
                                                                    (matrix_left_top[0],matrix_left_top[1]+m.height)], width=10)

    def drawClearText(self, m):

        matrix_left_top = m.topleft

        if m.prev_clear_text != [''] and m.prev_clear_text != m.track_clear_text:
            m.track_clear_text = m.prev_clear_text
            m.clear_text.clear()
            m.clear_flag = self.getTick()
            for i in range(len(m.prev_clear_text)):
                if m.prev_clear_text[i].find("PERFECT CLEAR") != -1:
                    m.clear_text.append(Label(self.font, m.prev_clear_text[i], self.yellow, 
                        (matrix_left_top[0] - self.offset, matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                elif m.prev_clear_text[i].find("T-SPIN") != -1:
                    m.clear_text.append(Label(self.font, m.prev_clear_text[i], self.purple, 
                        (matrix_left_top[0] - self.offset, matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                elif m.prev_clear_text[i].find("B2B") != -1:
                    m.clear_text.append(Label(self.font, m.prev_clear_text[i], self.light_blue, 
                        (matrix_left_top[0] - self.offset, matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                elif m.prev_clear_text[i].find("TRIS") != -1:
                    m.clear_text.append(Label(self.font, m.prev_clear_text[i], self.zone_colour, 
                        (matrix_left_top[0] - self.offset, matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
                else:
                    m.clear_text.append(Label(self.font, m.prev_clear_text[i], self.white, 
                        (matrix_left_top[0] - self.offset, matrix_left_top[1] + (5 + i) * self.font_size),"topright"))
            for msg in m.clear_text:
                msg.draw(self.screen)
        else:
            if m.clear_flag is not None:
                if self.getTick() - m.clear_flag <= 2000:  # show for 2 seconds max
                    for msg in m.clear_text:
                        msg.draw(self.screen)
                else:
                    m.clear_flag = None
            if m.prev_clear_text == ['']:
                m.track_clear_text.clear()

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
        milles = time_passed % 1000
        time_str = ""
        time_str += str(hours) + ":" if hours != 0 else ""
        time_str += str(minutes) + ":" if minutes >= 10 else "0" + str(minutes) + ":"
        time_str += str(seconds) if seconds >= 10 else "0" + str(seconds)
        if self.m.game_mode == "SPRINT":
            time_str += "." + str(milles)
            if self.m.objective_met:
                self.sprint_time = time_str
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

        # no das when using env-mode
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
                    self.m.swapHold()
                    print("SWAP_HOLD")
                    self.getMoveStatus(True)
                elif config.key2action[key_press] == "SHIFT_LEFT":
                    print("SHIFT_LEFT")
                    if self.use_graphics:
                        self.shift_once = True
                        self.das_direction = "LEFT"
                        self.left_das_tick = self.getTick()
                        self.right_arr_tick = None
                        if self.cancel_das:
                            self.right_das_tick = None
                        else:
                            if self.right_das_tick is not None:
                                self.left_das_tick = self.right_das_tick
                    else:
                        self.m.shiftLeft()
                        self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == "SHIFT_RIGHT":
                    print("SHIFT_RIGHT")
                    if self.use_graphics:
                        self.shift_once = True
                        self.das_direction = "RIGHT"
                        self.right_das_tick = self.getTick()
                        self.left_arr_tick = None
                        if self.cancel_das:
                            self.left_das_tick = None
                        else:
                            if self.left_das_tick is not None:
                                self.right_das_tick = self.left_das_tick
                    else:
                        self.m.shiftRight()
                        self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == "SOFT_DROP":
                    print("SOFT_DROP")
                    self.soft_drop_tick = self.getTick()
                    if not self.use_graphics:
                        self.m.softDrop()
                        self.getMoveStatus(tick=self.getTick())
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
                elif config.key2action[key_press] == "PAUSE":
                    print("PAUSE")
                    loader.Loader(scene="PAUSE",prev="PAUSE").run()
                    self.updateConfig()

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
                self.prev_move_tick = None if self.use_graphics else self.getTick()
                self.enforce_lock_delay = False
                self.move_cnt = 0
            else:
                self.prev_move_tick = tick
                self.move_cnt += 1 if self.enforce_lock_delay else 0

    def updateConfig(self):
        self.das = config.das
        self.arr = config.arr
        self.soft_drop_speed = config.soft_drop_speed

    def gravityEq(self, level):
        return (0.8 - ((level-1) * 0.007)) ** (level-1)

    def updateGravity(self):
        self.gravity = 1/self.gravityEq(self.m.level)
    
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
        #print("{} {} {}".format(current_tick, self.prev_move_tick, self.getLockDelay()), file=sys.stderr)
        #print(self.m.mino_locations, file=sys.stderr)
        #print(self.m.touchedStack(), file=sys.stderr)
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

        while True and not (self.m.game_over or self.m.objective_met):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.getFixedInput(event.type, event.key)

            self.getContinuousInput()
            self.enforceAutoLock()
            self.screen.fill(self.black)
            self.drawMatrix(self.m)
            self.drawGhost(self.m)
            self.drawGrid(self.m)
            self.drawQueue(self.m)
            self.drawHold(self.m)
            self.drawText(self.m)
            self.drawClearText(self.m)
            self.drawZoneMeter(self.m)
            pygame.display.flip()

            end_tick = self.getTick()
            if (end_tick - start_tick) >= 1000 // self.gravity and not self.m.zone_state:
                start_tick = end_tick
                self.m.enforceGravity()
                self.getMoveStatus(tick=end_tick)
                # print(m.matrix)

            if self.m.game_mode == "JOURNEY":
                self.updateGravity()

        if self.m.game_over:
            loader.Loader(scene="GAME OVER",game_mode=self.m.game_mode,objective=str(self.m.score)).run()
        elif self.m.objective_met:
            objective = ""
            if self.m.game_mode == "SPRINT":
                objective = self.sprint_time
            elif self.m.game_mode == "JOURNEY":
                objective = str(self.m.score)
            loader.Loader(scene="END SCREEN",game_mode=self.m.game_mode,objective=objective).run()

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
