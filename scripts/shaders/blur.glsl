#version 330

uniform sampler2D image;
uniform vec2 axis;   // (1.0, 0.0) for horizontal, (0.0, 1.0) for vertical
uniform vec2 texelSize;   // (1.0 / width, 1.0 / height)
uniform int radius;
uniform float sigma;

in vec2 uvs;
out vec4 f_colour;

float gaussian(float x, float sigma) {
    return exp(-(x * x) / (2.0 * sigma * sigma)) * (1 / sqrt(2.0 * sigma * sigma * 3.141539));
}

void main()
{
    image;
    axis;
    texelSize;
    uvs;

    vec3 result = vec3(0.0);
    float totalWeight = 0.0;

    for (int i = -radius; i <= radius; i++) {
        float w = gaussian(float(i), sigma);
        vec2 offset = axis * texelSize * float(i);
        result += texture(image, uvs + offset).rgb * w;
        totalWeight += w;
    }

    result /= totalWeight; // normalize
    f_colour = vec4(result, 1.0);
}