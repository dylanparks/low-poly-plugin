"""How alive a model's clips are: what an animator checks by eye, measured from the rig. A clip can pass every crossing,
balance and joint check and still read as robotic: every joint on one timing curve, the head nailed in space, the feet
nailed to the floor, the weight never moving, mirrored limbs moving as one, stretches where nothing moves at all.
Usage: python -I motion_quality.py <model.gltf|.glb> [clip ...] [--kinds kinds.json] [--detail]
  kinds.json, optional: {"clip name": "idle|gait|action"}; otherwise a clip's kind is read from its name (stand, idle,
  breathe, rest, sleep, sit: idle; walk, run, trot, gallop, canter, jog, sprint, fly, swim, crawl: gait; anything else:
  action). --detail lists every moving bone's range, peak time and lag.
The legs, arms and head are read from the rig (lowpoly/rig_parts.py), not from bone names. Each clip is sampled 60 times a
second (at least 48 samples) and posed as the viewer poses it. Per clip:
  - moving: a bone that carries skin and turns more than 2 degrees over the clip; static: one that turns less than 0.5 (the
    helper bones that only translate, and bones without skin, are left out);
  - sync: each moving bone has a fastest moment, the time its turning speed peaks; sync is the share of those bones
    whose peak falls within 12 ms of three or more others'. A high share means the clip runs on
    one timing curve: nothing leads, nothing follows. Real movement runs from the centre out, each segment 20-60 ms after
    the one before. A gait's legs are left out: the stride times them;
  - order: along each chain from the pelvis to a hand (and to the head), the share of adjacent pairs (peaking within a
    quarter of a second of each other: one move) where the outer bone peaks at or after the inner one;
  - head: how far the head's joint travels and how far the head turns in the world, against the upper trunk's turn. A
    head that neither travels nor turns while the trunk turns is locked; real heads are steadier than the trunk, not fixed;
  - mass: the travel of the skin's mean point (a centre-of-mass proxy) sideways, up and down, and fore and aft;
  - feet: each ankle's travel and each foot's turn about the vertical; in an action clip, feet that neither travel nor
    turn are nailed. slide: the furthest a foot's lowest joint moves over the ground while it is down (within 0.6% of the
    height of its lowest point), not counted in a gait, which runs in place;
  - hold: the longest stretch in which no bone turns faster than 2 degrees a second and nothing translates (a dead hold);
  - twin: for each left-right pair of limbs, how alike their mirrored motion is (1: mirror images moving as one);
  - loop: for a clip whose last pose matches its first, the jump in speed across the join;
  - gait clips also: the pelvis's turn about the vertical (yaw), its side tilt (roll) and its pitch range; the upper
    trunk's yaw against the pelvis's (counter-rotation: negative correlation); the head's pitch range against the trunk's.
Ends with one line per clip that lp check reads:
  clip <name> [<kind>]: sync <share> | order <share> | static <share> | head <travel %H> <turn deg> trunk <turn deg> |
      mass <x> <y> <z> %H | feet <travel %H> <turn deg> | hold <s> | twin <worst> | loop <jump> | pelvis <yaw> <roll> deg |
      counter <corr> | headpitch <head> <trunk> | slide <%H>
Standard library only."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 2 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, json, math, os, re, struct, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
from lowpoly import gltf_io, rig_parts  # noqa: E402
from lowpoly.spring_bake import decode_clip, sample, qmul, qrot, qconj  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
DETAIL = '--detail' in sys.argv
KINDS = {}
if '--kinds' in sys.argv:
    KINDS = json.load(open(sys.argv[sys.argv.index('--kinds') + 1], encoding='utf-8'))
    args = [a for a in args if a != sys.argv[sys.argv.index('--kinds') + 1]]
A, _ = gltf_io.read_gltf(args[0]); want = args[1:]
names = A['bones']; nb = len(names); par = A['parent']
C = []
for s in A['subs']:
    raw = base64.b64decode(s['v']); C += [struct.unpack_from('<16f', raw, k * 64) for k in range(len(raw) // 64)]
WS = [[(int(round(c[12 + j])), c[8 + j]) for j in range(4) if c[8 + j] > 0] for c in C]
R = rig_parts.parts(A, [(c[:3], w) for c, w in zip(C, WS)])
H = R['height']
if not A.get('anims'): print('== %s: no clips; nothing measured' % A.get('name')); sys.exit(0)
J0 = rig_parts.joints(A)
parent = lambda i: par[i] if par[i] is not None and par[i] >= 0 and par[i] != i else None
kids = {i: [k for k in range(nb) if parent(k) == i] for i in range(nb)}


def sub(i):
    out = [i]
    for k in kids[i]: out += sub(k)
    return out


def anc(i):
    out = []
    while parent(i) is not None: i = parent(i); out.append(i)
    return out


skinw = [0.0] * nb
for ws in WS:
    for b, w in ws: skinw[b] += w
legs = R['limbs']; leg_bones = set().union(*(L['bones'] for L in legs)) if legs else set()
head = R['head']['bone'] if R['head'] else None
# arms: side branches off the midline with four or more bones that are not legs (as leg_bend_study reads them)
arms = []
for b in range(nb):
    p = parent(b)
    if p is None or b in leg_bones or abs(J0[b][0]) < 0.01 * H or abs(J0[p][0]) >= 0.01 * H: continue
    if len(sub(b)) >= 4: arms.append(b)
# a hand (the third bone down an arm and everything under it) and a foot (the ankle's bone and under it) each move as a unit
hand_of = {}
for a in arms:
    c_, i_ = [a], a
    while kids[i_]:
        i_ = max(kids[i_], key=lambda k: max(math.dist(J0[b], J0[a]) for b in sub(k))); c_.append(i_)
    if len(c_) >= 3:
        for b in sub(c_[2]): hand_of[b] = c_[2]
for L in legs:
    lowj = min(sub(L['ankle']), key=lambda b: J0[b][1]); top = lowj if parent(lowj) in (None, L['ankle']) or lowj == L['ankle'] else parent(lowj)
    for b in sub(top): hand_of[b] = top
    L['foot'] = top; L['low'] = lowj
# the pelvis: the legs' common parent (else the rig's root); the upper trunk: the last bone the head and the arms share
def midline_above(b):
    p = parent(b)
    while p is not None and abs(J0[p][0]) >= 0.01 * H: p = parent(p)
    return 0 if p is None else p


# a four-legged rig hangs its legs from two bones: the pelvis is the one nearer the root (the hind legs'), and the upper
# trunk is the other (the front legs', the chest), when the head hangs from it
girdles = sorted({midline_above(L['root']) for L in legs}, key=lambda b: len(anc(b)))
pelvis = girdles[0] if girdles else 0
roots_up = [head] if head is not None else []
roots_up += arms
if not arms and len(girdles) > 1 and (head is None or girdles[-1] in anc(head)):
    trunk = girdles[-1]
elif roots_up:
    common = None
    for a in [roots_up[0]] + anc(roots_up[0]):
        if all(a == r or a in anc(r) for r in roots_up): common = a; break
    trunk = common if common is not None else pelvis
else: trunk = pelvis
# a helper: a leaf bone whose clips only translate it (a muscle's belly), or a bone with no skin
inv = [(tuple(A['inv'][i * 7:i * 7 + 4]), tuple(A['inv'][i * 7 + 4:i * 7 + 7])) for i in range(nb)]
r0 = [tuple(A['rest'][i * 7:i * 7 + 4]) for i in range(nb)]; p0 = [tuple(A['rest'][i * 7 + 4:i * 7 + 7]) for i in range(nb)]


def world(rots, poss):
    W = [None] * nb
    for i in range(nb):
        q, p = rots[i], poss[i]; pi = parent(i)
        if pi is None: W[i] = (q, p)
        else:
            pq, pp = W[pi]; W[i] = (qmul(pq, q), tuple(a + b for a, b in zip(pp, qrot(pq, p))))
    return W


def qangle(a, b):
    """the angle between two orientations, degrees"""
    d = abs(sum(x * y for x, y in zip(a, b))); return math.degrees(2 * math.acos(max(-1.0, min(1.0, d))))


def rotvec(q, ref):
    """the rotation from ref to q as an axis times its angle (radians)"""
    d = qmul(qconj(ref), q)
    if d[3] < 0: d = tuple(-x for x in d)
    s_ = math.sqrt(max(0.0, 1 - d[3] * d[3])); ang = 2 * math.atan2(s_, d[3])
    return (0.0, 0.0, 0.0) if s_ < 1e-9 else tuple(x / s_ * ang for x in d[:3])


def yaw_roll_pitch(q):
    """a bone's world turn about the vertical, its side tilt and its pitch, degrees, from where its axes point"""
    f = qrot(q, (0.0, 0.0, 1.0)); u = qrot(q, (0.0, 1.0, 0.0)); r = qrot(q, (1.0, 0.0, 0.0))
    return (math.degrees(math.atan2(f[0], f[2])), math.degrees(math.asin(max(-1, min(1, r[1])))),
            math.degrees(math.asin(max(-1, min(1, -f[1])))))


