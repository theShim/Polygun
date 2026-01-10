#version 330

uniform sampler2D sceneTex;
in vec2 uvs;
out vec4 f_colour;

void main() {
    vec3 color = texture(sceneTex, uvs).rgb;
    float brightness = max(color.r, max(color.g, color.b));

    if (brightness > 1.0)
        f_colour = vec4(color, 1.0);
    else
        f_colour = vec4(0.0);
}