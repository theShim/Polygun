#version 330

uniform sampler2D sceneTex;
uniform sampler2D bloomTex;
uniform float bloomStrength;

in vec2 uvs;
out vec4 f_colour;

void main() {
    vec3 scene = texture(sceneTex, uvs).rgb;
    vec3 bloom = texture(bloomTex, uvs).rgb;
    f_colour = vec4(scene + bloom * bloomStrength, 1.0);
}