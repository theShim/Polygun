import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.gui.menu_buttons import Button
from scripts.gui.delaunay import Del
from scripts.gui.cursor import Cursor
from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Title_Screen(State):
    def __init__(self, game):
        super().__init__(game, "title_screen")

        self.d = Del(game, 100)
        self.logo = pygame.image.load("assets/gui/logo.png").convert_alpha()
        self.t = 0

        self.buttons = pygame.sprite.Group()
        self.start_button = Button(self.game, [self.buttons], "Start", (30, HEIGHT * 0.65))
        self.options_button = Button(self.game, [self.buttons], "Options", (30, HEIGHT * 0.65 + 60))
        self.quit_button = Button(self.game, [self.buttons], "Quit", (30, HEIGHT * 0.65 + 120))

        Cursor(self.game, [self.game.gui_elements])

    def update(self):
        self.start_button.out_of_frame = False
        self.options_button.out_of_frame = False
        self.quit_button.out_of_frame = False

        self.d.update()
        self.t += math.radians(2)

        self.screen.blit(self.logo, self.logo.get_rect(center=(WIDTH/2, self.logo.height / 2 + 30 + math.sin(self.t) * 8)))

        self.buttons.update()

        
        if self.start_button.clicked:
            self.game.state_loader.add_state(self.game.state_loader.get_state("dungeon"))
            self.start_button.out_of_frame = True
            self.options_button.out_of_frame = True
            self.quit_button.out_of_frame = True
            self.options_button.clicked = False

        elif self.options_button.clicked:
            self.game.state_loader.add_state(self.game.state_loader.get_state("settings"))
            self.game.state_loader.current_state.prev = self
            self.start_button.out_of_frame = True
            self.options_button.out_of_frame = True
            self.quit_button.out_of_frame = True
            self.options_button.clicked = False
        
        elif self.quit_button.clicked:
            self.game.quit()

        self.game.gui_elements.update()