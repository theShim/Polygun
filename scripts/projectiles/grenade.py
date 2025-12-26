import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random

from scripts.particles.sparks import Grenade_Spark
from scripts.particles.grenade_explosion import Grenade_Explosion

from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

class Grenade(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, target_pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        
        self.start_pos = vec(pos)
        self.target_pos = vec(target_pos)
        self.pos = self.start_pos.copy()

        self.v = 19 * math.sqrt(GRAV)
        self.R_target = (self.target_pos - self.start_pos).magnitude()
        self.R_max = (self.v * self.v) / GRAV
        self.R = min(self.R_target, self.R_max)

        sin2theta = (GRAV * self.R) / (self.v * self.v)
        sin2theta = max(-1.0, min(1.0, sin2theta))
        self.theta = 0.5 * math.asin(sin2theta)

        self.total_time = (2 * self.v * math.sin(self.theta)) / GRAV
        self.height_mult = 2

        self.time = 0.3
        self.dh = 0
        self.landed = False

        self.spark_flag = False
        self.spark = Timer(3, 1)

    def move(self):
        self.time += self.game.dt * 4
        t = self.time / self.total_time

        self.dh = (self.v * math.sin(self.theta) * self.time - (0.5 * GRAV * self.time * self.time)) * self.height_mult
        
        if self.time > self.total_time:
            self.time = self.total_time
            self.dh = 0
            self.landed = True
            t = 1

        self.pos = self.start_pos.lerp(self.target_pos, t)

    def update(self):
        self.move()

        if self.landed:
            Grenade_Explosion(self.game, [self.game.all_sprites, self.game.particles], self.pos)
            return self.kill()

        self.spark.update()
        if self.spark.finished:
            delta = self.pos - self.target_pos
            self.angle = math.atan2(delta.y, delta.x)

            self.spark_flag = not self.spark_flag
            self.spark.reset()

            vel = -(self.target_pos - self.start_pos) / self.total_time + vec(0, self.v * math.sin(self.theta) - GRAV * self.time) * self.height_mult
            angle = math.atan2(vel.y, vel.x)# + math.pi

            colours = [
                (25, 12, 36),
                (235, 101, 70),
                (191, 60, 97)
            ]
            Grenade_Spark(
                self.game, 
                [self.game.all_sprites, self.game.particles], 
                self.pos, 
                random.uniform(3, 5), 
                angle + (math.pi/32) * (-1 if self.spark_flag else 1),
                speed=random.uniform(5, 5),
                colour=random.choice(colours),
                shadow_height=-vec(0, self.dh),
                shadow_col=(0, 0, 0, 0),
                shadow_angle = self.angle + (math.pi/32) * (-1 if self.spark_flag else 1)
            )
            colours = [
                (253, 252, 211),
                (239, 209, 113),
            ]
            Grenade_Spark(
                self.game, 
                [self.game.all_sprites, self.game.particles], 
                self.pos, 
                random.uniform(3, 5), 
                angle - (math.pi/32) * (-1 if self.spark_flag else 1),
                speed=random.uniform(5, 5),
                colour=random.choice(colours),
                shadow_height=-vec(0, self.dh),
                shadow_col=(0, 0, 0, 0),
                shadow_angle = self.angle + (math.pi/32) * (-1 if self.spark_flag else 1)
            )

        self.draw()

    def draw(self):
        radius = 8 # (((5 * self.dh) / self.max_height) + 4)

        y = radius / 2
        shadow = pygame.Surface((y*4, y), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0), [0, 0, y*4, y])
        shadow.set_alpha(128)
        self.screen.blit(shadow, shadow.get_rect(center=(self.pos + vec(0, radius) - self.game.offset)))

        pygame.draw.circle(self.screen, (235, 101, 70), self.pos - self.game.offset - vec(0, self.dh), radius)
        pygame.draw.circle(self.screen, (178, 50, 22), self.pos - self.game.offset - vec(0, self.dh), radius, 3)


class GrenadeExplosion(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)