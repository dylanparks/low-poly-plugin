"""How a model's mouth is built and how far its jaw opens: the jaw's share of the head, the mouth's open edges (lip rims left
open), the teeth (separate closed pieces, or none), and the gape in every clip, measured as the mouth shows it: the angle
at the jaw's hinge between the upper lip's front and the chin, with the lip gap between them and how far the snout
pitches from its bind pose at the widest gape. Standard library only.
Usage: python -I jaw_study.py <model.gltf|.glb> [jaw bone name]
  The gape runs from the upper lip's front (the head's midline skin nearest the chin) and the chin (the jaw's frontmost
  midline skin) to the jaw bone's joint.
  The jaw bone is found by name (one containing "jaw") unless given. A rig with no jaw bone is reported and the tool stops.
Judge the gapes against the species' anatomy: its maximum bony gape (a modern cat about 65 degrees) is the limit
(lowpoly-core/references/temperament.md, "Open the jaw wide")."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 2 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, math, os, struct, sys
from collections import Counter
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
from lowpoly import gltf_io  # noqa: E402
from lowpoly.spring_bake import decode_clip, sample, qmul, qrot  # noqa: E402

A, _ = gltf_io.read_gltf(sys.argv[1])
names = A['bones']; nb = len(names); par = A['parent']
jaws = [i for i, nm in enumerate(names) if 'jaw' in nm.lower()]
if len(sys.argv) > 2: jaws = [names.index(sys.argv[2])]
if not jaws:
    print('== %s: no jaw bone (no bone named like "jaw"): the mouth cannot open; nothing measured' % A.get('name')); sys.exit(0)
jb = jaws[0]; hb = par[jb]

C, T, base = [], [], 0
for s in A['subs']:
    raw = base64.b64decode(s['v']); n = len(raw) // 64
    C += [struct.unpack_from('<16f', raw, k * 64) for k in range(n)]
    ix = struct.unpack('<%dH' % (len(base64.b64decode(s['i'])) // 2), base64.b64decode(s['i']))
    T += [tuple(base + i for i in ix[k:k + 3]) for k in range(0, len(ix), 3)]; base += n
N = len(C)
key = lambda i: (round(C[i][0], 4), round(C[i][1], 4), round(C[i][2], 4))
share = lambda i, b: sum(C[i][8 + j] for j in range(4) if int(round(C[i][12 + j])) == b and C[i][8 + j] > 0)
ys = [c[1] for c in C]; H = (max(ys) - min(ys)) or 1.0

# ---- pieces: the main skin, and the rest (teeth, claws, cards)
parent_of = {}
def find(a):
    while parent_of.get(a, a) != a: a = parent_of[a]
    return a
for t in T:
    ks = [key(i) for i in t]
    for k in ks[1:]: parent_of[find(k)] = find(ks[0])
pieces = Counter(find(key(t[0])) for t in T)
main = pieces.most_common(1)[0][0]
other = [p for p in pieces if p != main]
tooth_pieces = sum(1 for p in other if any(find(key(t[0])) == p and any(share(i, jb) > 0.5 or share(i, hb) > 0.5 for i in t) for t in T))

# ---- the head and the jaw
def sub(b):
    out = {b}
    for k in range(nb):
        if par[k] is not None and par[k] in out: out.add(k)
    return out
head_bones = sub(hb)
in_head = [i for i in range(N) if sum(share(i, b) for b in head_bones) >= 0.5]
on_jaw = [i for i in range(N) if share(i, jb) >= 0.5]
upos = lambda idx: len({key(i) for i in idx})
E = Counter()
for t in T:
    for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): E[frozenset((key(a), key(b)))] += 1
hk = {key(i) for i in in_head}
open_mouth = sum(1 for e, c in E.items() if c == 1 and all(p in hk for p in e))
print('== %s: jaw bone %s under %s' % (A.get('name'), names[jb], names[hb]))
print('   head %d positions, jaw %d (%.0f%% of the head); open edges on the head (lip rims left open): %d'
      % (upos(in_head), upos(on_jaw), 100 * upos(on_jaw) / max(1, upos(in_head)), open_mouth))
print('   separate pieces besides the skin: %d, of them on the head or jaw bones (modelled teeth): %d%s'
      % (len(other), tooth_pieces, '' if tooth_pieces else ' (teeth, if any, are painted)'))

# ---- the gape's three points
mid = [i for i in range(N) if abs(C[i][0]) < 0.02 * H]
up = [i for i in mid if share(i, hb) >= 0.5 and share(i, jb) < 0.5]
lo = [i for i in mid if share(i, jb) >= 0.5]
if not up or not lo:
    print('   no midline skin on the head and on the jaw: the gape cannot be measured'); sys.exit(0)
# the chin: the jaw's frontmost midline skin; the upper lip's front: the head's midline skin nearest the chin (not the nose
# tip, which sits higher and would add the snout's own depth to every angle)
CHIN = max(lo, key=lambda i: C[i][2])
NOSE = min(up, key=lambda i: math.dist(C[i][:3], C[CHIN][:3]))
inv = [(tuple(A['inv'][i * 7:i * 7 + 4]), tuple(A['inv'][i * 7 + 4:i * 7 + 7])) for i in range(nb)]
r0 = [tuple(A['rest'][i * 7:i * 7 + 4]) for i in range(nb)]; p0 = [tuple(A['rest'][i * 7 + 4:i * 7 + 7]) for i in range(nb)]


def world(rots, poss):
    W = [None] * nb
    for i in range(nb):
        q, p = rots[i], poss[i]; pi = par[i]
        if pi is None or pi < 0 or pi == i: W[i] = (q, p)
        else:
            pq, pp = W[pi]; W[i] = (qmul(pq, q), tuple(a + b for a, b in zip(pp, qrot(pq, p))))
    return W


def skin(i, W):
    p = C[i][:3]; out = [0.0, 0.0, 0.0]
    for j in range(4):
        w = C[i][8 + j]
        if w <= 0: continue
        b = int(round(C[i][12 + j])); iq, ip = inv[b]
        q = tuple(a + c for a, c in zip(qrot(iq, p), ip))
        wq, wp = W[b]; q = tuple(a + c for a, c in zip(qrot(wq, q), wp))
        out = [o + w * c for o, c in zip(out, q)]
    return out


def gape(W):
    h = W[jb][1]; a = skin(NOSE, W); c = skin(CHIN, W)
    va = [a[k] - h[k] for k in range(3)]; vc = [c[k] - h[k] for k in range(3)]
    d = math.sqrt(sum(x * x for x in va) * sum(x * x for x in vc)) or 1.0
    ang = math.degrees(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(va, vc)) / d))))
    return ang, math.degrees(math.atan2(va[1], math.hypot(va[0], va[2]))), math.dist(a, c)


g0 = gape(world(r0, p0))
W0 = world(r0, p0)
print('   bind pose: gape %.1f deg, lip gap %.3f m (%.1f%% of the height); the upper lip %.3f m ahead of the hinge'
      % (g0[0], g0[2], 100 * g0[2] / H, abs(C[NOSE][2] - W0[jb][1][2])))
for clip, src in A.get('anims', {}).items():
    keys = decode_clip(src, nb); rows = []
    for f in range(97):
        u = f / 96
        W = world([sample(keys[i][0], u, 4) or r0[i] for i in range(nb)], [sample(keys[i][1], u, 3) or p0[i] for i in range(nb)])
        g = gape(W); rows.append((u, g[0], g[1] - g0[1], g[2]))
    mx = max(rows, key=lambda r: r[1]); mn = min(rows, key=lambda r: r[1])
    flag = '  (the lips part by more than the head is long: a jaw pulled off its hinge, or an unreliable clip)' if mx[3] > 0.5 * H else ''
    print('   clip %-10s %.2f s: gape %.1f..%.1f deg, lip gap %.3f..%.3f m; widest at %.2f s with the snout %+.0f deg from its bind pitch%s'
          % (clip, src['d'], mn[1], mx[1], mn[3], mx[3], mx[0] * src['d'], mx[2], flag))
