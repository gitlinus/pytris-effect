import sys
import pygame
import pyautogui
import time
import numpy as np
import math
from .utils import matrix
from .utils import config

pygame.init()

screen_width, screen_height = pyautogui.size()
m = matrix.Matrix(2*screen_height//60) # matrix height should be roughly 2/3 of screen height
vertical_offset = 50
offset = 50
screen_size = screen_width, screen_height-vertical_offset
screen = pygame.display.set_mode(size=screen_size, flags=pygame.SCALED)
matrix_left_top = (screen_width-m.width)//2, (screen_height-m.height)//2

pygame.display.set_caption('Pytris Effect')

font_size = m.mino_dim # font_size should be the same as the width of a single mino
font = pygame.font.Font(None,font_size)

black = 0, 0, 0
white = 255, 255, 255
grey = 128, 128, 128
yellow = 255, 255, 0
purple = 255, 0, 255
light_blue = 0, 127, 255
zone_colour = pygame.Color('dodgerblue')

gravity = 1 # number of blocks per second at which the tetromino falls
das = 120 # (delayed auto-shift) number of milleseconds before arr sets in
arr = 50 # (auto repeat rate) number of milleseconds in between each time the tetromino is shifted
soft_drop_speed = 10 # rate (minos per second) at which soft drop makes the tetromino fall
das_direction = None
left_das_tick = None
right_das_tick = None
left_arr_tick = None
right_arr_tick = None
soft_drop_tick = None
shift_once = False
cancel_das = True # leave true by default

ghostPiece = True
showGrid = True

enforce_auto_lock = True # turns on auto locking of pieces when they touch the stack if True
move_reset = 15 # the maximum number of moves the player can make after the tetromino touches the stack
lock_delay = 500 # maximum of milleseconds in between moves after the tetromino touches the stack before it is locked in place
prev_move_tick = None
move_cnt = 0
visited = np.zeros((m.matrix.shape[0],m.matrix.shape[1]),dtype=int)
enforce_lock_delay = False

# text labels beside matrix
class Label:
    def __init__(self, font, text, colour, position, anchor="topleft"):
        self.image = font.render(text, True, colour)
        self.rect = self.image.get_rect()
        setattr(self.rect, anchor, position)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

time_label = Label(font,"TIME",yellow,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3))
score_label = Label(font,"SCORE",yellow,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3+3*font_size))
lines_label = Label(font,"LINES",yellow,(matrix_left_top[0]-offset,matrix_left_top[1]+2*m.height//3),"topright")
zone_label = Label(font,"ZONE",yellow,(matrix_left_top[0]-offset-2*font_size,matrix_left_top[1]+m.height-2*font_size),"center")
# zone shape is a square diamond, diagonal length = 4*font_size
zone_points = [
                (matrix_left_top[0]-offset-2*font_size,matrix_left_top[1]+m.height-4*font_size),
                (matrix_left_top[0]-offset,matrix_left_top[1]+m.height-2*font_size),
                (matrix_left_top[0]-offset-2*font_size,matrix_left_top[1]+m.height),
                (matrix_left_top[0]-offset-4*font_size,matrix_left_top[1]+m.height-2*font_size)
            ] # top, right, bottom, left
zone_center = (matrix_left_top[0]-offset-2*font_size,matrix_left_top[1]+m.height-2*font_size)

def drawMatrix():
    pygame.draw.rect(screen,white,pygame.Rect(matrix_left_top,m.dim()))

    # draw piece spawn area:
    for i in range(2):
        for j in range(10):
            if m.matrix[i,j]!=0:
                pygame.draw.rect(
                    screen,
                    m.index2rgb[m.matrix[i,j]],
                    pygame.Rect((matrix_left_top[0]+j*m.mino_dim,
                                matrix_left_top[1]-(2-i)*m.mino_dim),
                                (m.mino_dim,m.mino_dim))
                )

    # draw the actual matrix area:
    for i in range(20):
        for j in range(10):
            if m.matrix[i+2,j]!=0:
                pygame.draw.rect(
                    screen,
                    m.index2rgb[m.matrix[i+2,j]],
                    pygame.Rect((matrix_left_top[0]+j*m.mino_dim,
                                matrix_left_top[1]+i*m.mino_dim),
                                (m.mino_dim,m.mino_dim))
                )

def drawQueue(length=5): # max queue length of 5
    if(length>5): 
        length = 5
    queue = m.getQueue()
    drawingSpace = np.zeros((3,4),dtype=int)

    for i in range(length):
        tetr = queue[i]
        tetr_mat = m.tetromino2matrix[tetr]
        drawingSpace[0:tetr_mat.shape[0],0:tetr_mat.shape[1]] += tetr_mat

        for row in range(drawingSpace.shape[0]):
            for col in range(drawingSpace.shape[1]):
                if drawingSpace[row,col] != 0:
                    pygame.draw.rect(
                        screen,
                        m.index2rgb[drawingSpace[row,col]],
                        pygame.Rect((matrix_left_top[0]+m.width+offset+col*m.mino_dim,
                                    matrix_left_top[1]+(3*i+row-2)*m.mino_dim),
                                    (m.mino_dim,m.mino_dim))
                    )
                    drawingSpace[row,col] = 0

def drawHold():
    tetr = m.getHold()
    if tetr != "":
        drawingSpace = np.zeros((3,4),dtype=int)
        tetr_mat = m.tetromino2matrix[tetr]
        if tetr != 'I':
            drawingSpace[0:tetr_mat.shape[0],1:tetr_mat.shape[1]+1] += tetr_mat
        else:
            drawingSpace[0:tetr_mat.shape[0],0:tetr_mat.shape[1]] += tetr_mat

        for row in range(drawingSpace.shape[0]):
            for col in range(drawingSpace.shape[1]):
                if drawingSpace[row,col] != 0:
                    pygame.draw.rect(
                        screen,
                        m.index2rgb[drawingSpace[row,col]],
                        pygame.Rect((matrix_left_top[0]-offset+(col-4)*m.mino_dim,
                                    matrix_left_top[1]+(row-2)*m.mino_dim),
                                    (m.mino_dim,m.mino_dim))
                    )
                    drawingSpace[row,col] = 0

def drawGhost(): # draws ghost piece
    if ghostPiece:
        dist = 0 
        found = False
        for r in range(21): # at most drop by a distance of 20
            for i in m.mino_locations:
                if i[0]+r >= m.matrix.shape[0] or (m.matrix[i[0]+r,i[1]] != 0 and (i[0]+r,i[1]) not in m.mino_locations):
                    found = True
                    break
            if found: break
            else: dist = r
        for pos in m.mino_locations: # draw ghost piece darker then actual piece colour
            if (dist+pos[0],pos[1]) not in m.mino_locations: # don't cover actual piece
                pygame.draw.rect(
                        screen,
                        (lambda a: (a[0]//3, a[1]//3, a[2]//3))(m.tetromino2rgb[m.current_tetromino]),
                        pygame.Rect((matrix_left_top[0]+pos[1]*m.mino_dim,
                                    matrix_left_top[1]+(dist+pos[0]-2)*m.mino_dim),
                                    (m.mino_dim,m.mino_dim))
                    )
def drawGrid():
# draw grid
    if showGrid:
        for i in range(11): #vertical lines
            pygame.draw.line(screen,grey,
                (matrix_left_top[0]+i*m.mino_dim,matrix_left_top[1]-2*m.mino_dim),
                (matrix_left_top[0]+i*m.mino_dim,matrix_left_top[1]+m.height)
            )
        for i in range(22): #horizontal lines
            pygame.draw.line(screen,grey,
                (matrix_left_top[0],matrix_left_top[1]+(i-1)*m.mino_dim),
                (matrix_left_top[0]+m.width,matrix_left_top[1]+(i-1)*m.mino_dim)
            )

def drawText():
    time_label.draw(screen)
    Label(font,getTimer(),yellow,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3+font_size)).draw(screen)
    score_label.draw(screen)
    Label(font,getScore(),yellow,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3+4*font_size)).draw(screen)
    lines_label.draw(screen)
    Label(font,getStats(),yellow,(matrix_left_top[0]-offset,matrix_left_top[1]+2*m.height//3+font_size),"topright").draw(screen)

def drawZoneMeter():
    percentage_filled = m.current_zone / m.full_zone 
    if 0 < percentage_filled and percentage_filled < 0.5: # draw triangle
        height = math.sqrt(percentage_filled * 8 * font_size * font_size)
        shift = math.tan(math.pi/4) * height
        right_point = (zone_center[0] + shift, zone_points[2][1] - height)
        left_point = (zone_center[0] - shift, zone_points[2][1] - height)
        pygame.draw.polygon(screen, zone_colour, [right_point, zone_points[2], left_point])
    elif percentage_filled == 0.5:
        pygame.draw.polygon(screen, zone_colour, [zone_points[1], zone_points[2], zone_points[3]])
    elif percentage_filled > 0.5 and percentage_filled < 1:
        height = math.sqrt((1-percentage_filled) * 8 * font_size * font_size)
        shift = math.tan(math.pi/4) * height
        right_point = (zone_center[0] + shift, zone_points[0][1] + height)
        left_point = (zone_center[0] - shift, zone_points[0][1] + height)
        pygame.draw.polygon(screen, zone_colour, zone_points)
        pygame.draw.polygon(screen, black, [left_point, zone_points[0], right_point])
    elif percentage_filled >= 1:
        pygame.draw.polygon(screen, zone_colour, zone_points)
    if percentage_filled >= 1: # yellow border if filled
        pygame.draw.polygon(screen, yellow, zone_points, width=5)
    else:
        pygame.draw.polygon(screen, grey, zone_points, width=5)
    zone_label.draw(screen)

clear_flag = None
clear_text = []
track_clear_text = []
def drawClearText():
    global clear_flag, clear_text, track_clear_text
    if m.prev_clear_text != [''] and m.prev_clear_text != track_clear_text:
        track_clear_text = m.prev_clear_text
        clear_text.clear()
        clear_flag = pygame.time.get_ticks()
        for i in range(len(m.prev_clear_text)):
            if m.prev_clear_text[i].find("PERFECT CLEAR") != -1:
                clear_text.append(Label(font,m.prev_clear_text[i],yellow,(matrix_left_top[0]-offset,matrix_left_top[1]+(5+i)*font_size),"topright"))
            elif m.prev_clear_text[i].find("T-SPIN") != -1:
                clear_text.append(Label(font,m.prev_clear_text[i],purple,(matrix_left_top[0]-offset,matrix_left_top[1]+(5+i)*font_size),"topright"))
            elif m.prev_clear_text[i].find("B2B") != -1:
                clear_text.append(Label(font,m.prev_clear_text[i],light_blue,(matrix_left_top[0]-offset,matrix_left_top[1]+(5+i)*font_size),"topright"))
            else:
                clear_text.append(Label(font,m.prev_clear_text[i],white,(matrix_left_top[0]-offset,matrix_left_top[1]+(5+i)*font_size),"topright"))
        for msg in clear_text:
            msg.draw(screen)
    else:
        if clear_flag != None:
            if(pygame.time.get_ticks() - clear_flag <= 2000): # show for 2 seconds max
                for msg in clear_text:
                    msg.draw(screen)
            else:
                clear_flag = None
        if m.prev_clear_text == ['']:
            track_clear_text.clear()

def getStats(): # number of lines cleared
    return str(m.getLines())
        
def getTimer(): # time elapsed
    time_passed = pygame.time.get_ticks()
    hours = time_passed // 1000 // 60 // 60
    minutes = time_passed // 1000 // 60 % 60
    seconds = time_passed // 1000 % 60
    time_str = ""
    time_str += str(hours)+":" if hours != 0 else ""
    time_str += str(minutes)+":" if minutes >= 10 else "0"+str(minutes)+":"
    time_str += str(seconds) if seconds >= 10 else "0"+str(seconds)
    return time_str

def getScore(): # current score
    return str(m.getScore())

def getFixedInput(key_event, key_press): # for single actions (hard drop, rotations, swap hold)
    global das_direction, left_das_tick, right_das_tick, left_arr_tick, right_arr_tick, soft_drop_tick, shift_once

    if key_event == pygame.KEYDOWN:
        if key_press in config.key2action:
            if config.key2action[key_press] == "HARD_DROP":
                m.hardDrop()
                print("HARD_DROP")
                getMoveStatus(True)
            elif config.key2action[key_press] == "ROTATE_CW":
                m.rotateCW()
                print("ROTATE_CW")
                getMoveStatus(tick=pygame.time.get_ticks())
            elif config.key2action[key_press] == "ROTATE_CCW":
                m.rotateCCW()
                print("ROTATE_CCW")
                getMoveStatus(tick=pygame.time.get_ticks())
            elif config.key2action[key_press] == "ROTATE_180":
                m.rotate180()
                print("ROTATE_180")
                getMoveStatus(tick=pygame.time.get_ticks())
            elif config.key2action[key_press] == "SWAP_HOLD": #note: remember to implement way to stop swap_hold being executed consecutively
                m.swapHold()
                print("SWAP_HOLD")
                getMoveStatus(True)
            elif config.key2action[key_press] == "SHIFT_LEFT":
                print("SHIFT_LEFT")
                shift_once = True
                das_direction = "LEFT"
                left_das_tick = pygame.time.get_ticks()
                right_arr_tick = None
                if cancel_das:
                    right_das_tick = None
                else:
                    if right_das_tick != None:
                        left_das_tick = right_das_tick
            elif config.key2action[key_press] == "SHIFT_RIGHT":
                print("SHIFT_RIGHT")
                shift_once = True
                das_direction = "RIGHT"
                right_das_tick = pygame.time.get_ticks()
                left_arr_tick = None
                if cancel_das:
                    left_das_tick = None
                else:
                    if left_das_tick != None:
                        right_das_tick = left_das_tick
            elif config.key2action[key_press] == "SOFT_DROP":
                print("SOFT_DROP")
                soft_drop_tick = pygame.time.get_ticks()
            elif config.key2action[key_press] == "RESET":
                print("RESET")
                m.resetMatrix()
                m.addTetromino()

    elif key_event == pygame.KEYUP: # reset das, arr, and soft drop
        if key_press in config.key2action:
            if config.key2action[key_press] == "SHIFT_LEFT":
                left_das_tick = None
                left_arr_tick = None
            elif config.key2action[key_press] == "SHIFT_RIGHT":
                right_das_tick = None
                right_arr_tick = None
            elif config.key2action[key_press] == "SOFT_DROP":
                soft_drop_tick = None

def getContinuousInput(): # for continuous actions (shift left, shift right, soft drop)
    keys = pygame.key.get_pressed()

    global das_direction, left_das_tick, left_arr_tick, right_das_tick, right_arr_tick, soft_drop_tick, shift_once
    current_tick = pygame.time.get_ticks()

    if not keys[config.action2key["SHIFT_LEFT"]] and not keys[config.action2key["SHIFT_RIGHT"]]: # reset direction
        das_direction = None

    if cancel_das:
        if left_das_tick == None and (keys[config.action2key["SHIFT_LEFT"]] and not keys[config.action2key["SHIFT_RIGHT"]]): # das was cancelled but key was held down still
            left_das_tick = current_tick
            das_direction = "LEFT"
        if right_das_tick == None and (keys[config.action2key["SHIFT_RIGHT"]] and not keys[config.action2key["SHIFT_LEFT"]]): # das was cancelled but key was held down still
            right_das_tick = current_tick
            das_direction = "RIGHT"
    else:
        if das_direction == "RIGHT" and (keys[config.action2key["SHIFT_LEFT"]] and not keys[config.action2key["SHIFT_RIGHT"]]): # direction changed but no das cancellation
            das_direction = "LEFT"
        if das_direction == "LEFT" and (keys[config.action2key["SHIFT_RIGHT"]] and not keys[config.action2key["SHIFT_LEFT"]]): # direction changed but no das cancellation
            das_direction = "RIGHT"

    if das_direction == "LEFT" and left_das_tick != None: # das was already started
        if current_tick - left_das_tick >= das and keys[config.action2key["SHIFT_LEFT"]]: # if pressed for das duration, set in arr
            if left_arr_tick == None:    
                left_arr_tick = current_tick
            else: # set in arr
                if current_tick - left_arr_tick >= arr:
                    m.shiftLeft()
                    left_arr_tick = current_tick
                    getMoveStatus(tick=current_tick)
        elif shift_once: # das duration not met, only shift tetromino once
            shift_once = False
            m.shiftLeft()
            getMoveStatus(tick=current_tick)

    elif das_direction == "RIGHT" and right_das_tick != None:
        if current_tick - right_das_tick >= das and keys[config.action2key["SHIFT_RIGHT"]]:
            if right_arr_tick == None:
                right_arr_tick = current_tick
            else: # set in arr
                if current_tick - right_arr_tick >= arr:
                    m.shiftRight()
                    right_arr_tick = current_tick
                    getMoveStatus(tick=current_tick)
        elif shift_once:
            shift_once = False
            m.shiftRight()
            getMoveStatus(tick=current_tick)

    if soft_drop_tick != None and keys[config.action2key["SOFT_DROP"]]: # treat soft drop like faster gravity
        if (current_tick - soft_drop_tick) >= 1000//soft_drop_speed:
            m.softDrop()
            soft_drop_tick = current_tick
            getMoveStatus(tick=current_tick)

def getMoveStatus(reset=False,tick=None):
    global enforce_auto_lock, prev_move_tick, enforce_lock_delay, move_cnt, visited
    if enforce_auto_lock:
        if reset:
            visited.fill(0) # reset visited array
            prev_move_tick = None
            enforce_lock_delay = False
            move_cnt = 0
        else:
            prev_move_tick = tick
            move_cnt += 1 if enforce_lock_delay else 0

def updateVisited():
    global visited
    for i in m.mino_locations:
        visited[i[0],i[1]] = 1

def alreadyVisited():
    global visited
    for i in m.mino_locations:
        if not visited[i[0],i[1]]: 
            return False
    return True

def enforceAutoLock():
    """
        if touchedStack 
            get current tick and tick of last move
            if lock delay reached -> freeze tetromino
            else
                if location not visited -> reset move counter
                else -> turn on enforce_lock_delay
                    if move_reset equals move counter -> freeze tetromino
    """
    global enforce_auto_lock, prev_move_tick, lock_delay, enforce_lock_delay, move_cnt, move_reset, visited
    current_tick = pygame.time.get_ticks()
    if enforce_auto_lock and m.touchedStack() and prev_move_tick != None:
        if current_tick - prev_move_tick >= lock_delay:
            m.freezeTetromino()
            getMoveStatus(True)
        else:
            if not alreadyVisited():
                move_cnt = 0
                enforce_lock_delay = False
                updateVisited()
            else:
                enforce_lock_delay = True
                if move_cnt >= move_reset:
                    m.freezeTetromino()
                    getMoveStatus(True)

# for testing purposes only
m.addTetromino()
# print(m.matrix)
start_tick = pygame.time.get_ticks()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            getFixedInput(event.type, event.key)

    getContinuousInput()
    enforceAutoLock()
    screen.fill(black)
    drawMatrix()
    drawGhost()
    drawGrid()
    drawQueue()
    drawHold()
    drawText()
    drawClearText()
    drawZoneMeter()
    pygame.display.flip()

    end_tick = pygame.time.get_ticks()
    if(end_tick - start_tick) >= 1000//gravity:
        start_tick = end_tick
        m.enforceGravity()
        getMoveStatus(tick=end_tick)
        # print(m.matrix)

