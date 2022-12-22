import copy
from .utils import config, matrix, constants
import numpy as np
import math
import os

# text labels beside matrix
class Label:
    def __init__(self, font, text, colour, position, anchor="topleft"):
        self.image = font.render(text, True, colour)
        self.rect = self.image.get_rect()
        setattr(self.rect, anchor, position)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class GameState:

    def __init__(self,
                 cls,
                 draw,
                 graphic_mode=True,
                 player=True,
                 game_mode=constants.GameMode.ZEN,
                 **kwargs):

        self.cls = cls
        self.draw = draw
        self.screen = draw.screen # hacky but it works

        self.gravity = config.gravity  # number of blocks per second at which the tetromino falls
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
        self.start_tick = None
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
        self.hold_available = False # for sfx use only

        self.game_mode = game_mode
        self.log_buffer = dict() # logging what happens during a render phase
        self.player = player

        self.use_graphics = graphic_mode
        if self.use_graphics:

            self.screen_width = self.draw.coords[2]
            self.screen_height = self.draw.coords[3]
            self.vertical_offset = 50
            self.offset = 50
            # self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
            self.screen_size = self.screen_width, self.screen_height - self.vertical_offset
            # self.screen = pygame.display.set_mode(size=self.screen_size, flags=pygame.SCALED)
            self.m = matrix.Matrix(game_mode, (self.screen_width, self.screen_height))  # initialize matrix object
            self.matrix_left_top = self.m.topleft

            # pygame.display.set_caption('Pytris Effect')

            self.font_size = self.m.mino_dim  # font_size should be the same as the width of a single mino
            self.font = self.cls.font.Font(None, self.font_size)

            self.zone_colour = self.cls.Color('dodgerblue')

            self.visited = np.zeros((self.m.matrix.shape[0], self.m.matrix.shape[1]), dtype=int)

        if not player:
            if not self.use_graphics:
                self.m = matrix.Matrix()
                self.visited = np.zeros((self.m.matrix.shape[0], self.m.matrix.shape[1]), dtype=int)
            
            self.its_per_tick = kwargs['its_per_sec'] * kwargs['sec_per_tick']
            self.its_for_lock = kwargs['its_per_sec'] * self.lock_delay / 1000.0
            self.phase = 0
            self.score = 0
            self.ticks = 0
            colour_map = lambda x: self.m.index2rgb[x]
            self.vec_map = np.vectorize(colour_map)

    def getMatrix(self):
        return self.m.matrix

    def drawMatrix(self):
        """When using graphics, draw the board. When using api, return the board"""

        matrix_left_top = self.m.topleft

        if self.use_graphics:
            self.draw.rect(config.white, (matrix_left_top, self.m.dim()))

            # draw piece spawn area:
            for i in range(2):
                for j in range(10):
                    if self.m.matrix[i, j] != 0:
                        self.draw.rect(
                            self.m.index2rgb[self.m.matrix[i, j]],
                            ((matrix_left_top[0] + j * self.m.mino_dim, matrix_left_top[1] - (2 - i) * self.m.mino_dim),
                                (self.m.mino_dim, self.m.mino_dim)))

            # draw the actual matrix area:
            for i in range(20):
                for j in range(10):
                    if self.m.matrix[i + 2, j] != 0:
                        self.draw.rect(
                            self.m.index2rgb[self.m.matrix[i + 2, j]],
                            ((matrix_left_top[0] + j * self.m.mino_dim, matrix_left_top[1] + i * self.m.mino_dim),
                                (self.m.mino_dim, self.m.mino_dim)))
        else:
            visible = self.m.matrix[2:, :]
            visible = self.vec_map(visible)
            return np.moveaxis(visible, 0, -1)

    def drawQueue(self, length=5):  # max queue length of 5

        matrix_left_top = self.m.topleft

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
                        self.draw.rect(
                            self.m.index2rgb[drawingSpace[row, col]],
                            ((matrix_left_top[0] + self.m.width + self.offset + col * self.m.mino_dim,
                                matrix_left_top[1] + (3 * i + row - 2) * self.m.mino_dim),
                                (self.m.mino_dim, self.m.mino_dim)))
                        drawingSpace[row, col] = 0

    def drawHold(self):

        matrix_left_top = self.m.topleft

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
                        self.draw.rect(
                            self.m.index2rgb[drawingSpace[row, col]],
                            ((matrix_left_top[0] - self.offset + (col - 4) * self.m.mino_dim,
                                matrix_left_top[1] + (row - 2) * self.m.mino_dim),
                                (self.m.mino_dim, self.m.mino_dim)))
                        drawingSpace[row, col] = 0

    def drawGhost(self):  # draws ghost piece

        matrix_left_top = self.m.topleft

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
                    self.draw.rect(
                        (lambda a: (a[0] // 3, a[1] // 3, a[2] // 3))(self.m.tetromino2rgb[self.m.current_tetromino]),
                        ((matrix_left_top[0] + pos[1] * self.m.mino_dim,
                            matrix_left_top[1] + (dist + pos[0] - 2) * self.m.mino_dim),
                            (self.m.mino_dim, self.m.mino_dim)))

    def drawGrid(self):
        matrix_left_top = self.m.topleft
        # draw grid
        if self.showGrid:
            for i in range(11):  # vertical lines
                self.draw.line(config.grey,
                     ((matrix_left_top[0] + i * self.m.mino_dim, matrix_left_top[1] - 2 * self.m.mino_dim),
                     (matrix_left_top[0] + i * self.m.mino_dim, matrix_left_top[1] + self.m.height)))
            for i in range(22):  # horizontal lines
                self.draw.line(config.grey,
                     ((matrix_left_top[0], matrix_left_top[1] + (i - 1) * self.m.mino_dim),
                     (matrix_left_top[0] + self.m.width, matrix_left_top[1] + (i - 1) * self.m.mino_dim)))

    def drawText(self):

        matrix_left_top = self.m.topleft

        time_label = Label(self.font, "TIME", config.yellow,
                           self.draw.transformCoordinates((matrix_left_top[0] + self.m.width + self.offset,
                                                           matrix_left_top[1] + 2 * self.m.height // 3)))
        score_label = Label(self.font, "SCORE", config.yellow,
                            self.draw.transformCoordinates((matrix_left_top[0] + self.m.width + self.offset,
                                matrix_left_top[1] + 2 * self.m.height // 3 + 3 * self.font_size)))
        lines_label = Label(self.font, "LINES", config.yellow,
                            self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                                                            matrix_left_top[1] + 2 * self.m.height // 3)), "topright")
        level_label = Label(self.font, "LEVEL", config.yellow,
                            self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                                matrix_left_top[1] + 2 * self.m.height // 3 - 3 * self.font_size)), "topright")

        time_label.draw(self.screen)
        Label(self.font, self.getTimer(), config.yellow,
              self.draw.transformCoordinates((matrix_left_top[0] + self.m.width + self.offset,
                    matrix_left_top[1] + 2 * self.m.height // 3 + self.font_size))).draw(self.screen)

        score_label.draw(self.screen)
        Label(self.font, self.getScore(), config.yellow,
              self.draw.transformCoordinates((matrix_left_top[0] + self.m.width + self.offset,
                    matrix_left_top[1] + 2 * self.m.height // 3 + 4 * self.font_size))).draw(self.screen)

        lines_label.draw(self.screen)
        num_lines = self.getStats()
        if self.m.objective is not None:
            num_lines += "/" + str(self.m.objective)
        Label(self.font, num_lines, config.yellow,
              self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                    matrix_left_top[1] + 2 * self.m.height // 3 + self.font_size)), "topright").draw(self.screen)

        if self.m.game_mode == constants.GameMode.JOURNEY:
            level_label.draw(self.screen)
            Label(self.font, str(self.m.level), config.yellow,
                  self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                        matrix_left_top[1] + 2 * self.m.height // 3 - 2 * self.font_size)), "topright").draw(self.screen)

    def drawZoneMeter(self):

        matrix_left_top = self.m.topleft

        zone_label = Label(self.font, "ZONE", config.yellow,
                           self.draw.transformCoordinates((matrix_left_top[0] - self.offset - 2 * self.font_size,
                                matrix_left_top[1] + self.m.height - 2 * self.font_size)), "center")

        # zone shape is a square diamond, diagonal length = 4*font_size
        zone_points = [
            (matrix_left_top[0] - self.offset - 2 * self.font_size, matrix_left_top[1] + self.m.height - 4 * self.font_size),
            (matrix_left_top[0] - self.offset, matrix_left_top[1] + self.m.height - 2 * self.font_size),
            (matrix_left_top[0] - self.offset - 2 * self.font_size, matrix_left_top[1] + self.m.height),
            (matrix_left_top[0] - self.offset - 4 * self.font_size, matrix_left_top[1] + self.m.height - 2 * self.font_size)
        ]  # top, right, bottom, left
        zone_center = (
            matrix_left_top[0] - self.offset - 2 * self.font_size,
            matrix_left_top[1] + self.m.height - 2 * self.font_size)

        self.getZoneTimer()
        percentage_filled = self.m.current_zone / self.m.full_zone
        if 0 < percentage_filled < 0.5:  # draw triangle
            height = int(math.sqrt(percentage_filled * 8 * self.font_size * self.font_size))
            shift = int(math.tan(math.pi / 4) * height)
            right_point = (zone_center[0] + shift, zone_points[2][1] - height)
            left_point = (zone_center[0] - shift, zone_points[2][1] - height)
            self.draw.polygon(self.zone_colour, [right_point, zone_points[2], left_point])
        elif percentage_filled == 0.5:
            self.draw.polygon(self.zone_colour,
                                [zone_points[1], zone_points[2], zone_points[3]])
        elif 0.5 < percentage_filled < 1:
            height = int(math.sqrt((1 - percentage_filled) * 8 * self.font_size * self.font_size))
            shift = int(math.tan(math.pi / 4) * height)
            right_point = (zone_center[0] + shift, zone_points[0][1] + height)
            left_point = (zone_center[0] - shift, zone_points[0][1] + height)
            self.draw.polygon(self.zone_colour, zone_points)
            self.draw.polygon(config.black, [left_point, zone_points[0], right_point])
        elif percentage_filled >= 1:
            self.draw.polygon(self.zone_colour, zone_points)
        if percentage_filled >= 1:  # config.yellow border if filled
            self.draw.polygon(config.yellow, zone_points, width=5)
        else:
            self.draw.polygon(config.grey, zone_points, width=5)

        zone_label.draw(self.screen)

        # draw border around matrix for zone
        if self.m.zone_state:
            self.draw.polygon(
                self.zone_colour,
                self.draw.transformCoordinates(
                    [matrix_left_top, (matrix_left_top[0] + self.m.width, matrix_left_top[1]),
                     (matrix_left_top[0] + self.m.width, matrix_left_top[1] + self.m.height),
                     (matrix_left_top[0], matrix_left_top[1] + self.m.height)]), width=10)

    # (TODO): switch to using self.m instead of passing in m
    def drawClearText(self):
        matrix_left_top = self.m.topleft

        if self.m.prev_clear_text != [''] and self.m.prev_clear_text != self.m.track_clear_text:
            self.m.track_clear_text = self.m.prev_clear_text
            self.m.clear_text.clear()
            self.m.clear_flag = self.getTick()
            for i in range(len(self.m.prev_clear_text)):
                if self.m.prev_clear_text[i].find("PERFECT CLEAR") != -1:
                    self.m.clear_text.append(Label(
                        self.font, self.m.prev_clear_text[i], config.yellow,
                        self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                            matrix_left_top[1] + (5 + i) * self.font_size)), "topright"))
                elif self.m.prev_clear_text[i].find("T-SPIN") != -1:
                    self.m.clear_text.append(Label(
                        self.font, self.m.prev_clear_text[i], config.purple,
                        self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                            matrix_left_top[1] + (5 + i) * self.font_size)), "topright"))
                elif self.m.prev_clear_text[i].find("B2B") != -1:
                    self.m.clear_text.append(Label(
                        self.font, self.m.prev_clear_text[i], config.light_blue,
                        self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                            matrix_left_top[1] + (5 + i) * self.font_size)), "topright"))
                elif self.m.prev_clear_text[i].find("TRIS") != -1:
                    self.m.clear_text.append(Label(
                        self.font, self.m.prev_clear_text[i], self.zone_colour,
                        self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                            matrix_left_top[1] + (5 + i) * self.font_size)), "topright"))
                else:
                    self.m.clear_text.append(Label(
                        self.font, self.m.prev_clear_text[i], config.white,
                        self.draw.transformCoordinates((matrix_left_top[0] - self.offset,
                            matrix_left_top[1] + (5 + i) * self.font_size)), "topright"))
            for msg in self.m.clear_text:
                msg.draw(self.screen)
            
            self.playClearSfx() # play sfx

        else:
            if self.m.clear_flag is not None:
                if self.getTick() - self.m.clear_flag <= 2000:  # show for 2 seconds max
                    for msg in self.m.clear_text:
                        msg.draw(self.screen)
                else:
                    self.m.clear_flag = None
            if self.m.prev_clear_text == ['']:
                self.m.track_clear_text.clear()

    def playClearSfx(self):
        sfx_path = os.path.abspath('./src/sounds/sfx')
        sfx_file = ""
        i = self.m.prev_clear_text[0]
        if i=="SINGLE":
            sfx_file = "01_single.wav"
        elif i=="DOUBLE":
            sfx_file = "02_double.wav"
        elif i=="TRIPLE":
            sfx_file = "03_triple.wav"
        elif i=="QUADRUPLE":
            sfx_file = "04_tetris.wav"
        elif i=="B2B QUADRUPLE":
            sfx_file = "05_b2btetris.wav"
        elif i=="T-SPIN":
            sfx_file = "06_tspin.wav"
        elif i=="MINI T-SPIN" or i=="MINI T-SPIN SINGLE" or i=="MINI T-SPIN DOUBLE":
            sfx_file = "07_tspinmini.wav"
        elif i=="T-SPIN SINGLE":
            sfx_file = "08_tspinsingle.wav"
        elif i=="T-SPIN DOUBLE":
            sfx_file = "09_tspindouble.wav"
        elif i=="T-SPIN TRIPLE":
            sfx_file = "10_tspintriple.wav"
        elif i=="B2B MINI T-SPIN SINGLE" or i=="B2B MINI T-SPIN DOUBLE":
            sfx_file = "11_b2btspinmini.wav"
        elif i=="B2B T-SPIN SINGLE":
            sfx_file = "12_b2btspinsingle.wav"
        elif i=="B2B T-SPIN DOUBLE":
            sfx_file = "13_b2btspindouble.wav"
        elif i=="B2B T-SPIN TRIPLE":
            sfx_file = "14_b2btspintriple.wav"
        elif i=="PERFECT CLEAR":
            sfx_file = "16_perfectclear.wav"
        sfx_path = os.path.join(sfx_path,sfx_file)
        if os.path.isfile(sfx_path):
            self.cls.mixer.Sound(sfx_path).play()

    def playMoveSfx(self, move, cond=True):
        sfx_path = os.path.abspath('./src/sounds/sfx')
        sfx_file = ""
        if move == constants.Action.HARD_DROP:
            sfx_file = "sfx_harddrop.wav"
        elif move == constants.Action.ROTATE_CW or move == constants.Action.ROTATE_CCW or move == constants.Action.ROTATE_180:
            sfx_file = "sfx_rotate.wav"
        elif move == constants.Action.SWAP_HOLD and self.hold_available: # cant be matrix's hold_available variable because hold is processed before sfx plays
            sfx_file = "sfx_hold.wav"
        elif move == constants.Action.SHIFT_LEFT or move == constants.Action.SHIFT_RIGHT:
            sfx_file = "sfx_move.wav"
        elif move == constants.Action.SOFT_DROP:
            sfx_file = "sfx_softdrop.wav"
        elif move == "AUTOLOCK":
            sfx_file = "sfx_lockdown.wav"
        sfx_path = os.path.join(sfx_path,sfx_file)
        if os.path.isfile(sfx_path) and cond:
            self.cls.mixer.Sound(sfx_path).play()

    def getZoneTimer(self):
        if self.m.zone_state:
            current_tick = self.getTick()
            if self.m.current_zone == 0:
                self.m.leaveZone()
                self.start_zone_tick = None
                return
            if current_tick - self.start_zone_tick >= 500:  # full zone (40 lines) -> 20 zone seconds
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
        if self.m.game_mode == constants.GameMode.SPRINT:
            time_str += "." + str(milles)
            if self.m.objective_met:
                self.sprint_time = time_str
        return time_str

    def getScore(self):  # current score
        return str(self.m.getScore())

    def getTick(self):
        if self.player:
            return self.cls.time.get_ticks()
        else:
            return self.ticks

    def getLockDelay(self):
        if self.player:
            return self.lock_delay
        else:
            return self.its_for_lock

    def getFixedInput(self, key_event, key_press):  # for single actions (hard drop, rotations, swap hold)
        DBG = False
        # no das when using env-mode
        if key_event == self.cls.KEYDOWN:
            if key_press in config.key2action:
                if config.key2action[key_press] == constants.Action.HARD_DROP:
                    self.m.hardDrop()
                    if DBG:
                        print("HARD_DROP")
                    self.getMoveStatus(True)
                elif config.key2action[key_press] == constants.Action.ROTATE_CW:
                    self.m.rotateCW()
                    if DBG:
                        print("ROTATE_CW")
                    self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == constants.Action.ROTATE_CCW:
                    self.m.rotateCCW()
                    if DBG:
                        print("ROTATE_CCW")
                    self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == constants.Action.ROTATE_180:
                    self.m.rotate180()
                    if DBG:
                        print("ROTATE_180")
                    self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == constants.Action.SWAP_HOLD:
                    self.m.swapHold()
                    if DBG:
                        print("SWAP_HOLD")
                    self.getMoveStatus(True)
                    self.log_buffer["piece_placed"] = False
                elif config.key2action[key_press] == constants.Action.SHIFT_LEFT:
                    if DBG:
                        print("SHIFT_LEFT")
                    if self.player:
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
                elif config.key2action[key_press] == constants.Action.SHIFT_RIGHT:
                    if DBG:
                        print("SHIFT_RIGHT")
                    if self.player:
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
                elif config.key2action[key_press] == constants.Action.SOFT_DROP:
                    if DBG:
                        print("SOFT_DROP")
                    self.soft_drop_tick = self.getTick()
                    if not self.player:
                        self.m.softDrop()
                        self.getMoveStatus(tick=self.getTick())
                elif config.key2action[key_press] == constants.Action.RESET:
                    if DBG:
                        print("RESET")
                    self.reset()
                elif config.key2action[key_press] == constants.Action.ACTIVATE_ZONE:
                    if DBG:
                        print("ACTIVATE_ZONE")
                    if self.m.zoneReady():
                        self.m.activateZone()
                        self.start_zone_tick = self.getTick()

                cond = config.key2action[key_press] != constants.Action.SHIFT_LEFT and config.key2action[key_press] != constants.Action.SHIFT_RIGHT
                self.playMoveSfx(config.key2action[key_press],cond)

        elif key_event == self.cls.KEYUP:  # reset das, arr, and soft drop
            if key_press in config.key2action:
                if config.key2action[key_press] == constants.Action.SHIFT_LEFT:
                    self.left_das_tick = None
                    self.left_arr_tick = None
                elif config.key2action[key_press] == constants.Action.SHIFT_RIGHT:
                    self.right_das_tick = None
                    self.right_arr_tick = None
                elif config.key2action[key_press] == constants.Action.SOFT_DROP:
                    self.soft_drop_tick = None

    def getContinuousInput(self):  # for continuous actions (shift left, shift right, soft drop)
        keys = self.cls.key.get_pressed()

        current_tick = self.getTick()

        if not keys[config.action2key[constants.Action.SHIFT_LEFT]] and not keys[config.action2key[constants.Action.SHIFT_RIGHT]]:  # reset direction
            self.das_direction = None

        if self.cancel_das:
            if self.left_das_tick is None and (keys[config.action2key[constants.Action.SHIFT_LEFT]] and not keys[
                config.action2key[constants.Action.SHIFT_RIGHT]]):  # das was cancelled but key was held down still
                self.left_das_tick = current_tick
                self.das_direction = "LEFT"
            if self.right_das_tick is None and (keys[config.action2key[constants.Action.SHIFT_RIGHT]] and not keys[
                config.action2key[constants.Action.SHIFT_LEFT]]):  # das was cancelled but key was held down still
                self.right_das_tick = current_tick
                self.das_direction = "RIGHT"
        else:
            if self.das_direction == "RIGHT" and (keys[config.action2key[constants.Action.SHIFT_LEFT]] and not keys[
                config.action2key[constants.Action.SHIFT_RIGHT]]):  # direction changed but no das cancellation
                self.das_direction = "LEFT"
            if self.das_direction == "LEFT" and (keys[config.action2key[constants.Action.SHIFT_RIGHT]] and not keys[
                config.action2key[constants.Action.SHIFT_LEFT]]):  # direction changed but no das cancellation
                self.das_direction = "RIGHT"

        if self.das_direction == "LEFT" and self.left_das_tick is not None:  # das was already started
            if current_tick - self.left_das_tick >= self.das and keys[config.action2key[constants.Action.SHIFT_LEFT]]:
                # if pressed for das duration, set in arr
                if self.left_arr_tick is None:
                    self.left_arr_tick = current_tick
                else:  # set in arr
                    if current_tick - self.left_arr_tick >= self.arr:
                        cond = self.m.shiftLeft()
                        self.left_arr_tick = current_tick
                        self.getMoveStatus(tick=current_tick)
                        self.playMoveSfx(constants.Action.SHIFT_LEFT,cond)
            elif self.shift_once:  # das duration not met, only shift tetromino once
                self.shift_once = False
                cond = self.m.shiftLeft()
                self.getMoveStatus(tick=current_tick)
                self.playMoveSfx(constants.Action.SHIFT_LEFT,cond)

        elif self.das_direction == "RIGHT" and self.right_das_tick is not None:
            if current_tick - self.right_das_tick >= self.das and keys[config.action2key[constants.Action.SHIFT_RIGHT]]:
                if self.right_arr_tick is None:
                    self.right_arr_tick = current_tick
                else:  # set in arr
                    if current_tick - self.right_arr_tick >= self.arr:
                        cond = self.m.shiftRight()
                        self.right_arr_tick = current_tick
                        self.getMoveStatus(tick=current_tick)
                        self.playMoveSfx(constants.Action.SHIFT_RIGHT,cond)
            elif self.shift_once:
                self.shift_once = False
                cond = self.m.shiftRight()
                self.getMoveStatus(tick=current_tick)
                self.playMoveSfx(constants.Action.SHIFT_RIGHT,cond)

        if self.soft_drop_tick is not None and keys[
            config.action2key[constants.Action.SOFT_DROP]]:  # treat soft drop like faster gravity
            if (current_tick - self.soft_drop_tick) >= 1000 // self.soft_drop_speed:
                self.m.softDrop()
                self.soft_drop_tick = current_tick
                self.getMoveStatus(tick=current_tick)
                self.playMoveSfx(constants.Action.SOFT_DROP)

    def getMoveStatus(self, reset=False, tick=None):
        if self.enforce_auto_lock:
            if reset:
                self.visited.fill(0)  # reset visited array
                self.prev_move_tick = None if self.player else self.getTick()
                self.enforce_lock_delay = False
                self.move_cnt = 0

                self.log_buffer["piece_placed"] = True
            else:
                self.prev_move_tick = tick
                self.move_cnt += 1 if self.enforce_lock_delay else 0

    def gravityEq(self, level):
        return (0.8 - ((level - 1) * 0.007)) ** (level - 1)

    def updateGravity(self):
        self.gravity = 1 / self.gravityEq(self.m.level)

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
        # print("{} {} {}".format(current_tick, self.prev_move_tick, self.getLockDelay()), file=sys.stderr)
        # print(self.m.mino_locations, file=sys.stderr)
        # print(self.m.touchedStack(), file=sys.stderr)
        if self.enforce_auto_lock and self.m.touchedStack() and self.prev_move_tick is not None:
            if current_tick - self.prev_move_tick >= self.getLockDelay():
                self.m.freezeTetromino()
                self.getMoveStatus(True)
                self.playMoveSfx("AUTOLOCK")
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
                        self.playMoveSfx("AUTOLOCK")

    def objectiveMet(self):
        return self.m.objective_met

    def gameOver(self):
        return self.m.game_over

    def reset(self):
        self.m.resetMatrix()
        self.m.addTetromino()
        if not self.m.game_mode == constants.GameMode.ZEN:
            self.game_start_tick = self.getTick()

    def processEvents(self, events=[]):
        self.log_buffer.clear()
        for event in events:
            if event.type == self.cls.KEYDOWN or event.type == self.cls.KEYUP:
                self.getFixedInput(event.type, event.key)

        self.getContinuousInput()


    def render(self, events=[]):
        if self.game_start_tick is None:
            # initialize game
            self.game_start_tick = self.getTick()
            self.start_tick = self.game_start_tick
            self.m.addTetromino()

        self.hold_available = self.m.hold_available # for hold sfx 

        self.processEvents(events)

        self.enforceAutoLock()
        self.drawMatrix()
        self.drawGhost()
        self.drawGrid()
        self.drawQueue()
        self.drawHold()
        self.drawText()
        self.drawClearText()
        self.drawZoneMeter()

        cur_tick = self.getTick()
        if cur_tick - self.start_tick >= 1000 // self.gravity and not self.m.zone_state:
            self.start_tick = cur_tick
            self.m.enforceGravity()
            self.getMoveStatus(tick=cur_tick)

        if self.m.game_mode == constants.GameMode.JOURNEY:
            self.updateGravity()

    def get_copy(self, **kwargs):
        g = GameState(
            cls=self.cls,
            draw=self.draw,
            graphic_mode=self.use_graphics,
            game_mode=self.game_mode,
            **kwargs    
        )

        # copy over any state variables
        g.gravity = self.gravity
        g.das = self.das
        g.arr = self.arr
        g.soft_drop_speed = self.soft_drop_speed

        g.das_direction = self.das_direction
        g.left_das_tick = self.left_das_tick
        g.right_das_tick = self.right_das_tick
        g.left_arr_tick = self.left_arr_tick
        g.right_arr_tick = self.right_arr_tick
        g.soft_drop_tick = self.soft_drop_tick
        g.shift_once = self.shift_once
        g.cancel_das = self.cancel_das

        g.game_start_tick = self.game_start_tick
        g.start_tick = self.start_tick
        g.start_zone_tick = self.start_zone_tick
        g.sprint_time = self.sprint_time
        g.ghostPiece = self.ghostPiece
        g.showGrid = self.showGrid

        g.enforce_auto_lock = self.enforce_auto_lock
        g.move_reset = self.move_reset
        g.lock_delay = self.lock_delay
        g.prev_move_tick = self.prev_move_tick
        g.move_cnt = self.move_cnt
        g.enforce_lock_delay = self.enforce_lock_delay
        g.hold_available = self.hold_available

        g.log_buffer = self.log_buffer
        g.m = copy.deepcopy(self.m)
        g.visited = copy.deepcopy(self.visited)

        return g