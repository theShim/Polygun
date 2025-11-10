#version 330 core

uniform sampler2D tex;
uniform sampler2D noiseTex;
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

    
    vec2 uv = uvs;

    float pencilOffset = floor(time * 0.004) * 0.2;
    vec2 noiseSample = texture(noiseTex, uv / 6.0 + pencilOffset).rg - 0.5;
    uv += noiseSample * 0.002;

    vec3 color = texture(tex, uv).rgb;
    // float detail = (texture(noiseTex, uv + pencilOffset).b - 0.5) * 0.03;
    // detail += (texture(noiseTex, uv * 4.0 - pencilOffset / 3.0).b - 0.5) * 0.015;

    vec3 pencil = color;// + detail * 1.2;
    pencil = mix(color, pencil, 0.7); // blend strength
    pencil = clamp(pencil, 0.0, 1.0);

    // Optional: tiny warm tint (looks like paper reflection)
    pencil *= vec3(1.05, 1.02, 0.97);

    f_color = vec4(pencil, 1.0);

}
