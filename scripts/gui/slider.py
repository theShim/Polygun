import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

from scripts.gui.custom_fonts import Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

SCALE = 4

class Slider(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, pool):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.gui_surf
        self.pool = pool
        self.changed = False

        self.pos = vec(pos)
        self.vol = self.game.music_player.get_pool_volume(self.pool)

        self.base = pygame.Surface((72, 7), pygame.SRCALPHA)
        self.base.fill((20, 16, 32))
        self.base.fill((39, 37, 60), [0, 0, 72, 2])
        self.base = pygame.transform.scale(self.base, vec(self.base.get_size()) * SCALE)
        pygame.draw.rect(self.base, (1, 0, 0), self.base.get_rect(), SCALE)
        
        self.knob = Knob(self.game, self, 
            [self.pos[0] + SCALE, self.pos[1] - SCALE * 2], 
            [self.pos[0] + self.base.get_width() - 33 - SCALE, self.pos[1] - SCALE * 2],
            self.vol)

    def change_vol(self, new_vol):
        self.vol = new_vol
        self.game.music_player.set_pool_volume(self.pool, self.vol)
        self.changed = True

    def update(self):
        self.changed = False
        self.screen.blit(self.base, self.pos)

        pygame.draw.rect(self.screen, [17, 158, 214], [self.pos[0] + SCALE, self.pos[1] + SCALE, int(self.knob.pos.x - self.knob.start.x), SCALE])
        pygame.draw.rect(self.screen, [65, 243, 252], [self.pos[0] + SCALE, self.pos[1] + SCALE * 2, int(self.knob.pos.x - self.knob.start.x), SCALE * 4])
        
        self.knob.update()


class Knob(pygame.sprite.Sprite):
    def __init__(self, game, parent, start, end, start_t):
        super().__init__()
        self.game = game
        self.screen = self.game.gui_surf
        self.parent = parent

        self.start = vec(start)
        self.end = vec(end)
        self.pos = self.start.lerp(self.end, start_t)

        self.base = pygame.Surface((14-3, 14-3), pygame.SRCALPHA)
        self.base.fill((57, 58, 74))
        pygame.draw.rect(self.base, (1, 0, 0), self.base.get_rect(), 1)
        pygame.draw.line(self.base, (20, 16, 32), [2, 2], [2, 11-3])
        pygame.draw.line(self.base, (20, 16, 32), [11-3, 2], [11-3, 11-3])
        pygame.draw.line(self.base, (30, 23, 48), [3, 2], [10-3, 2])
        pygame.draw.line(self.base, (30, 23, 48), [3, 11-3], [10-3, 11-3])
        self.base = pygame.transform.scale(self.base, vec(self.base.get_size()) * SCALE)

        self.held = False

    def clamp_pos(self):
        if self.pos.x < self.start.x:
            self.pos.x = self.start.x
        if self.pos.x > self.end.x:
            self.pos.x = self.end.x

    def change_volume(self):
        dist = abs(self.start.x - self.pos.x)
        vol = dist / (self.end.x - self.start.x)
        self.parent.change_vol(vol)

    def move(self):
        mouse = pygame.mouse.get_pressed()
        mousePos = self.game.mousePos

        if mouse[0]:
            if self.held == False:
                if self.base.get_rect(topleft=self.pos).collidepoint(mousePos):
                    self.held = True
            else:
                self.pos.x = mousePos[0] - self.base.get_width()/2
                self.clamp_pos()
                self.change_volume()
        else:
            self.held = False

    def update(self):
        self.move()

        self.screen.blit(self.base, self.pos)
        if self.base.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()) or self.held:
            pygame.draw.rect(self.screen, [65, 243, 252], [self.pos.x + SCALE*2, self.pos.y + SCALE*2, SCALE, SCALE*7])
            pygame.draw.rect(self.screen, [65, 243, 252], [self.pos.x + self.base.get_width() - SCALE*3, self.pos.y + SCALE*2, SCALE, SCALE*7])
            pygame.draw.rect(self.screen, [17, 158, 214], [self.pos.x + SCALE*2, self.pos.y + SCALE*2, SCALE*7, SCALE])
            pygame.draw.rect(self.screen, [17, 158, 214], [self.pos.x + SCALE*2, self.pos.y + self.base.get_height() - SCALE*3, SCALE*7, SCALE])