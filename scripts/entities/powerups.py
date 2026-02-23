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
        "cost" : 45,
        "type" : "permanent",
    },
    "steak" : {
        "name" : "Steak",
        "description" : "Packed with protein. Possibly made of meat.",
        "effects" : ["+10 Max HP"],
        "cost" : 24,
        "type" : "consumable",
    },
    "bean_juice" : {
        "name" : "Bean Juice",
        "description" : "beans.",
        "effects" : ["+7.5% Attack Speed", "+7% Movement Speed"],
        "cost" : 44,
        "type" : "permanent"
    },
    "energy_drink" : {
        "name" : "Energy Drink",
        "description" : "Filled with electrolytes, lemons, phenylcyclidine, benzodiazepines and dihydrogen monoxide.",
        "effects" : ["+50% Movement Speed for 60s"],
        "cost" : 20,
        "type" : "timed",
        "duration" : FPS * 60,
    },
    "medkit" : {
        "name" : "Medkit",
        "description" : "W NHS",
        "effects" : ["2s after getting hurt, heal for 10% max HP"],
        "cost" : 60,
        "type" : "permanent"
    },
    "focus_crystal" : {
        "name" : "Focus Crystal",
        "description" : "Astrology can be fatal.",
        "effects" : ["+20% Damage to enemies within 3 metres."],
        "cost" : 32,
        "type" : "permanent"
    },
    "gasoline" : {
        "name" : "Gasoline",
        "description" : "Work in Progress",
        "effects" : [r"On the next bullet, all nearby enemies are dealt 150% base damage."],
        "cost" : 28,
        "type" : "consumable"
    },
}

def wrap_text(text: str, font: Font, width):
    sections = [] #final return

    stack = "" #current segment
    for word in text.split(" "): #split the string into a list of words
        curr_width = font.calc_surf_width(stack) #calculate the segment width
        #if the segment width so far is greater than the max. w
        if curr_width > width:
            sections.append(stack.strip(" "))
            stack = "" #reset the segment

        stack += word + " " #otherwise add the word to the segment
    sections.append(stack.strip(" ")) #add the remaining segment to the stack
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
        self.font3 = Custom_Font.font2

        self.angle = a_offset + math.pi/6
        self.angle_offset = 6 * math.pi

        #circle background
        self.radius = 72
        self.surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (0, 0, 0), (self.radius, self.radius), self.radius) #black circle
        pygame.draw.circle(self.surf, (255, 255, 255), (self.radius, self.radius), self.radius, 8) #white border
        self.surf = pygame.transform.pixelate(self.surf, 2) #slightly pixelate the background
        self.shadow = pygame.mask.from_surface(self.surf).to_surface(setcolor=(0, 0, 0), unsetcolor=(0, 0, 0, 0))
        
        self.ring_radius = 0
        self.anchor = vec(WIDTH/2, HEIGHT/2)
        self.pos = self.anchor.copy()
        self.external_offset = vec()

        self.hover_offset = 0
        self.hover = False

        self.name, img = random.choice(list(self.SPRITES.items()))
        self.surf.blit(img, img.get_rect(center=vec(self.surf.size)/2))

        self.power_surf = pygame.transform.scale_by(self.surf, 0.35)
        self.power_shadow = pygame.mask.from_surface(self.power_surf).to_surface(setcolor=(0, 0, 0), unsetcolor=(0, 0, 0, 0))
        self.info = POWER_UP_INFO[self.name]
        self.type_ = self.info["type"]
        if self.type_ == "timed":
            self.timer = Timer(self.info["duration"], 1)
        self.cost_mod = random.randint(-10, 10)

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
        self.screen.blit(self.power_shadow, self.power_surf.get_rect(bottomright=(WIDTH - 16 + 2 - x * self.power_surf.width * 0.6, HEIGHT - 10 + 2 - y * self.power_surf.height)))
        self.screen.blit(self.power_surf, self.power_surf.get_rect(bottomright=(WIDTH - 16 - x * self.power_surf.width * 0.6, HEIGHT - 10 - y * self.power_surf.height)))

    def gui_update(self):
        a = self.angle + self.angle_offset
        self.angle_offset *= 0.975

        t = (1 - (self.angle_offset / (8 * math.pi)))
        self.ring_radius = 170 * t

        self.pos = self.anchor + vec(math.cos(a), math.sin(a)) * self.ring_radius - vec(self.surf.size)/2
        self.pos.x += 220 * t

        self.hover = self.game.mousePos.distance_to(self.pos + vec(self.surf.size)/2) < self.radius

        if self.hover:
            if pygame.mouse.get_just_pressed()[0] and self.game.player.silver >= self.info['cost'] + self.cost_mod:
                self.mode = "powerup"
                self.game.possible_powerups = []
                self.game.player.item_manager.items.add(self)
                self.parent.used = True
                self.game.player.silver -= self.info['cost'] + self.cost_mod

            self.hover_offset += (-20 - self.hover_offset) * 0.2
            self.font1.render(self.screen, self.info["name"], (255, 255, 255), (40, 70))
            
            desc_lines = wrap_text(self.info["description"], self.font2, WIDTH * 0.4)
            for i, line in enumerate(desc_lines):
                self.font2.render(self.screen, line, (255, 255, 255), (40, 80 + self.font1.space_height + i * self.font2.space_height))

            i = 0
            for effect in self.info["effects"]:
                self.font2.render(self.screen, "●", (255, 255, 255), (40, 100 + self.font1.space_height + (len(desc_lines) + i) * self.font2.space_height))
                effect_lines = wrap_text(effect, self.font2, WIDTH * 0.35)
                for j, line in enumerate(effect_lines):
                    self.font2.render(self.screen, line, (255, 255, 255), (40 + self.font2.space_width * 2, 100 + self.font1.space_height + ((len(desc_lines) + i + j) * self.font2.space_height)))
                i += 1

            self.font3.render(self.screen, f"Cost: {self.info['cost'] + self.cost_mod}", (255, 255, 255) if self.game.player.silver >= self.info['cost'] + self.cost_mod else (186, 0, 0), (40 + self.font2.space_width * 2, 100 + self.font1.space_height + ((len(desc_lines) + i + j + 2) * self.font2.space_height)))
        else:
            self.hover_offset += (0 - self.hover_offset) * 0.2

        self.screen.blit(self.shadow, self.pos + vec(6, 9 + t * 30) + self.external_offset)
        self.screen.blit(self.surf, self.pos + vec(0, t * 30 + self.hover_offset) + self.external_offset)