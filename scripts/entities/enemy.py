import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random
import json
import numpy as np

from scripts.particles.sparks import Spark
from scripts.projectiles.bullet import Bullet

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

    ##############################################################################################

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.size = 12
        angles = np.linspace(0, 2 * math.pi, 4)
        self.points = np.column_stack((np.cos(angles), np.sin(angles))) * self.size
        self.pos = vec(pos)

        #movement
        self.vel = vec()
        self.old_vel = vec()
        self.acc = vec()
        self.run_speed = 100
        self.dash_speed = 30
        self.angle = 0
        self.height = 0

        #shooting
        self.bullet_spread = math.pi/20 #+- spread angle in radians
        self.shoot_timer = Timer(10, 1)

        #damage indicator stuff
        self.knockback_vel = vec()
        self.hurt = False
        self.damage_timer = Timer(4, 1)

        self.shader = self.game.shader_handler.SHADERS["grayscale"]


        #############################################################################

    def knockback(self, vel):
        self.knockback_vel = vel

    def take_hit(self, damage=0):
        self.hurt = True
        self.damage_timer.reset()

    def collisions(self, direction):
        room = self.game.state_loader.current_state.get_current_room(self.pos)

        for tile in room.tilemap.collideables(self.game.offset):
            if tile.hitbox.collidepoint(self.pos):
                if direction == "vertical":
                    if self.pos.y - self.size / 2 < tile.hitbox.bottom and self.vel.y < 0:
                        self.pos.y = tile.hitbox.bottom + self.size / 2
                        self.vel.y = 0
                    elif self.pos.y + self.size / 2 > tile.hitbox.top and self.vel.y > 0:
                        self.pos.y = tile.hitbox.top - self.size / 2
                        self.vel.y = 0

                elif direction == "horizontal":
                    if self.pos.x - self.size / 2 < tile.hitbox.right and self.vel.x < 0:
                        self.pos.x = tile.hitbox.right + self.size / 2
                        self.vel.x = 0
                    elif self.pos.x + self.size / 2 > tile.hitbox.left and self.vel.x > 0:
                        self.pos.x = tile.hitbox.left - self.size / 2
                        self.vel.x = 0

    def move(self):
        self.acc = vec()
        self.vel = (self.game.player.pos - self.pos).normalize() * self.run_speed

        self.pos.x += self.vel.x * self.game.dt
        self.pos.x += self.knockback_vel.x * self.game.dt
        self.collisions("horizontal")

        self.pos.y += self.vel.y * self.game.dt
        self.pos.y += self.knockback_vel.y * self.game.dt
        self.collisions("vertical")

        self.knockback_vel = self.knockback_vel.lerp(vec(), 0.3)

        self.change_direction()
        # self.apply_forces()

    def change_direction(self):
        targetPos = self.pos + self.vel

        delta = targetPos - self.pos
        self.angle = math.atan2(delta.y, delta.x)

        #############################################################################

    def update(self):
        self.move()

        if self.hurt:
            self.damage_timer.update()
            if self.damage_timer.finished:
                self.hurt = False

        self.draw()

    def draw(self):
        buffer_scale = 8
        temp_surf = pygame.Surface((self.size * buffer_scale, self.size * buffer_scale), pygame.SRCALPHA)
        center = vec(self.size * buffer_scale / 2, self.size * buffer_scale / 2)

        points = self.points.copy()
        if self.acc.magnitude():
            points[:, 1] *= 0.6
        points = rot_2d(points, self.angle)
        
        pygame.draw.polygon(self.screen, (0, 0, 0, 0), (-self.game.offset + points * 1.25) + self.pos + vec(0, 4))
        pygame.draw.polygon(temp_surf, (114, 0, 2) if not self.hurt else (255, 255, 255), points * 1.3 + center)
        pygame.draw.polygon(temp_surf, (255, 0, 55) if not self.hurt else (255, 255, 255), points + center)

        # Apply shader only to that region
        # temp_surf = self.game.shader_handler.SHADERS["invert"].apply(temp_surf)

        # Blit result to the main screen
        rect = temp_surf.get_rect(center=self.pos - self.game.offset)
        self.screen.blit(temp_surf, rect)
