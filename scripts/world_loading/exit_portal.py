import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################

class ExitPortal(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.radius = 1
        self.max_radius = 40
        self.pause_timer = Timer(FPS, 1)
        self.activate_sound = True
        
        self.children = pygame.sprite.Group()

    def update(self):
        if (self.game.player.pos - self.pos).magnitude() < self.radius:
            self.game.state_loader.current_state.levels[self.game.state_loader.current_state.current_level_index].minimap.kill()
            self.game.state_loader.current_state.current_level_index += 1
            self.game.state_loader.current_state.levels[self.game.state_loader.current_state.current_level_index].generate_minimap()
            self.game.player.pos = vec(WIDTH/2 - self.game.player.size/2, HEIGHT/2 - self.game.player.size/2 + TILE_SIZE * 5)
            return self.kill()
        
        self.pause_timer.update()
        if not self.pause_timer.finished: return
        
        if self.activate_sound:
            self.game.music_player.play("exit_portal_activate", pool="ambient", loop=False)
            self.activate_sound = False
        
        self.radius = self.radius + (self.max_radius - self.radius) * 0.05
        for i in range(3):
            PortalParticle(self.game, [self.children], self.pos, random.randint(int(20 * (self.radius / self.max_radius)), int(40 * (self.radius / self.max_radius))))
        self.children.update(None)
        self.render()

    def render(self):
        rect = pygame.Rect(0, 0, self.radius * 2.5, self.radius * 2)
        rect.center = self.pos - self.game.offset

        pygame.draw.ellipse(self.game.emissive_surf, (255, 255, 255), rect.inflate(12, 12), 4)
        pygame.draw.ellipse(self.screen, (255, 255, 255), rect.inflate(12, 12))
        self.children.update(False)

        pygame.draw.ellipse(self.game.emissive_surf, (0, 0, 0), rect)
        pygame.draw.ellipse(self.screen, (0, 0, 0), rect)
        self.children.update(True)

class PortalParticle(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, radius=20):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.pos.x += random.uniform(-radius, radius)
        self.radius = radius
        self.decay = max(0.5, random.random())
        self.vel = vec()

    def update(self, draw_flag=False):
        if draw_flag != None:
            return self.draw(draw_flag)

        self.radius -= self.decay
        self.vel += vec(random.uniform(-self.radius / 10, self.radius / 10) * 0.225, random.uniform(-self.radius / 10, self.radius / 10) * 0.225)
        self.vel *= 0.9
        if self.radius <= 1:
            return self.kill()
        
        self.pos += self.vel

    def draw(self, draw_flag):
        if draw_flag in ["bg", False]:
            pygame.draw.circle(self.game.emissive_surf, (255, 255, 255), self.pos - self.game.offset, self.radius)
            pygame.draw.circle(self.screen, (255, 255, 255), self.pos - self.game.offset, self.radius)
        elif draw_flag in ["fg", True]:
            pygame.draw.circle(self.game.emissive_surf, (0, 0, 0), self.pos - self.game.offset, self.radius * 0.8)
            pygame.draw.circle(self.screen, (0, 0, 0), self.pos - self.game.offset, self.radius * 0.8)