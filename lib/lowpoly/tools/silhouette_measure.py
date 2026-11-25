"""Dense, exact measurements from a reference image's silhouette, so a builder measures instead of guessing.

A reference is only as useful as the numbers taken from it. Reading three or four ratios by eye leaves the rest of the
shape to be invented; this tool reads the whole outline. It separates the animal from a plain background (sampled from the
image's corners, or given), keeps solid regions only (thin guide lines, grids and text are dropped), and reports:
  side   at N stations from nose to tail: the top line and the underline, as heights above the ground over the reference
         height (the withers or the highest point of the back); plus the overall length.
  front, rear   at N heights from the ground up: the outline's left and right edges and the total width, over the height.
  top    at N stations from nose to tail: the half-width either side of the midline, over the body's length.
Use it on dead-on (orthographic) views: a conformation diagram, a model sheet, a photo taken square to the animal from far
away. A 3/4 or close-up photo foreshortens and its numbers are wrong.

  python silhouette_measure.py image --view side|front|rear|top [--box x0,y0,x1,y1] [--ground y] [--height-ref y]
                               [--stations 24] [--bg r,g,b] [--tol 60] [--json out.json]
    --box         the region holding the one view (a sheet often has several views side by side)
    --ground      the ground row (default: the lowest solid row in the box); not used for top views
    --height-ref  the row of the reference height (side: the withers; default: the box's highest solid row)
    --json        writes a refs.json "measured" entry (with "view", "measured", and the image as "source")
Needs Pillow for JPEG and WebP (PNG works with the standard library alone). Pillow usually lives in the user's site-packages,
which python -I hides: run it as  python -E silhouette_measure.py ...  with the plugin's tools folder as the working folder."""
import sys, os, json, math
args = sys.argv[1:]
if not args or args[0] in ('-h', '--help') or '--view' not in args: sys.exit(__doc__)
opt, pos, i = {}, [], 0
while i < len(args):
    if args[i].startswith('--'): opt[args[i][2:]] = args[i + 1]; i += 2
    else: pos.append(args[i]); i += 1
path, view = pos[0], opt['view']
N = int(opt.get('stations', 24)); TOL = float(opt.get('tol', 60))
try:
    from PIL import Image
    im = Image.open(path).convert('RGB'); W, H = im.size; px = im.load(); get = lambda x, y: px[x, y]
except ImportError:
    if not path.lower().endswith('.png'): sys.exit('silhouette_measure: Pillow is needed for %s (PNG works without it)' % path)
    here = os.path.dirname(os.path.abspath(__file__)); import zlib, struct
    src = open(os.path.join(here, 'foot_detail.py'), encoding='utf-8').read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
    W, H, rows = read_png(path); get = lambda x, y: tuple(rows[y][x][:3])
x0, y0, x1, y1 = (int(v) for v in opt['box'].split(',')) if 'box' in opt else (0, 0, W, H)
if 'bg' in opt: bg = tuple(int(v) for v in opt['bg'].split(','))
else:
    # the box's border, mostly background: the per-channel median of every border pixel (a guide line or ground line
    # crossing the border is a minority)
    cs = [get(x, y) for x in range(x0, x1, 2) for y in (y0, y1 - 1)] + [get(x, y) for y in range(y0, y1, 2) for x in (x0, x1 - 1)]
    bg = tuple(sorted(c[k] for c in cs)[len(cs) // 2] for k in range(3))
def raw(x, y): c = get(x, y); return abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) > TOL
M = {}
def fg(x, y):
    if not (x0 <= x < x1 and y0 <= y < y1): return False
    k = (x, y)
    if k not in M: M[k] = raw(x, y)
    return M[k]
def solid(x, y):   # 5x5 cross mostly foreground: drops 1-3 px guide lines, grid and text strokes
    return sum(fg(x + d, y) for d in (-2, -1, 0, 1, 2)) >= 5 and sum(fg(x, y + d) for d in (-2, -1, 0, 1, 2)) >= 5
rows_with = [y for y in range(y0 + 2, y1 - 2, 2) if any(solid(x, y) for x in range(x0 + 2, x1 - 2, 3))]
if not rows_with: sys.exit('silhouette_measure: nothing separated from the background %s (try --bg or --tol)' % (bg,))
top_row = rows_with[0]; bottom_row = rows_with[-1]
ground = int(opt.get('ground', bottom_row)); href = int(opt.get('height-ref', top_row))
out = {'view': view, 'source': path, 'use': 'measure-only', 'measured': {}}
if view in ('side', 'top'):
    cols = [x for x in range(x0 + 2, x1 - 2, 2) if any(solid(x, y) for y in range(y0 + 2, y1 - 2, 3))]
    L = cols[-1] - cols[0]; xs = [cols[0] + L * (k + 0.5) / N for k in range(N)]
    print('%s view: length %d px from x %d to %d; background %s' % (view, L, cols[0], cols[-1], bg))
    if view == 'side':
        Hh = ground - href
        print('reference height %d px (ground %d, reference row %d); length / height %.3f' % (Hh, ground, href, L / Hh))
        print(' station  x     top/H   under/H  depth/H')
        prof = []
        for k, x in enumerate(xs):
            ys = [y for y in range(y0 + 2, ground - 2) if solid(int(x), y)]
            if not ys: continue
            t, b = (ground - ys[0]) / Hh, (ground - ys[-1]) / Hh
            prof.append([round(k / (N - 1), 3), round(t, 3), round(b, 3)])
            print('  %5.2f %5d   %6.3f   %6.3f   %6.3f' % (k / (N - 1), x, t, b, t - b))
        out['measured'] = {'length_over_height': round(L / Hh, 3), 'profile_station_top_under_over_height': prof}
    else:
        print(' station  x     left/L   right/L  width/L')
        prof = []
        for k, x in enumerate(xs):
            ys = [y for y in range(y0 + 2, y1 - 2) if solid(int(x), y)]
            if not ys: continue
            mid = (ys[0] + ys[-1]) / 2
            prof.append([round(k / (N - 1), 3), round((ys[-1] - ys[0]) / L, 3)])
            print('  %5.2f %5d   %6.3f   %6.3f   %6.3f' % (k / (N - 1), x, (ys[0] - mid) / L, (ys[-1] - mid) / L, (ys[-1] - ys[0]) / L))
        out['measured'] = {'profile_station_width_over_length': prof}
else:
    Hh = ground - href
    print('%s view: height %d px (ground %d, top %d); background %s' % (view, Hh, ground, href, bg))
    print(' height/H  left_edge/H  right_edge/H  width/H  (pieces: separate legs or locks show as more than one run)')
    prof = []
    for k in range(N):
        y = int(ground - Hh * (k + 0.5) / N)
        runs, on, s = [], False, 0
        for x in range(x0 + 2, x1 - 2):
            v = solid(x, y)
            if v and not on: on, s = True, x
            if not v and on: on = False; runs.append((s, x))
        if on: runs.append((s, x1 - 2))
        runs = [r for r in runs if r[1] - r[0] >= 3]
        if not runs: continue
        l, r = runs[0][0], runs[-1][1]
        prof.append([round((ground - y) / Hh, 3), round((r - l) / Hh, 3), len(runs)])
        print('  %6.3f   %8d   %10d   %7.3f   %d' % ((ground - y) / Hh, l, r, (r - l) / Hh, len(runs)))
    out['measured'] = {'profile_height_width_over_height_pieces': prof}
if 'json' in opt:
    json.dump(out, open(opt['json'], 'w', encoding='utf-8'), indent=1); print('wrote', opt['json'])
