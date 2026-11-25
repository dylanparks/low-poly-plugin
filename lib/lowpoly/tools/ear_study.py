"""Ears: how they are built, where they sit on the head, how they join it, and how they are textured.
Ear vertices are the ones weighted mostly to a bone named like 'ear'; animals without ear bones get geometric detection
(head vertices that rise above the skull's top line beside the midline, plus the ring of head vertices they stand on).
Writes 8x crops of each animal's ear texture with the ear triangles outlined (red = facing forward, blue = facing back).
Standard library only; only reads the viewer's files.
Usage: python -I ear_study.py <model.gltf> <out.png> <name>   (or a viewer folder and one or more animal ids, to compare them)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import re, base64, contextlib, io, math, os, struct, sys, zlib
from collections import Counter

D, OUT, IDS = sys.argv[1], sys.argv[2], sys.argv[3:]
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
panels = []
for aid in IDS:
    g = {}; sys.argv = ['x', D, aid]
    with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
    A, V, T, names = g['A'], g['V'], g['T'], g['names']
    uvs = []
    for s in A['subs']:
        raw = base64.b64decode(s['v'])
        for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
    w, h, img = read_png(g['texpath']())
    P = [v[0] for v in V]; ys = [p[1] for p in P]; zs = [p[2] for p in P]; lo, H = min(ys), max(ys) - min(ys)
    zmax, zmin = max(zs), min(zs)
    key = lambda i: tuple(round(c, 4) for c in P[i])
    from lowpoly import rig_parts                       # the head from the rig; the height rule when the rig shows none
    head_t = rig_parts.head_triangles(rig_parts.parts(A, V), T) or [t for t in T if all(P[i][2] > zmax - 0.25 * (zmax - zmin) and P[i][1] > lo + 0.45 * H for i in t)]
    head_v = {i for t in head_t for i in t}
    ear_bone = lambda i: sum(wt for b, wt in V[i][1] if re.search(r'(?<![a-z])ear', names[b].lower()))
    if any(ear_bone(i) > 0 for i in range(len(V))):
        how = 'ear bones: ' + ', '.join(sorted({names[b] for i in range(len(V)) for b, wt in V[i][1] if re.search(r'(?<![a-z])ear', names[b].lower()) and wt > 0}))
        tip = {i for i in range(len(V)) if ear_bone(i) > 0.5}
    else:
        how = 'no ear bones (geometric detection)'
        hx = max(abs(P[i][0]) for i in head_v)
        mid = [i for i in head_v if abs(P[i][0]) < 0.15 * hx]
        top = max(P[i][1] for i in mid)
        tip = {i for i in head_v if P[i][1] > top + 0.01 * H and abs(P[i][0]) > 0.2 * hx}
    ear_t = [t for t in T if any(i in tip for i in t)]
    ear_v = {i for t in ear_t for i in t}
    base = ear_v - tip                                     # head vertices the ears stand on
    left = lambda s: {i for i in s if P[i][0] > 0}
    lt, lb = left(tip), left(base)
    # one ear (left): size, position on the head, tilt
    head_len = max(P[i][2] for i in head_v) - min(P[i][2] for i in head_v)
    head_w = 2 * max(abs(P[i][0]) for i in head_v)
    hz0 = min(P[i][2] for i in head_v)
    bc = [sum(P[i][k] for i in lb) / len(lb) for k in range(3)] if lb else [0, 0, 0]
    tp = max(lt, key=lambda i: math.dist(P[i], bc))
    height = math.dist(P[tp], bc)
    bw = max(math.dist(P[a], P[b]) for a in lb for b in lb) if len(lb) > 1 else 0
    vec = [P[tp][k] - bc[k] for k in range(3)]
    tilt_out = math.degrees(math.atan2(vec[0], vec[1])); tilt_back = math.degrees(math.atan2(-vec[2], vec[1]))
    # card or volume: open edges among the ear triangles (by position)
    E = Counter()
    for t in [t for t in ear_t if all(P[i][0] > 0 for i in t)]:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): E[frozenset((key(a), key(b)))] += 1
    allE = Counter()
    for t in T:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): allE[frozenset((key(a), key(b)))] += 1
    open_e = sum(1 for e in E if allE[e] == 1)
    shares_head = sum(1 for i in lb if any(i in t for t in head_t if not any(j in tip for j in t)))
    print('== %s: %s' % (A['name'], how))
    print('   one ear: %d tip vertices, %d base vertices shared with the head, %d triangles; %s (%d open edges)'
          % (len(lt), len(lb), len([t for t in ear_t if all(P[i][0] > 0 for i in t)]),
             'a card / open shell' if open_e else 'closed into the head skin', open_e))
    print('   size: %.2f of head length tall, base %.2f of head width (%.3f m tall, base %.3f m)'
          % (height / head_len, bw / head_w, height, bw))
    nose = max(P[i][2] for i in head_v); skull_top = max(P[i][1] for i in head_v if not i in tip)
    print('   position: base %.2f head widths behind the nose tip, %.0f%% of the half-width out from the midline, %+.3f m from the '
          'skull top; tilted %.0f deg outward, %.0f deg back' % ((nose - bc[2]) / head_w, 100 * abs(bc[0]) / (head_w / 2), bc[1] - skull_top, tilt_out, tilt_back))
    wts = Counter(tuple(sorted(names[b] for b, wt in V[i][1] if wt > 0.1)) for i in lb)
    print('   base weights:', '; '.join('%s x%d' % ('+'.join(k), n) for k, n in wts.most_common(3)))

    # --- texture
    def texels(tris):
        pix, a3, auv = set(), 0.0, 0.0
        for t in tris:
            p0, p1, p2 = (P[i] for i in t); u = [(uvs[i][0] * w, uvs[i][1] * h) for i in t]
            cr = [(p1[(k + 1) % 3] - p0[(k + 1) % 3]) * (p2[(k + 2) % 3] - p0[(k + 2) % 3]) - (p1[(k + 2) % 3] - p0[(k + 2) % 3]) * (p2[(k + 1) % 3] - p0[(k + 1) % 3]) for k in range(3)]
            a3 += 0.5 * math.sqrt(sum(x * x for x in cr))
            auv += 0.5 * abs((u[1][0] - u[0][0]) * (u[2][1] - u[0][1]) - (u[2][0] - u[0][0]) * (u[1][1] - u[0][1]))
            for py in range(int(min(q[1] for q in u)), int(max(q[1] for q in u)) + 1):
                for px in range(int(min(q[0] for q in u)), int(max(q[0] for q in u)) + 1):
                    x, y = px + 0.5, py + 0.5
                    d = [(u[(k + 1) % 3][0] - u[k][0]) * (y - u[k][1]) - (u[(k + 1) % 3][1] - u[k][1]) * (x - u[k][0]) for k in range(3)]
                    if all(v >= 0 for v in d) or all(v <= 0 for v in d): pix.add((px % w, py % h))
        return pix, (math.sqrt(auv / a3) if a3 else 0)

    def normal(t):
        p0, p1, p2 = (P[i] for i in t)
        n = [(p1[(k + 1) % 3] - p0[(k + 1) % 3]) * (p2[(k + 2) % 3] - p0[(k + 2) % 3]) - (p1[(k + 2) % 3] - p0[(k + 2) % 3]) * (p2[(k + 1) % 3] - p0[(k + 1) % 3]) for k in range(3)]
        l = math.sqrt(sum(v * v for v in n)) or 1; return [v / l for v in n]
    et = ear_t
    ep, ed = texels(et); hp_, hd = texels([t for t in head_t if t not in ear_t])
    L = [lum(img[y][x]) for x, y in ep]; m = sum(L) / len(L); sd = math.sqrt(sum((v - m) ** 2 for v in L) / len(L))
    edge = sum(abs(lum(img[y][(x + 1) % w]) - lum(img[y][x])) + abs(lum(img[(y + 1) % h][x]) - lum(img[y][x])) for x, y in ep) / len(ep)
    shared = len(ep & hp_) / len(ep)
    front = [t for t in et if normal(t)[2] > 0.2]; back = [t for t in et if normal(t)[2] < -0.2]
    fp, _ = texels(front); bp, _ = texels(back)
    col = lambda pix: [sum(img[y][x][k] for x, y in pix) / max(1, len(pix)) / 255 for k in range(3)]
    uvkey = Counter((round(uvs[i][0], 4), round(uvs[i][1], 4)) for t in et for i in t)
    print('   texture: %d texels at %.0f px/m (head %.0f px/m); brightness %.2f, spread %.3f, range %.2f-%.2f, edges %.3f'
          % (len(ep), ed, hd, m, sd, min(L), max(L), edge))
    print('   %.0f%% of the ear texels are shared with the rest of the head (0%% = its own patch); front faces %d tris rgb %.2f %.2f %.2f, '
          'back faces %d tris rgb %.2f %.2f %.2f; front and back share %d texels'
          % (100 * shared, len(front), *col(fp), len(back), *col(bp), len(fp & bp)))
    # crop panel
    xs = [x for x, _ in ep]; yv = [y for _, y in ep]
    x0, x1, y0, y1 = max(0, min(xs) - 4), min(w - 1, max(xs) + 4), max(0, min(yv) - 4), min(h - 1, max(yv) + 4)
    if (x1 - x0) * (y1 - y0) > 9000:      # ears painted in two places: crop around the front faces only
        xs = [x for x, _ in fp] or xs; yv = [y for _, y in fp] or yv
        x0, x1, y0, y1 = max(0, min(xs) - 4), min(w - 1, max(xs) + 4), max(0, min(yv) - 4), min(h - 1, max(yv) + 4)
    S_ = 8; pw, ph = (x1 - x0 + 1) * S_, (y1 - y0 + 1) * S_
    pan = [[img[y0 + r // S_][x0 + c // S_] for c in range(pw)] for r in range(ph)]
    for t in et:
        colr = (230, 40, 40) if normal(t)[2] > 0.2 else (60, 110, 255) if normal(t)[2] < -0.2 else (240, 220, 60)
        u = [((uvs[i][0] * w - x0) * S_, (uvs[i][1] * h - y0) * S_) for i in t]
        for k in range(3):
            (ax, ay), (bx, by) = u[k], u[(k + 1) % 3]; n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for s_ in range(n + 1):
                xx, yy = int(ax + (bx - ax) * s_ / n), int(ay + (by - ay) * s_ / n)
                if 0 <= xx < pw and 0 <= yy < ph: pan[yy][xx] = colr
    panels.append(pan)
W = sum(len(p[0]) for p in panels) + 10 * (len(panels) + 1); Hh = max(len(p) for p in panels) + 20
sheet = [[(90, 90, 90)] * W for _ in range(Hh)]; ox = 10
for p in panels:
    for r, row in enumerate(p):
        for c, colv in enumerate(row): sheet[10 + r][ox + c] = colv
    ox += len(p[0]) + 10
raw = b''.join(b'\x00' + bytes(v for colv in row for v in colv) for row in sheet)
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, Hh, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
print('sheet', OUT, W, Hh)
