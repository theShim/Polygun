import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import json

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class ControlsHandler(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.controls = {}
        self.load_json()

    def load_json(self):
        try:
            with open("data/player_controls.json", "r") as file:
                data = json.load(file)

            self.controls["move_up"] = data["move_up"]
            self.controls["move_down"] = data["move_down"]
            self.controls["move_left"] = data["move_left"]
            self.controls["move_right"] = data["move_right"]
            
            self.controls["jump"] = data["jump"]
            self.controls["dash"] = data["dash"]
            self.controls["swap_weapon"] = data["swap_weapon"]
            
            self.controls["pause"] = data["pause"]
            
        except:
            self.controls = {
                "move_up" : pygame.K_UP,
                "move_down" : pygame.K_DOWN,
                "move_left" : pygame.K_LEFT,
                "move_right" : pygame.K_RIGHT,
                
                "jump" : pygame.K_SPACE,
                "dash" : pygame.K_LCTRL,
                "swap_weapon" : pygame.K_r,
                
                "pause" : pygame.K_ESCAPE,
            }
            self.save_json()

    def save_json(self):
        with open("data/player_controls.json", "w") as file:
            json.dump(self.controls, file, indent=4)

    def update(self):
        pass