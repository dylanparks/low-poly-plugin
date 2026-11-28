"""Measure a humanoid model as an anthropometrist measures a person, and set each measure beside its target.
Usage: python -I body_measure.py <model.gltf> <measurements.json> [bones.json]
measurements.json: the targets in metres, grouped (heights, head, torso, arm, leg), each {name: {"median": m, ...}}, as
lowpoly-characters writes from a survey (ANSUR II's names). bones.json, optional: the rig's names when they differ from the
plugin's humanoid rig: {"head": "head", "arm": ["arm_L", "fore_L", "hand_L", "fingers_L"], "leg": ["thigh_L", "shin_L",
"foot_L", "toe_L"]}. The bind pose is measured (an A- or T-pose is fine: the arm is measured along its own axis).
How each is taken, from the skin (the clothes' surface: a model is measured over its clothes, so its girths run a little
over the body's):
  - a girth is the convex outline of a slice through the skin (a tape measure's path), its breadth and depth the slice's
    width and depth; the torso and legs are sliced level, the arm square to its own axis;
  - heights are each landmark's height above the ground (the lowest skin point);
  - lengths along the arm run from its joints and its fingertip.
Prints one row per measure: target, model, the difference in percent, and a flag past +-6% (girths over clothes allow +8%).
Standard library only."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, json, math, os, struct, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
from lowpoly import gltf_io, rig_parts  # noqa: E402

A, _ = gltf_io.read_gltf(sys.argv[1]); T_ = json.load(open(sys.argv[2], encoding='utf-8'))
BN = {'head': 'head', 'neck': 'neck', 'arm': ['arm_L', 'fore_L', 'hand_L', 'fingers_L'], 'leg': ['thigh_L', 'shin_L', 'foot_L', 'toe_L']}
if len(sys.argv) > 3: BN.update(json.load(open(sys.argv[3], encoding='utf-8')))
names = A['bones']; J = rig_parts.joints(A); JB = lambda n: J[names.index(n)]
C, T, base = [], [], 0
for s in A['subs']:
    raw = base64.b64decode(s['v']); n = len(raw) // 64
    C += [struct.unpack_from('<16f', raw, k * 64) for k in range(n)]
    ix = struct.unpack('<%dH' % (len(base64.b64decode(s['i'])) // 2), base64.b64decode(s['i']))
    T += [tuple(base + i for i in ix[k:k + 3]) for k in range(0, len(ix), 3)]; base += n
P = [c[:3] for c in C]
# the skin is measured, not what rests on it: keep the largest connected piece (separate pieces such as hair, a thumb
# built as its own piece, teeth or armour are left out, as a tape measure goes under them)
_k = lambda i: (round(P[i][0], 4), round(P[i][1], 4), round(P[i][2], 4))
_par = {}
def _f(a):
    while _par.get(a, a) != a: a = _par[a]
    return a
for t in T:
    for i in t[1:]: _par[_f(_k(i))] = _f(_k(t[0]))
from collections import Counter as _Counter
_main = _Counter(_f(_k(t[0])) for t in T).most_common(1)[0][0]
T = [t for t in T if _f(_k(t[0])) == _main]
y0 = min(P[i][1] for t in T for i in t)
WS = [{int(round(c[12 + j])): c[8 + j] for j in range(4) if c[8 + j] > 0} for c in C]


def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a):
    l = math.sqrt(dot(a, a)) or 1.0; return tuple(x / l for x in a)
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def share(i, bones):
    ids = {names.index(b) for b in bones if b in names}; return sum(w for b, w in WS[i].items() if b in ids)


def subtree(b):
    out = {names.index(b)}
    for k in range(len(names)):
        if A['parent'][k] is not None and A['parent'][k] in out: out.add(k)
    return {names[k] for k in out}


def slice_pts(o, n, keep=lambda tri: True):
    """the points where the skin crosses the plane through o with normal n"""
    pts = []
    for t in T:
        if not keep(t): continue
        d = [dot(sub(P[i], o), n) for i in t]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (d[a] < 0) != (d[b] < 0):
                f = d[a] / (d[a] - d[b]); pts.append(tuple(P[t[a]][k] + f * (P[t[b]][k] - P[t[a]][k]) for k in range(3)))
    return pts


def hull(pts2):
    pts2 = sorted(set((round(x, 6), round(y, 6)) for x, y in pts2))
    if len(pts2) < 3: return pts2
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0: h.pop()
            h.append(p)
        return h
    lo, hi = half(pts2), half(pts2[::-1]); return lo[:-1] + hi[:-1]


def girth(pts, e1, e2, o):
    if len(pts) < 3: return None
    q = [(dot(sub(p, o), e1), dot(sub(p, o), e2)) for p in pts]; hl = hull(q)
    per = sum(math.dist(hl[k], hl[(k + 1) % len(hl)]) for k in range(len(hl)))
    return per, max(a for a, _ in q) - min(a for a, _ in q), max(b for _, b in q) - min(b for _, b in q)


X, Y, Z = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
arm_b, leg_b = BN['arm'], BN['leg']
arm_side = set().union(*(subtree(b) for b in arm_b[:1])) | {b.replace('_L', '_R') for b in subtree(arm_b[0])}
not_arm = lambda t: all(share(i, arm_side) < 0.5 for i in t)
left_leg = lambda t: sum(P[i][0] for i in t) > 0 and not_arm(t)   # the left leg's side of the midline (the slice keeps x > 0)


def level(h, keep=not_arm, side=None):
    pts = [p for p in slice_pts((0, y0 + h, 0), Y, keep) if side is None or (p[0] > 0) == (side > 0)]
    return girth(pts, X, Z, (0, 0, 0))


def best(hs, fn, pick=max, k=0):
    vals = [(v[k], v) for v in (fn(h) for h in hs) if v]
    return pick(vals)[1] if vals else None


M = {}                                                    # name -> (model value, how)
H = max(P[i][1] for t in T for i in t) - y0
M['stature'] = (H, 'the highest skin point')
g = T_['heights']; tg = lambda grp, k: T_[grp][k]['median']
# the torso, level slices at the survey's own heights (arms left out)
for nm, hk, grp in (('chest', 'chestheight', 'torso'), ('waist', 'waistheightomphalion', 'torso')):
    r = level(tg('heights', hk))
    if r: M[nm + 'circumference'], M[nm + 'breadth'], M[nm + 'depth'] = (r[0], 'level at %s' % hk), (r[1], 'level'), (r[2], 'level')
r = level(tg('heights', 'trochanterionheight'))
if r: M['hipbreadth'] = (r[1], 'level at the trochanter (both thighs)')
r = best([tg('heights', 'buttockheight') + d for d in (-0.03, -0.015, 0, 0.015, 0.03)], level)
if r: M['buttockcircumference'], M['buttockdepth'] = (r[0], 'the largest level girth round the buttocks'), (r[2], 'its depth')
M['neckcircumferencebase'] = (None, 'not measured: taken round the base of the neck on a tilt, over the trapezius')
hd = BN['head']; hj = JB(hd)
r = best([hj[1] - y0 - 0.04 + 0.01 * k for k in range(4)], level, min)
if r: M['neckcircumference'] = (r[0], 'the narrowest level girth of the neck')
# the head: its girth over the brow, its length and breadth, the face's breadth at the cheekbones
_skin = {i for t in T for i in t}
head_v = [i for i in range(len(P)) if share(i, subtree(hd)) >= 0.5 and i in _skin]
hy = [P[i][1] for i in head_v]
r = best([max(hy) - y0 - 0.02 - 0.01 * k for k in range(6)], lambda h: level(h, lambda t: all(i in set(head_v) for i in t)))   # above the ears (euryon)
if r: M['headcircumference'], M['headlength'], M['headbreadth'] = (r[0], 'the largest level girth of the head'), (r[2], 'its depth'), (r[1], 'its width')
face = set(i for i in head_v if P[i][2] > 0.0)               # the face's half: the ears behind it are not the cheekbones
r = best([max(hy) - y0 - 0.10 - 0.01 * k for k in range(5)], lambda h: level(h, lambda t: all(i in face for i in t)), max, 1)
if r: M['bizygomaticbreadth'] = (r[1], 'the widest level slice of the face below the eyes')
chin = min(hy); M['mentonsellionlength'] = (None, 'not measured (needs the nasion marked)')
# the shoulders: across the joints' outer skin; the deltoids at their widest (in the bind pose, along each arm)
sh = JB(arm_b[0]); el = JB(arm_b[1]); wr = JB(arm_b[2]); kn = JB(arm_b[3])
ax = norm(sub(el, sh))
arm_v = [i for i in range(len(P)) if share(i, subtree(arm_b[0])) >= 0.5 and P[i][0] > 0]
tip = max(arm_v, key=lambda i: dot(sub(P[i], sh), ax))
up = norm(cross(Z, ax)) if abs(ax[2]) < 0.9 else X
thumb = {b for b in names if b.startswith('thumb')}
def arm_slice(s, keep=lambda t: any(share(i, subtree(arm_b[0])) >= 0.5 for i in t) and all(P[i][0] > 0 for i in t)
              and all(share(i, thumb) < 0.5 for i in t)):     # the thumb is not round the palm
    o = tuple(sh[k] + ax[k] * s for k in range(3)); return girth(slice_pts(o, ax, keep), Z, norm(cross(ax, Z)), o)
outer = max(arm_v, key=lambda i: dot(sub(P[i], sh), norm(cross(Z, ax)) if ax[1] < 0 else up) if dot(sub(P[i], sh), ax) < 0.06 else -9)
M['biacromialbreadth'] = (2 * (sh[0] + 0.02), 'twice the shoulder joint\'s offset plus 2 cm to the acromion')
LA, LF = math.dist(sh, el), math.dist(el, wr)
M['shoulderelbowlength'] = (LA + 0.06, 'shoulder joint to elbow joint + 6 cm (acromion above, olecranon below)')
M['forearmhandlength'] = (dot(sub(P[tip], el), ax) + 0.03, 'elbow joint to the fingertip + 3 cm (the olecranon)')
M['radialestylionlength'] = (LF, 'elbow joint to wrist joint')
M['handlength'] = (dot(sub(P[tip], wr), ax), 'wrist joint to the fingertip')
for nm, lo, hi, pick in (('bicepscircumferenceflexed', 0.07, LA - 0.04, max), ('forearmcircumferenceflexed', LA + 0.04, LA + LF * 0.6, max),
                         ('wristcircumference', LA + LF - 0.02, LA + LF + 0.01, min)):
    r = best([lo + (hi - lo) * k / 8 for k in range(9)], arm_slice, pick)
    if r: M[nm] = (r[0], 'square to the arm, the %s girth' % ('largest' if pick is max else 'smallest'))
r = best([LA + LF + 0.03 + 0.01 * k for k in range(5)], arm_slice, max)
if r: M['handcircumference'], M['handbreadth'] = (r[0], 'the palm\'s largest girth'), (max(r[1], r[2]), 'its width')
# the legs: level slices of the left leg
for nm, hs, pick in (('thighcircumference', [tg('heights', 'crotchheight') - 0.02 - 0.01 * k for k in range(4)], max),
                     ('lowerthighcircumference', [tg('heights', 'kneeheightmidpatella') + 0.07 + 0.01 * k for k in range(4)], min),
                     ('calfcircumference', [0.26 + 0.02 * k for k in range(9)], max),
                     ('anklecircumference', [tg('heights', 'lateralmalleolusheight') + 0.03 + 0.01 * k for k in range(6)], min)):
    r = best(hs, lambda h: level(h, left_leg, side=1), pick)
    if r: M[nm] = (r[0], 'level, the left leg\'s %s girth' % ('largest' if pick is max else 'smallest'))
foot_v = [i for i in range(len(P)) if share(i, subtree(leg_b[2])) >= 0.5 and P[i][0] > 0]
if foot_v:
    M['footlength'] = (max(P[i][2] for i in foot_v) - min(P[i][2] for i in foot_v), 'the boot\'s length heel to toe')
    M['footbreadthhorizontal'] = (max(P[i][0] for i in foot_v) - min(P[i][0] for i in foot_v), 'its width')
for nm, (grp, key) in {'crotchheight': ('heights', 'crotchheight')}.items(): pass
crotch = [p for p in P if abs(p[0]) < 0.004 and p[1] < 1.0 * H * 0.6]
if crotch: M['crotchheight'] = (min(p[1] for p in crotch if p[1] > 0.3 * H) - y0, 'the lowest midline skin above the knees')

print('== %s: %d measures against %s' % (A.get('name'), len([v for v in M.values() if v[0] is not None]), T_.get('source', sys.argv[2])))
print('| measure | target (median, 5-95%%) | model | difference | how |\n|---|---|---|---|---|')
worst = 0.0; rows = []
for grp in ('heights', 'head', 'torso', 'arm', 'leg'):
    for k, d in T_.get(grp, {}).items():
        if k not in M or M[k][0] is None: continue
        v, how = M[k]; diff = 100 * (v - d['median']) / d['median']
        lim = 8.0 if 'circumference' in k else 6.0
        flag = ' **over**' if diff > lim else (' **under**' if diff < -6.0 else '')
        if flag: worst = max(worst, abs(diff))
        rows.append(abs(diff))
        print('| %s | %.3f (%.3f-%.3f) | %.3f | %+.1f%%%s | %s |' % (k, d['median'], d['p5'], d['p95'], v, diff, flag, how))
print('body: %d measures, median difference %.1f%%, %d past the limits, worst %.1f%%' % (
    len(rows), sorted(rows)[len(rows) // 2] if rows else 0, sum(1 for r in rows if r > 6), worst))
