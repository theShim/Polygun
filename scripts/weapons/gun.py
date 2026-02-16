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
from scripts.particles.bullet_casing import Bullet_Casing, Shotgun_Casing
from scripts.projectiles.bullet import Bullet

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

class Gun(pygame.sprite.Sprite):
    TYPE = "ranged"
    
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.bullet_spread = math.pi/80 #+- spread angle in radians
        self.shoot_timer = Timer(10, 1)
        self.shake_duration = 0
        self.shake_intesity = 0

    def play_sound(self):
        self.game.music_player.play("gunshot", pool="sfx", loop=False)

    def spawn_casing(self, mouseAngle):
        Bullet_Casing(self.game, [self.game.all_sprites, self.game.particles], self.game.player.pos, mouseAngle + math.pi + random.uniform(-self.bullet_spread, self.bullet_spread) * 20, -vec(0, self.game.player.jump_height))

    def shoot(self, mouseAngle):
        spread = random.uniform(-self.bullet_spread, self.bullet_spread)
        if "double_rounds" in self.game.player.item_manager.current_items:
            n1 = vec(-math.sin(mouseAngle), math.cos(mouseAngle)) * 8
            n2 = vec(math.sin(mouseAngle), -math.cos(mouseAngle)) * 8
            Bullet(self.game, [self.game.all_sprites], self.game.player.pos + n1, mouseAngle + spread, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player)
            Bullet(self.game, [self.game.all_sprites], self.game.player.pos + n2, mouseAngle + spread, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player)
        else:
            Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle + spread, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player)

    def update(self):
        self.play_sound()

        self.game.screen_shake.start(self.shake_duration, self.shake_intesity)
        
        mousePos = self.game.mousePos + vec(0, self.game.player.jump_height)
        mouseAngle = math.atan2(mousePos.y - self.game.player.pos.y + self.game.offset.y, mousePos.x - self.game.player.pos.x + self.game.offset.x)

        self.shoot(mouseAngle)
        self.spawn_casing(mouseAngle)
        
        for i in range(random.randint(3, 3)):
            Spark(
                self.game, 
                [self.game.all_sprites, self.game.particles], 
                self.game.player.pos, 
                (self.game.player.size + random.uniform(-4, 12)) / 6, 
                mouseAngle + random.uniform(-math.pi/5 * 1.1, math.pi/5 * 1.1),
                speed=random.uniform(2, 2),
                shadow_height=-vec(0, self.game.player.jump_height),
                shadow_col=(0, 0, 0, 0)
            )


class Rifle(Gun):
    def __init__(self, game, groups):
        super().__init__(game, groups)

class Shotgun(Gun):
    def __init__(self, game, groups):
        super().__init__(game, groups)
        self.shoot_timer = Timer(FPS * 0.8, 1)
        self.cone = math.pi / 6
        self.shake_duration = 5
        self.shake_intesity = 4
        
    def spawn_casing(self, mouseAngle):
        Shotgun_Casing(self.game, [self.game.all_sprites, self.game.particles], self.game.player.pos, mouseAngle + math.pi + random.uniform(-self.bullet_spread, self.bullet_spread) * 20, -vec(0, self.game.player.jump_height))

    def shoot(self, mouseAngle):
        self.game.player.vel += vec(math.cos(mouseAngle), math.sin(mouseAngle)) * -3
        Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle - self.cone, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player, speed=16, lifetime=FPS * 0.2, damage=5)
        Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle - self.cone/2, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player, speed=16, lifetime=FPS * 0.2, damage=5)
        Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player, speed=16, lifetime=FPS * 0.2, damage=7)
        Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle + self.cone/2, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player, speed=16, lifetime=FPS * 0.2, damage=5)
        Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle + self.cone, (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player, speed=16, lifetime=FPS * 0.2, damage=5)

class Pistol(Gun):
    def __init__(self, game, groups):
        super().__init__(game, groups)
        self.shoot_timer = Timer(FPS * 0.5, 1)
        self.bullet_spread = math.pi/160 #+- spread angle in radians

    def shoot(self, mouseAngle):
        Bullet(self.game, [self.game.all_sprites], self.game.player.pos, mouseAngle + random.uniform(-self.bullet_spread, self.bullet_spread), (0, 255 - 90, 247 - 90), shadow_height=-vec(0, self.game.player.jump_height), owner=self.game.player, speed=18, lifetime=FPS * 0.6, damage=8)


Gun.Rifle = Rifle
Gun.Shotgun = Shotgun
Gun.Pistol = Pistol