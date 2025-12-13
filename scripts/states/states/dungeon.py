import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.states.state_loader import State
from scripts.world_loading.dungeons import DungeonLevel
from scripts.world_loading.tilemap import Tile

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS

    ##############################################################################################

class Dungeon(State):
    LEVEL_NUM = 1

    def __init__(self, game, prev=None):
        super().__init__(game, "dungeon", prev)
        # self.tilemap.load("tiled/tmx/debug.tmx")
        # # self.game.player.rect.center = [100, -50]

        self.levels: list[DungeonLevel] = [DungeonLevel(self.game) for _ in range(self.LEVEL_NUM)]
        self.current_level_index = 0

    def update(self):
        self.game.calculate_offset() #camera
        self.render()

    def render(self):
        # self.tilemap.render()
        pygame.draw.circle(self.screen, (255, 0, 0, 120), (WIDTH * 0.7, HEIGHT/2) - self.game.offset, 50)

        tiles = []
        for room in self.levels[self.current_level_index].rooms.values():
            tiles += list(room.tilemap.on_screen_tiles(self.game.offset, buffer=[1, 1]))
        for spr in sorted(self.game.all_sprites.sprites() + tiles, key=lambda s: s.rect.bottom if isinstance(s, Tile) else s.pos.y):
            spr.update()