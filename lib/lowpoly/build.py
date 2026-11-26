"""Build a model the way the measured models were built: one half, mirrored and welded, then posed, on one mirrored pelt.
Standard library only.

Why a half: both sides then match by construction, in vertices, triangles, winding and texels. Builds that made each side
separately drifted apart three times in one animal (an ear at another angle, teeth turned inside out, stitches that differed
side to side), and each was a round of review (lowpoly-core SKILL.md 3, "Build one half").

    from lowpoly.build import Half, pose_x, to_model
    h = Half()
    a = h.arc([(0, .76, .3), (.10, .70, .3), (.13, .55, .3), (.09, .40, .3), (0, .36, .3)], {'chest': 1.0}, 'body')
    b = h.arc([...], {...}, 'body')            # an arc runs from the top midline to the bottom midline, x >= 0
    h.strip(a, b)                              # stitches two arcs of any vertex counts
    hole = [a[2], a[3], b[3], b[2]]            # a limb grows from a hole: leave the quad out, bridge a loop to it
    h.loop_bridge(hole, h.loop([...], {...}, 'leg'))
    m = h.mirror_and_weld()                    # the whole skin: midline vertices (x = 0) are shared, the rest twinned
    m.fix_winding()                            # every closed piece faces outward
    uv = m.pelt_uv()                           # one UV per vertex: a mirrored side-view pelt, the back and belly unrolled
    P2, J2 = pose_x(m, joints, parents, {'thigh_L': 0.15, 'thigh_R': -0.15})   # step the stance off-centre for the bind pose
    A = to_model(m, bones, parents, joints, uv, name='animal')                # the plugin's layout, for gltf_io.write_gltf

Bones named with a side take a pattern: weights written for the left as {'thigh_L': 1} become {'thigh_R': 1} on the right
(the suffixes _L/_R, or a function passed as mirror_bone)."""
import base64, math, struct


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _len(a): return math.sqrt(_dot(a, a))
def _norm(a):
    l = _len(a) or 1.0; return (a[0] / l, a[1] / l, a[2] / l)


def _swap_side(name):
    if name.endswith('_L'): return name[:-2] + '_R'
    if name.endswith('_R'): return name[:-2] + '_L'
    return name


