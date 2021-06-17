import sys
import pygame
import pyautogui
import time
import numpy as np
from .utils import matrix

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

def drawMatrix(showGrid=True):
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

# for testing purposes only
m.addTetromino()
m.swapHold()
print(m.matrix)
starttick = pygame.time.get_ticks()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(black)
    drawMatrix()
    drawQueue()
    drawHold()
    drawText()
    pygame.display.flip()

    endtick = pygame.time.get_ticks()
    if(endtick - starttick) >= 1000//gravity:
        starttick = endtick
        if(not m.enforceGravity()):
            m.addTetromino()
        print(m.matrix)

