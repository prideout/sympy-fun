#!/usr/bin/python

from sympy import diff, simplify, symbols
from sympy.matrices import *
from sympy.functions import sin,cos

# Vector-valued function utilities:
def VVF(*args):
    return Matrix(args)
def DVVF(m, variable):
    return m.applyfunc(lambda f: diff(f,variable))
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

