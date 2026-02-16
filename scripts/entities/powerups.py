import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import os

from scripts.gui.custom_fonts import Custom_Font, Font

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE, SIZE

    ##############################################################################################

POWER_UP_INFO = {
    "double_rounds" : {
        "name" : "Double Rounds",
        "description" : "Because once was so nice, you had to do it twice.",
        "effects" : ["x2 bullets for 30 seconds"],
        "cost" : 16,
        "type" : "timed",
        "duration" : FPS * 30,
    },
    "crowbar" : {
        "name" : "Crowbar",
        "description" : "Blunt force trauma is a great way to meet new people.",
        "effects" : [r"+75% damage to enemies above 90% health"],
        "cost" : 35,
        "type" : "permanent",
    },
    "steak" : {
        "name" : "Steak",
        "description" : "Packed with protein. Possibly made of meat.",
        "effects" : ["+10 Max HP"],
        "cost" : 24,
        "type" : "consumable",
    }
}

def wrap_text(text: str, font: Font, width):
    sections = []

    stack = ""
    for word in text.split(" "):
        curr_width = font.calc_surf_width(stack)
        if curr_width > width:
            sections.append(stack.strip(" "))
            stack = ""

        stack += word + " "
    sections.append(stack.strip(" "))
    return sections

    
class PowerUp(pygame.sprite.Sprite):
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        path = "assets/power_ups/"
        for filename in os.listdir(path):
            img = pygame.image.load(path + filename).convert_alpha()
            cls.SPRITES[filename.split(".")[0]] = img

    def __init__(self, game, groups, mode, parent, a_offset=0):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen if mode != "gui" else self.game.gui_surf
        self.mode = mode
        self.parent = parent #vending machine object
        self.font1 = Custom_Font.font2_5
        self.font2 = Custom_Font.font1_5

        self.angle = a_offset + math.pi/6
        self.angle_offset = 6 * math.pi

        self.radius = 72
        self.surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (0, 0, 0), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.surf, (255, 255, 255), (self.radius, self.radius), self.radius, 8)
        self.surf = pygame.transform.pixelate(self.surf, 2)
        self.shadow = pygame.mask.from_surface(self.surf).to_surface(setcolor=(0, 0, 0), unsetcolor=(0, 0, 0, 0))
        self.ring_radius = 0
        self.anchor = vec(WIDTH/2, HEIGHT/2)
        self.pos = self.anchor.copy()
        self.external_offset = vec()

        self.hover_offset = 0
        self.hover = False

        self.name, img = random.choice(list(self.SPRITES.items()))
        self.surf.blit(img, img.get_rect(center=vec(self.surf.size)/2))

        self.power_surf = pygame.transform.scale_by(self.surf, 0.25)
        self.power_shadow = pygame.mask.from_surface(self.power_surf).to_surface(setcolor=(0, 0, 0), unsetcolor=(0, 0, 0, 0))
        self.info = POWER_UP_INFO[self.name]
        self.type_ = self.info["type"]
        if self.type_ == "timed":
            self.timer = Timer(self.info["duration"], 1)

    def update(self, index=0):
        if self.mode == "gui":
            self.gui_update()

        elif self.mode == "powerup":
            self.powerup_update(index)

    def powerup_update(self, index):
        if self.type_ == "timed":
            self.timer.update()
            if self.timer.finished:
                return self.kill()
            
        elif self.type_ == "consumable":
            if self.name == "steak":
                self.game.player.max_health += 10
                return self.kill()

        x = index % 8
        y = index // 8
        self.screen.blit(self.power_shadow, self.power_surf.get_rect(bottomright=(WIDTH - 16 + 2 - x * self.power_surf.width * 0.8, HEIGHT - 10 + 2 - y * self.power_surf.height)))
        self.screen.blit(self.power_surf, self.power_surf.get_rect(bottomright=(WIDTH - 16 - x * self.power_surf.width * 0.8, HEIGHT - 10 - y * self.power_surf.height)))

    def gui_update(self):
        a = self.angle + self.angle_offset
        self.angle_offset *= 0.975

        t = (1 - (self.angle_offset / (8 * math.pi)))
        self.ring_radius = 170 * t

        self.pos = self.anchor + vec(math.cos(a), math.sin(a)) * self.ring_radius - vec(self.surf.size)/2
        self.pos.x += 220 * t

        self.hover = self.game.mousePos.distance_to(self.pos + vec(self.surf.size)/2) < self.radius

        if self.hover:
            if pygame.mouse.get_just_pressed()[0]:
                self.mode = "powerup"
                self.game.possible_powerups = []
                self.game.player.item_manager.items.add(self)
                self.parent.used = True

            self.hover_offset += (-20 - self.hover_offset) * 0.2
            self.font1.render(self.screen, self.info["name"], (255, 255, 255), (40, 70))
            
            desc_lines = wrap_text(self.info["description"], self.font2, WIDTH * 0.4)
            for i, line in enumerate(desc_lines):
                self.font2.render(self.screen, line, (255, 255, 255), (40, 80 + self.font1.space_height + i * self.font2.space_height))

            for effect in self.info["effects"]:
                self.font2.render(self.screen, "●", (255, 255, 255), (40, 100 + self.font1.space_height + len(desc_lines) * self.font2.space_height))
                effect_lines = wrap_text(effect, self.font2, WIDTH * 0.35)
                for j, line in enumerate(effect_lines):
                    self.font2.render(self.screen, line, (255, 255, 255), (40 + self.font2.space_width * 2, 100 + self.font1.space_height + ((len(desc_lines) + j) * self.font2.space_height)))
        else:
            self.hover_offset += (0 - self.hover_offset) * 0.2

        self.screen.blit(self.shadow, self.pos + vec(6, 9 + t * 30) + self.external_offset)
        self.screen.blit(self.surf, self.pos + vec(0, t * 30 + self.hover_offset) + self.external_offset)