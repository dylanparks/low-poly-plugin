"""Measure the model against its references, part by part: an overlay that gives numbers, not an impression.
In the agent trial a builder reported "the overlay lines the body up closely" while its pincers were a club instead of an
elbowed arm and its legs reached two thirds as far as the reference's: an overlay looked at, not measured. Corrections given
as a direction then overshot both ways. This reads landmarks marked once on each reference (refs.json), finds the same
landmarks on the model from its rig, aligns the two on landmarks you name, and prints every landmark's error and every traced
outline's worst gap, in metres and as a share of the aligned span, flagging each one over the skill's 5%.

Usage: python -I measure_overlay.py <model.gltf> <refs.json> <out dir> [threshold %=5]

refs.json: {"refs": [ ... ]}. Entries without "landmarks" are skipped (they can still carry the licence and notes). Per entry:
  "file"        the image, relative to refs.json. PNG is drawn under the overlay; any other format is measured the same,
                drawn on a plain background (the tools read downloads in an isolated interpreter, without image libraries),
                and shown over the photo in overlay.html.
  "species"     what the image shows. Say when it stands in for the modelled species ("Crocodylus palustris, a stand-in"):
                every row measured on it is labelled with it.
  "view"        side | top | front | rear.
  "part"        optional: the special part the reference shows (head, wing, foot); lp check's refs.parts looks for it.
  "measured"    optional, instead of landmarks: ratios read by eye off a photo that could not be downloaded, e.g.
                {"shoulder_over_head": [1.0, 1.25]}, with the photo's address in "source". They are not overlaid, but they
                count as covering the view for lp check's refs.views, and the builder checks the model against them.
  "facing"      side: left | right (where the nose points). top: up | down | left | right. Default left (side), up (top).
                The animal's own left lands on the image's right in a front view, on its left in a rear view, toward the camera
                in a side view facing left, and on the image's left in a top view facing up.
                The error columns are the model's landmark minus the reference's, in the animal's own directions:
                forward + means the model's point is ahead of the photo's, up + above it, left + further toward the
                animal's own left (whatever side of the image that is).
  "pose"        what the animal is doing (standing, walking, perched, flying...). Only compare like with like.
  "use"         "measure-only" for a file whose licence doesn't allow more (lowpoly-core/references/measuring.md, "Filling gaps"):
                its rows are labelled, as a reminder that it never enters the model.
  "landmarks"   {"name": [x px, y px], ...}, names from the list below or ones the entry defines under "model_landmarks".
  "align"       [name, name]: two landmarks that fix the scale and position (default nose and tail_tip, else the two
                landmarks furthest apart). The errors are shares of the span between them on the model.
  "rotate"      true when the subject is tilted in the frame (a head turned, a skeleton laid at an angle): the align
                landmarks fix the rotation as well as the scale and position (ground_y is then ignored).
  "ground_y"    side, front and rear: the image row of the ground. With it the model stands on that row (vertical position
                from the ground, not from the align landmarks).
  "px_per_m"    when the image has a scale bar: also report the model's size against the real one.
  "outline"     traced edges, as lists of [x, y] points. Side, front and rear views: "top" and "bottom" (the top line and the
                underline). Top view: "left" and "right" (the animal's own sides). Each point is compared with the model's
                silhouette at the same station.
  "model_landmarks"  {"name": {"bone": "bone name"}} (that bone's joint) or {"name": [x, y, z]} in metres: landmarks the rig
                can't name, like an eye or a crest.
Landmark names found on the model from the rig (lowpoly/rig_parts.py), in the bind pose:
  nose, head_top, head_back, jaw_low        the head's skin: its front, top, back and lowest points
  back_top, belly                           the highest and lowest points of the body's skin (not the head, limbs or tail)
  tail_base, tail_tip                       the tail's first joint and its rearmost point (a tail: the chain holding the
                                            model's rearmost skin, up to the bone whose parent carries limbs)
  <limb>_top, _knee, _ankle, _toe, _heel   per limb: the first joint with skin (hip or shoulder), the next (knee or elbow),
                                            the ankle (or wrist), and the foot's front and back points at the ground
  Limbs are named by side and order: fore and hind when there are two pairs, leg when one, leg1..legN from the front when
  more; L and R are the animal's own left and right ("L_hind_knee"). In a side view a name without L_ or R_ means the side
  facing the camera (the left when the nose points left).
Writes <out>/overlay.md and overlay.json (the tables), <out>/overlay_<n>.png per reference (the photo when it is a PNG, the
model's silhouette, the traced outlines, each landmark pair joined by a line, red over the threshold), and overlay.html
(the same over the photo, any format). Standard library only."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 4 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, contextlib, io, json, math, os, struct, sys, zlib

D, REFS, OUT = sys.argv[1:4]
LIMIT = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('def lum')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, '-']
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
A, V, T = g['A'], g['V'], g['T']
from lowpoly import rig_parts                                   # noqa: E402  (rig_study put lib/ on the path)
R = rig_parts.parts(A, V); names = A['bones']; J = rig_parts.joints(A)
P = [v[0] for v in V]; own = R['owner']


def fail(msg): sys.exit('measure_overlay: ' + msg)


# ---- the model's landmarks, from the rig
def pts_of(bones): return [P[c] for c in range(len(P)) if own[c] in bones]


LM, LM_HOW = {}, {}
head_b = R['head']['bones'] if R['head'] else set()
limb_b = set().union(*(l['bones'] for l in R['limbs'])) if R['limbs'] else set()
nb = len(names)
def parent(i): p = A['parent'][i]; return p if p is not None and p >= 0 and p != i else None
kids = {i: [k for k in range(nb) if parent(k) == i] for i in range(nb)}
def sub(i):
    out = [i]
    for k in kids[i]: out += sub(k)
    return out
if head_b:
    hp = pts_of(head_b)
    for nm, f in (('nose', lambda p: p[2]), ('head_top', lambda p: p[1]), ('head_back', lambda p: -p[2]), ('jaw_low', lambda p: -p[1])):
        LM[nm] = max(hp, key=f); LM_HOW[nm] = 'head skin (%s)' % R['head']['rule']
# the tail: the chain holding the rearmost skin outside the head and limbs, up to the bone whose parent carries limbs
rest_c = [c for c in range(len(P)) if own[c] is not None and own[c] not in head_b and own[c] not in limb_b]
tail_b = set()
if rest_c:
    c0 = min(rest_c, key=lambda c: P[c][2]); b = own[c0]
    roots = {l['root'] for l in R['limbs']}
    while parent(b) is not None and not (set(sub(parent(b))) & roots) and parent(b) not in head_b: b = parent(b)
    if not set(sub(b)) & roots and b not in head_b and len(sub(b)) < nb:
        tail_b = set(sub(b)); LM['tail_base'] = J[b]; LM['tail_tip'] = P[c0]
        LM_HOW['tail_base'] = 'joint of %s' % names[b]; LM_HOW['tail_tip'] = 'rearmost skin'
body = [P[c] for c in rest_c if own[c] not in tail_b]
if body:
    LM['back_top'] = max(body, key=lambda p: p[1]); LM['belly'] = min(body, key=lambda p: p[1])
    LM_HOW['back_top'] = LM_HOW['belly'] = 'body skin'
# limbs: by side, front to back
for side, tag in ((1, 'L'), (-1, 'R')):
    ls = sorted([l for l in R['limbs'] if l['side'] == side], key=lambda l: -J[l['root']][2])
    lab = ['fore', 'hind'] if len(ls) == 2 else ['leg'] if len(ls) == 1 else ['leg%d' % (k + 1) for k in range(len(ls))]
    for l, nm in zip(ls, lab):
        chain, i = [l['root']], l['root']
        while i != l['ankle'] and kids[i]:
            i = next((k for k in kids[i] if l['ankle'] in sub(k)), None)
            if i is None: break
            chain.append(i)
        top = next((b for b in chain if any(own[c] == b for c in range(len(P)))), chain[0])
        k = chain.index(top)
        p = '%s_%s' % (tag, nm)
        LM[p + '_top'] = J[top]; LM_HOW[p + '_top'] = 'joint of %s' % names[top]
        if k + 1 < len(chain) and chain[k + 1] != l['ankle']:
            LM[p + '_knee'] = J[chain[k + 1]]; LM_HOW[p + '_knee'] = 'joint of %s' % names[chain[k + 1]]
        LM[p + '_ankle'] = J[l['ankle']]; LM_HOW[p + '_ankle'] = 'joint of %s' % names[l['ankle']]
        fp = pts_of(l['foot_bones'])
        if fp:
            low = min(q[1] for q in fp); sole = [q for q in fp if q[1] < low + 0.03 * R['height']] or fp
            LM[p + '_toe'] = max(sole, key=lambda q: q[2]); LM[p + '_heel'] = min(sole, key=lambda q: q[2])
            LM_HOW[p + '_toe'] = LM_HOW[p + '_heel'] = 'foot skin at the ground'

# ---- views: model (x, y, z; x the animal's left, z forward) to image directions
SIDE_F = {'left': ((-1, 0), (0, -1)), 'right': ((1, 0), (0, -1))}                     # forward, up
TOP_F = {'up': ((0, -1), (-1, 0)), 'down': ((0, 1), (1, 0)), 'left': ((-1, 0), (0, 1)), 'right': ((1, 0), (0, -1))}   # forward, left


def basis(view, facing):
    """the image directions of the model's x, y and z (unit scale)"""
    if view == 'side':
        f, u = SIDE_F[facing or 'left']; return (0, 0), (u[0], u[1]), f          # x is depth: not drawn
    if view == 'top':
        f, l = TOP_F[facing or 'up']; return l, (0, 0), f
    if view == 'front': return (1, 0), (0, -1), (0, 0)
    if view == 'rear': return (-1, 0), (0, -1), (0, 0)
    fail('unknown view %r (side, top, front or rear)' % view)