class Half:
    """the left half of a model (x >= 0): vertices with weights and a part label, and triangles"""

    def __init__(self, midline=1e-6):
        self.P, self.W, self.part, self.F, self.eps = [], [], [], [], midline

    def v(self, p, w, part='body'):
        if p[0] < -self.eps: raise ValueError('a half-model vertex must have x >= 0: %r' % (p,))
        self.P.append((0.0 if abs(p[0]) <= self.eps else float(p[0]), float(p[1]), float(p[2])))
        self.W.append(dict(w)); self.part.append(part); return len(self.P) - 1

    def arc(self, pts, w, part='body'):
        """an open row of vertices, by convention from the top midline to the bottom midline"""
        return [self.v(p, w, part) for p in pts]

    loop = arc      # a closed row (a limb's ring): the same vertices, stitched with loop_bridge

    def tri(self, a, b, c):
        if len({a, b, c}) == 3: self.F.append((a, b, c))

    def quad(self, a, b, c, d):
        """a-b-c-d round the quad, split on the shorter diagonal (the same choice on both sides after mirroring)"""
        if math.dist(self.P[a], self.P[c]) <= math.dist(self.P[b], self.P[d]): self.tri(a, b, c); self.tri(a, c, d)
        else: self.tri(a, b, d); self.tri(b, c, d)

    def strip(self, A, B, skip=()):
        """stitch two open rows of any vertex counts, walking both by their share of length; skip names (i, j) pairs of
        A's segment indices to leave out as a hole (use it with equal counts)"""
        def shares(L):
            d = [0.0]
            for k in range(1, len(L)): d.append(d[-1] + math.dist(self.P[L[k - 1]], self.P[L[k]]))
            t = d[-1] or 1.0; return [x / t for x in d]
        ta, tb = shares(A), shares(B); i = j = 0
        if len(A) == len(B):
            for k in range(len(A) - 1):
                if k not in skip: self.quad(A[k], A[k + 1], B[k + 1], B[k])
            return
        while i < len(A) - 1 or j < len(B) - 1:
            if j >= len(B) - 1 or (i < len(A) - 1 and ta[i + 1] <= tb[j + 1]):
                self.tri(A[i], A[i + 1], B[j]); i += 1
            else:
                self.tri(A[i], B[j + 1], B[j]); j += 1

    def loop_bridge(self, A, B):
        """stitch two closed loops of any vertex counts, in angle order round the axis between their centres"""
        P = self.P
        cen = lambda L: _mul(tuple(map(sum, zip(*[P[i] for i in L]))), 1.0 / len(L))
        ca, cb = cen(A), cen(B); ax = _norm(_sub(cb, ca))
        def turn(L, c):
            s = (0.0, 0.0, 0.0)
            for k in range(len(L)): s = _add(s, _cross(_sub(P[L[k]], c), _sub(P[L[(k + 1) % len(L)]], c)))
            return _dot(s, ax)
        if (turn(A, ca) > 0) != (turn(B, cb) > 0): B = B[::-1]
        ref = _sub(P[A[0]], ca); ref = _norm(_sub(ref, _mul(ax, _dot(ref, ax)))); oth = _cross(ax, ref)
        sgn = 1 if turn(A, ca) > 0 else -1
        ang = lambda i, c: math.atan2(_dot(_sub(P[i], c), oth), _dot(_sub(P[i], c), ref)) * sgn
        k0 = min(range(len(B)), key=lambda k: abs((ang(B[k], cb) - ang(A[0], ca) + math.pi) % (2 * math.pi) - math.pi))
        B = B[k0:] + B[:k0]
        def unwrap(L, c, off=0.0):
            out = [off]
            for k in range(1, len(L)): out.append(out[-1] + (ang(L[k], c) - ang(L[k - 1], c)) % (2 * math.pi))
            return out + [off + 2 * math.pi]
        off = (ang(B[0], cb) - ang(A[0], ca) + math.pi) % (2 * math.pi) - math.pi
        ta, tb = unwrap(A, ca), unwrap(B, cb, off); i = j = 0; m, n = len(A), len(B)
        while i < m or j < n:
            if j >= n or (i < m and ta[i + 1] <= tb[j + 1]): self.tri(A[i % m], A[(i + 1) % m], B[j % n]); i += 1
            else: self.tri(A[i % m], B[(j + 1) % n], B[j % n]); j += 1

    def fan(self, L, c, closed=False):
        for k in range(len(L) - (0 if closed else 1)): self.tri(L[k], L[(k + 1) % len(L)], c)

    def cap(self, L):
        """close a loop flat without a centre vertex (a sole, a muzzle's end)"""
        for k in range(1, len(L) - 1): self.tri(L[0], L[k], L[k + 1])

    def mirror_and_weld(self, mirror_bone=_swap_side):
        """the whole skin: every vertex off the midline gets a twin at -x with its weights' bones swapped side for side;
        every triangle gets its mirror image. Midline vertices are shared, so the centre is welded by construction."""
        m = Mesh(); twin = {}
        for i, p in enumerate(self.P):
            m.P.append(p); m.W.append(dict(self.W[i])); m.part.append(self.part[i])
        for i, p in enumerate(self.P):
            if p[0] == 0.0: twin[i] = i; continue
            twin[i] = len(m.P); m.P.append((-p[0], p[1], p[2]))
            w = {}
            for b, x in self.W[i].items(): w[mirror_bone(b)] = w.get(mirror_bone(b), 0.0) + x
            m.W.append(w); m.part.append(self.part[i])
        for i in list(twin):                         # a midline vertex weighted to one side's bone: share it between the two
            if twin[i] == i:
                w = {}
                for b, x in m.W[i].items():
                    for bb in {b, mirror_bone(b)}: w[bb] = w.get(bb, 0.0) + x / len({b, mirror_bone(b)})
                m.W[i] = w
        for a, b, c in self.F:
            m.F.append((a, b, c))
            t = (twin[a], twin[c], twin[b])            # mirrored, with the winding turned so it faces the same way out
            if len(set(t)) == 3 and set(t) != {a, b, c}: m.F.append(t)
        m.twin = dict(twin); m.twin.update({v: k for k, v in twin.items()})
        return m


