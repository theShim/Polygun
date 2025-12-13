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

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

class Player(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.size = size = 16
        self.points = np.array([
            [-size/2, -size/2],
            [size/2, -size/2],
            [size/2, size/2],
            [-size/2, size/2]
        ])
        self.pos = vec(WIDTH/2 - size/2, HEIGHT/2 - size/2)

        self.vel = vec()
        self.old_vel = vec()
        self.acc = vec()
        self.run_speed = 50
        self.dash_speed = 30
        self.angle = 0
        
        #jumping
        self.jump_vel = 50 #the velocity applied upwards
        self.jump_height = 0 #the pseudo height to give the effect of jumping rather than just moving up
        self.max_jump_height = (self.jump_vel ** 2) / (2 * GRAV) #projectile motion equation
        self.jump_time = 0 #the current moment in time of the jump
        self.jumping = False #just a boolean of whether the play is jumping or not

        self.shader = self.game.shader_handler.SHADERS["grayscale"]

        # self.boost_timer = Timer()

    def move(self):
        self.acc = vec()
        keys = pygame.key.get_pressed()

        self.directional_inputs(keys)
        self.dash()
        self.jump(keys)
        self.apply_forces()

    def directional_inputs(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acc.x = -1 * self.run_speed
            if self.vel.x > 0: self.vel.x = 0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acc.x = 1 * self.run_speed
            if self.vel.x < 0: self.vel.x = 0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.acc.y = 1 * self.run_speed
            if self.vel.y < 0: self.vel.y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.acc.y = -1 * self.run_speed
            if self.vel.y > 0: self.vel.y = 0

        self.acc.clamp_magnitude_ip(self.run_speed)
        self.change_direction()

    def jump(self, keys):
        if keys[pygame.K_SPACE] and not self.jumping:
            self.jumping = True
            self.jump_time = 0


        #the psuedo height stuff, just projectile motion
        if self.jumping:
            self.jump_time += self.game.dt * 10
            self.jump_height = ((self.jump_vel * self.jump_time) - 
                                (0.5 * GRAV * (self.jump_time ** 2)))
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jumping = 0

    def dash(self):
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_LCTRL]:
            if self.vel.magnitude():
                self.vel = self.vel.normalize() * self.dash_speed

    def apply_forces(self):
        #actually applying acceleration to the player velocity
        self.vel.x += self.acc.x * self.game.dt
        self.vel.y += self.acc.y * self.game.dt

        self.vel *= FRIC #slowing them down by applying friction
        if -0.25 < self.vel.x < 0.25: #bounds to prevent sliding bug
            self.vel.x = 0
        if -0.25 < self.vel.y < 0.25:
            self.vel.y = 0
            
        self.pos.y += self.vel.y
        self.collisions("vertical")
        self.pos.x += self.vel.x
        self.collisions("horizontal")

        if self.vel.magnitude() > 10:
            col = pygame.Color(237, 12, 0).lerp((255, 183, 0), random.uniform(0, 1))
            Spark(
                self.game, 
                [self.game.all_sprites, self.game.particles], 
                np.mean([self.points[0], self.points[1]], axis=1) + self.pos + 8 * vec(random.uniform(-1, 1), random.uniform(-1, 1)) + vec(4, 4), 
                (self.size + random.uniform(-4, 8)) / 6, 
                self.angle + math.pi + random.uniform(-1, 1) / 4,
                speed=random.uniform(2, 4),
                colour=col,
                shadow_height=-vec(0, self.jump_height),
                shadow_col=(0, 0, 0, 0)
            )
            Spark(
                self.game, 
                [self.game.all_sprites, self.game.particles], 
                np.mean([self.points[0], self.points[1]], axis=1) + self.pos + 8 * vec(random.uniform(-1, 1), random.uniform(-1, 1)) + vec(4, 4), 
                (self.size + random.uniform(-4, 8)) / 6, 
                self.angle + math.pi + random.uniform(-1, 1) / 4,
                speed=random.uniform(2, 4),
                colour=col,
                shadow_height=-vec(0, self.jump_height),
                shadow_col=(0, 0, 0, 0)
            )

    def change_direction(self):
        # get raw mouse pos (window coords, affected by scaling)
        # mousePos = pygame.mouse.get_pos()

        # # scale back into internal surface resolution
        # window_size = pygame.display.get_window_size()  # actual window size (after scaling)
        # scale_x = WIDTH / window_size[0]
        # scale_y = HEIGHT / window_size[1]
        # mousePos = vec(mousePos[0] * scale_x, mousePos[1] * scale_y)

        # targetPos = (mousePos) + self.game.offset
        if not self.acc.magnitude():
            return
        
        targetPos = self.pos + self.vel

        delta = targetPos - self.pos
        self.angle = math.atan2(delta.y, delta.x)

    def collisions(self, direction):
        for room in self.game.state_loader.current_state.levels[self.game.state_loader.current_state.current_level_index].rooms.values():
            flag = False
            for tile in room.tilemap.collideables(self.game.offset):
                pygame.draw.line(self.screen, (255, 255, 0), self.pos - self.game.offset, tile.rect.center - self.game.offset, 2)
                pygame.draw.rect(self.screen, (255, 0, 0), [tile.rect.x - self.game.offset.x, tile.rect.y - self.game.offset.y, *tile.rect.size], 2)
                # if self.pos.distance_to(tile.rect.center) < self.size * 3:
                    # pygame.draw.line(self.screen, (0, 255, 0), self.pos - self.game.offset, tile.rect.center - self.game.offset, 2)
                if direction == "vertical":
                    if self.pos.y - self.size / 2 < tile.rect.bottom and self.vel.y < 0:
                        self.pos.y = tile.rect.bottom + self.size / 2
                        # flag = True
                    elif self.pos.y + self.size / 2 > tile.rect.top and self.vel.y > 0:
                        self.pos.y = tile.rect.top - self.size / 2
                        # flag = True

                elif direction == "horizontal":
                    if self.pos.x - self.size / 2 < tile.rect.right and self.vel.x < 0:
                        self.pos.x = tile.rect.right + self.size / 2
                        # flag = True
                    elif self.pos.x + self.size / 2 > tile.rect.left and self.vel.x > 0:
                        self.pos.x = tile.rect.left - self.size / 2
                        # flag = True
            if flag:
                break

    def update(self):
        self.move()
        # self.draw()

        self.collisions("")

        self.shader_draw()

    def draw(self):
        jump_scale = max(0.25, 1 -(self.jump_height / self.max_jump_height))

        points = self.points.copy()
        if self.acc.magnitude():
            points[:, 1] *= 0.6
        points = rot_2d(points, self.angle)


        pygame.draw.polygon(self.screen, (0, 0, 0, 0), (points * (jump_scale * 1.25)) + self.pos + vec(0, 4))
        pygame.draw.polygon(self.screen, (0, 114, 110), points * 1.25 + self.pos - vec(0, self.jump_height))
        pygame.draw.polygon(self.screen, (0, 255, 247), points + self.pos - vec(0, self.jump_height))

    def shader_draw(self):
        buffer_scale = 8
        temp_surf = pygame.Surface((self.size * buffer_scale, self.size * buffer_scale), pygame.SRCALPHA)
        center = vec(self.size * buffer_scale / 2, self.size * buffer_scale / 2)

        points = self.points.copy()
        if self.acc.magnitude():
            points[:, 1] *= 0.6
        points = rot_2d(points, self.angle)
        jump_scale = max(0.25, 1 -(self.jump_height / self.max_jump_height))
        
        pygame.draw.polygon(self.screen, (0, 0, 0, 0), (-self.game.offset + points * (jump_scale * 1.25)) + self.pos + vec(0, 4 * jump_scale))
        pygame.draw.polygon(temp_surf, (0, 114, 110), points * 1.25 + center - vec(0, self.jump_height))
        pygame.draw.polygon(temp_surf, (0, 255, 247), points + center - vec(0, self.jump_height))

        # Apply shader only to that region
        # temp_surf = self.game.shader_handler.SHADERS["invert"].apply(temp_surf)

        # Blit result to the main screen
        # pygame.draw.circle(temp_surf, (11, 164, 29), (self.size / 2, self.size / 2), self.size/2)
        # pygame.draw.circle(temp_surf, (242, 34, 34), (self.size / 2, self.size / 2), self.size/2 * 0.95)
        rect = temp_surf.get_rect(center=self.pos - self.game.offset)
        self.screen.blit(temp_surf, rect)