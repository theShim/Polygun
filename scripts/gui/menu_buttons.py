import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

class Button(pygame.sprite.Sprite):
    def __init__(self, game, groups, text: str, pos: vec, font = Custom_Font.font2_5):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.font: Font = font
        
        self.text = text
        self.surf = pygame.Surface((self.font.calc_surf_width(self.text) + 6, self.font.space_height + 6), pygame.SRCALPHA)
        self.font.render(self.surf, self.text, (0, 0, 1), (6, 3))
        self.font.render(self.surf, self.text, (0, 0, 1), (0, 3))
        self.font.render(self.surf, self.text, (0, 0, 1), (3, 6))
        self.font.render(self.surf, self.text, (0, 0, 1), (3, 0))
        self.font.render(self.surf, self.text, (255, 255, 255), (3, 3))


        self.pos = vec(pos)
        self.oPos = vec(pos)
        self.target_pos = self.pos + vec(20, -5)

        self.line_end = vec(0, self.pos.y + self.font.space_height - 3)
        self.line_oPos = vec(-5, self.pos.y + self.font.space_height - 3)
        self.line_target_pos = vec(self.pos.x + self.font.calc_surf_width(self.text) + 24, self.pos.y + self.font.space_height - 3)

        self.pointer_points = np.array([
            [math.cos(0), math.sin(0)],
            [math.cos(2 * math.pi / 3), math.sin(2 * math.pi / 3)],
            [math.cos(4 * math.pi / 3), math.sin(4 * math.pi / 3)],
        ]) * 10
        self.pointer_pos = vec(-15, self.pos.y + self.font.space_height / 2 + 10)
        self.pointer_oPos = vec(-15, self.pos.y + self.font.space_height / 2 + 10)
        self.pointer_target_pos = vec(self.pos.x - 3, self.pos.y + self.font.space_height / 2 - 9)
        self.pointer_angle = -math.pi/6
        self.pointer_oAngle = -math.pi/6
        self.pointer_target_angle = 0
        self.pointer_offset_timer = 0

        self.hitbox = pygame.Rect(self.pos.x - 30, self.pos.y, 300, self.font.space_height)
        self.clicked = False
        self.out_of_frame = False


    def update(self):
        mousePos = pygame.mouse.get_pos()
        window_size = pygame.display.get_window_size()  # actual window size (after scaling)
        scale_x = WIDTH / window_size[0]
        scale_y = HEIGHT / window_size[1]
        mousePos = vec(mousePos[0] * scale_x, mousePos[1] * scale_y)

        if not self.out_of_frame:
            self.clicked = False
            if self.hitbox.collidepoint(mousePos):
                self.pos = self.pos.lerp(self.target_pos, 0.5)
                self.line_end = self.line_end.lerp(self.line_target_pos, 0.5)
                self.pointer_pos = self.pointer_pos.lerp(self.pointer_target_pos, 0.5)
                self.pointer_angle = lerp(self.pointer_angle, self.pointer_target_angle, 0.5)
                self.pointer_offset_timer += math.radians(7)
                
                if pygame.mouse.get_just_pressed()[0]:
                    self.clicked = True
            else:
                self.pos = self.pos.lerp(self.oPos, 0.5)
                self.line_end = self.line_end.lerp(self.line_oPos, 0.5)
                self.pointer_pos = self.pointer_pos.lerp(self.pointer_oPos, 0.5)
                self.pointer_angle = lerp(self.pointer_angle, self.pointer_oAngle, 0.5)
                self.pointer_offset_timer = 0
        else:
            self.pos = self.pos.lerp(vec(-300, self.pos.y), 0.2)
            self.line_end = self.line_end.lerp(vec(-200, self.line_oPos.y), 0.1)
            self.pointer_pos = self.pointer_pos.lerp(vec(-200, self.pointer_oPos.y), 0.1)

        self.screen.blit(self.surf, (self.pos.x - 3, self.pos.y - 3))

        pygame.draw.line(self.screen, (0, 0, 0), self.line_oPos, self.line_end + vec(1, 0), 7)
        pygame.draw.line(self.screen, (255, 255, 255), self.line_oPos, self.line_end, 3)

        points = rot_2d(self.pointer_points, self.pointer_angle)
        pygame.draw.polygon(self.screen, (255, 255, 255), points + self.pointer_pos + vec(math.sin(self.pointer_offset_timer), 0) * 2)
        pygame.draw.polygon(self.screen, (0, 0, 0), points * 1.05 + self.pointer_pos + vec(math.sin(self.pointer_offset_timer), 0) * 2, 2)

    ##############################################################################################

class Label(pygame.sprite.Sprite):
    def __init__(self, game, groups, text: str, pos: vec, font = Custom_Font.font2_5):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.font: Font = font
        
        self.text = text
        self.surf = pygame.Surface((self.font.calc_surf_width(self.text) + 6, self.font.space_height + 6), pygame.SRCALPHA)
        self.font.render(self.surf, self.text, (0, 0, 1), (6, 3))
        self.font.render(self.surf, self.text, (0, 0, 1), (0, 3))
        self.font.render(self.surf, self.text, (0, 0, 1), (3, 6))
        self.font.render(self.surf, self.text, (0, 0, 1), (3, 0))
        self.font.render(self.surf, self.text, (255, 255, 255), (3, 3))

        self.pos = vec(pos)
        self.oPos = vec(pos)
        self.target_pos = self.pos + vec(20, -5)

        self.line_end = vec(0, self.pos.y + self.font.space_height - 3)
        self.line_oPos = vec(-5, self.pos.y + self.font.space_height - 3)
        self.line_target_pos = vec(self.pos.x + self.font.calc_surf_width(self.text) + 24, self.pos.y + self.font.space_height - 3)

        self.out_of_frame = False


    def update(self):
        mousePos = pygame.mouse.get_pos()
        window_size = pygame.display.get_window_size()  # actual window size (after scaling)
        scale_x = WIDTH / window_size[0]
        scale_y = HEIGHT / window_size[1]
        mousePos = vec(mousePos[0] * scale_x, mousePos[1] * scale_y)

        if not self.out_of_frame:
            self.pos = self.pos.lerp(self.oPos, 0.5)
            self.line_end = self.line_end.lerp(self.line_oPos, 0.5)
        else:
            self.pos = self.pos.lerp(vec(-300, self.pos.y), 0.2)
            self.line_end = self.line_end.lerp(vec(-200, self.line_oPos.y), 0.1)

        self.screen.blit(self.surf, (self.pos.x - 3, self.pos.y - 3))

        pygame.draw.line(self.screen, (0, 0, 0), self.line_oPos, self.line_end + vec(1, 0), 7)
        pygame.draw.line(self.screen, (255, 255, 255), self.line_oPos, self.line_end, 3)