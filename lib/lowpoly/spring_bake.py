"""Bake secondary motion into a model's clips: spring bones with gravity, drag and collision spheres, written back as keyframes.

Game engines of the target era play baked keyframe clips, not live physics. Parts that should lag, swing and droop (a bird's
primaries on the downstroke, a tail behind a walk, ears, a crest, a trunk) are therefore simulated once here and stored as
ordinary rotation keys. The method follows the VRM spring bone (the open VRM specification; pixiv's MIT-licensed three-vrm
implements it), written from the description, not copied: each spring bone's tail point carries inertia, is pulled back toward
where the animation puts it (stiffness), loses speed (drag), falls (gravity), keeps the bone's length, and is pushed out of
any collision sphere. The bone is then turned so it points at that tail.

Config (JSON):
  {"chains": [{"bones": ["tail2", "tail3", "tail4"], "stiffness": 1.0, "drag": 0.4, "gravity": 0.3,
               "gravity_dir": [0, -1, 0], "tip_length": 0.08}],
   "colliders": [{"bone": "pelvis", "offset": [0, 0, 0], "radius": 0.12}],
   "clips": ["walk", "flap"], "fps": 60, "keys": 24, "warmup": 2}
- bones: a chain, parent first; each must be the child of the one before (the first may hang off any bone). Branching
  parts (feather bones on the arm, forearm and hand) are one chain per branch; a one-bone chain is fine.
- clips (per chain, optional): the clips this chain bakes in, so a part can be loose in one clip and stiff in another by
  listing it twice with different settings (a soaring wing's primaries droop; the same bones in the flap only lag). Every listed bone
  swings; its tail is its child's joint, or for the last bone, a point tip_length along the bone's own direction (default: the
  previous bone's length).
- per_clip (per chain, optional): {"attack": {"stiffness": 12}, "soar": {"gravity": 2}}: the same chain with other
  stiffness, drag or gravity in the named clips (a fast swoop needs stiffer ears than a hover), without listing it twice.
- stiffness: how hard the tail returns to where the animation puts it, in bone lengths per second (VRM's stiffness force,
  scaled by the bone's length so animals of any size respond alike); 0 hangs free. drag 0..1: the share of speed lost each
  step. gravity: bone lengths per second along gravity_dir (VRM's gravity power, scaled the same way). Per chain. Start with
  stiffness 4-8, drag 0.3-0.5, gravity 0-2, and raise stiffness if a part swings too far.
- colliders: spheres carried by bones (offset in the bone's frame); tails are kept outside them.
- ground: the floor's height that no tail goes below (default: the bind pose's lowest point); null turns it off.
- clips: which clips to bake (default: every clip). Each clip is run warmup + 1 times as a loop at fps, and the last loop is
  sampled into `keys` evenly spaced rotation keys ("clip_keys": {"hover": 84} gives a long clip more of them, so a 4 s loop
  is not sampled as coarsely as a 0.8 s one) (plus the end key equal to the first, so the loop is seamless); how far the
  loop's start and end disagreed before that is reported, as a check that the warm-up was long enough.
Only the chain bones' rotation keys change; positions, other bones, the mesh and the texture are kept. Standard library only."""
import base64, json, math, struct

# ---------------------------------------------------------------- quaternions (x, y, z, w)


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qconj(q): return (-q[0], -q[1], -q[2], q[3])


def qrot(q, v):
    x, y, z, w = q; vx, vy, vz = v
    tx, ty, tz = 2 * (y * vz - z * vy), 2 * (z * vx - x * vz), 2 * (x * vy - y * vx)
    return (vx + w * tx + y * tz - z * ty, vy + w * ty + z * tx - x * tz, vz + w * tz + x * ty - y * tx)


def qnorm(q):
    n = math.sqrt(sum(c * c for c in q)) or 1.0
    return tuple(c / n for c in q)


def slerp(a, b, t):
    d = sum(x * y for x, y in zip(a, b))
    if d < 0: b = tuple(-x for x in b); d = -d
    if d > 0.9995: return qnorm(tuple(x + (y - x) * t for x, y in zip(a, b)))
    th = math.acos(d); s = math.sin(th)
    return qnorm(tuple((math.sin((1 - t) * th) * x + math.sin(t * th) * y) / s for x, y in zip(a, b)))


