import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random
import json
import numpy as np

from scripts.entities.silver import Silver
from scripts.particles.sparks import Spark
from scripts.entities.remains import Remains
from scripts.projectiles.bullet import Bullet
from scripts.projectiles.grenade import Grenade
from scripts.projectiles.shockwave import Shockwave

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
        self.shoot_timer = Timer(60, 1)
        for i in range(random.randint(0, 60)):
            self.shoot_timer.update()

        #damage indicator stuff
        self.health = 20
        self.knockback_vel = vec()
        self.hurt = False
        self.damage_timer = Timer(4, 1)

        #death
        self.dying = False

        self.shader = self.game.shader_handler.SHADERS["grayscale"]


        #############################################################################

    def knockback(self, vel):
        self.knockback_vel = vel

    def take_hit(self, damage=0):
        self.hurt = True
        self.damage_timer.reset()

        self.health -= damage
        if self.health <= 0:
            self.trigger_death()

    def trigger_death(self):
        self.dying = True

    def death(self):
        for i in range(random.randint(3, 5)):
            Spark(
                self.game, 
                [self.game.all_sprites, self.game.particles], 
                self.pos - vec(0, self.height), 
                (12 + random.uniform(-4, 12)) / 6, 
                random.uniform(0, 2 * math.pi),
                speed=random.uniform(2, 3),
                colour=(255, 0, 55),
                shadow_col=(0, 0, 0, 0),
                grav=True,
            )
            Remains(
                self.game,
                [self.game.all_sprites],
                self.pos,
                (255, 0, 55),
                self.height
            )

        for i in range(random.randint(1, 4)):
            Silver(self.game, [self.game.all_sprites, self.game.entities], self.pos, -vec(0, self.height))
            
        return self.kill()

        #############################################################################

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

        for enemy in self.game.enemies:
            if enemy != self:
                if (vel := (self.pos - enemy.pos)).magnitude() < self.size * 1.75:
                    self.knockback(vel * 12)
                    enemy.knockback(vel * -1 * 12)
                    

    def move(self):
        self.acc = vec()

        if not self.dying:
            self.vel = (self.game.player.pos - self.pos).normalize() * self.run_speed
        else:
            self.vel = vec()

        self.pos.x += self.vel.x * self.game.dt
        self.pos.x += self.knockback_vel.x * self.game.dt
        self.collisions("horizontal")

        self.pos.y += self.vel.y * self.game.dt
        self.pos.y += self.knockback_vel.y * self.game.dt
        self.collisions("vertical")

        self.knockback_vel = self.knockback_vel.lerp(vec(), 0.3)

        if not self.dying:
            self.change_direction()
        # self.apply_forces()

    def change_direction(self):
        targetPos = self.pos + self.vel

        delta = targetPos - self.pos
        self.angle = math.atan2(delta.y, delta.x)

        #############################################################################

    def update(self):
        self.move()

        if not (self.hurt or self.dying):
            self.shoot_timer.update()
            if self.shoot_timer.finished:
                Bullet(self.game, [self.game.all_sprites], self.pos, self.angle + random.uniform(-self.bullet_spread, self.bullet_spread), (255 - 55, 0, 55 - 55), speed=10, shadow_height=-vec(0, 0), scale_mod=0.75, owner=self)
                self.shoot_timer.reset()
                self.game.music_player.play("gunshot", pool="sfx", loop=False)

        if self.hurt:
            self.damage_timer.update()
            if self.damage_timer.finished:
                self.hurt = False

        if self.dying:
            self.points *= 0.9
            self.angle += math.radians(20)
            
            if self.points[0, 0] < 0.25:
                self.death()
                return

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

    ##############################################################################################

