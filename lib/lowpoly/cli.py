"""lp: the low-poly pipeline's command line. Standard library only.

  lp check <model.gltf|.glb> [--spec spec.json] [--stage mesh|rig|texture|motion|all] [--out dir]
      Measures the model with the tools in lowpoly/tools and judges every measurement against targets.json. Writes
      report.json and report.md to --out (default: <model>_report beside the model) and exits 1 if any check at the "fail"
      level fails, 0 otherwise.
  lp waste <model.gltf|.glb>
      How the model spends its polygons: rendered vertices per position, each part's share of the triangles beside its
      share of the surface, whether it was built as a mirrored half, and every edge that could be collapsed with almost
      no change to the surface (two triangles each that shape nothing), listed by part and position. Run it on the
      untextured blockout, before any paint (lowpoly-core SKILL.md, "Stage gates").
  lp render <model.gltf|.glb> [--out dir] [--clip name]
      Contact pictures for a person to look at: the head textured and lit from two sides, the hindquarters, the walk.
  lp preview <model.gltf|.glb> [--out dir] [--clip name] [--phase 0..1] [--refs refs.json]
      The model as the reviewer sees it: sheet.png with six fixed views of the whole body (3/4 front, 3/4 rear, side,
      front, rear, top) under the engine's lights, with the ground line and a scale bar, plus views/<view>.png and
      preview.html, a self-contained page to turn it round and play its clips. With --refs, compare.html sets each
      side, front, rear and top view beside that view's references (photos turned to the model's facing, by-eye
      "measured" numbers with their source). The views are shaded as the viewer shades them (sRGB, Lambert, 1/pi). Attach the sheet to every report.
  lp bake-springs <model.gltf|.glb> <springs.json> <out.gltf>
      Bakes secondary motion into the clips: chains of spring bones (a tail, primaries, ears) that lag, swing and droop
      under stiffness, drag and gravity, kept out of collision spheres, written back as rotation keys. Prints how far each
      bone turns from the animation and how well each loop closes. The springs.json format: lp bake-springs --help.
  lp export-viewer <viewer dir> <model id> <out.gltf>
      Writes a model from a viewer project (animals.js and its kin) as glTF 2.0 with its texture beside it.

  lp overlay <model.gltf|.glb> <refs.json> [--out dir] [--threshold 5]
      Measures the model against its references: each reference's landmarks (marked in pixels in refs.json) against the
      same landmarks read from the rig, aligned on two of them, plus any traced top line, underline or side edges. Prints
      every error in metres and as a share of the aligned span, flags those over the threshold, and writes overlay.md,
      overlay.json, a picture per reference and overlay.html (over the photo). The refs.json format: lp overlay --help.

spec.json (all optional) says what the model is, so that only the checks that apply to it run:
  {"body_plan": "quadruped|biped|bird|fish|lizard|arthropod|flyer", "skin": "fur|scales|plates|chitin|wet|feathers",
   "feet": "paw|clawed|long-toed|hoof|hand|none", "tier": "large|medium|small|tiny|swarm|very-large",
   "eye": {"u": 307, "v": 34, "half_width": 4, "half_height": 3}, "walk_clip": "walk",
   "standing_clips": ["idle", "stand"], "refs": "refs.json", "cards": 16}   (standing_clips default: the idle clip and any
   clip named idle or stand; refs, relative to the spec: the overlay's landmarks, judged at the mesh stage; cards: how many
   open edges the design has on purpose, such as a membrane wing's free outline, so mesh.closed passes at that many and
   fails on one more. body_plan flyer skips the standing checks: the feet's ground metrics and motion.balance; "eyes": "glow"
   marks a pupil-less glowing eye (a hostile mob's, lowpoly-core/references/temperament.md), which skips the pupil-eye checks eye.body,
   eye.rim and eye.catchlight; the default is "pupil";
   "ref_parts": ["head", "wing"] names special parts that each need a reference with a matching "part" (refs.parts);
   "hero": true makes the reference checks fail instead of warn: refs.views wants a measurable reference in the side,
   front or rear, and top views, and a missing refs.json counts as all three missing)
Without an eye position the eye checks are skipped and say so.

A spec can be a style contract (lowpoly/contract.py): "profiles" names shared layers (style/, muzzle/, eyes/, species/,
colour/, temperament/ in lowpoly/profiles; temperament/hostile sets the glowing eye and resolves last) that fill in what the model is ("muzzle": "soft-equine", "eye_shape": "side-almond"), set
check ranges, a palette and rules; "parts" lists the model's parts with their bones, triangle budgets and how they meet the
body, judged by the parts.* checks (lowpoly/tools/parts_study.py); "checks" sets this model's own ranges.
  lp contract <spec.json> [--out brief.md]
      Prints the resolved contract: every layer, what each sets, the check ranges, the parts and their budgets against the
      tier, the palette and the rules. It is the brief for anyone building a part of the model."""
import math, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, 'tools')
sys.path.insert(0, os.path.dirname(HERE))
from lowpoly import gltf_io, contract  # noqa: E402

class UsageError(Exception):
    """a mistake in the command line or the inputs: reported as one line, exit code 2"""


SPEC_VALUES = {'body_plan': ('quadruped', 'biped', 'bird', 'fish', 'lizard', 'arthropod', 'flyer'),
               'skin': ('fur', 'scales', 'plates', 'chitin', 'wet', 'feathers'),
               'feet': ('paw', 'clawed', 'long-toed', 'hoof', 'hand', 'none'),
               'tier': ('large', 'medium', 'small', 'tiny', 'swarm', 'very-large'),
               'eyes': ('pupil', 'glow'),
               'muzzle': ('leather-pad', 'soft-equine', 'muffle', 'small-bare', 'disc', 'split-lip', 'lipless', 'beak', 'primate'),
               'eye_shape': ('side-almond', 'forward')}
SPEC_KEYS = set(SPEC_VALUES) | {'eye', 'walk_clip', 'standing_clips', 'name', 'refs', 'cards', 'hero', 'ref_parts'} | contract.CONTRACT_KEYS
STAGES = ('mesh', 'rig', 'texture', 'motion', 'all')


