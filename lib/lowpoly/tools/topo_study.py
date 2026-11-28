"""How a model spends its polygons, judged against what a low-poly model is for: a silhouette that deforms, paid for in
rendered vertices and texels (lowpoly-core SKILL.md, "What a model is for"). Standard library only; reads glTF.
Usage: python -I topo_study.py <model.gltf|.glb> [--waste]

It reports:
  cost      rendered vertices (corners) per welded position. Every UV seam and every hard edge duplicates a vertex for the
            renderer; a single mirrored pelt keeps this near 1.0 by construction, a model cut into many texture
            charts runs past 2.
  shares    each part's share of the triangles beside its share of the surface, and its triangles per square metre. Parts
            come from the rig (lowpoly/rig_parts.py): the head with its jaw and ears, each limb, its feet, and the body
            (torso, neck and tail). The head's density over the body's is the bloat number (lp check warns past 4).
            Separate pieces (teeth, claws) are counted on their own line, not in the head's share or density.
  mirror    whether the model was built as a mirrored half: triangles per side, and the share of left triangles whose
            exact texels a right triangle also uses. Positions are not compared: a bind pose stepped off-centre is right.
  waste     edges that could be collapsed with almost no change to the surface (the rms distance the collapse moves the
            skin, under 0.2% of the height), leaving out edges a joint needs (their two ends carried by different bones).
            Each such edge is two triangles that shape nothing: move them to where the outline is coarse. With --waste,
            every wasted edge is listed with its part and position. A texture feature can justify an edge this tool calls
            waste (an eye's corner, a stripe's edge): judge those by eye."""
