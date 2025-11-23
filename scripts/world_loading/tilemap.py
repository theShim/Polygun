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

        self.load()

    def load(self):
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                pos = (int(x + self.room_pos.x * LEVEL_SIZE) * TILE_SIZE, int(y + self.room_pos.y * LEVEL_SIZE) * TILE_SIZE)
                self.tilemap[pos] = Tile(self.game, pos, 0)

        for x in range(LEVEL_SIZE):
            self.tilemap[(x + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)] = Tile(self.game, (x + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE), 1)
            self.tilemap[(x + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE + LEVEL_SIZE - 1)] = Tile(self.game, (x + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE + LEVEL_SIZE - 1), 1)
        for y in range(LEVEL_SIZE):
            self.tilemap[(self.room_pos.x * LEVEL_SIZE, y + self.room_pos.y * LEVEL_SIZE)] = Tile(self.game, (self.room_pos.x * LEVEL_SIZE, y + self.room_pos.y * LEVEL_SIZE), 1)
            self.tilemap[(self.room_pos.x * LEVEL_SIZE + LEVEL_SIZE - 1, y + self.room_pos.y * LEVEL_SIZE)] = Tile(self.game, (self.room_pos.x * LEVEL_SIZE + LEVEL_SIZE - 1, y + self.room_pos.y * LEVEL_SIZE), 1)

        if (self.room_pos.x + 1, self.room_pos.y) in self.room.conns:
            del self.tilemap[(LEVEL_SIZE - 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + self.room_pos.y * LEVEL_SIZE)]
            del self.tilemap[(LEVEL_SIZE - 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + 1 + self.room_pos.y * LEVEL_SIZE)]
        if (self.room_pos.x - 1, self.room_pos.y) in self.room.conns:
            del self.tilemap[(self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + self.room_pos.y * LEVEL_SIZE)]
            del self.tilemap[(self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + 1 + self.room_pos.y * LEVEL_SIZE)]
        if (self.room_pos.x, self.room_pos.y + 1) in self.room.conns:
            del self.tilemap[(LEVEL_SIZE//2 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE - 1 + self.room_pos.y * LEVEL_SIZE)]
            del self.tilemap[(LEVEL_SIZE//2 + 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE - 1 + self.room_pos.y * LEVEL_SIZE)]
        if (self.room_pos.x, self.room_pos.y - 1) in self.room.conns:
            del self.tilemap[(LEVEL_SIZE//2 + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)]
            del self.tilemap[(LEVEL_SIZE//2 + 1 + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)]

    def on_screen_tiles(self, offset, buffer=[0, 0]):
        start_x = int(offset[0] // (self.tile_size) - buffer[0])
        start_y = int(offset[1] // (self.tile_size) - buffer[1])
        # if start_x != self.last_start.x and start_y != self.last_start.y:

        end_x = int((offset[0] + WIDTH) // self.tile_size  + buffer[0]) + 1
        end_y = int((offset[1] + HEIGHT) // self.tile_size + buffer[1]) + 1

        #off-screen culling
        if not (self.room_pos.x - 1 < ((start_x + end_x) / 2) / LEVEL_SIZE < self.room_pos.x + 2): return
        if not (self.room_pos.y - 1 < ((start_y + end_y) / 2) / LEVEL_SIZE < self.room_pos.y + 2): return

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                loc = (x, y)
                if loc in self.tilemap:
                    tile: Tile = self.tilemap[loc]
                    yield tile


class Tile(pygame.sprite.Sprite):
    
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE)) #floor
        surf.fill((34, 34, 34))
        cls.SPRITES[0] = surf

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE * 2)) #wall
        surf.fill((56, 56, 67))
        surf.fill((20, 20, 24), [0, TILE_SIZE, TILE_SIZE, TILE_SIZE])
        cls.SPRITES[1] = surf
    
    def __init__(self, game, pos: tuple, index: int):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.index = index
        self.pos = vec(pos) * TILE_SIZE
        self.rect = pygame.Rect(*self.pos, TILE_SIZE, TILE_SIZE)

    def update(self):
        image = self.SPRITES[self.index]
        self.game.screen.blit(image, self.rect.topleft - self.game.offset)
    