def resolve(name, view, facing):
    """a reference's landmark name to the model's: a side view's unprefixed limb name means the side facing the camera"""
    if name in LM: return name
    if view == 'side':
        near = 'L' if (facing or 'left') == 'left' else 'R'
        if near + '_' + name in LM: return near + '_' + name
    return None


def image_size(path):
    b = open(path, 'rb').read(65536 * 4)
    if b[:8] == b'\x89PNG\r\n\x1a\n': return struct.unpack('>II', b[16:24])
    if b[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF: i += 1; continue
            m = b[i + 1]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack('>HH', b[i + 5:i + 9]); return w, h
            i += 2 + struct.unpack('>H', b[i + 2:i + 4])[0]
    return None


# ---- drawing (a tiny rasteriser and a 3x5 font)
FONT = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./-:_%+ ', (
    '010101111101101', '110101110101110', '011100100100011', '110101101101110', '111100110100111', '111100110100100',
    '011100101101011', '101101111101101', '111010010010111', '001001001101010', '101101110101101', '100100100100111',
    '101111111101101', '110101101101101', '010101101101010', '110101110100100', '010101101110011', '110101110101101',
    '011100010001110', '111010010010010', '101101101101111', '101101101101010', '101101111111101', '101101010101101',
    '101101010010010', '111001010100111', '111101101101111', '010110010010111', '110001010100111', '110001010001110',
    '101101111001001', '111100110001110', '011100111101111', '111001010010010', '111101111101111', '111101111001110',
    '000000000000010', '001001010100100', '000000111000000', '000010000010000', '000000000000111', '101001010100101',
    '000010111010000', '000000000000000')))


