import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math
import numpy as np

from scripts.gui.menu_buttons import Button
from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.CORE_FUNCS import vec

    ##############################################################################################

class TransitionIn(State):
    def __init__(self, game, next_state: State):
        super().__init__(game, "transition")
        self.next_state = next_state

        self.lines = pygame.sprite.Group()
        for i, y in enumerate(range(HEIGHT, 0, -HEIGHT//5)):
            l = TransitionLine(self.game, [self.lines], y, -i / 5)
        l.last = True

        self.state = 0

    def update(self):
        self.prev.update()
        self.lines.update()

        if self.state == 0:
            if any([line.done for line in self.lines]):
                self.game.state_loader.pop_state()
                self.game.state_loader.add_state(self.next_state)
                self.prev = self.game.state_loader.current_state
                self.game.state_loader.add_state(self.game.state_loader.last_state)
                self.state = 1

        elif self.state == 1:
            for line in self.lines:
                line.start_pos = line.target_pos
                line.target_pos = (2 * (WIDTH + line.line_height + line.buffer), 0)
                line.t = line.t_offset
            self.state = 2

class TransitionLine(pygame.sprite.Sprite):
    def __init__(self, game, groups, y, t_offset):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.line_height = HEIGHT / 5
        self.buffer = 10
        self.points = np.array([
            [WIDTH, y],
            [WIDTH + self.line_height, y - self.line_height],
            [WIDTH + self.line_height + WIDTH + self.line_height + self.buffer, y - self.line_height],
            [WIDTH + WIDTH + self.line_height + self.buffer, y]
        ])

        self.start_pos = vec()
        self.target_pos = vec(WIDTH + self.line_height + self.buffer, 0)
        self.offset = vec()
        self.t_offset = t_offset
        self.t = t_offset

        self.last = False
        self.done = False

    def update(self):
        self.t += 0.02
        if self.t >= 1: self.t = 1
        t = 1 - ((1 - self.t) ** 3)

        self.offset = self.start_pos.lerp(self.target_pos, max(0, t))

        if self.last:
            if self.t >= 1: self.done = True

        self.draw()

    def draw(self):
        pygame.draw.polygon(self.screen, (0, 0, 0), self.points - self.offset)