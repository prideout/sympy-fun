#!/usr/bin/python

from Derive import *

def Print(label, vvf):
    print label + '\n' + '-' * len(label)
    print "x =", vvf[0]
    print "y =", vvf[1]
    print "z =", vvf[2]
    print

# For radius symbols, we need to specify a positive assumption;
# this prevents "Abs" expressions from cropping up in "normalize"
r, R = symbols('r R', positive=True)
h, f = symbols('h f') # h and f control height & freq of ridges

# Torus
sweepCurve = VVF(R*cos(u), R*sin(u), 0)
crossSection = VVF(0, -r*cos(v), r*sin(v))
surface = Sweep(sweepCurve, crossSection)
normals = NormalFunc(surface)
print
Print('Torus Surface', surface)
Print('Torus Normals', normals)
print '\n' , '=' * 60

# Torus with Meridian Ridges
r2 = r + h*sin(u*f)
crossSection = VVF(0, -r2*cos(v), r2*sin(v))
surface = Sweep(sweepCurve, crossSection)
normals = NormalFunc(surface)
Print('Ridged Torus Surface', surface)
Print('Ridged Torus Normals', normals)
print '\n', '-' * 60

# http://docs.sympy.org/0.7.1/modules/utilities/codegen.html

# Trefoil with Longitudinal Ridges
# http://en.wikipedia.org/wiki/Trefoil_knot

# Torus with Trefoil Ridge
# http://en.wikipedia.org/wiki/Trefoil_knot

# Bicubic Patch
