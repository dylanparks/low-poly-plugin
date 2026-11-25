"""Close-up side / rear / underside views of a region of an animal in the bind pose (default: the hindquarters, where
the hind legs join the belly), flat-shaded with the wireframe on top; triangles on hind-leg bones tinted red.
Standard library only; only reads the viewer's files.
Usage: python -I region_views.py <model.gltf> <out.png> <animal id> [z from=0.0] [z to=0.55] [y to=0.7] (fractions of length/height)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import re, contextlib, io, math, os, struct, sys, zlib

D, OUT, AID = sys.argv[1:4]
ZA = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
ZB = float(sys.argv[5]) if len(sys.argv) > 5 else 0.55
YB = float(sys.argv[6]) if len(sys.argv) > 6 else 0.7
here = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
A, V, T, names = g['A'], g['V'], g['T'], g['names']
P = [v[0] for v in V]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
lo, H = min(ys), max(ys) - min(ys); zmax, zmin = max(zs), min(zs)
HIND = set()
for b, n in enumerate(names):
    if re.search(r'thigh|shin|calf|bk|hip|horselink|foot|leg', n.lower()) and not re.search(r'spine', n.lower()): HIND.add(b)
ear = lambda i: sum(w for b, w in V[i][1] if b in HIND) > 0.3
zlen = zmax - zmin
head = [t for t in T if all(zmin + ZA * zlen <= P[i][2] <= zmin + ZB * zlen and P[i][1] <= lo + YB * H for i in t)]
hp = [P[i] for t in head for i in t]
c = [(min(q[k] for q in hp) + max(q[k] for q in hp)) / 2 for k in range(3)]
span = max(max(q[k] for q in hp) - min(q[k] for q in hp) for k in range(3))
S = 300; sc = (S - 20) / span
VIEWS = [('side', lambda p: (-(p[2] - c[2]), -(p[1] - c[1]), p[0]), (1, 0, 0)),      # looking from +x, head to the left
         ('rear', lambda p: (-(p[0] - c[0]), -(p[1] - c[1]), -p[2]), (0, 0, -1)),    # looking from behind
         ('below', lambda p: ((p[0] - c[0]), -(p[2] - c[2]), -p[1]), (0, -1, 0))]    # looking up from underneath, head at the top
W = S * len(VIEWS); img = bytearray([40, 42, 48] * (W * S))


def put(x, y, col):
    if 0 <= x < W and 0 <= y < S: k = (y * W + x) * 3; img[k:k + 3] = bytes(col)


def tri(pts, col):
    (x0, y0), (x1, y1), (x2, y2) = pts
    for y in range(int(max(0, min(y0, y1, y2))), int(min(S - 1, max(y0, y1, y2))) + 1):
        xs = []
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)), ((x1, y1), (x2, y2)), ((x2, y2), (x0, y0))):
            if (ay <= y + 0.5 < by) or (by <= y + 0.5 < ay): xs.append(ax + (y + 0.5 - ay) * (bx - ax) / (by - ay))
        if len(xs) >= 2:
            for x in range(int(min(xs)), int(max(xs)) + 1): put(x, y, col)


def line(a, b, col):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for s in range(n + 1): put(int(a[0] + (b[0] - a[0]) * s / n), int(a[1] + (b[1] - a[1]) * s / n), col)


for vi, (name, proj, eye) in enumerate(VIEWS):
    ox = vi * S + S // 2
    order = sorted(head, key=lambda t: sum(proj(P[i])[2] for i in t) / 3)
    for t in order:
        q = [proj(P[i]) for i in t]
        n = [(P[t[1]][(k + 1) % 3] - P[t[0]][(k + 1) % 3]) * (P[t[2]][(k + 2) % 3] - P[t[0]][(k + 2) % 3])
             - (P[t[1]][(k + 2) % 3] - P[t[0]][(k + 2) % 3]) * (P[t[2]][(k + 1) % 3] - P[t[0]][(k + 1) % 3]) for k in range(3)]
        ln = math.sqrt(sum(v * v for v in n)) or 1
        lit = 0.35 + 0.65 * abs(sum(n[k] * eye[k] for k in range(3)) / ln)
        base = (220, 90, 80) if all(ear(i) for i in t) else (200, 150, 140) if any(ear(i) for i in t) else (170, 175, 185)
        pts = [(ox + x * sc, S // 2 + y * sc) for x, y, _ in q]
        tri(pts, tuple(int(b * lit) for b in base))
        for k in range(3): line(pts[k], pts[(k + 1) % 3], (25, 25, 30))
    for x in range(vi * S, vi * S + S): put(x, 0, (90, 90, 90))
raw = b''.join(b'\x00' + bytes(img[y * W * 3:(y + 1) * W * 3]) for y in range(S))
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, S, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
print(A['name'], len(head), 'triangles ->', OUT)
