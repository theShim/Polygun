import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

# from scripts.world_loading.tiles import Tile
# from scripts.world_loading.nature.manager import Nature_Manager

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

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
                pos = (int(x + self.room_pos.x * LEVEL_SIZE), int(y + self.room_pos.y * LEVEL_SIZE))
                self.tilemap[pos] = Tile(self.game, pos, 0)

        for x in range(LEVEL_SIZE):
            pos = (x + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)
            self.tilemap[pos] = Tile(self.game, pos, 1)
            pos = (x + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE + LEVEL_SIZE - 1)
            self.tilemap[pos] = Tile(self.game, pos, 1)

        for y in range(LEVEL_SIZE):
            pos = (self.room_pos.x * LEVEL_SIZE, y + self.room_pos.y * LEVEL_SIZE)
            self.tilemap[pos] = Tile(self.game, pos, 1)
            pos = (self.room_pos.x * LEVEL_SIZE + LEVEL_SIZE - 1, y + self.room_pos.y * LEVEL_SIZE)
            self.tilemap[pos] = Tile(self.game, pos, 1)

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

    def auto_tile(self):
        for pos in self.tilemap:
            tile = self.tilemap[pos]
            if not tile.index: continue

            neighbours = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if abs(dx) == abs(dy): continue

                    to_check = (pos[0] + dx, pos[1] + dy)
                    if to_check in self.tilemap:
                        if self.tilemap[to_check].index:
                            neighbours.append((dx, dy))

                    else:
                        for room_x, room_y in self.room.conns:
                            to_check_room = (int(room_x), int(room_y))
                            to_check_tilemap = self.room.parent_level.rooms[to_check_room].tilemap.tilemap
                            if to_check in to_check_tilemap:
                                if to_check_tilemap[to_check].index:
                                    neighbours.append((dx, dy))
                                    break

            room_type = Tile.AUTO_TILE_MAP[tuple(sorted(neighbours))]
            tile.index = room_type

        #corners
        for pos in self.tilemap:
            tile = self.tilemap[pos]
            if tile.index: continue

            neighbours = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if abs(dx) == abs(dy): continue

                    to_check = (pos[0] + dx, pos[1] + dy)
                    if to_check in self.tilemap:
                        if (id_ := self.tilemap[to_check].index):
                            neighbours.append(id_)
            
            room_type = Tile.CORNER_PIXEL_MAP.get(tuple(sorted(filter(lambda x: x != 15 and not (17 <= x <= 29), neighbours))), tile.index)
            tile.index = room_type

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
                # else:
                #     print(self.room.conns)


class Tile(pygame.sprite.Sprite):

    AUTO_TILE_MAP = {
        #neighbours : room_type
        tuple(sorted([]))                                 : 1,
        tuple(sorted([(1, 0),]))                          : 2,
        tuple(sorted([(-1, 0), (1, 0)]))                  : 3,
        tuple(sorted([(-1, 0),]))                         : 4,
        tuple(sorted([(0, 1),]))                          : 5,
        tuple(sorted([(0, -1), (0, 1)]))                  : 6,
        tuple(sorted([(0, -1),]))                         : 7,
        tuple(sorted([(1, 0), (0, 1)]))                   : 8,
        tuple(sorted([(-1, 0), (0, 1), (1, 0)]))          : 9,
        tuple(sorted([(-1, 0), (0, 1)]))                  : 10,
        tuple(sorted([(0, -1), (1, 0)]))                  : 11,
        tuple(sorted([(-1, 0), (0, -1), (1, 0)]))         : 12,
        tuple(sorted([(-1, 0), (0, -1)]))                 : 13,
        tuple(sorted([(0, -1), (1, 0), (0, 1)]))          : 14,
        tuple(sorted([(-1, 0), (0, -1), (1, 0), (0, 1)])) : 15,
        tuple(sorted([(0, -1), (-1, 0), (0, 1)]))         : 16,
    }

    CORNER_PIXEL_MAP = {
        tuple(sorted([9, 14])) : 17,
        tuple(sorted([9, 16])) : 18,
        tuple(sorted([12, 16])) : 18,
        tuple(sorted([12, 14])) : 20,
        tuple(sorted([9, 9, 6])) : 21,
        tuple(sorted([9, 9, 5])) : 21,
        tuple(sorted([16, 16, 3])) : 22,
        tuple(sorted([16, 16, 4])) : 22,
        tuple(sorted([12, 12, 6])) : 23,
        tuple(sorted([12, 12, 7])) : 23,
        tuple(sorted([14, 14, 3])) : 24,
        tuple(sorted([14, 14, 2])) : 24,
        tuple(sorted([9, 16, 6, 3])) : 25,
        tuple(sorted([9, 16, 6, 4])) : 25,
        tuple(sorted([9, 16, 5, 3])) : 25,
        tuple(sorted([9, 16, 5, 4])) : 25,
        tuple(sorted([16, 12, 6, 3])) : 26,
        tuple(sorted([16, 12, 6, 4])) : 26,
        tuple(sorted([16, 12, 7, 3])) : 26,
        tuple(sorted([16, 12, 7, 4])) : 26,
        tuple(sorted([12, 14, 6, 3])) : 27,
        tuple(sorted([12, 14, 6, 2])) : 27,
        tuple(sorted([12, 14, 7, 3])) : 27,
        tuple(sorted([12, 14, 7, 2])) : 27,
        tuple(sorted([14, 9, 6, 3])) : 28,
        tuple(sorted([14, 9, 6, 2])) : 28,
        tuple(sorted([14, 9, 5, 3])) : 28,
        tuple(sorted([14, 9, 5, 2])) : 28,
        tuple(sorted([3, 3, 6, 6])) : 29,
        tuple(sorted([3, 3, 6, 5])) : 29,
        tuple(sorted([3, 3, 6, 7])) : 29,
        tuple(sorted([3, 3, 5, 7])) : 29,
        tuple(sorted([3, 2, 6, 6])) : 29,
        tuple(sorted([3, 2, 6, 5])) : 29,
        tuple(sorted([3, 2, 6, 7])) : 29,
        tuple(sorted([3, 2, 5, 7])) : 29,
        tuple(sorted([3, 4, 6, 6])) : 29,
        tuple(sorted([3, 4, 6, 5])) : 29,
        tuple(sorted([3, 4, 6, 7])) : 29,
        tuple(sorted([3, 4, 5, 7])) : 29,
        tuple(sorted([2, 4, 6, 6])) : 29,
        tuple(sorted([2, 4, 6, 5])) : 29,
        tuple(sorted([2, 4, 6, 7])) : 29,
        tuple(sorted([2, 4, 5, 7])) : 29,
    }
    
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        tilemap = pygame.transform.scale_by(pygame.image.load("assets/tiles/tilemap.png"), 4).convert_alpha()
        tilemap.set_colorkey((0, 0, 0))

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE)) #floor
        surf.fill((255, 34, 34))
        cls.SPRITES[0] = surf

        for y in range(3): #walls
            for x in range(10):
                id_ = y * 10 + x + 1
                if id_ == 30: break

                surf = tilemap.subsurface([x * TILE_SIZE, y * (2 * TILE_SIZE), TILE_SIZE, 2 * TILE_SIZE])
                cls.SPRITES[id_] = surf
    
    def __init__(self, game, pos: tuple, index: int):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.index = index
        self.pos = vec(pos) * TILE_SIZE
        self.rect = pygame.Rect(*self.pos, TILE_SIZE, TILE_SIZE)

    def update(self):
        if self.index:
            image = self.SPRITES[self.index]
            self.game.screen.blit(image, self.rect.topleft - self.game.offset)
    