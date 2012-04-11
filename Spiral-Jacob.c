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
    GLfloat PackedNormalMatrix[9];
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

static void CreateTorus(float major, float minor, int slices, int stacks)
{
    GLuint vao;
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);

    int vertexCount = slices * stacks * 3;
    int vertexStride = sizeof(float) * 2;
    GLsizeiptr size = vertexCount * vertexStride;
    GLfloat* positions = (GLfloat*) malloc(size);

    GLfloat* position = positions;
    for (int slice = 0; slice < slices; slice++) {
        float v = slice * TwoPi / slices;
        for (int stack = 0; stack < stacks; stack++) {
            float u = stack * TwoPi / (stacks - 1);
            *position++ = u;
            *position++ = v;
        }
    }

    GLuint handle;
    glGenBuffers(1, &handle);
    glBindBuffer(GL_ARRAY_BUFFER, handle);
    glBufferData(GL_ARRAY_BUFFER, size, positions, GL_STATIC_DRAW);
    glEnableVertexAttribArray(a("Position"));
    glVertexAttribPointer(a("Position"), 2, GL_FLOAT, GL_FALSE,
                          vertexStride, 0);
    free(positions);

    Scene.IndexCount = (slices-1) * (stacks-1) * 6;
    size = Scene.IndexCount * sizeof(GLushort);
    GLushort* indices = (GLushort*) malloc(size);
    GLushort* index = indices;
    int v = 0;
    for (int i = 0; i < slices - 1; i++) {
        for (int j = 0; j < stacks - 1; j++) {
            int next = j + 1;
            *index++ = v+next+stacks; *index++ = v+next; *index++ = v+j;
            *index++ = v+j; *index++ = v+j+stacks; *index++ = v+next+stacks;
        }
        v += stacks;
    }

    glGenBuffers(1, &handle);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, handle);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, size, indices, GL_STATIC_DRAW);

    free(indices);
}

void PezInitialize()
{
    LoadProgram("VS", "TCS", "TES", "GS", "FS");

    PezConfig cfg = PezGetConfig();
    const float h = 1.5f;
    const float w = h * cfg.Width / cfg.Height;
    const float z[2] = {65, 90};
    Scene.Projection = M4MakeFrustum(-w, w, -h, h, z[0], z[1]);

    const float MajorRadius = 8.0f, MinorRadius = 2.0f;
    const int Slices = 64, Stacks = 32;
    CreateTorus(MajorRadius, MinorRadius, Slices, Stacks);
    Scene.Time = 0;

    glEnable(GL_DEPTH_TEST);
    glClearColor(0.2f, 0.2f, 0.2f, 1.0f);
}

void PezUpdate(float seconds)
{
    const float RadiansPerSecond = 0.75f;
    Scene.Time += seconds;

    float theta = Scene.Time * RadiansPerSecond;
   
    // Create the model-view matrix:
    Scene.ModelMatrix = M4MakeRotationZ(theta);
    Point3 eye = {0, -50, 50};
    Point3 target = {0, 0, 0};
    Vector3 up = {0, 1, 0};
    Scene.ViewMatrix = M4MakeLookAt(eye, target, up);
    Scene.Modelview = M4Mul(Scene.ViewMatrix, Scene.ModelMatrix);
    Scene.NormalMatrix = M4GetUpper3x3(Scene.Modelview);
    for (int i = 0; i < 9; ++i)
        Scene.PackedNormalMatrix[i] = M3GetElem(Scene.NormalMatrix, i/3, i%3);
}

void PezRender()
{
    float* pModel = (float*) &Scene.ModelMatrix;
    float* pView = (float*) &Scene.ViewMatrix;
    float* pModelview = (float*) &Scene.Modelview;
    float* pProjection = (float*) &Scene.Projection;
    float* pNormalMatrix = &Scene.PackedNormalMatrix[0];
    glUniformMatrix4fv(u("ViewMatrix"), 1, 0, pView);
    glUniformMatrix4fv(u("ModelMatrix"), 1, 0, pModel);
    glUniformMatrix4fv(u("Modelview"), 1, 0, pModelview);
    glUniformMatrix4fv(u("Projection"), 1, 0, pProjection);
    glUniformMatrix3fv(u("NormalMatrix"), 1, 0, pNormalMatrix);
    glUniform1f(u("Time"), Scene.Time);

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glPatchParameteri(GL_PATCH_VERTICES, 3);
    glDrawElements(GL_PATCHES, Scene.IndexCount, GL_UNSIGNED_SHORT, 0);
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

static GLuint LoadTexture(const char* filename)
{
    unsigned long w, h;
    int color_type, bit_depth, row_stride;
    png_bytep image;

    if (true) {
        FILE *fp = fopen(filename, "rb");
        pezCheck(fp ? 1 : 0, "Can't find %s", filename);
        unsigned char header[8];
        fread(header, 1, 8, fp);
        bool isPng = !png_sig_cmp(header, 0, 8);
        pezCheck(isPng, "%s is not a valid PNG file.", filename);
        png_structp png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
        pezCheckPointer(png_ptr, "PNG error line %d", __LINE__);
        png_infop info_ptr = png_create_info_struct(png_ptr);
        pezCheckPointer(info_ptr, "PNG error line %d", __LINE__);
        png_init_io(png_ptr, fp);
        png_set_sig_bytes(png_ptr, 8);
        png_read_info(png_ptr, info_ptr);
        w = png_get_image_width(png_ptr, info_ptr);
        h = png_get_image_height(png_ptr, info_ptr);
        color_type = png_get_color_type(png_ptr, info_ptr);
        bit_depth = png_get_bit_depth(png_ptr, info_ptr);
        pezPrintString("%s %dx%d bpp=%d ct=%d\n", filename, w, h, bit_depth, color_type);
        png_read_update_info(png_ptr, info_ptr);
        row_stride = png_get_rowbytes(png_ptr,info_ptr);
        image = (png_bytep) malloc(h * row_stride);
        png_bytep* row_pointers = (png_bytep*) malloc(sizeof(png_bytep) * h);
        png_bytep row = image;
        for (int y = h-1; y >= 0; y--, row += row_stride) {
            row_pointers[y] = row;
        }
        png_read_image(png_ptr, row_pointers);
        free(row_pointers);
        fclose(fp);
        png_destroy_read_struct(&png_ptr, &info_ptr, png_infopp_NULL);
    }

    pezCheck(bit_depth == 8, "Bit depth must be 8.");

    GLenum type = 0;
    switch (color_type) {
    case PNG_COLOR_TYPE_RGB:  type = GL_RGB;  break;
    case PNG_COLOR_TYPE_RGBA: type = GL_RGBA; break;
    case PNG_COLOR_TYPE_GRAY: type = GL_RED;  break;
    default: pezFatal("Unknown color type: %d.", color_type);
    }

    GLuint handle;
    glGenTextures(1, &handle);
    glBindTexture(GL_TEXTURE_2D, handle);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexImage2D(GL_TEXTURE_2D, 0, type, w, h, 0, type, GL_UNSIGNED_BYTE, image);
    glGenerateMipmap(GL_TEXTURE_2D);
    pezCheck(OpenGLError);

    free(image);
    return handle;
}
