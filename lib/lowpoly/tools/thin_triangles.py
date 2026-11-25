"""Find sliver triangles in a region of an animal's skin: a triangle whose longest edge is many times its height. A sliver on a visible
surface takes the light on its own, as a bright or dark line, and stretches badly in skinning. It usually comes from joining a tall edge
to a very short one (a thin strip like a mouth line running into a deep neck). Reports each triangle's aspect (longest edge squared over
twice the area: 2.3 for an equilateral one, over about 10 is a sliver), in the bind pose and in the worst frame of a clip.
Standard library only; only reads the viewer's files.
Usage: python -I thin_triangles.py <model.gltf> - <z from> <z to> <y from> <y to> [how many=8] [clip]"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 7 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, math, os, sys

D, AID = sys.argv[1:3]
ZA, ZB, YA, YB = (float(v) for v in sys.argv[3:7])
N = int(sys.argv[7]) if len(sys.argv) > 7 else 8
CLIP = sys.argv[8] if len(sys.argv) > 8 else None
here = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
V, T = g['V'], g['T']; P0 = [v[0] for v in V]


def aspect(P, f):
    a, b, c = (P[i] for i in f)
    u = [b[k] - a[k] for k in range(3)]; v = [c[k] - a[k] for k in range(3)]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]; ar = math.sqrt(sum(x * x for x in n)) / 2
    lm = max(math.dist(a, b), math.dist(b, c), math.dist(c, a))
    return lm * lm / (2 * ar) if ar > 1e-12 else 1e9


worst = {}
frames = [P0] + ([g['skin'](g['world'](g['pose_at'](g['clip'](CLIP), k / 24))) for k in range(24)] if CLIP else [])
for ti, f in enumerate(T):
    c = [sum(P0[i][k] for i in f) / 3 for k in range(3)]
    if not (ZA <= c[2] <= ZB and YA <= c[1] <= YB): continue
    worst[ti] = (aspect(P0, f), max(aspect(P, f) for P in frames), tuple(round(x, 2) for x in c))
print('%s: the thinnest triangles in the box (aspect in the bind pose | worst in %s):' % (g['A']['name'], CLIP or 'the bind pose'))
for a0, a1, c in sorted(worst.values(), reverse=True)[:N]: print('  %5.1f | %5.1f   at (%.2f, %.2f, %.2f)' % ((a0, a1) + c))
