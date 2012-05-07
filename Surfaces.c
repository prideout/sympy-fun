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
static void CreatePng(const char* filename, int w, int h, const unsigned char* data);

#define u(x) glGetUniformLocation(CurrentProgram(), x)
#define a(x) glGetAttribLocation(CurrentProgram(), x)
#define OpenGLError GL_NO_ERROR == glGetError(),                        \
        "%s:%d - OpenGL Error - %s", __FILE__, __LINE__, __FUNCTION__   \

static const bool TakeScreenshots = false;

PezConfig PezGetConfig()
{
    PezConfig config;
    config.Title = __FILE__;
    config.Width = 800*2;
    config.Height = 600*2;
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
    if (TakeScreenshots) {
        theta = -0.25;
    }
   
    // Create the model-view matrix:
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

    // Make sure there is a subroutine we can pick:
    GLenum prog = CurrentProgram();
    GLenum stage = GL_TESS_EVALUATION_SHADER;
    int activeCount;
    glGetProgramStageiv(prog, stage, GL_ACTIVE_SUBROUTINE_UNIFORM_LOCATIONS, &activeCount);
    pezCheck(activeCount == 1);
    GLuint surfaceFunc = glGetSubroutineUniformLocation(prog, stage, "SurfaceFunc");

    // Pick the subroutine:
    float time = fmod(Scene.Time, 5);
    const char* names[] = {
        "SimpleTorusSurface",
        "RidgedTorusSurface",
        "SuperellipseTorusSurface",
        "SuperellipseMobiusSurface",
        "SpiralSurface"
    };
    int sel = ((int) time) % (sizeof(names) / sizeof(names[0]));
    GLuint surface = glGetSubroutineIndex(prog, stage, names[sel]);
    static GLuint indices[1];
    bool takeScreenshot = false;
    if (indices[surfaceFunc] != surface) {
        indices[surfaceFunc] = surface;
        glUniformSubroutinesuiv(stage, 1, indices);
        takeScreenshot = TakeScreenshots;
    }

    // Clear and draw:
    if (takeScreenshot) {
        glClearColor(0, 0, 0, 0);
    } else {
        glClearColor(0.2f, 0.2f, 0.2f, 1.0f);
    }
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glPatchParameteri(GL_PATCH_VERTICES, 4);
    glDrawArrays(GL_PATCHES, 0, 4);

    // Record a screenshot if desired:
    if (takeScreenshot) {
        int w = PezGetConfig().Width;
        int h = PezGetConfig().Height;
        unsigned char* data = (unsigned char*) malloc(w * h * 4);
        glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data);
        CreatePng(names[sel], w, h, data);
        free(data);
    }
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

static void CreatePng(const char* base, int w, int h, const unsigned char* data)
{
    FILE * fp;
    png_structp png_ptr = NULL;
    png_infop info_ptr = NULL;
    size_t y;
    png_byte ** row_pointers = NULL;
    int depth = 8;

    char filename[256];
    sprintf(filename, "%s.png", base);
    
    fp = fopen(filename, "wb");
    pezCheck(fp ? 1 : 0, "Unable to open %s", filename);

    png_ptr = png_create_write_struct (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    pezCheck(png_ptr ? 1 : 0, "Unable to create PNG struct");
    
    info_ptr = png_create_info_struct (png_ptr);
    pezCheck(info_ptr ? 1 : 0, "Unable to create PNG info");

    if (setjmp (png_jmpbuf (png_ptr))) {
        pezFatal("Unable to set errorhandler");
    }
    
    png_set_IHDR (png_ptr,
                  info_ptr,
                  w,
                  h,
                  depth,
                  PNG_COLOR_TYPE_RGBA,
                  PNG_INTERLACE_NONE,
                  PNG_COMPRESSION_TYPE_DEFAULT,
                  PNG_FILTER_TYPE_DEFAULT);
    
    row_pointers = (png_byte**) png_malloc (png_ptr, h * sizeof (png_byte *));
    for (y = 0; y < h; ++y) {
        int row = h-1-y;
        row_pointers[y] = (png_byte*) (data + row * w * 4);
    }
    
    png_init_io (png_ptr, fp);
    png_set_rows (png_ptr, info_ptr, row_pointers);
    png_write_png (png_ptr, info_ptr, PNG_TRANSFORM_IDENTITY, NULL);

    png_free (png_ptr, row_pointers);
    png_destroy_write_struct (&png_ptr, &info_ptr);
    fclose (fp);
    pezPrintString("Wrote %s\n", filename);
}
