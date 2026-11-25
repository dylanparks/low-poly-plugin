"""Textured close-ups of a head in the bind pose (front, three-quarter, side; orthographic, z-buffered, flat lit), plus
the same views with every triangle coloured by where its texture comes from, to see how the face, eyes and muzzle are
laid onto the geometry. Standard library only; only reads the viewer's files.
Usage: python -I head_textured.py <model.gltf> <out.png> <animal id> [head fraction of length, or - for the rig's head (default)] [clip phase]
With a clip name and a phase (0..1) the head is drawn skinned in that frame of the clip (an open mouth, a turned head)."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, struct, sys, zlib

D, OUT, AID = sys.argv[1:4]
FRAC_GIVEN = len(sys.argv) > 4 and sys.argv[4] != '-'
FRAC = float(sys.argv[4]) if FRAC_GIVEN else 0.22
CLIP, PHASE = (sys.argv[5], float(sys.argv[6])) if len(sys.argv) > 6 else (None, 0.0)
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
A, V, T = g['A'], g['V'], g['T']
uvs = []
for s in A['subs']:
    raw = base64.b64decode(s['v'])
    for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
tw, th, tex = read_png(g['texpath']())
P = [v[0] for v in V]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
lo, H, zmax, zmin = min(ys), max(ys) - min(ys), max(zs), min(zs)
# the head from the rig (lowpoly/rig_parts.py), or from the height rule when the rig shows none or a fraction was given
from lowpoly import rig_parts
_R = rig_parts.parts(A, V); head = None if FRAC_GIVEN else rig_parts.head_triangles(_R, T)
HEAD_RULE = ('rig: ' + _R['head']['rule']) if head else 'height: the front %.0f%% of the length above 40%% of the height' % (100 * FRAC)
if not head: head = [t for t in T if all(P[i][2] > zmax - FRAC * (zmax - zmin) and P[i][1] > lo + 0.40 * H for i in t)]   # chosen in the bind pose
if not head: sys.exit('head_textured: no head triangles found (%s)' % HEAD_RULE)
if CLIP: P = g['skin'](g['world'](g['pose_at'](g['clip'](CLIP), PHASE)))
hp = [P[i] for t in head for i in t]
cen = [(min(q[k] for q in hp) + max(q[k] for q in hp)) / 2 for k in range(3)]
span = max(max(q[k] for q in hp) - min(q[k] for q in hp) for k in range(3))
S = 300; sc = (S - 24) / span
c45, s45 = math.cos(math.radians(40)), math.sin(math.radians(40))
VIEWS = [  # name, projection to (x right, y down, depth toward the viewer), light direction
    ('front', lambda p: (p[0] - cen[0], -(p[1] - cen[1]), p[2] - cen[2])),
    ('3/4', lambda p: ((p[0] - cen[0]) * c45 + (p[2] - cen[2]) * s45, -(p[1] - cen[1]), -(p[0] - cen[0]) * s45 + (p[2] - cen[2]) * c45)),
    ('side', lambda p: ((p[2] - cen[2]), -(p[1] - cen[1]), p[0] - cen[0])),
]
W = S * len(VIEWS); img = [[(40, 42, 48)] * W for _ in range(2 * S)]
for vi, (name, proj) in enumerate(VIEWS):
    zb = [[-1e9] * S for _ in range(S)]
    for t in head:
        q = [proj(P[i]) for i in t]
        pts = [(S / 2 + x * sc, S / 2 + y * sc, d) for x, y, d in q]
        (x0, y0, _), (x1, y1, _), (x2, y2, _) = pts
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9: continue
        e1 = [P[t[1]][k] - P[t[0]][k] for k in range(3)]; e2 = [P[t[2]][k] - P[t[0]][k] for k in range(3)]
        n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
        ln = math.sqrt(sum(v * v for v in n)) or 1
        lit = 0.55 + 0.45 * abs(n[1] / ln * 0.6 + n[2] / ln * 0.5 + n[0] / ln * 0.3)
        tint = ((t[0] * 97) % 200 + 40, (t[0] * 57) % 200 + 40, (t[0] * 31) % 200 + 40)
        for py in range(int(max(0, min(y0, y1, y2))), int(min(S - 1, max(y0, y1, y2))) + 1):
            for px in range(int(max(0, min(x0, x1, x2))), int(min(S - 1, max(x0, x1, x2))) + 1):
                xx, yy = px + 0.5, py + 0.5
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / den
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / den; c = 1 - a - b
                if a < -1e-4 or b < -1e-4 or c < -1e-4: continue
                dep = a * pts[0][2] + b * pts[1][2] + c * pts[2][2]
                if dep <= zb[py][px]: continue
                zb[py][px] = dep
                u = a * uvs[t[0]][0] + b * uvs[t[1]][0] + c * uvs[t[2]][0]; v = a * uvs[t[0]][1] + b * uvs[t[1]][1] + c * uvs[t[2]][1]
                col = tex[min(th - 1, max(0, int(v * th)))][min(tw - 1, max(0, int(u * tw)))]
                img[py][vi * S + px] = tuple(min(255, int(ch * lit)) for ch in col)
                img[S + py][vi * S + px] = tint
raw = b''.join(b'\x00' + bytes(v for col in row for v in col) for row in img)
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, 2 * S, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
print(A['name'], len(head), 'head triangles (%s) ->' % HEAD_RULE, OUT)
