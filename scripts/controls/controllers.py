import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import json

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class BaseController:
    def __init__(self, game, joystick):
        self.game = game

        self.joystick: pygame.joystick.Joystick = joystick
        self.analog_deadzone = 0.1

class SwitchController(BaseController):
    BUTTONS = {
        "shoot" : 9
    }
    def __init__(self, joystick):
        super().__init__(joystick)