#version 330

uniform sampler2D image;
uniform vec2 axis;   //(1.0, 0.0) for horizontal, (0.0, 1.0) for vertical
uniform vec2 texelSize;
uniform int radius;
uniform float sigma;

in vec2 uvs;
out vec4 f_colour;

//calculates the weight for some distance away from the center of the screen
//with sigma controlling how sharply it falls off based on the bell curve equation
float gaussian(float x, float sigma) {
    return exp(-(x * x) / (2.0 * sigma * sigma)) * (1 / sqrt(2.0 * sigma * sigma * 3.141539));
}

void main()
{
    image;
    axis;
    texelSize;
    uvs;

    vec3 result = vec3(0.0);    //the resulting colour
    float totalWeight = 0.0;    //the total gaussian weight

    //for every pixel, check every offset pixel along the relevant axis from
    //-radius to +radius for its colour and sample a weighted colour at that pixel
    for (int i = -radius; i <= radius; i++) {
        float w = gaussian(float(i), sigma);
        vec2 offset = axis * texelSize * float(i);
        result += texture(image, uvs + offset).rgb * w;
        totalWeight += w;
    }

    result /= totalWeight;  //just to normalize the total colour
    f_colour = vec4(result, 1.0);
}