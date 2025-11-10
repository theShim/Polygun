import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import moderngl
from array import array

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Shader_Handler:
    def __init__(self, game):
        self.game = game

        self.SHADERS = {
            "grayscale" : Sprite_Shader(self.game, "vertex_shader", "grayscale"),
            "glow"      : Sprite_Shader(self.game, "vertex_shader", "glow"),
            "invert"    : Sprite_Shader(self.game, "vertex_shader", "invert"),
        }

           ##############################################################################

class Sprite_Shader:
    def __init__(self, game, vert_path, frag_path):
        self.game = game
        self.ctx: moderngl.Context = self.game.ctx

        quad_data = array('f', [
            -1.0,  1.0,  0.0, 0.0,  # top-left
             1.0,  1.0,  1.0, 0.0,  # top-right
            -1.0, -1.0,  0.0, 1.0,  # bottom-left
             1.0, -1.0,  1.0, 1.0,  # bottom-right
        ])
        self.vbo = self.ctx.buffer(quad_data)   
        
        with open(f"scripts/shaders/{vert_path}.glsl") as file:
            vertex_shader = "".join(file.readlines())
        with open(f"scripts/shaders/{frag_path}.glsl") as file:
            frag_shader = "".join(file.readlines())

        self.prog = self.ctx.program(
            vertex_shader = vertex_shader,
            fragment_shader = frag_shader
        )
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, "2f 2f", "vert", "texcoord")]
        )   

    def apply(self, surface: pygame.Surface, shader_params: dict = dict()) -> pygame.Surface:
        width, height = surface.get_size()

        # Convert the Pygame surface to bytes, flipped vertically to match OpenGL coordinates
        tex_bytes = pygame.image.tobytes(surface, "RGBA", True)

        # Upload texture to GPU
        tex = self.ctx.texture((width, height), 4, tex_bytes)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.use(0)

        # Create framebuffer to render shader output into
        fb_tex = self.ctx.texture((width, height), 4)
        fb = self.ctx.framebuffer(color_attachments=[fb_tex])
        fb.use()

        # Clear framebuffer
        self.ctx.clear(0, 0, 0, 0)

        # Bind shader uniforms
        self.prog["tex"].value = 0

        for key in shader_params:
            if key in self.prog:
                self.prog[key].value = shader_params[key]

        # Render quad
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Read pixels from framebuffer
        data = fb.read(components=4, alignment=1)

        # Clean up
        tex.release()
        fb.release()
        fb_tex.release()
        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, *pygame.display.get_window_size())

        # Return as Pygame surface
        return pygame.image.frombytes(data, (width, height), "RGBA", True)