def read_spec(path):
    """the spec as a dict, and a note for every key or value lp does not know (a typo would quietly skip its checks)"""
    if not path: return {}, ['no spec: the checks that depend on the body plan, skin, feet, tier or eye were not run']
    if not os.path.isfile(path): raise UsageError('spec not found: %s' % path)
    try: spec = json.load(open(path, encoding='utf-8'))
    except ValueError as e: raise UsageError('spec is not valid JSON (%s): %s' % (path, e))
    if not isinstance(spec, dict): raise UsageError('spec must be a JSON object: %s' % path)
    try: spec, res = contract.resolve(spec)
    except contract.ContractError as e: raise UsageError('spec %s: %s' % (path, e))
    spec['_contract'] = res
    notes = ['spec: unknown key %r (known: %s)' % (k, ', '.join(sorted(SPEC_KEYS))) for k in spec if k not in SPEC_KEYS and k != '_contract']
    notes += ['spec: %s %r is not one of %s, so its checks were not run' % (k, spec[k], '/'.join(v))
              for k, v in SPEC_VALUES.items() if k in spec and spec[k] not in v]
    # a model the rules call hostile, with a pupil eye nobody chose: the gorilla shipped a docile brown eye with a catchlight,
    # because its colour and eye profiles described one and "hostile" was only a sentence in its rules
    said = ' '.join(r for _, r in res['rules']) + ' ' + str(spec.get('name', ''))
    if re.search(r'\bhostile\b', said, re.I) and spec.get('eyes', 'pupil') != 'glow' and 'temperament/hostile' not in res['layers'] \
            and res['sources'].get('eyes') != 'contract':
        notes.append('spec: the name or rules call the model hostile, but its eyes are pupil eyes: add "temperament/hostile" to '
                     '"profiles" (a glowing eye, lowpoly-core/references/temperament.md), or set "eyes": "pupil" to keep them on purpose')
    return spec, notes


STAGE_TOOLS = {'mesh': ['mesh', 'topo', 'feet', 'thin', 'limbs', 'rear', 'overlay'], 'rig': ['mesh', 'rig'], 'motion': ['rig', 'stand', 'cross', 'legs'],
               'texture': ['uv', 'body', 'skin', 'eye', 'nose', 'regions', 'parts']}


