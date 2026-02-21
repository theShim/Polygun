import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

from scripts.gui.custom_fonts import Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Minimap(pygame.sprite.Sprite):
    def __init__(self, game, groups, conns: dict, exit_room=None):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.gui_surf

        #find the bounds of the rooms to construct a surface size
        rooms = list(conns.keys())
        min_x = math.inf
        min_y = math.inf
        max_x = -math.inf
        max_y = -math.inf
        for room in rooms:
            min_x = min(min_x, room[0])
            min_y = min(min_y, room[1])
            max_x = max(max_x, room[0])
            max_y = max(max_y, room[1])
        
        #added a parameter so I could easily scale the size of gui elements as needed
        self.pxsize = pxsize = 4
        #calculating the surface size requied to fit every box for the minimap
        width  = (max_x - min_x + 1) * ((8 + 6) * pxsize) - (6 * pxsize)
        height = (max_y - min_y + 1) * ((6 + 4) * pxsize) - (4 * pxsize)

        #construct the actual surf
        self.surf = pygame.Surface((width + 3, height + 3), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(topright = (WIDTH - 16, 0 + 16))
        self.surf_coords = {}

        #draw the raw rectangles for each room at their relative (x, y) positions
        for (x, y) in rooms:
            col = (59 + 40, 57 + 40, 65 + 40)
            nx = x + abs(min_x) #coords relative to the surface
            ny = y + abs(min_y)
            self.surf_coords[(x, y)] = (nx * ((8 + 6) * pxsize), ny * ((6 + 4) * pxsize))
            pygame.draw.rect(self.surf, (0, 0, 1), [nx * ((8 + 6) * pxsize) + 3, ny * ((6 + 4) * pxsize) + 3, 8 * pxsize, 6 * pxsize], pxsize, border_radius=4)
            pygame.draw.rect(self.surf, col, [nx * ((8 + 6) * pxsize), ny * ((6 + 4) * pxsize), 8 * pxsize, 6 * pxsize], border_radius=4)
            pygame.draw.rect(self.surf, (74 + 120, 71 + 120, 68 + 120), [nx * ((8 + 6) * pxsize), ny * ((6 + 4) * pxsize), 8 * pxsize, 6 * pxsize], pxsize, border_radius=4)
        
        #draw the connections instead
        used = []
        for room in conns:
            for conn in conns[room]:
                if key := tuple(sorted([room, conn])) in used:
                    continue
                used.append(key)

                #the type of connection to be drawn differs depending on which way it's going
                #each axis has a different calculation for the topleft of the rect
                delta = (conn[0] - room[0], conn[1] - room[1])
                x, y = room
                x += abs(min_x)
                y += abs(min_y)
                
                #going to the left  
                if delta == (-1, 0):
                    #shadow
                    pygame.draw.rect(
                        self.surf, 
                        (0, 0, 0), 
                        [
                            self.surf_coords[room][0] - 6 * pxsize + 3, 
                            self.surf_coords[room][1] + 2 * pxsize + 3, 
                            5 * pxsize + 1, 2 * pxsize
                        ])
                    #actual bridge
                    pygame.draw.rect(
                        self.surf, 
                        (59 + 40, 57 + 40, 65 + 40), 
                        [
                            self.surf_coords[room][0] - 6 * pxsize, 
                            self.surf_coords[room][1] + 2 * pxsize, 
                            6 * pxsize, 2 * pxsize
                        ])
                    
                #going to the right
                elif delta == (1, 0):
                    pygame.draw.rect(
                        self.surf, 
                        (0, 0, 0), 
                        [
                            self.surf_coords[room][0] + 8 * pxsize + 3, 
                            self.surf_coords[room][1] + 2 * pxsize + 3, 
                            5 * pxsize, 2 * pxsize
                        ])
                    pygame.draw.rect(
                        self.surf, 
                        (59 + 40, 57 + 40, 65 + 40), 
                        [
                            self.surf_coords[room][0] + 8 * pxsize, 
                            self.surf_coords[room][1] + 2 * pxsize, 
                            6 * pxsize, 2 * pxsize
                        ])

                #going down
                elif delta == (0, 1):
                    pygame.draw.rect(
                        self.surf, 
                        (0, 0, 0), 
                        [
                            self.surf_coords[room][0] + 3 * pxsize + 3, 
                            self.surf_coords[room][1] + 6 * pxsize + 3, 
                            2 * pxsize, 3 * pxsize + 1
                        ])
                    pygame.draw.rect(
                        self.surf, 
                        (59 + 40, 57 + 40, 65 + 40), 
                        [
                            self.surf_coords[room][0] + 3 * pxsize, 
                            self.surf_coords[room][1] + 6 * pxsize, 
                            2 * pxsize, 4 * pxsize
                        ])

                #going up
                elif delta == (0, -1):
                    pygame.draw.rect(
                        self.surf, 
                        (0, 0, 0), 
                        [
                            self.surf_coords[room][0] + 3 * pxsize + 3, 
                            self.surf_coords[room][1] - 4 * pxsize + 3, 
                            2 * pxsize, 3 * pxsize + 1
                        ])
                    pygame.draw.rect(
                        self.surf, 
                        (59 + 40, 57 + 40, 65 + 40), 
                        [
                            self.surf_coords[room][0] + 3 * pxsize, 
                            self.surf_coords[room][1] - 4 * pxsize, 
                            2 * pxsize, 4 * pxsize
                        ])
                    
        self.angle = 0
        self.exit_room = exit_room #room object

    def update(self):
        #player rendering
        self.angle += math.radians(3)
        points = np.array([
            vec(math.cos(self.angle), math.sin(self.angle)),
            vec(math.cos(self.angle - math.pi/2), math.sin(self.angle - math.pi/2)),
            vec(math.cos(self.angle - math.pi), math.sin(self.angle - math.pi)),
            vec(math.cos(self.angle + math.pi/2), math.sin(self.angle + math.pi/2)),
        ]) * self.pxsize * 1.2

        surf = self.surf.copy()

        try: #preventing bug for if the state does not have a valid room for the tilemap
             #e.g. transition state
            player_pos = self.surf_coords[self.game.state_loader.current_state.get_current_room().pos]
        except:
            return
        points += player_pos + vec(self.pxsize * 4, self.pxsize * 3)
        pygame.draw.polygon(surf, (0, 255 - 100, 247 - 100), points + vec(1, 2))
        pygame.draw.polygon(surf, (0, 255, 247), points)

        #exit flag
        exit_room_pos = self.surf_coords[self.exit_room.pos]
        if player_pos != exit_room_pos:
            
            #stick of the flag
            p1 = vec(-1.25, -1) * self.pxsize + exit_room_pos + vec(self.pxsize * 4 - 2, self.pxsize * 3 - 3)
            p2 = vec(-1.25, 1.25) * self.pxsize + exit_room_pos + vec(self.pxsize * 4 - 2, self.pxsize * 3 + 1)
            pygame.draw.line(surf, (0, 0, 0), p1 + vec(1, 1), p2 + vec(1, 1), 2)
            pygame.draw.line(surf, (110, 45, 2), p1, p2, 2)

            points = np.array([
                vec(-1.25, -1),
                vec(1.5, -1),
                vec(1.5, 1),
                vec(-1.25, 1)
            ]) * self.pxsize + exit_room_pos + vec(self.pxsize * 4, self.pxsize * 3)

            #roughly O(25) for loop each square of the exit flag
            #each y value is affected by a sin wave with the x value as a parameter for a swaying effect
            i = False
            for y in range(int(points[0, 1]), int(points[2, 1]), 2):
                for x in range(int(points[0, 0]), int(points[1, 0]), 2):
                    i = not i
                    pygame.draw.rect(surf, (0, 0, 0), [x, y + 2 + math.sin(3 * self.angle + x / 2) * 0.5 - 1, 2, 2])
                    pygame.draw.rect(surf, (0, 0, 0) if i else (255, 255, 255), [x, y + math.sin(3 * self.angle + x / 2) * 0.5 - 1, 2, 2])
                i = not i #alternate between black and white squares

        self.screen.blit(surf, self.rect)