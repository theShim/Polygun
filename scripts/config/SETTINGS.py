import pygame

DEBUG = not False

SIZE = WIDTH, HEIGHT = (960, 540) #window size
WINDOW_TITLE = "WINDOW TITLE"
FPS = 60
CAMERA_FOLLOW_SPEED = 12

TILE_SIZE = 64 #pixel width and height of a tile
LEVEL_SIZE = 20 #how many tiles wide each room is
LEVEL_BUFFER = 6 #spacing between each room (also == length of corridoor)

#   PHYSICS
FRIC = 0.9
GRAV = 25

#will be replaced by a proper controls manager in later iterations
CONTROLS = {
    "up"        : pygame.K_w,
    "down"      : pygame.K_s,
    "left"      : pygame.K_a,
    "right"     : pygame.K_d,
    "jump"      : pygame.K_SPACE,
}

