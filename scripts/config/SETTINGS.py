import pygame

DEBUG = False

SIZE = WIDTH, HEIGHT = (640, 400)
WINDOW_TITLE = "WINDOW TITLE"
FPS = 60
CAMERA_FOLLOW_SPEED = 12
TILE_SIZE = 32

Z_LAYERS = {
    "player" : 5
}

#   PHYSICS
FRIC = 0.9
GRAV = 0.4

CONTROLS = {
    "up"        : pygame.K_w,
    "down"      : pygame.K_s,
    "left"      : pygame.K_a,
    "right"     : pygame.K_d,
    "jump"      : pygame.K_SPACE,
}