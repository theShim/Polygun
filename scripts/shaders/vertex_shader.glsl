#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

uniform float zoom;

void main() {
    zoom;
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);

    // vec2 center = vec2(0.5, 0.5);
    // uvs = (texcoord - center) / zoom + center;
}