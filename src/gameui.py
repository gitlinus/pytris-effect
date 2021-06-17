import sys
import pygame
import pyautogui
import time
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

        
def drawTimer():
    time_passed = pygame.time.get_ticks()
    hours = time_passed // 1000 // 60 // 60
    minutes = time_passed // 1000 // 60 % 60
    seconds = time_passed // 1000 % 60
    time_str = ""
    time_str += str(hours)+":" if hours != 0 else ""
    time_str += str(minutes)+":" if minutes >= 10 else "0"+str(minutes)+":"
    time_str += str(seconds) if seconds >= 10 else "0"+str(seconds)
    text = font.render("TIME", True, yellow)
    screen.blit(text,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3))
    text = font.render(str(time_str), True, yellow)
    screen.blit(text,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3+font_size))

def drawScore():
    text = font.render("SCORE", True, yellow)
    screen.blit(text,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3+3*font_size))
    text = font.render(str(m.getScore()), True, yellow)
    screen.blit(text,(matrix_left_top[0]+m.width+offset,matrix_left_top[1]+2*m.height//3+4*font_size))

m.addTetromino()
print(m.matrix)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    screen.fill(black)
    drawMatrix()
    drawTimer()
    drawScore()
    pygame.display.flip()
