#version 330 core

uniform sampler2D tex;
in vec2 uvs;
out vec4 f_colour;

void main() {
    vec4 color = texture(tex, uvs);
    f_colour = vec4(1.0 - color.r, 1.0 - color.g, 1.0 - color.b, color.a);
}