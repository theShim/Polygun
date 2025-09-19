import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
import moderngl

# from scripts.states.state_machine import State_Loader

import sys
from array import array

from scripts.entities.player import Player

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *
# from scripts.utils.debugger import Debugger

if DEBUG:
    #code profiling for performance optimisations
    import pstats
    import cProfile
    import io

    ##############################################################################################

class Game:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #initalising pygame window
        flags = pygame.SCALED | pygame.DOUBLEBUF | pygame.OPENGL
        self.window = pygame.display.set_mode(SIZE, flags, vsync=1)
        self.screen = pygame.Surface(SIZE)
        pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.offset = vec()
        self.zoom = 1.0

        #opengl stuff
        self.initialise_opengl()
        self.t = 0

        #caching
        self.cache_sprites()

        #groups
        self.all_sprites = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()

        #
        # self.state_loader = State_Loader(self, start="debug")
        # self.state_loader.populate_states()

        # self.debugger = Debugger(self)


        self.player = Player(self, [self.all_sprites, self.entities])

        ####################################################################################

    def initialise(self):
        pygame.init()  #general pygame
        pygame.font.init() #font stuff
        pygame.display.set_caption(WINDOW_TITLE) #Window Title 

        pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
        pygame.mixer.init()

        pygame.event.set_blocked(None) #setting allowed events to reduce lag
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])

    def initialise_opengl(self):
        self.ctx = moderngl.create_context()

        self.quad_buffer = self.ctx.buffer(data=array("f", [
            #position (x, y), uv (x, y); each line = new coord; xy E [-1, 1], uv E [0, 1]
            -1.0, 1.0,  0.0, 0.0, #topleft
            1.0,  1.0,  1.0, 0.0, #topright
            -1.0, -1.0, 0.0, 1.0, #bottomleft
            1.0,  -1.0, 1.0, 1.0, #bottomright
        ]))

        with open("scripts/shaders/vertex_shader.glsl") as file:
            self.vertex_shader = "".join(file.readlines())

        with open("scripts/shaders/main_shader.glsl") as file:
            self.frag_shader = "".join(file.readlines())

        self.program = self.ctx.program(vertex_shader=self.vertex_shader, fragment_shader=self.frag_shader)
        self.opengl_renderer = self.ctx.vertex_array(self.program, [(self.quad_buffer, "2f 2f", "vert", "texcoord")])

    def surf_to_text(self, surf: pygame.Surface) -> moderngl.Texture:
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = "BGRA"
        tex.repeat_x = tex.repeat_y = not False
        tex.write(surf.get_view("1"))
        return tex

        ####################################################################################

    def cache_sprites(self):
        return
        Player.cache_sprites()

    def calculate_offset(self):
        #have the screen offset kinda lerp to the player location
        self.offset.x += (self.player.rect.centerx - WIDTH/2 - self.offset.x) / CAMERA_FOLLOW_SPEED
        self.offset.y += (self.player.rect.centery - HEIGHT/2 - self.offset.y) / CAMERA_FOLLOW_SPEED

        #restricting the offsets
        #MAKE THIS DIFFERENT ACCORDING TO CUSTOM STAGE SIZES LATER
        #e.g. if self.offset.x < self.stage.offset.bounds[0]: x = self.stage.offset.bounds[0]
        if self.offset.x < 0:
            self.offset.x = 0
        # if self.offset.x > math.inf:
        #     self.offset.x = math.inf

    def calculate_zoom(self):
        pass

        ####################################################################################

    def run(self):
        if DEBUG:
            PROFILER = cProfile.Profile()
            PROFILER.enable()

        last_time = pygame.time.get_ticks()
        running = True
        while running:
            #deltatime
            self.dt = (current_time := pygame.time.get_ticks()) - last_time
            self.dt /= 1000
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    
            self.screen.fill((18, 35, 54))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_MINUS]: self.zoom /= 1.05
            if keys[pygame.K_EQUALS]: self.zoom *= 1.05

            self.all_sprites.update()

            # self.state_loader.update()


            if DEBUG:
                debug_info = f"FPS: {int(self.clock.get_fps())}"
                self.debugger.add_text(debug_info)
                self.debugger.update()

            
            #opengl drawing
            self.t += self.dt * 1000
            frame_tex = self.surf_to_text(self.screen)
            frame_tex.use(0)

            self.program["tex"] = 0 #dict assignment usually means uniform
            self.program["time"] = self.t
            self.program["zoom"] = self.zoom

            self.opengl_renderer.render(mode=moderngl.TRIANGLE_STRIP)
            frame_tex.release()

            pygame.display.flip()
            self.clock.tick(60)

        if DEBUG:
            PROFILER.disable()
            PROFILER.dump_stats("test.stats")
            pstats.Stats("test.stats", stream=(s:=io.StringIO())).sort_stats((sortby:=pstats.SortKey.CUMULATIVE)).print_stats()
            print(s.getvalue())

        pygame.quit()
        sys.exit()
    

    ##############################################################################################

if __name__ == "__main__":
    game = Game()
    game.run()