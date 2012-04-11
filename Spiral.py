from sympy import *
from sympy.matrices import *
from sympy.functions import sin,cos

u, v, alpha = symbols('u v alpha')
f, twopi = Matrix([None]*3), 2*pi
twopi = 2*pi
f[0] = alpha * (1-v/twopi) * cos(2*v) * (1+cos(u)) + 0.1 * cos(2*v)
f[1] = alpha * (1-v/twopi) * sin(2*v) * (1+cos(u)) + 0.1 * sin(2*v)
f[2] = alpha * (1-v/twopi) * sin(u) + v / twopi
print f
dfdu = Matrix([diff(f[i],u) for i in (0,1,2)])
dfdv = Matrix([diff(f[i],v) for i in (0,1,2)])
n = dfdu.cross(dfdv)
print n
for i in xrange(3): print simplify(n[i])
