#!/usr/bin/python

from sympy import diff, simplify, symbols
from sympy.matrices import *
from sympy.functions import sin,cos

# Vector-valued function utilities:
def VVF(*args):
    return Matrix(args)
def DVVF(m, variable):
    return Matrix([diff(m[i],variable) for i in xrange(len(m))])
def Print(label, vvf):
    print label + '\n' + '-' * len(label)
    print "x =", vvf[0]
    print "y =", vvf[1]
    print "z =", vvf[2]
    print
def Simplify(m):
    for i in xrange(len(m)):
        m[i] = simplify(m[i])
    return m

u, v = symbols('u v')

def Sweep(curvePositions, curveNormals, crossSection):
    """Takes three vector-valued functions:"""
    """The first two arguments are functions of u"""
    """The crossSection should be a function of v"""
    curveTangents = DVVF(curvePositions,u)
    curveBinormals = curveNormals.cross(curveTangents).transpose()
    curveBinormals = Simplify(curveBinormals).normalized()
    curveBasis = curveNormals.row_join(curveTangents).row_join(curveBinormals)
    return curvePositions + curveBasis * crossSection
def NormalFunc(f):
    """Takes a vector-valued function of u and v"""
    """Computes formula for determining the surface normal at any point"""
    dfdu = DVVF(f, u)
    dfdv = DVVF(f, v)
    return Simplify(dfdu.cross(dfdv))

# For radius symbols, we need to specify a positive assumption;
# this prevents "Abs" expressions from cropping up in "normalize"
r, R = symbols('r R', positive=True)

positions = VVF(R*cos(u), R*sin(u), 0)
normals = VVF(cos(u), sin(u), 0)
crossSection = VVF(r*cos(v), 0, r*sin(v))
torus = Sweep(positions, normals, crossSection)
normals = NormalFunc(torus)

Print('Torus Surface', torus)
Print('Torus Normals', normals)
