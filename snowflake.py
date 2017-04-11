"""
Snowing animation using pygame.
With the help of: http://programarcadegames.com/index.php?lang=en Chapter 8. Introduction to Animation.
By niquefaDiego
"""

import pygame, random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
size = (500, 500)  # screen dimensions
screen = pygame.display.set_mode(size)

nSnowflakes = 200  # number of snowflakes
snowflakes = []  # list of snowflakes positions
snowflakeSpeed = []  # list of the speeds of each snowflake

# fill snowflakes with nSnowflakes random positions
for i in range(nSnowflakes):
    # generate snowflake with random position and speed
    posX = random.randrange(size[0])
    posY = random.randrange(size[1])
    speed = 2 + random.randrange(3)  # 1 <= speed <= 3

    # add to snowflakes lists
    snowflakes.append([posX, posY])
    snowflakeSpeed.append(speed)

# program speed controller
clock = pygame.time.Clock()

endProgram = False
while endProgram == False:

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            endProgram = True

    # draw screen
    screen.fill(BLACK)
    for pos in snowflakes:
        pygame.draw.line(screen, WHITE, pos, (pos[0], pos[1]+10), 2)  # draw snowflake
    pygame.display.flip()

    # update snowflakes positions
    for i in range(nSnowflakes):
        pos = snowflakes[i]
        pos[1] += snowflakeSpeed[i]

        # if snowflake is out of screen
        if (pos[1] >= 4 + size[1]):
            # generate new random position slightly above the screen
            pos[0] = random.randrange(size[0])
            pos[1] = random.randrange(-10, -5)

    # 15 frames per seconds
    clock.tick(15)

pygame.quit()