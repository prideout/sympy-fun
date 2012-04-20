#!/usr/bin/python

from sympy import diff, simplify, symbols
from sympy.matrices import *
from sympy.functions import sin,cos

# Vector-valued function utilities:
def VVF(*args):
    return Matrix(args)
def DVVF(m, variable):
    return m.applyfunc(lambda f: diff(f,variable))
def Print(label, vvf):
    print label + '\n' + '-' * len(label)
    print "x =", vvf[0]
    print "y =", vvf[1]
    print "z =", vvf[2]
    print
def PrintPlot(vvf):
    """Paste into Wolfram Alpha and enjoy"""
    strings = tuple(map(str, vvf))
    print "ParametricPlot3D[{%s, %s, %s}, {u,0,2pi}, {v,0,2pi}]" % strings
def Simplify(m):
    m.simplify()
    return m
def Normalized(m):
    return Simplify(m / simplify(m.norm()))

u, v = symbols('u v', positive=True)

def Sweep(sweepCurve, crossSection):
    """Takes two vector-valued functions: """
    """ - sweepCurve is a function of u   """
    """ - crossSection is a function of v """

    # Compute first-order and second-order derivatives:
    d = DVVF(sweepCurve,u)
    dd = DVVF(d,u)

    # Perform Gram-Schmidt orthogonalization:
    # Does NOT assume the sweep is an arc-length parameterization.
    t = Normalized(d)
    n = Normalized(dd - t * dd.dot(t))
    b = Normalized(t.cross(n).transpose())

    # Formulate the Frenet Frame:
    curveBasis = t.row_join(n).row_join(b)

    # Transform the cross section to the curve's space:
    return Simplify(sweepCurve + curveBasis * crossSection)

def NormalFunc(f):
    """Takes a vector-valued function of u and v"""
    """Computes formula for determining the surface normal at any point"""
    dfdu = DVVF(f, u)
    dfdv = DVVF(f, v)
    return Simplify(dfdu.cross(dfdv))

# For radius symbols, we need to specify a positive assumption;
# this prevents "Abs" expressions from cropping up in "normalize"
r, R = symbols('r R', positive=True)

sweepCurve = VVF(R*cos(u), R*sin(u), 0)
crossSection = VVF(0, -r*cos(v), r*sin(v))
torus = Sweep(sweepCurve, crossSection)
normals = NormalFunc(torus)

print
Print('Torus Surface', torus)
Print('Torus Normals', normals)
print
PrintPlot(torus.subs({R: 3, r: 1}))
print
