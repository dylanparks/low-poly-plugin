"""Remove slivers from a finished, consistently wound closed mesh, without changing its shape (lowpoly-core §3; lowpoly-animals/references/heads.md:
visible slivers under an aspect of about 10). Two passes:

1. Weld near-duplicate vertices: an edge shorter than `short` (3-6 mm pairs left where two construction steps put a vertex in
   almost the same place) is collapsed to its midpoint. Its two triangles go away, so this also lowers the triangle count.
2. Flip shared edges where that thins neither triangle: for two triangles that make a nearly flat quad (under `flat` degrees
   between them), the quad's other diagonal is used when it lowers the worse of the two triangles' aspect.

Aspect = longest edge squared over twice the area (1.15 for an equilateral triangle; the same measure as thin_triangles.py).
`verts` is a list of [position, weights]; `faces` a list of index triples, edited in place. `face_maps` are dicts or sets keyed
by frozenset(face) (regions such as the ears): a flip or weld is only made inside one region and the keys are carried along.
`frozen(i)` marks vertices that must not move (for example ones a UV patch is built from)."""
import math


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _len(a): return math.sqrt(_dot(a, a))


def aspect(P, f):
    p = [P[i] for i in f]; e = [_len(_sub(p[a], p[b])) for a, b in ((0, 1), (1, 2), (2, 0))]
    area = _len(_cross(_sub(p[1], p[0]), _sub(p[2], p[0]))) / 2
    return max(e) ** 2 / (2 * area) if area > 1e-14 else 1e9


def _normal(P, f):
    n = _cross(_sub(P[f[1]], P[f[0]]), _sub(P[f[2]], P[f[0]])); l = _len(n)
    return (n[0] / l, n[1] / l, n[2] / l) if l > 1e-14 else (0.0, 0.0, 0.0)


def _region(face_maps, f):
    k = frozenset(f)
    return tuple((('in', m[k]) if isinstance(m, dict) else ('in',)) if k in m else ('out',) for m in face_maps)


def _rekey(face_maps, old, new_faces):
    for m in face_maps:
        hit = [frozenset(f) for f in old if frozenset(f) in m]
        if not hit: continue
        val = m[hit[0]] if isinstance(m, dict) else None
        for k in hit:
            if isinstance(m, dict): del m[k]
            else: m.discard(k)
        for f in new_faces:
            if isinstance(m, dict): m[frozenset(f)] = val
            else: m.add(frozenset(f))


def tidy(verts, faces, face_maps=(), frozen=lambda i: False, short=0.004, flat=25.0, worst=6.0, only=lambda f: True):
    """`only(face)` limits both passes to some faces (a region of a model whose other parts have their own UV rules)."""
    P = [v[0] for v in verts]
    report = {'welded': 0, 'flipped': 0, 'tris_before': len(faces)}
    # ---- 1. weld near-duplicates
    while True:
        edges = {}
        for fi, f in enumerate(faces):
            for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])): edges.setdefault(frozenset((a, b)), []).append(fi)
        cands = sorted((_len(_sub(P[a], P[b])), a, b) for (a, b), fs in ((tuple(k), v) for k, v in edges.items()) if len(fs) == 2)
        done = False
        for d, a, b in cands:
            if d >= short: break
            if frozen(a) or frozen(b): continue
            fa, fb = edges[frozenset((a, b))]
            if not (only(faces[fa]) and only(faces[fb])): continue
            if _region(face_maps, faces[fa]) != _region(face_maps, faces[fb]): continue
            na = {i for f in faces if a in f for i in f} - {a}; nb = {i for f in faces if b in f for i in f} - {b}
            opp = {i for i in faces[fa] + faces[fb] if i not in (a, b)}
            if (na & nb) != opp: continue                                    # the link condition: the skin stays a closed manifold
            # a vertex on the midline stays there (a mirrored model stays mirrored); otherwise the midpoint
            m = P[a] if abs(P[a][0]) < 1e-5 else P[b] if abs(P[b][0]) < 1e-5 else tuple((P[a][k] + P[b][k]) / 2 for k in range(3))
            touched = [fi for fi, f in enumerate(faces) if (a in f or b in f) and fi not in (fa, fb)]
            before = {fi: _normal(P, faces[fi]) for fi in touched}
            new = {fi: tuple(a if i == b else i for i in faces[fi]) for fi in touched}
            Pm = list(P); Pm[a] = m
            if any(_dot(before[fi], _normal(Pm, new[fi])) < 0.5 for fi in touched): continue   # no triangle may turn over
            old_faces = [faces[fi] for fi in touched] + [faces[fa], faces[fb]]
            for fi in touched: faces[fi] = new[fi]
            _rekey(face_maps, old_faces, [faces[fi] for fi in touched])
            for fi in sorted((fa, fb), reverse=True): del faces[fi]
            P[a] = m; verts[a][0] = m; report['welded'] += 1; done = True
            break
        if not done: break
    # ---- 2. flip diagonals of nearly flat quads where that thins the worse triangle
    for _ in range(6):
        changed = False
        edges = {}
        for fi, f in enumerate(faces):
            for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])): edges.setdefault((a, b), fi)
        for (a, b), fi in list(edges.items()):
            gi = edges.get((b, a))
            if gi is None or gi < fi: continue
            f, g = faces[fi], faces[gi]
            if not (only(f) and only(g)): continue
            if not (set((a, b)) <= set(f) and set((a, b)) <= set(g)): continue
            c = next(i for i in f if i not in (a, b)); d = next(i for i in g if i not in (a, b))
            if c == d or (c, d) in edges or (d, c) in edges: continue
            old = max(aspect(P, f), aspect(P, g))
            if old < worst: continue
            if _region(face_maps, f) != _region(face_maps, g): continue
            nf, ng = _normal(P, f), _normal(P, g)
            if _dot(nf, ng) < math.cos(math.radians(flat)): continue
            f2, g2 = (a, d, c), (b, c, d)                                    # f = a->b->c, g = b->a->d: same winding after
            n2, m2 = _normal(P, f2), _normal(P, g2)
            avg = tuple(nf[k] + ng[k] for k in range(3))
            if _dot(n2, avg) <= 0 or _dot(m2, avg) <= 0: continue
            if max(aspect(P, f2), aspect(P, g2)) >= old * 0.95: continue
            faces[fi], faces[gi] = f2, g2
            _rekey(face_maps, [f, g], [f2, g2])
            report['flipped'] += 1; changed = True
            edges = {}
            for fj, h in enumerate(faces):
                for x, y in ((h[0], h[1]), (h[1], h[2]), (h[2], h[0])): edges.setdefault((x, y), fj)
        if not changed: break
    report['tris_after'] = len(faces)
    report['worst_aspect'] = round(max(aspect(P, f) for f in faces), 1)
    return report