class Hexagon(Enemy):                               #plants bombs on the floor
    def __init__(self, game, groups, pos):
        super().__init__(game, groups, pos)

        self.size = 16
        angles = np.linspace(0, 2 * math.pi, 7)
        self.points = np.column_stack((np.cos(angles), np.sin(angles))) * self.size
        self.pos = vec(pos)

        self.height = 50
        self.attack_cycle_timer = Timer(FPS * 5, 1)
        self.chase_timer = Timer(10, 1)
        self.attacking = True
        self.attack_t = 0
        self.attack_duration = 3.2
        self.attack_delay = Timer(30, 1)
        self.spawned_blackhole = False
        
        for i in range(random.randint(0, FPS * 5)):
            self.attack_cycle_timer.update()

        #############################################################################
                    
    def move(self):
        
        if not self.chase_timer.finished and self.attack_cycle_timer.finished:
            self.vel += (v := (self.game.player.pos - self.pos)).normalize() * min(300, v.magnitude())
        self.vel *= 0.9

        self.pos.x += self.vel.x * self.game.dt
        self.pos.x += self.knockback_vel.x * self.game.dt
        self.collisions("horizontal")

        self.pos.y += self.vel.y * self.game.dt
        self.pos.y += self.knockback_vel.y * self.game.dt
        self.collisions("vertical")

        self.knockback_vel = self.knockback_vel.lerp(vec(), 0.3)

        if not self.dying:
            self.change_direction()

    def change_direction(self):
        self.angle += math.radians(5)

        #############################################################################

    def update(self):
        self.attack_cycle_timer.update()
        if self.attack_cycle_timer.finished:
            self.chase_timer.update()
            if self.chase_timer.finished:
                self.angle += math.radians(5)
                self.attack_delay.update()
                if self.attack_delay.finished:
                    self.attack_t += self.game.dt * 5
                    self.height = (50 / ((self.attack_duration / 2) ** 4)) * ((self.attack_t - (self.attack_duration / 2)) ** 4)
                    if self.attack_t >= self.attack_duration / 2 and not self.spawned_blackhole:
                        # Grenade(self.game, [self.game.all_sprites], self.pos, self.pos)
                        # self.take_hit()
                        Shockwave(self.game, [self.game.all_sprites], self.pos)
                    if self.attack_t >= self.attack_duration:
                        self.attack_t = 0
                        self.chase_timer.reset()
                        self.attack_cycle_timer.reset()
                        self.attack_delay.reset()
                        self.height = 50

        self.move()

        if self.hurt:
            self.damage_timer.update()
            if self.damage_timer.finished:
                self.hurt = False

        if self.dying:
            self.points *= 0.9
            self.angle += math.radians(20)
            
            if self.points[0, 0] < 0.25:
                for i in range(random.randint(3, 5)):
                    Spark(
                        self.game, 
                        [self.game.all_sprites, self.game.particles], 
                        self.pos - vec(0, self.height), 
                        (12 + random.uniform(-4, 12)) / 6, 
                        random.uniform(0, 2 * math.pi),
                        speed=random.uniform(2, 3),
                        colour=(134, 0, 196),
                        shadow_col=(0, 0, 0, 0),
                        grav=True,
                    )
                    Remains(
                        self.game,
                        [self.game.all_sprites, self.game.particles],
                        self.pos,
                        (134, 0, 196),
                        self.height
                    )
                for i in range(random.randint(1, 4)):
                    Silver(self.game, [self.game.all_sprites, self.game.entities], self.pos, -vec(0, self.height))
                return self.kill()

        self.draw()

    def draw(self):
        buffer_scale = 8
        temp_surf = pygame.Surface((self.size * buffer_scale, self.size * buffer_scale * 2), pygame.SRCALPHA)
        center = vec(self.size * buffer_scale / 2, self.size * buffer_scale)

        points = self.points.copy()
        if self.acc.magnitude():
            points[:, 1] *= 0.6
        points = rot_2d(points, self.angle)
        jump_scale = max(0.25, (self.height / 50))
        
        pygame.draw.polygon(temp_surf, (0, 0, 0, 150), (points * 1.25 * jump_scale) + center + vec(0, 4))
        pygame.draw.polygon(temp_surf, (66, 0, 83) if not self.hurt else (255, 255, 255), points * 1.4 + center - vec(0, self.height))
        pygame.draw.polygon(temp_surf, (134, 0, 196) if not self.hurt else (255, 255, 255), points + center - vec(0, self.height))

        rect = temp_surf.get_rect(center=self.pos - self.game.offset)
        self.screen.blit(temp_surf, rect)