class Img:
    def __init__(s, w, h, bg=(34, 36, 42)): s.w, s.h = w, h; s.px = [bytearray(bytes(bg) * w) for _ in range(h)]
    def put(s, x, y, c, a=1.0):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            if a >= 1: s.px[y][3 * x:3 * x + 3] = bytes(c)
            else:
                o = s.px[y][3 * x:3 * x + 3]; s.px[y][3 * x:3 * x + 3] = bytes(int(o[k] * (1 - a) + c[k] * a) for k in range(3))
    def line(s, a, b, c, wdt=1):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for k in range(n + 1):
            t = k / n; x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for dx in range(-(wdt // 2), wdt - wdt // 2):
                for dy in range(-(wdt // 2), wdt - wdt // 2): s.put(x + dx, y + dy, c)
    def tri(s, p, c, a):
        (x0, y0), (x1, y1), (x2, y2) = p
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9: return
        for py in range(max(0, int(min(y0, y1, y2))), min(s.h - 1, int(max(y0, y1, y2))) + 1):
            for px in range(max(0, int(min(x0, x1, x2))), min(s.w - 1, int(max(x0, x1, x2))) + 1):
                u = ((y1 - y2) * (px + .5 - x2) + (x2 - x1) * (py + .5 - y2)) / den; v = ((y2 - y0) * (px + .5 - x2) + (x0 - x2) * (py + .5 - y2)) / den
                if u >= 0 and v >= 0 and u + v <= 1 and not s.mask[py][px]: s.mask[py][px] = 1; s.put(px, py, c, a)
    def text(s, x, y, t, c=(235, 238, 245), k=2):
        for ch in str(t).upper():
            bits = FONT.get(ch, FONT[' '])
            for r in range(5):
                for cc in range(3):
                    if bits[r * 3 + cc] == '1':
                        for dy in range(k):
                            for dx in range(k): s.put(x + cc * k + dx, y + r * k + dy, c)
            x += 4 * k
    def png(s, path):
        raw = b''.join(b'\x00' + bytes(r) for r in s.px)
        def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', s.w, s.h, 8, 2, 0, 0, 0))
                               + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


# ---- measure each reference
try: cfg = json.load(open(REFS, encoding='utf-8'))
except Exception as e: fail('could not read %s: %s' % (REFS, e))
entries = cfg.get('refs', cfg if isinstance(cfg, list) else [])
base = os.path.dirname(os.path.abspath(REFS))
os.makedirs(OUT, exist_ok=True)
report, md, html = [], ['# Overlay: %s' % A.get('name', os.path.basename(D)), '',
                        'Errors are the model minus the reference, in metres on the model and as a share of the aligned span; '
                        'rows over %g%% are marked **over**. Landmarks on the model are read from the rig.' % LIMIT, ''], []
skipped = []
for n, e in enumerate(entries):
    if not e.get('landmarks'): skipped.append(e.get('file', '#%d' % n)); continue
    view, facing = e.get('view', 'side'), e.get('facing')
    if view == 'top' and facing and facing not in TOP_F: fail('%s: facing %r in a top view (up, down, left or right)' % (e.get('file'), facing))
    bx, by, bz = basis(view, facing)
    lm = dict(LM)
    for k, v in (e.get('model_landmarks') or {}).items():
        if isinstance(v, dict) and 'bone' in v:
            if v['bone'] not in names: fail('%s: model_landmarks %s: no bone %r' % (e.get('file'), k, v['bone']))
            lm[k] = J[names.index(v['bone'])]; LM_HOW[k] = 'joint of %s (refs.json)' % v['bone']
        else: lm[k] = tuple(v); LM_HOW[k] = 'given in refs.json'
    LM.update(lm)
    def m2(p): return (p[0] * bx[0] + p[1] * by[0] + p[2] * bz[0], p[0] * bx[1] + p[1] * by[1] + p[2] * bz[1])
    pairs, unknown = {}, []
    for k, xy in e['landmarks'].items():
        r = resolve(k, view, facing)
        if r: pairs[k] = (r, tuple(xy))
        else: unknown.append(k)
    if len(pairs) < 2 and not (len(pairs) == 1 and e.get('ground_y') is not None): fail('%s: fewer than two landmarks the model has (unknown: %s; the model has: %s)' % (e.get('file'), ', '.join(unknown) or 'none', ', '.join(sorted(LM))))
    al = e.get('align') or (['nose', 'tail_tip'] if all(k in pairs for k in ('nose', 'tail_tip')) else None)
    if not al:
        ks = list(pairs); al = max(((a, b) for a in ks for b in ks if a < b), key=lambda ab: math.dist(pairs[ab[0]][1], pairs[ab[1]][1]))
    for k in al:
        if k not in pairs: fail('%s: align landmark %r is not marked on this reference, or the model has no such landmark' % (e.get('file'), k))
    (ra, ia), (rb, ib) = pairs[al[0]], pairs[al[1]]
    ma, mb = m2(LM[ra]), m2(LM[rb]); span_m = math.dist(ma, mb)
    if span_m < 1e-9: fail('%s: the align landmarks coincide on the model' % e.get('file'))
    S = math.dist(ia, ib) / span_m                               # px per model metre
    # "rotate": a reference whose subject is tilted (a head turned in the frame): the two align landmarks also fix the angle
    th = (math.atan2(ib[1] - ia[1], ib[0] - ia[0]) - math.atan2(mb[1] - ma[1], mb[0] - ma[0])) if e.get('rotate') else 0.0
    ct, st = math.cos(th), math.sin(th)
    def rot(q): return (q[0] * ct - q[1] * st, q[0] * st + q[1] * ct)
    ra, rb = rot(ma), rot(mb)
    tx = (ia[0] + ib[0]) / 2 - S * (ra[0] + rb[0]) / 2; ty = (ia[1] + ib[1]) / 2 - S * (ra[1] + rb[1]) / 2
    if e.get('ground_y') is not None and view in ('side', 'front', 'rear') and not e.get('rotate'): ty = float(e['ground_y'])   # y = 0 on the ground row
    def toimg(p): q = rot(m2(p)); return (tx + S * q[0], ty + S * q[1])
    basis_txt = (e.get('species') or 'species not recorded') + ('; measure-only' if e.get('use') == 'measure-only' else '')
    rows = []
    for k, (r, xy) in pairs.items():
        mp = toimg(LM[r]); ex, ey = (mp[0] - xy[0]) / S, (mp[1] - xy[1]) / S
        dx, dy = ex * ct + ey * st, -ex * st + ey * ct            # back into the model's own directions when rotated
        # in the animal's terms: forward and up (side), left and forward (top), left and up (front, rear)
        if view == 'side': f = SIDE_F[facing or 'left'][0]; a1, a2 = ('forward', dx * f[0] + dy * f[1]), ('up', -dy)
        elif view == 'top': f, l = TOP_F[facing or 'up']; a1, a2 = ('forward', dx * f[0] + dy * f[1]), ('left', dx * l[0] + dy * l[1])
        else: a1, a2 = ('left', dx if view == 'front' else -dx), ('up', -dy)
        d = math.hypot(dx, dy); pct = 100 * d / span_m
        rows.append({'landmark': k, 'model_landmark': r, 'ref_px': xy, 'model_px': [round(mp[0], 1), round(mp[1], 1)],
                     'error_m': round(d, 4), 'error_pct': round(pct, 1), a1[0] + '_m': round(a1[1], 4), a2[0] + '_m': round(a2[1], 4),
                     'aligned': k in al, 'over': pct > LIMIT and k not in al, 'found_by': LM_HOW.get(r, '')})
    # outlines: the model's silhouette at each traced point's station
    proj = [toimg(p) for p in P]
    def extent(axis, at):
        """the silhouette's min and max along the other image axis at image coordinate `at` on `axis` (0 = x, 1 = y)"""
        lo_, hi_ = None, None
        for t in T:
            q = [proj[i] for i in t]
            for a, b in ((0, 1), (1, 2), (2, 0)):
                if (q[a][axis] - at) * (q[b][axis] - at) <= 0 and q[a][axis] != q[b][axis]:
                    s_ = (at - q[a][axis]) / (q[b][axis] - q[a][axis]); o = q[a][1 - axis] + s_ * (q[b][1 - axis] - q[a][1 - axis])
                    lo_ = o if lo_ is None or o < lo_ else lo_; hi_ = o if hi_ is None or o > hi_ else hi_
        return lo_, hi_
    outl = []
    for edge, pts in (e.get('outline') or {}).items():
        if view == 'top':
            if edge not in ('left', 'right'): fail('%s: a top view traces "left" and "right" edges, not %r' % (e.get('file'), edge))
            l = TOP_F[facing or 'up'][1]; axis = 1 if l[1] == 0 else 0          # stations run along the body
            want_min = (l[0] < 0 or l[1] < 0) == (edge == 'left')
        else:
            if edge not in ('top', 'bottom'): fail('%s: a %s view traces "top" and "bottom" edges, not %r' % (e.get('file'), view, edge))
            axis = 0; want_min = edge == 'top'
        gaps = []
        for xy in pts:
            lo_, hi_ = extent(axis, xy[axis])
            if lo_ is None: gaps.append((xy, None)); continue
            m = lo_ if want_min else hi_
            out_ = (xy[1 - axis] - m) if want_min else (m - xy[1 - axis])     # positive: the model stands outside the trace
            gaps.append((xy, out_ / S))
        meas = [gp for gp in gaps if gp[1] is not None]
        if not meas: continue
        worst = max(meas, key=lambda gp: abs(gp[1]))
        outl.append({'edge': edge, 'points': len(pts), 'missed': len(pts) - len(meas),
                     'mean_abs_m': round(sum(abs(gp[1]) for gp in meas) / len(meas), 4), 'worst_m': round(worst[1], 4),
                     'worst_pct': round(100 * abs(worst[1]) / span_m, 1), 'worst_at_px': worst[0],
                     'over': 100 * abs(worst[1]) / span_m > LIMIT, 'gaps_m': [None if gp[1] is None else round(gp[1], 4) for gp in gaps]})
    size = None
    if e.get('px_per_m'):
        real = math.dist(ia, ib) / float(e['px_per_m']); size = {'model_m': round(span_m, 4), 'reference_m': round(real, 4), 'ratio': round(span_m / real, 3)}
    rec = {'file': e.get('file'), 'species': basis_txt, 'use': e.get('use'), 'view': view, 'facing': facing, 'pose': e.get('pose'), 'align': list(al),
           'span_m': round(span_m, 4), 'px_per_model_m': round(S, 2), 'landmarks': rows, 'outline': outl, 'unknown_landmarks': unknown,
           'size': size}
    report.append(rec)
    # the tables
    md += ['## %d. %s (%s view%s%s)' % (n, e.get('file'), view, ', facing ' + facing if facing else '', ', ' + e['pose'] if e.get('pose') else ''),
           '', 'Reference shows: %s. Aligned on %s and %s (%.3f m on the model).' % (basis_txt, al[0], al[1], span_m), '']
    if size: md += ['Size: the model spans %.3f m where the reference\'s scale bar gives %.3f m (model %.0f%% of real).' % (size['model_m'], size['reference_m'], 100 * size['ratio']), '']
    ax = [k for k in rows[0] if k.endswith('_m') and k != 'error_m'] if rows else []
    md += ['| Landmark | Error | %s | %s | Found on the model by |' % (ax[0].replace('_m', ' (m)'), ax[1].replace('_m', ' (m)')) if ax else '', '|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: -r['error_pct']):
        md.append('| %s%s | %s%.3f m, %.1f%% | %+.3f | %+.3f | %s |' % (r['landmark'], ' (aligned)' if r['aligned'] else '', '**over** ' if r['over'] else '',
                                                               r['error_m'], r['error_pct'], r[ax[0]], r[ax[1]], r['found_by']))
    if outl:
        md += ['', '| Outline | Points | Mean gap | Worst gap (+ the model outside the trace) |', '|---|---|---|---|']
        for o in outl:
            md.append('| %s | %d%s | %.3f m | %s%+.3f m, %.1f%% at px %s |' % (o['edge'], o['points'], ' (%d off the model)' % o['missed'] if o['missed'] else '',
                                                                      o['mean_abs_m'], '**over** ' if o['over'] else '', o['worst_m'], o['worst_pct'], list(o['worst_at_px'])))
    if unknown: md += ['', 'Not on the model (name them under "model_landmarks"): %s' % ', '.join(unknown)]
    md.append('')
    # the picture: photo (PNG) or a plain background, the silhouette, outlines, landmark pairs
    path = os.path.join(base, e.get('file', ''))
    wh = image_size(path) if os.path.isfile(path) else None
    W0, H0 = wh or (int(max(p[0] for p in proj) + 40), int(max(p[1] for p in proj) + 40))
    k = min(1.0, 1400 / W0); W1, H1 = max(1, int(W0 * k)), max(1, int(H0 * k))
    img = Img(W1, H1); img.mask = [bytearray(W1) for _ in range(H1)]
    if wh and open(path, 'rb').read(8) == b'\x89PNG\r\n\x1a\n':
        pw, ph, rows_ = read_png(path)
        for y in range(H1):
            for x in range(W1):
                c = rows_[min(ph - 1, int(y / k))][min(pw - 1, int(x / k))]; img.px[y][3 * x:3 * x + 3] = bytes(int(v * 0.75) for v in c[:3])
    for t in T: img.tri([(proj[i][0] * k, proj[i][1] * k) for i in t], (255, 150, 60), 0.35)
    for o in (e.get('outline') or {}).values():
        for a, b in zip(o, o[1:]): img.line((a[0] * k, a[1] * k), (b[0] * k, b[1] * k), (90, 220, 255), 2)
    for idx, r in enumerate(sorted(rows, key=lambda r: r['landmark'])):
        a = (r['ref_px'][0] * k, r['ref_px'][1] * k); b = (r['model_px'][0] * k, r['model_px'][1] * k)
        img.line(a, b, (255, 70, 70) if r['over'] else (240, 240, 240), 2)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 9: img.put(a[0] + dx, a[1] + dy, (90, 220, 255))
        for d in range(-4, 5): img.put(b[0] + d, b[1] + d, (255, 150, 60)); img.put(b[0] + d, b[1] - d, (255, 150, 60))
        img.text(a[0] + 6, a[1] - 12, r['landmark'], (90, 220, 255) if not r['over'] else (255, 120, 120))
    img.text(10, 10, '%s  %s view  span %.2f m  blue ref  orange model' % (os.path.basename(e.get('file', '')), view, span_m))
    pn = os.path.join(OUT, 'overlay_%d.png' % n); img.png(pn); rec['picture'] = pn
    # the page: the same marks as SVG over the photo, whatever its format
    if wh:
        mime = 'image/png' if path.lower().endswith('.png') else 'image/jpeg' if path.lower().endswith(('.jpg', '.jpeg')) else 'image/webp'
        data = base64.b64encode(open(path, 'rb').read()).decode()
        sil = ''.join('<polygon points="%s"/>' % ' '.join('%.1f,%.1f' % proj[i] for i in t) for t in T)
        lines = ''.join('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s"/><circle cx="%g" cy="%g" r="5" fill="#5adcff"/><text x="%g" y="%g">%s %.1f%%</text>'
                        % (r['ref_px'][0], r['ref_px'][1], r['model_px'][0], r['model_px'][1], '#ff4646' if r['over'] else '#fff',
                           r['ref_px'][0], r['ref_px'][1], r['ref_px'][0] + 8, r['ref_px'][1] - 8, r['landmark'], r['error_pct']) for r in rows)
        trace = ''.join('<polyline points="%s"/>' % ' '.join('%g,%g' % tuple(p) for p in o) for o in (e.get('outline') or {}).values())
        html.append('<h2>%d. %s</h2><p>%s view. Reference shows: %s.</p><svg viewBox="0 0 %d %d" width="100%%"><image href="data:%s;base64,%s" width="%d" height="%d"/>'
                    '<g fill="#ff9640" opacity=".4" stroke="none">%s</g><g fill="none" stroke="#5adcff" stroke-width="3">%s</g>'
                    '<g stroke-width="3" font-size="%d" fill="#fff" style="paint-order:stroke" stroke-linejoin="round">%s</g></svg>'
                    % (n, e.get('file'), view, basis_txt, W0, H0, mime, data, W0, H0, sil, trace, max(12, W0 // 70), lines))

if skipped: md += ['References without landmarks (not measured): %s' % ', '.join(skipped), '']
md += ['## Landmarks the model has', '', ', '.join('%s (%s)' % (k, LM_HOW.get(k, '')) for k in sorted(LM)), '']
open(os.path.join(OUT, 'overlay.md'), 'w', encoding='utf-8').write('\n'.join(md))
json.dump({'model': A.get('name'), 'threshold_pct': LIMIT, 'refs': report, 'model_landmarks': {k: [round(c, 4) for c in v] for k, v in LM.items()},
           'skipped': skipped}, open(os.path.join(OUT, 'overlay.json'), 'w', encoding='utf-8'), indent=1)
open(os.path.join(OUT, 'overlay.html'), 'w', encoding='utf-8').write(
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>Overlay</title><style>body{background:#22242a;color:#e8eaef;font:14px/1.5 system-ui,sans-serif;margin:0 16px 40px;max-width:1200px}'
    'svg{background:#000;display:block;margin:8px 0 24px}text{font-family:system-ui,sans-serif}</style></head><body><h1>Overlay: %s</h1>%s</body></html>'
    % (str(A.get('name', '')).replace('<', ''), ''.join(html) or '<p>No reference image could be read.</p>'))
n_lm = sum(len(r['landmarks']) for r in report); over = [(r['file'], x['landmark'], x['error_pct']) for r in report for x in r['landmarks'] if x['over']]
over_o = [(r['file'], o['edge'], o['worst_pct']) for r in report for o in r['outline'] if o['over']]
worst_lm = max((x['error_pct'] for r in report for x in r['landmarks'] if not x['aligned']), default=0.0)
worst_ol = max((o['worst_pct'] for r in report for o in r['outline']), default=0.0)
print('\n'.join(md))
print('overlay: %d references, %d landmarks (%d over %g%%), %d outlines (%d over) | worst landmark %.1f%%, worst outline %.1f%%'
      % (len(report), n_lm, len(over), LIMIT, sum(len(r['outline']) for r in report), len(over_o), worst_lm, worst_ol))
