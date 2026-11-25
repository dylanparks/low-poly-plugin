"""Standing balance: in each standing clip, is the centre of mass over the feet? Standard library only.
The centre of mass is the closed skin's volume centroid (uniform density). The ground contact is every skin vertex within
1.2% of the animal's height of the frame's lowest point, among the feet's vertices when the rig shows feet (lowpoly/rig_parts.py:
the ankle down), so a tail tip resting on the ground is not a foot. For each frame, the margin is how far the centre of mass sits inside the contact's extent,
front to back and side to side, as a fraction of that extent's half-length: 1 = dead centre, 0 = on the edge, negative =
outside (the animal is falling). Each clip reports its worst frame.
Planted feet: in the same clips, each foot's sole (its vertices on the ground in the clip's first frame) must stay where it was
while it touches the ground. The slide is the largest horizontal move of a sole vertex from that spot, in any frame where it is
still within the contact band, in % of the animal's height: a foot lifted and set down again (a step) is anchored afresh where it
lands, so only drift while it stays down counts: a foot dragged by a parent
bone that breathes or sways does (a housecat's breathing chest swung its forelegs 3.6 mm, 1% of its height).
Usage: python -I stand_study.py <model.gltf> - [clip names, comma-separated; default: the idle clip and any clip named idle or stand]
Only clips where the animal stands still on planted feet belong here: a walk, a run, a lunge onto one foot or a fall is
off balance for moments by design (momentum carries it). List a planted-feet attack explicitly to include it."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, os, sys

here = os.path.dirname(os.path.abspath(__file__))
MODEL = sys.argv[1]; CLIPS = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] else None
g = {'__file__': os.path.join(here, 'rig_study.py')}; argv = sys.argv; sys.argv = ['x', MODEL, '-']
src = open(os.path.join(here, 'rig_study.py'), encoding='utf-8').read().split('# ---- 1.')[0]
with contextlib.redirect_stdout(io.StringIO()): exec(src, g)
sys.argv = argv
world, pose_at, clip, skin, V, T, A, rest = (g[k] for k in ('world', 'pose_at', 'clip', 'skin', 'V', 'T', 'A', 'rest'))


def com(P):
    vol = 0.0; c = [0.0, 0.0, 0.0]
    for a, b, d in T:
        p, q, r = P[a], P[b], P[d]
        v = (p[0] * (q[1] * r[2] - q[2] * r[1]) - p[1] * (q[0] * r[2] - q[2] * r[0]) + p[2] * (q[0] * r[1] - q[1] * r[0])) / 6
        vol += v
        for k in range(3): c[k] += v * (p[k] + q[k] + r[k]) / 4
    return [x / vol for x in c] if abs(vol) > 1e-12 else None


def margin(P):
    c = com(P)
    if c is None: return None
    Q = [P[c] for c in FEET] if FEET else P
    y0 = min(p[1] for p in Q); ground = [p for p in Q if p[1] < y0 + BAND]
    out = []
    for k in (2, 0):                                              # front to back (z), then side to side (x)
        lo, hi = min(p[k] for p in ground), max(p[k] for p in ground); half = (hi - lo) / 2
        out.append(((hi - c[k]) if c[k] > (lo + hi) / 2 else (c[k] - lo)) / half if half > 1e-6 else -1.0)
    return out, c, ground


_ys = [v[0][1] for v in V]; BAND = 0.012 * (max(_ys) - min(_ys))      # 4.8 cm on a 4 m animal, 4 mm on a cat
from lowpoly import rig_parts
_fc = rig_parts.foot_corners(rig_parts.parts(A, V))
FEET = sorted(set().union(*_fc)) if _fc and all(_fc) else None
HEIGHT = max(_ys) - min(_ys)


def slide(P0, frames):
    """the worst horizontal drift of a sole vertex while it stays on the ground, (metres, foot index). A vertex that leaves the
    contact band and lands again is anchored afresh where it lands: a step is not a slide."""
    groups = [sorted(f) for f in _fc] if FEET else [list(range(len(P0)))]
    g0 = min(P0[i][1] for gr in groups for i in gr)
    worst = (0.0, None)
    for fi, gr in enumerate(groups):
        anchor = {i: P0[i] for i in gr if P0[i][1] < g0 + BAND}
        for P in frames + frames[:1]:                         # the loop closes on the first frame
            gy = min(P[i][1] for g_ in groups for i in g_)
            for i in gr:
                if P[i][1] >= gy + BAND: anchor.pop(i, None); continue
                if i not in anchor: anchor[i] = P[i]; continue
                d = ((P[i][0] - anchor[i][0]) ** 2 + (P[i][2] - anchor[i][2]) ** 2) ** 0.5
                if d > worst[0]: worst = (d, fi)
    return worst
names = CLIPS or [n for n in A['anims'] if n == A.get('idle') or 'idle' in n.lower() or 'stand' in n.lower()]
print('== %s: standing balance (centre of mass over the ground contact; contact from %s)' % (A['name'], 'the feet in the rig' if FEET else 'all the skin'))
mb, cb, gb = margin(skin(world(rest)))
print('   %-10s worst margin front-back %+.2f, side-side %+.2f | centre of mass z %.2f | contact z %.2f..%.2f'
      % ('bind pose', mb[0], mb[1], cb[2], min(p[2] for p in gb), max(p[2] for p in gb)))
for n in names:
    d, cl = clip(n); N = 1 if d == 0 else max(24, min(300, int(d * 30)))      # 30 per second: a quick step falls between sparse frames
    worst = None
    frames = [skin(world(pose_at((d, cl), k / max(1, N)))) for k in range(N)]
    for k in range(N):
        r = margin(frames[k])
        if r is None: continue
        (mz, mx), c, gr = r
        if worst is None or min(mz, mx) < min(worst[0], worst[1]): worst = (mz, mx, c, gr, k / max(1, N))
    mz, mx, c, gr, t = worst
    print('   clip %-10s worst margin front-back %+.2f, side-side %+.2f (phase %.2f) | centre of mass z %.2f | contact z %.2f..%.2f'
          % (n, mz, mx, t, c[2], min(p[2] for p in gr), max(p[2] for p in gr)))
    sd, sf = slide(frames[0], frames[1:])
    print('   clip %-10s foot slide %.4f m = %.2f%% of the height (foot %s)' % (n, sd, 100 * sd / HEIGHT, '-' if sf is None else sf))

# ---- below the ground (2026-11-24): the pangolin's tail sank 5.5 cm through the ground in its idle and walk and nothing
# flagged it (the balance counts only the feet as contact). Every clip, every frame: the lowest skin point against the ground
# (y = 0, where the feet stand)
worst_g = (0.0, None, 0.0)
for n in A['anims']:
    d, cl = clip(n); N = 1 if d == 0 else max(24, min(120, int(d * 12)))
    for k in range(N):
        P = skin(world(pose_at((d, cl), k / max(1, N))))
        lo = min(p[1] for p in P)
        if lo < worst_g[0]: worst_g = (lo, n, k / max(1, N))
print('== below the ground: lowest skin point %.4f m = %.2f%% of the height (clip %s, phase %.2f)'
      % (worst_g[0], 100 * worst_g[0] / HEIGHT, worst_g[1] or '-', worst_g[2]))
