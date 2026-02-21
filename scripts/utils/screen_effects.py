import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.utils.CORE_FUNCS import Timer, vec

    ##############################################################################################

#effect object
#will run on enemy hits, player damage, certain world events / impact frames
class Screen_Shake:
    def __init__(self, game):
        self.game = game

        self.timer = 0 #how long should the screen be shaking for
        self.intensity = 4 #by what offset (max range of pixels)
        self.drop_off = 1 #decay factor if needed

    @property
    def on(self): #flag property for if the effect is active or not
        return bool(self.timer)

    #initialise a new "shake event"
    def start(self, duration: int, intensity=1, drop_off=1):
        self.timer = duration
        self.intensity = intensity
        self.drop_off = drop_off

    #constantly updating every frame
    def update(self):
        if self.timer <= 0: return #if the timer is complete, don't update

        #otherwise decrement the timer and intensities as required
        self.timer -= 1
        if self.drop_off < 1:
            self.intensity *= self.drop_off
        #randomly change the camera offset to give a screen shake illusion
        self.game.offset += vec(random.uniform(-1*self.intensity, 1*self.intensity), random.uniform(-1*self.intensity, 1*self.intensity))