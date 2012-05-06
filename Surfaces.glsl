-- VS

in vec2 Position;
out vec2 vPosition;

void main()
{
    vPosition = Position;
}

-- TCS

uniform float TessLevel = 16;

layout(vertices = 3) out;
in vec2 vPosition[];
out vec2 tcPosition[];

void main()
{
    tcPosition[gl_InvocationID] = vPosition[gl_InvocationID];
    gl_TessLevelInner[0] = gl_TessLevelOuter[0] =
    gl_TessLevelOuter[1] = gl_TessLevelOuter[2] = TessLevel;
}

-- TES

layout(triangles, equal_spacing, ccw) in;

in vec2 tcPosition[];
out vec3 tePosition;
out vec3 teNormal;
uniform mat4 Projection;
uniform mat4 Modelview;

const float R = 1.5;
const float r = 0.25;

// Ridge frequency and height:
const float f = 20;
const float h = 0.05;

subroutine vec3 ParametricFunction(float u, float v);
subroutine uniform ParametricFunction SurfaceFunc;
subroutine uniform ParametricFunction NormalFunc;

// Simple Torus
subroutine(ParametricFunction)
vec3 SimpleTorusSurface(float u, float v)
{
    float x = (-R - r*cos(v))*cos(u);
    float y = (-R - r*cos(v))*sin(u);
    float z = r*sin(v);
    return vec3(x, y, z);
}
subroutine(ParametricFunction)
vec3 SimpleTorusNormal(float u, float v)
{
    float x = r*(-R - r*cos(v))*cos(u)*cos(v);
    float y = r*(-R - r*cos(v))*sin(u)*cos(v);
    float z = r*(R + r*cos(v))*sin(v);
    return normalize(vec3(x, y, z));
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
subroutine(ParametricFunction)
vec3 RidgedTorusNormal(float u, float v)
{
    float x = -f*h*(h*sin(f*u) + r)*sin(u)*pow(cos(v), 2)*cos(f*u) + f*h*(h*sin(f*u) + r)*sin(u)*cos(f*u) + (h*sin(f*u) + r)*(R*cos(u) + f*h*sin(u)*cos(v)*cos(f*u) + (h*sin(f*u) + r)*cos(u)*cos(v))*cos(v);
    float y = f*h*(h*sin(f*u) + r)*cos(u)*pow(cos(v), 2)*cos(f*u) - f*h*(h*sin(f*u) + r)*cos(u)*cos(f*u) + (-h*sin(f*u) - r)*(-R*sin(u) + f*h*cos(u)*cos(v)*cos(f*u) + (-h*sin(f*u) - r)*sin(u)*cos(v))*cos(v);
    float z = (-h*sin(f*u) - r)*(-R*sin(u) + f*h*cos(u)*cos(v)*cos(f*u) + (-h*sin(f*u) - r)*sin(u)*cos(v))*sin(u)*sin(v) + (h*sin(f*u) + r)*(R*cos(u) + f*h*sin(u)*cos(v)*cos(f*u) + (h*sin(f*u) + r)*cos(u)*cos(v))*sin(v)*cos(u);
    return normalize(vec3(x, y, z));
}

void main()
{
    vec2 p0 = gl_TessCoord.x * tcPosition[0];
    vec2 p1 = gl_TessCoord.y * tcPosition[1];
    vec2 p2 = gl_TessCoord.z * tcPosition[2];
    vec2 p = (p0 + p1 + p2);

    tePosition = SurfaceFunc(p.x, p.y);
    teNormal = NormalFunc(p.x, p.y);

    gl_Position = Projection * Modelview * vec4(tePosition, 1);
}

-- GS

out vec3 gNormal;
in vec3 tePosition[3];
in vec3 teNormal[3];

uniform mat3 NormalMatrix;
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

void main()
{
    for (int i = 0; i < 3; i++) {
        gNormal = NormalMatrix * teNormal[i];
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
    }

    EndPrimitive();
}

-- FS

in vec3 gNormal;
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

    vec3 color = gl_FrontFacing ? FrontMaterial : BackMaterial;
    vec3 lighting = AmbientMaterial + df * color;
    if (gl_FrontFacing)
        lighting += sf * SpecularMaterial;

    FragColor = vec4(lighting,1);
}
