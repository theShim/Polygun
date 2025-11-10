#version 330 core

uniform sampler2D tex;
in vec2 uvs;
out vec4 f_colour;

void main() {
    vec4 color = texture(tex, uvs);
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    f_colour = vec4(gray, gray, gray, color.a);
}