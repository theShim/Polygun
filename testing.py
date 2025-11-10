# def generate_dungeon(max_cells=15, branch_weight=3):
#     """
#     Generates a dungeon as connected rooms (cells) branching out from a start node.

#     Args:
#         max_cells: maximum number of cells to generate
#         branch_weight: branching probability control (lower = more branching)
#                        chance = 1 / (branch_weight + 1)

#     Returns:
#         cells: list of all generated cell coordinates
#         connections: dict mapping each cell to its connected neighbors
#         boss_room: coordinate of chosen boss room (leaf node)
#     """

#     start = (0, 0)
#     cells = [start]
#     stack = [start]
#     connections = {start: []}

#     while len(cells) < max_cells and stack:
#         x, y = stack.pop()
#         # generate neighbor positions
#         neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
#         random.shuffle(neighbors)

#         for nx, ny in neighbors:
#             if len(cells) >= max_cells:
#                 break

#             if (nx, ny) not in cells and random.randint(0, branch_weight) == branch_weight:
#                 # Add new cell
#                 cells.append((nx, ny))
#                 stack.append((nx, ny))
#                 connections.setdefault((x, y), []).append((nx, ny))
#                 connections.setdefault((nx, ny), []).append((x, y))

#     # Find leaf nodes (rooms with only one connection)
#     leaf_nodes = [cell for cell, links in connections.items() if len(links) == 1 and cell != start]

#     # Choose a random leaf node to be the boss room
#     boss_room = random.choice(leaf_nodes) if leaf_nodes else None

#     return cells, connections, boss_room

import random

def generate_path(min_length=5, max_length=10):
    start = (0, 0)
    cells = [start]
    stack = [start]
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
        #otherwise just get rid of the cell from the stack entirely
        else:
            stack.pop()

    return cells