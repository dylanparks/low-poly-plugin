"""Render an animal's walk clip as a grid of side-view silhouettes (facing left, like a reference sheet). Standard library only.
Usage: python -I walk_sheet.py <model.gltf> - <clip> <out.png> [frames=12] [cols=3]"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 5 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import sys, io, contextlib, struct, zlib
D, AID, CLIP, OUT = sys.argv[1:5]
NF = int(sys.argv[5]) if len(sys.argv) > 5 else 12; COLS = int(sys.argv[6]) if len(sys.argv) > 6 else 3
g = {}; sys.argv = ['x', D, AID]
src = open(__file__.replace('walk_sheet.py', 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
with contextlib.redirect_stdout(io.StringIO()): exec(src, g)
world, rest, pose_at, clip, skin, T, A = (g[k] for k in ('world', 'rest', 'pose_at', 'clip', 'skin', 'T', 'A'))
cl = clip(CLIP)
frames = [skin(world(pose_at(cl, k / NF))) for k in range(NF)]
allp = [p for f in frames for p in f]
zmin, zmax = min(p[2] for p in allp), max(p[2] for p in allp); ymin, ymax = min(p[1] for p in allp), max(p[1] for p in allp)
CW, CH, PAD = 300, 170, 12
s = min((CW - 2 * PAD) / (zmax - zmin), (CH - 2 * PAD) / (ymax - ymin))
ROWS = (NF + COLS - 1) // COLS; W, H = CW * COLS, CH * ROWS
img = bytearray([255] * (W * H * 3))
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: i = (y * W + x) * 3; img[i:i + 3] = bytes(c)
for k, P in enumerate(frames):
    ox, oy = (k % COLS) * CW, (k // COLS) * CH
    pts = [(ox + PAD + (zmax - p[2]) * s, oy + CH - PAD - (p[1] - ymin) * s) for p in P]   # nose to the left
    # far-side legs lighter so the near legs read on top (x < 0 is the right side = far side when facing left)
    order = sorted(T, key=lambda t: sum(P[i][0] for i in t))
    for t in order:
        far = sum(P[i][0] for i in t) / 3 < -0.02
        col = (150, 156, 160) if far else (84, 92, 98)
        (x0, y0), (x1, y1), (x2, y2) = (pts[i] for i in t)
        lo, hi = int(max(oy, min(y0, y1, y2))), int(min(oy + CH - 1, max(y0, y1, y2)))
        for y in range(lo, hi + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)), ((x1, y1), (x2, y2)), ((x2, y2), (x0, y0))):
                if (ay <= y + 0.5 < by) or (by <= y + 0.5 < ay): xs.append(ax + (y + 0.5 - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1): put(x, y, col)
    gy = int(oy + CH - PAD + 1)
    for x in range(ox + 4, ox + CW - 4): put(x, gy, (220, 120, 120))
    # frame number as dots
    for d in range(k + 1): put(ox + 6 + d * 4, oy + 6, (0, 0, 0)); put(ox + 6 + d * 4, oy + 7, (0, 0, 0))
raw = b''.join(b'\x00' + bytes(img[y * W * 3:(y + 1) * W * 3]) for y in range(H))
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
print('wrote', OUT, W, H)
