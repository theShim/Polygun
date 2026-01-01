import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

    ##############################################################################################

#normal pygame sound object just with a name attribute
class Sound(pygame.mixer.Sound):
    def __init__(self, filename):
        super().__init__(filename)
        self.name = filename.split("/")[-1]

SOUNDS = {
    "xqc_dungeon" : Sound("audio/xqc_dungeon.mp3"),
    "gunshot" : Sound("audio/gun.mp3"),
}