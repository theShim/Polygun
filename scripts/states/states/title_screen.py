import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.gui.menu_buttons import Button
from scripts.gui.delaunay import Del
from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Title_Screen(State):
    def __init__(self, game):
        super().__init__(game, "title_screen")

        self.d = Del(self, 100)
        self.logo = pygame.image.load("assets/gui/logo.png").convert_alpha()
        self.t = 0

        self.buttons = pygame.sprite.Group()
        Button(self.game, [self.buttons], "Start", (30, HEIGHT * 0.65))
        Button(self.game, [self.buttons], "Options", (30, HEIGHT * 0.65 + 60))
        Button(self.game, [self.buttons], "Quit", (30, HEIGHT * 0.65 + 120))

    def update(self):
        # self.screen.fill((255, 0, 0))

        self.d.update()
        self.t += math.radians(2)

        self.screen.blit(self.logo, self.logo.get_rect(center=(WIDTH/2, self.logo.height / 2 + 30 + math.sin(self.t) * 8)))

        self.buttons.update()