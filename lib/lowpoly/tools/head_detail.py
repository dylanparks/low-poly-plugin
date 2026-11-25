"""Head texture detail per animal: texel density (texture px per metre and per animal height) and painted contrast
(luminance spread and edge strength) inside the head triangles' UV footprint. Standard library only.
Usage: python -I head_detail.py <model.gltf> <name>   (or a viewer folder and one or more animal ids, to compare them)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import sys, io, contextlib, struct, zlib, math
D = sys.argv[1]


def read_png(path):
    b = open(path, 'rb').read(); i = 8; w = h = ct = None; idat = b''
    while i < len(b):
        n, t = struct.unpack('>I4s', b[i:i + 8]); d = b[i + 8:i + 8 + n]; i += 12 + n
        if t == b'IHDR': w, h, bd, ct = struct.unpack('>IIBB', d[:10])
        elif t == b'IDAT': idat += d
    bpp = {2: 3, 6: 4, 0: 1, 4: 2}[ct]; raw = zlib.decompress(idat); stride = w * bpp; out = []; prev = bytearray(stride); p = 0
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
        out.append([sum(line[x * bpp:x * bpp + min(3, bpp)]) / (3 * 255) for x in range(w)]); prev = line
    return w, h, out


src = open(D + '/../rig_study.py').read() if False else None
for aid in sys.argv[2:]:
    g = {}; sys.argv = ['x', sys.argv[1], aid]
    code = open(__file__.replace('head_detail.py', 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
    with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
    A, V, T = g['A'], g['V'], g['T']
    # UVs: re-read corners (rig_study keeps positions and weights only)
    import base64
    uvs = []
    for s in A['subs']:
        raw = base64.b64decode(s['v'])
        for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
    w, h, img = read_png(D + '/textures/%s.png' % A['tex'][0])
    P = [v[0] for v in V]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
    H = max(ys) - min(ys); zmax, zmin = max(zs), min(zs)
    # head = triangles whose corners all lie in the front 18% of the length and above 45% of the height
    from lowpoly import rig_parts                       # the head from the rig; the height rule when the rig shows none
    head = rig_parts.head_triangles(rig_parts.parts(A, V), T) or [t for t in T if all(P[i][2] > zmax - 0.18 * (zmax - zmin) and P[i][1] > min(ys) + 0.45 * H for i in t)]
    a3 = auv = 0.0; pix = set()
    for t in head:
        p0, p1, p2 = (P[i] for i in t); u0, u1, u2 = (uvs[i] for i in t)
        c = [(p1[1] - p0[1]) * (p2[2] - p0[2]) - (p1[2] - p0[2]) * (p2[1] - p0[1]), (p1[2] - p0[2]) * (p2[0] - p0[0]) - (p1[0] - p0[0]) * (p2[2] - p0[2]),
             (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])]
        a3 += 0.5 * math.sqrt(sum(x * x for x in c))
        auv += 0.5 * abs((u1[0] - u0[0]) * (u2[1] - u0[1]) - (u2[0] - u0[0]) * (u1[1] - u0[1])) * w * h
        # rasterise the UV triangle to collect texels (wrap to the texture)
        xs = [u[0] * w for u in (u0, u1, u2)]; yv = [u[1] * h for u in (u0, u1, u2)]
        for py in range(int(min(yv)), int(max(yv)) + 1):
            for px_ in range(int(min(xs)), int(max(xs)) + 1):
                x, y = px_ + 0.5, py + 0.5
                d1 = (xs[1] - xs[0]) * (y - yv[0]) - (yv[1] - yv[0]) * (x - xs[0])
                d2 = (xs[2] - xs[1]) * (y - yv[1]) - (yv[2] - yv[1]) * (x - xs[1])
                d3 = (xs[0] - xs[2]) * (y - yv[2]) - (yv[0] - yv[2]) * (x - xs[2])
                if (d1 >= 0 and d2 >= 0 and d3 >= 0) or (d1 <= 0 and d2 <= 0 and d3 <= 0): pix.add((px_ % w, py % h))
    lum = [img[y][x] for x, y in pix]; m = sum(lum) / len(lum); sd = math.sqrt(sum((l - m) ** 2 for l in lum) / len(lum))
    grad = [abs(img[y][(x + 1) % w] - img[y][x]) + abs(img[(y + 1) % h][x] - img[y][x]) for x, y in pix]
    dens = math.sqrt(auv / a3)
    print('%-28s tex %dx%d | head: %d tris, %d texels | %.0f px/m = %.0f px per animal height | lum mean %.2f, spread (sd) %.3f, '
          'range %.2f-%.2f | edge strength %.3f'
          % (A['name'], w, h, len(head), len(pix), dens, dens * H, m, sd, min(lum), max(lum), sum(grad) / len(grad)))
