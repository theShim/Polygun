import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import random
import sys
import math
import time
import numpy as np

from scipy.spatial import Delaunay

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class Del:
    def __init__(self, game, point_num=100):
        self.game = game
        self.screen = self.game.screen

        self.points = np.array([
            vec(random.uniform(-50, WIDTH+50), random.uniform(-50, HEIGHT+50)) for i in range(point_num)
        ] + [
            vec(-50, -50),
            vec(-50, HEIGHT+50),
            vec(WIDTH+50, -50),
            vec(WIDTH+50, HEIGHT+50)
        ])
        #movement of each point in a random direction
        self.vectors = np.array([
            vec([random.uniform(-1, 1), random.uniform(-1, 1)]) * 0.9 for i in range(point_num)
        ] + [
            vec(0, 0),
            vec(0, 0),
            vec(0, 0),
            vec(0, 0),
        ])

        self.weight = 0
        self.p1 = vec(random.random() * WIDTH, random.random() * HEIGHT)
        self.v1 = vec([random.uniform(-1, 1), random.uniform(-1, 1)]) * 2
        self.p2 = vec(random.random() * WIDTH, random.random() * HEIGHT)
        self.v2 = vec([random.uniform(-1, 1), random.uniform(-1, 1)]) * 2

    def update(self):
        self.points += self.vectors
        self.p1 += self.v1
        self.p2 += self.v2

        if self.p1.x < -50 or self.p1.x > WIDTH + 50:
            self.v1.x *= -1
        if self.p2.x < -50 or self.p2.x > WIDTH + 50:
            self.v2.x *= -1
        if self.p1.y < -50 or self.p1.y > HEIGHT + 50:
            self.v1.y *= -1
        if self.p2.y < -50 or self.p2.y > HEIGHT + 50:
            self.v2.y *= -1

        #border collisions
        condition1 = self.points[:, 0] < -50
        condition2 = self.points[:, 1] < -50
        condition3 = self.points[:, 0] > WIDTH + 50
        condition4 = self.points[:, 1] > HEIGHT + 50

        self.vectors[condition1, 0] *= -1
        self.vectors[condition2, 1] *= -1
        self.vectors[condition3, 0] *= -1
        self.vectors[condition4, 1] *= -1

        mousePos = self.game.mousePos

        #recalculate the new triangles and render them
        self.triangles = Delaunay(np.vstack([self.points, mousePos]))
        self.draw()

    def draw(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.weight += 20
        elif keys[pygame.K_DOWN]:
            self.weight -= 20

        mousePos = self.game.mousePos

        points = np.vstack([self.points, mousePos])
        for polygon in self.triangles.simplices:
            polygon = points[polygon]

            # height = polygon[polygon[:, 1].argsort()][-1][1]
            # ratio = ((height + self.weight) / HEIGHT)
            # t = min(1, max(0, ratio))

            centroid = polygon.mean(axis=0)
            d1 = self.p1.distance_squared_to(centroid)#np.linalg.norm(centroid - self.p1)
            d2 = self.p2.distance_squared_to(centroid)#np.linalg.norm(centroid - self.p2)
            t = d1 / (d1 + d2)

            c = pygame.Color(0, 242, 255).lerp(pygame.Color(91, 44, 131), t)
            pygame.draw.polygon(self.screen, c, polygon, 0)
            
        # for p in self.points:
        #     pygame.draw.circle(screen, (255 - 255, 255 - 255, 255 - 255), p, 3)