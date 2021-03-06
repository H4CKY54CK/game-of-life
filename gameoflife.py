import os
import time
import numpy as np
from itertools import product
import pygame
from collections import deque


# 80 x 80 runs ok, but it really starts to slow down after that.
COLS = ROWS = 60
# ROWS = 120
# COLS = 120

# Used to be unicode values. Made it easy to switch it up on-the-fly.
FILLED = 1
EMPTY = 0

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
# Set color changer
d = deque((BLUE, RED, GREEN))
current_color = d[0]

# Grid cell size
WIDTH = 5
HEIGHT = 5
 
MARGIN = 1
 
class GameOfLife:

    def __init__(self):
        self.grid = np.zeros(ROWS*COLS, dtype=bool).reshape(COLS,ROWS)

    # Counts neighbors. Now that I've explained what it does, this seems unnecessarily complicated.
    def check(self, a, b):
        # x = [a-1,a,a+1]
        # y = [b-1,b,b+1]

        # for e, i in enumerate(x):
        #     if i < 0:
        #         x[e] = 0
        #     elif i == len(self.grid[:,0]):
        #         x[e] = len(self.grid[:,0])-1

        # for e, i in enumerate(y):
        #     if i < 0:
        #         y[e] = 0
        #     elif i == len(self.grid[0,:]):
        #         y[e] = len(self.grid[0,:])-1

        a -= 1
        b -= 1
        if a < 0 and b < 0:
            a = 0
            b = 0
            return np.count_nonzero(self.grid[a:a+2,b:b+2])
        elif a < 0:
            a = 0
            return np.count_nonzero(self.grid[a:a+2, b:b+3])
        elif b < 0:
            return np.count_nonzero(self.grid[a:a+3, b:b+2])
        else:
            return np.count_nonzero(self.grid[a:a+3, b:b+3])

    # Reset all the values of the grid.
    def clear(self):
        for x,y in product(range(ROWS), range(COLS)):
            self.grid[x,y] = 0


    def unb(self, x, y):
        unbounded = [[1, 1, 1, 0, 1],
                     [1, 0, 0, 0, 0],
                     [0, 0, 0, 1, 1],
                     [0, 1, 1, 0, 1],
                     [1, 0, 1, 0, 1]]
        unbounded = np.array(unbounded)
        for a, b in product(range(5),range(5)):
            if unbounded[a,b] == 1:
                self.grid[x+a,y+b] = 1


    # Create a glider.
    def glider(self, x, y, direction=None):
        if direction is None:
            direction = 'right'
        g = np.array([EMPTY for i in range(9)]).reshape(3,3)
        g[0,1] = FILLED
        if direction == 'right':
            g[1,2] = FILLED
        if direction == 'left':
            g[1,0] = FILLED
        g[2,0] = FILLED
        g[2,1] = FILLED
        g[2,2] = FILLED
        # self.grid[x:x+3,y:y+3] = g
        for a,b in product(range(3),range(3)):
            if g[a,b] == 1:
                self.grid[x+a, y+b] = 1

    # Create a spaceship.
    def spaceship(self, x, y):
        g = np.array([EMPTY for i in range(20)]).reshape(4,5)
        g[0,0] = FILLED
        g[0,3] = FILLED
        g[1,4] = FILLED
        g[2,0] = FILLED
        g[2,4] = FILLED
        g[3,1:5] = FILLED
        # self.grid[x:x+4, y:y+5] = g
        for a,b in product(range(4),range(5)):
            if g[a,b] == 1:
                self.grid[x+a, y+b] = 1

    # Create a glider gun.
    def glider_gun(self, x, y):
        g = np.array([int(i) for i in '000000000000000000000000100000000000000000000000000000000010100000000000000000000000110000001100000000000011000000000001000100001100000000000011110000000010000010001100000000000000110000000010001011000010100000000000000000000010000010000000100000000000000000000001000100000000000000000000000000000000110000000000000000000000']).reshape(9,36)
        # self.grid[x:x+9, y:y+36] = g
        for a,b in product(range(9),range(36)):
            if g[a,b] == 1:
                self.grid[x+a, y+b] = 1

    # Update the grid, one step.
    def step(self):
        new = self.grid.copy()
        for x,y in product(range(ROWS), range(COLS)):
            cnt = self.check(x,y)
            if self.grid[x,y] == FILLED:
                if cnt not in set((3,4)):
                    new[x,y] = EMPTY
            elif self.grid[x,y] == EMPTY:
                if cnt == 3:
                    new[x,y] = FILLED
        self.grid = new

        # Haven't figured out which is faster. Copying the grid, or using a list.

        # kill = []
        # revive = []
        # for i in kill:
        #     self.grid[i[0],i[1]] = EMPTY
        # for i in revive:
        #     self.grid[i[0],i[1]] = FILLED




grid = GameOfLife()
pygame.init()
 
screen = pygame.display.set_mode((ROWS*6,COLS*6))
 
pygame.display.set_caption("Game of Life")
 
# Loop until the user clicks the close button.
done = False
 
# Doesn't seem like we need it?
clock = pygame.time.Clock()
# For drawing
speed = 0
cspeed = 15
# Other pre-defaults
paused = True
leftDragFlag = False
rightDragFlag = False

while not done:
    pos = pygame.mouse.get_pos()
    column = pos[0] // (WIDTH + MARGIN)
    row = pos[1] // (HEIGHT + MARGIN)
    if paused is None:
        paused = True
    for event in pygame.event.get():
        # User clicks 'X'
        if event.type == pygame.QUIT:
            # Flag that says whether to close or not.
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                leftDragFlag = True
            elif event.button == 3:
                rightDragFlag = True
        elif event.type == pygame.MOUSEBUTTONUP:
            leftDragFlag = False
            rightDragFlag = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                speed += 5
                if speed > 30:
                    speed = 30
            if event.key == pygame.K_q:
                speed -= 5
                if speed < 10:
                    speed = 10
            if event.key == pygame.K_p:
                paused = True if not paused else False
                speed = 15
            if event.key == pygame.K_r:
                speed = 0
                grid.clear()
                paused = None
            if event.key == pygame.K_b:
                try:
                    grid.unb(row,column)
                except:
                    pass
            if event.key == pygame.K_g:
                try:
                    grid.glider(row, column)
                except:
                    pass
            if event.key == pygame.K_s:
                try:
                    grid.spaceship(row, column)
                except:
                    pass
            if event.key == pygame.K_u:
                try:
                    grid.glider_gun(row, column)
                except:
                    pass
            if event.key == pygame.K_c:
                d.rotate()
                current_color = d[0]

    if leftDragFlag:
        grid.grid[row][column] = 1

    if rightDragFlag:
        grid.grid[row][column] = 0

    screen.fill(BLACK)

    for row in range(len(grid.grid[0])):
        for column in range(len(grid.grid[0])):
            color = WHITE
            if grid.grid[row][column] == 1:
                color = current_color
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])

    clock.tick(speed)

    if not paused:
        grid.step()
    
    pygame.display.flip()
pygame.quit()


