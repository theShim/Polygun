import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.gui.menu_buttons import Button, Label, KeyboardInputButton
from scripts.gui.custom_fonts import Custom_Font
from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE
from scripts.utils.CORE_FUNCS import vec, Timer

    ##############################################################################################

class Keyboard_GUI(State):
    def __init__(self, game):
        super().__init__(game, "keyboard_gui")

        self.shadow1 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(math.ceil(self.shadow1.height * 0.6)):
            pygame.draw.line(self.shadow1, (0, 0, 0, 255 * (1 - (y/(self.shadow1.height * 0.6)))), (0, y), (self.shadow1.width, y))
        self.shadow1_pos = vec(0, -HEIGHT)
        self.shadow2 = pygame.transform.flip(self.shadow1, True, True)
        self.shadow2_pos = vec(0, HEIGHT)

        self.buttons = pygame.sprite.Group()
        Label(self.game, [self.buttons], "Keyboard", (30, 60))
        self.back_button = Button(self.game, [self.buttons], "Back", (30, 480), font=Custom_Font.font2)

        self.keys = pygame.sprite.Group()
        self.up = KeyboardInputButton(self.game, [self.buttons, self.keys], "Move UP: ", (60, 140), self.game.controls_handler.controls["move_up"], font=Custom_Font.font2)
        self.down = KeyboardInputButton(self.game, [self.buttons, self.keys], "Move DOWN:", (60, 180), self.game.controls_handler.controls["move_down"], font=Custom_Font.font2)
        self.left = KeyboardInputButton(self.game, [self.buttons, self.keys], "Move LEFT: ", (60, 220), self.game.controls_handler.controls["move_left"], font=Custom_Font.font2)
        self.right = KeyboardInputButton(self.game, [self.buttons, self.keys], "Move RIGHT: ", (60, 260), self.game.controls_handler.controls["move_right"], font=Custom_Font.font2)
        
        self.jump = KeyboardInputButton(self.game, [self.buttons, self.keys], "Jump: ", (60, 300), self.game.controls_handler.controls["jump"], font=Custom_Font.font2)
        self.dash = KeyboardInputButton(self.game, [self.buttons, self.keys], "Dash: ", (60, 340), self.game.controls_handler.controls["dash"], font=Custom_Font.font2)
        self.swap_weapon = KeyboardInputButton(self.game, [self.buttons, self.keys], "Swap Weapon: ", (60, 380), self.game.controls_handler.controls["swap_weapon"], font=Custom_Font.font2)

        self.pause = KeyboardInputButton(self.game, [self.buttons, self.keys], "Pause: ", (60, 420), self.game.controls_handler.controls["pause"], font=Custom_Font.font2)
        
        self.to_change_button = None
        self.throbber_timer = Timer(30, 1)
        self.ellipsis = 0
        self.dark_overlay = pygame.Surface(SIZE, pygame.SRCALPHA)
        self.dark_overlay.fill((0, 0, 0, 220))
        
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

        if self.to_change_button:
            self.screen.blit(self.dark_overlay)

            self.throbber_timer.update()
            if self.throbber_timer.finished:
                self.throbber_timer.reset()
                self.ellipsis = (self.ellipsis + 1) % 4
            Custom_Font.font2.render(self.screen, f"Enter a Key to Rebind{'.' * self.ellipsis}", (255, 255, 255), vec(SIZE) / 2 + vec(-Custom_Font.font2.calc_surf_width("Enter a Key to Rebind...") / 2, -Custom_Font.font2.space_height * 1.5))

            for event in self.game.events:
                if event.type == pygame.KEYDOWN:
                    self.to_change_button.clicked = False
                    if event.key == pygame.K_ESCAPE:
                        self.to_change_button = None
                    else:
                        for key, value in self.game.controls_handler.controls.items():
                            if value == self.to_change_button.key:
                                self.game.controls_handler.controls[key] = event.key
                                break

                        self.to_change_button.key = event.key
                        self.to_change_button.update_surf()
                        self.to_change_button = None
            return

        for button in self.keys:
            if button.clicked:
                self.to_change_button = button
                break

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