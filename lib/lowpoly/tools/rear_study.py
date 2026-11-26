"""The hindquarters seen from behind: the outline the rear and 3/4-rear game camera reads, which no side or front measure sees.
Standard library only; reads glTF.
Usage: python -I rear_study.py <model.gltf|.glb> [clip phase: clip name and 0..1, to measure a posed frame]

The hindquarters are the triangles carried mostly by the hind limbs (lowpoly/rig_parts.py: the limbs whose root is furthest
back) and the body skin round their roots (behind the front of the hind leg's hole). Their silhouette, looked at straight from
behind (x across, y up), is rasterised into rows of 0.5% of the height, and each side's outline is read row by row.
It reports:
  width     the hips' half-width (the body's widest at the rump, legs left out) and the thighs' (the hind legs' widest),
            and their ratio: over 1 the thighs stick out past the hips as saddlebags.
  bulge     the most the outline steps out and back again over a short run: a lobe that sticks out sideways, as a % of the
            height (the outline's largest outward excursion from a straight line between the rows above and below it).
  notch     the deepest inward dent in the outline between two wider parts (a waist between the thigh and the body, or
            between the thigh and the shin), as a % of the height.
  corner    the sharpest turn of the outline, in degrees, from a smoothed outline (a facet sticking out reads as a corner).
Why: the haunch is one convex mass (the gluteals and the biceps femoris over the hip joint and the thigh, down to the
stifle), and below it the leg narrows evenly to the hock. A convex mass has no waist and no corner, so the outline from
behind runs down from the hip as one column: no lobe stepping out past it, no dent between the thigh and the body. The
limits allow for low-poly facets only (lowpoly-animals/references/limbs.md, "The haunch from behind"). Check the widths
against the species' own rear and 3/4-rear references with lp overlay where a dead-rear one exists."""
import sys as _sys  # _usage_guard
if __name__ == '__main__' and (len(_sys.argv) < 2 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, math, os, struct, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lowpoly import gltf_io, rig_parts  # noqa: E402

A, _ = gltf_io.read_gltf(sys.argv[1])
C, T = [], []
for s in A['subs']:
    raw = base64.b64decode(s['v']); n = len(raw) // 64; base = len(C)
    C += [struct.unpack_from('<16f', raw, k * 64) for k in range(n)]
    ib = base64.b64decode(s['i']); ix = struct.unpack('<%dH' % (len(ib) // 2), ib)
    T += [(base + ix[k], base + ix[k + 1], base + ix[k + 2]) for k in range(0, len(ix) - 2, 3)]
P = [c[:3] for c in C]
V = [((c[0], c[1], c[2]), [(int(round(c[12 + j])), c[8 + j]) for j in range(4) if c[8 + j] > 1e-4]) for c in C]
R = rig_parts.parts(A, V)
names, nb = A['bones'], len(A['bones'])

# ---- an optional posed frame: skin the corners at a clip's phase
if len(sys.argv) > 3:
    from lowpoly.spring_bake import decode_clip, sample, qmul, qrot
    clip, ph = sys.argv[2], float(sys.argv[3]); keys = decode_clip(A['anims'][clip], nb); par = A['parent']
    r0 = [tuple(A['rest'][i * 7:i * 7 + 4]) for i in range(nb)]; p0 = [tuple(A['rest'][i * 7 + 4:i * 7 + 7]) for i in range(nb)]
    rr = [sample(keys[i][0], ph, 4) or r0[i] for i in range(nb)]; pp = [sample(keys[i][1], ph, 3) or p0[i] for i in range(nb)]
    Wd = [None] * nb
    for i in range(nb):
        pi = par[i]
        if pi is None or pi < 0 or pi == i: Wd[i] = (rr[i], pp[i])
        else:
            pq, pv = Wd[pi]; Wd[i] = (qmul(pq, rr[i]), tuple(a + b for a, b in zip(pv, qrot(pq, pp[i]))))
    inv = [(tuple(A['inv'][i * 7:i * 7 + 4]), tuple(A['inv'][i * 7 + 4:i * 7 + 7])) for i in range(nb)]
    def skin(k):
        out = [0.0, 0.0, 0.0]
        for b, w in V[k][1]:
            iq, ip = inv[b]; q = tuple(a + c for a, c in zip(qrot(iq, P[k]), ip))
            wq, wp = Wd[b]; q = tuple(a + c for a, c in zip(qrot(wq, q), wp)); out = [o + w * c for o, c in zip(out, q)]
        return tuple(out)
    P = [skin(k) for k in range(len(P))]

ys = [p[1] for p in P]; ymin, H = min(ys), (max(ys) - min(ys)) or 1.0
if not R['limbs']: print('== no limbs in the rig: nothing measured'); sys.exit(0)
# the hind limbs: the two whose root joint is furthest back (lowest z: the nose is toward +z)
J = rig_parts.joints(A)
limbs = sorted(R['limbs'], key=lambda l: J[l['root']][2])[:2]
hind = set().union(*(l['bones'] for l in limbs))
share = lambda k, bs: sum(w for b, w in V[k][1] if b in bs)
legv = [k for k in range(len(P)) if share(k, hind) >= 0.5]
z_front = max(P[k][2] for k in legv)                       # the front of the hind legs (their hole reaches past the knee)
z_back = min(P[k][2] for k in legv)
in_rear = lambda t: max(P[i][2] for i in t) <= z_front + 0.02 * H
tri_leg = lambda t: sum(share(i, hind) for i in t) / 3 >= 0.5
# the tail: bones named tail, left out (it hangs over the middle and is not the haunch's outline)
tail = {b for b in range(nb) if 'tail' in names[b].lower()}
tris = [t for t in T if in_rear(t) and max(share(i, tail) for i in t) < 0.5]     # no triangle touching the tail's root: it sways

# ---- rasterise the rear view (x across, y up) into rows; per row the outermost covered x on each side
ROW = 0.005 * H
rows = defaultdict(lambda: [0.0, 0.0])                      # row -> [left extent (x > 0), right extent (as a positive number)]
rows_body = defaultdict(lambda: [0.0, 0.0])
for t in tris:
    pts = [(P[i][0], P[i][1]) for i in t]
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    for r in range(int((y0 - ymin) / ROW), int((y1 - ymin) / ROW) + 1):
        yc = ymin + (r + 0.5) * ROW; xs = []
        for a, b in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
            if (a[1] <= yc <= b[1]) or (b[1] <= yc <= a[1]):
                xs.append(a[0] if b[1] == a[1] else a[0] + (yc - a[1]) / (b[1] - a[1]) * (b[0] - a[0]))
        if not xs: continue
        for x in xs:
            for tgt in ((rows,) if tri_leg(t) else (rows, rows_body)):
                if x > 0: tgt[r][0] = max(tgt[r][0], x)
                else: tgt[r][1] = max(tgt[r][1], -x)

leg_rows = defaultdict(lambda: [0.0, 0.0])
for t in tris:
    if not tri_leg(t): continue
    for i in t:
        r = int((P[i][1] - ymin) / ROW); s_ = 0 if P[i][0] > 0 else 1; leg_rows[r][s_] = max(leg_rows[r][s_], abs(P[i][0]))
hip = max(max(v) for v in rows_body.values()) if rows_body else 0.0
thigh = max(max(v) for v in leg_rows.values()) if leg_rows else 0.0


# the haunch band: from the hind legs' ankle (hock) joint up to 10% of the height above the hip joints. The paws (their toes
# are notches by design) and the back's top line are judged elsewhere
y_lo = max(J[l['ankle']][1] for l in limbs); y_hi = max(J[l['root']][1] for l in limbs) + 0.10 * H


def outline(side):
    rs = sorted(r for r in rows if rows[r][side] > 0 and y_lo <= ymin + (r + 0.5) * ROW <= y_hi)
    ol = [(ymin + (r + 0.5) * ROW, rows[r][side]) for r in rs]
    # trim end rows that only clip a sliver (the spine's peak at the band's top): a row under 60% of its neighbour's width
    while len(ol) > 2 and ol[-1][1] < 0.6 * ol[-2][1]: ol.pop()
    while len(ol) > 2 and ol[0][1] < 0.6 * ol[1][1]: ol.pop(0)
    return ol


def measures(ol):
    """bulge: the largest outward excursion of a point from the chord between the outline 6% of the height above and below;
    notch: the deepest inward excursion from that chord; corner: the sharpest turn of the outline smoothed over 3 rows"""
    span = max(1, int(0.06 * H / ROW)); bulge = notch = 0.0; at_b = at_n = None
    for k in range(span, len(ol) - span):
        (ya, xa), (y, x), (yb, xb) = ol[k - span], ol[k], ol[k + span]
        chord = xa + (xb - xa) * (y - ya) / ((yb - ya) or 1e-9)
        if x - chord > bulge: bulge, at_b = x - chord, y
        if chord - x > notch and x < min(max(p[1] for p in ol[:k]), max(p[1] for p in ol[k + 1:])): notch, at_n = chord - x, y
    sm = [(ol[k][0], sum(p[1] for p in ol[max(0, k - 1):k + 2]) / len(ol[max(0, k - 1):k + 2])) for k in range(len(ol))]
    worst, at_c = 0.0, None; st = max(1, int(0.02 * H / ROW))
    for k in range(st, len(sm) - st):
        a = math.atan2(sm[k][1] - sm[k - st][1], sm[k][0] - sm[k - st][0])
        b = math.atan2(sm[k + st][1] - sm[k][1], sm[k + st][0] - sm[k][0])
        turn = abs(math.degrees((b - a + math.pi) % (2 * math.pi) - math.pi))
        if turn > worst: worst, at_c = turn, sm[k][0]
    return bulge, at_b, notch, at_n, worst, at_c


name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
print('== %s: rear view of the hindquarters (%d triangles behind z %.3f; hind limbs %s; height %.2f m)%s'
      % (name, len(tris), z_front, ', '.join(names[l['root']] for l in limbs), H, ' at %s %.2f' % (sys.argv[2], float(sys.argv[3])) if len(sys.argv) > 3 else ''))
print('   width: hips %.3f m, thighs %.3f m, thighs over hips %.2f | haunch band y %.2f..%.2f m' % (hip, thigh, thigh / hip if hip else 0, y_lo, y_hi))
res = [measures(outline(s)) for s in (0, 1)]
for s, (bulge, at_b, notch, at_n, corner, at_c) in zip(('left', 'right'), res):
    print('   %-5s outline: bulge %.1f%% of the height%s | notch %.1f%%%s | sharpest turn %.0f deg%s'
          % (s, 100 * bulge / H, ' at y %.2f' % at_b if at_b else '', 100 * notch / H, ' at y %.2f' % at_n if at_n else '',
             corner, ' at y %.2f' % at_c if at_c else ''))
print('   rear: thighs over hips %.2f | bulge %.1f%% | notch %.1f%% | corner %.0f deg'
      % (thigh / hip if hip else 0, 100 * max(r[0] for r in res) / H, 100 * max(r[2] for r in res) / H, max(r[4] for r in res)))
