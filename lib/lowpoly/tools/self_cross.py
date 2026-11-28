"""Parts passing through each other in motion: in each of N frames of each clip (and the bind pose), the triangles that
cross a triangle they share no vertex with, named by the bones that own them. The first count is the main skin's own:
teeth, eyes and claws set into it as separate pieces cross it on purpose (lp check mesh.loose checks those).
The second count is the separate pieces': crossings that involve a piece other than the main skin and were not already there
in the bind pose, or that cross in every frame of the clip. A tooth sunk into the gum or a shell's root sunk into the
shoulder crosses on purpose and keeps crossing the same triangles, so it is excused (a piece left visibly poking through for
the whole clip is too: judge that in the renders); a piece that moves through the body or another piece in motion is counted (the
alicorn's resting wing shell crossed the body and the flight wing 124-140 times during its swap while the main skin read 16).

A clean skin creases a little at its joints (fox walk 0-5 crossings in the worst frame, crocodile 12); a wing or limb that
cuts through itself, another part or the body shows tens to hundreds (a folded membrane wing 290-376, the eagle's folded
wing layers about 790 at rest). The rest pose and the walk are where it hides: check it from below and behind too.

  python self_cross.py model.gltf [frames=24] [clip ...] [--where]
      clip "bind" is the bind pose; default every clip and bind. --where also lists, for each clip's worst frame, every
      crossing pair with the two triangles' owning bones, their vertex indices and the crossing's position (the midpoint of
      the two triangles' centres, in model metres), so a fix can go to the right triangles instead of being searched for.

Prints one line per clip:  clip NAME worst N crossings at phase P; frames with more than 12: K of F; pairs: a×b n, ...
and, when the model has separate pieces, one more:  separate pieces, NAME: worst N new crossings at phase P; pairs: ...
"""
import sys, os, math, contextlib, io, tempfile
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'): sys.exit(__doc__)
WHERE = '--where' in sys.argv; _args = [a for a in sys.argv[1:] if a != '--where']
model = _args[0]; N = int(_args[1]) if len(_args) > 1 else 24; clips = _args[2:]
src_path = os.path.join(here, 'preview.py')
head = open(src_path, encoding='utf-8').read().split("# yaw 0 looks at")[0]
g = {'__file__': src_path, '__name__': 'self_cross'}
sys.argv = ['preview.py', model, tempfile.gettempdir(), '-', '0']
with contextlib.redirect_stdout(io.StringIO()): exec(compile(head, src_path, 'exec'), g)
A, T, V, posed = g['A'], g['T'], g['V'], g['posed']
_bad = max((b for v in V for b, w in v[1]), default=-1)
if _bad >= len(A['bones']):
    sys.exit('self_cross: the skin weights a vertex to bone %d, but the model has only %d bones (joints): the file is malformed; '
             're-export it (a joint missing from skins[0].joints, or weights written before a bone was removed)' % (_bad, len(A['bones'])))
names = list(g.get('names') or [b if isinstance(b, str) else b.get('name', str(i)) for i, b in enumerate(A['bones'])])
def owner(ci):
    k = max(V[ci][1], key=lambda x: x[1])[0]
    return names[k] if 0 <= k < len(names) else 'bone%d' % k
clips = clips or ['bind'] + list(A.get('anims', {}))
# only the main skin: teeth, eyes and claws set into it as their own pieces cross it on purpose
P0, _ = posed(None, 0.0); k0 = lambda ci: tuple(round(x, 5) for x in P0[ci])
par = {}
def fnd(x):
    while par.setdefault(x, x) != x: par[x] = par[par[x]]; x = par[x]
    return x
for t in T: par[fnd(k0(t[1]))] = fnd(k0(t[0])); par[fnd(k0(t[2]))] = fnd(k0(t[0]))
size = {}
for t in T: r = fnd(k0(t[0])); size[r] = size.get(r, 0) + 1
main = max(size, key=size.get)
MAIN = [fnd(k0(t[0])) == main for t in T]          # per triangle: on the main skin
PIECES = not all(MAIN)
BIND_X = set()                                     # triangle pairs (by index) involving a piece that cross in the bind pose
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def seg_tri(p, q, a, b, c):
    """does segment pq pass through the inside of triangle abc (Moller-Trumbore, ends and edges excluded)"""
    e1, e2 = sub(b, a), sub(c, a); d = sub(q, p); h = cross(d, e2); det = dot(e1, h)
    if abs(det) < 1e-14: return False
    f = 1 / det; s = sub(p, a); u = f * dot(s, h)
    if u < 1e-6 or u > 1 - 1e-6: return False
    qv = cross(s, e1); v = f * dot(d, qv)
    if v < 1e-6 or u + v > 1 - 1e-6: return False
    t = f * dot(e2, qv); return 1e-6 < t < 1 - 1e-6
def tri_x(P3, Q3):
    return any(seg_tri(P3[i], P3[(i + 1) % 3], *Q3) for i in range(3)) or any(seg_tri(Q3[i], Q3[(i + 1) % 3], *P3) for i in range(3))
