"""How much a model's texture paints its 3D form: light from above, shadow in the creases (the leg-body junction, behind the
elbow, under the jaw), anatomy shapes and fur strokes. Standard library only; reads the viewer's files.
Usage: python -I body_study.py <model.gltf> <out dir> <animal id> [rays per vertex=48]

1. Bands (a side-view render of the texture alone, unlit, nose at the left, the model's length 720 px): the torso's brightness
   split into large shapes (blurred over 5% of the length: painted light and colour zones), mid shapes (1-5%: muscles, ribs,
   creases, folds) and fine detail (under 1%: fur strokes), as standard deviations. Plus the fur's direction: the coherence of
   the fine detail's gradients (0 = no direction, 1 = all strokes parallel) and their mean angle (0 = along the body).
   Writes <id>_side.png.
2. Paint against the geometry (per vertex): how enclosed each vertex is (the share of 48 rays over its normal's hemisphere that
   hit the mesh within 30% of the animal's height: creases score high) and which way it faces. Each is compared with its
   neighbours within 12% of the height, so large colour zones (a white belly, spots) cancel out. Reports the correlation of the
   painted brightness with enclosure (negative = creases painted darker) and with facing up (positive = tops painted lighter),
   and how much darker than its neighbours the most enclosed tenth of vertices is painted."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, random, struct, sys, zlib

D, OUTD, AID = sys.argv[1:4]
NR = int(sys.argv[4]) if len(sys.argv) > 4 else 48
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; argv = sys.argv; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
sys.argv = argv
A, V, T = g['A'], g['V'], g['T']
uvs = []
for s in A['subs']:
    raw = base64.b64decode(s['v'])
    for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
tw, th, tex = read_png(g['texpath']())
P = [v[0] for v in V]
lum = lambda c: (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255
texel = lambda u, v: tex[min(th - 1, max(0, int(v * th)))][min(tw - 1, max(0, int(u * tw)))]
ys = [p[1] for p in P]; zs = [p[2] for p in P]
lo, H = min(ys), max(ys) - min(ys); zmin, zmax = min(zs), max(zs); LEN = zmax - zmin
# the torso: between the rearmost and the frontmost foot (vertices below 6% of the height), above 45% of the height
feet = [p[2] for p in P if p[1] < lo + 0.06 * H]
TZ0, TZ1 = (min(feet), max(feet)) if feet and max(feet) - min(feet) > 0.2 * LEN else (zmin + 0.2 * LEN, zmax - 0.2 * LEN)   # legless: the middle

# ---------------------------------------------------------------- 1. side render of the texture alone
SCL = 720 / LEN; WD = 760; HT = int(H * SCL) + 40
img = [[None] * WD for _ in range(HT)]; zb = [[-1e9] * WD for _ in range(HT)]; region = [[False] * WD for _ in range(HT)]
proj = lambda p: (20 + (zmax - p[2]) * SCL, 20 + (lo + H - p[1]) * SCL, p[0])
for t in T:
    pts = [proj(P[i]) for i in t]
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = pts
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-9: continue
    for py in range(max(0, int(min(y0, y1, y2))), min(HT - 1, int(max(y0, y1, y2)) + 1)):
        for px in range(max(0, int(min(x0, x1, x2))), min(WD - 1, int(max(x0, x1, x2)) + 1)):
            xx, yy = px + 0.5, py + 0.5
            a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / den; b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / den; c = 1 - a - b
            if min(a, b, c) < -1e-4: continue
            dep = a * pts[0][2] + b * pts[1][2] + c * pts[2][2]
            if dep <= zb[py][px]: continue
            zb[py][px] = dep
            u = a * uvs[t[0]][0] + b * uvs[t[1]][0] + c * uvs[t[2]][0]; v = a * uvs[t[0]][1] + b * uvs[t[1]][1] + c * uvs[t[2]][1]
            img[py][px] = texel(u, v)
            z = zmax - (xx - 20) / SCL; y = lo + H - (yy - 20) / SCL
            region[py][px] = TZ0 + 0.05 * (TZ1 - TZ0) < z < TZ1 - 0.05 * (TZ1 - TZ0) and y > lo + 0.45 * H


def box_blur(L, r):
    """mean over a (2r+1)^2 window, of the covered pixels only (the silhouette's edge does not bleed in)"""
    hgt, wid = len(L), len(L[0]); out = [[None] * wid for _ in range(hgt)]
    S = [[0.0] * (wid + 1) for _ in range(hgt + 1)]; N = [[0] * (wid + 1) for _ in range(hgt + 1)]
    for y in range(hgt):
        for x in range(wid):
            v = L[y][x]
            S[y + 1][x + 1] = S[y][x + 1] + S[y + 1][x] - S[y][x] + (v if v is not None else 0.0)
            N[y + 1][x + 1] = N[y][x + 1] + N[y + 1][x] - N[y][x] + (1 if v is not None else 0)
    for y in range(hgt):
        for x in range(wid):
            if L[y][x] is None: continue
            ya, yb, xa, xb = max(0, y - r), min(hgt, y + r + 1), max(0, x - r), min(wid, x + r + 1)
            n = N[yb][xb] - N[ya][xb] - N[yb][xa] + N[ya][xa]
            out[y][x] = (S[yb][xb] - S[ya][xb] - S[yb][xa] + S[ya][xa]) / n
    return out


Lm = [[None if c is None else lum(c) for c in row] for row in img]
r1, r2 = max(1, int(0.005 * 720)), int(0.025 * 720)            # half-widths: 1% and 5% of the length
B1, B2 = box_blur(Lm, r1), box_blur(Lm, r2)
pts_ = [(y, x) for y in range(HT) for x in range(WD) if region[y][x]]
def sd(vals): m = sum(vals) / len(vals); return math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))
fine = [Lm[y][x] - B1[y][x] for y, x in pts_]; mid = [B1[y][x] - B2[y][x] for y, x in pts_]; large = [B2[y][x] for y, x in pts_]
# stroke direction: the structure tensor of the fine detail's gradient
jxx = jyy = jxy = 0.0
for y, x in pts_:
    if 0 < y < HT - 1 and 0 < x < WD - 1 and None not in (Lm[y][x + 1], Lm[y][x - 1], Lm[y + 1][x], Lm[y - 1][x]):
        gx = (Lm[y][x + 1] - B1[y][x + 1]) - (Lm[y][x - 1] - B1[y][x - 1]); gy = (Lm[y + 1][x] - B1[y + 1][x]) - (Lm[y - 1][x] - B1[y - 1][x])
        jxx += gx * gx; jyy += gy * gy; jxy += gx * gy
