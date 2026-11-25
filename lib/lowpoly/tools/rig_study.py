"""How the reference animals' legs join the body and move: skin weights at the junction, and the walk clip run through FK + skinning.
Usage: python -I rig_study.py <model.gltf|.glb> - [walk clip name]   (or a viewer folder and an animal id)"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, json, math, struct, sys
from collections import Counter, defaultdict

root, AID = sys.argv[1], sys.argv[2]


import glob, os
_here = os.path.dirname(os.path.abspath(globals().get('__file__') or sys.modules['__main__'].__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_here)))           # lib/, so that "lowpoly" imports
from lowpoly import gltf_io
# The model: a .gltf or .glb file, or (for the project the tools were first written in) a viewer folder and an animal id.
if root.lower().endswith(('.gltf', '.glb')): A, TEXFILE = gltf_io.read_gltf(root)
else: A, TEXFILE = gltf_io.load_viewer(root, AID)


def texpath(D=None, A_=None):
    """the model's texture image (the glTF's own image, or the viewer's textures/<name>.png)"""
    return TEXFILE


names, parent = A['bones'], A['parent']
nb = len(names)


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qrot(q, v):
    x, y, z, w = q; vx, vy, vz = v
    tx, ty, tz = 2 * (y * vz - z * vy), 2 * (z * vx - x * vz), 2 * (x * vy - y * vx)
    return (vx + w * tx + y * tz - z * ty, vy + w * ty + z * tx - x * tz, vz + w * tz + x * ty - y * tx)


def slerp(a, b, t):
    d = sum(x * y for x, y in zip(a, b))
    if d < 0: b = tuple(-x for x in b); d = -d
    if d > 0.9995: r = tuple(x + (y - x) * t for x, y in zip(a, b))
    else:
        th = math.acos(d); s = math.sin(th)
        r = tuple((math.sin((1 - t) * th) * x + math.sin(t * th) * y) / s for x, y in zip(a, b))
    n = math.sqrt(sum(x * x for x in r)); return tuple(x / n for x in r)


rest = [(tuple(A['rest'][i * 7:i * 7 + 4]), tuple(A['rest'][i * 7 + 4:i * 7 + 7])) for i in range(nb)]
inv = [(tuple(A['inv'][i * 7:i * 7 + 4]), tuple(A['inv'][i * 7 + 4:i * 7 + 7])) for i in range(nb)]

