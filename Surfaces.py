#!/usr/bin/python

from Derive import *
from sympy import ccode, symbols
from sympy.functions import Abs, sign, sin, cos

# Print a vector-valued function with C syntax
def Print(label, vvf):
    print '// ' + label
    print "float x =", ccode(vvf[0]) + ";"
    print "float y =", ccode(vvf[1]) + ";"
    print "float z =", ccode(vvf[2]) + ";"
    print

def PrintDivider():
    print '/' * 60, '\n'

# Vector-valued function that draws a circle on the Y-Z plane.
def CircleYZ(radius):
    return VVF(0, -radius*cos(v), radius*sin(v))

def SuperellipseYZ(n, a, b):
    x = Abs(cos(v)) ** 2/n * a * sign(cos(v))
    y = Abs(sin(v)) ** 2/n * b * sign(sin(v))
    return VVF(0, x, y)

# Rotates the given vector-valued function along the X-axis
def RotateX(f, q):
    y = f[1] * cos(q) - f[2] * sin(q)
    z = f[1] * sin(q) + f[2] * cos(q)
    x = f[0]
    return VVF(x, y, z)

# For radius symbols, we need to specify a positive assumption;
# this prevents "Abs" expressions from cropping up in "normalize"
# h and f control height & freq of ridges
r, R = symbols('r R', positive=True)
h, f = symbols('h f')

# Torus
if True:
    sweepCurve = VVF(R*cos(u), R*sin(u), 0)
    crossSection = CircleYZ(r)
    surface = Sweep(sweepCurve, crossSection)
    normals = NormalFunc(surface)
    print
    Print('Torus Surface', surface)
    Print('Torus Normals', normals)
    PrintDivider()

# Torus with Meridian Ridges
if True:
    crossSection = CircleYZ(r + h*sin(u*f))
    surface = Sweep(sweepCurve, crossSection)
    normals = NormalFunc(surface)
    Print('Ridged Torus Surface', surface)
    Print('Ridged Torus Normals', normals)
    PrintDivider()

# Torus with a superellipse cross-section
if True:
    sweepCurve = VVF(R*cos(u), R*sin(u), 0)
    crossSection = SuperellipseYZ(4, 1, 1)
    surface = Sweep(sweepCurve, crossSection)
    normals = NormalFunc(surface)
    print
    Print('Superellipse Torus Surface', surface)
    Print('Superellipse Torus Normals', normals)
    PrintDivider()

# Superellipse Mobius
if True:
    sweepCurve = VVF(R*cos(u), R*sin(u), 0)
    crossSection = SuperellipseYZ(4, 1, 0.25) # b = 0.25 causes squishness.
    crossSection = RotateX(crossSection, v * 2)
    surface = Sweep(sweepCurve, crossSection)
    normals = NormalFunc(surface)
    print
    Print('Superellipse Mobius Surface', surface)
    Print('Superellipse Mobius Normals', normals)
    PrintDivider()


# Trefoil that lies on the torus (r-2)^2 + z^2 = 1
# Causes infinite recursion in sympy...
if False:
    x = (2 + cos(3*u))*cos(2*u)
    y = (2 + cos(3*u))*sin(2*u)
    z = sin(3*u)
    sweepCurve = VVF(x, y, z)
    crossSection = CircleYZ(radius = 1.0)
    surface = Sweep(sweepCurve, crossSection)
    Print('Trefoil-on-Torus Surface', surface)
    PrintDivider()

# Simpler Trefoil -- also causes sympy trouble.
if False:
    a, b, c = 0.5, 0.3, 0.5
    x = -1.5 * b * sin(1.5 * u) * cos(u) - (a + b * cos(1.5 * u)) * sin(u)
    y = -1.5 * b * sin(1.5 * u) * sin(u) + (a + b * cos(1.5 * u)) * cos(u)
    z =  1.5 * c * cos(1.5 * u)
    sweepCurve = VVF(x, y, z)
    crossSection = CircleYZ(r)
    surface = Sweep(sweepCurve, crossSection)
    print
    Print('Simple Trefoil Surface', surface)
    PrintDivider()

# Bicubic Patch
if False:
    B = Matrix(4,4,[
        -1, 3, -3, 1,
        3, -6, 3, 0,
        -3, 3, 0, 0,
        1, 0, 0, 0 ])
    Bt = B.transpose()
    a_thru_p = [chr(i + ord('a')) for i in xrange(16)]
    axes = 'x','y','z'
    ax_thru_pz = ["%s_%s" % (x, c) for c in axes for x in a_thru_p]
    ax_thru_pz = symbols(' '.join(ax_thru_pz))
    x = Matrix(4,4,ax_thru_pz[0:16])  # a_x, b_x, c_x, ...
    y = Matrix(4,4,ax_thru_pz[16:32]) # a_y, b_y, c_y, ...
    z = Matrix(4,4,ax_thru_pz[32:48]) # a_z, b_z, c_z, ...
    um = Matrix(1,4,[u*u*u,u*u,u,1])
    vm = Matrix(4,1,[v*v*v,v*v,v,1])
    x, y, z = [um * B * P * Bt * vm for P in x,y,z]
    x, y, z = [simplify(P[0]) for P in x,y,z]
    surface = VVF(x, y, z)
    normals = NormalFunc(surface) # <--- this is slow
    Print('Bicubic Patch Surface', surface)
    Print('Bicubic Patch Normals', normals)
    PrintDivider()