def from_to(u, v):
    """the shortest rotation taking unit vector u onto unit vector v"""
    d = sum(a * b for a, b in zip(u, v))
    if d < -0.999999:                                       # opposite: any perpendicular axis
        ax = (1, 0, 0) if abs(u[0]) < 0.9 else (0, 1, 0)
        c = (u[1] * ax[2] - u[2] * ax[1], u[2] * ax[0] - u[0] * ax[2], u[0] * ax[1] - u[1] * ax[0])
        return qnorm(c + (0.0,))
    c = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return qnorm((c[0], c[1], c[2], 1 + d))


def unit(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / n for c in v)


def angle(a, b):
    return math.degrees(2 * math.acos(min(1.0, abs(sum(x * y for x, y in zip(a, b))))))


# ---------------------------------------------------------------- clips in the layout's encoding


def decode_clip(src, nb):
    """[(rotation keys [(t, x, y, z, w)], position keys [(t, x, y, z)]) per bone]"""
    raw = base64.b64decode(src['k']); f = struct.unpack('<%df' % (len(raw) // 4), raw); p = 0; out = []
    for _ in range(nb):
        nr, npos = int(f[p]), int(f[p + 1]); p += 2
        rot = [tuple(f[p + 5 * k:p + 5 * k + 5]) for k in range(nr)]; p += 5 * nr
        pos = [tuple(f[p + 4 * k:p + 4 * k + 4]) for k in range(npos)]; p += 4 * npos
        out.append((rot, pos))
    return out


def encode_clip(keys):
    buf = []
    for rot, pos in keys:
        buf += [float(len(rot)), float(len(pos))]
        for k in rot: buf += list(k)
        for k in pos: buf += list(k)
    return base64.b64encode(struct.pack('<%df' % len(buf), *buf)).decode()


def sample(keys, u, n):
    if not keys: return None
    if len(keys) == 1: return tuple(keys[0][1:])
    k = 0
    while k < len(keys) - 2 and keys[k + 1][0] <= u: k += 1
    t0, t1 = keys[k][0], keys[k + 1][0]; f = min(1, max(0, (u - t0) / (t1 - t0))) if t1 > t0 else 0
    a, b = tuple(keys[k][1:]), tuple(keys[k + 1][1:])
    return slerp(a, b, f) if n == 4 else tuple(x + (y - x) * f for x, y in zip(a, b))


# ---------------------------------------------------------------- the bake


class BakeError(Exception):
    """a mistake in the config: the message says what"""


def bake(A, cfg):
    """bake cfg's springs into A's clips in place; returns a report (list of lines)"""
    names, par = A['bones'], A['parent']; nb = len(names)
    def parent(i): p = par[i]; return p if p is not None and p >= 0 and p != i else None
    rest = [(tuple(A['rest'][i * 7:i * 7 + 4]), tuple(A['rest'][i * 7 + 4:i * 7 + 7])) for i in range(nb)]
    idx = {n: i for i, n in enumerate(names)}
    def bone(n, what):
        if n not in idx: raise BakeError('%s: no bone %r (bones: %s)' % (what, n, ', '.join(names)))
        return idx[n]
    chains = []
    for c in cfg.get('chains') or []:
        bs = [bone(n, 'chain') for n in c.get('bones') or []]
        if not bs: raise BakeError('a chain has no "bones"')
        for a, b in zip(bs, bs[1:]):
            if parent(b) != a: raise BakeError('chain %s: %s is not the child of %s' % (c['bones'], names[b], names[a]))
        chains.append({'bones': bs, 'stiffness': float(c.get('stiffness', 1.0)), 'drag': min(1.0, max(0.0, float(c.get('drag', 0.4)))),
                       'gravity': float(c.get('gravity', 0.0)), 'gdir': unit(tuple(c.get('gravity_dir', (0, -1, 0)))),
                       'tip': c.get('tip_length'), 'clips': list(c.get('clips') or []), 'per_clip': dict(c.get('per_clip') or {})})
        for cl, ov in chains[-1]['per_clip'].items():
            bad = set(ov) - {'stiffness', 'drag', 'gravity'}
            if bad: raise BakeError('chain %s: per_clip %s may set stiffness, drag and gravity, not %s' % (c['bones'], cl, ', '.join(sorted(bad))))
    if not chains: raise BakeError('no "chains" in the config')
    cols = [(bone(c['bone'], 'collider'), tuple(c.get('offset', (0, 0, 0))), float(c['radius'])) for c in cfg.get('colliders') or []]
    ground = cfg.get('ground', 'bind')
    if ground == 'bind':
        raw = b''.join(base64.b64decode(s_['v']) for s_ in A['subs'])
        ground = min(struct.unpack_from('<f', raw, k + 4)[0] for k in range(0, len(raw), 64))
    fps = float(cfg.get('fps', 60)); nkeys = int(cfg.get('keys', 24)); warm = int(cfg.get('warmup', 2))
    clips = cfg.get('clips') or list(A.get('anims', {}))
    for c in clips + [k for ch in chains for k in ch['clips']]:
        if c not in A.get('anims', {}): raise BakeError('no clip %r (clips: %s)' % (c, ', '.join(A.get('anims', {}))))
    all_chains = chains
    kids = {i: [k for k in range(nb) if parent(k) == i] for i in range(nb)}
    order = []                                               # parents before children
    seen = set()
    def visit(i):
        if i in seen: return
        if parent(i) is not None: visit(parent(i))
        seen.add(i); order.append(i)
    for i in range(nb): visit(i)
    report = []

    for cname in clips:
        chains = [dict(ch, **{k: float(v) for k, v in ch['per_clip'].get(cname, {}).items()})      # the chains this clip bakes,
                  for ch in all_chains if not ch['clips'] or cname in ch['clips']]                  # with this clip's own settings
        if not chains: report.append('clip %s: no chain applies, left as it was' % cname); continue
        spring = {b for ch in chains for b in ch['bones']}
        src = A['anims'][cname]; dur = src['d'] if src.get('d', 0) > 0 else 1.0
        keys = decode_clip(src, nb)
        def local(i, u):
            rk, pk = keys[i]
            return (sample(rk, u, 4) or rest[i][0], sample(pk, u, 3) or rest[i][1])
        def world_of(loc):
            W = [None] * nb
            for i in order:
                q, p = loc[i]; pi = parent(i)
                if pi is None: W[i] = (q, p)
                else:
                    pq, pp = W[pi]; W[i] = (qmul(pq, q), tuple(a + b for a, b in zip(pp, qrot(pq, p))))
            return W
        # each spring bone's axis (towards its tail) and length, in its own frame, from the bind pose
        Wr = world_of(rest)
        axis, length = {}, {}
        for ch in chains:
            for k, b in enumerate(ch['bones']):
                tail_kids = [c for c in kids[b] if c in ch['bones']] or kids[b]
                if tail_kids: tw = Wr[tail_kids[0]][1]
                else:
                    prev = Wr[parent(b)][1] if parent(b) is not None else Wr[b][1]
                    d = unit(tuple(a - c for a, c in zip(Wr[b][1], prev))); L = ch['tip'] or math.dist(Wr[b][1], prev) or 0.05
                    tw = tuple(a + L * c for a, c in zip(Wr[b][1], d))
                v = tuple(a - c for a, c in zip(tw, Wr[b][1])); length[b] = math.sqrt(sum(c * c for c in v)) or 1e-6
                axis[b] = unit(qrot(qconj(Wr[b][0]), v))
        steps = max(8, int(round(dur * fps))); dt = dur / steps
        state = {}                                           # bone -> (tail now, tail before)
        sampled = {b: [] for b in spring}; dev = {b: 0.0 for b in spring}
        first_loop_end = {}
        total = (warm + 1) * steps
        for n in range(total + 1):
            u = (n % steps) / steps
            loc = [local(i, u) for i in range(nb)]
            anim = [l[0] for l in loc]
            W = [None] * nb
            for i in order:                                  # forward kinematics, turning each spring bone as it is reached
                q, p = loc[i]; pi = parent(i)
                pq, pp = ((0, 0, 0, 1), (0, 0, 0)) if pi is None else W[pi]
                head = tuple(a + b for a, b in zip(pp, qrot(pq, p))) if pi is not None else p
                if i in spring:
                    target_rot = qmul(pq, q)
                    goal = tuple(h + length[i] * a for h, a in zip(head, qrot(target_rot, axis[i])))
                    ch = next(c for c in chains if i in c['bones'])
                    cur, prev = state.get(i, (goal, goal))
                    # VRM's step: keep moving (less the drag), pulled toward the animated direction (stiffness) and down
                    # (gravity); both terms in bone lengths per second, so animals of any size respond alike
                    pull = unit(tuple(g - h for g, h in zip(goal, head)))
                    nxt = tuple(c + (c - pv) * (1 - ch['drag']) + a * ch['stiffness'] * dt * length[i] + g * ch['gravity'] * dt * length[i]
                                for c, pv, a, g in zip(cur, prev, pull, ch['gdir']))
                    for cb, off, r in cols:                  # stay outside every collision sphere
                        if W[cb] is None: continue
                        cq, cp = W[cb]; cc = tuple(a + b for a, b in zip(cp, qrot(cq, off)))
                        d = tuple(a - b for a, b in zip(nxt, cc)); dl = math.sqrt(sum(x * x for x in d))
                        if dl < r: nxt = tuple(c + x / (dl or 1e-6) * r for c, x in zip(cc, d))
                    if ground is not None and nxt[1] < ground: nxt = (nxt[0], float(ground), nxt[2])
                    nxt = tuple(h + length[i] * a for h, a in zip(head, unit(tuple(x - h for x, h in zip(nxt, head)))))
                    state[i] = (nxt, cur)
                    # the bone's world rotation: the animated one, turned so its axis points at the tail
                    want = unit(tuple(x - h for x, h in zip(nxt, head)))
                    now = qrot(target_rot, axis[i])
                    wrot = qmul(from_to(now, want), target_rot)
                    q = qnorm(qmul(qconj(pq), wrot)) if pi is not None else wrot
                    loc[i] = (q, p)
                    if n >= warm * steps and n < total:
                        sampled[i].append((u, q)); dev[i] = max(dev[i], angle(q, anim[i]))
                    if n == warm * steps: first_loop_end[i] = q
                    if n == total: first_loop_end[i] = (first_loop_end[i], q)
                W[i] = (qmul(pq, loc[i][0]) if pi is not None else loc[i][0], head if pi is not None else p)
        # write the sampled rotations back as keys (evenly spaced), the end key equal to the first: a seamless loop
        newkeys = list(keys)
        for b in spring:
            s = sampled[b]
            rk = []
            nk = int((cfg.get('clip_keys') or {}).get(cname, nkeys))
            for k in range(nk):
                u = k / nk; j = min(range(len(s)), key=lambda m: abs(s[m][0] - u))
                rk.append((u,) + tuple(s[j][1]))
            rk.append((1.0,) + tuple(rk[0][1:]))
            newkeys[b] = (rk, keys[b][1])
        A['anims'][cname] = dict(src, k=encode_clip(newkeys))
        seam = max(angle(*first_loop_end[b]) for b in spring)
        report.append('clip %s (%.2f s, %d steps a loop, %d warm-up loops): %s | loop seam before closing %.1f deg%s'
                      % (cname, dur, steps, warm, ', '.join('%s %.0f deg' % (names[b], dev[b]) for b in sorted(spring, key=lambda b: names[b])),
                         seam, ' (raise warmup)' if seam > 5 else ''))
    return report


def bake_file(model, config, out):
    """read a glTF, bake, write it to out (with its .bin and texture); returns the report"""
    from lowpoly import gltf_io
    A, tex = gltf_io.read_gltf(model)
    try: cfg = json.load(open(config, encoding='utf-8'))
    except ValueError as e: raise BakeError('config is not valid JSON (%s): %s' % (config, e))
    report = bake(A, cfg)
    gltf_io.write_gltf(A, out, tex)
    return ['largest turn away from the animation, per bone:'] + report
