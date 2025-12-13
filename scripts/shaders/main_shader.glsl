#version 330 core

uniform sampler2D tex;
uniform sampler2D noiseTex;
uniform float time;

in vec2 uvs;
out vec4 f_color;

vec2 pixelate(vec2 uv) {
    float Pixels = 512.0 * 2048;
    float dx = 32.0 * (1.0 / Pixels);
    float dy = 32.0 * (1.0 / Pixels);
    return vec2(dx * floor(uv.x / dx), dy * floor(uv.y / dy));
}

vec3 vignette(vec2 uv, vec3 col) {
    // float offset = floor(time * 0.004) * 0.2;
    // vec2 noiseSample = texture(noiseTex, uv * 10 - offset).rg - 0.5;
    // uv += noiseSample * 0.1;

    vec2 circ_center = vec2(0.5, 0.5);
    float dist = distance(uv, circ_center);
    float vig = smoothstep(0.58, 0.3, dist); // inner < outer = fade inward
    return col * mix(0.4, 1.1, vig); // inner = darker edge
}

void main() {
    time;
    noiseTex;
    f_color = vec4(texture(tex, pixelate(uvs)).rgb, 1.0);

    
    vec2 uv = uvs;

    float pencilOffset = floor(time * 0.004) * 0.2;
    vec2 noiseSample = texture(noiseTex, uv / 6.0 + pencilOffset).rg - 0.5;
    uv += noiseSample * 0.0025;

    vec3 color = texture(tex, uv).rgb;
    // float detail = (texture(noiseTex, uv + pencilOffset).b - 0.5) * 0.03;
    // detail += (texture(noiseTex, uv * 4.0 - pencilOffset / 3.0).b - 0.5) * 0.015;

    vec3 pencil = color;// + detail * 1.2;
    pencil = mix(color, pencil, 0.9); // blend strength
    pencil = clamp(pencil, 0.0, 1.0);

    // Optional: tiny warm tint (looks like paper reflection)
    pencil *= vec3(1.05, 1.02, 0.97);

    vec3 final_colour = vignette(uvs, pencil);

    f_color = vec4(final_colour, 1.0);

}
