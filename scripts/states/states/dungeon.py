import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.entities.enemy import Enemy
from scripts.states.state_loader import State
from scripts.world_loading.dungeons import DungeonLevel, Room
from scripts.world_loading.tilemap import Tile
from scripts.gui.health_bar import HealthBar
from scripts.gui.crosshair import CrossHair
from scripts.gui.energy_bar import EnergyBar
from scripts.gui.currency import CurrencyGUI

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

        self.start = True

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
        if self.start:
            HealthBar(self.game, [self.game.gui_elements])
            CrossHair(self.game, [self.game.gui_elements])
            EnergyBar(self.game, [self.game.gui_elements])
            CurrencyGUI(self.game, [self.game.gui_elements])
            
            self.game.music_player.play("xqc_dungeon", pool="music", loop=True)
            self.start = False
            
        self.game.calculate_offset() #camera
        self.get_current_room().update()
        self.render()

    def render(self):
        pygame.draw.circle(self.screen, (255, 0, 0, 120), (WIDTH * 0.7, HEIGHT/2) - self.game.offset, 50)

        tiles = []
        lava_tiles = []
        for room in self.levels[self.current_level_index].rooms.values():
            tiles += list(room.tilemap.on_screen_tiles(self.game.offset, buffer=[1, 1]))
            for lava_region in room.tilemap.lava_regions:
                lava_region.player_collide()
                lava_tiles += lava_region.tiles

        sprites = []
        for spr in self.game.all_sprites:
            if isinstance(spr, Enemy):
                if spr in self.get_current_room().enemies_to_kill:
                    sprites += [spr]
            else:
                if (self.game.player.pos - spr.pos).magnitude() < 1300:
                    sprites += [spr]

        for spr in lava_tiles:
            spr.update()

        for spr in sorted(sprites + tiles, key=lambda s: s.rect.bottom if isinstance(s, Tile) else s.pos.y):
            spr.update()

        self.game.gui_elements.update()