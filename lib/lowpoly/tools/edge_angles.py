"""Find the sharp creases in a region of an animal's skin in the bind pose: for every edge shared by two triangles inside a box, the
angle between the two triangles' normals (0 = flat, 90 = a square corner, 180 = a knife edge folded back on itself). A crease of
more than about 90 degrees shows as a hard line through smooth shading, as the T. rex's brow did at 141 degrees. Standard library
only; only reads the viewer's files.
Usage: python -I edge_angles.py <model.gltf> - <z from> <z to> <y from> <y to> [x from=0.05] [how many=8]
  Coordinates are the model's (metres, the animal faces +z); only x >= x from is searched (one side of a symmetric model)."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 7 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, math, os, sys
from collections import defaultdict

D, AID = sys.argv[1:3]
ZA, ZB, YA, YB = (float(v) for v in sys.argv[3:7])
XA = float(sys.argv[7]) if len(sys.argv) > 7 else 0.05
N = int(sys.argv[8]) if len(sys.argv) > 8 else 8
here = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
V, T = g['V'], g['T']; P = [v[0] for v in V]


def normal(f):
    a, b, c = (P[i] for i in f)
    u = [b[k] - a[k] for k in range(3)]; v = [c[k] - a[k] for k in range(3)]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    l = math.sqrt(sum(x * x for x in n)) or 1.0
    return [x / l for x in n]


# vertices that sit at the same place (the corners duplicated for a texture seam) are one vertex here
at = {}; same = [at.setdefault(tuple(round(c, 5) for c in p), i) for i, p in enumerate(P)]
edges = defaultdict(list)
for f in T:
    for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])): edges[frozenset((same[a], same[b]))].append(f)
found = []
for e, fs in edges.items():
    if len(fs) != 2: continue
    a, b = tuple(e); pa, pb = P[a], P[b]
    if not all(XA <= p[0] and ZA <= p[2] <= ZB and YA <= p[1] <= YB for p in (pa, pb)): continue
    n1, n2 = normal(fs[0]), normal(fs[1])
    found.append((math.degrees(math.acos(max(-1.0, min(1.0, sum(n1[k] * n2[k] for k in range(3)))))), pa, pb))
found.sort(key=lambda t: -t[0])
print('%s: %d edges in the box; the sharpest %d (angle between the triangles\' normals):' % (g['A']['name'], len(found), min(N, len(found))))
for ang, pa, pb in found[:N]:
    print('  %5.1f deg   (%.2f, %.2f, %.2f) - (%.2f, %.2f, %.2f)' % ((ang,) + tuple(pa) + tuple(pb)))
if found: print('  mean of those: %.1f deg' % (sum(a for a, _, _ in found[:N]) / min(N, len(found))))
