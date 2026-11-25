"""Parts against each other: does every part of a model share the body's texel density and brightness, and keep to its own
triangle budget? Standard library only. The parts and their budgets come from the model's contract (spec.json "parts").

Usage: python -I parts_study.py <model.gltf> <parts.json or a spec.json with "parts">
  "parts": {"<name>": {"bones": ["mane*", "neck2"], "triangles": 120, "density": [0.6, 2.5], "joins": "body", "contrast": false}}
  bones:     the bones whose triangles make the part (fnmatch patterns). A triangle belongs to the part of the bone that
             carries most of its corners' weight; triangles of no part are the body.
  min_weight: for a part that rides mostly on another's bones (a mane weighted to the neck, with its own bones only toward
             its edge): the share of a triangle's weight its bones need to claim it (0.01 = any weight at all).
  triangles: the part's budget (optional).
  density:   the part's texels per metre over the body's, the range it may take (default 0.6-2.5: a head may be painted
             denser than the body, never several times sparser or denser).
  joins:     the part (or "body") it grows out of: the brightness step across that join is measured on the triangles either
             side of it (default "body").
  contrast:  true when the part is meant to differ from what it joins (a rainbow mane on a white neck, a dark hoof on a
             pale leg): its join step is reported but not judged.
Prints one line per part:
  part <name>: <n> triangles (budget <b>) | density <d> texels/m = <r> x body (range lo-hi) | brightness <l> | join <target> step <s>
"""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 3 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, fnmatch, json, math, os, struct, sys, zlib

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
from lowpoly import gltf_io  # noqa: E402
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])

A, tex = gltf_io.read_gltf(sys.argv[1])
cfg = json.load(open(sys.argv[2], encoding='utf-8'))
PARTS = cfg.get('parts', cfg)
if not tex or not os.path.isfile(tex): sys.exit('no texture beside the model')
W, H, ROWS = read_png(tex)

s = A['subs'][0]; raw = base64.b64decode(s['v']); fl = struct.unpack('<%df' % (len(raw) // 4), raw)
C = [fl[i:i + 16] for i in range(0, len(fl), 16)]
ix = base64.b64decode(s['i']); I = struct.unpack('<%dH' % (len(ix) // 2), ix)
T = [I[i:i + 3] for i in range(0, len(I), 3)]
bones = A['bones']


def part_of_bone(b):
    for name, p in PARTS.items():
        if any(fnmatch.fnmatchcase(b, pat) for pat in p.get('bones', [])): return name
    return 'body'


BPART = [part_of_bone(b) for b in bones]


def tri_part(t):
    wsum = {}
    for i in t:
        c = C[i]
        for k in range(4): wsum[BPART[int(c[12 + k])]] = wsum.get(BPART[int(c[12 + k])], 0.0) + c[8 + k]
    tot = sum(wsum.values()) or 1.0
    for name, p in PARTS.items():                 # a part riding on another's bones claims any triangle it carries enough of
        if 'min_weight' in p and wsum.get(name, 0.0) / tot >= p['min_weight']: return name
    return max(wsum, key=wsum.get)


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def lum(c): return (0.2126 * (c[0] / 255) ** 2.2 + 0.7152 * (c[1] / 255) ** 2.2 + 0.0722 * (c[2] / 255) ** 2.2) ** (1 / 2.2)


def texel(u, v):
    x = min(W - 1, max(0, int(u * W))); y = min(H - 1, max(0, int(v * H))); return lum(ROWS[y][x])


def tri_stats(t):
    P = [C[i][:3] for i in t]; UV = [(C[i][6], C[i][7]) for i in t]
    a3 = 0.5 * math.sqrt(sum(x * x for x in cross(sub(P[1], P[0]), sub(P[2], P[0]))))
    a2 = 0.5 * abs((UV[1][0] - UV[0][0]) * (UV[2][1] - UV[0][1]) - (UV[2][0] - UV[0][0]) * (UV[1][1] - UV[0][1])) * W * H
    pts = [(1 / 3, 1 / 3), (2 / 3, 1 / 6), (1 / 6, 2 / 3), (1 / 6, 1 / 6)]
    l = sum(texel(UV[0][0] + a * (UV[1][0] - UV[0][0]) + b * (UV[2][0] - UV[0][0]),
                  UV[0][1] + a * (UV[1][1] - UV[0][1]) + b * (UV[2][1] - UV[0][1])) for a, b in pts) / len(pts)
    return a3, a2, l


TP = [tri_part(t) for t in T]
ST = [tri_stats(t) for t in T]
key = lambda i: (round(C[i][0], 4), round(C[i][1], 4), round(C[i][2], 4))
at_pos = {}
for k, t in enumerate(T):
    for i in t: at_pos.setdefault(key(i), set()).add(k)


def agg(ks):
    a3 = sum(ST[k][0] for k in ks); a2 = sum(ST[k][1] for k in ks)
    l = sum(ST[k][2] * ST[k][0] for k in ks) / a3 if a3 > 0 else None
    return a3, a2, l


names = ['body'] + [n for n in PARTS]
stats = {n: agg([k for k, p in enumerate(TP) if p == n]) for n in names}
def dens(n): a3, a2, _ = stats[n]; return math.sqrt(a2 / a3) if a3 > 0 else None
bd = dens('body')
print('== %s: %d triangles; body %d triangles, %s texels/m, brightness %s'
      % (A['name'], len(T), TP.count('body'), '%.0f' % bd if bd else '-', '%.2f' % stats['body'][2] if stats['body'][2] is not None else '-'))
for n in PARTS:
    p = PARTS[n]; ks = [k for k, q in enumerate(TP) if q == n]
    if not ks: print('part %s: 0 triangles (no bone matched %s)' % (n, p.get('bones'))); continue
    d = dens(n); lo, hi = p.get('density', [0.6, 2.5]); tgt = p.get('joins', 'body')
    border_p = [k for k in ks if any(TP[j] == tgt for i in T[k] for j in at_pos[key(i)])]
    border_t = sorted({j for k in border_p for i in T[k] for j in at_pos[key(i)] if TP[j] == tgt})
    step = None
    if border_p and border_t:
        step = agg(border_p)[2] - agg(border_t)[2]
    budget = p.get('triangles')
    print('part %s: %d triangles (budget %s) | density %.0f texels/m = %.2f x body (range %s-%s) | brightness %.2f | join %s step %s%s'
          % (n, len(ks), budget if budget is not None else '-', d, d / bd if bd else 0, lo, hi, stats[n][2], tgt,
             '%+.2f' % step if step is not None else '-', ' (contrast)' if p.get('contrast') else ''))
