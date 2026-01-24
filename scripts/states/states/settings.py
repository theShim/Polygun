import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.gui.menu_buttons import Button
from scripts.gui.custom_fonts import Custom_Font
from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class Settings(State):
    def __init__(self, game):
        super().__init__(game, "settings")
        self.screen = self.game.gui_surf
        
        self.shadow = pygame.Surface((WIDTH * 0.5, HEIGHT), pygame.SRCALPHA)
        for x in range(self.shadow.width):
            pygame.draw.line(self.shadow, (0, 0, 0, 255 * (1 - (x/self.shadow.width))), (x, 0), (x, self.shadow.height))
        self.shadow_pos = vec(-WIDTH, 0)

        self.buttons = pygame.sprite.Group()
        self.video_button = Button(self.game, [self.buttons], "Video", (30, 100 - 40), font=Custom_Font.font2)
        self.audio_button = Button(self.game, [self.buttons], "Audio", (30, 160 - 40), font=Custom_Font.font2)
        self.keyboard_button = Button(self.game, [self.buttons], "Keyboard Inputs", (30, 220 - 40), font=Custom_Font.font2)
        self.controller_button = Button(self.game, [self.buttons], "Controller Inputs", (30, 280 - 40), font=Custom_Font.font2)
        self.accessibility_button = Button(self.game, [self.buttons], "Accessibility", (30, 340 - 40), font=Custom_Font.font2)

        self.back_button = Button(self.game, [self.buttons], "Back", (30, 480), font=Custom_Font.font2)

    def update(self):
        self.prev.d.update() #delaunay
        self.prev.buttons.update()
        
        self.shadow_pos = self.shadow_pos.lerp(vec(), 0.3)
        self.screen.blit(self.shadow, self.shadow_pos)
        self.screen.blit(self.shadow, self.shadow_pos)

        self.buttons.update()

        if self.back_button.clicked:
            for button in self.buttons:
                button.out_of_frame = True

            self.shadow_pos = self.shadow_pos.lerp(vec(-WIDTH, 0), 0.3)
            if self.shadow_pos.x < -WIDTH / 2:
                self.back_button.clicked = False
                self.game.state_loader.pop_state()
                self.back_button.clicked = False


        elif self.controller_button.clicked:
            for button in self.buttons:
                button.out_of_frame = True
            
            self.shadow_pos = self.shadow_pos.lerp(vec(-WIDTH, 0), 0.3)
            if self.shadow_pos.x < -WIDTH / 2:
                self.back_button.clicked = False
                self.game.state_loader.add_state(self.game.state_loader.get_state("controllers_gui"))
                self.game.state_loader.current_state.prev = self
                self.controller_button.clicked = False


        elif self.keyboard_button.clicked:
            for button in self.buttons:
                button.out_of_frame = True
            
            self.shadow_pos = self.shadow_pos.lerp(vec(-WIDTH, 0), 0.3)
            if self.shadow_pos.x < -WIDTH / 2:
                self.back_button.clicked = False
                self.game.state_loader.add_state(self.game.state_loader.get_state("keyboard_gui"))
                self.game.state_loader.current_state.prev = self
                self.keyboard_button.clicked = False
                

        else:
            for button in self.buttons:
                button.out_of_frame = False

        self.game.gui_elements.update()