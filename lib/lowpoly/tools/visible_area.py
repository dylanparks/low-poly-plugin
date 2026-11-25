"""How much of a part the camera actually sees: a frame of a clip (or the bind pose) is drawn with a depth buffer from the
front, the 3/4 front, the side, the rear and the top, and every cell is credited to the nearest triangle. The part's visible
area is the cells won by its triangles; the silhouette is every covered cell. Occluded triangles count for nothing, unlike a
sum of triangle areas, so it answers "how much wing does the player see when it is folded?" or "is the jaw visible from
the side?".

A triangle belongs to the part when the bone that weights its corners most (summed over its three corners) has a name
containing one of the given substrings (case-insensitive): "--bones d2,d3,d4,d5,forearm" for a bat's wing and membrane,
"jaw" for a lower jaw.

  python visible_area.py model.gltf --bones a,b,... [--clip name] [--phase 0.3] [--cell 0.004]
      --cell: the cell size in metres (default: the model's height / 300).

Prints one line per view:  view  part N.NNN m2  silhouette N.NNN m2  part share NN%.
Standard library only; reads the model with the plugin's own skinning (preview.py's posed())."""
import sys, os, math, contextlib, io, tempfile
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
argv = sys.argv[1:]
if not argv or argv[0] in ('-h', '--help') or '--bones' not in argv: sys.exit(__doc__)
opts, pos, i = {}, [], 0
while i < len(argv):
    if argv[i].startswith('--'): opts[argv[i][2:]] = argv[i + 1] if i + 1 < len(argv) else ''; i += 2
    else: pos.append(argv[i]); i += 1
model = pos[0]; subs = [s.strip().lower() for s in opts['bones'].split(',') if s.strip()]
clip = opts.get('clip'); phase = float(opts.get('phase', 0))
src_path = os.path.join(here, 'preview.py')
head = open(src_path, encoding='utf-8').read().split("# yaw 0 looks at")[0]
g = {'__file__': src_path, '__name__': 'visible_area'}
sys.argv = ['preview.py', model, tempfile.gettempdir(), '-', '0']
with contextlib.redirect_stdout(io.StringIO()): exec(compile(head, src_path, 'exec'), g)
A, T, V, posed = g['A'], g['T'], g['V'], g['posed']
if clip and clip not in A.get('anims', {}): sys.exit('visible_area: no clip %r (clips: %s)' % (clip, ', '.join(A.get('anims', {}))))
names = list(g.get('names') or A['bones'])
def owner(t):
    acc = {}
    for c in t:
        for b, w in V[c][1]: acc[b] = acc.get(b, 0) + w
    b = max(acc, key=acc.get); return names[b] if 0 <= b < len(names) else ''
part = [any(s in owner(t).lower() for s in subs) for t in T]
if not any(part): sys.exit('visible_area: no triangle is owned by a bone matching %s (bones: %s)' % (subs, ', '.join(names)))
P, _ = posed(clip, phase)
H = max(p[1] for p in P) - min(p[1] for p in P)
S = float(opts['cell']) if opts.get('cell') else max(H, 1e-6) / 300
# camera directions: (name, yaw, pitch); yaw 0 looks along -z at the animal's front (it faces +z), 90 from its left side
VIEWS = [('front', 0, 0), ('3/4 front', 45, 15), ('side', 90, 0), ('rear', 180, 0), ('top', 0, 90)]
def proj_for(yaw, pitch):
    a, b = math.radians(yaw), math.radians(pitch)
    f = (math.sin(a) * math.cos(b), math.sin(b), math.cos(a) * math.cos(b))           # toward the camera
    r = (math.cos(a), 0.0, -math.sin(a))                                              # screen right
    u = (f[1] * r[2] - f[2] * r[1], f[2] * r[0] - f[0] * r[2], f[0] * r[1] - f[1] * r[0])  # screen up
    return lambda p: (p[0] * r[0] + p[1] * r[1] + p[2] * r[2], p[0] * u[0] + p[1] * u[1] + p[2] * u[2], p[0] * f[0] + p[1] * f[1] + p[2] * f[2])
print('%s, %s, bones matching %s, cell %.1f mm' % (os.path.basename(model), ('clip %s phase %.2f' % (clip, phase)) if clip else 'bind pose',
                                                  ','.join(subs), S * 1000))
for name, yaw, pitch in VIEWS:
    proj = proj_for(yaw, pitch); zb = {}; own = {}
    for k, t in enumerate(T):
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = (proj(P[c]) for c in t)
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-14: continue
        for ix in range(int(math.floor(min(ax, bx, cx) / S)), int(math.floor(max(ax, bx, cx) / S)) + 1):
            for iy in range(int(math.floor(min(ay, by, cy) / S)), int(math.floor(max(ay, by, cy) / S)) + 1):
                qx, qy = (ix + .5) * S, (iy + .5) * S
                l1 = ((by - cy) * (qx - cx) + (cx - bx) * (qy - cy)) / den; l2 = ((cy - ay) * (qx - cx) + (ax - cx) * (qy - cy)) / den
                l3 = 1 - l1 - l2
                if min(l1, l2, l3) < 0: continue
                z = l1 * az + l2 * bz + l3 * cz
                if z > zb.get((ix, iy), -1e18): zb[(ix, iy)] = z; own[(ix, iy)] = part[k]
    pa = sum(1 for v in own.values() if v) * S * S; tot = len(own) * S * S
    print('  %-10s part %.3f m2  silhouette %.3f m2  part share %2.0f%%' % (name, pa, tot, 100 * pa / max(tot, 1e-12)))
