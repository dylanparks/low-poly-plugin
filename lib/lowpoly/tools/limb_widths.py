"""Where each leg's mass sits, seen from the front: the outline's half-width at each height between a limb's top joint (hip or
shoulder) and the next joint down (knee or elbow), over the limb's stretch of the body. A thigh is fullest at about mid-leg and
tapers up into the haunch and down to the knee (lowpoly-animals/references/limbs.md). Built twice the other way round: the 12 m test T. rex
was widest at the belly line just above the knee, and the test fox at the knee itself, each with the haunch pinched above it.
The limbs are found from the rig, not from bone names: a limb's top bone is one whose chain reaches the ground and whose parent's
chain does not; the next joint down is its first child. Only the leg's own skin and the body's count: a triangle is measured
when, at each corner, the leg's bones and the body's carry at least half the weight. Another leg, a wing, a pincer arm or any
other side branch of the rig beside the thigh is left out (a bird's folded wing read as its thigh, and the check warned on a
leg that hadn't changed). For each limb it reports the heights of the two joints, the widest
half-width between them and where it sits (t: 0 at the knee or elbow, 1 at the hip or shoulder), and the half-widths at the
lower and the upper joint as shares of the widest. Then the rearmost pair (the hind legs) as the summary lp check judges.
Standard library only; reads glTF 2.0 (and the viewer's files).
Usage: python -I limb_widths.py <model.gltf> - [rows=12]"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, os, sys

D, AID = sys.argv[1:3]
ROWS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
here = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
A, V, T = g['A'], g['V'], g['T']; P = [v[0] for v in V]
names, parent = A['bones'], A['parent']; nb = len(names)
W = g['world'](g['rest'])
J = [tuple(W[i][1]) for i in range(nb)]                                         # each bone's joint, in the bind pose
ys = [p[1] for p in P]; ymin, H = min(ys), max(ys) - min(ys)
def par(i): p = parent[i]; return p if p is not None and p >= 0 and p != i else None
kids = {i: [k for k in range(nb) if par(k) == i] for i in range(nb)}


def grounded(i):
    """the sides (+1 / -1) of the joints near the ground in bone i's chain; a joint on the midline counts as neither"""
    s = set()
    if J[i][1] < ymin + 0.15 * H and abs(J[i][0]) > 0.01 * H: s.add(1 if J[i][0] > 0 else -1)
    for k in kids[i]: s |= grounded(k)
    return s


# a limb's top bone: its chain reaches the ground on one side only, while its parent's reaches both sides (the hips over the
# two hind legs, the chest over the two forelegs); the toes and the shin below it reach one side, as their parent does
G = [grounded(i) for i in range(nb)]
roots = [i for i in range(nb) if len(G[i]) == 1 and kids[i] and par(i) is not None and len(G[par(i)]) == 2
         and J[i][1] > ymin + 0.25 * H]
# a girdle bone (a hip or shoulder bone above the leg's own top joint) barely drops to its child: measuring between them
# read a 13 mm slice of the Komodo's hip as its whole thigh (widest at the knee, the knee 1.00 of it). Step down to the
# first joint that drops at least a quarter of its height above the ground.
def _leg_top(r):
    while kids[r] and J[r][1] - J[kids[r][0]][1] < 0.25 * (J[r][1] - ymin) and len(G[kids[r][0]]) == 1:
        r = kids[r][0]
    return r
roots = [_leg_top(r) for r in roots]


# whose skin counts: the body's bones (outside every leg and every side branch: a wing, a pincer arm, an ear) and the leg's own
from lowpoly import rig_parts                                       # noqa: E402  (rig_study put lib/ on the path)
_R = rig_parts.parts(A, [(p, ws) for p, ws in V])
def _sub(i): return [i] + [b for k in kids[i] for b in _sub(k)]
_legs = set().union(*(l['bones'] for l in _R['limbs'])) if _R['limbs'] else set()
for r in roots: _legs |= set(_sub(r))
_side_branch = set()
for b in range(nb):
    p = par(b)
    if b not in _legs and p is not None and abs(J[b][0]) > 0.01 * H and abs(J[p][0]) <= 0.01 * H: _side_branch |= set(_sub(b))
BODY = set(range(nb)) - _legs - _side_branch


def own_skin(r):
    """the triangles of leg r's own skin and the body's: every corner at least half carried by those bones"""
    ok_b = BODY | set(_sub(r))
    ok_c = [sum(w for b, w in V[c][1] if b in ok_b) >= 0.5 - 1e-6 for c in range(len(V))]
    return [t for t in T if all(ok_c[i] for i in t)]


def width_at(y, z0, z1, side, tris=None):
    """the outermost |x| of the skin on one side at height y, over z in [z0, z1], from the triangles the height cuts"""
    best = 0.0
    for t in (T if tris is None else tris):
        p = [P[i] for i in t]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            A_, B_ = p[a], p[b]
            if (A_[1] - y) * (B_[1] - y) <= 0 and A_[1] != B_[1]:
                s = (y - A_[1]) / (B_[1] - A_[1]); x = A_[0] + s * (B_[0] - A_[0]); z = A_[2] + s * (B_[2] - A_[2])
                if z0 <= z <= z1 and x * side > 0: best = max(best, abs(x))
    return best


print('== %s: limbs found from the rig: %s' % (A.get('name', AID), ', '.join(names[r] for r in roots) or 'none'))
res = []
for r in roots:
    top = J[r]; low = J[max(kids[r], key=lambda k: J[r][1] - J[k][1])]          # the next joint down
    if top[1] - low[1] < 0.02 * H: continue
    side = 1 if top[0] > 0 else -1
    reach = top[1] - low[1]; zc = (top[2] + low[2]) / 2
    z0, z1 = zc - 0.6 * reach, zc + 0.6 * reach
    rows = [low[1] + (top[1] - low[1]) * k / ROWS for k in range(ROWS + 1)]
    own = own_skin(r)
    w = [width_at(y, z0, z1, side, own) for y in rows]
    k_peak = max(range(len(w)), key=lambda k: w[k]); peak = w[k_peak]
    if peak <= 0: continue
    t_peak = k_peak / ROWS
    res.append((r, top, low, t_peak, w[0] / peak, w[-1] / peak, peak))
    print('   %-14s top joint y %.3f, lower joint y %.3f | widest %.3f at y %.3f (t %.2f) | lower joint %.2f of it, top joint %.2f'
          % (names[r], top[1], low[1], peak, rows[k_peak], t_peak, w[0] / peak, w[-1] / peak))
    print('      ' + '  '.join('%.3f:%.3f' % (y, x) for y, x in zip(rows, w)))
if res:
    zmin = min(rr[1][2] for rr in res)
    hind = [rr for rr in res if abs(rr[1][2] - zmin) < 0.25 * H]
    print('hind legs: widest at t %.2f..%.2f (0 the knee, 1 the hip) | knee %.2f..%.2f of the widest | hip %.2f..%.2f of the widest'
          % (min(h[3] for h in hind), max(h[3] for h in hind), min(h[4] for h in hind), max(h[4] for h in hind),
             min(h[5] for h in hind), max(h[5] for h in hind)))