class Mesh:
    def __init__(self): self.P, self.W, self.part, self.F, self.twin = [], [], [], [], {}

    def open_edges(self):
        e = {}
        for f in self.F:
            for k in range(3):
                key = (min(f[k], f[(k + 1) % 3]), max(f[k], f[(k + 1) % 3])); e[key] = e.get(key, 0) + 1
        return [k for k, c in e.items() if c != 2]

    def fix_winding(self):
        """consistent winding across shared edges, then each connected piece turned outward by its own signed volume
        (the skin and every separate tooth or claw)"""
        edges = {}
        for fi, f in enumerate(self.F):
            for k in range(3): edges.setdefault((min(f[k], f[(k + 1) % 3]), max(f[k], f[(k + 1) % 3])), []).append(fi)
        seen = [False] * len(self.F); out = list(self.F); P = self.P
        for s0 in range(len(out)):
            if seen[s0]: continue
            seen[s0] = True; stack = [s0]; piece = [s0]
            while stack:
                fi = stack.pop(); f = out[fi]
                for k in range(3):
                    a, b = f[k], f[(k + 1) % 3]
                    for gj in edges[(min(a, b), max(a, b))]:
                        if gj == fi or seen[gj]: continue
                        g = out[gj]
                        if any(g[q] == a and g[(q + 1) % 3] == b for q in range(3)): out[gj] = (g[0], g[2], g[1])
                        seen[gj] = True; stack.append(gj); piece.append(gj)
            if sum(_dot(P[out[i][0]], _cross(P[out[i][1]], P[out[i][2]])) for i in piece) < 0:
                for i in piece: a, b, c = out[i]; out[i] = (a, c, b)
        self.F = out

    def normals(self):
        N = [(0.0, 0.0, 0.0)] * len(self.P)
        for a, b, c in self.F:
            n = _cross(_sub(self.P[b], self.P[a]), _sub(self.P[c], self.P[a]))
            for i in (a, b, c): N[i] = _add(N[i], n)
        return [_norm(n) for n in N]

    def pelt_uv(self, unroll=1.0, margin=0.02):
        """One UV per vertex: a side view shared by both sides (u along the length, v the height), with the surfaces that
        face up or down unrolled past the silhouette by how far in from the side they lie, so the back and the belly get
        texels instead of one row. Parts that overlap in the side view (a leg over the belly, an ear over the crown) still
        share texels: give those their own strip by passing their vertices' UVs through offset_part()."""
        N = self.normals(); X = max(abs(p[0]) for p in self.P) or 1.0
        raw = []
        for p, n in zip(self.P, N):
            lift = unroll * (X - abs(p[0])) * abs(n[1]) * (1 if n[1] >= 0 else -1)
            raw.append((-p[2], -(p[1] + lift)))
        us = [r[0] for r in raw]; vs = [r[1] for r in raw]
        s = (1 - 2 * margin) / max(max(us) - min(us), max(vs) - min(vs), 1e-9)
        return [(margin + (u - min(us)) * s, margin + (v - min(vs)) * s) for u, v in raw]


def pose_x(mesh, joints, parents, angles, names):
    """Turn bones about the x axis (a leg stepped forward or back) and return the posed positions and joints, for a bind
    pose that stands like the animal: build symmetric, then pose. angles: {bone name: radians}; children follow."""
    nb = len(names); idx = {n: i for i, n in enumerate(names)}
    order = sorted(range(nb), key=lambda i: len(_chain(i, parents)))
    M = [None] * nb                                   # per bone: (accumulated angle, pivot before, pivot after)
    newJ = list(joints)
    def rot(v, a):
        c, s = math.cos(a), math.sin(a); return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)
    for i in order:
        p = parents[i]; a = angles.get(names[i], 0.0)
        if p is None: M[i] = (a, joints[i], joints[i]); continue
        pa, p0, p1 = M[p]
        newJ[i] = _add(p1, rot(_sub(joints[i], p0), pa)); M[i] = (pa + a, joints[i], newJ[i])
    out = []
    for p, w in zip(mesh.P, mesh.W):
        acc = (0.0, 0.0, 0.0); tot = sum(w.values()) or 1.0
        for b, x in w.items():
            a, p0, p1 = M[idx[b]]; acc = _add(acc, _mul(_add(p1, rot(_sub(p, p0), a)), x / tot))
        out.append(acc)
    return out, newJ


def _chain(i, parents):
    out = []
    while parents[i] is not None: i = parents[i]; out.append(i)
    return out


