import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.entities.enemy import Enemy, EnemySpawnData
from scripts.entities.tesseract import Tesseract
from scripts.world_loading.tilemap import Tilemap

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################

def generate_path(min_length=5, max_length=10):
    start = (0, 0)
    cells = [start]
    stack = [start]
    connections = {}
    target_length = random.randint(min_length, max_length)

    #while there are possible cell locations and it hasn't reached the wanted target length,
    while stack and len(cells) < target_length:
        x, y = stack[-1] #take the top position on the stack
        neighbours = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        random.shuffle(neighbours) #randomise all the possible neighbours surrounding the current cell
        
        for i in range(2):
            #pick the next available position out of the random neighbour list
            next_cell = None
            for nx, ny in neighbours:
                if (nx, ny) not in cells:
                    next_cell = (nx, ny)
                    break

            #if one of the positions is available, add it to stack and the cell list and repeat the process
            if next_cell:
                neighbours.remove((nx, ny))
                
                cells.append(next_cell)
                stack.append(next_cell)

                if (x, y) not in connections:
                    connections[(x, y)] = []
                if (nx, ny) not in connections:
                    connections[(nx, ny)] = []
                connections[(x, y)].append((nx, ny))
                connections[(nx, ny)].append((x, y))

            #otherwise just get rid of the cell from the stack entirely
            else:
                stack.pop()

    return cells, connections


class DungeonLevel:
    def __init__(self, game, parent):
        self.game = game
        self.parent_dungeon = parent

        self.rooms: dict[tuple, Room] = {}
        self.conns: dict[tuple, list[tuple]] = {}
        self.current_room = None
        self.exit_room: Room = None
        self.boss_room: Room = None

        self.generate_dungeon()

    def generate_dungeon(self):
        nodes, conns = generate_path()
        self.conns = conns

        for node in nodes:
            self.rooms[node] = Room(self.game, node, conns[node], self)
        for node in nodes:
           self.rooms[node].tilemap.auto_tile()

        self.rooms[(0, 0)].start_room = True

    def generate_boss_room(self):
        leaves = [cell for cell, links in self.conns.items() if len(links) == 1 and cell != (0, 0)]
        self.boss_room = random.choice(leaves)


class Room:

    UNENTERED = 0
    PLAYER_FIGHTING = 1
    CLEARED = 2

    def __init__(self, game, pos, conns, parent_level):
        self.game = game

        self.pos = pos
        self.conns = conns
        self.parent_level = parent_level
        self.tilemap = Tilemap(self.game, self)

        self.state = Room.UNENTERED
        self.start_room = False
        self.temp = True

        self.wave_stack: list[list[EnemySpawnData]] = [
            [EnemySpawnData(Enemy, 4), EnemySpawnData(Enemy, 4)],
            [EnemySpawnData(Enemy.Pentagon, 1), EnemySpawnData(Enemy.Hexagon, 1)],
            [EnemySpawnData(Enemy, 2)],
        ]
        self.max_waves = len(self.wave_stack)

        self.enemies_to_kill = pygame.sprite.Group()

        
    def spawn_wave(self):
        if not self.wave_stack:
            return
        
        wave = self.wave_stack.pop(0)

        for data in wave:
            pos = [self.pos[0] * TILE_SIZE * LEVEL_SIZE + random.uniform(TILE_SIZE * 2, LEVEL_SIZE * TILE_SIZE - TILE_SIZE * 2),
                    self.pos[1] * TILE_SIZE * LEVEL_SIZE + random.uniform(TILE_SIZE * 2, LEVEL_SIZE * TILE_SIZE - TILE_SIZE * 2)]
            for _ in range(data.count):
                offset = vec(random.uniform(-TILE_SIZE, TILE_SIZE), random.uniform(-TILE_SIZE, TILE_SIZE))
                enemy = data.enemy_class(
                    self.game,
                    [self.game.all_sprites, self.game.entities, self.game.enemies, self.enemies_to_kill],
                    pos + offset
                )

    def update(self):
        if self.start_room:
            self.state = Room.CLEARED
            self.wave_stack = []

            if self.temp:
                Tesseract(self.game, [self.game.all_sprites, self.game.entities, self.game.bosses])
                self.temp = False
            
        #only time the update method (and therefore the first condition) is triggered is if the player is in the room, 
        #i.e. it's been entered by the player
        if self.state == Room.UNENTERED:
            
            room_x = (self.game.player.pos.x % (TILE_SIZE * LEVEL_SIZE)) // TILE_SIZE
            room_y = (self.game.player.pos.y % (TILE_SIZE * LEVEL_SIZE)) // TILE_SIZE
            delta_x = room_x - (LEVEL_SIZE // 2)
            delta_y = room_y - (LEVEL_SIZE // 2)
            mag = delta_x * delta_x + delta_y * delta_y
            
            if mag < (LEVEL_SIZE * 0.5 * 0.75) ** 2:
                self.state = Room.PLAYER_FIGHTING

                self.tilemap.fill_corridoors()
                for conn in self.conns:
                    self.parent_level.rooms[conn].tilemap.fill_corridoors()

                self.tilemap.auto_tile()
                for conn in self.conns:
                    self.parent_level.rooms[conn].tilemap.auto_tile()

                self.spawn_wave()

        elif self.state == Room.PLAYER_FIGHTING:
            if len(self.enemies_to_kill):
                return
            
            self.spawn_wave()
            if len(self.enemies_to_kill):
                return
            
            self.state = Room.CLEARED

            self.tilemap.remove_corridoors()
            for conn in self.conns:
                self.parent_level.rooms[conn].tilemap.remove_corridoors()

            self.tilemap.auto_tile()
            for conn in self.conns:
                self.parent_level.rooms[conn].tilemap.auto_tile()