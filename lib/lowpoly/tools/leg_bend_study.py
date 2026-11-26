"""How the legs bend and keep their width through every clip: the joints' angles, a hinge bent the wrong way, the skin's
rings pinching at a bend, the skin stretching along the leg, and a pair of legs moving in lockstep.
Usage: python -I leg_bend_study.py <model.gltf|.glb>
The legs are read from the rig (lowpoly/rig_parts.py: a limb's top bone, its chain down to the ground, its ankle), not from
bone names. Per clip, sampled at 97 frames, skinned as the viewer skins (linear blend):
  - joints: every joint inside a leg's chain, its inside angle (180 = straight) and range. A hinge is a joint between the
    leg's top and its ankle that the bind pose shows bent (inside angle under 170), and the ankle when it is bent well
    (under 150: a hock; a carpus that stands near straight flexes both ways and is not judged). A hinge whose joint crosses
    the line between its neighbours, from its bind side to the other, by more than 5 degrees is hyperextended: a knee or
    elbow bent backwards;
  - rings: the leg's skin grouped by the bones that carry it (a ring blended across a joint, a stretch on one bone); a
    ring's size is the mean distance between its vertices. Linear blend skinning shrinks a ring weighted half and half
    across a joint to about cos(bend / 2) of its width: 0.91 at a 50 degree bend, 0.71 at 90;
  - stretch: every edge of the leg's skin longer than 0.6% of the height, its length against the bind pose;
  - lockstep: for each pair of legs whose tops share a parent (the forelegs, the hind legs), the correlation over the clip of
    their joints' angles (1 = moving as one, 0 = unrelated, -1 = in counterphase), the mean over the joints that move.
Ends with one line per clip lp check reads:
  clip <name>: ring <worst> | stretch <lo>..<hi> | hyperextended <frames> | lockstep <worst pair's mean>
Standard library only."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 2 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, itertools, math, os, struct, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
from lowpoly import gltf_io, rig_parts  # noqa: E402
from lowpoly.spring_bake import decode_clip, sample, qmul, qrot, qconj  # noqa: E402

A, _ = gltf_io.read_gltf(sys.argv[1])
names = A['bones']; nb = len(names); par = A['parent']
C, T, base = [], [], 0
for s in A['subs']:
    raw = base64.b64decode(s['v']); n = len(raw) // 64
    C += [struct.unpack_from('<16f', raw, k * 64) for k in range(n)]
    ix = struct.unpack('<%dH' % (len(base64.b64decode(s['i'])) // 2), base64.b64decode(s['i']))
    T += [tuple(base + i for i in ix[k:k + 3]) for k in range(0, len(ix), 3)]; base += n
WS = [[(int(round(c[12 + j])), c[8 + j]) for j in range(4) if c[8 + j] > 0] for c in C]
R = rig_parts.parts(A, [(c[:3], w) for c, w in zip(C, WS)])
H = R['height']
if not R['limbs'] or not A.get('anims'):
    print('== %s: %s; nothing measured' % (A.get('name'), 'no legs in the rig' if not R['limbs'] else 'no clips')); sys.exit(0)
J0 = rig_parts.joints(A)
kids = {i: [k for k in range(nb) if par[k] == i and k != i] for i in range(nb)}


def sub(i):
    out = [i]
    for k in kids[i]: out += sub(k)
    return out


def angle_at(a, b, c):
    u = [a[k] - b[k] for k in range(3)]; v = [c[k] - b[k] for k in range(3)]
    d = math.sqrt(sum(x * x for x in u) * sum(x * x for x in v)) or 1e-12
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(u, v)) / d))))


def side_of(a, b, c, normal):
    """which side of the line a-c the joint b lies on, about the leg's bending plane's normal"""
    u = [c[k] - a[k] for k in range(3)]; v = [b[k] - a[k] for k in range(3)]
    cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return sum(x * y for x, y in zip(cr, normal))


LEGS = []
for L in R['limbs']:
    chain, i = [L['root']], L['root']
    while kids[i]:
        i = min(kids[i], key=lambda k: min(J0[b][1] for b in sub(k))); chain.append(i)
    k_ankle = chain.index(L['ankle']) if L['ankle'] in chain else len(chain) - 2
    joints = []
    for k in range(1, len(chain) - 1):
        a, b, c = J0[chain[k - 1]], J0[chain[k]], J0[chain[k + 1]]
        ang = angle_at(a, b, c)
        hinge = (k < k_ankle and ang < 170) or (k == k_ankle and ang < 150)
        # the bending plane: the leg's own, through the three joints (a straight joint takes the side-view plane)
        u = [a[q] - b[q] for q in range(3)]; v = [c[q] - b[q] for q in range(3)]
        nrm = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        if math.sqrt(sum(x * x for x in nrm)) < 1e-9: nrm = (1.0, 0.0, 0.0)
        joints.append({'k': k, 'bone': chain[k], 'hinge': hinge, 'bind': ang, 'normal': nrm})
    bones = set(L['bones'])
    vs = [i for i in range(len(C)) if sum(w for b, w in WS[i] if b in bones) >= 0.5]
    LEGS.append({'root': L['root'], 'chain': chain, 'joints': joints, 'verts': vs, 'name': names[L['root']]})

key = lambda i: (round(C[i][0], 4), round(C[i][1], 4), round(C[i][2], 4))
for L in LEGS:
    g = {}
    for i in L['verts']:
        top = sorted(WS[i], key=lambda bw: -bw[1])
        ring = names[top[0][0]] if len(top) < 2 or top[1][1] < 0.25 else '+'.join(sorted((names[top[0][0]], names[top[1][0]])))
        g.setdefault(ring, {})[key(i)] = i
    L['rings'] = {r: list(d.values()) for r, d in g.items() if len(d) >= 3}
    vs = set(L['verts']); es = set()
    for t in T:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if a in vs and b in vs and key(a) != key(b): es.add((min(a, b), max(a, b)))
    L['edges'] = [(a, b, math.dist(C[a][:3], C[b][:3])) for a, b in es if math.dist(C[a][:3], C[b][:3]) > 0.006 * H]
pairs = [(a, b) for a, b in itertools.combinations(range(len(LEGS)), 2) if par[LEGS[a]['root']] == par[LEGS[b]['root']]]

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
    for b, w in WS[i]:
        iq, ip = inv[b]; q = tuple(a + c for a, c in zip(qrot(iq, p), ip)); wq, wp = W[b]
        q = tuple(a + c for a, c in zip(qrot(wq, q), wp)); out = [o + w * c for o, c in zip(out, q)]
    return out


def ring_size(pts):
    n = len(pts); return sum(math.dist(a, b) for a, b in itertools.combinations(pts, 2)) / max(1, n * (n - 1) / 2)


def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = math.sqrt(sum((x - ma) ** 2 for x in a)); vb = math.sqrt(sum((x - mb) ** 2 for x in b))
    if va < 1e-9 or vb < 1e-9: return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb)


W0 = world(r0, p0)
bind_ring = {(li, r): ring_size([skin(i, W0) for i in ids]) for li, L in enumerate(LEGS) for r, ids in L['rings'].items()}
bind_side = {(li, j['k']): side_of(*(W0[L['chain'][j['k'] + d]][1] for d in (-1, 0, 1)), j['normal'])
             for li, L in enumerate(LEGS) for j in L['joints']}
print('== %s: %d legs (%s); hinges judged for hyperextension: %s' % (
    A.get('name'), len(LEGS), ', '.join(L['name'] for L in LEGS),
    ', '.join('%s %.0f' % (names[j['bone']], j['bind']) for L in LEGS for j in L['joints'] if j['hinge']) or 'none'))
summary = []
for clip, src in A['anims'].items():
    keys = decode_clip(src, nb); F = 96
    ang = {(li, j['k']): [] for li, L in enumerate(LEGS) for j in L['joints']}
    ring = {}; st_lo, st_hi = (9.0, None), (0.0, None); hyper = {}
    for f in range(F + 1):
        u = f / F
        W = world([sample(keys[i][0], u, 4) or r0[i] for i in range(nb)], [sample(keys[i][1], u, 3) or p0[i] for i in range(nb)])
        cache = {}
        def S(i):
            if i not in cache: cache[i] = skin(i, W)
            return cache[i]
        for li, L in enumerate(LEGS):
            ch = L['chain']
            for j in L['joints']:
                a, b, c = (W[ch[j['k'] + d]][1] for d in (-1, 0, 1))
                ang[(li, j['k'])].append(angle_at(a, b, c))
                if j['hinge']:
                    # the bending plane follows the leg as it moves: rotate the bind normal by the bone's own rotation
                    nrm = qrot(qmul(W[ch[j['k']]][0], qconj(W0[ch[j['k']]][0])), j['normal'])
                    if side_of(a, b, c, nrm) * bind_side[(li, j['k'])] < 0 and angle_at(a, b, c) < 175:
                        hyper.setdefault((L['name'], names[j['bone']]), []).append(round(u, 2))
            for r, ids in L['rings'].items():
                v = ring_size([S(i) for i in ids]) / (bind_ring[(li, r)] or 1e-9)
                if v < ring.get((li, r), (9.0, 0))[0]: ring[(li, r)] = (v, u)
            for a, b, l0 in L['edges']:
                v = math.dist(S(a), S(b)) / l0
                if v < st_lo[0]: st_lo = (v, (u, L['name'], a, b))
                if v > st_hi[0]: st_hi = (v, (u, L['name'], a, b))
    print('-- clip %s (%.2f s)' % (clip, src['d']))
    for li, L in enumerate(LEGS):
        js = '  '.join('%s %3.0f..%3.0f' % (names[j['bone']], min(ang[(li, j['k'])]), max(ang[(li, j['k'])])) for j in L['joints'])
        worst = sorted(((v, u, r) for (l2, r), (v, u) in ring.items() if l2 == li))[:2]
        print('   %-12s %s | narrowest rings %s' % (L['name'], js, ', '.join('%s %.2f at %.2f' % (r, v, u) for v, u, r in worst)))
    for (leg, jn), us in hyper.items():
        print('   HYPEREXTENDED: %s %s in %d frames, from %.2f' % (leg, jn, len(us), us[0]))
    def where(e):
        u, leg, a, b = e; return '%s at %.2f' % (leg, u)
    print('   stretch: shortest edge %.2f (%s), longest %.2f (%s)' % (st_lo[0], where(st_lo[1]), st_hi[0], where(st_hi[1])))
    worst_pair = None
    for a, b in pairs:
        cs = []
        for ja, jb in zip(LEGS[a]['joints'], LEGS[b]['joints']):
            sa, sb = ang[(a, ja['k'])], ang[(b, jb['k'])]
            if max(sa) - min(sa) < 2 and max(sb) - min(sb) < 2: continue
            c = corr(sa, sb)
            if c is not None: cs.append(c)
        if not cs: continue
        m = sum(cs) / len(cs)
        print('   %s vs %s: angle correlation %.2f (per joint %s)' % (LEGS[a]['name'], LEGS[b]['name'], m, ', '.join('%.2f' % c for c in cs)))
        if worst_pair is None or m > worst_pair: worst_pair = m
    wr = min((v for v, u in ring.values()), default=1.0)
    summary.append('clip %s: ring %.2f | stretch %.2f..%.2f | hyperextended %d | lockstep %s' % (
        clip, wr, st_lo[0], st_hi[0], sum(len(v) for v in hyper.values()), '%.2f' % worst_pair if worst_pair is not None else '-'))
print('\n'.join(summary))
