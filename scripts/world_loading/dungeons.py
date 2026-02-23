import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.entities.enemy import Enemy, EnemySpawnData
from scripts.entities.tesseract import Tesseract
from scripts.gui.minimap import Minimap
from scripts.world_loading.exit_portal import ExitPortal
from scripts.world_loading.tilemap import Tilemap
from scripts.world_loading.vending_machine import VendingMachine

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE, SIZE

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
    def __init__(self, game, parent, level_no=0):
        self.game = game
        self.parent_dungeon = parent

        self.rooms: dict[tuple, Room] = {}
        self.conns: dict[tuple, list[tuple]] = {}
        self.level_no = level_no

        self.current_room = None
        self.start_room: Room = None
        self.exit_room: Room = None
        self.boss_room: Room = None

        self.minimap: Minimap = None

        self.generate_dungeon()

    def get_leaves(self) -> list[tuple]:
        return [cell for cell, links in self.conns.items() if len(links) == 1 and cell != (0, 0)]

    def generate_dungeon(self):
        nodes, conns = generate_path(7, 9)
        self.conns = conns

        for node in nodes:
            self.rooms[node] = Room(self.game, node, conns[node], self)
        for node in nodes:
           self.rooms[node].tilemap.auto_tile()
           self.rooms[node].tilemap.lava_region_dfs()

        self.generate_start_room()
        self.generate_exit_room()
        self.choose_vending_rooms()

    def generate_start_room(self):
        self.rooms[(0, 0)].start_room = True
        self.start_room = self.rooms[(0, 0)]
        self.start_room.tilemap.load()
        self.start_room.tilemap.auto_tile()

    def generate_exit_room(self):
        leaves = self.get_leaves()
        leaves = sorted(leaves, key=lambda c: c[0] ** 2 + c[1] ** 2)
        self.exit_room = self.rooms[leaves[-1]]
        self.exit_room.exit_room = True
        
        # self.rooms[(0, 0)].exit_room = True
        # self.exit_room = self.rooms[(0, 0)]

    def choose_vending_rooms(self):
        for node in self.rooms:
            room = self.rooms[node]
            room.vending_room = random.randint(1, 100) <= 70 and not (room.start_room or room.exit_room)

    def generate_boss_room(self):
        leaves = self.get_leaves()
        self.boss_room = random.choice(leaves)

    def generate_minimap(self):
        self.minimap = Minimap(self.game, [self.game.gui_elements], self.conns, exit_room=self.exit_room)