def frame_x(P, main_only):
    """the crossing triangle pairs in one pose, as (index i, index j) into T; main_only keeps the main skin's triangles"""
    key = lambda ci: tuple(round(x, 5) for x in P[ci])
    idx = [k for k, t in enumerate(T) if (MAIN[k] or not main_only) and len({key(c) for c in t}) == 3]   # a collapsed (hidden) triangle never crosses
    W = {k: frozenset(key(c) for c in T[k]) for k in idx}
    bb = {k: tuple((min(P[c][i] for c in T[k]), max(P[c][i] for c in T[k])) for i in range(3)) for k in idx}
    order = sorted(idx, key=lambda k: bb[k][0][0]); out = []
    for ii, i in enumerate(order):
        for j in order[ii + 1:]:
            if bb[j][0][0] > bb[i][0][1]: break
            if any(bb[i][d][1] < bb[j][d][0] or bb[j][d][1] < bb[i][d][0] for d in (1, 2)) or W[i] & W[j]: continue
            if tri_x([P[c] for c in T[i]], [P[c] for c in T[j]]): out.append((min(i, j), max(i, j)))
    return out


if PIECES:
    BIND_X = {ij for ij in frame_x(posed(None, 0.0)[0], False) if not (MAIN[ij[0]] and MAIN[ij[1]])}


# a clip made for one body (a character's blend-space variant: the thin idle, the muscular run) is judged on that body:
# its morph target applied at full weight while it is posed. <model>.character.json names them: each "clip_blends" entry's
# below/above clip plays on its option's below/above morph (the thin idle on the thin body; on the median body its arms,
# brought in to a thin body's hips, cut into the median hips)
def _variant_bodies():
    import json, base64, struct
    cfg_p = os.path.splitext(os.path.abspath(model))[0] + '.character.json'
    if not os.path.exists(cfg_p): return {}
    cfg = json.load(open(cfg_p, encoding='utf-8')); opts = {o.get('id'): o for o in cfg.get('options', [])}
    morphs = {}
    for m in (A.get('subs') or [{}])[0].get('morphs') or []:
        d = m.get('d')
        if isinstance(d, str): raw = base64.b64decode(d); d = list(struct.unpack('<%df' % (len(raw) // 4), raw))
        morphs[m.get('name')] = d
    out = {}
    for bl in cfg.get('clip_blends', []):
        o = opts.get(bl.get('option'), {})
        for side in ('below', 'above'):
            if bl.get(side) and o.get(side) in morphs: out[bl[side]] = (o[side], morphs[o[side]])
    return out
VARIANT = _variant_bodies()
_V0 = list(V)
def _body(delta):
    for ci, (pos, ws) in enumerate(_V0):
        V[ci] = ((pos[0] + delta[ci * 3], pos[1] + delta[ci * 3 + 1], pos[2] + delta[ci * 3 + 2]), ws) if delta else (pos, ws)


for clip in clips:
    if clip != 'bind' and clip not in A.get('anims', {}): print('clip %s not in the model' % clip); continue
    _body(VARIANT[clip][1] if clip in VARIANT and len(VARIANT[clip][1]) == 3 * len(_V0) else None)
    frames = [0.0] if clip == 'bind' else [k / N for k in range(N)]; rows = []; prow = []
    for ph in frames:
        P, _ = posed(None if clip == 'bind' else clip, ph)
        xs = frame_x(P, not PIECES); pairs = {}; spots = []; ppairs = {}
        for i, j in xs:
            k2 = ' x '.join(sorted((owner(T[i][0]), owner(T[j][0]))))
            if MAIN[i] and MAIN[j]:
                pairs[k2] = pairs.get(k2, 0) + 1
                if WHERE:
                    ci = [sum(P[c][d] for c in T[i]) / 3 for d in range(3)]; cj = [sum(P[c][d] for c in T[j]) / 3 for d in range(3)]
                    spots.append((k2, T[i], T[j], [round((ci[d] + cj[d]) / 2, 3) for d in range(3)]))
            elif (i, j) not in BIND_X: ppairs[(i, j)] = k2
        rows.append((sum(pairs.values()), ph, pairs, spots)); prow.append((ph, ppairs))
    if PIECES and prow:                            # pairs crossing in every frame ride with the body on purpose
        always = set.intersection(*[set(pp) for _, pp in prow]) if len(prow) > 1 else set()
        prow2 = []
        for ph, pp in prow:
            named = {}
            for ij, k2 in pp.items():
                if ij not in always: named[k2] = named.get(k2, 0) + 1
            prow2.append((sum(named.values()), ph, named))
        prow = prow2
    n, ph, pairs, spots = max(rows, key=lambda r: r[0])
    top = ', '.join('%s %d' % kv for kv in sorted(pairs.items(), key=lambda kv: -kv[1])[:5]) or 'none'
    print('clip %s worst %d crossings at phase %.3f; frames with more than 12: %d of %d; pairs: %s%s'
          % (clip, n, ph, sum(1 for r in rows if r[0] > 12), len(rows), top,
             ('; on the %s body' % VARIANT[clip][0]) if clip in VARIANT else ''))
    for k2, ti, tj, at in (spots if WHERE else []):
        print('    %-28s tri %s x tri %s at %s' % (k2, tuple(ti), tuple(tj), at))
    if PIECES and prow:
        pn, pph, pp = max(prow, key=lambda r: r[0])
        ptop = ', '.join('%s %d' % kv for kv in sorted(pp.items(), key=lambda kv: -kv[1])[:5]) or 'none'
        print('separate pieces, %s: worst %d new crossings at phase %.3f; pairs: %s' % (clip, pn, pph, ptop))
