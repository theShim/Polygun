import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

    ##############################################################################################

class Debugger:
    def __init__(self, game):
        self.game = game
        self.screen = self.game.screen

        self.text = ""
        self.font = pygame.font.SysFont('Verdana', 18)

    def add_text(self, text):
        self.text += text + "\n"

    def update(self):
        self.render()
        self.text = ""
    
    def render(self):
        label = self.font.render(self.text, False, (255, 255, 255))
        self.screen.blit(label, (0, 0))