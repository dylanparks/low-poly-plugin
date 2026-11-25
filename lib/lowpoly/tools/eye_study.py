"""How an animal's eye and the area round it are painted: the texture's zones from the pupil outward, measured in texels and in
millimetres on the model, so different models (and a photo) can be compared. Standard library only; reads the viewer's files.

Usage:
  python -I eye_study.py <model.gltf> locate <out dir> <animal id> [head fraction, or - for the rig's head (default)]
      Writes <id>_head.png: the head triangles' footprint in the texture, enlarged 6x, with a tick every 8 texels, to find the
      eye's texel position by eye.
  python -I eye_study.py <model.gltf> measure <out dir> <animal id> <eye u px> <eye v px> [eye half-width px] [half-height px]
      Measures round that texel (the radius is found from the dark core unless given): the dark core, the rim, the socket and the surround, as luminance and colour in rings at
      1x, 1.5x, 2x, 3x and 4x the eye's radius, and above, below, in front of and behind it. Writes <id>_eye.png (the eye
      area enlarged 10x). Distances in mm use the texture's density on the head (texels per metre along the head).
  python -I eye_study.py - photo <out dir> <name> <image.png> <eye x px> <eye y px> <eye radius px>
      The same rings measured on a photo (an 8-bit PNG); the radius is the eye's half-width in the photo's pixels."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, math, os, struct, sys, zlib

D, MODE, OUTD = sys.argv[1:4]
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])


def write_png(path, rows):
    h, w = len(rows), len(rows[0]); raw = bytearray()
    for r in rows:
        raw += b'\x00'
        for p in r: raw += bytes(max(0, min(255, int(c))) for c in p[:3])
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(bytes(raw), 9)) + ch(b'IEND', b''))


def lum(p): return (0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]) / 255


def sat(p):
    mx, mn = max(p[:3]), min(p[:3]); return 0.0 if mx == 0 else (mx - mn) / mx


def hue(p):
    r, g, b = (c / 255 for c in p[:3]); mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn: return None
    d = mx - mn
    h = (g - b) / d % 6 if mx == r else (b - r) / d + 2 if mx == g else (r - g) / d + 4
    return h * 60


def rings(get, cx, cy, r, px_mm, ry=None):
    """luminance, saturation and hue in rings round (cx, cy), and in four sectors at 1.5-2.5 radii"""
    ry = ry or r; k = ry / r                    # elliptical rings for an almond eye: distances in units of the eye's own radii
    dist = lambda dx, dy: math.hypot(dx, dy / k)
    out = []
    for lo, hi, name in ((0, 0.35, 'core'), (0.35, 0.8, 'eye body'), (0.8, 1.2, 'rim'), (1.2, 1.8, 'lid/socket'),
                         (1.8, 2.6, 'surround'), (2.6, 4.0, 'base coat')):
        ps = [get(cx + dx, cy + dy) for dy in range(-int(4 * r) - 1, int(4 * r) + 2) for dx in range(-int(4 * r) - 1, int(4 * r) + 2)
              if lo * r <= dist(dx, dy) < hi * r]
        ps = [p for p in ps if p is not None]
        if not ps: continue
        L = [lum(p) for p in ps]; m = sum(L) / len(L); sd = math.sqrt(sum((x - m) ** 2 for x in L) / len(L))
        hs = [h for h in (hue(p) for p in ps) if h is not None]
        out.append((name, lo, hi, m, sd, min(L), max(L), sum(sat(p) for p in ps) / len(ps), (sum(hs) / len(hs)) if hs else -1))
    sect = {}
    for name, (sx, sy) in (('above', (0, -1)), ('below', (0, 1)), ('front', (-1, 0)), ('behind', (1, 0))):
        ps = [get(cx + dx, cy + dy) for dy in range(-int(3 * r) - 1, int(3 * r) + 2) for dx in range(-int(3 * r) - 1, int(3 * r) + 2)
              if 1.5 * r <= dist(dx, dy) < 2.6 * r and (dx * sx + dy * sy / k) > 0.7 * dist(dx, dy)]
        ps = [p for p in ps if p is not None]
        if ps: sect[name] = (sum(lum(p) for p in ps) / len(ps), sum(sat(p) for p in ps) / len(ps))
    return out, sect


def report(title, out, sect, r, px_mm):
    print('== %s: eye radius %.1f px%s' % (title, r, ('' if not px_mm else ' = %.1f mm on the model' % (r / px_mm))))
    print('   %-11s %-10s %6s %6s %12s %6s %6s' % ('zone', 'radii', 'lum', 'sd', 'min..max', 'sat', 'hue'))
    for name, lo, hi, m, sd, mn, mx, s, h in out:
        print('   %-11s %4.2f-%-4.2f %6.2f %6.2f %5.2f..%-5.2f %6.2f %6.0f' % (name, lo, hi, m, sd, mn, mx, s, h))
    base = out[-1][3]
    print('   steps from the base coat (lum): ' + ', '.join('%s %+.2f' % (n, m - base) for n, _, _, m, *_ in out[:-1]))
    print('   sectors at 1.5-2.6 radii (lum, sat): ' + ', '.join('%s %.2f/%.2f' % (k, v[0], v[1]) for k, v in sect.items()))


if MODE == 'photo':
    name, img_path = sys.argv[4], sys.argv[5]; cx, cy, r = float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8])
    w, h, im = read_png(img_path)
    get = lambda x, y: tuple(im[int(y)][int(x)][:3]) if 0 <= int(x) < w and 0 <= int(y) < h else None
    out, sect = rings(get, cx, cy, r, None); report(name + ' (photo)', out, sect, r, None)
    sys.exit()

AID = sys.argv[4]
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; argv = sys.argv; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
sys.argv = argv
A, V, T = g['A'], g['V'], g['T']
uvs = []
for s in A['subs']:
    raw = base64.b64decode(s['v'])
    for k in range(0, len(raw), 64): uvs.append(struct.unpack_from('<2f', raw, k + 24))
tw, th, tex = read_png(g['texpath']())
FRAC_GIVEN = MODE == 'locate' and len(sys.argv) > 5 and sys.argv[5] != '-'
FRAC = float(sys.argv[5]) if FRAC_GIVEN else 0.25
P = [v[0] for v in V]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
lo, H, zmax, zmin = min(ys), max(ys) - min(ys), max(zs), min(zs)
# the head from the rig (lowpoly/rig_parts.py), or from the height rule when the rig shows none or a fraction was given
from lowpoly import rig_parts
_R = rig_parts.parts(A, V); head = None if FRAC_GIVEN else rig_parts.head_triangles(_R, T)
HEAD_RULE = ('rig: ' + _R['head']['rule']) if head else 'height: the front %.0f%% of the length above 40%% of the height' % (100 * FRAC)
if not head: head = [t for t in T if all(P[i][2] > zmax - FRAC * (zmax - zmin) and P[i][1] > lo + 0.40 * H for i in t)]
if not head: sys.exit('eye_study: no head triangles found (%s); give a head fraction in locate mode' % HEAD_RULE)
get = lambda x, y: tuple(tex[int(y) % th][int(x) % tw][:3])


def texel_density():
    """texels per metre on the head: total UV edge length over 3D edge length, over the head triangles"""
    uvl = sum(math.hypot((uvs[t[a]][0] - uvs[t[b]][0]) * tw, (uvs[t[a]][1] - uvs[t[b]][1]) * th) for t in head for a, b in ((0, 1), (1, 2), (2, 0)))
    l3 = sum(math.dist(P[t[a]], P[t[b]]) for t in head for a, b in ((0, 1), (1, 2), (2, 0)))
    return uvl / l3


def eye_density(cx, cy, reach):
    """texels per metre at the eye itself: the head triangles whose texture footprint comes within reach of the eye's texel.
    An eye often has its own, enlarged patch of the texture; the head's average then turns its texels into too many
    or too few millimetres (the red fox v2's eye patch: 614 texels/m against the head's 575)."""
    uvl = l3 = 0.0
    for t in head:
        q = [(uvs[i][0] * tw, uvs[i][1] * th) for i in t]
        if min(math.hypot(u - cx, v - cy) for u, v in q) > reach and not (min(u for u, _ in q) <= cx <= max(u for u, _ in q) and
                                                                           min(v for _, v in q) <= cy <= max(v for _, v in q)): continue
        for a, b in ((0, 1), (1, 2), (2, 0)):
            uvl += math.hypot(q[a][0] - q[b][0], q[a][1] - q[b][1]); l3 += math.dist(P[t[a]], P[t[b]])
    return uvl / l3 if l3 > 0 else None


if MODE == 'locate':
    us = [uvs[i][0] * tw for t in head for i in t]; vs = [uvs[i][1] * th for t in head for i in t]
    u0, u1, v0, v1 = max(0, int(min(us)) - 4), min(tw, int(max(us)) + 5), max(0, int(min(vs)) - 4), min(th, int(max(vs)) + 5)
    S = 6; rows = []
    for y in range(v0, v1):
        for _ in range(S):
            row = []
            for x in range(u0, u1):
                p = get(x, y); tick = (x % 8 == 0 or y % 8 == 0)
                row += [(255, 0, 255) if tick and _ == 0 else p] * S
            rows.append(row)
    path = os.path.join(OUTD, AID + '_head.png'); write_png(path, rows)
    print('%s: head footprint u %d..%d, v %d..%d (texture %dx%d), %.0f texels/m on the head -> %s' % (AID, u0, u1, v0, v1, tw, th, texel_density(), path))
else:
    cx, cy = float(sys.argv[5]), float(sys.argv[6])
    # the eye's radius: where the luminance, rising from the dark core, crosses halfway to the surround's
    core = lum(get(cx, cy)); sur = sum(lum(get(cx + 3 * math.cos(a), cy + 3 * math.sin(a))) for a in [k * math.pi / 8 for k in range(16)]) / 16
    rad = []
    for k in range(16):
        a = k * math.pi / 8
        for d10 in range(5, 120):
            d = d10 / 10
            if lum(get(cx + d * math.cos(a), cy + d * math.sin(a))) > core + 0.5 * (max(sur, core + 0.05) - core): rad.append(d); break
    rad.sort(); r = rad[len(rad) // 2] if rad else 2.0
    ry = None; SLIT = False
    # A slit pupil (a fox's, a cat's, a crocodile's) is a dark core much longer than it is wide: the crossing above finds the
    # slit, not the eye, and every ring then falls inside the iris (the red fox v2 read catchlight 0.41, socket 0 with a
    # 0.90 catchlight painted). Then the eye is the iris: follow each ray past the slit, across the iris, to where it darkens
    # into the lid line, and take the half-width and half-height from those edges.
    if len(rad) == 16 and rad[0] > 0 and rad[-1] / rad[0] >= 2.5:
        edge, cross = {}, {}
        for k in range(16):
            a = k * math.pi / 8; d0 = None
            for d10 in range(5, 160):
                d = d10 / 10
                if lum(get(cx + d * math.cos(a), cy + d * math.sin(a))) > core + 0.5 * (max(sur, core + 0.05) - core): d0 = d; break
            if d0 is None: continue
            cross[k] = d0
            iris = sorted(lum(get(cx + (d0 + q) * math.cos(a), cy + (d0 + q) * math.sin(a))) for q in (0.5, 1.0, 1.5, 2.0))[2]
            if abs(math.cos(a)) > 0.9:     # across the slit: the eye body must be an iris colour (a fox's amber), not white
                sats = sorted(sat(get(cx + (d0 + q) * math.cos(a), cy + (d0 + q) * math.sin(a))) for q in (0.5, 1.0, 1.5, 2.0))
                if sats[2] < 0.35 or iris < max(0.12, 3 * core): continue   # feathers or fur round a round pupil (a swan's lores)
            for d10 in range(int(10 * d0) + 15, 400):
                d = d10 / 10
                if lum(get(cx + d * math.cos(a), cy + d * math.sin(a))) < 0.55 * iris: edge[k] = d; break
        hz = sorted(edge[k] for k in edge if abs(math.cos(k * math.pi / 8)) > 0.9)
        # along the slit the rays run into the lid without crossing any iris: the slit spans the iris's height, so its own
        # length gives the half-height
        vt = sorted(cross[k] for k in cross if abs(math.sin(k * math.pi / 8)) > 0.9)
        if len(hz) >= 4 and vt and hz[-1] < 1.8 * hz[0]:   # an iris found on both sides of the slit, about as wide each way
            r, ry = hz[len(hz) // 2], vt[len(vt) // 2]; SLIT = True
            if ry >= r: ry = None
    if len(sys.argv) > 7: r = float(sys.argv[7]); ry = None       # the eye's half-width, read off the enlarged crop
    if len(sys.argv) > 8: ry = float(sys.argv[8])                 # and its half-height, for an almond eye
    pxm = eye_density(cx, cy, 2 * r) or texel_density()
    out, sect = rings(get, cx, cy, r, pxm / 1000, ry)
    report('%s (%s)' % (A['name'], AID), out, sect, r, pxm / 1000)
    print('   eye width %.1f texels; density at the eye %.0f texels/m (head %.0f); texture %dx%d%s' % (2 * r, pxm, texel_density(), tw, th,
          '; slit pupil: the radius is the iris edge%s' % ('' if ry is None else ', half-height %.1f px' % ry) if SLIT else ''))
    S, R = 10, int(5 * r) + 2
    rows = []
    for y in range(int(cy) - R, int(cy) + R + 1):
        for _ in range(S): rows.append([c for x in range(int(cx) - R, int(cx) + R + 1) for c in [get(x, y)] * S])
    write_png(os.path.join(OUTD, AID + '_eye.png'), rows)
