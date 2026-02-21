import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################

#the parent portal object with the main hitbox
class ExitPortal(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.radius = 1     #radius modifiers to lerp the size to give the effect of the portal opening
        self.max_radius = 40
        self.pause_timer = Timer(FPS, 1)
        self.activate_sound = True
        
        self.children = pygame.sprite.Group()

    def update(self):
        #if the player collides with it, trigger the relevant functionality
        if (self.game.player.pos - self.pos).magnitude() < self.radius:
            #cull any items that don't need to exist on room completion
            for spr in self.game.to_cull_on_level_complete: 
                spr.kill()
            #delete the current minimap
            self.game.state_loader.current_state.levels[self.game.state_loader.current_state.current_level_index].minimap.kill()
            self.game.state_loader.current_state.current_level_index += 1 #go to the next room
            #regenerate the "next" (current) minimap
            self.game.state_loader.current_state.levels[self.game.state_loader.current_state.current_level_index].generate_minimap()
            
            #reset the player position
            self.game.player.pos = vec(WIDTH/2 - self.game.player.size/2 + TILE_SIZE * 2.5, HEIGHT/2 - self.game.player.size/2 + TILE_SIZE * 6)
            return self.kill() #kill the portal object after the player has entered it
        
        #short delay before the portal actually spawns in, though allow the player to collide into it quickly
        #hence why it's after the above if statement
        self.pause_timer.update()
        if not self.pause_timer.finished: return
        
        #allow 1 frame to play the gate opening sound
        if self.activate_sound:
            self.game.screen_shake.start(60, 25, 0.99)
            self.game.music_player.play("exit_portal_activate", pool="ambient", loop=False)
            self.activate_sound = False
        
        #increase the portal radius size and create+update relevant child particles
        self.radius = self.radius + (self.max_radius - self.radius) * 0.05
        for i in range(3):
            PortalParticle(self.game, [self.children], self.pos, random.randint(int(20 * (self.radius / self.max_radius)), int(40 * (self.radius / self.max_radius))))
        self.children.update(None) #update without rendering
        self.render()

    def render(self):
        rect = pygame.Rect(0, 0, self.radius * 2.5, self.radius * 2)
        rect.center = self.pos - self.game.offset

        #render all the background white parts
        pygame.draw.ellipse(self.game.emissive_surf, (255, 255, 255), rect.inflate(12, 12), 4)
        pygame.draw.ellipse(self.screen, (255, 255, 255), rect.inflate(12, 12))
        self.children.update(False) #render white

        #render foreground black parts
        pygame.draw.ellipse(self.game.emissive_surf, (0, 0, 0), rect)
        pygame.draw.ellipse(self.screen, (0, 0, 0), rect)
        self.children.update(True) #render black

#particles the portal emits that seem to bubble out of it
class PortalParticle(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, radius=20):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.pos.x += random.uniform(-radius, radius) #random offset across the portal frame
        self.radius = radius
        self.decay = max(0.5, random.random()) #for the particle radius to decrease 
        self.vel = vec()

    def update(self, draw_flag=False):
        if draw_flag != None:
            return self.draw(draw_flag)

        self.radius -= self.decay #decrement radius by the random decay factor
        self.vel += vec(random.uniform(-self.radius / 10, self.radius / 10) * 0.225, random.uniform(-self.radius / 10, self.radius / 10) * 0.225)
        self.vel *= 0.9 #decrease outward velocity
        if self.radius <= 1: #kill flag for particles since less than 1 isn't visible
            return self.kill()
        
        self.pos += self.vel

    def draw(self, draw_flag):
        if draw_flag in ["bg", False]: #draw white background
            pygame.draw.circle(self.game.emissive_surf, (255, 255, 255), self.pos - self.game.offset, self.radius)
            pygame.draw.circle(self.screen, (255, 255, 255), self.pos - self.game.offset, self.radius)
        elif draw_flag in ["fg", True]: #draw black foreground
            pygame.draw.circle(self.game.emissive_surf, (0, 0, 0), self.pos - self.game.offset, self.radius * 0.8)
            pygame.draw.circle(self.screen, (0, 0, 0), self.pos - self.game.offset, self.radius * 0.8)