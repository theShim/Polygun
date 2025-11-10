#version 330 core

uniform sampler2D tex;
uniform vec2 resolution;
uniform float intensity;  //glow strength
uniform float radius;     //blur radius (px)

in vec2 uvs;
out vec4 f_colour;

void main() {
    vec2 texel = 1.0 / resolution;
    vec3 baseColor = texture(tex, uvs).rgb;
    float brightness = dot(baseColor, vec3(0.299, 0.587, 0.114));

    vec3 glow = vec3(0.0);
    if (brightness > 0.5) {  // threshold
        // Simple blur around the pixel
        for (int x = -3; x <= 3; ++x) {
            for (int y = -3; y <= 3; ++y) {
                vec2 offset = vec2(x, y) * texel * radius;
                glow += texture(tex, uvs + offset).rgb;
            }
        }
        glow /= 49.0;  // average samples
    }

    vec3 color = baseColor + glow * intensity;

    f_colour = vec4(color, 1.0);
}