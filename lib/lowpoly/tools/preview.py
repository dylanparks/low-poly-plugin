"""The model as a person reviewing it sees it: six fixed views under the engine's lights, and a page to turn it round in.
Every builder in the first agent trial judged its work from renders that did not match what the reviewer saw (too bright,
framed on the head only, never from behind or above), and most later feedback was about views the builder had never looked
at. This draws the whole body, framed on its full extent, at one scale per pair of views that share an axis (the two 3/4s;
side and top; front and rear) so proportions compare directly within each pair, with the ground line and a scale bar:
  3/4 front (left, from above), 3/4 rear (left, from above), side (left), front, rear, top (nose up).
Lighting, normals and texture sampling are lit_view.py's (the viewer's hemisphere sky and ground plus a sun, smooth normals,
bilinear texture). With a clip and a phase the model is skinned in that frame, normals included.
It also writes preview.html: one self-contained page (no network, plain WebGL) with the same lights, the six views as
buttons, drag to orbit, the wheel to zoom, and every clip baked to frames so it plays exactly as skinned here.
Standard library only.
Usage: python -I preview.py <model.gltf|.glb> <out dir> [clip name] [phase 0..1] [tile width=480]
Writes <out>/sheet.png (the six views, labelled), <out>/views/<view>.png and <out>/preview.html."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, json, math, os, struct, sys, zlib

D, OUT = sys.argv[1:3]
CLIP = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] not in ('', '-') else None
PHASE = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
TW = int(sys.argv[5]) if len(sys.argv) > 5 else 480
TH = TW * 3 // 4
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('def lum')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, '-']
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
A, V, T = g['A'], g['V'], g['T']
if CLIP and CLIP not in A.get('anims', {}):
    sys.exit('preview: no clip %r (clips: %s)' % (CLIP, ', '.join(A.get('anims', {})) or 'none'))
corners = []
for s in A['subs']:
    raw = base64.b64decode(s['v'])
    for k in range(0, len(raw), 64): corners.append(struct.unpack_from('<8f', raw, k))      # position, normal, uv
TEX = g['texpath']()
if TEX and not open(TEX, 'rb').read(8).startswith(b'\x89PNG'):
    sys.exit('preview: the texture is not a PNG (%s); convert it first' % TEX)
tw, th, tex = read_png(TEX) if TEX else (1, 1, [[(180, 180, 180)]])
nb = len(A['bones'])


def posed(clip_name, phase):
    """corner positions and normals in a frame of a clip (the bind pose without one); normals skinned like the positions"""
    if not clip_name: return [list(c[0:3]) for c in corners], [list(c[3:6]) for c in corners]
    W = g['world'](g['pose_at'](g['clip'](clip_name), phase))
    P = g['skin'](W); N = []
    for ci, (pos, ws) in enumerate(V):
        n = corners[ci][3:6]; acc = [0.0, 0.0, 0.0]
        for b, w in ws:
            r = g['qrot'](W[b][0], g['qrot'](g['inv'][b][0], n))
            for k in range(3): acc[k] += w * r[k]
        l = math.sqrt(sum(a * a for a in acc)) or 1.0; N.append([a / l for a in acc])
    return P, N


# yaw 0 looks at the animal's left side, nose to the image's left; 90 from the front; pitch positive looks down
VIEWS = [('3/4 front', 'front34', 45, 22), ('3/4 rear', 'rear34', -45, 22), ('side', 'side', 0, 0),
         ('front', 'front', 90, 0), ('rear', 'rear', -90, 0), ('top', 'top', -90, 90)]


def projector(yaw, pitch):
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    def proj(p):
        x, y, z = p; d = z * sy + x * cy
        return -(z * cy - x * sy), y * cp - d * sp, d * cp + y * sp
    return proj


sun = (3, 6, -4); _l = math.sqrt(sum(c * c for c in sun)); sun = tuple(c / _l for c in sun)
ground = (0x44 / 255, 0x50 / 255, 0x66 / 255)
BG = (40, 42, 48)


def _lin(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def _srgb(v): v = max(0.0, min(1.0, v)); return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
GROUND_LIN = tuple(_lin(g) for g in ground)


def light(c, n):
    """the viewer's shading, as three.js r160 computes it: the texture decoded from sRGB to linear, a hemisphere light
    (white sky, 0x445066 ground, intensity 1.2) and a sun (1.6) on a Lambert surface whose response is albedo / pi, then
    encoded back to sRGB. The model is z-mirrored as the viewer shows it. (Before 2026-11-23 this multiplied the sRGB colour
    by the light directly, with no 1/pi: up-facing surfaces rendered about 2.8x brighter than in the viewer, so builders
    darkened coats that then looked muddy in the viewer.)"""
    nm = (n[0], n[1], -n[2]); h = 0.5 + 0.5 * nm[1]; d = max(0.0, sum(nm[k] * sun[k] for k in range(3)))
    return [_srgb(_lin(c[k]) * (1.2 * (h + (1 - h) * GROUND_LIN[k]) + 1.6 * d) / math.pi) for k in range(3)]


def sample(u, v):
    x = u * tw - 0.5; y = v * th - 0.5; x0, y0 = math.floor(x), math.floor(y); fx, fy = x - x0, y - y0
    def at(i, j): return tex[min(th - 1, max(0, j))][min(tw - 1, max(0, i))]
    return [((at(x0, y0)[k] * (1 - fx) + at(x0 + 1, y0)[k] * fx) * (1 - fy) + (at(x0, y0 + 1)[k] * (1 - fx) + at(x0 + 1, y0 + 1)[k] * fx) * fy) / 255 for k in range(3)]


def new_img(w, h, c=BG): return [bytearray(bytes(c) * w) for _ in range(h)]


def put(img, x, y, c):
    if 0 <= y < len(img) and 0 <= x < len(img[0]) // 3: img[y][3 * x:3 * x + 3] = bytes(c)


def render(P, N, yaw, pitch, S, w, h):
    proj = projector(yaw, pitch); q = [proj(p) for p in P]
    xs = [a[0] for a in q]; ys = [a[1] for a in q]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    img = new_img(w, h); zb = [[-1e18] * w for _ in range(h)]
    def scr(a): return (w / 2 + (a[0] - cx) * S, h / 2 - (a[1] - cy) * S, a[2])
    for t in T:
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [scr(q[i]) for i in t]
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9: continue
        cs = [corners[i] for i in t]; ns = [N[i] for i in t]
        for py in range(max(0, int(min(y0, y1, y2))), min(h - 1, int(max(y0, y1, y2))) + 1):
            for px in range(max(0, int(min(x0, x1, x2))), min(w - 1, int(max(x0, x1, x2))) + 1):
                a = ((y1 - y2) * (px + .5 - x2) + (x2 - x1) * (py + .5 - y2)) / den; b = ((y2 - y0) * (px + .5 - x2) + (x0 - x2) * (py + .5 - y2)) / den; c = 1 - a - b
                if a < -1e-4 or b < -1e-4 or c < -1e-4: continue
                z = a * z0 + b * z1 + c * z2
                if z <= zb[py][px]: continue
                zb[py][px] = z
                n = [a * ns[0][k] + b * ns[1][k] + c * ns[2][k] for k in range(3)]; nl = math.sqrt(sum(m * m for m in n)) or 1.0
                col = light(sample(a * cs[0][6] + b * cs[1][6] + c * cs[2][6], a * cs[0][7] + b * cs[1][7] + c * cs[2][7]), [m / nl for m in n])
                img[py][3 * px:3 * px + 3] = bytes(int(m * 255) for m in col)
    if pitch == 0:                # the ground plane (y = 0), where it is in the frame
        gy = int(round(h / 2 + cy * S))
        for px in range(w):
            if 0 <= gy < h and zb[gy][px] < -1e17: put(img, px, gy, (110, 116, 130))
    return img


# a 3x5 pixel font for the labels
FONT = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./-:_ ', (
    '010101111101101', '110101110101110', '011100100100011', '110101101101110', '111100110100111', '111100110100100',
    '011100101101011', '101101111101101', '111010010010111', '001001001101010', '101101110101101', '100100100100111',
    '101111111101101', '110101101101101', '010101101101010', '110101110100100', '010101101110011', '110101110101101',
    '011100010001110', '111010010010010', '101101101101111', '101101101101010', '101101111111101', '101101010101101',
    '101101010010010', '111001010100111', '111101101101111', '010110010010111', '110001010100111', '110001010001110',
    '101101111001001', '111100110001110', '011100111101111', '111001010010010', '111101111101111', '111101111001110',
    '000000000000010', '001001010100100', '000000111000000', '000010000010000', '000000000000111', '000000000000000')))


def text(img, x, y, s, c=(220, 224, 232), k=2):
    for ch in s.upper():
        bits = FONT.get(ch, FONT[' '])
        for r in range(5):
            for cc in range(3):
                if bits[r * 3 + cc] == '1':
                    for dy in range(k):
                        for dx in range(k): put(img, x + cc * k + dx, y + r * k + dy, c)
        x += 4 * k


def scale_bar(img, S, w, h):
    for L in (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10):
        if 50 <= L * S <= 140: break
    x0, y0 = 12, h - 14; n = int(L * S)
    for px in range(x0, x0 + n + 1):
        for dy in (0, 1): put(img, px, y0 + dy, (220, 224, 232))
    for dy in range(-4, 2): put(img, x0, y0 + dy, (220, 224, 232)); put(img, x0 + n, y0 + dy, (220, 224, 232))
    text(img, x0 + n + 8, y0 - 6, ('%g cm' % (L * 100)) if L < 1 else ('%g m' % L))


def write_png(path, img):
    w, h = len(img[0]) // 3, len(img)
    raw = b''.join(b'\x00' + bytes(row) for row in img)
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


# ---- the six views, one scale for all of them
P, N = posed(CLIP, PHASE)
# one scale per pair of views that share an axis, so they compare directly: the two 3/4s, side with top (the length), front
# with rear (the width and height). A single scale for all six left a long, low animal a sliver from the front.
PAIRS = {'front34': 0, 'rear34': 0, 'side': 1, 'top': 1, 'front': 2, 'rear': 2}
SC = {}
for _, fname, yaw, pitch in VIEWS:
    q = [projector(yaw, pitch)(p) for p in P]
    ex = max(a[0] for a in q) - min(a[0] for a in q); ey = max(a[1] for a in q) - min(a[1] for a in q)
    k = PAIRS[fname]; SC[k] = min(SC.get(k, 1e18), 0.86 * TW / max(ex, 1e-9), 0.80 * TH / max(ey, 1e-9))
os.makedirs(os.path.join(OUT, 'views'), exist_ok=True)
HEAD = 30
sheet = new_img(3 * TW, 2 * TH + HEAD, (30, 32, 38))
title = '%s  %s' % (A.get('name') or os.path.splitext(os.path.basename(D))[0],
                    ('clip %s phase %.2f' % (CLIP, PHASE)) if CLIP else 'bind pose')
text(sheet, 10, 9, ''.join(ch for ch in title if ch.upper() in FONT))
for k, (label, fname, yaw, pitch) in enumerate(VIEWS):
    S = SC[PAIRS[fname]]
    img = render(P, N, yaw, pitch, S, TW, TH)
    text(img, 10, 10, label); scale_bar(img, S, TW, TH)
    write_png(os.path.join(OUT, 'views', fname + '.png'), img)
    ox, oy = (k % 3) * TW, HEAD + (k // 3) * TH
    for r in range(TH): sheet[oy + r][3 * ox:3 * (ox + TW)] = img[r]
    for r in range(TH): put(sheet, ox, oy + r, (30, 32, 38))
    for c in range(TW): put(sheet, ox + c, oy, (30, 32, 38))
write_png(os.path.join(OUT, 'sheet.png'), sheet)

# ---- the page: positions and normals baked per frame for every clip, so it plays exactly as skinned here
FRAMES = 24


def f32(vals): return base64.b64encode(struct.pack('<%df' % len(vals), *vals)).decode()


idx = [i for t in T for i in t]
if len(corners) > 65535: sys.exit('preview: more than 65535 corners')
clips = {}
for name in A.get('anims', {}):
    fp, fn = [], []
    for f in range(FRAMES):
        Pf, Nf = posed(name, f / FRAMES); fp += [c for p in Pf for c in p]; fn += [c for n in Nf for c in n]
    clips[name] = {'d': A['anims'][name].get('d', 1.0), 'p': f32(fp), 'n': f32(fn)}
P0, N0 = posed(None, 0)
data = {'name': A.get('name') or os.path.basename(D), 'frames': FRAMES, 'count': len(corners),
        'bind': {'p': f32([c for p in P0 for c in p]), 'n': f32([c for n in N0 for c in n])},
        'uv': f32([c for co in corners for c in co[6:8]]), 'idx': base64.b64encode(struct.pack('<%dH' % len(idx), *idx)).decode(),
        'clips': clips, 'views': [[lab, yaw, pitch] for lab, _, yaw, pitch in VIEWS],
        'tex': 'data:image/png;base64,' + (base64.b64encode(open(TEX, 'rb').read()).decode() if TEX else '')}
page = open(os.path.join(here, 'preview_page.html'), encoding='utf-8').read()
page = page.replace('__TITLE__', data['name'].replace('<', '')).replace('__DATA__', json.dumps(data))
open(os.path.join(OUT, 'preview.html'), 'w', encoding='utf-8').write(page)
print('preview: %s | px/m 3/4 %.0f, side and top %.0f, front and rear %.0f | %d triangles | clips: %s' % (data['name'], SC[0], SC[1], SC[2], len(T), ', '.join(clips) or 'none'))
print('sheet: %s' % os.path.join(OUT, 'sheet.png'))
print('page: %s' % os.path.join(OUT, 'preview.html'))
