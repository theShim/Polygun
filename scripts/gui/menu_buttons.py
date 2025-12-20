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
        mousePos = self.game.mousePos

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
        if not self.out_of_frame:
            self.pos = self.pos.lerp(self.oPos, 0.5)
            self.line_end = self.line_end.lerp(self.line_oPos, 0.5)
        else:
            self.pos = self.pos.lerp(vec(-300, self.pos.y), 0.2)
            self.line_end = self.line_end.lerp(vec(-200, self.line_oPos.y), 0.1)

        self.screen.blit(self.surf, (self.pos.x - 3, self.pos.y - 3))

        pygame.draw.line(self.screen, (0, 0, 0), self.line_oPos, self.line_end + vec(1, 0), 7)
        pygame.draw.line(self.screen, (255, 255, 255), self.line_oPos, self.line_end, 3)

    ##############################################################################################

class KeyboardInputButton(pygame.sprite.Sprite):

    CONTROLS_TO_TEXT = {
        pygame.K_UP : "Up Arrow",
        pygame.K_DOWN : "Down Arrow",
        pygame.K_LEFT : "Left Arrow",
        pygame.K_RIGHT : "Right Arrow",

        pygame.K_a : "A",
        pygame.K_b : "B",
        pygame.K_c : "C",
        pygame.K_d : "D",
        pygame.K_e : "E",
        pygame.K_f : "F",
        pygame.K_g : "G",
        pygame.K_h : "H",
        pygame.K_i : "I",
        pygame.K_j : "J",
        pygame.K_k : "K",
        pygame.K_l : "L",
        pygame.K_m : "M",
        pygame.K_n : "N",
        pygame.K_o : "O",
        pygame.K_p : "P",
        pygame.K_q : "Q",
        pygame.K_r : "R",
        pygame.K_s : "S",
        pygame.K_t : "T",
        pygame.K_u : "U",
        pygame.K_v : "V",
        pygame.K_w : "W",
        pygame.K_x : "X",
        pygame.K_y : "Y",
        pygame.K_z : "Z",

        pygame.K_0 : "0",
        pygame.K_1 : "1",
        pygame.K_2 : "2",
        pygame.K_3 : "3",
        pygame.K_4 : "4",
        pygame.K_5 : "5",
        pygame.K_6 : "6",
        pygame.K_7 : "7",
        pygame.K_8 : "8",
        pygame.K_9 : "9",

        pygame.K_TAB : "Tab",
        pygame.K_CAPSLOCK : "Caps",
        pygame.K_LSHIFT : "Left Shift",
        pygame.K_RSHIFT : "Right Shift",
        pygame.K_LCTRL : "Left Control",
        pygame.K_RCTRL : "Right Control",
        pygame.K_LMETA : "Window Key",
        pygame.K_LALT : "Left Alt",
        pygame.K_RALT : "Right Alt",
        pygame.K_SPACE : "Space",
        pygame.K_QUOTE : "'",
        pygame.K_MINUS : "-",
        pygame.K_PLUS : "+",
        pygame.K_BACKQUOTE : "`",
        pygame.K_SEMICOLON : ";",
        pygame.K_LEFTBRACKET : "[",
        pygame.K_RIGHTBRACKET : "]",
        pygame.K_HASH : "#",
        pygame.K_SLASH : "/",
        pygame.K_BACKSLASH : "\\",
        pygame.K_COMMA : ",",
        pygame.K_PERIOD : ".",
        pygame.K_RETURN : "Enter",
        pygame.K_PRINTSCREEN : "Print Screen",
        pygame.K_INSERT : "Insert",
        pygame.K_DELETE : "Delete",
        pygame.K_ESCAPE : "Escape",

        pygame.K_F1 : "F1",
        pygame.K_F2 : "F2",
        pygame.K_F3 : "F3",
        pygame.K_F4 : "F4",
        pygame.K_F5 : "F5",
        pygame.K_F6 : "F6",
        pygame.K_F7 : "F7",
        pygame.K_F8 : "F8",
        pygame.K_F9 : "F9",
        pygame.K_F10 : "F10",
        pygame.K_F11 : "F11",
        pygame.K_F12 : "F12",
    }

    def __init__(self, game, groups, text, pos, key, font=Custom_Font.font2_5):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.font: Font = font
        
        self.text = text # f"{text:<13}{self.CONTROLS_TO_TEXT[key]:<10}"
        self.key = key
        self.surf = None

        self.pos = vec(pos)
        self.oPos = vec(pos)
        self.target_pos = self.pos + vec(20, -5)
        
        self.update_surf()

        self.line_origin = self.pos + vec(self.font.calc_surf_width(f"{self.text:<14}") + self.font.calc_surf_width(f"{self.CONTROLS_TO_TEXT[self.key]:<14}") / 2, self.font.space_height - 3)
        self.line_displacement = vec()

        self.hitbox = pygame.Rect(self.pos.x - 30, self.pos.y, 400, self.font.space_height)
        self.clicked = False
        self.out_of_frame = False

    def update_surf(self):
        total_string = f"{self.text:<14}{self.CONTROLS_TO_TEXT[self.key]:<14}"
        text_string = f"{self.text:<14}"
        text_width = self.font.calc_surf_width(text_string)
        text_width = text_width if text_width == 208 else 208
        if text_width == 208:
            text_width = text_width
        else:
            text_width = 208
        key_string = self.CONTROLS_TO_TEXT[self.key]

        self.surf = pygame.Surface((self.font.calc_surf_width(total_string) + 6, self.font.space_height + 6), pygame.SRCALPHA)

        self.font.render(self.surf, text_string, (0, 0, 1), (6, 3))
        self.font.render(self.surf, text_string, (0, 0, 1), (0, 3))
        self.font.render(self.surf, text_string, (0, 0, 1), (3, 6))
        self.font.render(self.surf, text_string, (0, 0, 1), (3, 0))

        self.font.render(self.surf, key_string, (0, 0, 1), (6 + text_width, 3))
        self.font.render(self.surf, key_string, (0, 0, 1), (0 + text_width, 3))
        self.font.render(self.surf, key_string, (0, 0, 1), (3 + text_width, 6))
        self.font.render(self.surf, key_string, (0, 0, 1), (3 + text_width, 0))

        self.font.render(self.surf, text_string, (255, 255, 255), (3, 3))
        self.font.render(self.surf, key_string, (255, 255, 255), (3 + text_width, 3))
        
        self.line_origin = self.pos + vec(self.font.calc_surf_width(f"{self.text:<14}") + self.font.calc_surf_width(self.CONTROLS_TO_TEXT[self.key]) / 2, self.font.space_height - 3)

    def update(self):
        mousePos = self.game.mousePos

        if not self.out_of_frame:
            self.clicked = False
            if self.hitbox.collidepoint(mousePos):
                self.line_displacement = self.line_displacement.lerp(vec(self.font.calc_surf_width(self.CONTROLS_TO_TEXT[self.key]) / 2, 0), 0.5)
                
                if pygame.mouse.get_just_pressed()[0]:
                    self.clicked = True
            else:
                self.line_displacement = self.line_displacement.lerp(vec(0, 0), 0.5)
        else:
            self.line_displacement = self.line_displacement.lerp(vec(0, 0), 0.5)

        self.screen.blit(self.surf, (self.pos.x - 3, self.pos.y - 3))

        if self.line_displacement.magnitude() > 0.5:
            pygame.draw.line(self.screen, (0, 0, 0), self.line_origin + self.line_displacement, self.line_origin - self.line_displacement, 7)
            pygame.draw.line(self.screen, (255, 255, 255), self.line_origin + self.line_displacement, self.line_origin - self.line_displacement, 3)