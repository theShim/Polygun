import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.gui.menu_buttons import Button, Label
from scripts.gui.controllers_gui import DeviceConnection
from scripts.gui.custom_fonts import Custom_Font
from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class Controllers_GUI(State):
    def __init__(self, game):
        super().__init__(game, "controllers_gui")

        self.shadow1 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(math.ceil(self.shadow1.height * 0.6)):
            pygame.draw.line(self.shadow1, (0, 0, 0, 255 * (1 - (y/(self.shadow1.height * 0.6)))), (0, y), (self.shadow1.width, y))
        self.shadow1_pos = vec(0, -HEIGHT)
        self.shadow2 = pygame.transform.flip(self.shadow1, True, True)
        self.shadow2_pos = vec(0, HEIGHT)

        self.buttons = pygame.sprite.Group()
        Label(self.game, [self.buttons], "Controllers", (30, 60))
        self.back_button = Button(self.game, [self.buttons], "Back", (30, 480), font=Custom_Font.font2)
        DeviceConnection(self.game, [self.buttons], 0)
        
    def update(self):
        self.prev.prev.d.update() #delaunay
        self.prev.buttons.update()

        self.shadow1_pos = self.shadow1_pos.lerp(vec(), 0.3)
        self.screen.blit(self.shadow1, self.shadow1_pos)
        self.screen.blit(self.shadow1, self.shadow1_pos)

        self.shadow2_pos = self.shadow2_pos.lerp(vec(), 0.3)
        self.screen.blit(self.shadow2, self.shadow2_pos)
        self.screen.blit(self.shadow2, self.shadow2_pos)

        self.buttons.update()

        if self.back_button.clicked:
            for button in self.buttons:
                button.out_of_frame = True

            self.shadow1_pos = self.shadow1_pos.lerp(vec(0, -HEIGHT), 0.3)
            self.shadow2_pos = self.shadow2_pos.lerp(vec(0, HEIGHT), 0.3)
            if self.shadow1_pos.y < -HEIGHT / 2:
                self.back_button.clicked = False
                self.game.state_loader.pop_state()
                self.back_button.clicked = False
        else:
            for button in self.buttons:
                button.out_of_frame = False

        self.game.gui_elements.update()