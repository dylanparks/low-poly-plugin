"""What kind of skin a model's texture paints, measured on the model: fur, scales, plates, wet skin or chitin differ in how
regular the pattern is, how sharp its edges are, whether it has dark crevices between cells, and whether it has painted
glossy highlights. Standard library only; reads the viewer's files.
Usage: python -I skin_study.py <model.gltf> <out dir> <animal id>
Measured on the side render of the texture alone (unlit, the model 720 px long; the same render as body_study.py), over every
pixel of the silhouette at least 4 px from its edge:
  - bands: large shapes (over 5% of the length), form (1-5%), fine detail (under 1%), as sd of brightness;
  - repeat: the autocorrelation of the detail (form plus fine) along the body and up and down. The first peak after the first
    trough gives a cell size (as % of the model's length) and how regular the repeat is (the peak's height: 0 none, 1 a perfect
    tiling). Scales and plates repeat; fur and wet skin don't;
  - direction: the coherence of the fine detail's gradients (0 = no direction, 1 = parallel strokes);
  - crevices: the share of pixels at least 0.10 darker than their 1%-neighbourhood (the dark grout between scales and plates);
  - highlights: the share of pixels at least 0.18 brighter than their 5%-neighbourhood and above 0.45 (painted gloss), and the
    highlights' saturation (white gloss against coloured);
  - edges: the share of pixels whose brightness changes by more than 0.12 to a neighbour;
  - colour: mean saturation, the spread of hue, and the brightness range (5-95%).
Writes <id>_swatch.png: a 160 x 160 px patch of the render from the most solid part of the body, enlarged 2x."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, math, os, sys, zlib, struct, colorsys

D, OUTD, AID = sys.argv[1:4]
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'body_study.py'), encoding='utf-8').read()
part1 = src[:src.index('# ---------------------------------------------------------------- 2.')]
g = {'__file__': os.path.join(here, 'body_study.py')}
argv = sys.argv; sys.argv = ['body_study.py', D, OUTD, AID, '0']
with contextlib.redirect_stdout(io.StringIO()): exec(part1, g)
sys.argv = argv
Lm, B1, B2, img, HT, WD = g['Lm'], g['B1'], g['B2'], g['img'], g['HT'], g['WD']
inner = [[Lm[y][x] is not None and all(0 <= y + dy < HT and 0 <= x + dx < WD and Lm[y + dy][x + dx] is not None
                                        for dy in (-4, 0, 4) for dx in (-4, 0, 4)) for x in range(WD)] for y in range(HT)]
pts = [(y, x) for y in range(HT) for x in range(WD) if inner[y][x]]
sd = lambda v: math.sqrt(sum((a - sum(v) / len(v)) ** 2 for a in v) / len(v))
large = [B2[y][x] for y, x in pts]; mid = [B1[y][x] - B2[y][x] for y, x in pts]; fine = [Lm[y][x] - B1[y][x] for y, x in pts]
Dd = [[(Lm[y][x] - B2[y][x]) if inner[y][x] else None for x in range(WD)] for y in range(HT)]


SAMPLE = pts[::max(1, len(pts) // 15000)]                       # a sample of the pixels is enough for the repeat


def autocorr(dx, dy):
    num = va = 0.0; n = 0
    for y, x in SAMPLE:
        yy, xx = y + dy, x + dx
        if 0 <= yy < HT and 0 <= xx < WD and Dd[yy][xx] is not None:
            a, b = Dd[y][x], Dd[yy][xx]; num += a * b; va += (a * a + b * b) / 2; n += 1
    return num / va if va else 0.0


def repeat(axis):
    ac = [autocorr(l, 0) if axis == 'x' else autocorr(0, l) for l in range(1, 41)]
    trough = next((i for i in range(1, len(ac) - 1) if ac[i] < ac[i - 1] and ac[i] <= ac[i + 1]), None)
    if trough is None: return None, 0.0
    peak = max(range(trough, len(ac)), key=lambda i: ac[i])
    return (peak + 1) / 720 * 100, ac[peak] - ac[trough]


px_ = (WD and 1)
rx, sx = repeat('x'); ry, sy = repeat('y')
jxx = jyy = jxy = 0.0
for y, x in pts:
    if None in (Lm[y][x + 1], Lm[y][x - 1], Lm[y + 1][x], Lm[y - 1][x], B1[y][x + 1], B1[y][x - 1], B1[y + 1][x], B1[y - 1][x]): continue
    gx = (Lm[y][x + 1] - B1[y][x + 1]) - (Lm[y][x - 1] - B1[y][x - 1]); gy = (Lm[y + 1][x] - B1[y + 1][x]) - (Lm[y - 1][x] - B1[y - 1][x])
    jxx += gx * gx; jyy += gy * gy; jxy += gx * gy
coh = math.sqrt((jxx - jyy) ** 2 + 4 * jxy * jxy) / (jxx + jyy) if jxx + jyy else 0
crev = sum(1 for y, x in pts if Lm[y][x] - B1[y][x] < -0.10) / len(pts)
hl = [(y, x) for y, x in pts if Lm[y][x] - B2[y][x] > 0.18 and Lm[y][x] > 0.45]
hl_sat = sum(colorsys.rgb_to_hsv(*(c / 255 for c in img[y][x][:3]))[1] for y, x in hl) / len(hl) if hl else 0
edges = sum(1 for y, x in pts if Lm[y][x + 1] is not None and Lm[y + 1][x] is not None and max(abs(Lm[y][x] - Lm[y][x + 1]), abs(Lm[y][x] - Lm[y + 1][x])) > 0.12) / len(pts)
hsv = [colorsys.rgb_to_hsv(*(c / 255 for c in img[y][x][:3])) for y, x in pts]
sat = sum(h[1] for h in hsv) / len(hsv)
hx = sum(math.cos(2 * math.pi * h[0]) * h[1] for h in hsv); hy_ = sum(math.sin(2 * math.pi * h[0]) * h[1] for h in hsv)
hue_spread = 1 - math.hypot(hx, hy_) / (sum(h[1] for h in hsv) or 1)
Ls = sorted(Lm[y][x] for y, x in pts)
print('== %s (%s): %d pixels' % (g['A']['name'], AID, len(pts)))
print('   bands large %.3f | form %.3f | fine %.3f' % (sd(large), sd(mid), sd(fine)))
print('   repeat along %s | up-down %s | direction coherence %.2f'
      % ('%.1f%% (%.2f)' % (rx, sx) if rx else 'none', '%.1f%% (%.2f)' % (ry, sy) if ry else 'none', coh))
print('   crevices %.1f%% | highlights %.2f%% (saturation %.2f) | edges %.1f%% | saturation %.2f, hue spread %.2f, brightness %.2f-%.2f'
      % (100 * crev, 100 * len(hl) / len(pts), hl_sat, 100 * edges, sat, hue_spread, Ls[len(Ls) // 20], Ls[19 * len(Ls) // 20]))
# swatch: the most solid 160 x 160 window
best, by, bx = -1, 0, 0
for y0 in range(0, max(1, HT - 160), 10):
    for x0 in range(0, max(1, WD - 160), 10):
        n = sum(1 for y in range(y0, min(HT, y0 + 160), 8) for x in range(x0, min(WD, x0 + 160), 8) if inner[y][x])
        if n > best: best, by, bx = n, y0, x0
rows = []
for y in range(by, min(HT, by + 160)):
    row = b'\x00'
    for x in range(bx, min(WD, bx + 160)):
        c = img[y][x][:3] if img[y][x] is not None else (40, 42, 48); row += bytes(c) * 2
    rows += [row, row]
w_ = (min(WD, bx + 160) - bx) * 2
ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(os.path.join(OUTD, AID + '_swatch.png'), 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w_, len(rows), 8, 2, 0, 0, 0))
                                                        + ch(b'IDAT', zlib.compress(b''.join(rows), 9)) + ch(b'IEND', b''))
