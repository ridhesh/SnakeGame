import random
import pygame
import sys
import os
from pygame.locals import *

# Game Settings
WINDOWWIDTH = 1280   # Canvas width
WINDOWHEIGHT = 720    # Canvas height
CELLSIZE = 20  # Size of each pixel in the grid (snake and apple)
FPS = 10  # Frames per second (game speed)
GRACE_PERIOD = 30  # Frames to wait before game over after collision

# Direction Constants
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
ORANGE = (255, 140, 0)
GRAY = (40, 40, 40)
BLUE = (0, 0, 255)  # Power-up apple color

# Additional Color Definitions
BGCOLOR = BLACK  # Background color
GRIDCOLOR = GRAY  # Grid line color
WORMCOLOR = GREEN  # Snake color
APPLECOLOR = RED  # Regular apple color
OBSTACLECOLOR = ORANGE  # Obstacle color
POWERUPCOLOR = BLUE  # Power-up color

# Grid dimensions
CELLWIDTH = WINDOWWIDTH // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# Snake head index
HEAD = 0

# High score file
HIGH_SCORE_FILE = 'high_score.txt'

def load_high_score():
    """ Load high score from a file. """
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def save_high_score(score):
    """ Save high score to a file. """
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write(str(score))

def main():
    """ Main function to run the game. """
    global CLOCK, SCREEN, FONT, high_score

    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))  # Windowed mode
    FONT = pygame.font.Font('freesansbold.ttf', 30)
    pygame.display.set_caption('Snake Game')

    high_score = load_high_score()
    showStartScreen()  # Show start screen
    while True:
        score = runGame()  # Capture the score returned from runGame()
        showGameOverScreen(score)  # Pass the score to showGameOverScreen

def runGame():
    """ The main game loop. """
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)

    global wormCoords
    wormCoords = [{'x': startx, 'y': starty}]
    direction = RIGHT
    apples = [getRandomLocation() for _ in range(3)]  # Spawn 3 regular apples
    powerups = []  # Initially empty list for power-ups
    obstacles = [getRandomLocation() for _ in range(5)]  # Spawn 5 obstacles

    currentSpeed = FPS
    isPaused = False
    level = 1
    score = 0
    snake_growth = 0  # Variable to track snake growth
    grace_frame_counter = 0  # Counter for grace period after collisions

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_p:  # Pause game
                    isPaused = not isPaused
                elif event.key == K_f:  # Toggle fullscreen
                    toggle_fullscreen()

        if isPaused:
            drawPauseScreen()
            pygame.display.update()
            continue

        # Move the snake
        newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y']}
        if direction == UP:
            newHead['y'] -= 1
        elif direction == DOWN:
            newHead['y'] += 1
        elif direction == RIGHT:
            newHead['x'] += 1
        elif direction == LEFT:
            newHead['x'] -= 1
        
        # Check for collisions with boundaries
        if (newHead['x'] < 0 or newHead['x'] >= CELLWIDTH or
                newHead['y'] < 0 or newHead['y'] >= CELLHEIGHT):
            grace_frame_counter += 1  # Increment grace frame counter
            if grace_frame_counter >= GRACE_PERIOD:
                return score  # Game over

        # Check collision with self
        if newHead in wormCoords:
            grace_frame_counter += 1  # Increment grace frame counter
            if grace_frame_counter >= GRACE_PERIOD:
                return score  # Collision with self, game over

        # Check for collisions with apples
        for apple in apples[:]:
            if newHead['x'] == apple['x'] and newHead['y'] == apple['y']:
                apples.remove(apple)  # Remove the eaten apple
                score += 10  # Increase score for eating an apple
                snake_growth += 1  # Increment growth counter
                apples.append(getRandomLocation())  # Spawn a new apple
                grace_frame_counter = 0  # Reset grace period on eat

        # Update snake position
        wormCoords.insert(HEAD, newHead)

        # Now handle the snake growth
        if snake_growth > 0:
            snake_growth -= 1  # Snake grows if there was a growth request
        else:
            del wormCoords[-1]  # Remove the last segment of the snake if not growing

        # Collision with obstacles
        for obstacle in obstacles:
            if newHead['x'] == obstacle['x'] and newHead['y'] == obstacle['y']:
                grace_frame_counter += 1  # Increment grace frame counter
                if grace_frame_counter >= GRACE_PERIOD:
                    return score  # Game over if collided with an obstacle

        # Drawing the screen
        SCREEN.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApples(apples)  # Draw all apples
        drawObstacles(obstacles)  # Draw all obstacles
        drawScore(score)
        drawLevel(level)
        drawHighScore(high_score)  # Draw high score
        pygame.display.update()
        CLOCK.tick(currentSpeed)