def kind_of(name):
    if name in KINDS: return KINDS[name]
    n = name.lower()
    if re.search(r'stand|idle|breath|rest|sleep|sit|graze|perch|hover|spar|guard|stance|ready', n): return 'idle'
    if re.search(r'walk|run|trot|gallop|canter|jog|sprint|fly|flap|glide|swim|crawl|slither|stalk|prowl', n): return 'gait'
    return 'action'


def lag_of(a, b, dt, loop):
    """the lag (seconds, positive: b after a) at which two signals' cross-correlation is strongest in size, and that
    correlation; searched over a quarter of the clip either way"""
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    a = [x - ma for x in a]; b = [x - mb for x in b]
    na = math.sqrt(sum(x * x for x in a)); nb_ = math.sqrt(sum(x * x for x in b))
    if na < 1e-9 or nb_ < 1e-9: return 0.0, 0.0
    best = (0.0, 0, 0.0)
    for k in range(-(n // 4), n // 4 + 1):
        if loop: c = sum(a[i] * b[(i + k) % n] for i in range(n))
        else: c = sum(a[i] * b[i + k] for i in range(max(0, -k), min(n, n - k)))
        c /= na * nb_
        if abs(c) > best[0] + 1e-9 or (abs(abs(c) - best[0]) <= 1e-9 and abs(k) < abs(best[1])): best = (abs(c), k, c)
    return best[1] * dt, best[2]


def corr(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa > 1e-9 and sb > 1e-9 else 0.0


def main_signal(vecs):
    """a bone's turning as one signal: its rotation vectors' component along the axis they vary most about"""
    n = len(vecs); m = [sum(v[k] for v in vecs) / n for k in range(3)]
    d = [[v[k] - m[k] for k in range(3)] for v in vecs]
    cov = [[sum(x[i] * x[j] for x in d) for j in range(3)] for i in range(3)]
    ax = [1.0, 0.7, 0.4]
    for _ in range(24):                                       # power iteration: the first principal axis
        ax = [sum(cov[i][j] * ax[j] for j in range(3)) for i in range(3)]
        l = math.sqrt(sum(x * x for x in ax)) or 1.0; ax = [x / l for x in ax]
    return [sum(x[k] * ax[k] for k in range(3)) for x in d]


print('== %s: height %.2f m; pelvis %s, upper trunk %s, head %s, %d legs, %d arms' % (
    A.get('name'), H, names[pelvis], names[trunk], names[head] if head is not None else '-', len(legs), len(arms)))
lines = []
for clip, src in A['anims'].items():
    if want and clip not in want: continue
    keys = decode_clip(src, nb); dur = float(src.get('d', 1.0)) or 1.0
    n = max(96, int(round(dur * 120))); dt = dur / n
    fr = []                                                   # per sample: (local rotations, local positions, world)
    for f in range(n + 1):
        u = f / n
        rots = [sample(keys[i][0], u, 4) or r0[i] for i in range(nb)]
        poss = [sample(keys[i][1], u, 3) or p0[i] for i in range(nb)]
        fr.append((rots, poss, world(rots, poss)))
    loop = max(qangle(fr[0][0][i], fr[n][0][i]) for i in range(nb)) < 1.0 and \
        max(math.dist(fr[0][1][i], fr[n][1][i]) for i in range(nb)) < 0.002 * H
    F = fr[:n] if loop else fr                                # a loop's last sample repeats its first
    m = len(F); kind = kind_of(clip)
    rng = [max(qangle(F[0][0][i], F[f][0][i]) for f in range(m)) for i in range(nb)]
    trans = [max(math.dist(F[0][1][i], F[f][1][i]) for f in range(m)) for i in range(nb)]
    # a helper: a bone without skin, or a leaf that never turns and is only moved (a muscle's belly pressed into a fold)
    helper = [skinw[i] <= 0 or (not kids[i] and rng[i] < 0.01 and (trans[i] > 0 or len(keys[i][1]) > 1)) for i in range(nb)]
    body = [i for i in range(nb) if not helper[i]]
    moving = [i for i in body if rng[i] > 2.0]; static = [i for i in body if rng[i] < 0.5]
    # ---- sync and order: who peaks together at the clip's main event
    depth = lambda i: len(anc(i))
    def step(i, f): return qangle(F[f][0][i], F[(f + 1) % m][0][i]) / dt
    nf = m if loop else m - 1
    sp_b = {i: [step(i, f) for f in range(nf)] for i in moving}
    def smooth3(xs):
        k = len(xs); g = (lambda j: xs[j % k]) if loop else (lambda j: xs[max(0, min(k - 1, j))])
        return [(g(j - 1) + 2 * g(j) + g(j + 1)) / 4 for j in range(k)]
    sp_b = {i: smooth3(smooth3(v)) for i, v in sp_b.items()}
    pool_ = [i for i in moving if not (kind == 'gait' and i in leg_bones)]
    peaks = {}
    for i in pool_:                                           # each bone's own fastest moment, to a fraction of a sample
        v = sp_b[i]; j = max(range(nf), key=lambda q: v[q])
        y0, y1, y2 = v[(j - 1) % nf] if loop or j > 0 else v[j], v[j], v[(j + 1) % nf] if loop or j < nf - 1 else v[j]
        den = y0 - 2 * y1 + y2; off = 0.5 * (y0 - y2) / den if abs(den) > 1e-12 else 0.0
        peaks[i] = (j + max(-1.0, min(1.0, off))) * dt
    period = nf * dt
    def apart(x, y):
        d = abs(x - y); return min(d, period - d) if loop else d
    # a hand's digits close together and a foot's toes bend together: each hand or foot counts once, at its own bone
    unit = {}
    for i in peaks:
        u = i
        for a in [i] + anc(i):
            if a in hand_of: u = hand_of[a]; break
        unit.setdefault(u, []).append(peaks[i])
    upk = {u: v[0] if u in peaks and False else sum(v) / len(v) for u, v in unit.items()}
    crowd = sum(1 for i in upk if sum(1 for k in upk if k != i and apart(upk[k], upk[i]) <= 0.012) >= 3)
    sync = crowd / len(upk) if len(upk) >= 4 else float('nan')
    drv = pelvis if pelvis in peaks else (min(peaks, key=depth) if peaks else None)
    pairs = ok = 0
    for end in arms + ([head] if head is not None else []):
        tip = end
        while kids[tip] and end in arms: tip = max(kids[tip], key=lambda k: max(math.dist(J0[b], J0[end]) for b in sub(k)))
        chain = [b for b in reversed([tip] + anc(tip)) if b in peaks]
        for a_, b_ in zip(chain, chain[1:]):
            if apart(peaks[a_], peaks[b_]) > 0.25: continue    # their fastest moments belong to different moves
            d_ = peaks[b_] - peaks[a_]
            if loop and abs(d_) > period / 2: d_ -= math.copysign(period, d_)
            pairs += 1; ok += d_ >= -0.004
    order = ok / pairs if pairs >= 3 else float('nan')        # one or two pairs is too thin a basis
    lags = {i: (peaks[i], 1.0) for i in peaks}; pool = list(peaks)
    # ---- head against the upper trunk
    hd = (float('nan'),) * 3
    if head is not None:
        hp = [F[f][2][head][1] for f in range(m)]
        travel = max(math.dist(hp[0], p) for p in hp) / H * 100
        hturn = max(qangle(F[0][2][head][0], F[f][2][head][0]) for f in range(m))
        tturn = max(qangle(F[0][2][trunk][0], F[f][2][trunk][0]) for f in range(m))
        hd = (travel, hturn, tturn)
    # ---- the skin's mean point
    cm = []
    for f in range(m):
        W = F[f][2]; sx = sy = sz = 0.0
        for c, ws in zip(C, WS):
            p = c[:3]
            for b, w in ws:
                iq, ip = inv[b]; q = tuple(a + d for a, d in zip(qrot(iq, p), ip)); wq, wp = W[b]
                q = qrot(wq, q); sx += w * (q[0] + wp[0]); sy += w * (q[1] + wp[1]); sz += w * (q[2] + wp[2])
        cm.append((sx / len(C), sy / len(C), sz / len(C)))
    mass = tuple((max(p[k] for p in cm) - min(p[k] for p in cm)) / H * 100 for k in range(3))
    # ---- feet: the foot's joint (the ankle) travels, the lowest bone (the toes, flat on the ground) turns
    ft_travel = ft_turn = slide = 0.0
    for L in legs:
        ps = [F[f][2][L['foot']][1] for f in range(m)]
        ft_travel = max(ft_travel, max(math.dist(ps[0], q_) for q_ in ps) / H * 100)
        yw = [yaw_roll_pitch(F[f][2][L['low']][0])[0] for f in range(m)]
        ft_turn = max(ft_turn, max(abs((y - yw[0] + 180) % 360 - 180) for y in yw))
        if kind != 'gait':                                    # a gait runs in place: its feet are meant to travel
            gp = [F[f][2][L['low']][1] for f in range(m)]; y0 = min(q_[1] for q_ in gp); start = None
            for q_ in gp + [None]:
                if q_ is not None and q_[1] < y0 + 0.006 * H:
                    if start is None: start = q_
                    slide = max(slide, math.hypot(q_[0] - start[0], q_[2] - start[2]) / H * 100)
                else: start = None
    # ---- dead holds
    speed = []
    for f in range(m - (0 if loop else 1)):
        g = (f + 1) % m
        sp = max(max(qangle(F[f][0][i], F[g][0][i]) for i in body) / dt, max(math.dist(F[f][1][i], F[g][1][i]) for i in range(nb)) / dt / H * 500)
        speed.append(sp)
    run_ = best = 0
    for sp in speed + (speed if loop else []):
        run_ = run_ + 1 if sp < 2.0 else 0; best = max(best, run_)
    hold = min(best, len(speed)) * dt
    jump = float('nan')
    if loop and len(speed) > 3:
        pk = max(speed) or 1.0; jump = abs(speed[-1] - speed[0]) / pk
    # ---- twins: left and right limbs as mirror images
    twin = 0.0
    def mirror(v): return (v[0], -v[1], -v[2])
    for group in ((arms if kind != 'gait' else []), [L['root'] for L in legs] if kind != 'gait' else []):
        for a in group:
            for b in group:
                if J0[a][0] <= 0 or J0[b][0] >= 0 or parent(a) != parent(b): continue
                ca, cb = [a] + [k for k in sub(a) if k != a], [b] + [k for k in sub(b) if k != b]
                rs = []
                for x, y in zip(ca, cb):
                    if x not in moving and y not in moving: continue
                    vx = [rotvec(F[f][0][x], F[0][0][x]) for f in range(m)]
                    vy = [mirror(rotvec(F[f][0][y], F[0][0][y])) for f in range(m)]
                    sx_ = main_signal(vx); ax_ = [sum(v[k] for v in vy) / m for k in range(3)]
                    sy_ = main_signal(vy)
                    c_ = abs(corr(sx_, sy_)); amp = (max(sx_) - min(sx_)) or 1e-9; amp2 = (max(sy_) - min(sy_)) or 1e-9
                    rs.append(c_ * min(amp, amp2) / max(amp, amp2))
                if rs: twin = max(twin, sum(rs) / len(rs))
    # ---- gait: the pelvis and the counter-rotation
    py = [yaw_roll_pitch(F[f][2][pelvis][0]) for f in range(m)]; ty = [yaw_roll_pitch(F[f][2][trunk][0]) for f in range(m)]
    span = lambda xs: max(xs) - min(xs)
    pyaw, proll = span([p[0] for p in py]), span([p[1] for p in py])
    rel = [t[0] - p[0] for t, p in zip(ty, py)]
    counter = corr([p[0] for p in py], rel) if pyaw > 0.5 and span(rel) > 0.5 else float('nan')
    hpitch = span([yaw_roll_pitch(F[f][2][head][0])[2] for f in range(m)]) if head is not None else float('nan')
    tpitch = span([t[2] for t in ty])
    f2 = lambda v: 'nan' if v != v else '%.2f' % v
    print('clip %s [%s]%s, %.2f s: %d moving, %d static of %d bones with skin' % (clip, kind, ', loop' if loop else '', dur, len(moving), len(static), len(body)))
    if static: print('   static: %s' % ', '.join(names[i] for i in static))
    if drv is not None:
        print('   sync %s (%d of %d parts peak in a crowd of four within 12 ms); order %s' % (f2(sync), crowd, len(upk), f2(order)))
    if DETAIL:
        for i in sorted(moving, key=depth):
            print('      %-12s range %5.1f deg  peak %s' % (names[i], rng[i], ('%5.0f ms' % (peaks[i] * 1000)) if i in peaks else '(stride)'))
    print('   head travel %s %%H, turn %s deg; upper trunk turn %s deg; head pitch %s, trunk pitch %s' % (f2(hd[0]), f2(hd[1]), f2(hd[2]), f2(hpitch), f2(tpitch)))
    print('   mass: side %.2f, up %.2f, fore-aft %.2f %%H; feet: travel %.2f %%H, turn %.1f deg, slide %.2f %%H' % (mass + (ft_travel, ft_turn, slide)))
    print('   dead hold %.2f s; twin %.2f; loop jump %s; pelvis yaw %.1f roll %.1f deg; counter %s' % (hold, twin, f2(jump), pyaw, proll, f2(counter)))
    lines.append('clip %s [%s]: sync %s | order %s | static %.2f | head %s %s trunk %s | mass %.2f %.2f %.2f | feet %.2f %.1f | hold %.2f | twin %.2f | loop %s | pelvis %.1f %.1f | counter %s | headpitch %s %s | slide %.2f' % (
        clip, kind, f2(sync), f2(order), len(static) / max(1, len(body)), f2(hd[0]), f2(hd[1]), f2(hd[2]), mass[0], mass[1], mass[2], ft_travel, ft_turn, hold, twin, f2(jump), pyaw, proll, f2(counter), f2(hpitch), f2(tpitch), slide))
print()
for l in lines: print(l)
