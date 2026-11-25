"""Render the front part of an animal the way the viewer shows it: smooth vertex normals, the viewer's lights (a white sky and a bluish
ground at 1.2, a sun at 1.6) and a bilinear texture, from any yaw and pitch. A flat-lit render (head_textured.py) hides a whole class of
faults that only the real lighting shows: an upward-facing surface lit to white, a strip that glows, a texture sampled at one fixed
coordinate and so streaked. Standard library only; only reads the viewer's files.
Usage: python -I lit_view.py <model.gltf> <out.png> <animal id> <yaw degrees> <pitch degrees> [front fraction of length, or - for the rig's head (default)] [clip phase]
  yaw 0 looks at the animal's left side, nose to the left; 90 looks at it from the front; pitch is positive looking down.
  With a clip name and a phase (0..1) the animal is skinned in that frame."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 6 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, math, os, struct, sys, zlib, base64

D, OUT, AID = sys.argv[1:4]
YAW, PITCH = math.radians(float(sys.argv[4])), math.radians(float(sys.argv[5]))
FRAC_GIVEN = len(sys.argv) > 6 and sys.argv[6] != '-'
FRAC = float(sys.argv[6]) if FRAC_GIVEN else 0.16
CLIP, PHASE = (sys.argv[7], float(sys.argv[8])) if len(sys.argv) > 8 else (None, 0.0)
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
A, V, T = g['A'], g['V'], g['T']
corners = []
for s in A['subs']:
    raw = base64.b64decode(s['v'])
    for k in range(0, len(raw), 64): corners.append(struct.unpack_from('<8f', raw, k))      # position, normal, uv
tw, th, tex = read_png(g['texpath']())
P0 = [v[0] for v in V]; ys = [p[1] for p in P0]; zs = [p[2] for p in P0]
lo, H, zmax, zmin = min(ys), max(ys) - min(ys), max(zs), min(zs)
# the head from the rig (lowpoly/rig_parts.py), or from the height rule when the rig shows none or a fraction was given
from lowpoly import rig_parts
_R = rig_parts.parts(A, V); sel = None if FRAC_GIVEN else rig_parts.head_triangles(_R, T)
HEAD_RULE = ('rig: ' + _R['head']['rule']) if sel else 'height: the front %.0f%% of the length above 40%% of the height' % (100 * FRAC)
if not sel: sel = [t for t in T if all(P0[i][2] > zmax - FRAC * (zmax - zmin) and P0[i][1] > lo + 0.40 * H for i in t)]
if not sel: sys.exit('lit_view: nothing selected (%s); give a front fraction' % HEAD_RULE)
P = g['skin'](g['world'](g['pose_at'](g['clip'](CLIP), PHASE))) if CLIP else P0
pts = [P[i] for t in sel for i in t]
cen = [(min(q[k] for q in pts) + max(q[k] for q in pts)) / 2 for k in range(3)]
span = max(max(q[k] for q in pts) - min(q[k] for q in pts) for k in range(3))
Wd, Ht = 900, 640; S = 0.62 * min(Wd, Ht) / span
cy, sy, cp, sp = math.cos(YAW), math.sin(YAW), math.cos(PITCH), math.sin(PITCH)


def proj(p):     # the animal's x is its left, z its front; at yaw 0 the camera is on its left looking right, the nose at the image's left
    x, y, z = p[0] - cen[0], p[1] - cen[1], p[2] - cen[2]
    X = -(z * cy - x * sy); d = z * sy + x * cy
    return X, y * cp - d * sp, d * cp + y * sp


sun = (3, 6, -4); l = math.sqrt(sum(c * c for c in sun)); sun = tuple(c / l for c in sun)
ground = (0x44 / 255, 0x50 / 255, 0x66 / 255)


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


def sample(u, v):                 # bilinear, like the viewer's texture
    x = u * tw - 0.5; y = v * th - 0.5; x0, y0 = math.floor(x), math.floor(y); fx, fy = x - x0, y - y0
    def at(i, j): return tex[min(th - 1, max(0, j))][min(tw - 1, max(0, i))]
    return [((at(x0, y0)[k] * (1 - fx) + at(x0 + 1, y0)[k] * fx) * (1 - fy) + (at(x0, y0 + 1)[k] * (1 - fx) + at(x0 + 1, y0 + 1)[k] * fx) * fy) / 255 for k in range(3)]


img = [[(40, 42, 48)] * Wd for _ in range(Ht)]; zb = [[-1e9] * Wd for _ in range(Ht)]
for t in sel:
    cs = [corners[i] for i in t]; q = [proj(P[i]) for i in t]
    sc = [(Wd / 2 + a[0] * S, Ht / 2 - a[1] * S, a[2]) for a in q]
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = sc
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-9: continue
    for py in range(max(0, int(min(y0, y1, y2))), min(Ht - 1, int(max(y0, y1, y2))) + 1):
        for px in range(max(0, int(min(x0, x1, x2))), min(Wd - 1, int(max(x0, x1, x2))) + 1):
            a = ((y1 - y2) * (px + .5 - x2) + (x2 - x1) * (py + .5 - y2)) / den; b = ((y2 - y0) * (px + .5 - x2) + (x0 - x2) * (py + .5 - y2)) / den; c = 1 - a - b
            if a < -1e-4 or b < -1e-4 or c < -1e-4: continue
            z = a * z0 + b * z1 + c * z2
            if z <= zb[py][px]: continue
            zb[py][px] = z
            n = [a * cs[0][3 + k] + b * cs[1][3 + k] + c * cs[2][3 + k] for k in range(3)]; nl = math.sqrt(sum(m * m for m in n)) or 1.0
            col = light(sample(a * cs[0][6] + b * cs[1][6] + c * cs[2][6], a * cs[0][7] + b * cs[1][7] + c * cs[2][7]), [m / nl for m in n])
            img[py][px] = tuple(int(m * 255) for m in col)
raw = b''.join(b'\x00' + bytes(v for p in row for v in p) for row in img)
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', Wd, Ht, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
print('%s (%s) -> %s' % (A['name'], HEAD_RULE, OUT))
