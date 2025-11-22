def deepcopy(arr): return [deepcopy(x) if isinstance(x, list) else x for x in arr]

grid = [[" " for j in range(11)] for i in range(11)]
grid[2][2] = "1"

sgn = lambda n: -1 if n < 0 else (1 if n > 0 else 0) 

def found_positions(cgrid):
    poss = []
    for y, row in enumerate(cgrid):
        for x, el in enumerate(row):
            if el != " ":
                poss.append([x, y])
    return poss

def possible_corners(poss):
    min_x = 100
    max_x = -100
    min_y = 100
    max_y = -100
    for pos in poss:
        if pos[0] < min_x: min_x = pos[0] - 1
        if pos[1] < min_y: min_y = pos[1] - 1
        if pos[0] > max_x: max_x = pos[0] + 1
        if pos[1] > max_y: max_y = pos[1] + 1
    
    possible = [[min_x, min_y], [min_x, max_y], [max_x, min_y], [max_x, max_y]]
    to_return = []
    directions = []
    
    for thing in possible:
        if (0 <= thing[0] < 11) and (0 <= thing[1] < 11):
            to_return.append(thing)
            directions.append([[-sgn(thing[0] - 2), 0], [0, -sgn(thing[1] - 2)]])
    return list(zip(to_return, directions))

def update(current_grid, i):
    # print("enternig", i)
    # for row in current_grid:
    #     print(row)
    # print('######################')

    if i == 8:
        for row in current_grid:
            print(row)
        print('######################')
        return
    
    for corner, directions in possible_corners(found_positions(current_grid)):
        new_grid = deepcopy(current_grid)
        new_grid[corner[1]][corner[0]] = f"{i}"

        invalid = False
        for dir in directions:
            for j in range(i):
                new_pos_x = corner[0] + dir[0] * j
                new_pos_y = corner[1]
                if (0 <= new_pos_x < 11) and (0 <= new_pos_y < 11) and new_grid[new_pos_y][new_pos_x] in [" ", f"{i}"]:
                    new_grid[new_pos_y][new_pos_x] = f"{i}"
                else:
                    invalid = True
            for j in range(i):
                new_pos_x = corner[0]
                new_pos_y = corner[1] + dir[1] * j
                if (0 <= new_pos_x < 11) and (0 <= new_pos_y < 11) and new_grid[new_pos_y][new_pos_x] in [" ", f"{i}"]:
                    new_grid[new_pos_y][new_pos_x] = f"{i}"
                else:
                    invalid = True

        # print(invalid)
        if invalid:
            continue
                

        update(new_grid, i + 1)

        # for directions in [[[1, 0], [0, 1]]]:
        #     for dir in directions:
        #         for j in range(1, i):
        #             new_pos_x = corner[0] + dir[0] * j
        #             new_pos_y = corner[1] + dir[1] * j
        #             if (0 <= new_pos_x < 11) and (0 <= new_pos_y < 11):
        #                 current_grid[new_pos_y][new_pos_x] = f"{i}"
        #     update(current_grid, i + 1)
    

i = 2
update(deepcopy(grid), i)