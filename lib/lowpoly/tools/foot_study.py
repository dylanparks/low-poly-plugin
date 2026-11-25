"""How a model's feet are built as geometry: vertices, triangles, toe or claw tips, ground contacts, bones, and a close-up of
one foot with its edges drawn. Standard library only; reads the viewer's files.
Usage: python -I foot_study.py <model.gltf> <out dir> <animal id> [foot zone, fraction of height, or - for the rig (default)] [clip phase for the pose]
A foot is a connected piece of the mesh below the foot zone that reaches the ground (its lowest vertex within 3% of the
height of the lowest point). When the rig shows the limbs (lowpoly/rig_parts.py), only skin carried by the feet's bones (each
limb's ankle bone and the bones below it) is in the zone: a sprawling knee, a tail lying on the ground or a bird's feather
cuff low enough to fall in it is left out, and counted. Without limbs in the rig, all the skin in the zone. Per foot it reports:
  - unique vertices and triangles, and the vertices' share of the model;
  - the footprint (front to back, side to side) and the foot zone's height, as fractions of the animal's height;
  - tips: vertices that stick out of the foot's outline, measured forward and outward from the foot's centre more than all of
    their neighbours do (toes and claws). Sharp tips are those whose neighbours sit at least 1.6 times closer to the centre;
  - contacts: vertices within 1% of the height of the foot's lowest point (a flat sole has 3 or more);
  - bones: how many bones weight the foot's vertices.
Writes <id>_foot.png: the frontmost foot from the front and three-quarter and the side, texture flat-lit with the edges
drawn."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, struct, sys, zlib

D, OUTD, AID = sys.argv[1:4]
ZONE = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != '-' else 0.12
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
texfile = (g['texpath']() or '')
tex = read_png(texfile) if A['tex'] and A['tex'][0] and os.path.exists(texfile) else None
P = [v[0] for v in V]
key = lambda p: (round(p[0], 4), round(p[1], 4), round(p[2], 4))
uid = {}
for i, p in enumerate(P): uid.setdefault(key(p), len(uid))
U = [None] * len(uid)
for i, p in enumerate(P): U[uid[key(p)]] = p
TU = [tuple(uid[key(P[i])] for i in t) for t in T]
ys = [p[1] for p in U]; lo, H = min(ys), max(ys) - min(ys)
nbr = {i: set() for i in range(len(U))}
for a, b, c in TU:
    nbr[a] |= {b, c}; nbr[b] |= {a, c}; nbr[c] |= {a, b}
from lowpoly import rig_parts
_fc = rig_parts.foot_corners(rig_parts.parts(A, V))
zone = {i for i, p in enumerate(U) if p[1] < lo + ZONE * H}
FOOT_RULE = ''
if _fc and all(_fc):                     # the feet's skin only: a vertex is the foot's if a foot bone weights it most
    _fu = {uid[key(P[c])] for fs in _fc for c in fs}
    _limb_of = {uid[key(P[c])]: n for n, fs in enumerate(_fc) for c in fs}
    _out = zone - _fu; zone &= _fu
    FOOT_RULE = ", the feet's bones only" + (' (%d other vertices in the zone left out)' % len(_out) if _out else '')
feet, seen = [], set()
for s0 in zone:
    if s0 in seen: continue
    comp, st = set(), [s0]; seen.add(s0)
    while st:
        q = st.pop(); comp.add(q)
        for r in nbr[q]:
            if r in zone and r not in seen: seen.add(r); st.append(r)
    if min(U[i][1] for i in comp) < lo + 0.03 * H and len(comp) >= 3: feet.append(comp)
# separate closed parts sunk into a foot (toes and claws built like teeth) join the foot they touch: within 4% of the height
merged = True
while merged:
    merged = False
    feet.sort(key=len, reverse=True)
    for i_ in range(len(feet)):
        for j_ in range(len(feet) - 1, i_, -1):
            _li = {_limb_of[x] for x in feet[i_] if x in _limb_of} if FOOT_RULE else set()
            _lj = {_limb_of[x] for x in feet[j_] if x in _limb_of} if FOOT_RULE else set()
            if _li and _lj and not (_li & _lj): continue          # the rig says these are two limbs' feet: never one foot
            if min(math.dist(U[a_], U[b_]) for a_ in feet[i_] for b_ in feet[j_]) < 0.04 * H:
                feet[i_] = feet[i_] | feet.pop(j_); merged = True
        if merged: break
bones_of = {}
for i, p in enumerate(P):
    bones_of.setdefault(uid[key(p)], set()).update(b for b, w in V[i][1] if w > 0.05)
zs = [p[2] for p in U]
print('== %s (%s): height %.2f m, %d unique vertices, %d feet found below %.0f%% of the height%s'
      % (A['name'], AID, H, len(U), len(feet), ZONE * 100, FOOT_RULE))
feet.sort(key=lambda f: -max(U[i][2] for i in f))
for n, f in enumerate(feet):
    tris = [t for t in TU if all(i in f for i in t)]
    fx = [U[i][0] for i in f]; fz = [U[i][2] for i in f]; fy = [U[i][1] for i in f]
    c = (sum(fx) / len(f), min(fy), sum(fz) / len(f))
    # tips: vertices further out (forward and to the sides, in the ground plane) from the centre than all their neighbours
    def reach(i): p = U[i]; return math.hypot(p[0] - c[0], max(0.0, p[2] - c[2]) * 1.0 + min(0.0, p[2] - c[2]) * 0.6)
    tips = [i for i in f if U[i][1] < c[1] + 0.6 * (max(fy) - c[1]) and all(reach(i) > reach(j) for j in nbr[i] if j in f)]
    sharp = [i for i in tips if all(reach(j) * 1.6 < reach(i) for j in nbr[i] if j in f)]
    contacts = [i for i in f if U[i][1] < min(fy) + 0.01 * H]
    bones = set().union(*(bones_of[i] for i in f))
    # splay: the foot's width at the ground against its width at the top of the zone (the ankle); reach: how far the sole runs
    # forward of the ankle's front, against the ankle's depth
    top = [i for i in f if U[i][1] > max(fy) - 0.25 * (max(fy) - min(fy))]; bot = [i for i in f if U[i][1] < min(fy) + 0.15 * (max(fy) - min(fy))]
    w_top = (max(U[i][0] for i in top) - min(U[i][0] for i in top)) or 1e-6; w_bot = max(U[i][0] for i in bot) - min(U[i][0] for i in bot)
    d_top = (max(U[i][2] for i in top) - min(U[i][2] for i in top)) or 1e-6
    reach_f = (max(U[i][2] for i in bot) - max(U[i][2] for i in top)) / d_top
    print('   foot %d: %3d vertices (%.0f%% of the model), %3d triangles | footprint %.2f x %.2f of height, zone %.2f | splay %.1fx | toes reach %.1f ankle depths forward | tips %d (sharp %d) | ground contacts %d | bones %d'
          % (n, len(f), 100 * len(f) / len(U), len(tris), (max(fz) - min(fz)) / H, (max(fx) - min(fx)) / H, (max(fy) - min(fy)) / H,
             w_bot / w_top, reach_f, len(tips), len(sharp), len(contacts), len(bones)))
# ---------------------------------------------------------------- a close-up of the frontmost foot, with its edges
if feet:
    f = feet[0]
    sel = [t for t, tu in zip(T, TU) if all(i in f for i in tu)]
    pts = [P[i] for t in sel for i in t]
    cen = [(min(q[k] for q in pts) + max(q[k] for q in pts)) / 2 for k in range(3)]
    span = max(max(q[k] for q in pts) - min(q[k] for q in pts) for k in range(3)) or 1
    S = 260; sc = (S - 20) / span
    c40, s40 = math.cos(math.radians(40)), math.sin(math.radians(40))
    VIEWS = [lambda p: (p[0] - cen[0], -(p[1] - cen[1]), p[2] - cen[2]),
             lambda p: ((p[0] - cen[0]) * c40 + (p[2] - cen[2]) * s40, -(p[1] - cen[1]), -(p[0] - cen[0]) * s40 + (p[2] - cen[2]) * c40),
             lambda p: ((p[2] - cen[2]), -(p[1] - cen[1]), -(p[0] - cen[0]) if cen[0] < 0 else (p[0] - cen[0]))]
    W = S * 3; img = [[(40, 42, 48)] * W for _ in range(S)]
    for vi, proj in enumerate(VIEWS):
        zb = [[-1e9] * S for _ in range(S)]; edge_px = []
        for t in sel:
            q = [proj(P[i]) for i in t]
            pts2 = [(S / 2 + x * sc, S / 2 + y * sc, d) for x, y, d in q]
            (x0, y0, _), (x1, y1, _), (x2, y2, _) = pts2
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-9: continue
            e1 = [P[t[1]][k] - P[t[0]][k] for k in range(3)]; e2 = [P[t[2]][k] - P[t[0]][k] for k in range(3)]
            nn = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
            ln = math.sqrt(sum(v * v for v in nn)) or 1
            lit = 0.45 + 0.55 * abs(nn[1] / ln * 0.6 + nn[2] / ln * 0.5 + nn[0] / ln * 0.4)
            for py in range(max(0, int(min(y0, y1, y2))), min(S - 1, int(max(y0, y1, y2)) + 1)):
                for px in range(max(0, int(min(x0, x1, x2))), min(S - 1, int(max(x0, x1, x2)) + 1)):
                    xx, yy = px + 0.5, py + 0.5
                    a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / den; b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / den; cc = 1 - a - b
                    if min(a, b, cc) < -1e-4: continue
                    dep = a * pts2[0][2] + b * pts2[1][2] + cc * pts2[2][2]
                    if dep <= zb[py][px]: continue
                    zb[py][px] = dep
                    if tex:
                        tw, th, tt = tex; u = a * uvs[t[0]][0] + b * uvs[t[1]][0] + cc * uvs[t[2]][0]; v = a * uvs[t[0]][1] + b * uvs[t[1]][1] + cc * uvs[t[2]][1]
                        col = tt[int(v * th) % th][int(u * tw) % tw][:3]
                    else: col = (170, 170, 170)
                    on_edge = min(a, b, cc) < 0.035
                    img[py][vi * S + px] = (255, 200, 60) if on_edge else tuple(min(255, int(ch * lit)) for ch in col)
    raw = b''.join(b'\x00' + bytes(v for col in row for v in col) for row in img)
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(os.path.join(OUTD, AID + '_foot.png'), 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W, S, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 9)) + ch(b'IEND', b''))
