#version 330 core

uniform sampler2D tex;
uniform sampler2D noiseTex;
uniform sampler2D bloomTex;
uniform float time;

in vec2 uvs;
out vec4 f_colour;

vec2 pixelate(vec2 uv) {
    float Pixels = 512.0 * 2048;
    float dx = 32.0 * (1.0 / Pixels);
    float dy = 32.0 * (1.0 / Pixels);
    return vec2(dx * floor(uv.x / dx), dy * floor(uv.y / dy));
}

vec3 vignette(vec2 uv, vec3 col) {
    vec2 circ_center = vec2(0.5, 0.5);
    float dist = distance(uv, circ_center);
    float vig = smoothstep(0.58, 0.3, dist); // inner < outer = fade inward
    return col * mix(0.4, 1.1, vig); // inner = darker edge
}

void main() {
    time;
    noiseTex;

    // float brightness = dot(texture(tex, uvs).rgb , vec3(0.2126, 0.7152, 0.0722));
    // if(brightness > 0.8) f_colour = vec4(0., 0., 0., 1.0);
    // else

    vec3 final_colour = texture(tex, uvs).rgb * 0.45 + texture(bloomTex, uvs).rgb;
    // f_colour = vec4(final_colour, 1.0);

    // vec4 colour = texture(tex, uvs);
    // if (colour.a < 0.01) discard;
    // vec3 emissive = vec3(1.0, 0.8, 0.3);
    // vec3 hdr = colour.rgb + emissive * 1.0 * colour.a;
    // f_colour = vec4(hdr, 1.0);

    
    // vec2 uv = uvs;

    // float pencilOffset = floor(time * 0.004) * 0.2;
    // vec2 noiseSample = texture(noiseTex, uv / 6.0 + pencilOffset).rg - 0.5;
    // uv += noiseSample * 0.0025;

    // vec3 color = texture(tex, uv).rgb;
    // // float detail = (texture(noiseTex, uv + pencilOffset).b - 0.5) * 0.03;
    // // detail += (texture(noiseTex, uv * 4.0 - pencilOffset / 3.0).b - 0.5) * 0.015;

    // vec3 pencil = color;// + detail * 1.2;
    // pencil = mix(color, pencil, 0.9); // blend strength
    // pencil = clamp(pencil, 0.0, 1.0);

    // // Optional: tiny warm tint (looks like paper reflection)
    // pencil *= vec3(1.05, 1.02, 0.97);

    final_colour = vignette(uvs, final_colour);

    f_colour = vec4(final_colour, 1.0);

}
