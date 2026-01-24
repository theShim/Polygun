import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

# from scripts.world_loading.tiles import Tile
# from scripts.world_loading.nature.manager import Nature_Manager

from scripts.world_loading.rooms import ROOMS

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
        room = random.choices(ROOMS, [10, 1, 100], k=1)[0]
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                pos = (int(x + self.room_pos.x * LEVEL_SIZE), int(y + self.room_pos.y * LEVEL_SIZE))
                self.tilemap[pos] = Tile(self.game, pos, room[y][x])

        self.remove_corridoors()

    def remove_corridoors(self):
        if (self.room_pos.x + 1, self.room_pos.y) in self.room.conns:
            self.tilemap[(LEVEL_SIZE - 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + self.room_pos.y * LEVEL_SIZE)].index = 0
            self.tilemap[(LEVEL_SIZE - 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + 1 + self.room_pos.y * LEVEL_SIZE)].index = 0
        if (self.room_pos.x - 1, self.room_pos.y) in self.room.conns:
            self.tilemap[(self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + self.room_pos.y * LEVEL_SIZE)].index = 0
            self.tilemap[(self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + 1 + self.room_pos.y * LEVEL_SIZE)].index = 0
        if (self.room_pos.x, self.room_pos.y + 1) in self.room.conns:
            self.tilemap[(LEVEL_SIZE//2 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE - 1 + self.room_pos.y * LEVEL_SIZE)].index = 0
            self.tilemap[(LEVEL_SIZE//2 + 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE - 1 + self.room_pos.y * LEVEL_SIZE)].index = 0
        if (self.room_pos.x, self.room_pos.y - 1) in self.room.conns:
            self.tilemap[(LEVEL_SIZE//2 + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)].index = 0
            self.tilemap[(LEVEL_SIZE//2 + 1 + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)].index = 0

    def fill_corridoors(self):
        if (self.room_pos.x + 1, self.room_pos.y) in self.room.conns:
            self.tilemap[(LEVEL_SIZE - 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + self.room_pos.y * LEVEL_SIZE)].index = 1
            self.tilemap[(LEVEL_SIZE - 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + 1 + self.room_pos.y * LEVEL_SIZE)].index = 1
        if (self.room_pos.x - 1, self.room_pos.y) in self.room.conns:
            self.tilemap[(self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + self.room_pos.y * LEVEL_SIZE)].index = 1
            self.tilemap[(self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE//2 + 1 + self.room_pos.y * LEVEL_SIZE)].index = 1
        if (self.room_pos.x, self.room_pos.y + 1) in self.room.conns:
            self.tilemap[(LEVEL_SIZE//2 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE - 1 + self.room_pos.y * LEVEL_SIZE)].index = 1
            self.tilemap[(LEVEL_SIZE//2 + 1 + self.room_pos.x * LEVEL_SIZE, LEVEL_SIZE - 1 + self.room_pos.y * LEVEL_SIZE)].index = 1
        if (self.room_pos.x, self.room_pos.y - 1) in self.room.conns:
            self.tilemap[(LEVEL_SIZE//2 + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)].index = 1
            self.tilemap[(LEVEL_SIZE//2 + 1 + self.room_pos.x * LEVEL_SIZE, self.room_pos.y * LEVEL_SIZE)].index = 1

    def auto_tile(self):
        for pos in self.tilemap:
            tile = self.tilemap[pos]
            if not tile.index: continue

            if tile.index == 100:
                to_check = (pos[0], pos[1] - 1)
                top_edge = not (self.tilemap[to_check].index == 100)
                to_check = (pos[0], pos[1] + 1)
                bottom_edge = not (self.tilemap[to_check].index == 100)
                self.tilemap[pos] = Lava_Tile(tile.game, tile.pos / TILE_SIZE, top_edge, bottom_edge)
                continue

            neighbours = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if abs(dx) == abs(dy): continue

                    to_check = (pos[0] + dx, pos[1] + dy)
                    if to_check in self.tilemap:
                        if self.tilemap[to_check].index:
                            neighbours.append((dx, dy))

                    else:
                        for ddx in range(-1, 2):
                            for ddy in range(-1, 2):
                                if abs(ddx) == abs(ddy): continue

                                room_x = self.room_pos.x + ddx
                                room_y = self.room_pos.y + ddy
                        # for room_x, room_y in self.room.conns:
                                to_check_room = (int(room_x), int(room_y))
                                if to_check_room in self.room.parent_level.rooms:
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
            if not tile.index: continue
            if tile.index == 100: continue

            neighbours = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if abs(dx) == abs(dy): continue

                    to_check = (pos[0] + dx, pos[1] + dy)
                    if to_check in self.tilemap:
                        if (id_ := self.tilemap[to_check].index):
                            neighbours.append(id_)
                    else:
                        for room_x, room_y in self.room.conns:
                            to_check_room = (int(room_x), int(room_y))
                            to_check_tilemap = self.room.parent_level.rooms[to_check_room].tilemap.tilemap
                            if to_check in to_check_tilemap:
                                if (id_ := to_check_tilemap[to_check].index):
                                    neighbours.append(id_)
                                    break

            room_type = Tile.CORNER_PIXEL_MAP.get(tile.index, dict()).get(tuple(sorted(neighbours)), tile.index)
            # if not room_type:
            #     if tile.index != 16:
            #         room_type = tile.index
            #     else:
            #         print(room_type, neighbours, )
            # else:
            #     if tile.index == 16:
            #         print(neighbours)
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

    def collideables(self, offset, buffer=[0, 0]):
        for tile in self.on_screen_tiles(offset, buffer):
            if 0 < tile.index < 100:
                yield tile


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

    CORNER_PIXEL_MAP = { #more like ohnepixel
        13 : {
            tuple(sorted([3, 6])) : 38
        },
        11 : {
            tuple(sorted([3, 6])) : 39
        },
        8 : {
            tuple(sorted([3, 6])) : 40
        },
        10 : {
            tuple(sorted([3, 6])) : 41
        },
        9 : {
            tuple(sorted([3, 9, 14])) : 37
        },
        16 : {
            tuple(sorted([6, 9, 16])) : 30,
            tuple(sorted([6, 12, 16])) : 33,
            tuple(sorted([6, 9, 33])) : 30,
            tuple(sorted([6, 12, 30])) : 33,
        }
    }
    
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        tilemap = pygame.transform.scale_by(pygame.image.load("assets/tiles/tilemap.png"), 4).convert_alpha()
        tilemap.set_colorkey((0, 0, 0))

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA) #floor
        surf.fill((255, 34, 34))
        cls.SPRITES[0] = surf

        for y in range(5): #walls
            for x in range(10):
                id_ = y * 10 + x + 1
                if id_ == 46: break

                surf = tilemap.subsurface([x * TILE_SIZE, y * (2 * TILE_SIZE), TILE_SIZE, 2 * TILE_SIZE]).convert_alpha()
                cls.SPRITES[id_] = surf

        cls.LIGHT_TINTS = {}
        for id_ in cls.SPRITES.keys():
            surf = cls.SPRITES[id_].copy().convert_alpha()
            for dy in range(surf.height):
                for dx in range(surf.width):
                    if surf.get_at((dx, dy)) in [(59, 57, 65), (21, 20, 23)]:
                        surf.set_at((dx, dy), (0, 0, 0, 0))
            cls.LIGHT_TINTS[id_] = surf
    
    def __init__(self, game, pos: tuple, index: int):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.index = index
        self.pos = vec(pos) * TILE_SIZE
        self.rect = pygame.Rect(*self.pos, TILE_SIZE, TILE_SIZE)
        self.hitbox = pygame.Rect(*self.pos, TILE_SIZE, TILE_SIZE * 2)

        self.font = pygame.font.SysFont('Verdana', 18)

    def update(self):
        if self.index:
            image = self.SPRITES[self.index]
            self.screen.blit(image, self.rect.topleft - self.game.offset)
            light_tint = self.LIGHT_TINTS[self.index]
            self.game.emissive_surf.blit(light_tint, self.rect.topleft - self.game.offset)

        # self.screen.blit((surf := self.font.render(f"{self.index}", False, (255, 0, 0))), surf.get_rect(topleft=self.rect.topleft - self.game.offset))
    
class Lava_Tile(Tile):
    def __init__(self, game, pos: tuple, top_edge = False, bottom_edge = False):
        super().__init__(game, pos, 100)
        
        self.hitbox = pygame.Rect(*self.pos, TILE_SIZE, TILE_SIZE)

        self.lava = True
        self.top_edge = top_edge
        self.bottom_edge = bottom_edge

        self.surf = pygame.Surface((TILE_SIZE, TILE_SIZE * 1), pygame.SRCALPHA)
        self.surf.fill((255, 102, 0))

    def update(self):
        self.screen.blit(self.surf, self.rect.topleft - self.game.offset)
        pygame.draw.rect(self.game.emissive_surf, (255, 102, 0), [*(self.rect.topleft - self.game.offset), self.rect.width, self.rect.height])

        if self.top_edge:
            pygame.draw.rect(self.screen, (20, 20, 20), [*(self.rect.topleft - self.game.offset), self.rect.width, self.rect.height * 0.75])
            pygame.draw.rect(self.game.emissive_surf, (20, 20, 20), [*(self.rect.topleft - self.game.offset), self.rect.width, self.rect.height * 0.75])
        
        # pygame.draw.rect(self.screen, (255, 0, 0), [*(self.rect.topleft - self.game.offset), *self.rect.size], 2)