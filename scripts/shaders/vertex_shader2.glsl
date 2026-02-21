#version 330 core

in vec2 vert;
out vec2 uvs;

void main() {
    uvs = vert * 0.5 + 0.5;
    gl_Position = vec4(vert, 0.0, 1.0);
}