a = """
// Torus Surface
float x = (R + r*cos(v))*cos(u);
float y = (R + r*cos(v))*sin(u);
float z = r*sin(v);

// Torus Normals
float x = r*(R + r*cos(v))*cos(u)*cos(v);
float y = r*(R + r*cos(v))*sin(u)*cos(v);
float z = r*(R + r*cos(v))*sin(v);

// Ridged Torus Surface
float x = R*cos(u) + (h*sin(f*u) + r)*cos(u)*cos(v);
float y = R*sin(u) + (h*sin(f*u) + r)*sin(u)*cos(v);
float z = (h*sin(f*u) + r)*sin(v);

// Ridged Torus Normals
float x = -f*h*(h*sin(f*u) + r)*sin(u)*pow(cos(v), 2)*cos(f*u) + f*h*(h*sin(f*u) + r)*sin(u)*cos(f*u) + (h*sin(f*u) + r)*(R*cos(u) + f*h*sin(u)*cos(v)*cos(f*u) + (h*sin(f*u) + r)*cos(u)*cos(v))*cos(v);
float y = f*h*(h*sin(f*u) + r)*cos(u)*pow(cos(v), 2)*cos(f*u) - f*h*(h*sin(f*u) + r)*cos(u)*cos(f*u) + (-h*sin(f*u) - r)*(-R*sin(u) + f*h*cos(u)*cos(v)*cos(f*u) + (-h*sin(f*u) - r)*sin(u)*cos(v))*cos(v);
float z = (-h*sin(f*u) - r)*(-R*sin(u) + f*h*cos(u)*cos(v)*cos(f*u) + (-h*sin(f*u) - r)*sin(u)*cos(v))*sin(u)*sin(v) + (h*sin(f*u) + r)*(R*cos(u) + f*h*sin(u)*cos(v)*cos(f*u) + (h*sin(f*u) + r)*cos(u)*cos(v))*sin(v)*cos(u);

// Superellipse Torus Surface
float x = (R - pow(cos(v), 2)*sign(cos(v))/4)*cos(u);
float y = (R - pow(cos(v), 2)*sign(cos(v))/4)*sin(u);
float z = pow(sin(v), 2)*sign(sin(v))/4;

// Superellipse Torus Normals
float x = (R/2 - pow(cos(v), 2)*sign(cos(v))/8)*sin(v)*cos(u)*cos(v)*sign(sin(v));
float y = (R/2 - pow(cos(v), 2)*sign(cos(v))/8)*sin(u)*sin(v)*cos(v)*sign(sin(v));
float z = (-R/2 + pow(cos(v), 2)*sign(cos(v))/8)*sin(v)*cos(v)*sign(cos(v));

// Superellipse Mobius Surface
float x = R*cos(u) - (-0.0625*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/4)*cos(u);
float y = R*sin(u) - (-0.0625*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/4)*sin(u);
float z = (0.0625*pow(sin(v), 2)*cos(2*v)*sign(sin(v)) + sin(2*v)*pow(cos(v), 2)*sign(cos(v))/4)*(pow(sin(u), 2) + pow(cos(u), 2));

// Superellipse Mobius Normals
float x = (R*cos(u) - (-0.0625*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/4)*cos(u))*(pow(sin(u), 2) + pow(cos(u), 2))*(-0.125*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) - sin(v)*sin(2*v)*cos(v)*sign(cos(v))/2 + 0.125*sin(v)*cos(v)*cos(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/2);
float y = -(-R*sin(u) + (-0.0625*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/4)*sin(u))*(pow(sin(u), 2) + pow(cos(u), 2))*(-0.125*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) - sin(v)*sin(2*v)*cos(v)*sign(cos(v))/2 + 0.125*sin(v)*cos(v)*cos(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/2);
float z = -(-R*sin(u) + (-0.0625*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/4)*sin(u))*(-0.125*pow(sin(v), 2)*cos(2*v)*sign(sin(v)) - 0.125*sin(v)*sin(2*v)*cos(v)*sign(sin(v)) - sin(v)*cos(v)*cos(2*v)*sign(cos(v))/2 - sin(2*v)*pow(cos(v), 2)*sign(cos(v))/2)*sin(u) + (R*cos(u) - (-0.0625*pow(sin(v), 2)*sin(2*v)*sign(sin(v)) + pow(cos(v), 2)*cos(2*v)*sign(cos(v))/4)*cos(u))*(-0.125*pow(sin(v), 2)*cos(2*v)*sign(sin(v)) - 0.125*sin(v)*sin(2*v)*cos(v)*sign(sin(v)) - sin(v)*cos(v)*cos(2*v)*sign(cos(v))/2 - sin(2*v)*pow(cos(v), 2)*sign(cos(v))/2)*cos(u);

// Bicubic Patch Surface
float x = a_x*pow(u, 3)*pow(v, 3) - 3*a_x*pow(u, 3)*pow(v, 2) + 3*a_x*pow(u, 3)*v - a_x*pow(u, 3) - 3*a_x*pow(u, 2)*pow(v, 3) + 9*a_x*pow(u, 2)*pow(v, 2) - 9*a_x*pow(u, 2)*v + 3*a_x*pow(u, 2) + 3*a_x*u*pow(v, 3) - 9*a_x*u*pow(v, 2) + 9*a_x*u*v - 3*a_x*u - a_x*pow(v, 3) + 3*a_x*pow(v, 2) - 3*a_x*v + a_x - 3*b_x*pow(u, 3)*pow(v, 3) + 6*b_x*pow(u, 3)*pow(v, 2) - 3*b_x*pow(u, 3)*v + 9*b_x*pow(u, 2)*pow(v, 3) - 18*b_x*pow(u, 2)*pow(v, 2) + 9*b_x*pow(u, 2)*v - 9*b_x*u*pow(v, 3) + 18*b_x*u*pow(v, 2) - 9*b_x*u*v + 3*b_x*pow(v, 3) - 6*b_x*pow(v, 2) + 3*b_x*v + 3*c_x*pow(u, 3)*pow(v, 3) - 3*c_x*pow(u, 3)*pow(v, 2) - 9*c_x*pow(u, 2)*pow(v, 3) + 9*c_x*pow(u, 2)*pow(v, 2) + 9*c_x*u*pow(v, 3) - 9*c_x*u*pow(v, 2) - 3*c_x*pow(v, 3) + 3*c_x*pow(v, 2) - d_x*pow(u, 3)*pow(v, 3) + 3*d_x*pow(u, 2)*pow(v, 3) - 3*d_x*u*pow(v, 3) + d_x*pow(v, 3) - 3*e_x*pow(u, 3)*pow(v, 3) + 9*e_x*pow(u, 3)*pow(v, 2) - 9*e_x*pow(u, 3)*v + 3*e_x*pow(u, 3) + 6*e_x*pow(u, 2)*pow(v, 3) - 18*e_x*pow(u, 2)*pow(v, 2) + 18*e_x*pow(u, 2)*v - 6*e_x*pow(u, 2) - 3*e_x*u*pow(v, 3) + 9*e_x*u*pow(v, 2) - 9*e_x*u*v + 3*e_x*u + 9*f_x*pow(u, 3)*pow(v, 3) - 18*f_x*pow(u, 3)*pow(v, 2) + 9*f_x*pow(u, 3)*v - 18*f_x*pow(u, 2)*pow(v, 3) + 36*f_x*pow(u, 2)*pow(v, 2) - 18*f_x*pow(u, 2)*v + 9*f_x*u*pow(v, 3) - 18*f_x*u*pow(v, 2) + 9*f_x*u*v - 9*g_x*pow(u, 3)*pow(v, 3) + 9*g_x*pow(u, 3)*pow(v, 2) + 18*g_x*pow(u, 2)*pow(v, 3) - 18*g_x*pow(u, 2)*pow(v, 2) - 9*g_x*u*pow(v, 3) + 9*g_x*u*pow(v, 2) + 3*h_x*pow(u, 3)*pow(v, 3) - 6*h_x*pow(u, 2)*pow(v, 3) + 3*h_x*u*pow(v, 3) + 3*i_x*pow(u, 3)*pow(v, 3) - 9*i_x*pow(u, 3)*pow(v, 2) + 9*i_x*pow(u, 3)*v - 3*i_x*pow(u, 3) - 3*i_x*pow(u, 2)*pow(v, 3) + 9*i_x*pow(u, 2)*pow(v, 2) - 9*i_x*pow(u, 2)*v + 3*i_x*pow(u, 2) - 9*j_x*pow(u, 3)*pow(v, 3) + 18*j_x*pow(u, 3)*pow(v, 2) - 9*j_x*pow(u, 3)*v + 9*j_x*pow(u, 2)*pow(v, 3) - 18*j_x*pow(u, 2)*pow(v, 2) + 9*j_x*pow(u, 2)*v + 9*k_x*pow(u, 3)*pow(v, 3) - 9*k_x*pow(u, 3)*pow(v, 2) - 9*k_x*pow(u, 2)*pow(v, 3) + 9*k_x*pow(u, 2)*pow(v, 2) - 3*l_x*pow(u, 3)*pow(v, 3) + 3*l_x*pow(u, 2)*pow(v, 3) - m_x*pow(u, 3)*pow(v, 3) + 3*m_x*pow(u, 3)*pow(v, 2) - 3*m_x*pow(u, 3)*v + m_x*pow(u, 3) + 3*n_x*pow(u, 3)*pow(v, 3) - 6*n_x*pow(u, 3)*pow(v, 2) + 3*n_x*pow(u, 3)*v - 3*o_x*pow(u, 3)*pow(v, 3) + 3*o_x*pow(u, 3)*pow(v, 2) + p_x*pow(u, 3)*pow(v, 3);
float y = a_y*pow(u, 3)*pow(v, 3) - 3*a_y*pow(u, 3)*pow(v, 2) + 3*a_y*pow(u, 3)*v - a_y*pow(u, 3) - 3*a_y*pow(u, 2)*pow(v, 3) + 9*a_y*pow(u, 2)*pow(v, 2) - 9*a_y*pow(u, 2)*v + 3*a_y*pow(u, 2) + 3*a_y*u*pow(v, 3) - 9*a_y*u*pow(v, 2) + 9*a_y*u*v - 3*a_y*u - a_y*pow(v, 3) + 3*a_y*pow(v, 2) - 3*a_y*v + a_y - 3*b_y*pow(u, 3)*pow(v, 3) + 6*b_y*pow(u, 3)*pow(v, 2) - 3*b_y*pow(u, 3)*v + 9*b_y*pow(u, 2)*pow(v, 3) - 18*b_y*pow(u, 2)*pow(v, 2) + 9*b_y*pow(u, 2)*v - 9*b_y*u*pow(v, 3) + 18*b_y*u*pow(v, 2) - 9*b_y*u*v + 3*b_y*pow(v, 3) - 6*b_y*pow(v, 2) + 3*b_y*v + 3*c_y*pow(u, 3)*pow(v, 3) - 3*c_y*pow(u, 3)*pow(v, 2) - 9*c_y*pow(u, 2)*pow(v, 3) + 9*c_y*pow(u, 2)*pow(v, 2) + 9*c_y*u*pow(v, 3) - 9*c_y*u*pow(v, 2) - 3*c_y*pow(v, 3) + 3*c_y*pow(v, 2) - d_y*pow(u, 3)*pow(v, 3) + 3*d_y*pow(u, 2)*pow(v, 3) - 3*d_y*u*pow(v, 3) + d_y*pow(v, 3) - 3*e_y*pow(u, 3)*pow(v, 3) + 9*e_y*pow(u, 3)*pow(v, 2) - 9*e_y*pow(u, 3)*v + 3*e_y*pow(u, 3) + 6*e_y*pow(u, 2)*pow(v, 3) - 18*e_y*pow(u, 2)*pow(v, 2) + 18*e_y*pow(u, 2)*v - 6*e_y*pow(u, 2) - 3*e_y*u*pow(v, 3) + 9*e_y*u*pow(v, 2) - 9*e_y*u*v + 3*e_y*u + 9*f_y*pow(u, 3)*pow(v, 3) - 18*f_y*pow(u, 3)*pow(v, 2) + 9*f_y*pow(u, 3)*v - 18*f_y*pow(u, 2)*pow(v, 3) + 36*f_y*pow(u, 2)*pow(v, 2) - 18*f_y*pow(u, 2)*v + 9*f_y*u*pow(v, 3) - 18*f_y*u*pow(v, 2) + 9*f_y*u*v - 9*g_y*pow(u, 3)*pow(v, 3) + 9*g_y*pow(u, 3)*pow(v, 2) + 18*g_y*pow(u, 2)*pow(v, 3) - 18*g_y*pow(u, 2)*pow(v, 2) - 9*g_y*u*pow(v, 3) + 9*g_y*u*pow(v, 2) + 3*h_y*pow(u, 3)*pow(v, 3) - 6*h_y*pow(u, 2)*pow(v, 3) + 3*h_y*u*pow(v, 3) + 3*i_y*pow(u, 3)*pow(v, 3) - 9*i_y*pow(u, 3)*pow(v, 2) + 9*i_y*pow(u, 3)*v - 3*i_y*pow(u, 3) - 3*i_y*pow(u, 2)*pow(v, 3) + 9*i_y*pow(u, 2)*pow(v, 2) - 9*i_y*pow(u, 2)*v + 3*i_y*pow(u, 2) - 9*j_y*pow(u, 3)*pow(v, 3) + 18*j_y*pow(u, 3)*pow(v, 2) - 9*j_y*pow(u, 3)*v + 9*j_y*pow(u, 2)*pow(v, 3) - 18*j_y*pow(u, 2)*pow(v, 2) + 9*j_y*pow(u, 2)*v + 9*k_y*pow(u, 3)*pow(v, 3) - 9*k_y*pow(u, 3)*pow(v, 2) - 9*k_y*pow(u, 2)*pow(v, 3) + 9*k_y*pow(u, 2)*pow(v, 2) - 3*l_y*pow(u, 3)*pow(v, 3) + 3*l_y*pow(u, 2)*pow(v, 3) - m_y*pow(u, 3)*pow(v, 3) + 3*m_y*pow(u, 3)*pow(v, 2) - 3*m_y*pow(u, 3)*v + m_y*pow(u, 3) + 3*n_y*pow(u, 3)*pow(v, 3) - 6*n_y*pow(u, 3)*pow(v, 2) + 3*n_y*pow(u, 3)*v - 3*o_y*pow(u, 3)*pow(v, 3) + 3*o_y*pow(u, 3)*pow(v, 2) + p_y*pow(u, 3)*pow(v, 3);
float z = a_z*pow(u, 3)*pow(v, 3) - 3*a_z*pow(u, 3)*pow(v, 2) + 3*a_z*pow(u, 3)*v - a_z*pow(u, 3) - 3*a_z*pow(u, 2)*pow(v, 3) + 9*a_z*pow(u, 2)*pow(v, 2) - 9*a_z*pow(u, 2)*v + 3*a_z*pow(u, 2) + 3*a_z*u*pow(v, 3) - 9*a_z*u*pow(v, 2) + 9*a_z*u*v - 3*a_z*u - a_z*pow(v, 3) + 3*a_z*pow(v, 2) - 3*a_z*v + a_z - 3*b_z*pow(u, 3)*pow(v, 3) + 6*b_z*pow(u, 3)*pow(v, 2) - 3*b_z*pow(u, 3)*v + 9*b_z*pow(u, 2)*pow(v, 3) - 18*b_z*pow(u, 2)*pow(v, 2) + 9*b_z*pow(u, 2)*v - 9*b_z*u*pow(v, 3) + 18*b_z*u*pow(v, 2) - 9*b_z*u*v + 3*b_z*pow(v, 3) - 6*b_z*pow(v, 2) + 3*b_z*v + 3*c_z*pow(u, 3)*pow(v, 3) - 3*c_z*pow(u, 3)*pow(v, 2) - 9*c_z*pow(u, 2)*pow(v, 3) + 9*c_z*pow(u, 2)*pow(v, 2) + 9*c_z*u*pow(v, 3) - 9*c_z*u*pow(v, 2) - 3*c_z*pow(v, 3) + 3*c_z*pow(v, 2) - d_z*pow(u, 3)*pow(v, 3) + 3*d_z*pow(u, 2)*pow(v, 3) - 3*d_z*u*pow(v, 3) + d_z*pow(v, 3) - 3*e_z*pow(u, 3)*pow(v, 3) + 9*e_z*pow(u, 3)*pow(v, 2) - 9*e_z*pow(u, 3)*v + 3*e_z*pow(u, 3) + 6*e_z*pow(u, 2)*pow(v, 3) - 18*e_z*pow(u, 2)*pow(v, 2) + 18*e_z*pow(u, 2)*v - 6*e_z*pow(u, 2) - 3*e_z*u*pow(v, 3) + 9*e_z*u*pow(v, 2) - 9*e_z*u*v + 3*e_z*u + 9*f_z*pow(u, 3)*pow(v, 3) - 18*f_z*pow(u, 3)*pow(v, 2) + 9*f_z*pow(u, 3)*v - 18*f_z*pow(u, 2)*pow(v, 3) + 36*f_z*pow(u, 2)*pow(v, 2) - 18*f_z*pow(u, 2)*v + 9*f_z*u*pow(v, 3) - 18*f_z*u*pow(v, 2) + 9*f_z*u*v - 9*g_z*pow(u, 3)*pow(v, 3) + 9*g_z*pow(u, 3)*pow(v, 2) + 18*g_z*pow(u, 2)*pow(v, 3) - 18*g_z*pow(u, 2)*pow(v, 2) - 9*g_z*u*pow(v, 3) + 9*g_z*u*pow(v, 2) + 3*h_z*pow(u, 3)*pow(v, 3) - 6*h_z*pow(u, 2)*pow(v, 3) + 3*h_z*u*pow(v, 3) + 3*i_z*pow(u, 3)*pow(v, 3) - 9*i_z*pow(u, 3)*pow(v, 2) + 9*i_z*pow(u, 3)*v - 3*i_z*pow(u, 3) - 3*i_z*pow(u, 2)*pow(v, 3) + 9*i_z*pow(u, 2)*pow(v, 2) - 9*i_z*pow(u, 2)*v + 3*i_z*pow(u, 2) - 9*j_z*pow(u, 3)*pow(v, 3) + 18*j_z*pow(u, 3)*pow(v, 2) - 9*j_z*pow(u, 3)*v + 9*j_z*pow(u, 2)*pow(v, 3) - 18*j_z*pow(u, 2)*pow(v, 2) + 9*j_z*pow(u, 2)*v + 9*k_z*pow(u, 3)*pow(v, 3) - 9*k_z*pow(u, 3)*pow(v, 2) - 9*k_z*pow(u, 2)*pow(v, 3) + 9*k_z*pow(u, 2)*pow(v, 2) - 3*l_z*pow(u, 3)*pow(v, 3) + 3*l_z*pow(u, 2)*pow(v, 3) - m_z*pow(u, 3)*pow(v, 3) + 3*m_z*pow(u, 3)*pow(v, 2) - 3*m_z*pow(u, 3)*v + m_z*pow(u, 3) + 3*n_z*pow(u, 3)*pow(v, 3) - 6*n_z*pow(u, 3)*pow(v, 2) + 3*n_z*pow(u, 3)*v - 3*o_z*pow(u, 3)*pow(v, 3) + 3*o_z*pow(u, 3)*pow(v, 2) + p_z*pow(u, 3)*pow(v, 3);

// Bicubic Patch Normals
float x = (3*a_y*pow(u, 2)*pow(v, 3) - 9*a_y*pow(u, 2)*pow(v, 2) + 9*a_y*pow(u, 2)*v - 3*a_y*pow(u, 2) - 6*a_y*u*pow(v, 3) + 18*a_y*u*pow(v, 2) - 18*a_y*u*v + 6*a_y*u + 3*a_y*pow(v, 3) - 9*a_y*pow(v, 2) + 9*a_y*v - 3*a_y - 9*b_y*pow(u, 2)*pow(v, 3) + 18*b_y*pow(u, 2)*pow(v, 2) - 9*b_y*pow(u, 2)*v + 18*b_y*u*pow(v, 3) - 36*b_y*u*pow(v, 2) + 18*b_y*u*v - 9*b_y*pow(v, 3) + 18*b_y*pow(v, 2) - 9*b_y*v + 9*c_y*pow(u, 2)*pow(v, 3) - 9*c_y*pow(u, 2)*pow(v, 2) - 18*c_y*u*pow(v, 3) + 18*c_y*u*pow(v, 2) + 9*c_y*pow(v, 3) - 9*c_y*pow(v, 2) - 3*d_y*pow(u, 2)*pow(v, 3) + 6*d_y*u*pow(v, 3) - 3*d_y*pow(v, 3) - 9*e_y*pow(u, 2)*pow(v, 3) + 27*e_y*pow(u, 2)*pow(v, 2) - 27*e_y*pow(u, 2)*v + 9*e_y*pow(u, 2) + 12*e_y*u*pow(v, 3) - 36*e_y*u*pow(v, 2) + 36*e_y*u*v - 12*e_y*u - 3*e_y*pow(v, 3) + 9*e_y*pow(v, 2) - 9*e_y*v + 3*e_y + 27*f_y*pow(u, 2)*pow(v, 3) - 54*f_y*pow(u, 2)*pow(v, 2) + 27*f_y*pow(u, 2)*v - 36*f_y*u*pow(v, 3) + 72*f_y*u*pow(v, 2) - 36*f_y*u*v + 9*f_y*pow(v, 3) - 18*f_y*pow(v, 2) + 9*f_y*v - 27*g_y*pow(u, 2)*pow(v, 3) + 27*g_y*pow(u, 2)*pow(v, 2) + 36*g_y*u*pow(v, 3) - 36*g_y*u*pow(v, 2) - 9*g_y*pow(v, 3) + 9*g_y*pow(v, 2) + 9*h_y*pow(u, 2)*pow(v, 3) - 12*h_y*u*pow(v, 3) + 3*h_y*pow(v, 3) + 9*i_y*pow(u, 2)*pow(v, 3) - 27*i_y*pow(u, 2)*pow(v, 2) + 27*i_y*pow(u, 2)*v - 9*i_y*pow(u, 2) - 6*i_y*u*pow(v, 3) + 18*i_y*u*pow(v, 2) - 18*i_y*u*v + 6*i_y*u - 27*j_y*pow(u, 2)*pow(v, 3) + 54*j_y*pow(u, 2)*pow(v, 2) - 27*j_y*pow(u, 2)*v + 18*j_y*u*pow(v, 3) - 36*j_y*u*pow(v, 2) + 18*j_y*u*v + 27*k_y*pow(u, 2)*pow(v, 3) - 27*k_y*pow(u, 2)*pow(v, 2) - 18*k_y*u*pow(v, 3) + 18*k_y*u*pow(v, 2) - 9*l_y*pow(u, 2)*pow(v, 3) + 6*l_y*u*pow(v, 3) - 3*m_y*pow(u, 2)*pow(v, 3) + 9*m_y*pow(u, 2)*pow(v, 2) - 9*m_y*pow(u, 2)*v + 3*m_y*pow(u, 2) + 9*n_y*pow(u, 2)*pow(v, 3) - 18*n_y*pow(u, 2)*pow(v, 2) + 9*n_y*pow(u, 2)*v - 9*o_y*pow(u, 2)*pow(v, 3) + 9*o_y*pow(u, 2)*pow(v, 2) + 3*p_y*pow(u, 2)*pow(v, 3))*(3*a_z*pow(u, 3)*pow(v, 2) - 6*a_z*pow(u, 3)*v + 3*a_z*pow(u, 3) - 9*a_z*pow(u, 2)*pow(v, 2) + 18*a_z*pow(u, 2)*v - 9*a_z*pow(u, 2) + 9*a_z*u*pow(v, 2) - 18*a_z*u*v + 9*a_z*u - 3*a_z*pow(v, 2) + 6*a_z*v - 3*a_z - 9*b_z*pow(u, 3)*pow(v, 2) + 12*b_z*pow(u, 3)*v - 3*b_z*pow(u, 3) + 27*b_z*pow(u, 2)*pow(v, 2) - 36*b_z*pow(u, 2)*v + 9*b_z*pow(u, 2) - 27*b_z*u*pow(v, 2) + 36*b_z*u*v - 9*b_z*u + 9*b_z*pow(v, 2) - 12*b_z*v + 3*b_z + 9*c_z*pow(u, 3)*pow(v, 2) - 6*c_z*pow(u, 3)*v - 27*c_z*pow(u, 2)*pow(v, 2) + 18*c_z*pow(u, 2)*v + 27*c_z*u*pow(v, 2) - 18*c_z*u*v - 9*c_z*pow(v, 2) + 6*c_z*v - 3*d_z*pow(u, 3)*pow(v, 2) + 9*d_z*pow(u, 2)*pow(v, 2) - 9*d_z*u*pow(v, 2) + 3*d_z*pow(v, 2) - 9*e_z*pow(u, 3)*pow(v, 2) + 18*e_z*pow(u, 3)*v - 9*e_z*pow(u, 3) + 18*e_z*pow(u, 2)*pow(v, 2) - 36*e_z*pow(u, 2)*v + 18*e_z*pow(u, 2) - 9*e_z*u*pow(v, 2) + 18*e_z*u*v - 9*e_z*u + 27*f_z*pow(u, 3)*pow(v, 2) - 36*f_z*pow(u, 3)*v + 9*f_z*pow(u, 3) - 54*f_z*pow(u, 2)*pow(v, 2) + 72*f_z*pow(u, 2)*v - 18*f_z*pow(u, 2) + 27*f_z*u*pow(v, 2) - 36*f_z*u*v + 9*f_z*u - 27*g_z*pow(u, 3)*pow(v, 2) + 18*g_z*pow(u, 3)*v + 54*g_z*pow(u, 2)*pow(v, 2) - 36*g_z*pow(u, 2)*v - 27*g_z*u*pow(v, 2) + 18*g_z*u*v + 9*h_z*pow(u, 3)*pow(v, 2) - 18*h_z*pow(u, 2)*pow(v, 2) + 9*h_z*u*pow(v, 2) + 9*i_z*pow(u, 3)*pow(v, 2) - 18*i_z*pow(u, 3)*v + 9*i_z*pow(u, 3) - 9*i_z*pow(u, 2)*pow(v, 2) + 18*i_z*pow(u, 2)*v - 9*i_z*pow(u, 2) - 27*j_z*pow(u, 3)*pow(v, 2) + 36*j_z*pow(u, 3)*v - 9*j_z*pow(u, 3) + 27*j_z*pow(u, 2)*pow(v, 2) - 36*j_z*pow(u, 2)*v + 9*j_z*pow(u, 2) + 27*k_z*pow(u, 3)*pow(v, 2) - 18*k_z*pow(u, 3)*v - 27*k_z*pow(u, 2)*pow(v, 2) + 18*k_z*pow(u, 2)*v - 9*l_z*pow(u, 3)*pow(v, 2) + 9*l_z*pow(u, 2)*pow(v, 2) - 3*m_z*pow(u, 3)*pow(v, 2) + 6*m_z*pow(u, 3)*v - 3*m_z*pow(u, 3) + 9*n_z*pow(u, 3)*pow(v, 2) - 12*n_z*pow(u, 3)*v + 3*n_z*pow(u, 3) - 9*o_z*pow(u, 3)*pow(v, 2) + 6*o_z*pow(u, 3)*v + 3*p_z*pow(u, 3)*pow(v, 2)) - (3*a_y*pow(u, 3)*pow(v, 2) - 6*a_y*pow(u, 3)*v + 3*a_y*pow(u, 3) - 9*a_y*pow(u, 2)*pow(v, 2) + 18*a_y*pow(u, 2)*v - 9*a_y*pow(u, 2) + 9*a_y*u*pow(v, 2) - 18*a_y*u*v + 9*a_y*u - 3*a_y*pow(v, 2) + 6*a_y*v - 3*a_y - 9*b_y*pow(u, 3)*pow(v, 2) + 12*b_y*pow(u, 3)*v - 3*b_y*pow(u, 3) + 27*b_y*pow(u, 2)*pow(v, 2) - 36*b_y*pow(u, 2)*v + 9*b_y*pow(u, 2) - 27*b_y*u*pow(v, 2) + 36*b_y*u*v - 9*b_y*u + 9*b_y*pow(v, 2) - 12*b_y*v + 3*b_y + 9*c_y*pow(u, 3)*pow(v, 2) - 6*c_y*pow(u, 3)*v - 27*c_y*pow(u, 2)*pow(v, 2) + 18*c_y*pow(u, 2)*v + 27*c_y*u*pow(v, 2) - 18*c_y*u*v - 9*c_y*pow(v, 2) + 6*c_y*v - 3*d_y*pow(u, 3)*pow(v, 2) + 9*d_y*pow(u, 2)*pow(v, 2) - 9*d_y*u*pow(v, 2) + 3*d_y*pow(v, 2) - 9*e_y*pow(u, 3)*pow(v, 2) + 18*e_y*pow(u, 3)*v - 9*e_y*pow(u, 3) + 18*e_y*pow(u, 2)*pow(v, 2) - 36*e_y*pow(u, 2)*v + 18*e_y*pow(u, 2) - 9*e_y*u*pow(v, 2) + 18*e_y*u*v - 9*e_y*u + 27*f_y*pow(u, 3)*pow(v, 2) - 36*f_y*pow(u, 3)*v + 9*f_y*pow(u, 3) - 54*f_y*pow(u, 2)*pow(v, 2) + 72*f_y*pow(u, 2)*v - 18*f_y*pow(u, 2) + 27*f_y*u*pow(v, 2) - 36*f_y*u*v + 9*f_y*u - 27*g_y*pow(u, 3)*pow(v, 2) + 18*g_y*pow(u, 3)*v + 54*g_y*pow(u, 2)*pow(v, 2) - 36*g_y*pow(u, 2)*v - 27*g_y*u*pow(v, 2) + 18*g_y*u*v + 9*h_y*pow(u, 3)*pow(v, 2) - 18*h_y*pow(u, 2)*pow(v, 2) + 9*h_y*u*pow(v, 2) + 9*i_y*pow(u, 3)*pow(v, 2) - 18*i_y*pow(u, 3)*v + 9*i_y*pow(u, 3) - 9*i_y*pow(u, 2)*pow(v, 2) + 18*i_y*pow(u, 2)*v - 9*i_y*pow(u, 2) - 27*j_y*pow(u, 3)*pow(v, 2) + 36*j_y*pow(u, 3)*v - 9*j_y*pow(u, 3) + 27*j_y*pow(u, 2)*pow(v, 2) - 36*j_y*pow(u, 2)*v + 9*j_y*pow(u, 2) + 27*k_y*pow(u, 3)*pow(v, 2) - 18*k_y*pow(u, 3)*v - 27*k_y*pow(u, 2)*pow(v, 2) + 18*k_y*pow(u, 2)*v - 9*l_y*pow(u, 3)*pow(v, 2) + 9*l_y*pow(u, 2)*pow(v, 2) - 3*m_y*pow(u, 3)*pow(v, 2) + 6*m_y*pow(u, 3)*v - 3*m_y*pow(u, 3) + 9*n_y*pow(u, 3)*pow(v, 2) - 12*n_y*pow(u, 3)*v + 3*n_y*pow(u, 3) - 9*o_y*pow(u, 3)*pow(v, 2) + 6*o_y*pow(u, 3)*v + 3*p_y*pow(u, 3)*pow(v, 2))*(3*a_z*pow(u, 2)*pow(v, 3) - 9*a_z*pow(u, 2)*pow(v, 2) + 9*a_z*pow(u, 2)*v - 3*a_z*pow(u, 2) - 6*a_z*u*pow(v, 3) + 18*a_z*u*pow(v, 2) - 18*a_z*u*v + 6*a_z*u + 3*a_z*pow(v, 3) - 9*a_z*pow(v, 2) + 9*a_z*v - 3*a_z - 9*b_z*pow(u, 2)*pow(v, 3) + 18*b_z*pow(u, 2)*pow(v, 2) - 9*b_z*pow(u, 2)*v + 18*b_z*u*pow(v, 3) - 36*b_z*u*pow(v, 2) + 18*b_z*u*v - 9*b_z*pow(v, 3) + 18*b_z*pow(v, 2) - 9*b_z*v + 9*c_z*pow(u, 2)*pow(v, 3) - 9*c_z*pow(u, 2)*pow(v, 2) - 18*c_z*u*pow(v, 3) + 18*c_z*u*pow(v, 2) + 9*c_z*pow(v, 3) - 9*c_z*pow(v, 2) - 3*d_z*pow(u, 2)*pow(v, 3) + 6*d_z*u*pow(v, 3) - 3*d_z*pow(v, 3) - 9*e_z*pow(u, 2)*pow(v, 3) + 27*e_z*pow(u, 2)*pow(v, 2) - 27*e_z*pow(u, 2)*v + 9*e_z*pow(u, 2) + 12*e_z*u*pow(v, 3) - 36*e_z*u*pow(v, 2) + 36*e_z*u*v - 12*e_z*u - 3*e_z*pow(v, 3) + 9*e_z*pow(v, 2) - 9*e_z*v + 3*e_z + 27*f_z*pow(u, 2)*pow(v, 3) - 54*f_z*pow(u, 2)*pow(v, 2) + 27*f_z*pow(u, 2)*v - 36*f_z*u*pow(v, 3) + 72*f_z*u*pow(v, 2) - 36*f_z*u*v + 9*f_z*pow(v, 3) - 18*f_z*pow(v, 2) + 9*f_z*v - 27*g_z*pow(u, 2)*pow(v, 3) + 27*g_z*pow(u, 2)*pow(v, 2) + 36*g_z*u*pow(v, 3) - 36*g_z*u*pow(v, 2) - 9*g_z*pow(v, 3) + 9*g_z*pow(v, 2) + 9*h_z*pow(u, 2)*pow(v, 3) - 12*h_z*u*pow(v, 3) + 3*h_z*pow(v, 3) + 9*i_z*pow(u, 2)*pow(v, 3) - 27*i_z*pow(u, 2)*pow(v, 2) + 27*i_z*pow(u, 2)*v - 9*i_z*pow(u, 2) - 6*i_z*u*pow(v, 3) + 18*i_z*u*pow(v, 2) - 18*i_z*u*v + 6*i_z*u - 27*j_z*pow(u, 2)*pow(v, 3) + 54*j_z*pow(u, 2)*pow(v, 2) - 27*j_z*pow(u, 2)*v + 18*j_z*u*pow(v, 3) - 36*j_z*u*pow(v, 2) + 18*j_z*u*v + 27*k_z*pow(u, 2)*pow(v, 3) - 27*k_z*pow(u, 2)*pow(v, 2) - 18*k_z*u*pow(v, 3) + 18*k_z*u*pow(v, 2) - 9*l_z*pow(u, 2)*pow(v, 3) + 6*l_z*u*pow(v, 3) - 3*m_z*pow(u, 2)*pow(v, 3) + 9*m_z*pow(u, 2)*pow(v, 2) - 9*m_z*pow(u, 2)*v + 3*m_z*pow(u, 2) + 9*n_z*pow(u, 2)*pow(v, 3) - 18*n_z*pow(u, 2)*pow(v, 2) + 9*n_z*pow(u, 2)*v - 9*o_z*pow(u, 2)*pow(v, 3) + 9*o_z*pow(u, 2)*pow(v, 2) + 3*p_z*pow(u, 2)*pow(v, 3));
float y = -(3*a_x*pow(u, 2)*pow(v, 3) - 9*a_x*pow(u, 2)*pow(v, 2) + 9*a_x*pow(u, 2)*v - 3*a_x*pow(u, 2) - 6*a_x*u*pow(v, 3) + 18*a_x*u*pow(v, 2) - 18*a_x*u*v + 6*a_x*u + 3*a_x*pow(v, 3) - 9*a_x*pow(v, 2) + 9*a_x*v - 3*a_x - 9*b_x*pow(u, 2)*pow(v, 3) + 18*b_x*pow(u, 2)*pow(v, 2) - 9*b_x*pow(u, 2)*v + 18*b_x*u*pow(v, 3) - 36*b_x*u*pow(v, 2) + 18*b_x*u*v - 9*b_x*pow(v, 3) + 18*b_x*pow(v, 2) - 9*b_x*v + 9*c_x*pow(u, 2)*pow(v, 3) - 9*c_x*pow(u, 2)*pow(v, 2) - 18*c_x*u*pow(v, 3) + 18*c_x*u*pow(v, 2) + 9*c_x*pow(v, 3) - 9*c_x*pow(v, 2) - 3*d_x*pow(u, 2)*pow(v, 3) + 6*d_x*u*pow(v, 3) - 3*d_x*pow(v, 3) - 9*e_x*pow(u, 2)*pow(v, 3) + 27*e_x*pow(u, 2)*pow(v, 2) - 27*e_x*pow(u, 2)*v + 9*e_x*pow(u, 2) + 12*e_x*u*pow(v, 3) - 36*e_x*u*pow(v, 2) + 36*e_x*u*v - 12*e_x*u - 3*e_x*pow(v, 3) + 9*e_x*pow(v, 2) - 9*e_x*v + 3*e_x + 27*f_x*pow(u, 2)*pow(v, 3) - 54*f_x*pow(u, 2)*pow(v, 2) + 27*f_x*pow(u, 2)*v - 36*f_x*u*pow(v, 3) + 72*f_x*u*pow(v, 2) - 36*f_x*u*v + 9*f_x*pow(v, 3) - 18*f_x*pow(v, 2) + 9*f_x*v - 27*g_x*pow(u, 2)*pow(v, 3) + 27*g_x*pow(u, 2)*pow(v, 2) + 36*g_x*u*pow(v, 3) - 36*g_x*u*pow(v, 2) - 9*g_x*pow(v, 3) + 9*g_x*pow(v, 2) + 9*h_x*pow(u, 2)*pow(v, 3) - 12*h_x*u*pow(v, 3) + 3*h_x*pow(v, 3) + 9*i_x*pow(u, 2)*pow(v, 3) - 27*i_x*pow(u, 2)*pow(v, 2) + 27*i_x*pow(u, 2)*v - 9*i_x*pow(u, 2) - 6*i_x*u*pow(v, 3) + 18*i_x*u*pow(v, 2) - 18*i_x*u*v + 6*i_x*u - 27*j_x*pow(u, 2)*pow(v, 3) + 54*j_x*pow(u, 2)*pow(v, 2) - 27*j_x*pow(u, 2)*v + 18*j_x*u*pow(v, 3) - 36*j_x*u*pow(v, 2) + 18*j_x*u*v + 27*k_x*pow(u, 2)*pow(v, 3) - 27*k_x*pow(u, 2)*pow(v, 2) - 18*k_x*u*pow(v, 3) + 18*k_x*u*pow(v, 2) - 9*l_x*pow(u, 2)*pow(v, 3) + 6*l_x*u*pow(v, 3) - 3*m_x*pow(u, 2)*pow(v, 3) + 9*m_x*pow(u, 2)*pow(v, 2) - 9*m_x*pow(u, 2)*v + 3*m_x*pow(u, 2) + 9*n_x*pow(u, 2)*pow(v, 3) - 18*n_x*pow(u, 2)*pow(v, 2) + 9*n_x*pow(u, 2)*v - 9*o_x*pow(u, 2)*pow(v, 3) + 9*o_x*pow(u, 2)*pow(v, 2) + 3*p_x*pow(u, 2)*pow(v, 3))*(3*a_z*pow(u, 3)*pow(v, 2) - 6*a_z*pow(u, 3)*v + 3*a_z*pow(u, 3) - 9*a_z*pow(u, 2)*pow(v, 2) + 18*a_z*pow(u, 2)*v - 9*a_z*pow(u, 2) + 9*a_z*u*pow(v, 2) - 18*a_z*u*v + 9*a_z*u - 3*a_z*pow(v, 2) + 6*a_z*v - 3*a_z - 9*b_z*pow(u, 3)*pow(v, 2) + 12*b_z*pow(u, 3)*v - 3*b_z*pow(u, 3) + 27*b_z*pow(u, 2)*pow(v, 2) - 36*b_z*pow(u, 2)*v + 9*b_z*pow(u, 2) - 27*b_z*u*pow(v, 2) + 36*b_z*u*v - 9*b_z*u + 9*b_z*pow(v, 2) - 12*b_z*v + 3*b_z + 9*c_z*pow(u, 3)*pow(v, 2) - 6*c_z*pow(u, 3)*v - 27*c_z*pow(u, 2)*pow(v, 2) + 18*c_z*pow(u, 2)*v + 27*c_z*u*pow(v, 2) - 18*c_z*u*v - 9*c_z*pow(v, 2) + 6*c_z*v - 3*d_z*pow(u, 3)*pow(v, 2) + 9*d_z*pow(u, 2)*pow(v, 2) - 9*d_z*u*pow(v, 2) + 3*d_z*pow(v, 2) - 9*e_z*pow(u, 3)*pow(v, 2) + 18*e_z*pow(u, 3)*v - 9*e_z*pow(u, 3) + 18*e_z*pow(u, 2)*pow(v, 2) - 36*e_z*pow(u, 2)*v + 18*e_z*pow(u, 2) - 9*e_z*u*pow(v, 2) + 18*e_z*u*v - 9*e_z*u + 27*f_z*pow(u, 3)*pow(v, 2) - 36*f_z*pow(u, 3)*v + 9*f_z*pow(u, 3) - 54*f_z*pow(u, 2)*pow(v, 2) + 72*f_z*pow(u, 2)*v - 18*f_z*pow(u, 2) + 27*f_z*u*pow(v, 2) - 36*f_z*u*v + 9*f_z*u - 27*g_z*pow(u, 3)*pow(v, 2) + 18*g_z*pow(u, 3)*v + 54*g_z*pow(u, 2)*pow(v, 2) - 36*g_z*pow(u, 2)*v - 27*g_z*u*pow(v, 2) + 18*g_z*u*v + 9*h_z*pow(u, 3)*pow(v, 2) - 18*h_z*pow(u, 2)*pow(v, 2) + 9*h_z*u*pow(v, 2) + 9*i_z*pow(u, 3)*pow(v, 2) - 18*i_z*pow(u, 3)*v + 9*i_z*pow(u, 3) - 9*i_z*pow(u, 2)*pow(v, 2) + 18*i_z*pow(u, 2)*v - 9*i_z*pow(u, 2) - 27*j_z*pow(u, 3)*pow(v, 2) + 36*j_z*pow(u, 3)*v - 9*j_z*pow(u, 3) + 27*j_z*pow(u, 2)*pow(v, 2) - 36*j_z*pow(u, 2)*v + 9*j_z*pow(u, 2) + 27*k_z*pow(u, 3)*pow(v, 2) - 18*k_z*pow(u, 3)*v - 27*k_z*pow(u, 2)*pow(v, 2) + 18*k_z*pow(u, 2)*v - 9*l_z*pow(u, 3)*pow(v, 2) + 9*l_z*pow(u, 2)*pow(v, 2) - 3*m_z*pow(u, 3)*pow(v, 2) + 6*m_z*pow(u, 3)*v - 3*m_z*pow(u, 3) + 9*n_z*pow(u, 3)*pow(v, 2) - 12*n_z*pow(u, 3)*v + 3*n_z*pow(u, 3) - 9*o_z*pow(u, 3)*pow(v, 2) + 6*o_z*pow(u, 3)*v + 3*p_z*pow(u, 3)*pow(v, 2)) + (3*a_x*pow(u, 3)*pow(v, 2) - 6*a_x*pow(u, 3)*v + 3*a_x*pow(u, 3) - 9*a_x*pow(u, 2)*pow(v, 2) + 18*a_x*pow(u, 2)*v - 9*a_x*pow(u, 2) + 9*a_x*u*pow(v, 2) - 18*a_x*u*v + 9*a_x*u - 3*a_x*pow(v, 2) + 6*a_x*v - 3*a_x - 9*b_x*pow(u, 3)*pow(v, 2) + 12*b_x*pow(u, 3)*v - 3*b_x*pow(u, 3) + 27*b_x*pow(u, 2)*pow(v, 2) - 36*b_x*pow(u, 2)*v + 9*b_x*pow(u, 2) - 27*b_x*u*pow(v, 2) + 36*b_x*u*v - 9*b_x*u + 9*b_x*pow(v, 2) - 12*b_x*v + 3*b_x + 9*c_x*pow(u, 3)*pow(v, 2) - 6*c_x*pow(u, 3)*v - 27*c_x*pow(u, 2)*pow(v, 2) + 18*c_x*pow(u, 2)*v + 27*c_x*u*pow(v, 2) - 18*c_x*u*v - 9*c_x*pow(v, 2) + 6*c_x*v - 3*d_x*pow(u, 3)*pow(v, 2) + 9*d_x*pow(u, 2)*pow(v, 2) - 9*d_x*u*pow(v, 2) + 3*d_x*pow(v, 2) - 9*e_x*pow(u, 3)*pow(v, 2) + 18*e_x*pow(u, 3)*v - 9*e_x*pow(u, 3) + 18*e_x*pow(u, 2)*pow(v, 2) - 36*e_x*pow(u, 2)*v + 18*e_x*pow(u, 2) - 9*e_x*u*pow(v, 2) + 18*e_x*u*v - 9*e_x*u + 27*f_x*pow(u, 3)*pow(v, 2) - 36*f_x*pow(u, 3)*v + 9*f_x*pow(u, 3) - 54*f_x*pow(u, 2)*pow(v, 2) + 72*f_x*pow(u, 2)*v - 18*f_x*pow(u, 2) + 27*f_x*u*pow(v, 2) - 36*f_x*u*v + 9*f_x*u - 27*g_x*pow(u, 3)*pow(v, 2) + 18*g_x*pow(u, 3)*v + 54*g_x*pow(u, 2)*pow(v, 2) - 36*g_x*pow(u, 2)*v - 27*g_x*u*pow(v, 2) + 18*g_x*u*v + 9*h_x*pow(u, 3)*pow(v, 2) - 18*h_x*pow(u, 2)*pow(v, 2) + 9*h_x*u*pow(v, 2) + 9*i_x*pow(u, 3)*pow(v, 2) - 18*i_x*pow(u, 3)*v + 9*i_x*pow(u, 3) - 9*i_x*pow(u, 2)*pow(v, 2) + 18*i_x*pow(u, 2)*v - 9*i_x*pow(u, 2) - 27*j_x*pow(u, 3)*pow(v, 2) + 36*j_x*pow(u, 3)*v - 9*j_x*pow(u, 3) + 27*j_x*pow(u, 2)*pow(v, 2) - 36*j_x*pow(u, 2)*v + 9*j_x*pow(u, 2) + 27*k_x*pow(u, 3)*pow(v, 2) - 18*k_x*pow(u, 3)*v - 27*k_x*pow(u, 2)*pow(v, 2) + 18*k_x*pow(u, 2)*v - 9*l_x*pow(u, 3)*pow(v, 2) + 9*l_x*pow(u, 2)*pow(v, 2) - 3*m_x*pow(u, 3)*pow(v, 2) + 6*m_x*pow(u, 3)*v - 3*m_x*pow(u, 3) + 9*n_x*pow(u, 3)*pow(v, 2) - 12*n_x*pow(u, 3)*v + 3*n_x*pow(u, 3) - 9*o_x*pow(u, 3)*pow(v, 2) + 6*o_x*pow(u, 3)*v + 3*p_x*pow(u, 3)*pow(v, 2))*(3*a_z*pow(u, 2)*pow(v, 3) - 9*a_z*pow(u, 2)*pow(v, 2) + 9*a_z*pow(u, 2)*v - 3*a_z*pow(u, 2) - 6*a_z*u*pow(v, 3) + 18*a_z*u*pow(v, 2) - 18*a_z*u*v + 6*a_z*u + 3*a_z*pow(v, 3) - 9*a_z*pow(v, 2) + 9*a_z*v - 3*a_z - 9*b_z*pow(u, 2)*pow(v, 3) + 18*b_z*pow(u, 2)*pow(v, 2) - 9*b_z*pow(u, 2)*v + 18*b_z*u*pow(v, 3) - 36*b_z*u*pow(v, 2) + 18*b_z*u*v - 9*b_z*pow(v, 3) + 18*b_z*pow(v, 2) - 9*b_z*v + 9*c_z*pow(u, 2)*pow(v, 3) - 9*c_z*pow(u, 2)*pow(v, 2) - 18*c_z*u*pow(v, 3) + 18*c_z*u*pow(v, 2) + 9*c_z*pow(v, 3) - 9*c_z*pow(v, 2) - 3*d_z*pow(u, 2)*pow(v, 3) + 6*d_z*u*pow(v, 3) - 3*d_z*pow(v, 3) - 9*e_z*pow(u, 2)*pow(v, 3) + 27*e_z*pow(u, 2)*pow(v, 2) - 27*e_z*pow(u, 2)*v + 9*e_z*pow(u, 2) + 12*e_z*u*pow(v, 3) - 36*e_z*u*pow(v, 2) + 36*e_z*u*v - 12*e_z*u - 3*e_z*pow(v, 3) + 9*e_z*pow(v, 2) - 9*e_z*v + 3*e_z + 27*f_z*pow(u, 2)*pow(v, 3) - 54*f_z*pow(u, 2)*pow(v, 2) + 27*f_z*pow(u, 2)*v - 36*f_z*u*pow(v, 3) + 72*f_z*u*pow(v, 2) - 36*f_z*u*v + 9*f_z*pow(v, 3) - 18*f_z*pow(v, 2) + 9*f_z*v - 27*g_z*pow(u, 2)*pow(v, 3) + 27*g_z*pow(u, 2)*pow(v, 2) + 36*g_z*u*pow(v, 3) - 36*g_z*u*pow(v, 2) - 9*g_z*pow(v, 3) + 9*g_z*pow(v, 2) + 9*h_z*pow(u, 2)*pow(v, 3) - 12*h_z*u*pow(v, 3) + 3*h_z*pow(v, 3) + 9*i_z*pow(u, 2)*pow(v, 3) - 27*i_z*pow(u, 2)*pow(v, 2) + 27*i_z*pow(u, 2)*v - 9*i_z*pow(u, 2) - 6*i_z*u*pow(v, 3) + 18*i_z*u*pow(v, 2) - 18*i_z*u*v + 6*i_z*u - 27*j_z*pow(u, 2)*pow(v, 3) + 54*j_z*pow(u, 2)*pow(v, 2) - 27*j_z*pow(u, 2)*v + 18*j_z*u*pow(v, 3) - 36*j_z*u*pow(v, 2) + 18*j_z*u*v + 27*k_z*pow(u, 2)*pow(v, 3) - 27*k_z*pow(u, 2)*pow(v, 2) - 18*k_z*u*pow(v, 3) + 18*k_z*u*pow(v, 2) - 9*l_z*pow(u, 2)*pow(v, 3) + 6*l_z*u*pow(v, 3) - 3*m_z*pow(u, 2)*pow(v, 3) + 9*m_z*pow(u, 2)*pow(v, 2) - 9*m_z*pow(u, 2)*v + 3*m_z*pow(u, 2) + 9*n_z*pow(u, 2)*pow(v, 3) - 18*n_z*pow(u, 2)*pow(v, 2) + 9*n_z*pow(u, 2)*v - 9*o_z*pow(u, 2)*pow(v, 3) + 9*o_z*pow(u, 2)*pow(v, 2) + 3*p_z*pow(u, 2)*pow(v, 3));
float z = (3*a_x*pow(u, 2)*pow(v, 3) - 9*a_x*pow(u, 2)*pow(v, 2) + 9*a_x*pow(u, 2)*v - 3*a_x*pow(u, 2) - 6*a_x*u*pow(v, 3) + 18*a_x*u*pow(v, 2) - 18*a_x*u*v + 6*a_x*u + 3*a_x*pow(v, 3) - 9*a_x*pow(v, 2) + 9*a_x*v - 3*a_x - 9*b_x*pow(u, 2)*pow(v, 3) + 18*b_x*pow(u, 2)*pow(v, 2) - 9*b_x*pow(u, 2)*v + 18*b_x*u*pow(v, 3) - 36*b_x*u*pow(v, 2) + 18*b_x*u*v - 9*b_x*pow(v, 3) + 18*b_x*pow(v, 2) - 9*b_x*v + 9*c_x*pow(u, 2)*pow(v, 3) - 9*c_x*pow(u, 2)*pow(v, 2) - 18*c_x*u*pow(v, 3) + 18*c_x*u*pow(v, 2) + 9*c_x*pow(v, 3) - 9*c_x*pow(v, 2) - 3*d_x*pow(u, 2)*pow(v, 3) + 6*d_x*u*pow(v, 3) - 3*d_x*pow(v, 3) - 9*e_x*pow(u, 2)*pow(v, 3) + 27*e_x*pow(u, 2)*pow(v, 2) - 27*e_x*pow(u, 2)*v + 9*e_x*pow(u, 2) + 12*e_x*u*pow(v, 3) - 36*e_x*u*pow(v, 2) + 36*e_x*u*v - 12*e_x*u - 3*e_x*pow(v, 3) + 9*e_x*pow(v, 2) - 9*e_x*v + 3*e_x + 27*f_x*pow(u, 2)*pow(v, 3) - 54*f_x*pow(u, 2)*pow(v, 2) + 27*f_x*pow(u, 2)*v - 36*f_x*u*pow(v, 3) + 72*f_x*u*pow(v, 2) - 36*f_x*u*v + 9*f_x*pow(v, 3) - 18*f_x*pow(v, 2) + 9*f_x*v - 27*g_x*pow(u, 2)*pow(v, 3) + 27*g_x*pow(u, 2)*pow(v, 2) + 36*g_x*u*pow(v, 3) - 36*g_x*u*pow(v, 2) - 9*g_x*pow(v, 3) + 9*g_x*pow(v, 2) + 9*h_x*pow(u, 2)*pow(v, 3) - 12*h_x*u*pow(v, 3) + 3*h_x*pow(v, 3) + 9*i_x*pow(u, 2)*pow(v, 3) - 27*i_x*pow(u, 2)*pow(v, 2) + 27*i_x*pow(u, 2)*v - 9*i_x*pow(u, 2) - 6*i_x*u*pow(v, 3) + 18*i_x*u*pow(v, 2) - 18*i_x*u*v + 6*i_x*u - 27*j_x*pow(u, 2)*pow(v, 3) + 54*j_x*pow(u, 2)*pow(v, 2) - 27*j_x*pow(u, 2)*v + 18*j_x*u*pow(v, 3) - 36*j_x*u*pow(v, 2) + 18*j_x*u*v + 27*k_x*pow(u, 2)*pow(v, 3) - 27*k_x*pow(u, 2)*pow(v, 2) - 18*k_x*u*pow(v, 3) + 18*k_x*u*pow(v, 2) - 9*l_x*pow(u, 2)*pow(v, 3) + 6*l_x*u*pow(v, 3) - 3*m_x*pow(u, 2)*pow(v, 3) + 9*m_x*pow(u, 2)*pow(v, 2) - 9*m_x*pow(u, 2)*v + 3*m_x*pow(u, 2) + 9*n_x*pow(u, 2)*pow(v, 3) - 18*n_x*pow(u, 2)*pow(v, 2) + 9*n_x*pow(u, 2)*v - 9*o_x*pow(u, 2)*pow(v, 3) + 9*o_x*pow(u, 2)*pow(v, 2) + 3*p_x*pow(u, 2)*pow(v, 3))*(3*a_y*pow(u, 3)*pow(v, 2) - 6*a_y*pow(u, 3)*v + 3*a_y*pow(u, 3) - 9*a_y*pow(u, 2)*pow(v, 2) + 18*a_y*pow(u, 2)*v - 9*a_y*pow(u, 2) + 9*a_y*u*pow(v, 2) - 18*a_y*u*v + 9*a_y*u - 3*a_y*pow(v, 2) + 6*a_y*v - 3*a_y - 9*b_y*pow(u, 3)*pow(v, 2) + 12*b_y*pow(u, 3)*v - 3*b_y*pow(u, 3) + 27*b_y*pow(u, 2)*pow(v, 2) - 36*b_y*pow(u, 2)*v + 9*b_y*pow(u, 2) - 27*b_y*u*pow(v, 2) + 36*b_y*u*v - 9*b_y*u + 9*b_y*pow(v, 2) - 12*b_y*v + 3*b_y + 9*c_y*pow(u, 3)*pow(v, 2) - 6*c_y*pow(u, 3)*v - 27*c_y*pow(u, 2)*pow(v, 2) + 18*c_y*pow(u, 2)*v + 27*c_y*u*pow(v, 2) - 18*c_y*u*v - 9*c_y*pow(v, 2) + 6*c_y*v - 3*d_y*pow(u, 3)*pow(v, 2) + 9*d_y*pow(u, 2)*pow(v, 2) - 9*d_y*u*pow(v, 2) + 3*d_y*pow(v, 2) - 9*e_y*pow(u, 3)*pow(v, 2) + 18*e_y*pow(u, 3)*v - 9*e_y*pow(u, 3) + 18*e_y*pow(u, 2)*pow(v, 2) - 36*e_y*pow(u, 2)*v + 18*e_y*pow(u, 2) - 9*e_y*u*pow(v, 2) + 18*e_y*u*v - 9*e_y*u + 27*f_y*pow(u, 3)*pow(v, 2) - 36*f_y*pow(u, 3)*v + 9*f_y*pow(u, 3) - 54*f_y*pow(u, 2)*pow(v, 2) + 72*f_y*pow(u, 2)*v - 18*f_y*pow(u, 2) + 27*f_y*u*pow(v, 2) - 36*f_y*u*v + 9*f_y*u - 27*g_y*pow(u, 3)*pow(v, 2) + 18*g_y*pow(u, 3)*v + 54*g_y*pow(u, 2)*pow(v, 2) - 36*g_y*pow(u, 2)*v - 27*g_y*u*pow(v, 2) + 18*g_y*u*v + 9*h_y*pow(u, 3)*pow(v, 2) - 18*h_y*pow(u, 2)*pow(v, 2) + 9*h_y*u*pow(v, 2) + 9*i_y*pow(u, 3)*pow(v, 2) - 18*i_y*pow(u, 3)*v + 9*i_y*pow(u, 3) - 9*i_y*pow(u, 2)*pow(v, 2) + 18*i_y*pow(u, 2)*v - 9*i_y*pow(u, 2) - 27*j_y*pow(u, 3)*pow(v, 2) + 36*j_y*pow(u, 3)*v - 9*j_y*pow(u, 3) + 27*j_y*pow(u, 2)*pow(v, 2) - 36*j_y*pow(u, 2)*v + 9*j_y*pow(u, 2) + 27*k_y*pow(u, 3)*pow(v, 2) - 18*k_y*pow(u, 3)*v - 27*k_y*pow(u, 2)*pow(v, 2) + 18*k_y*pow(u, 2)*v - 9*l_y*pow(u, 3)*pow(v, 2) + 9*l_y*pow(u, 2)*pow(v, 2) - 3*m_y*pow(u, 3)*pow(v, 2) + 6*m_y*pow(u, 3)*v - 3*m_y*pow(u, 3) + 9*n_y*pow(u, 3)*pow(v, 2) - 12*n_y*pow(u, 3)*v + 3*n_y*pow(u, 3) - 9*o_y*pow(u, 3)*pow(v, 2) + 6*o_y*pow(u, 3)*v + 3*p_y*pow(u, 3)*pow(v, 2)) - (3*a_x*pow(u, 3)*pow(v, 2) - 6*a_x*pow(u, 3)*v + 3*a_x*pow(u, 3) - 9*a_x*pow(u, 2)*pow(v, 2) + 18*a_x*pow(u, 2)*v - 9*a_x*pow(u, 2) + 9*a_x*u*pow(v, 2) - 18*a_x*u*v + 9*a_x*u - 3*a_x*pow(v, 2) + 6*a_x*v - 3*a_x - 9*b_x*pow(u, 3)*pow(v, 2) + 12*b_x*pow(u, 3)*v - 3*b_x*pow(u, 3) + 27*b_x*pow(u, 2)*pow(v, 2) - 36*b_x*pow(u, 2)*v + 9*b_x*pow(u, 2) - 27*b_x*u*pow(v, 2) + 36*b_x*u*v - 9*b_x*u + 9*b_x*pow(v, 2) - 12*b_x*v + 3*b_x + 9*c_x*pow(u, 3)*pow(v, 2) - 6*c_x*pow(u, 3)*v - 27*c_x*pow(u, 2)*pow(v, 2) + 18*c_x*pow(u, 2)*v + 27*c_x*u*pow(v, 2) - 18*c_x*u*v - 9*c_x*pow(v, 2) + 6*c_x*v - 3*d_x*pow(u, 3)*pow(v, 2) + 9*d_x*pow(u, 2)*pow(v, 2) - 9*d_x*u*pow(v, 2) + 3*d_x*pow(v, 2) - 9*e_x*pow(u, 3)*pow(v, 2) + 18*e_x*pow(u, 3)*v - 9*e_x*pow(u, 3) + 18*e_x*pow(u, 2)*pow(v, 2) - 36*e_x*pow(u, 2)*v + 18*e_x*pow(u, 2) - 9*e_x*u*pow(v, 2) + 18*e_x*u*v - 9*e_x*u + 27*f_x*pow(u, 3)*pow(v, 2) - 36*f_x*pow(u, 3)*v + 9*f_x*pow(u, 3) - 54*f_x*pow(u, 2)*pow(v, 2) + 72*f_x*pow(u, 2)*v - 18*f_x*pow(u, 2) + 27*f_x*u*pow(v, 2) - 36*f_x*u*v + 9*f_x*u - 27*g_x*pow(u, 3)*pow(v, 2) + 18*g_x*pow(u, 3)*v + 54*g_x*pow(u, 2)*pow(v, 2) - 36*g_x*pow(u, 2)*v - 27*g_x*u*pow(v, 2) + 18*g_x*u*v + 9*h_x*pow(u, 3)*pow(v, 2) - 18*h_x*pow(u, 2)*pow(v, 2) + 9*h_x*u*pow(v, 2) + 9*i_x*pow(u, 3)*pow(v, 2) - 18*i_x*pow(u, 3)*v + 9*i_x*pow(u, 3) - 9*i_x*pow(u, 2)*pow(v, 2) + 18*i_x*pow(u, 2)*v - 9*i_x*pow(u, 2) - 27*j_x*pow(u, 3)*pow(v, 2) + 36*j_x*pow(u, 3)*v - 9*j_x*pow(u, 3) + 27*j_x*pow(u, 2)*pow(v, 2) - 36*j_x*pow(u, 2)*v + 9*j_x*pow(u, 2) + 27*k_x*pow(u, 3)*pow(v, 2) - 18*k_x*pow(u, 3)*v - 27*k_x*pow(u, 2)*pow(v, 2) + 18*k_x*pow(u, 2)*v - 9*l_x*pow(u, 3)*pow(v, 2) + 9*l_x*pow(u, 2)*pow(v, 2) - 3*m_x*pow(u, 3)*pow(v, 2) + 6*m_x*pow(u, 3)*v - 3*m_x*pow(u, 3) + 9*n_x*pow(u, 3)*pow(v, 2) - 12*n_x*pow(u, 3)*v + 3*n_x*pow(u, 3) - 9*o_x*pow(u, 3)*pow(v, 2) + 6*o_x*pow(u, 3)*v + 3*p_x*pow(u, 3)*pow(v, 2))*(3*a_y*pow(u, 2)*pow(v, 3) - 9*a_y*pow(u, 2)*pow(v, 2) + 9*a_y*pow(u, 2)*v - 3*a_y*pow(u, 2) - 6*a_y*u*pow(v, 3) + 18*a_y*u*pow(v, 2) - 18*a_y*u*v + 6*a_y*u + 3*a_y*pow(v, 3) - 9*a_y*pow(v, 2) + 9*a_y*v - 3*a_y - 9*b_y*pow(u, 2)*pow(v, 3) + 18*b_y*pow(u, 2)*pow(v, 2) - 9*b_y*pow(u, 2)*v + 18*b_y*u*pow(v, 3) - 36*b_y*u*pow(v, 2) + 18*b_y*u*v - 9*b_y*pow(v, 3) + 18*b_y*pow(v, 2) - 9*b_y*v + 9*c_y*pow(u, 2)*pow(v, 3) - 9*c_y*pow(u, 2)*pow(v, 2) - 18*c_y*u*pow(v, 3) + 18*c_y*u*pow(v, 2) + 9*c_y*pow(v, 3) - 9*c_y*pow(v, 2) - 3*d_y*pow(u, 2)*pow(v, 3) + 6*d_y*u*pow(v, 3) - 3*d_y*pow(v, 3) - 9*e_y*pow(u, 2)*pow(v, 3) + 27*e_y*pow(u, 2)*pow(v, 2) - 27*e_y*pow(u, 2)*v + 9*e_y*pow(u, 2) + 12*e_y*u*pow(v, 3) - 36*e_y*u*pow(v, 2) + 36*e_y*u*v - 12*e_y*u - 3*e_y*pow(v, 3) + 9*e_y*pow(v, 2) - 9*e_y*v + 3*e_y + 27*f_y*pow(u, 2)*pow(v, 3) - 54*f_y*pow(u, 2)*pow(v, 2) + 27*f_y*pow(u, 2)*v - 36*f_y*u*pow(v, 3) + 72*f_y*u*pow(v, 2) - 36*f_y*u*v + 9*f_y*pow(v, 3) - 18*f_y*pow(v, 2) + 9*f_y*v - 27*g_y*pow(u, 2)*pow(v, 3) + 27*g_y*pow(u, 2)*pow(v, 2) + 36*g_y*u*pow(v, 3) - 36*g_y*u*pow(v, 2) - 9*g_y*pow(v, 3) + 9*g_y*pow(v, 2) + 9*h_y*pow(u, 2)*pow(v, 3) - 12*h_y*u*pow(v, 3) + 3*h_y*pow(v, 3) + 9*i_y*pow(u, 2)*pow(v, 3) - 27*i_y*pow(u, 2)*pow(v, 2) + 27*i_y*pow(u, 2)*v - 9*i_y*pow(u, 2) - 6*i_y*u*pow(v, 3) + 18*i_y*u*pow(v, 2) - 18*i_y*u*v + 6*i_y*u - 27*j_y*pow(u, 2)*pow(v, 3) + 54*j_y*pow(u, 2)*pow(v, 2) - 27*j_y*pow(u, 2)*v + 18*j_y*u*pow(v, 3) - 36*j_y*u*pow(v, 2) + 18*j_y*u*v + 27*k_y*pow(u, 2)*pow(v, 3) - 27*k_y*pow(u, 2)*pow(v, 2) - 18*k_y*u*pow(v, 3) + 18*k_y*u*pow(v, 2) - 9*l_y*pow(u, 2)*pow(v, 3) + 6*l_y*u*pow(v, 3) - 3*m_y*pow(u, 2)*pow(v, 3) + 9*m_y*pow(u, 2)*pow(v, 2) - 9*m_y*pow(u, 2)*v + 3*m_y*pow(u, 2) + 9*n_y*pow(u, 2)*pow(v, 3) - 18*n_y*pow(u, 2)*pow(v, 2) + 9*n_y*pow(u, 2)*v - 9*o_y*pow(u, 2)*pow(v, 3) + 9*o_y*pow(u, 2)*pow(v, 2) + 3*p_y*pow(u, 2)*pow(v, 3));

"""
