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
    curveBinormals = curveNormals.cross(curveTangents).transpose()
    curveBasis = (curveNormals.row_join(curveTangents).row_join(curveBinormals))
    return curveBasis * crossSection

def NormalFunc(f):
    """Takes a vector-valued function of u and v"""
    """Computes formula for determining the surface normal at any point"""
    dfdu = DVVF(f, u)
    dfdv = DVVF(f, v)
    return dfdu.cross(dfdv)

r, R, h, f = symbols('r R h f') # h and f control height & freq of ridges
positions = VVF(cos(u), sin(u), 0)
normals = VVF(cos(u), sin(u), 0)
crossSection = VVF(R + (r+h*sin(f*u))*cos(v), 0, (r+h*sin(f*u))*sin(v))
torus = Sweep(positions, normals, crossSection)
normals = NormalFunc(torus)

Print('Ridged Torus Surface', torus)
Print('Ridged Torus Normals', normals)
