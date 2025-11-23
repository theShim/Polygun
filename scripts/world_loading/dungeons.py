import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.world_loading.tilemap import Tilemap

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, Z_LAYERS, TILE_SIZE

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
        
        #pick the next available position out of the random neighbour list
        next_cell = None
        for nx, ny in neighbours:
            if (nx, ny) not in cells:
                next_cell = (nx, ny)
                break

        #if one of the positions is available, add it to stack and the cell list and repeat the process
        if next_cell:
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
    def __init__(self, game):
        self.game = game

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
            self.rooms[node] = Room(self.game, node, conns[node])

    def generate_boss_room(self):
        leaves = [cell for cell, links in self.conns.items() if len(links) == 1 and cell != (0, 0)]
        self.boss_room = random.choice(leaves)


class Room:
    def __init__(self, game, pos, conns):
        self.game = game

        self.pos = pos
        self.conns = conns
        self.tilemap = Tilemap(self.game, self)