#include <stdlib.h>
#include <png.h>
#include "pez.h"
#include "vmath.h"

struct SceneParameters {
    int IndexCount;
    float Time;
    Matrix4 Projection;
    Matrix4 Modelview;
    Matrix4 ViewMatrix;
    Matrix4 ModelMatrix;
    Matrix3 NormalMatrix;
} Scene;

static GLuint LoadProgram(const char* vsKey, const char* tcsKey, const char* tesKey, const char* gsKey, const char* fsKey);
static GLuint CurrentProgram();

#define u(x) glGetUniformLocation(CurrentProgram(), x)
#define a(x) glGetAttribLocation(CurrentProgram(), x)
#define OpenGLError GL_NO_ERROR == glGetError(),                        \
        "%s:%d - OpenGL Error - %s", __FILE__, __LINE__, __FUNCTION__   \

PezConfig PezGetConfig()
{
    PezConfig config;
    config.Title = __FILE__;
    config.Width = 800*3/2;
    config.Height = 600*3/2;
    config.Multisampling = true;
    config.VerticalSync = true;
    return config;
}

void PezInitialize()
{
    LoadProgram("VS", "TCS", "TES", "GS", "FS");
    PezConfig cfg = PezGetConfig();
    const float z[2] = {5, 90};
    const float fov = 0.55;
    float aspect = (float) cfg.Width / cfg.Height;
    Scene.Projection = M4MakePerspective(fov, aspect, z[0], z[1]);
    Scene.Time = 0;
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.2f, 0.2f, 0.2f, 1.0f);
    GLuint vao;
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);
    pezCheck(OpenGLError);
}

void PezUpdate(float seconds)
{
    const float RadiansPerSecond = 0.75f;
    Scene.Time += seconds;
    float theta = Scene.Time * RadiansPerSecond;
   
    // Create the model-view matrix:
    //Scene.ModelMatrix = M4MakeRotationX(theta);
    Scene.ModelMatrix = M4MakeRotationZYX((Vector3){theta, theta, theta});

    Point3 eye = {0, -5, 5};
    Point3 target = {0, 0, 0};
    Vector3 up = {0, 1, 0};
    Scene.ViewMatrix = M4MakeLookAt(eye, target, up);
    Scene.Modelview = M4Mul(Scene.ViewMatrix, Scene.ModelMatrix);
    Scene.NormalMatrix = M4GetUpper3x3(Scene.Modelview);
}

void PezRender()
{
    // Set up uniforms:
    float* pModel = (float*) &Scene.ModelMatrix;
    float* pView = (float*) &Scene.ViewMatrix;
    float* pModelview = (float*) &Scene.Modelview;
    float* pProjection = (float*) &Scene.Projection;
    float* pNormalMatrix = (float*) &Scene.NormalMatrix;
    glUniformMatrix4fv(u("ViewMatrix"), 1, 0, pView);
    glUniformMatrix4fv(u("ModelMatrix"), 1, 0, pModel);
    glUniformMatrix4fv(u("Modelview"), 1, 0, pModelview);
    glUniformMatrix4fv(u("Projection"), 1, 0, pProjection);
    glUniformMatrix3fv(u("NormalMatrix"), 1, 0, pNormalMatrix);
    glUniform1f(u("Time"), Scene.Time);

    // Make sure there are two subroutines we can pick:
    GLenum prog = CurrentProgram();
    GLenum stage = GL_TESS_EVALUATION_SHADER;
    int activeCount;
    glGetProgramStageiv(prog, stage, GL_ACTIVE_SUBROUTINE_UNIFORM_LOCATIONS, &activeCount);
    pezCheck(activeCount == 2);
    GLuint surfaceFunc = glGetSubroutineUniformLocation(prog, stage, "SurfaceFunc");
    GLuint normalFunc = glGetSubroutineUniformLocation(prog, stage, "NormalFunc");

    // Pick the two subroutines:
    GLuint indices[2];
    float time = fmod(Scene.Time, 5);
    if (time < 2.5) {
        indices[surfaceFunc] = glGetSubroutineIndex(prog, stage, "SimpleTorusSurface");
        indices[normalFunc]  = glGetSubroutineIndex(prog, stage, "SimpleTorusNormal");
    } else {
        indices[surfaceFunc] = glGetSubroutineIndex(prog, stage, "RidgedTorusSurface");
        indices[normalFunc]  = glGetSubroutineIndex(prog, stage, "RidgedTorusNormal");
    }
    glUniformSubroutinesuiv(stage, 2, indices);

    // Clear and Render:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glPatchParameteri(GL_PATCH_VERTICES, 4);
    glDrawArrays(GL_PATCHES, 0, 256 * 4);
}

