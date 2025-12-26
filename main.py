import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
import moderngl

import sys
from array import array
import numpy as np

from scripts.entities.player import Player
from scripts.gui.custom_fonts import Custom_Font
from scripts.gui.health_bar import HealthBar
from scripts.gui.crosshair import CrossHair
from scripts.shaders.shader import Shader_Handler
from scripts.states.state_loader import State_Loader
from scripts.controls.controller_handler import ControlsHandler
from scripts.world_loading.tilemap import Tile

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *
from scripts.utils.debugger import Debugger

if DEBUG:
    #code profiling for performance optimisations
    import pstats
    import cProfile
    import io

# print(countLinesIn(os.path.dirname(os.path.abspath(__file__))))

    ##############################################################################################

def create_noise_texture(ctx: moderngl.Context, size=256):
    """Generate a simple procedural noise texture."""
    # random grayscale noise, shape (height, width, channels)
    noise = np.random.rand(size, size, 3).astype('f4')  # RGB noise
    tex = ctx.texture((size, size), 3, (noise * 255).astype('u1').tobytes())
    tex.build_mipmaps()
    tex.repeat_x = True
    tex.repeat_y = True
    return tex

class Game:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #initalising pygame window
        flags = pygame.SCALED | pygame.DOUBLEBUF | pygame.OPENGL
        self.window = pygame.display.set_mode(SIZE, flags, vsync=1)
        self.screen = pygame.Surface(SIZE, pygame.SRCALPHA)
        pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.offset = vec()
        self.zoom = 1.0
        self.events = None

        #opengl stuff
        self.initialise_opengl()
        self.t = 0

        #caching
        self.cache_sprites()
        
        self.controls_handler = ControlsHandler(self)

        #groups
        self.all_sprites = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.gui_elements = pygame.sprite.Group()

        self.state_loader = State_Loader(self, start="dungeon")
        self.state_loader.populate_states()
        pygame.mouse.set_visible(False)

        self.debugger = Debugger(self)

        self.surf = pygame.Surface((100, 100))
        self.k = 0

        self.player = Player(self, [self.all_sprites, self.entities])

        HealthBar(self, [self.gui_elements])
        CrossHair(self, [self.gui_elements])

    @property
    def mousePos(self) -> vec:
        mousePos = pygame.mouse.get_pos()
        window_size = pygame.display.get_window_size()  # actual window size (after scaling)
        scale_x = WIDTH / window_size[0]
        scale_y = HEIGHT / window_size[1]
        mousePos = vec(mousePos[0] * scale_x, mousePos[1] * scale_y)
        return mousePos

        ####################################################################################

    def initialise(self):
        pygame.init()  #general pygame
        pygame.font.init() #font stuff
        pygame.display.set_caption(WINDOW_TITLE) #Window Title 

        pygame.joystick.init()

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
        
        self.noise_tex = create_noise_texture(self.ctx)
        
        self.shader_handler = Shader_Handler(self)
        # self.original_viewport = [i for i in self.ctx.viewport]

    def surf_to_text(self, surf: pygame.Surface) -> moderngl.Texture:
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = "BGRA"
        tex.repeat_x = tex.repeat_y = not False
        tex.write(surf.get_view("1"))
        return tex
    
    def quit(self):
        self.running = False
        self.controls_handler.save_json()

        ####################################################################################

    def cache_sprites(self):
        Tile.cache_sprites()
        Custom_Font.init()
        # Player.cache_sprites()

    def calculate_offset(self):
        #have the screen offset kinda lerp to the player location
        target_x = self.player.pos.x - WIDTH/2
        target_y = self.player.pos.y - HEIGHT/2

        mouse_dx = max(-WIDTH/2, min(WIDTH/2, self.mousePos.x - WIDTH / 2)) / 3.5
        mouse_dy = max(-HEIGHT/2, min(HEIGHT/2, self.mousePos.y - HEIGHT / 2)) / 3.5

        target_x += mouse_dx
        target_y += mouse_dy
        
        self.offset.x += (target_x - self.offset.x) / CAMERA_FOLLOW_SPEED
        self.offset.y += (target_y - self.offset.y) / CAMERA_FOLLOW_SPEED

    def calculate_zoom(self):
        pass

        ####################################################################################

    def run(self):
        if DEBUG:
            PROFILER = cProfile.Profile()
            PROFILER.enable()

        last_time = pygame.time.get_ticks()
        self.running = True
        while self.running:
            #deltatime
            self.dt = (current_time := pygame.time.get_ticks()) - last_time
            self.dt /= 1000
            last_time = current_time
            
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.quit()

                elif event.type == pygame.JOYDEVICEADDED:
                    self.controls_handler.add_controller(event.device_index)
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self.controls_handler.remove_controller(event.instance_id)
                    
            self.screen.fill((35, 34, 43))
            # self.calculate_offset()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_MINUS]: self.zoom /= 1.05
            if keys[pygame.K_EQUALS]: self.zoom *= 1.05

            # self.k += math.radians(4)
            # surf = self.surf
            # self.surf.fill((255 * abs(math.sin(self.k)), 0, 0), [0, 0, 100, 100])
            # self.surf.fill((0, 0, 255), [50, 0, 50, 100])
            # surf = self.shader_handler.SHADERS["invert"].apply(self.surf)
            # surf.set_colorkey((0, 0, 0, 0))
            # self.screen.blit(surf, (100, 40) - self.offset)


            # for spr in sorted(self.all_sprites, key=lambda spr: spr.pos.y):
            #     spr.update()

            self.state_loader.update()
            self.gui_elements.update()


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
            
            self.noise_tex.use(1)  # bind to texture unit 1
            self.program['noiseTex'].value = 1

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