coh = math.sqrt((jxx - jyy) ** 2 + 4 * jxy * jxy) / (jxx + jyy) if jxx + jyy else 0
grad_ang = 0.5 * math.degrees(math.atan2(2 * jxy, jxx - jyy))      # the dominant gradient; strokes run across it
stroke_ang = (grad_ang + 90 + 90) % 180 - 90
print('== %s (%s): %d torso pixels in the side render' % (A['name'], AID, len(pts_)))
print('   bands (sd of brightness): large %.3f | mid %.3f | fine %.3f   (torso mean %.2f)' % (sd(large), sd(mid), sd(fine), sum(large) / len(large)))
# local coherence (windows of 5% of the length): high locally but low overall = strokes that follow a flow over the form
WIN = int(0.05 * 720); loc = []
for wy in range(0, HT, WIN):
    for wx in range(0, WD, WIN):
        a_ = b_ = c_ = 0.0; n_ = 0
        for y in range(max(1, wy), min(HT - 1, wy + WIN)):
            for x in range(max(1, wx), min(WD - 1, wx + WIN)):
                if region[y][x] and None not in (Lm[y][x + 1], Lm[y][x - 1], Lm[y + 1][x], Lm[y - 1][x]):
                    gx = (Lm[y][x + 1] - B1[y][x + 1]) - (Lm[y][x - 1] - B1[y][x - 1]); gy = (Lm[y + 1][x] - B1[y + 1][x]) - (Lm[y - 1][x] - B1[y - 1][x])
                    a_ += gx * gx; b_ += gy * gy; c_ += gx * gy; n_ += 1
        if n_ > WIN * WIN // 2 and a_ + b_ > 0:
            loc.append((math.sqrt((a_ - b_) ** 2 + 4 * c_ * c_) / (a_ + b_), (0.5 * math.degrees(math.atan2(2 * c_, a_ - b_)) + 180) % 180 - 90))
