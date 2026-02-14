import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.gui.menu_buttons import Button
from scripts.gui.custom_fonts import Custom_Font
from scripts.states.state_loader import State
from scripts.gui.cursor import Cursor

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class Vending_Overlay(State):
    def __init__(self, game):
        super().__init__(game, "vending")
        self.screen = self.game.gui_surf
        
        self.buttons = pygame.sprite.Group()
        self.back_button = Button(self.game, [self.buttons], "Back", (30, 480), font=Custom_Font.font2)
        self.cursor = Cursor(self.game, [])
        self.active = True

        self.radius = (WIDTH/2) * 1.1
        
    def update(self):
        self.prev.update()
        
        self.radius *= 0.9 if self.active else (1 / 0.9)
        self.game.gui_surf.fill((44 - 30, 46 - 30, 95 - 30))
        pygame.draw.circle(self.screen, (0, 0, 0, 0), vec(WIDTH, HEIGHT)/2, self.radius)

        if not self.active:
            if self.radius >= (WIDTH/2) * 1:
                self.game.state_loader.pop_state()
                self.back_button.clicked = False
                self.radius = (WIDTH/2) * 1.1
                self.game.player.toggle_active()
                self.active = True

        self.back_button.update()
        if self.back_button.clicked and self.active:
            self.active = False
            self.radius = 1

        self.cursor.update()

        for pow_up in self.game.possible_powerups:
            pow_up.update()