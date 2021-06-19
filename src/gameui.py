import sys
import pygame
import pyautogui
import time
import numpy as np
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

font_size = m.mino_dim
font = pygame.font.Font(None,font_size)

black = 0, 0, 0
white = 255, 255, 255
grey = 128, 128, 128
yellow = 255, 255, 0

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
def drawGrid(showGrid=True):
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
            elif config.key2action[key_press] == "ROTATE_CW":
                m.rotateCW()
                print("ROTATE_CW")
            elif config.key2action[key_press] == "ROTATE_CCW":
                m.rotateCCW()
                print("ROTATE_CCW")
            elif config.key2action[key_press] == "ROTATE_180":
                m.rotate180()
                print("ROTATE_180")
            elif config.key2action[key_press] == "SWAP_HOLD": #note: remember to implement way to stop swap_hold being executed consecutively
                m.swapHold()
                print("SWAP_HOLD")
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
        elif shift_once: # das duration not met, only shift tetromino once
            shift_once = False
            m.shiftLeft()

    elif das_direction == "RIGHT" and right_das_tick != None:
        if current_tick - right_das_tick >= das and keys[config.action2key["SHIFT_RIGHT"]]:
            if right_arr_tick == None:
                right_arr_tick = current_tick
            else: # set in arr
                if current_tick - right_arr_tick >= arr:
                    m.shiftRight()
                    right_arr_tick = current_tick
        elif shift_once:
            shift_once = False
            m.shiftRight()

    if soft_drop_tick != None and keys[config.action2key["SOFT_DROP"]]: # treat soft drop like faster gravity
        if (current_tick - soft_drop_tick) >= 1000//soft_drop_speed:
            m.softDrop()
            soft_drop_tick = current_tick

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
    screen.fill(black)
    drawMatrix()
    drawGhost()
    drawGrid()
    drawQueue()
    drawHold()
    drawText()
    pygame.display.flip()

    end_tick = pygame.time.get_ticks()
    if(end_tick - start_tick) >= 1000//gravity:
        start_tick = end_tick
        # m.enforceGravity()
        print(m.matrix)