# vertices
V = []; T = []
for s in A['subs']:
    raw = base64.b64decode(s['v']); base = len(V)
    for k in range(0, len(raw), 64):
        f = struct.unpack_from('<16f', raw, k)
        V.append((f[0:3], [(int(f[12 + j]), f[8 + j]) for j in range(4) if f[8 + j] > 0.001]))
    ix = struct.unpack('<%dH' % (len(base64.b64decode(s['i'])) // 2), base64.b64decode(s['i']))
    T += [(base + ix[k], base + ix[k + 1], base + ix[k + 2]) for k in range(0, len(ix), 3)]


def clip(name):
    src = A['anims'][name]; f = struct.unpack('<%df' % (len(base64.b64decode(src['k'])) // 4), base64.b64decode(src['k'])); p = 0; out = []
    for b in range(nb):
        nr, np_ = int(f[p]), int(f[p + 1]); p += 2
        rot = [f[p + 5 * k:p + 5 * k + 5] for k in range(nr)]; p += 5 * nr
        pos = [f[p + 4 * k:p + 4 * k + 4] for k in range(np_)]; p += 4 * np_
        out.append((rot, pos))
    return src['d'], out


def sample(keys, u, n):
    if not keys: return None
    if len(keys) == 1: return tuple(keys[0][1:])
    k = 0
    while k < len(keys) - 2 and keys[k + 1][0] <= u: k += 1
    t0, t1 = keys[k][0], keys[k + 1][0]; f = min(1, max(0, (u - t0) / (t1 - t0))) if t1 > t0 else 0
    a, b = tuple(keys[k][1:]), tuple(keys[k + 1][1:])
    return slerp(a, b, f) if n == 4 else tuple(x + (y - x) * f for x, y in zip(a, b))


def world(local):
    W = [None] * nb
    for i in range(nb):
        q, p = local[i]; par = parent[i]
        if i == 0 or par is None or par < 0 or par == i: W[i] = (q, p)
        else:
            pq, pp = W[par]; W[i] = (qmul(pq, q), tuple(a + b for a, b in zip(pp, qrot(pq, p))))
    return W


def skin(W):
    out = []
    for pos, ws in V:
        acc = [0.0, 0.0, 0.0]
        for b, w in ws:
            iq, ip = inv[b]; v = tuple(a + c for a, c in zip(qrot(iq, pos), ip))
            wq, wp = W[b]; v = tuple(a + c for a, c in zip(qrot(wq, v), wp))
            for k in range(3): acc[k] += w * v[k]
        out.append(acc)
    return out


def pose_at(cl, u):
    _, keys = cl; local = []
    for i in range(nb):
        rot, pos = keys[i]
        q = sample(rot, u, 4) or rest[i][0]; p = sample(pos, u, 3) or rest[i][1]
        local.append((q, p))
    return local


print('== %s: %d bones, %d corners, %d tris; clips: %s' % (A['name'], nb, len(V), len(T), list(A['anims'])))

# ---- 1. junction: classify bones as body or limb by name/heuristic (limb = descendants of a hip/shoulder/thigh bone chain)
def chain(i):
    c = [];
    while i is not None and i >= 0:
        c.append(names[i]); p = parent[i]; i = None if p == i else p
    return c
kids = defaultdict(list)
for i, p in enumerate(parent):
    if p is not None and p >= 0 and p != i: kids[p].append(i)
# a limb root: a bone whose subtree reaches the ground (min bind y of its vertices < 3% of height) and that is a child of the spine
ys = [v[0][1] for v in V]; ymin, ymax = min(ys), max(ys)
dom = [max(ws, key=lambda x: x[1])[0] for _, ws in V]
def subtree(i):
    s = [i]; [s.extend(subtree(k)) for k in kids[i]]; return s
low = {dom[k] for k in range(len(V)) if V[k][0][1] < ymin + 0.03 * (ymax - ymin)}
limb_roots = []
for i in range(nb):
    st = set(subtree(i))
    if st & low and not (set(subtree(parent[i])) - st) & low if False else False: pass
# simpler: walk up from each foot bone until the parent's subtree contains another foot
feet = sorted(low)
for f in feet:
    i = f
    while True:
        p = parent[i]
        if p is None or p < 0 or p == i: break
        if len(set(subtree(p)) & low) > len(set(subtree(i)) & low): break
        i = p
    limb_roots.append(i)
limb_roots = sorted(set(limb_roots))
# a toe that reaches the ground on its own bone is part of its leg, not a limb of its own
limb_roots = [r for r in limb_roots if not any(o != r and r in subtree(o) for o in limb_roots)]
limb_bones = {b: r for r in limb_roots for b in subtree(r)}
print('limb chains:', [' > '.join(names[b] for b in sorted(subtree(r))) for r in limb_roots])

body_only = [k for k in range(len(V)) if all(b not in limb_bones for b, _ in V[k][1])]
limb_only = [k for k in range(len(V)) if all(b in limb_bones for b, _ in V[k][1])]
mixed = [k for k in range(len(V)) if k not in set(body_only) | set(limb_only)]
print('corners: body-only %d, limb-only %d, BLENDED body+limb %d' % (len(body_only), len(limb_only), len(mixed)))
mix_tri = sum(1 for t in T if any(k in set(body_only) for k in t) and any(k in set(limb_only) | set(mixed) for k in t))
print('triangles touching body-only AND limb-weighted corners (the shared skin at the joint): %d of %d' % (mix_tri, len(T)))
# where are the blended corners, as a fraction of height, and what do they mix
for r in limb_roots:
    m = [k for k in mixed if any(limb_bones.get(b) == r for b, _ in V[k][1])]
    if not m: continue
    hy = sorted((V[k][0][1] - ymin) / (ymax - ymin) for k in m)
    combos = Counter(tuple(sorted(names[b] for b, w in V[k][1] if w > 0.05)) for k in m).most_common(4)
    lw = [sum(w for b, w in V[k][1] if b in limb_bones) for k in m]
    print('  %-14s %2d blended corners at %.0f%%-%.0f%% height, limb share %.2f-%.2f; e.g. %s'
          % (names[r], len(m), 100 * hy[0], 100 * hy[-1], min(lw), max(lw), combos[:2]))
    # the topmost corners that move with the limb (limb share >= 0.3): how high up the body do they go
    hi = max((V[k][0][1] - ymin) / (ymax - ymin) for k in range(len(V)) if sum(w for b, w in V[k][1] if limb_bones.get(b) == r) >= 0.3)
    print('      highest corner with >=30%% weight on this limb: %.0f%% of height' % (100 * hi))

# ---- 2. the walk: per limb bone rotation range, foot attitude and lift through the cycle
wname = sys.argv[3] if len(sys.argv) > 3 else next((n for n in A['anims'] if n.endswith('wl') or 'wl' in n), None)
if wname:
    d, cl = clip(wname); cl = (d, cl)
    N = 24; Ws = [world(pose_at(cl, u / N)) for u in range(N)]
    Wb = world(rest)
    print('\n== walk clip %s, %.2f s' % (wname, d))
    for r in limb_roots:
        line = []
        for b in sorted(subtree(r)):
            # bend of this bone relative to its parent, compared with the bind pose: angle of the relative rotation
            angs = []
            for W in Ws:
                q = qmul(tuple(-c for c in Wb[b][0][:3]) + (Wb[b][0][3],), W[b][0])
                angs.append(2 * math.degrees(math.acos(min(1, abs(q[3])))))
            line.append('%s %3.0f' % (names[b], max(angs)))
        print('  world swing (max deg from bind):', ' | '.join(line))
    # the lowest corners of each limb: lift and tilt over the cycle
    pos0 = skin(Wb)
    for r in limb_roots:
        foot = [k for k in range(len(V)) if dom[k] in subtree(r) and V[k][0][1] < ymin + 0.06 * (ymax - ymin)]
        if not foot: continue
        lifts, tilts = [], []
        for W in Ws:
            P = skin(W); fy = [P[k][1] for k in foot]
            lifts.append(min(fy) - ymin); tilts.append(max(fy) - min(fy))
        b0 = [pos0[k][1] for k in foot]
        print('  %-14s foot: bind spread %.3f | lift 0..%.3f m | foot tilt (height spread) %.3f..%.3f m | grounded %d/%d frames'
              % (names[r], max(b0) - min(b0), max(lifts), min(tilts), max(tilts), sum(1 for l in lifts if l < 0.01 * (ymax - ymin)), N))
    # does the body skin at the junction stretch? distance change of junction edges over the cycle
    E = {tuple(sorted((a, b))) for t in T for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))}
    J = [e for e in E if (e[0] in set(body_only)) != (e[1] in set(body_only))]
    P0 = skin(Wb); worst = 0
    for W in Ws:
        P = skin(W)
        for a, b in J:
            l0 = math.dist(P0[a], P0[b]); l = math.dist(P[a], P[b])
            if l0 > 1e-4: worst = max(worst, abs(l / l0 - 1))
    print('  junction edges: %d; max stretch over the walk %.0f%%' % (len(J), 100 * worst))
