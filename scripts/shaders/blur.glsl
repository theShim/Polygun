#version 330

uniform sampler2D image;
uniform vec2 axis;   // (1.0, 0.0) for horizontal, (0.0, 1.0) for vertical
uniform vec2 texelSize;   // (1.0 / width, 1.0 / height)

in vec2 uvs;
out vec4 f_colour;

void main()
{
    vec3 result = vec3(0.0);

    // Gaussian weights (sigma ≈ 3.0)
    float weights[5] = float[](
        0.227027,
        0.1945946,
        0.1216216,
        0.054054,
        0.016216
    );

    result += texture(image, uvs).rgb * weights[0];

    for (int i = 1; i < 5; ++i) {
        vec2 offset = axis * texelSize * float(i);
        result += texture(image, uvs + offset).rgb * weights[i];
        result += texture(image, uvs - offset).rgb * weights[i];
    }

    f_colour = vec4(result, 1.0);
}