static GLuint CurrentProgram()
{
    GLuint p;
    glGetIntegerv(GL_CURRENT_PROGRAM, (GLint*) &p);
    return p;
}

static GLuint LoadProgram(const char* vsKey, const char* tcsKey, const char* tesKey, const char* gsKey, const char* fsKey)
{
    GLchar spew[256];
    GLint compileSuccess;
    GLuint programHandle = glCreateProgram();

    const char* vsSource = pezGetShader(vsKey);
    pezCheck(vsSource != 0, "Can't find vshader: %s\n", vsKey);
    GLuint vsHandle = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vsHandle, 1, &vsSource, 0);
    glCompileShader(vsHandle);
    glGetShaderiv(vsHandle, GL_COMPILE_STATUS, &compileSuccess);
    glGetShaderInfoLog(vsHandle, sizeof(spew), 0, spew);
    pezCheck(compileSuccess, "Can't compile vshader:\n%s", spew);
    glAttachShader(programHandle, vsHandle);

    if (tcsKey) {
        const char* tcsSource = pezGetShader(tcsKey);
        pezCheck(tcsSource != 0, "Can't find tcshader: %s\n", tcsKey);
        GLuint tcsHandle = glCreateShader(GL_TESS_CONTROL_SHADER);
        glShaderSource(tcsHandle, 1, &tcsSource, 0);
        glCompileShader(tcsHandle);
        glGetShaderiv(tcsHandle, GL_COMPILE_STATUS, &compileSuccess);
        glGetShaderInfoLog(tcsHandle, sizeof(spew), 0, spew);
        pezCheck(compileSuccess, "Can't compile tcshader:\n%s", spew);
        glAttachShader(programHandle, tcsHandle);
    }

    if (tesKey) {
        const char* tesSource = pezGetShader(tesKey);
        pezCheck(tesSource != 0, "Can't find teshader: %s\n", tesKey);
        GLuint tesHandle = glCreateShader(GL_TESS_EVALUATION_SHADER);
        glShaderSource(tesHandle, 1, &tesSource, 0);
        glCompileShader(tesHandle);
        glGetShaderiv(tesHandle, GL_COMPILE_STATUS, &compileSuccess);
        glGetShaderInfoLog(tesHandle, sizeof(spew), 0, spew);
        pezCheck(compileSuccess, "Can't compile teshader:\n%s", spew);
        glAttachShader(programHandle, tesHandle);
    }

    if (gsKey) {
        const char* gsSource = pezGetShader(gsKey);
        pezCheck(gsSource != 0, "Can't find gshader: %s\n", gsKey);
        GLuint gsHandle = glCreateShader(GL_GEOMETRY_SHADER);
        glShaderSource(gsHandle, 1, &gsSource, 0);
        glCompileShader(gsHandle);
        glGetShaderiv(gsHandle, GL_COMPILE_STATUS, &compileSuccess);
        glGetShaderInfoLog(gsHandle, sizeof(spew), 0, spew);
        pezCheck(compileSuccess, "Can't compile gshader:\n%s", spew);
        glAttachShader(programHandle, gsHandle);
    }

    if (fsKey) {
        const char* fsSource = pezGetShader(fsKey);
        pezCheck(fsSource != 0, "Can't find fshader: %s\n", fsKey);
        GLuint fsHandle = glCreateShader(GL_FRAGMENT_SHADER);
        glShaderSource(fsHandle, 1, &fsSource, 0);
        glCompileShader(fsHandle);
        glGetShaderiv(fsHandle, GL_COMPILE_STATUS, &compileSuccess);
        glGetShaderInfoLog(fsHandle, sizeof(spew), 0, spew);
        pezCheck(compileSuccess, "Can't compile fshader:\n%s", spew);
        glAttachShader(programHandle, fsHandle);
    }

    glLinkProgram(programHandle);
    GLint linkSuccess;
    glGetProgramiv(programHandle, GL_LINK_STATUS, &linkSuccess);
    glGetProgramInfoLog(programHandle, sizeof(spew), 0, spew);
    pezCheck(linkSuccess, "Can't link shaders:\n%s", spew);
    glUseProgram(programHandle);
    return programHandle;
}
