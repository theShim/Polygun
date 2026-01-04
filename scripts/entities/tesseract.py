import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random
import numpy as np

from scripts.particles.sparks import Spark
from scripts.projectiles.bullet import Bullet

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE, SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.utils.convex_hull import convex_hull

    ##############################################################################################

def project_4d_to_3d(p, d=3):
    w = 1 / (d - p[3])
    return p[:3] * w

def project_3d_to_2d(p, d=4):
    z = 1 / (d - p[2])
    return p[:2] * z

class Transform4D:

    @staticmethod    
    def rot_xy(a):
        return np.array([
            [ math.cos(a), -math.sin(a), 0, 0],
            [ math.sin(a),  math.cos(a), 0, 0],
            [ 0, 0, 1, 0],
            [ 0, 0, 0, 1]
        ])

    @staticmethod
    def rot_xz(a):
        return np.array([
            [math.cos(a), 0, math.sin(a), 0],
            [0, 1, 0, 0],
            [-math.sin(a), 0, math.cos(a), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rot_xw(a):
        return np.array([
            [math.cos(a), 0, 0, -math.sin(a)],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [math.sin(a), 0, 0, math.cos(a)]
        ])
    
    @staticmethod
    def rot_yz(a):
        return np.array([
            [1, 0, 0, 0],
            [0, math.cos(a), -math.sin(a), 0],
            [0, math.sin(a), math.cos(a), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rot_zw(a):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0,  math.cos(a), -math.sin(a)],
            [0, 0,  math.sin(a),  math.cos(a)]
        ])
    
    ##############################################################################################

class Tesseract(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        #array of 4D points
        self.points = np.array([
            [x, y, z, w]
            for x in (-1, 1)
            for y in (-1, 1)
            for z in (-1, 1)
            for w in (-1, 1)
        ], dtype=float)
        
        self.edges = []
        for i in range(len(self.points)):
            for j in range(i + 1, len(self.points)):
                if np.sum(self.points[i] != self.points[j]) == 1:
                    self.edges.append((i, j))

        self.angle = 0.0
        self.scale = 900
        
        self.pos = vec(WIDTH / 2, HEIGHT)

        self.health = 1000

    def bullet_collide(self, bullet: Bullet):
        rotated = self.points @ (Transform4D.rot_zw(self.angle) @ Transform4D.rot_xw(0) @ Transform4D.rot_xz(self.angle) @ Transform4D.rot_yz(2.93)).T
        projected = []
        for p in rotated:
            p3 = project_4d_to_3d(p)
            p2 = project_3d_to_2d(p3)
            projected.append(p2)
        projected = np.array(projected) * self.scale + self.pos

        points = projected.tolist()
        self.hitbox = convex_hull(points)

        if self.ray_intersects(self.hitbox, bullet.pos.x, bullet.pos.y):
            self.health -= bullet.damage
            return True
        return False
        
    def get_edges(self, points):
        edges = []
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            edges.append((start, end))
        return edges
        
    def ray_intersects(self, hitbox_points, ray_end_x, ray_y): #separating axis theorem
        intersections = 0

        for edge in self.get_edges(hitbox_points):
            start, end = edge
            if (start[1] > ray_y and end[1] < ray_y) or (start[1] < ray_y and end[1] > ray_y):
                t = (ray_y - start[1]) / (end[1] - start[1])
                intersection_x = start[0] + t * (end[0] - start[0])
                if intersection_x < ray_end_x:  # Check if the intersection is to the right of the start
                    intersections += 1
        
        return intersections % 2 == 1  #odd intersections mean inside, even means outside

    def update(self):
        # d = -1 if (keys := pygame.key.get_pressed())[pygame.K_u] else (1 if keys[pygame.K_j] else 0)
        self.angle += 1. * self.game.dt

        self.game.debugger.add_text(f"{self.angle}")

        #zw = special 4d one the funny looking one
        rotated = self.points @ (Transform4D.rot_zw(self.angle) @ Transform4D.rot_xw(0) @ Transform4D.rot_xz(self.angle) @ Transform4D.rot_yz(2.93)).T
        
        projected = []
        projected_3d = []
        for p in rotated:
            p3 = project_4d_to_3d(p)
            projected_3d.append(p3)
            p2 = project_3d_to_2d(p3)
            projected.append(p2)

        projected = np.array(projected) * self.scale + self.pos - self.game.offset
        
        for i, j in self.edges:
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                projected[i] + vec(0, 5 + (projected_3d[i][2] + 1) * 15),
                projected[j] + vec(0, 5 + (projected_3d[j][2] + 1) * 15),
                8
            )
        
        for i, j in self.edges:
            pygame.draw.line(
                self.screen,
                (120-60, 200-60, 255-60),
                projected[i] + vec(3),
                projected[j] + vec(3),
                8
            )
            pygame.draw.line(
                self.screen,
                (120, 200, 255),
                projected[i],
                projected[j],
                8
            )

        for p in projected:
            pygame.draw.circle(self.screen, (120, 200, 255), p.astype(int), 9)