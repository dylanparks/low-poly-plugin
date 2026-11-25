"""How much is painted on each body region, at the same physical scale on any model: texel density (texels per metre),
mean brightness, and painted contrast at 2 cm (fine: hair, scales, wrinkles) and 8 cm (mid: clumps, folds, patches), each
divided by the region's mean brightness so a dark animal and a pale one compare fairly.

Regions come from the bone that weights each triangle most: head (head, skull, jaw, neck, ear, beak), body (pelvis, spine,
chest, hips, root), leg (thigh, calf, shin, foot, toe, paw), arm (arm, forearm, hand, clavicle: a quadruped's forelegs
too), wing (a wing's own bones, wsh/warm/wfore/whand, feathers, fingers, thumb, digits), tail; anything else is "other".
Wings are their own region so a winged quadruped's forelegs and feathered wings are measured apart (the first alicorn's
were one region, and its smooth feather paint hid how its forelegs were painted).

Measured on the large creatures of the reference game (fine / mid, legs and arms or wings): bear 0.24 / 0.09, wolf
0.08 / 0.09, werewolf 0.09-0.10 / 0.10-0.11, drake 0.30-0.33 / 0.08-0.12, dragon 0.07-0.12 / 0.16-0.18, a dark boss
0.27-0.34 / 0.24-0.30, a mechanical suit 0.11-0.12 / 0.16-0.18, at 55-200 texels per metre. Their limbs carry about as
much as their bodies (the dark boss's more), and no region of any of them is darker than 0.17 mean brightness. The first
hostile giant bat's legs and wings measured 0.05 / 0.08-0.10 at 0.08-0.09 brightness, at 235-241 texels per metre: enough
resolution, painted almost flat, and darker than anything measured.

  python region_detail.py model.gltf
Prints one line per region:  region  density tx/m  share of surface  brightness  fine  mid  (fine + mid)."""
import sys, os, re, math, base64, struct, zlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'): sys.exit(__doc__)
from lowpoly import gltf_io
src = open(os.path.join(here, 'foot_detail.py'), encoding='utf-8').read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
REG = [('wing', r'wing|^w(sh|arm|fore|hand)|feather|primar|_d\d|^d\d|digit|finger|fing|thumb'), ('arm', r'arm|fore|hand|clav|pincer'), ('head', r'head|skull|jaw|neck|ear|snout|mouth|eye|beak'),
       ('leg', r'thigh|calf|shin|foot|toe|leg|knee|ankle|paw|heel'), ('tail', r'tail'), ('body', r'pelvis|spine|chest|hips|body|root|rib|belly|torso')]


def region(n):
    n = n.lower()
    for r, pat in REG:
        if re.search(pat, n): return r
    return 'other'


A, tp = gltf_io.read_gltf(sys.argv[1])
if not tp: sys.exit('region_detail: the model has no texture')
tw, th, px = read_png(tp)
names = [b if isinstance(b, str) else b.get('name', str(i)) for i, b in enumerate(A['bones'])]
L = [[(0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]) / 255 for p in row] for row in px]
I = [[0.0] * (tw + 1) for _ in range(th + 1)]
for y in range(th):
    s = 0.0
    for x in range(tw): s += L[y][x]; I[y + 1][x + 1] = I[y][x + 1] + s


def box_at(x, y, r):
    x0, x1, y0, y1 = max(0, x - r), min(tw, x + r + 1), max(0, y - r), min(th, y + r + 1)
    return (I[y1][x1] - I[y0][x1] - I[y1][x0] + I[y0][x0]) / ((x1 - x0) * (y1 - y0))


agg = {}
for s in A['subs']:
    raw = base64.b64decode(s['v']); C = [struct.unpack_from('<16f', raw, k) for k in range(0, len(raw), 64)]
    ib = base64.b64decode(s['i']); Ix = struct.unpack('<%dH' % (len(ib) // 2), ib)
    for k in range(0, len(Ix) - 2, 3):
        cs = [C[Ix[k + j]] for j in range(3)]; acc = {}
        for c in cs:
            for j in range(4):
                if c[8 + j] > 0: acc[int(c[12 + j])] = acc.get(int(c[12 + j]), 0) + c[8 + j]
        b = max(acc, key=acc.get) if acc else 0
        P = [c[0:3] for c in cs]; U = [(c[6] * tw, c[7] * th) for c in cs]
        a = [P[1][i] - P[0][i] for i in range(3)]; bb = [P[2][i] - P[0][i] for i in range(3)]
        cr = (a[1] * bb[2] - a[2] * bb[1], a[2] * bb[0] - a[0] * bb[2], a[0] * bb[1] - a[1] * bb[0])
        A3 = 0.5 * math.sqrt(sum(x * x for x in cr))
        (x0, y0), (x1, y1), (x2, y2) = U; A2 = 0.5 * abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0))
        if A3 < 1e-10: continue
        g = agg.setdefault(region(names[b] if b < len(names) else ''), [0.0, 0.0, set()]); g[0] += A3; g[1] += A2
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9: continue
        for x in range(int(min(x0, x1, x2)), int(max(x0, x1, x2)) + 1):
            for y in range(int(min(y0, y1, y2)), int(max(y0, y1, y2)) + 1):
                qx, qy = x + .5, y + .5
                l1 = ((y1 - y2) * (qx - x2) + (x2 - x1) * (qy - y2)) / den; l2 = ((y2 - y0) * (qx - x2) + (x0 - x2) * (qy - y2)) / den
                if l1 >= 0 and l2 >= 0 and l1 + l2 <= 1: g[2].add((x % tw, y % th))
tot = sum(g[0] for g in agg.values())
print('%s: texture %dx%d' % (A.get('name', os.path.basename(sys.argv[1])), tw, th))
for rg in ('head', 'body', 'leg', 'arm', 'wing', 'tail', 'other'):
    g = agg.get(rg)
    if not g or len(g[2]) < 20: continue
    dens = math.sqrt(g[1] / g[0]); c = g[2]; r1 = max(1, round(0.02 * dens)); r2 = max(r1 + 1, round(0.08 * dens))
    m = sum(L[y][x] for x, y in c) / len(c) or 1e-6
    fine = sum(abs(L[y][x] - box_at(x, y, r1)) for x, y in c) / len(c) / m
    mid = sum(abs(box_at(x, y, r1) - box_at(x, y, r2)) for x, y in c) / len(c) / m
    print('  %-9s density %4.0f tx/m  surface %3.0f%%  brightness %.2f  fine %.2f  mid %.2f  (%.2f)' % (rg, dens, 100 * g[0] / tot, m, fine, mid, fine + mid))
