import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.entities.powerups import PowerUp

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################
    
class VendingMachine(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.font = Font("assets/fonts/nea_font.png", scale=1.75)

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

        self.interact_button = pygame.Surface((30, 35), pygame.SRCALPHA)
        pygame.draw.rect(self.interact_button, (75, 81, 115), [0, 5, 30, 30], border_radius=4)
        pygame.draw.rect(self.interact_button, (105 - 20, 153 - 20, 251 - 20), [0, 0, 30, 30], border_radius=4)
        self.render_interact_flag = False
        self.interact_button_size = 0.0
        self.font.render(self.interact_button, "E", (49, 56, 123), (self.interact_button.width/2 - self.font.space_width/2, self.interact_button.height/2 - self.font.space_height/2 + 2))
        self.button_siner = 0

        self.game.possible_powerups += [PowerUp(self.game, [], "gui", a_offset=((i/3) * 2*math.pi)) for i in range(3)]

    def collisions(self):
        self.render_interact_flag = False

        if self.just_landed:
            player = self.game.player
            hitbox = pygame.Rect(player.pos.x - player.size/2, player.pos.y - player.size/2, player.size, player.size)
            if self.hitbox.colliderect(hitbox):
                player.health = 0

        else:
            if self.t < 1:
                return
            
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

            if vec(self.hitbox.center).distance_to(player.pos) < 80:
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
            self.lights2on = not self.lights2on

        self.collisions()
        if self.just_landed:
            self.game.music_player.play("vending_machine_fall", pool="sfx", loop=False)
        self.just_landed = False

        if self.render_interact_flag:
            self.interact_button_size += (1 - self.interact_button_size) * 0.25
            if self.interact_button_size > 0.995:
                self.interact_button_size = 1

            if pygame.key.get_just_pressed()[pygame.K_e] and self.game.player.active:
                current_state = self.game.state_loader.current_state
                self.game.state_loader.add_state(self.game.state_loader.get_state("vending"))
                self.game.state_loader.current_state.prev = current_state
                self.game.player.toggle_active()
            
        else:
            self.interact_button_size += (0 - self.interact_button_size) * 0.25
            if self.interact_button_size < 0.005:
                self.interact_button_size = 0

        self.button_siner += math.radians(4)

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

        if self.interact_button_size > 0.05:
            button = pygame.transform.scale_by(self.interact_button, self.interact_button_size) if self.interact_button_size < 1 else self.interact_button
            self.game.gui_surf.blit(button, button.get_rect(center=self.surf.get_rect(midbottom=self.pos - self.game.offset + vec(0, math.sin(self.button_siner) * 2 + 10)).center))
            self.game.emissive_surf.blit(button, button.get_rect(center=self.surf.get_rect(midbottom=self.pos - self.game.offset + vec(0, math.sin(self.button_siner) * 2 + 10)).center))