#!/usr/bin/python

from sympy import *
from sympy.matrices import *
from sympy.functions import sin,cos

# Vector-valued function utilities:
def VVF(*args):
    return Matrix(args)
def DVVF(m, variable):
    return Matrix([diff(m[i],variable) for i in xrange(len(m))])
def Print(label, vvf):
    print label + '\n' + '-' * len(label)
    print "x =", simplify(vvf[0])
    print "y =", simplify(vvf[1])
    print "z =", simplify(vvf[2])
    print

u, v = symbols('u v')
def Sweep(curvePositions, curveNormals, crossSection):
    """Takes three vector-valued functions:"""
    """The first two arguments are functions of u"""
    """The crossSection should be a function of v"""
    curveTangents = DVVF(curvePositions,u)
    curveBinormals = curveTangents.cross(curveNormals).transpose()
    curveBasis = (curveNormals.row_join(curveTangents).row_join(curveBinormals)).transpose()
    return curveBasis * crossSection
def NormalFunc(f):
    """Takes a vector-valued function of u and v"""
    """Computes formula for determining the surface normal at any point"""
    dfdu = DVVF(f, u)
    dfdv = DVVF(f, v)
    return dfdu.cross(dfdv)

r, R = symbols('r R')
positions = VVF(cos(u), sin(u), 0)
normals = VVF(cos(u), sin(u), 0)
crossSection = VVF(R + r*cos(v), 0, r*sin(v))
torus = Sweep(positions, normals, crossSection)
normals = NormalFunc(torus)

Print('Torus Surface', torus)
Print('Torus Normals', normals)
