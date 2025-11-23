import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.states.state_loader import State
from scripts.world_loading.dungeons import DungeonLevel

    ##############################################################################################

class Dungeon(State):
    LEVEL_NUM = 1

    def __init__(self, game, prev=None):
        super().__init__(game, "dungeon", prev)
        # self.tilemap.load("tiled/tmx/debug.tmx")
        # # self.game.player.rect.center = [100, -50]

        self.levels = [DungeonLevel(self.game) for _ in range(self.LEVEL_NUM)]