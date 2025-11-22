import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
from scripts.states.state_loader import State

    ##############################################################################################

class Debug_Stage(State):
    def __init__(self, game, prev=None):
        super().__init__(game, "debug", prev)
        # self.tilemap.load("tiled/tmx/debug.tmx")
        # # self.game.player.rect.center = [100, -50]