def to_model(mesh, names, parents, joints, uv, name='model', positions=None, anims=None, idle=''):
    """the plugin's model layout (gltf_io.write_gltf): one corner per vertex, rest rotations identity"""
    P = positions or mesh.P; N = mesh.normals(); idx = {n: i for i, n in enumerate(names)}
    corners = []
    for i, p in enumerate(P):
        ws = sorted(mesh.W[i].items(), key=lambda kv: -kv[1])[:4]; tot = sum(x for _, x in ws) or 1.0
        ws = [(idx[b], x / tot) for b, x in ws] + [(0, 0.0)] * (4 - len(ws))
        corners.append(struct.pack('<16f', *p, *N[i], *uv[i], *[x for _, x in ws], *[float(b) for b, _ in ws]))
    ix = [k for f in mesh.F for k in f]
    rest, inv = [], []
    for i in range(len(names)):
        loc = joints[i] if parents[i] is None else _sub(joints[i], joints[parents[i]])
        rest += [0.0, 0.0, 0.0, 1.0] + list(loc); inv += [0.0, 0.0, 0.0, 1.0] + [-c for c in joints[i]]
    return {'id': name, 'name': name, 'tex': [name], 'bones': list(names), 'parent': list(parents), 'rest': rest, 'inv': inv,
            'subs': [{'v': base64.b64encode(b''.join(corners)).decode(),
                      'i': base64.b64encode(struct.pack('<%dH' % len(ix), *ix)).decode(), 'r': [[0, 0, len(mesh.F)]]}],
            'anims': anims or {}, 'idle': idle}


def _selftest():
    """a body of three arcs with a nose and a tail point and one leg from a hole: closed, mirrored, one UV per vertex"""
    h = Half(); sh = [(0, 1.0), (0.7, 0.85), (1.0, 0.5), (0.7, 0.15), (0, 0.0)]
    arcs = [h.arc([(hw * sx, 0.4 + 0.3 * sy, z) for sx, sy in sh], {'spine': 1.0}) for z, hw in ((0.4, 0.10), (0.0, 0.14), (-0.4, 0.10))]
    nose = h.v((0, 0.55, 0.6), {'spine': 1.0}); tail = h.v((0, 0.55, -0.6), {'spine': 1.0})
    h.fan(arcs[0][::-1], nose); h.fan(arcs[2], tail)
    h.strip(arcs[0], arcs[1], skip=(2,)); h.strip(arcs[1], arcs[2])
    hole = [arcs[0][2], arcs[0][3], arcs[1][3], arcs[1][2]]
    knee = h.loop([(0.10 + dx, 0.2, 0.2 + dz) for dx, dz in ((0, 0.04), (0.04, 0), (0, -0.04), (-0.04, 0))], {'leg_L': 1.0}, 'leg')
    sole = h.loop([(0.10 + dx, 0.0, 0.2 + dz) for dx, dz in ((0, 0.05), (0.05, 0), (0, -0.05), (-0.05, 0))], {'leg_L': 1.0}, 'leg')
    h.loop_bridge(hole, knee); h.loop_bridge(knee, sole); h.cap(sole)
    m = h.mirror_and_weld(); m.fix_winding(); uv = m.pelt_uv()
    assert not m.open_edges(), m.open_edges()
    assert len(uv) == len(m.P) and all(0 <= u <= 1 and 0 <= v <= 1 for u, v in uv)
    left = sum(1 for f in m.F if sum(m.P[i][0] for i in f) > 0); right = sum(1 for f in m.F if sum(m.P[i][0] for i in f) < 0)
    assert left == right, (left, right)
    vol = sum(_dot(m.P[a], _cross(m.P[b], m.P[c])) for a, b, c in m.F) / 6
    assert vol > 0, vol
    names = ['spine', 'leg_L', 'leg_R']; parents = [None, 0, 0]; joints = [(0, 0.55, 0), (0.10, 0.4, 0.2), (-0.10, 0.4, 0.2)]
    P2, J2 = pose_x(m, joints, parents, {'leg_L': 0.3, 'leg_R': -0.3}, names)
    assert abs(P2[sole[0]][2] - m.P[sole[0]][2]) > 0.05
    A = to_model(m, names, parents, J2, uv, positions=P2)
    print('selftest ok: %d vertices, %d triangles (left %d, right %d), closed, volume %.4f m3, %d corners'
          % (len(m.P), len(m.F), left, right, vol, len(base64.b64decode(A['subs'][0]['v'])) // 64))
    return A


if __name__ == '__main__':
    import sys
    A = _selftest()
    if len(sys.argv) > 1:
        from lowpoly import gltf_io
        gltf_io.write_gltf(A, sys.argv[1]); print('wrote', sys.argv[1])
