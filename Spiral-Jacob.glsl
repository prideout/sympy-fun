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

uniform float TessLevel = 6;

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
const float pi = 3.141;

// u and v in [0,2π] 
// x(u,v) = α (1-v/(2π)) cos(n v) (1 + cos(u)) + γ cos(n v)
// y(u,v) = α (1-v/(2π)) sin(n v) (1 + cos(u)) + γ sin(n v)
// z(u,v) = α (1-v/(2π)) sin(u) + β v/(2π)
vec3 HornPosition(float u, float v, float alpha)
{
    float x = alpha*(-v/(2*pi) + 1)*(cos(u) + 1)*cos(2*v) + 0.1*cos(2*v);
    float y = alpha*(-v/(2*pi) + 1)*(cos(u) + 1)*sin(2*v) + 0.1*sin(2*v);
    float z = alpha*(-v/(2*pi) + 1)*sin(u) + v/(2*pi);
    return vec3(x, y, z);
}

vec3 HornNormal(float u, float v, float alpha)
{
    float v2 = v*v;
    float pi2 = pi*pi;
    float x = -alpha*(-v/(2*pi) + 1)*(-alpha*sin(u)/(2*pi) + 1/(2*pi))*sin(u)*sin(2*v) - alpha*(-v/(2*pi) + 1)*(2*alpha*(-v/(2*pi) + 1)*(cos(u) + 1)*cos(2*v) - alpha*(cos(u) + 1)*sin(2*v)/(2*pi) + 0.2*cos(2*v))*cos(u);
    float y = alpha*(-v/(2*pi) + 1)*(-alpha*sin(u)/(2*pi) + 1/(2*pi))*sin(u)*cos(2*v) + alpha*(-v/(2*pi) + 1)*(-2*alpha*(-v/(2*pi) + 1)*(cos(u) + 1)*sin(2*v) - alpha*(cos(u) + 1)*cos(2*v)/(2*pi) - 0.2*sin(2*v))*cos(u);
    float z = alpha*(-0.5*alpha*v2*cos(u) - 0.5*alpha*v2 + 2.0*pi*alpha*v*cos(u) + 2.0*pi*alpha*v - 2.0*pi2*alpha*cos(u) - 2.0*pi2*alpha + 0.1*pi*v - 0.2*pi2)*sin(u)/pi2;
    return normalize(-vec3(x, y, z));
}

// http://http.developer.nvidia.com/GPUGems/gpugems_ch42.html

// Actually, you only need a Jacobian if your deformer operates in 3-space (instead of the domain)
// Otherwise it's business as usual.  Compose two parametric equations an enjoy.

mat3 JacobianDisplacement(vec3 p)
{
   return mat3(1,0,0,0,1,0,0,0,1);
}

mat3 HornBasis(float u, float v, float alpha)
{
   return mat3(1,0,0,0,1,0,0,0,1);
}

const float Time = 0;

void main()
{
    float t = mod(Time*2, 2.0);if (t > 1) t = 1-(t-1); t = t*t;
    float alpha = t * 0.7 + 0.15;
    float scale = (2.0 - t);

    vec2 p0 = gl_TessCoord.x * tcPosition[0];
    vec2 p1 = gl_TessCoord.y * tcPosition[1];
    vec2 p2 = gl_TessCoord.z * tcPosition[2];
    vec2 p = (p0 + p1 + p2);

    tePosition = HornPosition(p.x, p.y, alpha);

    mat3 j = JacobianDisplacement(tePosition);
    mat3 b = HornBasis(p.x, p.y, alpha);

    tePosition += b.z * HornDisplacement(p.x, p.y);
    teNormal = normalize(Cross(j * b.x, j * b.y));

    gl_Position = Projection * Modelview * vec4(scale * tePosition, 1);
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
