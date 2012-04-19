-- VS

in vec2 Position;
out vec2 vPosition;

uniform mat4 Projection;
uniform mat4 Modelview;
uniform mat4 ViewMatrix;
uniform mat4 ModelMatrix;

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

// u and v in [0,2π] 
vec3 TorusPosition(float u, float v)
{
    float x = (R + h*sin(f*u)*cos(v) + r*cos(v))*cos(u);
    float y = (R + h*sin(f*u)*cos(v) + r*cos(v))*sin(u);
    float z = (h*sin(f*u) + r)*sin(v);
    return vec3(x, y, z);
}

vec3 TorusNormal(float u, float v)
{
    float sv2 = sin(v)*sin(v);
    float su2 = sin(u)*sin(u);
    float cu2 = cos(u)*cos(u);
    float cfu2 = cos(f*u)*cos(f*u);
    float h2 = h*h;
    float r2 = r*r;
    float x = f*h*(h*sin(f*u) + r)*(su2 + cu2)*sin(u)*sv2*cos(f*u) + (h*sin(f*u) + r)*(f*h*sin(u)*cos(v)*cos(f*u) + (R + (h*sin(f*u) + r)*cos(v))*cos(u))*(su2 + cu2)*cos(v);
    float y = -f*h*(h*sin(f*u) + r)*(su2 + cu2)*sv2*cos(u)*cos(f*u) - (h*sin(f*u) + r)*(f*h*cos(u)*cos(v)*cos(f*u) - (R + (h*sin(f*u) + r)*cos(v))*sin(u))*(su2 + cu2)*cos(v);
    float z = (R*h*sin(f*u) + R*r - h2*su2*cos(v)*cfu2 + h2*su2*cos(v) - h2*cu2*cos(v)*cfu2 + h2*cu2*cos(v) + 2*h*r*sin(f*u)*cos(v) + r2*cos(v))*sin(v);
    return normalize(vec3(x, y, z));
}

void main()
{
    vec2 p0 = gl_TessCoord.x * tcPosition[0];
    vec2 p1 = gl_TessCoord.y * tcPosition[1];
    vec2 p2 = gl_TessCoord.z * tcPosition[2];
    vec2 p = (p0 + p1 + p2);

    tePosition = TorusPosition(p.x, p.y);
    teNormal = TorusNormal(p.x, p.y);

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
