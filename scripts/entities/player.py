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
from scripts.particles.bullet_casing import Bullet_Casing
from scripts.projectiles.bullet import Bullet

from scripts.weapons.gun import Gun
from scripts.weapons.spikeball import Spikeball

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

    ##############################################################################################

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

        #movement
        self.vel = vec()
        self.old_vel = vec()
        self.acc = vec()
        self.run_speed = 50
        self.dash_speed = 30
        self.angle = 0
        
        #shooting
        # self.primary = Gun.Rifle(self.game, [])
        # self.primary.shoot_timer.t = self.primary.shoot_timer.end #remove the cooldon for the first attack
        self.primary = Spikeball(self.game, [], self.pos)
        self.secondary = None
        
        #jumping
        self.jump_vel = 50 #the velocity applied upwards
        self.jump_height = 0 #the pseudo height to give the effect of jumping rather than just moving up
        self.max_jump_height = (self.jump_vel ** 2) / (2 * GRAV) #projectile motion equation
        self.jump_time = 0 #the current moment in time of the jump
        self.jumping = False #just a boolean of whether the play is jumping or not

        self.max_health = 200
        self.health = self.max_health
        self.max_energy = 100
        self.energy = 0
        self.energy_refill_timer = Timer(FPS, 1)
        self.silver = 0 #silver cuz bullet casing looked too similar to gold or yellow coins
        self.pickup_radius = 100 #remains and money

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

    def mouse_inputs(self):
        mouse = pygame.mouse.get_pressed()

        if self.primary.TYPE == "ranged":
            self.primary.shoot_timer.update()
            if mouse[0] and (pygame.key.get_pressed()[pygame.K_LSHIFT] or self.primary.shoot_timer.finished):
                self.primary.shoot_timer.reset()
                self.primary.update()
        elif self.primary.TYPE == "melee":
            self.primary.update()

        else:
            raise BaseException("vveapon error")


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

        else:
            if self.jump_height > 0:
                self.jump_height -= GRAV / 10
            if self.jump_height <= 0:
                self.jump_height = 0

    def dash(self):
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_LCTRL]:
            if self.vel.magnitude() and self.energy >= 30:
                self.vel = self.vel.normalize() * self.dash_speed
                self.energy -= 30

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
        if not self.acc.magnitude():
            return
        
        targetPos = self.pos + self.vel
        delta = targetPos - self.pos
        self.angle = math.atan2(delta.y, delta.x)

    def collisions(self, direction):
        if self.game.state_loader.transitioning: return
        room = self.game.state_loader.current_state.get_current_room()

        #creating a rectangular hitbox regardless of rotation, centred at the player position
        hitbox = pygame.Rect(self.pos.x - self.size/2, self.pos.y - self.size/2, self.size, self.size)
        for tile in room.tilemap.collideables(self.game.offset):
            if tile.hitbox.colliderect(hitbox): #rect collision instead of point

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

    def update(self):
        self.move()
        self.mouse_inputs()

        self.energy_refill_timer.update()
        if self.energy_refill_timer.finished:
            self.energy_refill_timer.reset()
            self.energy += 0.5
        self.energy = min(self.energy, self.max_energy)

        # if pygame.key.get_just_pressed()[pygame.K_SPACE]:
        #     self.energy = 10

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
        
        pygame.draw.polygon(self.screen, (0, 0, 0), (-self.game.offset + points * (jump_scale * 1.25)) + self.pos + vec(0, 4 * jump_scale))
        pygame.draw.polygon(temp_surf, (0, 114, 110), points * 1.25 + center - vec(0, self.jump_height))
        pygame.draw.polygon(temp_surf, (0, 255, 247), points + center - vec(0, self.jump_height))

        # Apply shader only to that region
        # temp_surf = self.game.shader_handler.SHADERS["invert"].apply(temp_surf)

        rect = temp_surf.get_rect(center=self.pos - self.game.offset)


        mousePos = self.game.mousePos
        delta = mousePos - (self.pos - self.game.offset)
        angle = math.atan2(delta.y, delta.x)
        pointer_first = angle < 0
        
        #the lil arrow indicator. annoyed there isnt a better way to do differentiate if its infront of behind
        if pointer_first:
            pos = -self.game.offset + self.pos + vec(math.cos(angle), math.sin(angle)) * self.size * 1.5
            points_ = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (7) - vec(0, self.jump_height)
                for a in range(0, 360, 120)
            ]
            shadow_points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (9 * jump_scale) + vec(0, 4)
                for a in range(0, 360, 120)
            ]
            pygame.draw.polygon(self.screen, (0, 0, 0), shadow_points)
            pygame.draw.polygon(self.screen, (100, 100, 100), points_)

        self.screen.blit(temp_surf, rect)

        # bright_image = temp_surf.copy()
        # bright_image.fill(
        #     (255, 200, 80),
        #     special_flags=pygame.BLEND_RGB_ADD
        # )
        # self.game.emissive_surf.blit(bright_image, rect)

        # pygame.draw.polygon(self.game.emissive_surf, (0, 0, 0, 0), (points * (jump_scale * 1.25)) + self.pos + vec(0, 4) - self.game.offset)
        # pygame.draw.polygon(self.game.emissive_surf, (0, 114, 110), points * 1.25 + self.pos - vec(0, self.jump_height) - self.game.offset)
        pygame.draw.polygon(self.game.emissive_surf, (100 - 100, 255 - 100, 255 - 100), points * 1.75 + self.pos - vec(0, self.jump_height) - self.game.offset,)

        if not pointer_first:
            pos = -self.game.offset + self.pos + vec(math.cos(angle), math.sin(angle)) * self.size * 1.5
            points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (7) - vec(0, self.jump_height)
                for a in range(0, 360, 120)
            ]
            shadow_points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (9 * jump_scale) + vec(0, 4)
                for a in range(0, 360, 120)
            ]
            pygame.draw.polygon(self.screen, (0, 0, 0), shadow_points)
            pygame.draw.polygon(self.screen, (100, 100, 100), points)
