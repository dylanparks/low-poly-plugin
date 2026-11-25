"""How a model's texture is laid onto its triangles: stretch (the ratio of the two directions' pixel densities on each
triangle), how even the pixel density is over the surface, and UV seams (one mesh edge mapped to two places in the
texture) with the colour jump across them. Area-weighted. Standard library only; only reads the viewer's files.
Usage: python -I uv_study.py <model.gltf> <name> [--where: list where the worst seams are]   (or a viewer folder and one or more animal ids, to compare them)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, struct, sys, zlib
from collections import defaultdict

WHERE = '--where' in sys.argv
D, IDS = sys.argv[1], [a for a in sys.argv[2:] if a != '--where']
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]


def sample(img, w, h, u, v):
    x, y = u * w - 0.5, v * h - 0.5; x0, y0 = math.floor(x), math.floor(y); fx, fy = x - x0, y - y0
    c = [0.0, 0.0, 0.0]
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        p = img[min(h - 1, max(0, y0 + dy))][min(w - 1, max(0, x0 + dx))]
        for k in range(3): c[k] += wt * p[k] / 255
    return c


for aid in IDS:
    g = {}; sys.argv = ['x', D, aid]
    with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
    A, V, T = g['A'], g['V'], g['T']
    uvs = []
    for s in A['subs']:
        raw = base64.b64decode(s['v'])
        for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
    w, h, img = read_png(g['texpath']())
    P = [v[0] for v in V]
    rows = []   # (area, anisotropy, density, dominant normal axis)
    for t in T:
        p0, p1, p2 = (P[i] for i in t)
        e1 = [p1[k] - p0[k] for k in range(3)]; e2 = [p2[k] - p0[k] for k in range(3)]
        n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
        area = 0.5 * math.sqrt(sum(x * x for x in n))
        if area < 1e-9: continue
        l1 = math.sqrt(sum(x * x for x in e1)); ax = [x / l1 for x in e1]
        nn = [x / (2 * area) for x in n]; ay = [nn[1] * ax[2] - nn[2] * ax[1], nn[2] * ax[0] - nn[0] * ax[2], nn[0] * ax[1] - nn[1] * ax[0]]
        a = (l1, 0.0); b = (sum(e2[k] * ax[k] for k in range(3)), sum(e2[k] * ay[k] for k in range(3)))
        u0, u1, u2 = ((uvs[i][0] * w, uvs[i][1] * h) for i in t)
        du1 = (u1[0] - u0[0], u1[1] - u0[1]); du2 = (u2[0] - u0[0], u2[1] - u0[1])
        det = a[0] * b[1] - a[1] * b[0]
        if abs(det) < 1e-12: continue
        # J = [du1 du2] * inverse([a b])
        i00, i01, i10, i11 = b[1] / det, -b[0] / det, -a[1] / det, a[0] / det
        J = (du1[0] * i00 + du2[0] * i10, du1[0] * i01 + du2[0] * i11, du1[1] * i00 + du2[1] * i10, du1[1] * i01 + du2[1] * i11)
        tr = J[0] ** 2 + J[1] ** 2 + J[2] ** 2 + J[3] ** 2; dt = abs(J[0] * J[3] - J[1] * J[2])
        disc = math.sqrt(max(0.0, tr * tr / 4 - dt * dt))
        s1, s2 = math.sqrt(tr / 2 + disc), math.sqrt(max(0.0, tr / 2 - disc))
        axis = 'xyz'[max(range(3), key=lambda k: abs(nn[k]))]
        rows.append((area, s1 / max(s2, 1e-6), math.sqrt(s1 * max(s2, 1e-6)), axis))
    tot = sum(r[0] for r in rows)
    share = lambda f: 100 * sum(r[0] for r in rows if f(r)) / tot
    dens = sorted((r[2], r[0]) for r in rows); acc = 0; med = dens[-1][0]
    for d_, a_ in dens:
        acc += a_
        if acc >= tot / 2: med = d_; break
    logs = [(math.log(r[2]), r[0]) for r in rows]; mlog = sum(l * a_ for l, a_ in logs) / tot
    spread = math.sqrt(sum(a_ * (l - mlog) ** 2 for l, a_ in logs) / tot)
    print('== %s (%dx%d): median %.0f px/m; density spread x%.2f (1 sd); surface stretched more than 2:1 %.0f%%, more than 4:1 %.0f%%'
          % (A['name'], w, h, med, math.exp(spread), share(lambda r: r[1] > 2), share(lambda r: r[1] > 4)))
    for ax_ in 'xyz':
        part = [r for r in rows if r[3] == ax_]
        if part:
            pa = sum(r[0] for r in part)
            print('   faces facing %s: %3.0f%% of the surface, %3.0f%% of them stretched >4:1, median stretch %.1f'
                  % ({'x': 'sideways (x)', 'y': 'up/down (y)', 'z': 'forward/back (z)'}[ax_], 100 * pa / tot,
                     100 * sum(r[0] for r in part if r[1] > 4) / pa, sorted(r[1] for r in part)[len(part) // 2]))
    # seams: an edge (by position) whose two triangles give its endpoints different UVs
    key = lambda i: tuple(round(c, 4) for c in P[i])
    E = defaultdict(list)
    for t in T:
        for a_, b_ in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            E[frozenset((key(a_), key(b_)))].append((a_, b_))
    seams, jumps, worst = 0, [], []
    for e, sides in E.items():
        if len(sides) != 2: continue
        (a1, b1), (a2, b2) = sides
        if key(a1) != key(a2): a2, b2 = b2, a2
        d = max(math.dist((uvs[a1][0] * w, uvs[a1][1] * h), (uvs[a2][0] * w, uvs[a2][1] * h)),
                math.dist((uvs[b1][0] * w, uvs[b1][1] * h), (uvs[b2][0] * w, uvs[b2][1] * h)))
        if d < 1.0: continue
        seams += 1
        j = 0.0
        for f in (0.25, 0.5, 0.75):
            ua = [uvs[a1][k] + (uvs[b1][k] - uvs[a1][k]) * f for k in range(2)]; ub = [uvs[a2][k] + (uvs[b2][k] - uvs[a2][k]) * f for k in range(2)]
            j += math.dist(sample(img, w, h, *ua), sample(img, w, h, *ub)) / 3
        jumps.append(j)
        if WHERE and j > 0.15: worst.append((j, [round((P[a1][k] + P[b1][k]) / 2, 3) for k in range(3)]))
    jumps.sort()
    for j, m in sorted(worst, reverse=True)[:12]: print('      seam jump %.2f at (x %.3f, y %.3f, z %.3f)' % (j, *m))
    print('   UV seams: %d of %d edges; colour jump across them: median %.3f, worst 10%% above %.3f, %d edges jump more than 0.15'
          % (seams, sum(1 for s_ in E.values() if len(s_) == 2), jumps[len(jumps) // 2] if jumps else 0,
             jumps[int(len(jumps) * 0.9)] if jumps else 0, sum(1 for j in jumps if j > 0.15)))
