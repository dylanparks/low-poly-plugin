"""How a nose and muzzle are painted, measured on a textured head render (the output of head_textured.py: flat-lit, so the pixels
are the texture's colours, laid out the same way for every model whatever its UVs). Standard library only.
Usage: python -I nose_study.py <head_textured png> <name> [nose darkness threshold=0.55]   (or a viewer folder and one or more animal ids, to compare them)
Front view (left panel): the nose is the largest dark blob in the lower middle of the face (darker than the threshold times the
face's median brightness). Reports its width against the muzzle's, its brightness (mean, the darkest 10% = the nostrils, the
brightest 5% = the lit top or rim) and spread; the ring of muzzle just round it; and the face between the eyes, for the step from
face to muzzle. Side view (right panel): brightness profiles down the muzzle at three places between the nose tip and the eye,
for the bridge, the side, the mouth line (the darkest run in the lower half) and the chin.
Limit: the nose is found by darkness, so a lit band across its top that is brighter than the threshold is left out of it; judge
that band in the render."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import math, os, struct, sys, zlib

PNG, NAME = sys.argv[1], sys.argv[2]
TH = float(sys.argv[3]) if len(sys.argv) > 3 else 0.55
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
w, h, img = read_png(PNG)
BG = (40, 42, 48)
px = lambda x, y: tuple(img[y][x][:3])
lum = lambda p: (0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]) / 255
S = 300                                   # panel size
med = lambda v: sorted(v)[len(v) // 2] if v else 0
pct = lambda v, q: sorted(v)[min(len(v) - 1, int(q * len(v)))] if v else 0


def panel(k):
    return {(x - S * k, y): px(x, y) for x in range(S * k, S * (k + 1)) for y in range(S) if px(x, y) != BG}


# ---- front
F = panel(0)
ys = [p[1] for p in F]; ytop, ybot = min(ys), max(ys)
xs = [p[0] for p in F]; xmid = (min(xs) + max(xs)) / 2
face = [lum(c) for (x, y), c in F.items()]
m_face = med(face)
cand = {(x, y) for (x, y), c in F.items() if y > ytop + 0.55 * (ybot - ytop) and abs(x - xmid) < 0.22 * (max(xs) - min(xs))
        and lum(c) < TH * m_face}
# the largest connected dark blob, grown to the dark pixels round it
best = set()
seen = set()
for s0 in cand:
    if s0 in seen: continue
    comp, st = set(), [s0]; seen.add(s0)
    while st:
        q = st.pop(); comp.add(q)
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            r = (q[0] + d[0], q[1] + d[1])
            if r in cand and r not in seen: seen.add(r); st.append(r)
    if len(comp) > len(best): best = comp
print('== %s' % NAME)
if not best:
    print('   front: no dark nose blob (the nose is not darker than %.2f x the face): judge it by eye' % TH)
else:
    nb = best
    # fill holes: everything inside the blob's row spans (lit tops and rims inside the nose)
    rows = {}
    for x, y in nb: rows.setdefault(y, []).append(x)
    nose = {(x, y) for y, xx in rows.items() for x in range(min(xx), max(xx) + 1) if (x, y) in F}
    L = [lum(F[p]) for p in nose]; m = sum(L) / len(L); sd = math.sqrt(sum((v - m) ** 2 for v in L) / len(L))
    nx = [p[0] for p in nose]; ny = [p[1] for p in nose]
    yc = (min(ny) + max(ny)) // 2
    muzzle_w = max(x for (x, y) in F if y == yc) - min(x for (x, y) in F if y == yc) + 1
    ring = set()
    for x, y in nose:
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                q = (x + dx, y + dy)
                if q in F and q not in nose and dx * dx + dy * dy <= 36: ring.add(q)
    Lr = [lum(F[p]) for p in ring]
    # the face between the eyes: the middle fifth of the width, 30-45% down the head
    fz = [lum(c) for (x, y), c in F.items() if abs(x - xmid) < 0.10 * (max(xs) - min(xs)) and ytop + 0.30 * (ybot - ytop) < y < ytop + 0.45 * (ybot - ytop)]
    print('   front: nose %.2f of the muzzle width; nose brightness mean %.2f sd %.2f, nostrils (darkest 10%%) %.2f, lit top (brightest 5%%) %.2f'
          % ((max(nx) - min(nx) + 1) / muzzle_w, m, sd, pct(L, 0.10), pct(L, 0.95)))
    print('          muzzle ring round the nose %.2f (step to the nose %+.2f); face between the eyes %.2f (muzzle - face %+.2f)'
          % (sum(Lr) / len(Lr), m - sum(Lr) / len(Lr), med(fz), sum(Lr) / len(Lr) - med(fz)))
# the muzzle's painted fine detail, head-on: how far each pixel stands from its 3x3 neighbourhood's mean, over the mean, in
# the lower middle of the face (62-92% down, the middle half of the width). Fur strokes, skin grain and creases raise it; a
# face painted only as smooth gradients reads cartoonish (a rebuilt cat head dropped its hair strokes: 0.019 against 0.036)
_mz = [(x, y) for (x, y) in F if ytop + 0.62 * (ybot - ytop) < y < ytop + 0.92 * (ybot - ytop) and abs(x - xmid) < 0.25 * (max(xs) - min(xs))]
_d = []
for x, y in _mz:
    nb_ = [lum(F[(x + i, y + j)]) for i in (-1, 0, 1) for j in (-1, 0, 1) if (x + i, y + j) in F]
    if len(nb_) == 9: _d.append((lum(F[(x, y)]), abs(lum(F[(x, y)]) - sum(nb_) / 9)))
if _d:
    print('   front: muzzle fine detail %.3f (the pixels\' step from their 3x3 mean over the muzzle\'s mean brightness)'
          % ((sum(d for _, d in _d) / len(_d)) / max(1e-6, sum(v for v, _ in _d) / len(_d))))
# ---- side
Sd = panel(2)


def head_run(x):
    """the column's largest unbroken run of pixels: the head itself, without a horn, antler or ear that crosses the column
    apart from it (a unicorn's horn juts past the muzzle, and its pixels were read as the bridge)"""
    ys_ = sorted(y for (xx, y) in Sd if xx == x)
    runs, cur = [], []
    for y in ys_:
        if cur and y != cur[-1] + 1: runs.append(cur); cur = []
        cur.append(y)
    if cur: runs.append(cur)
    return max(runs, key=len) if runs else []


RUN = {x: head_run(x) for x in set(p[0] for p in Sd)}
x0 = max(RUN, key=lambda x: len(RUN[x]))                  # the deepest column, inside the head
tip = x0                                                  # walk forward while each column's run overlaps the last one:
while tip + 1 in RUN and RUN[tip + 1] and RUN[tip] and RUN[tip + 1][0] <= RUN[tip][-1] and RUN[tip + 1][-1] >= RUN[tip][0]:
    tip += 1                                              # a horn past the muzzle floats above it and stops the walk
back = min(RUN); hl = tip - back


def eye_in_band(f):
    """True when the bridge band (the top quarter of the column) at f back from the tip holds an eye pixel: one far darker
    than the column (a pupil eye's lid and pupil) or far brighter (a glow)"""
    x = int(tip - f * hl); c_ = [lum(Sd[(x, y)]) for y in RUN.get(x, []) if (x, y) in Sd]
    if len(c_) < 8: return False
    m_ = sorted(c_)[len(c_) // 2]
    return any(v < 0.30 * m_ or (v > 0.80 and v > 2.0 * m_) for v in c_[:max(1, len(c_) // 4)])


# A station whose bridge band takes in the eye moves forward until it does not (a big eye reached the 35% station and was
# read as a dark bridge on the red fox v2); the others stay where they are.
for frac in (0.10, 0.22, 0.35):
    f0 = frac
    while eye_in_band(frac) and frac > 0.06: frac = round(frac - 0.01, 2)
    if frac != f0: print('   side: the bridge band at %d%% held the eye: measured at %d%% instead' % (round(100 * f0), round(100 * frac)))
    x = int(tip - frac * hl)
    keep = set(RUN.get(x, []))
    col = sorted((y, lum(c)) for (xx, y), c in Sd.items() if xx == x and y in keep)
    if len(col) < 8: continue
    y0, y1 = col[0][0], col[-1][0]; n = len(col)
    top = [v for _, v in col[:max(1, n // 4)]]; mid = [v for _, v in col[n // 4:n // 2]]
    low = col[n // 2:]
    # the mouth line: the darkest 3-pixel run in the lower half, against the pixels 3-6 above and below it
    best_ = None
    for i in range(1, len(low) - 1):
        v = (low[i - 1][1] + low[i][1] + low[i + 1][1]) / 3
        if best_ is None or v < best_[0]: best_ = (v, i)
    v, i = best_
    above = [q for _, q in low[max(0, i - 6):max(0, i - 2)]]; below = [q for _, q in low[i + 3:i + 7]]
    chin = [q for _, q in low[i + 3:]]
    print('   side, %2d%% back from the tip: bridge %.2f | side %.2f | mouth line %.2f at %d%% down (lip above %.2f, below %.2f) | chin %.2f'
          % (frac * 100, sum(top) / len(top), sum(mid) / len(mid), v, round(100 * (low[i][0] - y0) / max(1, y1 - y0)),
             sum(above) / len(above) if above else -1, sum(below) / len(below) if below else -1, sum(chin) / len(chin) if chin else -1))
