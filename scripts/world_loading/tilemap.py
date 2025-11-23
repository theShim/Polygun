import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

# from scripts.world_loading.tiles import Tile
# from scripts.world_loading.nature.manager import Nature_Manager

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, Z_LAYERS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################
    
class Tilemap:
    def __init__(self, game, parent_room):
        self.game = game

        self.tilemap = {}
        self.tilemap_layers = []
        self.tile_size = TILE_SIZE

        self.room = parent_room
        self.room_pos = vec(parent_room.pos)

        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                pos = ((x + self.room_pos.x) * TILE_SIZE, (y + self.room_pos.y) * TILE_SIZE)
                self.tilemap[pos] = Tile(self.game, pos, 0)

        for x in range(LEVEL_SIZE):
            self.tilemap[(x, 0)] = 1
            self.tilemap[(x, LEVEL_SIZE - 1)] = 1
        for y in range(LEVEL_SIZE):
            self.tilemap[(0, y)] = 1
            self.tilemap[(LEVEL_SIZE - 1, y)] = 1


class Tile(pygame.sprite.Sprite):
    
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE)) #floor
        surf.fill((34, 34, 34))
        cls.SPRITES[0] = surf

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE)) #wall
        surf.fill((56, 56, 67))
        cls.SPRITES[1] = surf
    
    def __init__(self, game, pos: tuple, index: int):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.index = index
        self.pos = vec(pos)
        self.rect = pygame.Rect(*(self.pos * TILE_SIZE), TILE_SIZE, TILE_SIZE)

    def update(self):
        image = self.SPRITES[self.index]
        self.game.screen.blit(image, self.rect.topleft - self.game.offset)
    