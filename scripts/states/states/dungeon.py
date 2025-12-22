import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.entities.enemy import Enemy
from scripts.states.state_loader import State
from scripts.world_loading.dungeons import DungeonLevel, Room
from scripts.world_loading.tilemap import Tile

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################

class Dungeon(State):
    LEVEL_NUM = 1

    def __init__(self, game, prev=None):
        super().__init__(game, "dungeon", prev)
        # # self.game.player.rect.center = [100, -50]

        self.levels: list[DungeonLevel] = [DungeonLevel(self.game, self) for _ in range(self.LEVEL_NUM)]
        self.current_level_index = 0

        self.last_available_room = None

    def get_current_room(self, pos = None, offset: vec = vec()) -> Room:
        level: DungeonLevel = self.levels[self.current_level_index]
        
        if pos == None:
            pos = self.game.player.pos
        else:
            pos = vec(pos)

        room_x = pos.x // (TILE_SIZE * LEVEL_SIZE) + offset[0]
        room_y = pos.y // (TILE_SIZE * LEVEL_SIZE) + offset[1]
        
        to_check = (int(room_x), int(room_y))
        if to_check in level.rooms:
            self.last_available_room = level.rooms[to_check]
        room = self.last_available_room
        
        return room

    def update(self):
        self.game.calculate_offset() #camera
        self.get_current_room().update()
        self.render()

    def render(self):
        pygame.draw.circle(self.screen, (255, 0, 0, 120), (WIDTH * 0.7, HEIGHT/2) - self.game.offset, 50)

        tiles = []
        for room in self.levels[self.current_level_index].rooms.values():
            tiles += list(room.tilemap.on_screen_tiles(self.game.offset, buffer=[1, 1]))

        sprites = []
        for spr in self.game.all_sprites:
            if isinstance(spr, Enemy):
                if spr in self.get_current_room().enemies_to_kill:
                    sprites += [spr]
            else:
                sprites += [spr]

        for spr in sorted(sprites + tiles, key=lambda s: s.rect.bottom if isinstance(s, Tile) else s.pos.y):
            spr.update()