import sys as _sys  # _usage_guard
if __name__ == '__main__' and (len(_sys.argv) < 2 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, math, os, struct, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lowpoly import gltf_io, rig_parts  # noqa: E402

MODEL = sys.argv[1]; LIST = '--waste' in sys.argv[2:]
A, _ = gltf_io.read_gltf(MODEL)
C, T = [], []
for s in A['subs']:
    raw = base64.b64decode(s['v']); n = len(raw) // 64; base = len(C)
    C += [struct.unpack_from('<16f', raw, k * 64) for k in range(n)]
    ib = base64.b64decode(s['i']); ix = struct.unpack('<%dH' % (len(ib) // 2), ib)
    T += [(base + ix[k], base + ix[k + 1], base + ix[k + 2]) for k in range(0, len(ix) - 2, 3)]
names = A['bones']
key = lambda i: (round(C[i][0], 4), round(C[i][1], 4), round(C[i][2], 4))
pid, P = {}, []
for i in range(len(C)):
    if key(i) not in pid: pid[key(i)] = len(P); P.append(C[i][:3])
vi = [pid[key(i)] for i in range(len(C))]
TP = [tuple(vi[i] for i in t) for t in T]
keep = [k for k, t in enumerate(TP) if len(set(t)) == 3]
T = [T[k] for k in keep]; TP = [TP[k] for k in keep]
ys = [p[1] for p in P]; H = (max(ys) - min(ys)) or 1.0

# ---- parts from the rig
V = [((c[0], c[1], c[2]), [(int(round(c[12 + j])), c[8 + j]) for j in range(4) if c[8 + j] > 1e-4]) for c in C]
R = rig_parts.parts(A, V)
W = {}
for i in range(len(C)): W.setdefault(vi[i], dict(V[i][1]))
head = R['head']['bones'] if R['head'] else set()
foot = set().union(*(l['foot_bones'] for l in R['limbs'])) if R['limbs'] else set()
limb = set().union(*(l['bones'] for l in R['limbs'])) if R['limbs'] else set()


def vpart(v):
    w = W[v]; s = lambda bs: sum(x for b, x in w.items() if b in bs)
    if s(head) >= 0.5: return 'head'
    if s(foot) >= 0.5: return 'feet'
    if s(limb) >= 0.5: return 'limbs'
    return 'body'


VP = [vpart(v) for v in range(len(P))]
TPART = [Counter(VP[v] for v in t).most_common(1)[0][0] for t in TP]
# separate pieces (teeth sunk in the gums, claws) are left out of the shares and counted on their own: the head's share and
# density are its skin's (lowpoly-core SKILL.md §2, "not counting teeth"); a hostile mob's modelled teeth would otherwise
# read as a bloated head. The mouth's inside is skin and stays counted
_par = {}
def _find(a):
    while _par.get(a, a) != a: a = _par[a]
    return a
for t in TP:
    for v in t[1:]: _par[_find(v)] = _find(t[0])
_comp = Counter(_find(t[0]) for t in TP)
_main = _comp.most_common(1)[0][0] if _comp else None
TPART = ['pieces' if _find(t[0]) != _main else p for t, p in zip(TP, TPART)]


def cross(u, v): return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def area(t): n = cross(sub(P[t[1]], P[t[0]]), sub(P[t[2]], P[t[0]])); return 0.5 * math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)


print('== %s: %d positions, %d corners, %d triangles' % (os.path.splitext(os.path.basename(MODEL))[0], len(P), len(C), len(TP)))
print('cost: corners per position %.2f' % (len(C) / max(1, len(P))))
pc = Counter(TPART); pa = defaultdict(float)
for t, p in zip(TP, TPART): pa[p] += area(t)
tot = sum(pa.values()) or 1.0
print('shares (rig: %s):' % ('head %s, %d limbs' % (R['head']['rule'] if R['head'] else 'none found', len(R['limbs']))))
for p in ('head', 'body', 'limbs', 'feet', 'pieces'):
    if pc[p]: print('   %-6s %4d triangles %3.0f%% | surface %3.0f%% | %5.0f per m2' % (p, pc[p], 100 * pc[p] / len(TP), 100 * pa[p] / tot, pc[p] / max(pa[p], 1e-9)))
if pc['pieces']: print('   (pieces: %d separate pieces such as teeth or claws, left out of the head and body shares)' % (len(_comp) - 1))
if pc['head'] and pc['body']:
    print('head density over body %.1f' % ((pc['head'] / pa['head']) / (pc['body'] / pa['body'])))

# ---- mirrored construction, read through the texture
uv = lambda i: (round(C[i][6], 3), round(C[i][7], 3))
side = lambda t: sum(C[i][0] for i in t)
L = Counter(frozenset(uv(i) for i in t) for t in T if side(t) > 1e-4)
Rt = Counter(frozenset(uv(i) for i in t) for t in T if side(t) < -1e-4)
nl, nr = sum(L.values()), sum(Rt.values()); both = sum(min(L[k], Rt[k]) for k in L)
print('mirror: triangles left %d right %d | left triangles sharing a right triangle\'s texels %.0f%%' % (nl, nr, 100.0 * both / max(1, nl)))

# ---- waste: quadric error of collapsing each edge
edges = defaultdict(list)
for fi, t in enumerate(TP):
    for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): edges[(min(a, b), max(a, b))].append(fi)
def planes_of(PS):
    pl = defaultdict(list)
    for t in TP:
        n = cross(sub(PS[t[1]], PS[t[0]]), sub(PS[t[2]], PS[t[0]])); l = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        if l < 1e-12: continue
        n = (n[0] / l, n[1] / l, n[2] / l); d = -(n[0] * PS[t[0]][0] + n[1] * PS[t[0]][1] + n[2] * PS[t[0]][2])
        for v in t: pl[v].append((n, d))
    return pl


# every shape the model takes: the bind pose and each morph target (a body type, a face). An edge that shapes nothing in
# the median body can make the biceps of a bodybuilder; it is waste only if it shapes nothing in any of them
SHAPES = [P]
for s_ in A['subs'][:1]:
    for mo in s_.get('morphs', []):
        dl = struct.unpack('<%df' % (len(base64.b64decode(mo['d'])) // 4), base64.b64decode(mo['d']))
        PS = list(P)
        for i in range(min(len(C), len(dl) // 3)): PS[vi[i]] = (C[i][0] + dl[3 * i], C[i][1] + dl[3 * i + 1], C[i][2] + dl[3 * i + 2])
        SHAPES.append(PS)
PLANES = [planes_of(PS) for PS in SHAPES]


def rms(pt, pls):
    return math.sqrt(sum((n[0] * pt[0] + n[1] * pt[1] + n[2] * pt[2] + d) ** 2 for n, d in pls) / max(1, len(pls)))


def wdiff(a, b):
    ks = set(W[a]) | set(W[b]); return sum(abs(W[a].get(k, 0) - W[b].get(k, 0)) for k in ks)


LIMIT = 0.002 * H
cand = []
for (a, b), fs in edges.items():
    if len(fs) != 2: continue                                   # an open or over-shared edge is not a collapse candidate
    if wdiff(a, b) > 0.5: continue                              # a joint needs it: its ends ride different bones
    e = 0.0
    for PS, pl in zip(SHAPES, PLANES):
        pls = pl[a] + pl[b]
        mid = tuple((PS[a][k] + PS[b][k]) / 2 for k in range(3))
        e = max(e, min(rms(PS[a], pls), rms(PS[b], pls), rms(mid, pls)))
    if e < LIMIT: cand.append((e, a, b))
cand.sort(); used = set(); waste = []
for e, a, b in cand:                                             # independent collapses only: no vertex counted twice
    if a in used or b in used: continue
    used |= {a, b}; waste.append((e, a, b))
wt = 2 * len(waste)
bypart = Counter(VP[a] for _, a, b in waste)
if len(SHAPES) > 1: print('waste judged over %d shapes: the bind pose and %d morph targets' % (len(SHAPES), len(SHAPES) - 1))
print('waste: %d edges collapse with under %.1f mm of change (0.2%% of the height) = %d triangles, %.1f%% of the model%s'
      % (len(waste), LIMIT * 1000, wt, 100.0 * wt / max(1, len(TP)), (' | by part: ' + ', '.join('%s %d' % kv for kv in bypart.most_common())) if waste else ''))
if LIST:
    for e, a, b in waste:
        m = tuple((P[a][k] + P[b][k]) / 2 for k in range(3))
        print('   %-6s edge at x %+.3f y %.3f z %+.3f, %.0f mm long, collapse changes %.2f mm'
              % (VP[a], m[0], m[1], m[2], 1000 * math.dist(P[a], P[b]), 1000 * e))
