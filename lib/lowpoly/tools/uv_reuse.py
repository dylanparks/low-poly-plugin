"""Texture reuse: texels that two different, non-mirrored places on the mesh both map to (more than 3% of the animal's
height apart, on the same side), which makes a painted feature appear twice, e.g. an eye repeated on the muzzle.
Mirroring (left and right sharing one painted side) is not counted. Standard library only; only reads the viewer's files.
Usage: python -I uv_reuse.py <model.gltf> <name>   (or a viewer folder and one or more animal ids, to compare them)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, struct, sys, zlib
from collections import defaultdict

D, IDS = sys.argv[1], sys.argv[2:]
here = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
for aid in IDS:
    g = {}; sys.argv = ['x', D, aid]
    with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
    A, V, T = g['A'], g['V'], g['T']
    uvs = []
    for s in A['subs']:
        raw = base64.b64decode(s['v'])
        for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
    w, h, img = read_png(g['texpath']())
    P = [v[0] for v in V]; ys = [p[1] for p in P]; H = max(ys) - min(ys)
    cover = defaultdict(list)                       # texel -> [(3D point, side)]
    for t in T:
        u = [(uvs[i][0] * w, uvs[i][1] * h) for i in t]
        den = (u[1][1] - u[2][1]) * (u[0][0] - u[2][0]) + (u[2][0] - u[1][0]) * (u[0][1] - u[2][1])
        if abs(den) < 1e-9: continue
        for py in range(int(min(q[1] for q in u)), int(max(q[1] for q in u)) + 1):
            for px in range(int(min(q[0] for q in u)), int(max(q[0] for q in u)) + 1):
                x, y = px + 0.5, py + 0.5
                a = ((u[1][1] - u[2][1]) * (x - u[2][0]) + (u[2][0] - u[1][0]) * (y - u[2][1])) / den
                b = ((u[2][1] - u[0][1]) * (x - u[2][0]) + (u[0][0] - u[2][0]) * (y - u[2][1])) / den; c = 1 - a - b
                if min(a, b, c) < 0: continue
                p3 = [a * P[t[0]][k] + b * P[t[1]][k] + c * P[t[2]][k] for k in range(3)]
                cover[(px % w, py % h)].append((abs(p3[0]), p3[1], p3[2]))   # |x|: mirror twins coincide
    reused, places = 0, defaultdict(int)
    for tx, pts in cover.items():
        far = [(a, b) for i, a in enumerate(pts) for b in pts[i + 1:] if math.dist(a, b) > 0.03 * H]
        if far:
            reused += 1
            a, b = max(far, key=lambda ab: math.dist(*ab))
            places[(round(a[1] / (0.02 * H)), round(a[2] / (0.02 * H)), round(b[1] / (0.02 * H)), round(b[2] / (0.02 * H)))] += 1
    print('== %s: %d of %d used texels (%.1f%%) are reused by two places on the same side more than 3%% of the height apart'
          % (A['name'], reused, len(cover), 100 * reused / max(1, len(cover))))
    for (y1, z1, y2, z2), n in sorted(places.items(), key=lambda kv: -kv[1])[:5]:
        print('   %4d texels shared by (y %.3f, z %.3f) and (y %.3f, z %.3f)' % (n, y1 * 0.02 * H, z1 * 0.02 * H, y2 * 0.02 * H, z2 * 0.02 * H))
