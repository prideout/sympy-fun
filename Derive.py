#!/usr/bin/python

from sympy import diff, simplify, symbols, trigsimp
from sympy.matrices import *
from sympy.functions import sin,cos
import sys

def Progress():
    sys.stdout.write('.')
    sys.stdout.flush()

# Vector-valued function utilities:
def VVF(*args):
    return Matrix(args)
def DVVF(m, variable):
    return m.applyfunc(lambda f: diff(f,variable))
def Simplify(m):
#    m.simplify()
    return m
def Normalized(m):
    m = Simplify(m)
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
    Progress()
    t = Normalized(d)
    Progress()
    n = Normalized(dd - t * dd.dot(t))
    Progress()
    b = Normalized(t.cross(n).transpose())
    Progress()

    # Formulate the Frenet Frame:
    curveBasis = t.row_join(n).row_join(b)

    # Transform the cross section to the curve's space:
    s = sweepCurve + curveBasis * crossSection

    # Simplify and return:
    s = Simplify(s)
    print "."
    return s

def NormalFunc(f):
    """Takes a vector-valued function of u and v"""
    """Computes formula for determining the surface normal at any point"""
    dfdu = DVVF(f, u)
    dfdv = DVVF(f, v)
    return Simplify(dfdu.cross(dfdv))

