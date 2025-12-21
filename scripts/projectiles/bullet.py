import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random

from scripts.particles.sparks import Spark

from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp

    ##############################################################################################

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, angle, col, shadow_height = None):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        
        self.pos = vec(pos)
        self.angle = angle
        self.vel = vec(math.cos(self.angle), math.sin(self.angle))
        self.speed = 14
        self.col = col
        self.scale = 4
        self.shadow_height = shadow_height

        self.w = vec(math.cos(self.angle - math.pi / 2), math.sin(self.angle - math.pi / 2)) * self.scale
        
        for i in range(1):
            self.move()

    def move(self):
        self.pos += self.vel * self.speed

    def collisions(self):
        for room in self.game.state_loader.current_state.levels[self.game.state_loader.current_state.current_level_index].rooms.values():
            for tile in room.tilemap.collideables(self.game.offset):
                if tile.hitbox.collidepoint(self.pos):
                    for i in range(random.randint(3, 3)):
                        Spark(
                            self.game, 
                            [self.game.all_sprites, self.game.particles], 
                            self.pos, 
                            (self.scale + random.uniform(-4, 12)) / 3, 
                            self.angle + random.uniform(-math.pi/5 * 1.1, math.pi/5 * 1.1) + math.pi,
                            speed=random.uniform(2, 2),
                            shadow_height=self.shadow_height,
                            shadow_col=(0, 0, 0, 0)
                        )
                    return self.kill()
                
        for enemy in self.game.enemies:
            if enemy.pos.distance_to(self.pos) < enemy.size and abs(enemy.height - self.shadow_height.y) < 2:
                enemy.knockback(self.vel * self.speed * 40)
                enemy.take_hit()
                for i in range(random.randint(3, 3)):
                    Spark(
                        self.game, 
                        [self.game.all_sprites, self.game.particles], 
                        self.pos, 
                        (self.scale + random.uniform(-4, 12)) / 3, 
                        self.angle + random.uniform(-math.pi/5 * 1.1, math.pi/5 * 1.1) + math.pi,
                        speed=random.uniform(2, 2),
                        shadow_height=self.shadow_height,
                        shadow_col=(0, 0, 0, 0)
                    )
                return self.kill()
            
        if not pygame.Rect(0, 0, *SIZE).collidepoint(self.pos - self.game.offset):
            return self.kill()
        
    def player_collisions(self):
        pass

    def update(self):
        self.move()
        self.collisions()
        self.player_collisions()
        self.draw()

    def draw(self):
        points = [
            self.pos + self.w + 2 * self.vel * self.scale - self.game.offset,
            self.pos + self.w - 2 * self.vel * self.scale - self.game.offset,
            self.pos - self.w - 2 * self.vel * self.scale - self.game.offset,
            self.pos - self.w + 2 * self.vel * self.scale - self.game.offset,
        ]
        
        min_x = min(p.x for p in points) - 10
        min_y = min(p.y for p in points) - 10
        max_x = max(p.x for p in points) + 10
        max_y = max(p.y for p in points) + 10
        width, height = max_x - min_x, max_y - min_y
        
        bullet_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        adjusted_points = [(p.x - min_x, p.y - min_y) for p in points]
        shadow_points = [(p[0], p[1] + 10) for p in adjusted_points]
        
        pygame.draw.polygon(shadow_surface, (0, 0, 0, 100), shadow_points)
        pygame.draw.polygon(bullet_surface, (243, 255, 185), adjusted_points)
        pygame.draw.polygon(bullet_surface, self.col, [(c := vec(shadow_surface.get_rect().center)) + 1.1 * (p - c) for p in  adjusted_points], 2)
        
        self.screen.blit(shadow_surface, (min_x, min_y))
        if self.shadow_height:
            self.screen.blit(bullet_surface, (min_x, min_y) + self.shadow_height)
        else:
            self.screen.blit(bullet_surface, (min_x, min_y))