class Room:

    UNENTERED = 0
    PLAYER_FIGHTING = 1
    CLEARED = 2

    def __init__(self, game, pos, conns, parent_level):
        self.game = game

        self.state = Room.UNENTERED
        self.start_room = False
        self.exit_room = False
        self.exit_portal_spawned = False
        self.vending_room = False
        self.vending_machine_spawned = False
        self.temp = True

        self.pos = pos
        self.conns = conns
        self.parent_level = parent_level
        self.tilemap = Tilemap(self.game, self)

        self.wave_stack: list[list[EnemySpawnData]] = self.generate_wave_stack()
        self.max_waves = len(self.wave_stack)

        self.enemies_to_kill = pygame.sprite.Group()


    def spawn_exit_portal(self):
        if not self.exit_room: return #if it is not the exit room, don't spawn
        if self.exit_portal_spawned: return #if it's already been spawned once, don't spawn again

        self.exit_portal_spawned = True #flag variable
        ExitPortal(self.game, [self.game.all_sprites], [self.pos[0] * LEVEL_SIZE * TILE_SIZE + TILE_SIZE * LEVEL_SIZE / 2, self.pos[1] * LEVEL_SIZE * TILE_SIZE + TILE_SIZE * LEVEL_SIZE / 2])

    def spawn_vending_machine(self):
        if not self.vending_room: return
        if self.vending_machine_spawned: return

        self.vending_machine_spawned = True
        VendingMachine(self.game, [self.game.all_sprites], [self.pos[0] * LEVEL_SIZE * TILE_SIZE + TILE_SIZE * LEVEL_SIZE / 2, self.pos[1] * LEVEL_SIZE * TILE_SIZE + TILE_SIZE * LEVEL_SIZE / 2])


    def generate_wave_stack(self) -> list[list[EnemySpawnData]]:
        dungeon_level = self.parent_level.level_no #current dungeon level
        difficulty = dungeon_level + 1 #this scales directly with the level, with +1 to avoid 0

        wave_stack = []
        #the number of waves should ideally increase gradually every 1.5 levels
        num_waves = 1 + int(math.ceil(dungeon_level / 1.5))

        for i in range(num_waves):
            #later waves get a higher budget, hence the i * 2
            #the difficulty should cause a non-linear increase too, from the ** 1.2
            budget = int(4 + 2 * (difficulty ** 1.2)) + i * 2
          
            remaining = budget #remaining budget for this wave  
            to_spawn = {} #dictionary of {"enemy_type" : cost (int)}

            #keep adding enemies till the budget is completely exhausted
            #(which is why triangle had to be 1)
            while remaining > 0:
                #randomly choose an enemy based on weighted probabilites from their costs
                enemy_type = random.choices(
                    [
                        Enemy, Enemy.Pentagon, Enemy.Hexagon
                    ], 
                    [
                        #simple triangles become more common as difficulty rises to prevent
                        #a hexagon or pentagon massacre
                        2 * (difficulty - 1) * EnemySpawnData.COSTS[Enemy] + 10, 
                        #stronger enemies also increase in likelihood at a slower rate
                        2 * (difficulty - 1) * EnemySpawnData.COSTS[Enemy.Pentagon] + 2, 
                        2 * (difficulty - 1) * EnemySpawnData.COSTS[Enemy.Hexagon] + 1
                    ], 
                    k=1
                )[0]
                cost = EnemySpawnData.COSTS[enemy_type] #look up selected enemy cost
                
                #only add the enemy if there is enough budget remaining
                if cost <= remaining:
                    #then increment their count and decrement the remaining budget
                    to_spawn[enemy_type] = to_spawn.get(enemy_type, 0) + 1
                    remaining -= cost

            #construct the final wave stack
            wave_data = []
            for e_type, count in to_spawn.items():
                remaining = count

                #break apart groups of 3-4 enemies to prevent massive clumps in one spot
                while remaining > 0:
                    n = random.randint(3, 4)
                    group_size = min(n, remaining)
                    wave_data.append(EnemySpawnData(e_type, group_size))
                    remaining -= group_size
            
            wave_stack.append(wave_data) #add the wave to the stack
        return wave_stack #return the full wave stack
        
    #spawn the next wave for the current room
    def spawn_wave(self):
        if not self.wave_stack: #if there are any remaining waves to clear...
            return
        
        #get the last wave from the top of the stack
        wave = self.wave_stack.pop(0)

        #for each enemyspawndata in the wave
        for data in wave:
            #calculate a random position in the room
            pos = [self.pos[0] * TILE_SIZE * LEVEL_SIZE + random.uniform(TILE_SIZE * 2, LEVEL_SIZE * TILE_SIZE - TILE_SIZE * 2),
                    self.pos[1] * TILE_SIZE * LEVEL_SIZE + random.uniform(TILE_SIZE * 2, LEVEL_SIZE * TILE_SIZE - TILE_SIZE * 2)]
            #spawn in the required amount of enemies with a slight offset so they don't
            #spawn on top of each other
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
            
        #only time the update method (and therefore the first condition) is triggered is if the player is in the room, 
        #i.e. it's been entered by the player
        if self.state == Room.UNENTERED:
            
            room_x = (self.game.player.pos.x % (TILE_SIZE * LEVEL_SIZE)) // TILE_SIZE
            room_y = (self.game.player.pos.y % (TILE_SIZE * LEVEL_SIZE)) // TILE_SIZE
            delta_x = room_x - (LEVEL_SIZE // 2)
            delta_y = room_y - (LEVEL_SIZE // 2)
            mag = delta_x * delta_x + delta_y * delta_y
            
            #just so the wave doesn't start instantly outside the corridor, add some
            #leeway at a radius away from the center of the room
            if mag < (LEVEL_SIZE * 0.5 * 0.75) ** 2:
                self.state = Room.PLAYER_FIGHTING #set the room state to fighting

                #fill the corridoors in with tiles
                self.tilemap.fill_corridoors()
                for conn in self.conns:
                    self.parent_level.rooms[conn].tilemap.fill_corridoors()

                #reautotile to fix visual bugs
                self.tilemap.auto_tile()
                for conn in self.conns:
                    self.parent_level.rooms[conn].tilemap.auto_tile()

                self.spawn_wave()

        elif self.state == Room.PLAYER_FIGHTING:
            #if there are enemies in the current room, return back
            if len(self.enemies_to_kill):
                return
            
            #otherwise spawn the next wave
            self.spawn_wave()
            #if there are enemies - i.e. there is still a wave to complete - return
            if len(self.enemies_to_kill):
                return
            
            #otherwise there are no more rooms and therefore it has been cleared
            self.state = Room.CLEARED

            #remove the corridoors
            self.tilemap.remove_corridoors()
            for conn in self.conns:
                self.parent_level.rooms[conn].tilemap.remove_corridoors()

            #retile again
            self.tilemap.auto_tile()
            for conn in self.conns:
                self.parent_level.rooms[conn].tilemap.auto_tile()

        elif self.state == Room.CLEARED:
            self.spawn_exit_portal() #try spawning exit portal if its an end room
            self.spawn_vending_machine() #try spawning a vending machine if its a room for that