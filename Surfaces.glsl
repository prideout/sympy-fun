-- VS

void main() {}

-- TCS

layout(vertices = 4) out;
void main() {
    gl_TessLevelInner[0] = gl_TessLevelInner[1] =
    gl_TessLevelOuter[0] = gl_TessLevelOuter[1] = 
    gl_TessLevelOuter[2] = gl_TessLevelOuter[3] = 128;
}

-- TES

layout(quads, equal_spacing, ccw) in;

out vec3 tePosition;
out vec3 teNormal;
uniform mat4 Projection;
uniform mat4 Modelview;

const float R = 1.5;
const float r = 0.25;
const float f = 20;
const float h = 0.05;
const float Pi = 4*atan(1);
const float n = 3;

subroutine vec3 ParametricFunction(float u, float v);
subroutine uniform ParametricFunction SurfaceFunc;

void main()
{
    vec2 uv = gl_TessCoord.xy;
    vec2 p = uv * 2 * Pi;
    tePosition = SurfaceFunc(p.x, p.y);
    float du = 0.0001; float dv = 0.0001;
    vec3 C = SurfaceFunc(p.x + du, p.y);
    vec3 B = SurfaceFunc(p.x, p.y + dv);
    vec3 A = tePosition;
    teNormal = normalize(cross(C - A, B - A));
    gl_Position = Projection * Modelview * vec4(tePosition, 1);
}

// Simple Torus
subroutine(ParametricFunction)
vec3 SimpleTorusSurface(float u, float v)
{
    float x = (-R - r*cos(v))*cos(u);
    float y = (-R - r*cos(v))*sin(u);
    float z = r*sin(v);
    return vec3(x, y, z);
}

// Ridged Torus
subroutine(ParametricFunction)
vec3 RidgedTorusSurface(float u, float v)
{
    float x = R*cos(u) + (h*sin(f*u) + r)*cos(u)*cos(v);
    float y = R*sin(u) + (h*sin(f*u) + r)*sin(u)*cos(v);
    float z = (h*sin(f*u) + r)*sin(v);
    return vec3(x, y, z);
}

// Superellipse Torus
subroutine(ParametricFunction)
vec3 SuperellipseTorusSurface(float u, float v)
{
    u /= 2; // <-- cut in half
    float x = (1.0*R + 0.5*pow(abs(cos(v)), 2/n)*sign(cos(v)))*cos(u);
    float y = (1.0*R + 0.5*pow(abs(cos(v)), 2/n)*sign(cos(v)))*sin(u);
    float z = 0.5*pow(abs(sin(v)), 2/n)*sign(sin(v));
    return vec3(x, y, z);
}

// Superellipse Mobius
subroutine(ParametricFunction)
vec3 SuperellipseMobiusSurface(float u, float v)
{
    u /= 2; // <-- cut in half
    float x = (1.0*R + 0.125*sin(u/2)*pow(abs(sin(v)), 2/n)*sign(sin(v)) + 0.5*cos(u/2)*pow(abs(cos(v)), 2/n)*sign(cos(v)))*cos(u);
    float y = (1.0*R + 0.125*sin(u/2)*pow(abs(sin(v)), 2/n)*sign(sin(v)) + 0.5*cos(u/2)*pow(abs(cos(v)), 2/n)*sign(cos(v)))*sin(u);
    float z = -0.5*sin(u/2)*pow(abs(cos(v)), 2/n)*sign(cos(v)) + 0.125*cos(u/2)*pow(abs(sin(v)), 2/n)*sign(sin(v));
    return vec3(x, y, z);
}

// Spiral Shape
subroutine(ParametricFunction)
vec3 SpiralSurface(float u, float v)
{
    const float Alpha = 0.3;
    float x = Alpha*(-v/(2*Pi) + 1)*(cos(u) + 1)*cos(2*v) + 0.1*cos(2*v);
    float y = Alpha*(-v/(2*Pi) + 1)*(cos(u) + 1)*sin(2*v) + 0.1*sin(2*v);
    float z = Alpha*(-v/(2*Pi) + 1)*sin(u) + v/(2*Pi);
    return 2 * vec3(x, y, -z);
}

-- GS

out vec3 gNormal;
out vec3 gPosition;
in vec3 tePosition[3];
in vec3 teNormal[3];

uniform mat3 NormalMatrix;
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

void main()
{
    for (int i = 0; i < 3; i++) {
        gNormal = NormalMatrix * teNormal[i];
        gPosition = tePosition[i];
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
    }
    EndPrimitive();
}

-- FS

in vec3 gNormal;
in vec3 gPosition;
out vec4 FragColor;

uniform vec3 LightPosition = vec3(0.25, 0.25, 1.0);
uniform vec3 AmbientMaterial = vec3(0.04, 0.04, 0.04);
uniform vec3 SpecularMaterial = vec3(0.5, 0.5, 0.5);
uniform vec3 FrontMaterial = vec3(0.25, 0.5, 0.75);
uniform vec3 BackMaterial = vec3(0.75, 0.75, 0.7);
uniform float Shininess = 50;

void main()
{
    vec3 N = normalize(gNormal);
    if (!gl_FrontFacing)
        N = -N;
        
    vec3 L = normalize(LightPosition);
    vec3 Eye = vec3(0, 0, 1);
    vec3 H = normalize(L + Eye);
    
    float df = max(0.0, dot(N, L));
    float sf = max(0.0, dot(N, H));
    sf = pow(sf, Shininess);

    const bool Toon = false;
    if (Toon) {
        const float A = 0.1;
        const float B = 0.3;
        const float C = 0.6;
        const float D = 1.0;
	    float E = fwidth(df);
        if (df > A - E && df < A + E)
            df = mix(A, B, smoothstep(A - E, A + E, df));
        else if (df > B - E && df < B + E)
            df = mix(B, C, smoothstep(B - E, B + E, df));
        else if (df > C - E && df < C + E)
            df = mix(C, D, smoothstep(C - E, C + E, df));
        else if (df < A) df = 0.0;
        else if (df < B) df = B;
        else if (df < C) df = C;
        else df = D;
 
	    E = fwidth(sf);
        if (sf > 0.5 - E && sf < 0.5 + E) {
            sf = clamp(0.5 * (sf - 0.5 + E) / E, 0.0, 1.0);
        } else {
            sf = step(0.5, sf);
        }
    }

    vec3 P = gPosition;
    vec3 I = normalize(P);
    float cosTheta = abs(dot(I, N));
    float fresnel = 1.0 - clamp(pow(1.0 - cosTheta, 0.125), 0, 1);

    vec3 color = !gl_FrontFacing ? FrontMaterial : BackMaterial;
    vec3 lighting = AmbientMaterial + df * color;
    if (gl_FrontFacing)
        lighting += sf * SpecularMaterial;

    if (!Toon) {
        lighting += fresnel;
    }

    FragColor = vec4(lighting,1);
}