lc = sum(c for c, _ in loc) / len(loc) if loc else 0
angs = sorted(a for _, a in loc)
print('   fur strokes: overall coherence %.2f at %+.0f deg (0 = along the body) | locally %.2f, local directions spread %+.0f..%+.0f deg (10-90%%)'
      % (coh, stroke_ang, lc, angs[len(angs) // 10] if angs else 0, angs[9 * len(angs) // 10] if angs else 0))
sm = sorted(mid)
print('   painted shapes (mid band): darks (5%%) %+.3f, lights (95%%) %+.3f' % (sm[len(sm) // 20], sm[19 * len(sm) // 20]))
# a picture of the mid band: grey 128 = no shape, darker = painted shadow, lighter = painted light (x4)
mrows = []
for y in range(HT):
    row = b'\x00'
    for x in range(WD):
        if Lm[y][x] is None: row += b'(*0'
        else:
            q = max(0, min(255, int(128 + 4 * 255 * (B1[y][x] - B2[y][x])))); row += bytes((q, q, q))
    mrows.append(row)

rows = []
for y in range(HT):
    row = b'\x00'
    for x in range(WD): row += bytes(img[y][x][:3]) if img[y][x] is not None else b'\x28\x2a\x30'
    rows.append(row)
ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(os.path.join(OUTD, AID + '_mid.png'), 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', WD, HT, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(b''.join(mrows), 9)) + ch(b'IEND', b''))
open(os.path.join(OUTD, AID + '_side.png'), 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', WD, HT, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(b''.join(rows), 9)) + ch(b'IEND', b''))

# ---------------------------------------------------------------- 2. paint against the geometry
key = lambda p: (round(p[0], 4), round(p[1], 4), round(p[2], 4))
pos, corners_of = {}, {}
for i, p in enumerate(P): corners_of.setdefault(key(p), []).append(i)
U = list(corners_of); Pu = [P[corners_of[k][0]] for k in U]
nrm = {k: [0.0, 0.0, 0.0] for k in U}
for t in T:
    a, b, c = (P[i] for i in t)
    e1 = [b[k] - a[k] for k in range(3)]; e2 = [c[k] - a[k] for k in range(3)]
    n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
    for i in t:
        for k in range(3): nrm[key(P[i])][k] += n[k]
tris = [[P[i] for i in t] for t in T]


def hit(o, d, maxd):
    for a, b, c in tris:
        e1 = [b[k] - a[k] for k in range(3)]; e2 = [c[k] - a[k] for k in range(3)]
        pv = [d[1] * e2[2] - d[2] * e2[1], d[2] * e2[0] - d[0] * e2[2], d[0] * e2[1] - d[1] * e2[0]]
        det = sum(e1[k] * pv[k] for k in range(3))
        if abs(det) < 1e-12: continue
        tv = [o[k] - a[k] for k in range(3)]; u = sum(tv[k] * pv[k] for k in range(3)) / det
        if u < 0 or u > 1: continue
        qv = [tv[1] * e1[2] - tv[2] * e1[1], tv[2] * e1[0] - tv[0] * e1[2], tv[0] * e1[1] - tv[1] * e1[0]]
        v = sum(d[k] * qv[k] for k in range(3)) / det
        if v < 0 or u + v > 1: continue
        tt = sum(e2[k] * qv[k] for k in range(3)) / det
        if 1e-5 * H < tt < maxd: return True
    return False


random.seed(5)
DIRS = []
for _ in range(NR):                                                     # cosine-weighted directions about +z, reused per vertex
    r1_, r2_ = random.random(), random.random(); r = math.sqrt(r1_); th_ = 2 * math.pi * r2_
    DIRS.append((r * math.cos(th_), r * math.sin(th_), math.sqrt(1 - r1_)))


def occl(p, n):
    if not any(n): n = [0.0, 1.0, 0.0]
    t1 = [1, 0, 0] if abs(n[0]) < 0.9 else [0, 1, 0]
    b1 = [n[1] * t1[2] - n[2] * t1[1], n[2] * t1[0] - n[0] * t1[2], n[0] * t1[1] - n[1] * t1[0]]; l = math.sqrt(sum(x * x for x in b1)); b1 = [x / l for x in b1]
    b2 = [n[1] * b1[2] - n[2] * b1[1], n[2] * b1[0] - n[0] * b1[2], n[0] * b1[1] - n[1] * b1[0]]
    o = [p[k] + n[k] * 0.002 * H for k in range(3)]
    return sum(hit(o, [dx * b1[k] + dy * b2[k] + dz * n[k] for k in range(3)], 0.30 * H) for dx, dy, dz in DIRS) / len(DIRS)


AO, NY, LV = [], [], []
for k, p in zip(U, Pu):
    n = nrm[k]; l = math.sqrt(sum(x * x for x in n))
    n = [x / l for x in n] if l > 1e-12 else [0.0, 1.0, 0.0]
    o = occl(p, n)
    if o > 0.6:                                                         # an inward normal (winding): take the other side
        o2 = occl(p, [-x for x in n])
        if o2 < o: o, n = o2, [-x for x in n]
    vals = []
    for ci in corners_of[k]:
        u0, v0 = uvs[ci]
        for du in (-1, 0, 1):
            for dv in (-1, 0, 1): vals.append(lum(texel(u0 + du / tw, v0 + dv / th)))
    AO.append(o); NY.append(n[1]); LV.append(sum(vals) / len(vals))
R = 0.12 * H
dL, dA, dN = [], [], []
for i, p in enumerate(Pu):
    nb = [j for j, q in enumerate(Pu) if j != i and math.dist(p, q) < R]
    if len(nb) < 4: continue
    dL.append(LV[i] - sum(LV[j] for j in nb) / len(nb)); dA.append(AO[i] - sum(AO[j] for j in nb) / len(nb)); dN.append(NY[i] - sum(NY[j] for j in nb) / len(nb))


def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else 0.0


order = sorted(range(len(dA)), key=lambda i: -dA[i]); top = order[:max(3, len(order) // 10)]
print('   paint against geometry (%d vertices): brightness vs enclosure r = %+.2f | vs facing up r = %+.2f | the most enclosed tenth is painted %+.3f vs its neighbours'
      % (len(dL), corr(dL, dA), corr(dL, dN), sum(dL[i] for i in top) / len(top)))
