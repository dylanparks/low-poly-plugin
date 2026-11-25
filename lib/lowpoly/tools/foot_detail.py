"""Foot texture detail per animal: how many texture pixels the feet get, how much contrast is painted into them, how the
foot differs in colour from the lower leg above it, and a contact sheet of each foot's texture footprint (4x, triangle
outlines in red) to see what is drawn. Standard library only; only reads the viewer's files.
Usage: python -I foot_detail.py <model.gltf> <out.png> <name>   (or a viewer folder and one or more animal ids, to compare them)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, struct, sys, zlib

D, OUT, IDS = sys.argv[1], sys.argv[2], sys.argv[3:]


def read_png(path):
    b = open(path, 'rb').read(); i = 8; idat = b''
    while i < len(b):
        n, t = struct.unpack('>I4s', b[i:i + 8]); d = b[i + 8:i + 8 + n]; i += 12 + n
        if t == b'IHDR': w, h, bd, ct = struct.unpack('>IIBB', d[:10])
        elif t == b'IDAT': idat += d
    bpp = {2: 3, 6: 4, 0: 1, 4: 2}[ct]; raw = zlib.decompress(idat); stride = w * bpp; rows = []; prev = bytearray(stride); p = 0
    for _ in range(h):
        f = raw[p]; line = bytearray(raw[p + 1:p + 1 + stride]); p += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0; up = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + up) & 255
            elif f == 3: line[x] = (line[x] + (a + up) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(up - c), abs(a - c), abs(a + up - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else up if pb <= pc else c)) & 255
        rows.append([tuple(line[x * bpp + k] if bpp >= 3 else line[x * bpp] for k in range(3)) for x in range(w)]); prev = line
    return w, h, rows


def lum(c): return (c[0] + c[1] + c[2]) / (3 * 255)


here = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
panels = []
for aid in IDS:
    g = {}; sys.argv = ['x', D, aid]
    with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
    A, V, T = g['A'], g['V'], g['T']
    uvs = []
    for s in A['subs']:
        raw = base64.b64decode(s['v'])
        for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
    w, h, img = read_png(g['texpath']())
    P = [v[0] for v in V]; ys = [p[1] for p in P]; lo = min(ys); H = max(ys) - lo

    def texels(tris):
        pix, a3, auv = set(), 0.0, 0.0
        for t in tris:
            p0, p1, p2 = (P[i] for i in t); u = [(uvs[i][0] * w, uvs[i][1] * h) for i in t]
            c = [(p1[1] - p0[1]) * (p2[2] - p0[2]) - (p1[2] - p0[2]) * (p2[1] - p0[1]), (p1[2] - p0[2]) * (p2[0] - p0[0]) - (p1[0] - p0[0]) * (p2[2] - p0[2]),
                 (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])]
            a3 += 0.5 * math.sqrt(sum(x * x for x in c))
            auv += 0.5 * abs((u[1][0] - u[0][0]) * (u[2][1] - u[0][1]) - (u[2][0] - u[0][0]) * (u[1][1] - u[0][1]))
            for py in range(int(min(q[1] for q in u)), int(max(q[1] for q in u)) + 1):
                for px in range(int(min(q[0] for q in u)), int(max(q[0] for q in u)) + 1):
                    x, y = px + 0.5, py + 0.5
                    d = [(u[(k + 1) % 3][0] - u[k][0]) * (y - u[k][1]) - (u[(k + 1) % 3][1] - u[k][1]) * (x - u[k][0]) for k in range(3)]
                    if all(v >= 0 for v in d) or all(v <= 0 for v in d): pix.add((px % w, py % h))
        return pix, (math.sqrt(auv / a3) if a3 else 0)

    cy = lambda t: sum(P[i][1] for i in t) / 3 - lo                     # triangle centre height above the ground
    foot = [t for t in T if cy(t) < 0.08 * H]
    leg = [t for t in T if 0.10 * H < cy(t) < 0.25 * H]
    fp, fd = texels(foot); lp, _ = texels(leg)
    L = [lum(img[y][x]) for x, y in fp]; m = sum(L) / len(L); sd = math.sqrt(sum((v - m) ** 2 for v in L) / len(L))
    edge = sum(abs(lum(img[y][(x + 1) % w]) - lum(img[y][x])) + abs(lum(img[(y + 1) % h][x]) - lum(img[y][x])) for x, y in fp) / len(fp)
    fc = [sum(img[y][x][k] for x, y in fp) / len(fp) / 255 for k in range(3)]
    lc = [sum(img[y][x][k] for x, y in lp) / len(lp) / 255 for k in range(3)] if lp else [0, 0, 0]
    print('%-16s foot: %3d tris, %4d texels, %3.0f px/m | brightness %.2f, spread %.3f, range %.2f-%.2f, edges %.3f | '
          'foot rgb %.2f %.2f %.2f vs lower leg %.2f %.2f %.2f (foot %+.2f brighter)'
          % (A['name'], len(foot), len(fp), fd, m, sd, min(L), max(L), edge, *fc, *lc, m - (sum(lc) / 3)))
    # contact-sheet panels: one per foot (left front, left hind), 8x, with that foot's triangles outlined
    zs_ = [p_[2] for p_ in P]; zmid = (min(zs_) + max(zs_)) / 2
    for front in (True, False):
      grp = [t for t in foot if sum(P[i][0] for i in t) > 0 and (sum(P[i][2] for i in t) / 3 > zmid) == front]
      if not grp: continue
      gp, _ = texels(grp); xs = [x for x, _ in gp]; yv = [y for _, y in gp]
      x0, x1, y0, y1 = max(0, min(xs) - 4), min(w - 1, max(xs) + 4), max(0, min(yv) - 4), min(h - 1, max(yv) + 4)
      S = 8; pw, ph = (x1 - x0 + 1) * S, (y1 - y0 + 1) * S
      pan = [[img[y0 + r // S][x0 + c // S] for c in range(pw)] for r in range(ph)]
      for t in grp:
        u = [((uvs[i][0] * w - x0) * S, (uvs[i][1] * h - y0) * S) for i in t]
        for k in range(3):
            (ax, ay), (bx, by) = u[k], u[(k + 1) % 3]; n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for s_ in range(n + 1):
                xx, yy = int(ax + (bx - ax) * s_ / n), int(ay + (by - ay) * s_ / n)
                if 0 <= xx < pw and 0 <= yy < ph: pan[yy][xx] = (230, 40, 40)
      panels.append(pan)
    continue
    xs = [x for x, _ in fp]; yv = [y for _, y in fp]
    x0, x1, y0, y1 = max(0, min(xs) - 3), min(w - 1, max(xs) + 3), max(0, min(yv) - 3), min(h - 1, max(yv) + 3)
    S = 4; pw, ph = (x1 - x0 + 1) * S, (y1 - y0 + 1) * S
    pan = [[img[y0 + r // S][x0 + c // S] for c in range(pw)] for r in range(ph)]
    for t in foot:
        u = [((uvs[i][0] * w - x0) * S, (uvs[i][1] * h - y0) * S) for i in t]
        for k in range(3):
            (ax, ay), (bx, by) = u[k], u[(k + 1) % 3]; n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for s_ in range(n + 1):
                xx, yy = int(ax + (bx - ax) * s_ / n), int(ay + (by - ay) * s_ / n)
                if 0 <= xx < pw and 0 <= yy < ph: pan[yy][xx] = (230, 40, 40)
    panels.append(pan)
# stack the panels left to right on a grey sheet
W = sum(len(p[0]) for p in panels) + 10 * (len(panels) + 1); Hh = max(len(p) for p in panels) + 20
sheet = [[(90, 90, 90)] * W for _ in range(Hh)]; ox = 10
for p in panels:
    for r, row in enumerate(p):
        for c, col in enumerate(row): sheet[10 + r][ox + c] = col
    ox += len(p[0]) + 10
raw = b''.join(b'\x00' + bytes(v for col in row for v in col) for row in sheet)
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, Hh, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
print('sheet', OUT, W, Hh, '(left to right:', ', '.join(IDS) + ')')