class Pentagon(Enemy):                              #throws grenades
    def __init__(self, game, groups, pos):
        super().__init__(game, groups, pos)

        self.size = 14
        angles = np.linspace(0, 2 * math.pi, 6)
        self.points = np.column_stack((np.cos(angles), np.sin(angles))) * self.size
        self.pos = vec(pos)

        self.attacking = False
        self.grenaded = False
        self.range = 400
        self.attack_timer = Timer(FPS, 1)
        self.cooldown = Timer(FPS * 2, 1)

        for i in range(random.randint(0, FPS)):
            self.attack_timer.update()

        #############################################################################
                    
    def move(self):
        
        if not self.dying:
            if not self.attacking:
                self.vel = (self.game.player.pos - self.pos).normalize() * self.run_speed
            else:
                self.vel = vec()
        else:
            self.vel = vec()

        self.pos.x += self.vel.x * self.game.dt
        self.pos.x += self.knockback_vel.x * self.game.dt
        self.collisions("horizontal")

        self.pos.y += self.vel.y * self.game.dt
        self.pos.y += self.knockback_vel.y * self.game.dt
        self.collisions("vertical")

        self.knockback_vel = self.knockback_vel.lerp(vec(), 0.3)

        if not self.dying:
            self.change_direction()

        #############################################################################

    def update(self):
        self.move()

        if (self.game.player.pos - self.pos).magnitude() < self.range:
            self.attacking = True

        if self.attacking:
            if not self.grenaded:
                Grenade(self.game, [self.game.all_sprites], self.pos, self.game.player.pos)
                self.grenaded = True

            self.attack_timer.update()
            if self.attack_timer.finished:
                self.cooldown.update()
                if self.cooldown.finished:
                    self.attacking = False
                    self.grenaded = False
                    self.attack_timer.reset()
                    self.cooldown.reset()

        if self.hurt:
            self.damage_timer.update()
            if self.damage_timer.finished:
                self.hurt = False

        if self.dying:
            self.points *= 0.9
            self.angle += math.radians(20)
            
            if self.points[0, 0] < 0.25:
                for i in range(random.randint(3, 5)):
                    Spark(
                        self.game, 
                        [self.game.all_sprites, self.game.particles], 
                        self.pos - vec(0, self.height), 
                        (12 + random.uniform(-4, 12)) / 6, 
                        random.uniform(0, 2 * math.pi),
                        speed=random.uniform(2, 3),
                        colour=(235, 101, 70),
                        shadow_col=(0, 0, 0, 0),
                        grav=True,
                    )
                    Remains(
                        self.game,
                        [self.game.all_sprites, self.game.particles],
                        self.pos,
                        (235, 101, 70),
                        self.height
                    )
                for i in range(random.randint(1, 4)):
                    Silver(self.game, [self.game.all_sprites, self.game.entities], self.pos, -vec(0, self.height))
                return self.kill()

        self.draw()

    def draw(self):
        buffer_scale = 8
        temp_surf = pygame.Surface((self.size * buffer_scale, self.size * buffer_scale), pygame.SRCALPHA)
        center = vec(self.size * buffer_scale / 2, self.size * buffer_scale / 2)

        points = self.points.copy()
        if self.acc.magnitude():
            points[:, 1] *= 0.6
        points = rot_2d(points, self.angle)
        jump_scale = max(0.25, (self.height / 50))
        
        pygame.draw.polygon(self.screen, (0, 0, 0, 0), (-self.game.offset + points * 1.25) + self.pos + vec(0, 4))
        pygame.draw.polygon(temp_surf, (198, 70, 42) if not self.hurt else (255, 255, 255), points * 1.4 + center - vec(0, self.height))
        pygame.draw.polygon(temp_surf, (235, 101, 70) if not self.hurt else (255, 255, 255), points + center - vec(0, self.height))

        rect = temp_surf.get_rect(center=self.pos - self.game.offset)
        self.screen.blit(temp_surf, rect)

        
Enemy.Hexagon = Hexagon
Enemy.Pentagon = Pentagon

    ##############################################################################################

class EnemySpawnData:
    def __init__(self, enemy_class, count):
        self.enemy_class = enemy_class
        self.count = count