def mirror_better_side(verts, faces, side_of, eps=1e-4, keep=None):
    """Make a pair of mirrored parts (ears) triangulated alike. A ring-to-ring stitch can pick different diagonals on the two
    sides of a mirrored model, leaving a sliver on one side only. side_of maps frozenset(face) -> +1 / -1 for the part's faces.
    The side whose worst triangle is better is kept; the other side's faces are rebuilt as its mirror (x -> -x, winding
    reversed), matched by position; or the side given as `keep`. Returns (kept side, worst aspect before on each side)."""
    P = [v[0] for v in verts]
    by = {1: [f for f in faces if side_of.get(frozenset(f)) == 1], -1: [f for f in faces if side_of.get(frozenset(f)) == -1]}
    worst = {s: max(aspect(P, f) for f in fs) for s, fs in by.items() if fs}
    if len(worst) < 2: return None, worst
    keep = keep or (1 if worst[1] <= worst[-1] else -1); other = -keep          # `keep` forces a side
    cand = {i for f in by[other] for i in f}
    def twin(i):
        x, y, z = P[i]; j = min(cand, key=lambda c: (P[c][0] + x) ** 2 + (P[c][1] - y) ** 2 + (P[c][2] - z) ** 2)
        if (P[j][0] + x) ** 2 + (P[j][1] - y) ** 2 + (P[j][2] - z) ** 2 > eps ** 2 * 100: raise ValueError('no mirror twin')
        return j
    new = [(twin(f[0]), twin(f[2]), twin(f[1])) for f in by[keep]]
    old = set(map(frozenset, by[other]))
    faces[:] = [f for f in faces if frozenset(f) not in old] + new
    for k in old: del side_of[k]
    for f in new: side_of[frozenset(f)] = other
    return keep, worst


def collapse_collinear(verts, faces, face_maps=(), frozen=lambda i: False, limit=10.0):
    """For a triangle still over `limit` because one vertex lies almost on the opposite edge, collapse that vertex into the
    nearer end of the edge when the skin stays closed, no triangle turns over and the worst aspect round it improves.
    Returns the number of collapses."""
    P = [v[0] for v in verts]; n = 0
    for _ in range(20):
        bad = sorted(((aspect(P, f), f) for f in faces if aspect(P, f) > limit), key=lambda r: -r[0])
        done = False
        for asp_, f in bad:
            e = [(f[0], f[1], f[2]), (f[1], f[2], f[0]), (f[2], f[0], f[1])]
            a, b, c = max(e, key=lambda t: _len(_sub(P[t[0]], P[t[1]])))       # a-b the longest edge, c the vertex on it
            if frozen(c): continue
            for keep in sorted((a, b), key=lambda k: _len(_sub(P[k], P[c]))):
                fa = [fi for fi, g in enumerate(faces) if c in g and keep in g]
                if len(fa) != 2 or _region(face_maps, faces[fa[0]]) != _region(face_maps, faces[fa[1]]): continue
                nk = {i for g in faces if keep in g for i in g} - {keep}; nc = {i for g in faces if c in g for i in g} - {c}
                if (nk & nc) != {i for fi in fa for i in faces[fi] if i not in (keep, c)}: continue
                touched = [fi for fi, g in enumerate(faces) if c in g and fi not in fa]
                new = {fi: tuple(keep if i == c else i for i in faces[fi]) for fi in touched}
                if any(_dot(_normal(P, faces[fi]), _normal(P, new[fi])) < 0.5 for fi in touched): continue
                around_old = max(aspect(P, faces[fi]) for fi in touched + fa)
                if max(aspect(P, new[fi]) for fi in touched) >= around_old: continue
                old_faces = [faces[fi] for fi in touched] + [faces[fi] for fi in fa]
                for fi in touched: faces[fi] = new[fi]
                _rekey(face_maps, old_faces, [faces[fi] for fi in touched])
                for fi in sorted(fa, reverse=True): del faces[fi]
                n += 1; done = True; break
            if done: break
        if not done: break
    return n
