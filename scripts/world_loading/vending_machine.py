import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

# from scripts.world_loading.tiles import Tile
# from scripts.world_loading.nature.manager import Nature_Manager

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################
    
class VendingMachine(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.o_pos = vec(pos) + vec(0, -HEIGHT * 2)
        self.target_pos = vec(pos)
        self.pos = self.o_pos.copy()
        self.surf = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_machine.png").convert_alpha(), 3.5)
        self.surf.set_colorkey((0, 0, 0))
        self.t = 0

        self.lights1 = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_lights1.png").convert_alpha(), 3.5)
        self.lights1.set_colorkey((0, 0, 0))

        self.lights2 = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_lights2.png").convert_alpha(), 3.5)
        self.lights2.set_colorkey((0, 0, 0))
        self.flicker_timer = Timer(FPS, 1)
        self.lights2on = True

        shadow = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_shadow.png").convert_alpha(), 4)
        shadow.set_colorkey((0, 0, 0))
        self.shadow = pygame.mask.from_surface(shadow).to_surface(setcolor=(0, 0, 0, 200), unsetcolor=(0, 0, 0, 0))

        self.hitbox = pygame.Rect(self.target_pos.x - self.surf.width/2, self.target_pos.y - self.surf.height / 3, self.surf.width, self.surf.height / 2)
        self.just_landed = False

        self.interact_button = pygame.Surface((40, 45), pygame.SRCALPHA)
        pygame.draw.rect(self.interact_button, (0, 0, 0), [0, 5, 40, 40], border_radius=4)
        pygame.draw.rect(self.interact_button, (255, 255, 255), [0, 0, 40, 40], border_radius=4)
        self.render_interact_flag = False

    def collisions(self):
        self.render_interact_flag = False

        if self.just_landed:
            player = self.game.player
            hitbox = pygame.Rect(player.pos.x - player.size/2, player.pos.y - player.size/2, player.size, player.size)
            if self.hitbox.colliderect(hitbox):
                player.health = 0

        else:
            player = self.game.player
            hitbox = pygame.Rect(player.pos.x - player.size/2, player.pos.y - player.size/2, player.size, player.size)
            if self.hitbox.colliderect(hitbox):
                if player.pos.y - player.size / 2 < self.hitbox.bottom and player.vel.y < 0:
                    player.pos.y = self.hitbox.bottom + player.size / 2
                    player.vel.y = 0
                elif player.pos.y + player.size / 2 > self.hitbox.top and player.vel.y > 0:
                    player.pos.y = self.hitbox.top - player.size / 2
                    player.vel.y = 0

                elif player.pos.x - player.size / 2 < self.hitbox.right and player.vel.x < 0:
                    player.pos.x = self.hitbox.right + player.size / 2
                    player.vel.x = 0
                elif player.pos.x + player.size / 2 > self.hitbox.left and player.vel.x > 0:
                    player.pos.x = self.hitbox.left - player.size / 2
                    player.vel.x = 0

            if vec(self.hitbox.center).distance_to(player.pos) < 100:
                self.render_interact_flag = True


    def update(self):
        if self.t < 1:
            self.t += 0.4 * self.game.dt
            self.t = min(1, self.t)
            self.pos = self.o_pos.lerp(self.target_pos, 2 ** (10 * self.t - 10))
            if self.t == 1:
                self.pos = self.target_pos
                self.game.screen_shake.start(30, 15, 0.99)
                self.just_landed = True

        self.flicker_timer.update()
        if self.flicker_timer.finished:
            self.flicker_timer.change_speed(random.randint(1, 5))
            self.flicker_timer.reset()
            self.lights2on = not self.lights2on#

        self.collisions()
        self.just_landed = False

        self.draw()

    def draw(self):
        if self.t < 1:
            a = 0.8
            t = 2 ** (10 * self.t - 10)
            t = a * t + (1-a)
            shadow = pygame.transform.scale_by(self.shadow, t)
            self.screen.blit(shadow, shadow.get_rect(midbottom=self.target_pos - self.game.offset + vec(-8, -5)))

        else:
            self.screen.blit(self.shadow, self.surf.get_rect(midbottom=self.target_pos - self.game.offset + vec(-8, -5)))

        self.screen.blit(self.surf, self.surf.get_rect(midbottom=self.pos - self.game.offset))
        self.game.emissive_surf.blit(self.lights1, self.surf.get_rect(midbottom=self.pos - self.game.offset))

        if self.lights2on:
            self.game.emissive_surf.blit(self.lights2, self.surf.get_rect(midbottom=self.pos - self.game.offset))

        if self.render_interact_flag:
            self.screen.blit(self.interact_button, self.surf.get_rect(center=self.pos - self.game.offset))