def showStartScreen():
    """ Displays the start screen. """
    titlefont = pygame.font.Font('freesansbold.ttf', 100)
    titleText = titlefont.render('SNAKE FUN', True, DARKGREEN)

    instructions = FONT.render("Use arrow keys to move. Press P to pause.", True, WHITE)

    # Display start screen until a key is pressed
    while True:
        SCREEN.fill(BGCOLOR)
        titleTextRect = titleText.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 4))
        SCREEN.blit(titleText, titleTextRect)
        SCREEN.blit(instructions, (WINDOWWIDTH / 2 - instructions.get_width() / 2, (WINDOWHEIGHT / 2)))
        drawPressKeyMsg()  # Prompt to press a key

        if checkForKeyPress():
            pygame.event.get()  # Clear event queue
            return  # Start the game immediately

        pygame.display.update()
        CLOCK.tick(FPS)

def drawPressKeyMsg():
    """ Draws the message to press any key to start. """
    pressKeyFont = pygame.font.Font('freesansbold.ttf', 30)
    pressKeyText = pressKeyFont.render('Press any key to start...', True, WHITE)
    pressKeyRect = pressKeyText.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT - 50))
    SCREEN.blit(pressKeyText, pressKeyRect)

def checkForKeyPress():
    """ Checks for any key press. """
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # Allow exiting the game with escape
                terminate()
            return True
    return False

def showGameOverScreen(score):
    """ Displays the game over screen. """
    gameOverFont = pygame.font.Font('freesansbold.ttf', 100)
    gameOverText = gameOverFont.render('Game Over', True, WHITE)
    gameOverRect = gameOverText.get_rect(midtop=(WINDOWWIDTH / 2, 30))
    totalscoreFont = pygame.font.Font('freesansbold.ttf', 40)
    totalscoreText = totalscoreFont.render('Total Score: %s' % (score), True, WHITE)
    totalscoreRect = totalscoreText.get_rect(midtop=(WINDOWWIDTH / 2, 150))

    global high_score
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    highScoreText = totalscoreFont.render('High Score: %s' % (high_score), True, WHITE)
    highScoreRect = highScoreText.get_rect(midtop=(WINDOWWIDTH / 2, 200))

    SCREEN.fill(BGCOLOR)
    SCREEN.blit(gameOverText, gameOverRect)
    SCREEN.blit(totalscoreText, totalscoreRect)
    SCREEN.blit(highScoreText, highScoreRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(1000)
    checkForKeyPress()

    while True:
        if checkForKeyPress():
            pygame.event.get()
            return

def terminate():
    """ Terminates the game. """
    pygame.quit()
    sys.exit()

def drawGrid():
    """ Draws the grid on the screen. """
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(SCREEN, GRIDCOLOR, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(SCREEN, GRIDCOLOR, (0, y), (WINDOWWIDTH, y))

def drawWorm(wormCoords):
    """ Draws the snake on the screen. """
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(SCREEN, WORMCOLOR, wormSegmentRect)

def drawApples(apples):
    """ Draws apples on the screen. """
    for apple in apples:
        x = apple['x'] * CELLSIZE
        y = apple['y'] * CELLSIZE
        appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(SCREEN, APPLECOLOR, appleRect)

def drawObstacles(obstacles):
    """ Draws obstacles on the screen. """
    for obstacle in obstacles:
        x = obstacle['x'] * CELLSIZE
        y = obstacle['y'] * CELLSIZE
        obstacleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(SCREEN, OBSTACLECOLOR, obstacleRect)

def drawScore(score):
    """ Draws the score on the screen. """
    scoreText = FONT.render('Score: %s' % (score), True, WHITE)
    SCREEN.blit(scoreText, (10, 10))

def drawLevel(level):
    """ Draws the level on the screen. """
    levelText = FONT.render('Level: %s' % (level), True, WHITE)
    SCREEN.blit(levelText, (WINDOWWIDTH - 150, 10))

def drawHighScore(high_score):
    """ Draws the high score on the screen. """
    highScoreText = FONT.render('High Score: %s' % (high_score), True, WHITE)
    SCREEN.blit(highScoreText, (10, 40))

def drawPauseScreen():
    """ Draws the pause screen. """
    pauseFont = pygame.font.Font('freesansbold.ttf', 50)
    pauseText = pauseFont.render('Game Paused', True, WHITE)
    pauseRect = pauseText.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 2))
    SCREEN.blit(pauseText, pauseRect)

def toggle_fullscreen():
    """ Toggles between fullscreen and windowed mode. """
    global SCREEN
    if SCREEN.get_flags() & pygame.FULLSCREEN:
        SCREEN = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))  # Windowed mode
    else:
        SCREEN = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN)  # Fullscreen mode

def getRandomLocation():
    """ Gets a random location for apples and obstacles. """
    while True:
        loc = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
        # Check if the location is occupied by the worm body or existing apples and obstacles
        if loc not in wormCoords:
            return loc

if __name__ == '__main__':
    main()
