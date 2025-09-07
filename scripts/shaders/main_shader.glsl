#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 uvs;
out vec4 f_color;

vec2 pixelate(vec2 uv) {
    float Pixels = 512.0 * 32;
    float dx = 32.0 * (1.0 / Pixels);
    float dy = 32.0 * (1.0 / Pixels);
    return vec2(dx * floor(uv.x / dx), dy * floor(uv.y / dy));
}

void main() {
    time;
    f_color = vec4(texture(tex, uvs).rgb, 1.0);
}