def run_tool(name, *args, timeout=900):
    """run one measuring tool in an isolated interpreter; returns its text output"""
    cmd = [sys.executable, '-I', os.path.join(TOOLS, name + '.py')] + [str(a) for a in args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError('%s failed:\n%s' % (name, (r.stderr or r.stdout)[-1500:]))
    return r.stdout


def num(pattern, text, cast=float, default=None):
    m = re.search(pattern, text)
    return cast(m.group(1)) if m else default


# ---- measurements: each returns a dict of named numbers (and the raw text, for the report)

def measure_mesh(model, A):
    """the mesh basics, in process: welded positions, triangles, open edges, bones, blended corners"""
    import base64, struct
    key = lambda p: (round(p[0], 5), round(p[1], 5), round(p[2], 5))
    pos_id, tris, corners, blended = {}, [], 0, 0
    for sub in A['subs']:
        raw = base64.b64decode(sub['v']); n = len(raw) // 64
        V = [struct.unpack_from('<16f', raw, i * 64) for i in range(n)]
        I = struct.unpack('<%dH' % (len(base64.b64decode(sub['i'])) // 2), base64.b64decode(sub['i']))
        ids = [pos_id.setdefault(key(v[:3]), len(pos_id)) for v in V]
        corners += n; blended += sum(1 for v in V if sum(1 for w in v[8:12] if w > 1e-4) >= 2)
        tris += [(ids[I[k]], ids[I[k + 1]], ids[I[k + 2]]) for k in range(0, len(I) - 2, 3)]
    edges = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            e = (min(a, b), max(a, b)); edges[e] = edges.get(e, 0) + 1
    tris_nd = [t for t in tris if len(set(t)) == 3]
    P = [None] * len(pos_id)
    for k, i in pos_id.items(): P[i] = k
    return {'mesh.vertices': len(pos_id), 'mesh.triangles': len(tris_nd), 'mesh.bones': len(A['bones']),
            'mesh.open_edges': sum(1 for c in edges.values() if c == 1), 'mesh.corners': corners,
            'mesh.blended_pct': round(100.0 * blended / max(1, corners), 1), **loose_pieces(P, tris_nd)}


def _pt_tri(p, a, b, c):
    """distance from point p to triangle abc"""
    sub = lambda u, v: (u[0] - v[0], u[1] - v[1], u[2] - v[2]); dot = lambda u, v: u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    at = lambda o, d, k: (o[0] + d[0] * k, o[1] + d[1] * k, o[2] + d[2] * k)
    ab, ac, ap = sub(b, a), sub(c, a), sub(p, a); d1, d2 = dot(ab, ap), dot(ac, ap)
    if d1 <= 0 and d2 <= 0: return math.dist(p, a)
    bp = sub(p, b); d3, d4 = dot(ab, bp), dot(ac, bp)
    if d3 >= 0 and d4 <= d3: return math.dist(p, b)
    vc = d1 * d4 - d3 * d2
    if vc <= 0 and d1 >= 0 and d3 <= 0: return math.dist(p, at(a, ab, d1 / (d1 - d3)))
    cp = sub(p, c); d5, d6 = dot(ab, cp), dot(ac, cp)
    if d6 >= 0 and d5 <= d6: return math.dist(p, c)
    vb = d5 * d2 - d1 * d6
    if vb <= 0 and d2 >= 0 and d6 <= 0: return math.dist(p, at(a, ac, d2 / (d2 - d6)))
    va = d3 * d6 - d5 * d4
    if va <= 0 and d4 - d3 >= 0 and d5 - d6 >= 0: return math.dist(p, at(b, sub(c, b), (d4 - d3) / ((d4 - d3) + (d5 - d6))))
    den = 1.0 / (va + vb + vc); return math.dist(p, at(at(a, ab, vb * den), ac, vc * den))


def _seg_tri(p, q, a, b, c):
    """does segment pq cross triangle abc"""
    sub = lambda u, v: (u[0] - v[0], u[1] - v[1], u[2] - v[2]); dot = lambda u, v: u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    cr = lambda u, v: (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    e1, e2, d = sub(b, a), sub(c, a), sub(q, p); h = cr(d, e2); det = dot(e1, h)
    if abs(det) < 1e-15: return False
    f = 1 / det; s_ = sub(p, a); u = f * dot(s_, h)
    if u < 0 or u > 1: return False
    qv = cr(s_, e1); v = f * dot(d, qv)
    if v < 0 or u + v > 1: return False
    t = f * dot(e2, qv); return 0 <= t <= 1


def loose_pieces(P, tris):
    """pieces not joined to the main skin, and how far the worst one stands off it (% of the model's height). A tooth or
    an eye set into the skin touches it (0); a finger or a claw built as its own piece a little way off reads as broken."""
    par = list(range(len(P)))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for a, b, c in tris: par[f(b)] = f(a); par[f(c)] = f(a)
    G = {}
    for i in range(len(P)): G.setdefault(f(i), []).append(i)
    g = sorted(G.values(), key=len, reverse=True)
    if len(g) < 2: return {'mesh.pieces': 1, 'mesh.loose_gap': 0.0}
    main = set(g[0]); mt = [t for t in tris if t[0] in main]
    h = max(1e-9, max(p[1] for p in P) - min(p[1] for p in P))
    def touches(pc):
        """a piece set into the skin (a tooth sunk in the gum) has an edge passing through a skin triangle: its gap is 0"""
        ps = set(pc); edges = {(min(a, b), max(a, b)) for t in tris if t[0] in ps for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))}
        for a, b in edges:
            lo = [min(P[a][k], P[b][k]) for k in range(3)]; hi = [max(P[a][k], P[b][k]) for k in range(3)]
            for t in mt:
                if any(max(P[v][k] for v in t) < lo[k] or min(P[v][k] for v in t) > hi[k] for k in range(3)): continue
                if _seg_tri(P[a], P[b], P[t[0]], P[t[1]], P[t[2]]): return True
        return False
    gap = max(0.0 if touches(pc) else min(_pt_tri(P[i], P[t[0]], P[t[1]], P[t[2]]) for i in pc for t in mt) for pc in g[1:])
    return {'mesh.pieces': len(g), 'mesh.loose_gap': round(100.0 * gap / h, 2)}


def measure_feet(model, out, tag):
    t = run_tool('foot_study', model, out, tag)
    feet = re.findall(r'foot \d+:\s+(\d+) vertices.*?splay ([\d.]+)x \| toes reach ([-\d.]+) ankle depths.*?tips (\d+).*?'
                      r'ground contacts (\d+) \| bones (\d+)', t)
    m = {'feet.count': len(feet), 'model.height': num(r'height ([\d.]+) m', t)}
    if feet:
        # a ratio over 50 means the tool divided by an ankle (or foot length) of almost nothing: a collapsed ring, not a
        # measurement. Those feet are left out of the ratio and counted, so the report says so.
        sane = lambda i: [float(f[i]) for f in feet if float(f[i]) <= 50]
        m.update({'feet.vertices_min': min(int(f[0]) for f in feet), 'feet.tips_min': min(int(f[3]) for f in feet),
                  'feet.contacts_min': min(int(f[4]) for f in feet),
                  'feet.bones_min': min(int(f[5]) for f in feet),
                  'feet.unmeasurable_ratios': sum(1 for f in feet for i in (1, 2) if float(f[i]) > 50)})
        if sane(1): m['feet.splay_min'] = min(sane(1))
        if sane(2): m['feet.reach_min'] = min(sane(2))
    return m, t


def measure_topo(model):
    """how the polygons are spent: rendered vertices per position, the head's density over the body's, mirrored
    construction read through the texture, and edges that shape nothing (lowpoly/tools/topo_study.py)"""
    t = run_tool('topo_study', model)
    m = {'topo.corners_per_position': num(r'corners per position ([\d.]+)', t), 'topo.head_density': num(r'head density over body ([\d.]+)', t),
         'topo.mirror_texels_pct': num(r"right triangle's texels (\d+)%", t), 'topo.waste_pct': num(r'triangles, ([\d.]+)% of the model', t)}
    lr = re.search(r'triangles left (\d+) right (\d+)', t)
    if lr: m['topo.side_difference'] = abs(int(lr.group(1)) - int(lr.group(2)))
    return {k: v for k, v in m.items() if v is not None}, t


def measure_rear(model, A, walk_clip=None):
    """the hindquarters from behind (lowpoly/tools/rear_study.py): the haunch band's outline in the bind pose and at four
    phases of the walk, the worst of each measure. A saddlebag lobe, a waist between the thigh and the body or a sharp turn
    in the outline reads oddly from the rear and 3/4-rear camera, where no side or front measure looks"""
    frames = [()]
    clip = walk_clip if walk_clip in (A.get('anims') or {}) else ('walk' if 'walk' in (A.get('anims') or {}) else None)
    if clip: frames += [(clip, ph) for ph in ('0', '0.25', '0.5', '0.75')]
    worst, texts = {}, []
    for fr in frames:
        t = run_tool('rear_study', model, *fr); texts.append(t)
        r = re.search(r'rear: thighs over hips ([\d.]+) \| bulge ([\d.]+)% \| notch ([\d.]+)% \| corner (\d+) deg', t)
        if not r: continue
        for k, v in (('rear.bulge_pct', float(r.group(2))), ('rear.notch_pct', float(r.group(3))), ('rear.corner_deg', float(r.group(4)))):
            worst[k] = max(worst.get(k, 0.0), v)
    return worst, '\n'.join(texts)


def measure_thin(model, tag):
    t = run_tool('thin_triangles', model, tag, -99, 99, -99, 99, 3)
    return {'mesh.max_aspect': num(r'\n\s+([\d.]+) \|', t)}, t


def measure_overlay(model, out, refs):
    """the model against its references' landmarks and traced outlines (lowpoly-core/references/measuring.md): the worst landmark error
    and the worst outline gap, as shares of each reference's aligned span"""
    t = run_tool('measure_overlay', model, refs, os.path.join(out, 'overlay'))
    r = re.search(r'overlay: (\d+) references, (\d+) landmarks \((\d+) over .*?worst landmark ([\d.]+)%, worst outline ([\d.]+)%', t)
    m = {}
    if r and int(r.group(1)):
        m['overlay.references'] = int(r.group(1)); m['overlay.landmark_worst_pct'] = float(r.group(4))
        if 'Outline |' in t: m['overlay.outline_worst_pct'] = float(r.group(5))
    return m, t


REQUIRED_VIEWS = (('side', ('side',)), ('front or rear', ('front', 'rear')), ('top', ('top',)))


def measure_ref_views(refs_path, parts):
    """which views (and named parts) the reference set covers. A reference covers its view when it carries something to
    measure: two or more landmarks, a traced outline, or by-eye "measured" ratios (numbers read off a photo that could not be
    downloaded, with its address in "source"). No refs.json at all covers nothing: the check then says so instead of the
    overlay checks being skipped quietly (the housecat's chest and the alicorn's head were shaped from no front, top or
    head reference at all, and lp check still said PASSED)."""
    refs = []
    if refs_path and os.path.isfile(refs_path):
        try: refs = json.load(open(refs_path, encoding='utf-8')).get('refs', [])
        except Exception as e: raise RuntimeError('refs.json could not be read: %s' % e)
    def useful(r): return len(r.get('landmarks') or {}) >= 2 or bool(r.get('outline')) or bool(r.get('measured'))
    have = {str(r.get('view', '')).lower() for r in refs if useful(r)}
    missing_views = [name for name, alts in REQUIRED_VIEWS if not any(v in have for v in alts)]
    have_parts = {str(r.get('part', '')).lower() for r in refs if useful(r)}
    missing_parts = [p for p in (parts or []) if p.lower() not in have_parts]
    m = {'refs.views_missing': len(missing_views)}
    # how much each required view actually gives: landmarks, outline points, measured ratios and profile stations. Three or
    # four ratios read by eye leave the rest of the shape to be guessed; a dense silhouette profile does not.
    def items(r):
        n = len(r.get('landmarks') or {}) + sum(len(v) for v in (r.get('outline') or {}).values() if isinstance(v, list))
        for v in (r.get('measured') or {}).values(): n += len(v) if isinstance(v, list) and v and isinstance(v[0], list) else 1
        return n
    per = {name: sum(items(r) for r in refs if str(r.get('view', '')).lower() in alts) for name, alts in REQUIRED_VIEWS}
    m['refs.detail_min'] = min(per.values())
    if parts: m['refs.parts_missing'] = len(missing_parts)          # only when the spec names parts (else: not measured)
    txt = 'reference views: %s present; missing: %s. Named parts missing a reference: %s. Measurements per view: %s' % (
        ', '.join(sorted(have)) or 'none', ', '.join(missing_views) or 'none', ', '.join(missing_parts) or 'none',
        ', '.join('%s %d' % kv for kv in per.items()))
    return m, txt


def measure_limbs(model, tag):
    """where the hind legs' mass sits from the front: the widest half-width between the knee (t 0) and the hip (t 1), and the
    knee's half-width as a share of it (lowpoly-animals/references/limbs.md)"""
    t = run_tool('limb_widths', model, tag)
    m = {}
    r = re.search(r'hind legs: widest at t ([\d.]+)\.\.([\d.]+) .*?knee ([\d.]+)\.\.([\d.]+) of the widest', t)
    if r:
        m['limbs.hind_peak_t'] = float(r.group(1)); m['limbs.hind_knee_share'] = float(r.group(4))
    return m, t


def measure_rig(model, tag, clip=None):
    t = run_tool('rig_study', model, tag, *([clip] if clip else []))
    m = {'walk.clip': num(r'== walk clip (\S+),', t, str)}
    grounded = [int(a) / int(b) for a, b in re.findall(r'grounded (\d+)/(\d+) frames', t)]
    lifts = [float(x) for x in re.findall(r'lift [\d.]+\.\.([\d.]+) m', t)]
    if grounded: m['walk.duty_min'] = round(min(grounded), 3)
    if lifts: m['walk.lift_max_m'] = max(lifts)
    m['walk.junction_stretch_pct'] = num(r'max stretch over the walk (\d+)%', t)
    return m, t


def measure_stand(model, tag, clips=None):
    """the centre of mass over the feet in every standing clip: the worst margin over all of them (1 centred, 0 on the edge,
    negative falling)"""
    t = run_tool('stand_study', model, tag, ','.join(clips) if clips else '')
    rows = [(n, float(a), float(b)) for n, a, b in re.findall(r'clip (\S+)\s+worst margin front-back ([-+\d.]+), side-side ([-+\d.]+)', t)]
    m = {}
    if rows:
        worst = min(rows, key=lambda r: min(r[1], r[2]))
        m['stand.margin_min'] = round(min(worst[1], worst[2]), 2); m['stand.worst_clip'] = worst[0]
    slides = [(n, float(pc)) for n, pc in re.findall(r'clip (\S+)\s+foot slide [\d.]+ m = ([\d.]+)% of the height', t)]
    if slides:
        w = max(slides, key=lambda r: r[1]); m['stand.slide_pct'] = w[1]; m['stand.slide_clip'] = w[0]
    bg = re.search(r'below the ground: lowest skin point ([-\d.]+) m = ([-\d.]+)% of the height \(clip (\S+), phase', t)
    if bg: m['ground.below_pct'] = max(0.0, -float(bg.group(2))); m['ground.below_clip'] = bg.group(3)
    return m, t


def measure_cross(model):
    """parts passing through each other: the most crossing triangles in any frame of any clip or the bind pose"""
    t = run_tool('self_cross', model, 24)
    rows = [(n, int(c)) for n, c in re.findall(r'clip (\S+) worst (\d+) crossings', t)]
    m = {}
    if rows:
        worst = max(rows, key=lambda r: r[1]); m['motion.crossings_max'] = worst[1]; m['motion.crossings_clip'] = worst[0]
    prow = [(n, int(c)) for n, c in re.findall(r'^separate pieces, (\S+): worst (\d+) new crossings', t, re.M)]
    if prow:                                     # separate pieces (a shell, a swapped part) moving through the body or each other
        worst = max(prow, key=lambda r: r[1]); m['motion.pieces_max'] = worst[1]; m['motion.pieces_clip'] = worst[0]
    return m, t


GAIT = re.compile(r'walk|trot|run|gallop|canter|bound|hop|swim|fly|crawl', re.I)


def measure_legs(model, A, spec):
    """how the legs bend through the clips (lowpoly/tools/leg_bend_study.py): the narrowest ring of leg skin against the
    bind pose (linear blend skinning pinches a joint's ring as it folds), the most an edge along a leg stretches or
    shrinks, the frames a knee, elbow or hock bends backwards, and the most a pair of legs moves in lockstep in an action
    clip (an attack, a roar: not the walk, a gait or a standing clip, where pairs move in phase or counterphase by design)"""
    t = run_tool('leg_bend_study', model)
    rows = re.findall(r'^clip (\S+): ring ([\d.]+) \| stretch ([\d.]+)\.\.([\d.]+) \| hyperextended (\d+) \| lockstep (\S+)', t, re.M)
    if not rows: return {}, t
    anims = A.get('anims') or {}
    standing = set(spec.get('standing_clips') or [c for c in anims if c == A.get('idle') or re.search(r'idle|stand', c, re.I)])
    walk = spec.get('walk_clip', 'walk')
    m = {'legs.ring_min': min(float(r[1]) for r in rows), 'legs.stretch_min': min(float(r[2]) for r in rows),
         'legs.stretch_max': max(float(r[3]) for r in rows), 'legs.hyperextended': sum(int(r[4]) for r in rows)}
    m['legs.ring_clip'] = min(rows, key=lambda r: float(r[1]))[0]
    act = [(r[0], float(r[5])) for r in rows if r[5] != '-' and r[0] not in standing and r[0] != walk and not GAIT.search(r[0])]
    if act:
        w = max(act, key=lambda r: r[1]); m['legs.lockstep_max'] = w[1]; m['legs.lockstep_clip'] = w[0]
    return m, t


def measure_regions(model):
    """painted detail on the limbs: the flattest leg, arm or wing region's fine + mid contrast, and the darkest one's brightness"""
    t = run_tool('region_detail', model)
    rows = {r: (float(b), float(tot)) for r, b, tot in
            re.findall(r'^\s+(leg|arm|wing)\s+density.*?brightness ([\d.]+).*?\(([\d.]+)\)', t, re.M)}
    m = {}
    if rows:
        m['texture.limb_detail'] = round(min(v[1] for v in rows.values()), 2)
        m['texture.limb_detail_region'] = min(rows, key=lambda r: rows[r][1])
        m['texture.limb_brightness'] = round(min(v[0] for v in rows.values()), 2)
    return m, t


def measure_uv(model, tag):
    t = run_tool('uv_study', model, tag)
    return {'uv.density_px_per_m': num(r'median (\d+) px/m', t), 'uv.stretch4_pct': num(r'more than 4:1 (\d+)%', t),
            'uv.seam_median': num(r'median ([\d.]+), worst', t), 'uv.seam_worst10': num(r'worst 10% above ([\d.]+)', t)}, t


def measure_body(model, out, tag):
    t = run_tool('body_study', model, out, tag, 4)
    m = {'coat.large': num(r'large ([\d.]+)', t), 'coat.mid': num(r'mid ([\d.]+)', t), 'coat.fine': num(r'fine ([\d.]+)', t),
         'coat.coherence': num(r'overall coherence ([\d.]+)', t), 'coat.local_coherence': num(r'locally ([\d.]+)', t)}
    d, l = num(r'darks \(\d+%\) ([-+\d.]+)', t), num(r'lights \(\d+%\) ([-+\d.]+)', t)
    if d is not None and l is not None: m['coat.shape_depth'] = round(min(abs(d), abs(l)), 3)
    return m, t


def measure_skin(model, out, tag):
    t = run_tool('skin_study', model, out, tag)
    return {'skin.fine': num(r'fine ([\d.]+)', t), 'skin.crevices_pct': num(r'crevices ([\d.]+)%', t),
            'skin.highlights_pct': num(r'highlights ([\d.]+)%', t), 'skin.edges_pct': num(r'edges ([\d.]+)%', t),
            'skin.coherence': num(r'direction coherence ([\d.]+)', t)}, t


def measure_eye(model, out, tag, eye):
    args = [eye['u'], eye['v']] + [eye[k] for k in ('half_width', 'half_height') if k in eye]
    t = run_tool('eye_study', model, 'measure', out, tag, *args)
    rows = {z: tuple(float(x) for x in r) for z, *r in
            re.findall(r'\n\s+(core|eye body|rim|lid/socket)\s+[\d.]+-[\d.]+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\.\.([\d.]+)', t)}
    m = {}
    if rows:
        m['eye.brightest'] = max(rows[z][3] for z in ('core', 'eye body', 'rim') if z in rows)
        m['eye.darkest'] = min(rows[z][2] for z in ('core', 'eye body') if z in rows)
        if 'rim' in rows: m['eye.rim_sd'] = rows['rim'][1]
    s = num(r'lid/socket ([-+\d.]+)', t)
    if s is not None: m['eye.socket_step_abs'] = abs(s)
    m['eye.radius_mm'] = num(r'= ([\d.]+) mm on the model', t)
    if 'half_width' in eye:      # the spec's size is used as given: measure the painted eye too, so a stale size is caught
        t2 = run_tool('eye_study', model, 'measure', out, tag + '_found', eye['u'], eye['v'])
        m['eye.radius_found_mm'] = num(r'= ([\d.]+) mm on the model', t2)
    return m, t


def measure_nose(model, out, tag):
    png = os.path.join(out, tag + '_head.png')
    run_tool('head_textured', model, png, tag)
    t = run_tool('nose_study', png, tag)
    # every station counts for the bridge; the mouth only where a lip was found above the line (-1.00: none). A station with
    # no lip was dropped whole, bridge and all (the giant bat's nose checks were skipped that way)
    st = re.findall(r'bridge ([\d.]+) \| side ([\d.]+) \| mouth line ([\d.]+) at \d+% down \(lip above ([-\d.]+)', t)
    m = {}
    if st:
        m['nose.bridge_over_side_min'] = round(min(float(b) - float(s) for b, s, _, _ in st), 3)
        lips = [float(a) - float(ml) for _, _, ml, a in st if float(a) >= 0]
        if lips: m['nose.mouth_depth_max'] = round(max(lips), 3)
    fr = re.search(r'front: nose ([\d.]+) of the muzzle width; nose brightness mean [\d.]+ sd [\d.]+, nostrils \(darkest 10%\) ([\d.]+)', t)
    if fr: m['nose.width_ratio'] = float(fr.group(1)); m['nose.nostrils_darkest'] = float(fr.group(2))
    fd = re.search(r'muzzle fine detail ([\d.]+)', t)
    if fd: m['nose.detail'] = float(fd.group(1))
    return m, t



ORNAMENT = re.compile(r'horn|antler|crest|frill', re.I)     # never 'spine': a part may be the backbone


def body_height(A, parts):
    """the model's height leaving out the corners carried mostly by the bones of the contract's horn, antler, crest
    or frill parts; None when the spec names no such part"""
    import base64, fnmatch, struct
    pats = [p for name, d in parts.items() if ORNAMENT.search(name) for p in (d or {}).get('bones', [])]
    if not pats: return None
    skip = {i for i, b in enumerate(A['bones']) if any(fnmatch.fnmatch(b, p) for p in pats)}
    ys = []
    for sub in A['subs']:
        raw = base64.b64decode(sub['v'])
        for i in range(len(raw) // 64):
            f = struct.unpack_from('<16f', raw, i * 64)
            w, b = f[8:12], f[12:16]
            if sum(wk for wk, bk in zip(w, b) if int(bk) in skip) < 0.5: ys.append(f[1])
    return round(max(ys) - min(ys), 3) if ys else None

def measure_parts(model, out, parts):
    # parts against each other (lowpoly/tools/parts_study.py): budgets, texel density against the body, the brightness
    # step where each part joins what it grows from
    pj = os.path.join(out, 'parts.json'); json.dump({'parts': parts}, open(pj, 'w', encoding='utf-8'), indent=1)
    t = run_tool('parts_study', model, pj)
    over, dens, step = 0, 0.0, 0.0
    for n, tri, bud, ratio, lo, hi, js, con in re.findall(
            r'part (\S+): (\d+) triangles \(budget ([\d-]+)\) \| density \d+ texels/m = ([\d.]+) x body \(range ([\d.]+)-([\d.]+)\) \| brightness [\d.]+ \| join \S+ step ([-+\d.]+)( \(contrast\))?', t):
        if bud != '-': over = max(over, int(tri) - int(bud))
        r = float(ratio)
        if r > 0: dens = max(dens, float(lo) / r, r / float(hi))
        if js != '-' and not con: step = max(step, abs(float(js)))
    m = {'parts.over_budget': over, 'parts.density_worst': round(dens, 2), 'parts.join_step_max': round(step, 2)}
    empty = re.findall(r'part (\S+): 0 triangles', t)
    if empty: m['parts.empty'] = len(empty)
    return m, t


# ---- judging

def applies(check, spec):
    for k, allowed in (check.get('applies') or {}).items():
        if spec.get(k) not in allowed: return 'needs %s in %s (spec says %s)' % (k, '/'.join(allowed), spec.get(k, 'nothing'))
    for k, barred in (check.get('excludes') or {}).items():          # runs for every value but these (and without a spec)
        if spec.get(k) in barred: return 'not for %s %s' % (k, spec[k])
    return None


def judge(check, value, targets, spec):
    lo, hi = check.get('min'), check.get('max')
    if 'tier' in check:
        tier = targets['tiers'].get(spec.get('tier', ''))
        if not tier: return lo, hi, 'skip', 'no tier in the spec'
        lo, hi = tier[check['tier']]
    if check.get('spec_max') and isinstance(spec.get(check['spec_max']), int): hi = spec[check['spec_max']]
    if value is None: return lo, hi, 'skip', 'not measured'
    ok = (lo is None or value >= lo) and (hi is None or value <= hi)
    level = check.get('hero_level', check['level']) if spec.get('hero') else check['level']   # a hero build is held to more
    return lo, hi, ('pass' if ok else level), ''


def read_model(model):
    if not os.path.isfile(model): raise UsageError('model not found: %s' % model)
    if not model.lower().endswith(('.gltf', '.glb')): raise UsageError('the model must be a .gltf or .glb file: %s' % model)
    try: A, _ = gltf_io.read_gltf(model)
    except Exception as e: raise UsageError('could not read %s as glTF: %s' % (model, e))
    if not A.get('subs'): raise UsageError('%s has no skinned mesh to check' % model)
    return A


def check(model, spec_path=None, stage='all', out=None):
    if stage not in STAGES: raise UsageError('unknown stage %r (one of %s)' % (stage, ', '.join(STAGES)))
    A = read_model(model)
    targets = json.load(open(os.path.join(HERE, 'targets.json'), encoding='utf-8'))
    spec, spec_notes = read_spec(spec_path)
    tag = os.path.splitext(os.path.basename(model))[0]
    out = out or os.path.join(os.path.dirname(os.path.abspath(model)), tag + '_report')
    os.makedirs(out, exist_ok=True)
    stages = ['mesh', 'rig', 'texture', 'motion'] if stage == 'all' else [stage]
    want = {t for s in stages for t in STAGE_TOOLS[s]}
    M, raw, notes = {}, {}, list(spec_notes)
    t0 = time.time()

    def take(name, fn, *a):
        try:
            r = fn(*a)
            m, txt = r if isinstance(r, tuple) else (r, '')
            M.update(m); raw[name] = txt
        except Exception as e:  # a tool that fails is reported, never silently passed
            notes.append('%s could not run: %s' % (name, str(e).strip().splitlines()[-1] if str(e).strip() else e))
            raw[name] = str(e)

    if 'mesh' in want: take('mesh', measure_mesh, model, A)
    if 'feet' in want and spec.get('feet', 'paw') != 'none': take('feet', measure_feet, model, out, tag)
    if 'topo' in want: take('topo', measure_topo, model)
    if 'thin' in want: take('thin', measure_thin, model, tag)
    if 'limbs' in want: take('limbs', measure_limbs, model, tag)
    if 'rear' in want and spec.get('body_plan', 'quadruped') == 'quadruped': take('rear', measure_rear, model, A, spec.get('walk_clip'))
    if 'overlay' in want:
        rp = None
        if spec.get('refs'):
            rp = spec['refs'] if os.path.isabs(spec['refs']) else os.path.join(os.path.dirname(os.path.abspath(spec_path)), spec['refs'])
        take('refviews', measure_ref_views, rp, spec.get('ref_parts'))
        rv = raw.get('refviews', '')
        if rv.startswith('reference views'):
            notes.append(rv)
        if spec.get('refs'):
            refs = spec['refs'] if os.path.isabs(spec['refs']) else os.path.join(os.path.dirname(os.path.abspath(spec_path)), spec['refs'])
            if os.path.isfile(refs): take('overlay', measure_overlay, model, out, refs)
            else: notes.append('overlay checks skipped: refs file not found: %s' % refs)
        else: notes.append('overlay checks skipped: no "refs" in the spec (a refs.json with landmarks; lp --help)')
    if 'rig' in want and A.get('anims'): take('rig', measure_rig, model, tag, spec.get('walk_clip'))
    if 'stand' in want and A.get('anims'): take('stand', measure_stand, model, tag, spec.get('standing_clips'))
    if 'cross' in want: take('cross', measure_cross, model)
    if 'legs' in want and A.get('anims'): take('legs', measure_legs, model, A, spec)
    if 'uv' in want: take('uv', measure_uv, model, tag)
    if 'regions' in want: take('regions', measure_regions, model)
    skin = spec.get('skin', 'fur')                       # an unknown skin (a typo) runs neither study: its checks are not run
    if 'body' in want and skin == 'fur': take('body', measure_body, model, out, tag)
    if 'skin' in want and skin != 'fur' and skin in SPEC_VALUES['skin']: take('skin', measure_skin, model, out, tag)
    if 'eye' in want:
        if spec.get('eye'): take('eye', measure_eye, model, out, tag, spec['eye'])
        else: notes.append('eye checks skipped: no "eye" texel position in the spec')
    if 'nose' in want and skin == 'fur': take('nose', measure_nose, model, out, tag)
    if 'parts' in want and spec.get('parts'): take('parts', measure_parts, model, out, spec['parts'])
    if spec.get('eyes') != 'glow' and M.get('eye.radius_found_mm') and M.get('eye.radius_mm') and not 0.77 < M['eye.radius_found_mm'] / M['eye.radius_mm'] < 1.3:
        notes.append("eye.size uses the spec's eye half_width (%.1f mm), but the painted eye's dark core measures %.1f mm: update "
                     "the spec's \"eye\" when the painted eye changes (a swan's enlarged eye left eye.size unchanged)"
                     % (M['eye.radius_mm'], M['eye.radius_found_mm']))
    if M.get('parts.empty'): notes.append('%d contract part(s) matched no bone: see parts in raw.txt' % M['parts.empty'])
    if M.get('feet.unmeasurable_ratios'):
        notes.append('%d foot splay or reach ratios were left out: the ankle ring is collapsed (the tool divided by almost '
                     'nothing). Check those feet in the foot close-up' % M['feet.unmeasurable_ratios'])
    if (M.get('walk.lift_max_m') is not None or M.get('eye.radius_mm')) and not M.get('model.height'):   # the height without the mesh stage's foot study
        import base64, struct
        ys = [struct.unpack_from('<f', raw, i * 64 + 4)[0] for sub in A['subs'] for raw in (base64.b64decode(sub['v']),)
              for i in range(len(raw) // 64)]
        M['model.height'] = round(max(ys) - min(ys), 3)
    if M.get('walk.lift_max_m') is not None and M.get('model.height'):
        M['walk.lift_max_pct'] = round(100 * M['walk.lift_max_m'] / M['model.height'], 1)
    if M.get('eye.radius_mm') and M.get('model.height'):
        # the eye is judged against the animal's height without its horns, antlers, crests or frills: a kudu's horns raised
        # its height by a third and made a normal eye read as small (the parts named so in the spec's contract)
        h = body_height(A, spec.get('parts') or {}) or M['model.height']
        M['eye.size_pct'] = round(0.1 * M['eye.radius_mm'] / h, 2)
        if h < M['model.height'] - 1e-6: M['eye.height_used'] = round(h, 3)

    results = []
    for c in targets['checks']:
        if c['stage'] not in stages: continue
        why = applies(c, spec)
        if why:
            results.append(dict(id=c['id'], stage=c['stage'], status='n/a', value=None, note=why, ref=c.get('ref', ''))); continue
        v = M.get(c['measure'])
        o = (spec.get('_contract') or {}).get('checks', {}).get(c['id'])
        if o:
            c = dict(c, **{k: o[k] for k in ('min', 'max', 'level') if k in o})
            if 'min' in o or 'max' in o: c.pop('tier', None)
        lo, hi, status, why = judge(c, v, targets, spec)
        if o: why = (why + '; ' if why else '') + 'range from %s' % o['source']
        results.append(dict(id=c['id'], stage=c['stage'], measure=c['measure'], value=v, min=lo, max=hi, level=c['level'],
                            status=status, note=why or c.get('note', ''), ref=c.get('ref', '')))
    failed = [r for r in results if r['status'] == 'fail']
    counts = {k: sum(1 for r in results if r['status'] == k) for k in ('pass', 'fail', 'warn', 'skip', 'n/a')}
    report = dict(model=os.path.abspath(model), name=A.get('name'), spec={k: v for k, v in spec.items() if k != '_contract'},
                  contract_layers=(spec.get('_contract') or {}).get('layers'), stages=stages, counts=counts,
                  passed=not failed and not [n for n in notes if 'could not run' in n],
                  seconds=round(time.time() - t0, 1), measures=M, results=results, notes=notes)
    json.dump(report, open(os.path.join(out, 'report.json'), 'w', encoding='utf-8'), indent=1)
    open(os.path.join(out, 'raw.txt'), 'w', encoding='utf-8').write('\n'.join('#### %s\n%s' % kv for kv in raw.items()))
    open(os.path.join(out, 'report.md'), 'w', encoding='utf-8').write(to_md(report))
    return report, out


def fmt(v):
    if v is None: return '-'
    return ('%g' % v) if isinstance(v, (int, float)) else str(v)


def to_md(r):
    L = ['# lp check: %s' % (r['name'] or os.path.basename(r['model'])), '',
         '**%s** (%s; stages: %s; %.0f s): %d passed, %d failed, %d warnings, %d not run' % (
             'PASSED' if r['passed'] else 'FAILED', os.path.basename(r['model']), ', '.join(r['stages']), r['seconds'],
             r['counts']['pass'], r['counts']['fail'], r['counts']['warn'], r['counts']['skip'] + r['counts']['n/a']), '',
         '| Status | Check | Value | Range | Note | Reference |', '|---|---|---|---|---|---|']
    order = {'fail': 0, 'warn': 1, 'pass': 2, 'skip': 3, 'n/a': 4}
    for x in sorted(r['results'], key=lambda x: (order[x['status']], x['stage'])):
        lo, hi = x.get('min'), x.get('max')
        rng = ('' if x['status'] == 'n/a' or (lo is None and hi is None) else '%s-%s' % (fmt(lo), fmt(hi)) if lo is not None and hi is not None
               else 'at most %s' % fmt(hi) if lo is None else 'at least %s' % fmt(lo))
        L.append('| %s | %s | %s | %s | %s | %s |' % (x['status'].upper(), x['id'], fmt(x.get('value')), rng, x['note'], x['ref']))
    if r['notes']: L += ['', '**Notes**', ''] + ['- ' + n for n in r['notes']]
    return '\n'.join(L) + '\n'


def render(model, out=None, clip=None):
    tag = os.path.splitext(os.path.basename(model))[0]
    out = out or os.path.join(os.path.dirname(os.path.abspath(model)), tag + '_renders')
    A = read_model(model)
    os.makedirs(out, exist_ok=True)
    made = []
    for name, args in (('head_textured', [os.path.join(out, 'head.png'), tag]),
                       ('lit_view', [os.path.join(out, 'lit_left.png'), tag, 35, 20]),
                       ('lit_view', [os.path.join(out, 'lit_right.png'), tag, -35, 20]),
                       ('region_views', [os.path.join(out, 'hindquarters.png'), tag])):
        run_tool(name, model, *args); made.append(args[0])
    clip = clip or next((n for n in A.get('anims', {}) if 'wl' in n or 'walk' in n), None)
    if clip:
        p = os.path.join(out, 'walk.png'); run_tool('walk_sheet', model, tag, clip, p); made.append(p)
    return made


def compare_page(out, refs_path):
    """compare.html beside the preview: each of the model's side, front, rear and top views next to every reference for that
    view (the image, turned to the model's facing; or a by-eye "measured" entry's numbers and source), so every review
    compares against a real animal instead of judging a view alone. Returns the page's path and a one-line summary."""
    import html, shutil
    refs = json.load(open(refs_path, encoding='utf-8')).get('refs', [])
    base = os.path.dirname(os.path.abspath(refs_path)); rdir = os.path.join(out, 'refs'); os.makedirs(rdir, exist_ok=True)
    rows, used = [], 0
    for view in ('side', 'front', 'rear', 'top'):
        mine = [r for r in refs if str(r.get('view', '')).lower() == view]
        cells = []
        for k, r in enumerate(mine):
            cap = html.escape(' | '.join(str(r[x]) for x in ('species', 'part', 'pose', 'use') if r.get(x)))
            if r.get('file') and os.path.isfile(os.path.join(base, r['file'])):
                name = '%s_%d%s' % (view, k, os.path.splitext(r['file'])[1].lower())
                shutil.copyfile(os.path.join(base, r['file']), os.path.join(rdir, name))
                # the model's side view has the nose to the left, its top view the nose up: turn the photo to match
                f = str(r.get('facing', '')).lower(); tr = ''
                if view == 'side' and f == 'right': tr = 'transform:scaleX(-1)'
                if view == 'top': tr = {'down': 'transform:rotate(180deg)', 'left': 'transform:rotate(90deg)', 'right': 'transform:rotate(-90deg)'}.get(f, '')
                cells.append('<figure><img src="refs/%s" style="%s"><figcaption>%s</figcaption></figure>' % (name, tr, cap)); used += 1
            elif r.get('measured'):
                items = ''.join('<li>%s: %s</li>' % (html.escape(str(a)), html.escape(str(v))) for a, v in r['measured'].items())
                src = html.escape(str(r.get('source', '')))
                cells.append('<figure class=m><ul>%s</ul><figcaption>%s<br><a href="%s">%s</a></figcaption></figure>' % (items, cap, src, src)); used += 1
        if not cells: cells.append('<figure class=none>no reference for this view: refs.views will warn</figure>')
        rows.append('<section><h2>%s</h2><div class=row><figure><img src="views/%s.png"><figcaption>the model</figcaption></figure>%s</div></section>'
                    % (view, view, ''.join(cells)))
    page = ('<!doctype html><meta charset=utf-8><title>Model against references</title><style>body{background:#222;color:#ddd;'
            'font:13px sans-serif;margin:16px}.row{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start}figure{margin:0;'
            'max-width:460px}img{max-width:460px;max-height:360px;display:block;background:#333}figure.m,figure.none{padding:10px;'
            'background:#333;min-width:220px}a{color:#9cf}h2{margin:18px 0 6px}</style><h1>Model against its references</h1>'
            '<p>Measure-only references, never traced. Compare proportions and outline, not pose.</p>' + ''.join(rows))
    path = os.path.join(out, 'compare.html'); open(path, 'w', encoding='utf-8').write(page)
    return path, '%d references shown beside the side, front, rear and top views' % used


def preview(model, out=None, clip=None, phase=None, refs=None):
    tag = os.path.splitext(os.path.basename(model))[0]
    out = out or os.path.join(os.path.dirname(os.path.abspath(model)), tag + '_preview')
    A = read_model(model)
    if clip and clip not in A.get('anims', {}):
        raise UsageError('no clip %r in %s (clips: %s)' % (clip, model, ', '.join(A.get('anims', {})) or 'none'))
    try: ph = float(phase) if phase is not None else 0.0
    except ValueError: raise UsageError('--phase takes a number from 0 to 1, got %r' % phase)
    os.makedirs(out, exist_ok=True)
    if refs and not os.path.isfile(refs): raise UsageError('refs file not found: %s' % refs)
    t = run_tool('preview', model, out, clip or '-', ph)
    if refs:
        path, msg = compare_page(out, refs); t += 'compare: %s (%s)' % (path, msg) + chr(10)
    return t


def overlay(model, refs, out=None, threshold=None):
    read_model(model)
    if not os.path.isfile(refs): raise UsageError('refs file not found: %s' % refs)
    try: thr = float(threshold) if threshold is not None else 5.0
    except ValueError: raise UsageError('--threshold takes a percentage, got %r' % threshold)
    tag = os.path.splitext(os.path.basename(model))[0]
    out = out or os.path.join(os.path.dirname(os.path.abspath(model)), tag + '_overlay')
    try: return run_tool('measure_overlay', model, refs, out, thr)
    except RuntimeError as e: raise UsageError(str(e).splitlines()[-1])


def main(argv):
    for f in (sys.stdout, sys.stderr):
        try: f.reconfigure(encoding='utf-8')
        except Exception: pass
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(__doc__); return 0
    try:
        return run(argv)
    except UsageError as e:
        sys.stderr.write('lp: %s\n' % e); return 2


OPTIONS = {'check': ('spec', 'stage', 'out'), 'render': ('out', 'clip'), 'preview': ('out', 'clip', 'phase', 'refs'),
           'overlay': ('out', 'threshold'), 'bake-springs': (), 'export-viewer': (), 'contract': ('out',), 'waste': ()}
ARGS = {'check': 1, 'render': 1, 'preview': 1, 'overlay': 2, 'bake-springs': 3, 'export-viewer': 3, 'contract': 1, 'waste': 1}


def run(argv):
    cmd, rest = argv[0], argv[1:]
    if cmd == 'bake-springs' and rest[:1] in (['-h'], ['--help']):
        from lowpoly import spring_bake; print(spring_bake.__doc__); return 0
    if cmd in ('overlay', 'preview') and rest[:1] in (['-h'], ['--help']):     # the tool's own usage: the refs.json format and more
        print(run_tool('measure_overlay' if cmd == 'overlay' else 'preview', '--help')); return 0
    if cmd not in OPTIONS: raise UsageError('unknown command %r (check, contract, waste, render, preview, overlay, bake-springs or export-viewer; lp --help for more)' % cmd)
    opts, pos, i = {}, [], 0
    while i < len(rest):
        if rest[i].startswith('--'):
            name = rest[i][2:]
            if name not in OPTIONS[cmd]: raise UsageError('lp %s does not take --%s' % (cmd, name))
            if i + 1 >= len(rest) or rest[i + 1].startswith('--'): raise UsageError('--%s needs a value' % name)
            opts[name] = rest[i + 1]; i += 2
        else: pos.append(rest[i]); i += 1
    if len(pos) != ARGS[cmd]:
        raise UsageError('lp %s takes %d argument%s, got %d (lp --help)' % (cmd, ARGS[cmd], '' if ARGS[cmd] == 1 else 's', len(pos)))
    if cmd == 'check':
        r, out = check(pos[0], opts.get('spec'), opts.get('stage', 'all'), opts.get('out'))
        sys.stdout.write(to_md(r)); print('\nreport: %s' % os.path.join(out, 'report.json'))
        return 0 if r['passed'] else 1
    if cmd == 'contract':
        spec, notes = read_spec(pos[0])
        targets = json.load(open(os.path.join(HERE, 'targets.json'), encoding='utf-8'))
        md = contract.describe(spec, spec['_contract'], targets['tiers'])
        if notes: md += '\n## Notes\n\n' + '\n'.join('- ' + n for n in notes) + '\n'
        if opts.get('out'): open(opts['out'], 'w', encoding='utf-8').write(md); print('wrote', opts['out'])
        else: sys.stdout.write(md)
        return 0
    if cmd == 'waste':
        read_model(pos[0]); sys.stdout.write(run_tool('topo_study', pos[0], '--waste')); return 0
    if cmd == 'render':
        for p in render(pos[0], opts.get('out'), opts.get('clip')): print('wrote', p)
        return 0
    if cmd == 'bake-springs':
        from lowpoly import spring_bake
        read_model(pos[0])
        if not os.path.isfile(pos[1]): raise UsageError('springs config not found: %s' % pos[1])
        os.makedirs(os.path.dirname(os.path.abspath(pos[2])), exist_ok=True)
        try: lines = spring_bake.bake_file(pos[0], pos[1], pos[2])
        except spring_bake.BakeError as e: raise UsageError(str(e))
        for line in lines: print(line)
        print('wrote', pos[2]); return 0
    if cmd == 'overlay':
        sys.stdout.write(overlay(pos[0], pos[1], opts.get('out'), opts.get('threshold'))); return 0
    if cmd == 'preview':
        sys.stdout.write(preview(pos[0], opts.get('out'), opts.get('clip'), opts.get('phase'), opts.get('refs'))); return 0
    if not os.path.isdir(pos[0]): raise UsageError('viewer folder not found: %s' % pos[0])
    try: A, tex = gltf_io.load_viewer(pos[0], pos[1])
    except StopIteration: raise UsageError('no model %r in %s' % (pos[1], pos[0]))
    os.makedirs(os.path.dirname(os.path.abspath(pos[2])), exist_ok=True)
    gltf_io.write_gltf(A, pos[2], tex); print('wrote', pos[2]); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
