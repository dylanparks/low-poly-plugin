"""The character viewer: a page that shows a character model with its customization panel (the options a character
creator offers, such as a skin tone slider and a muscle slider), skinned and morphed live with its clips.
Usage: python -I character_view.py <model.gltf> [out dir]
Reads <model>.character.json beside the model (lowpoly-characters writes it): {"options": [...]}, each option
  {"id", "label", "type": "tone", "mask": a greyscale PNG of the bare skin's texels, "painted": the skin's painted RGB,
   "ramp": [[r, g, b], ...] palest to darkest, "default": 0..1, optional "sheen" (keeps painted highlights on dark
   tones) and "soften" (0..1: lifts the painted shadows as the tone gets light)}
  {"id", "label", "type": "morph", "min", "max", "default", "below": the morph target used under 0, "above": over 0}
Optional "clip_blends": [{"clip", "option", "below", "above"}]: a blend space, the clip mixed toward the variant clip
  "below" (the option under 0) or "above" (over 0) by |value|, bone by bone; the variants are left off the clip list
  (the idle's arms rest further from the body as the muscle grows).
The morph targets come from the glTF (glTF morph targets, applied before skinning, so every clip works at any value).
Writes <out dir>/character.html (default: <model dir>/character), one self-contained file. Standard library only."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 2 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import base64, json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
from lowpoly import gltf_io, rig_parts  # noqa: E402

model = sys.argv[1]
mdir = os.path.dirname(os.path.abspath(model)); base = os.path.splitext(os.path.basename(model))[0]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(mdir, 'character')
A, tex_path = gltf_io.read_gltf(model)
cfg_path = os.path.join(mdir, base + '.character.json')
cfg = json.load(open(cfg_path, encoding='utf-8')) if os.path.exists(cfg_path) else {'options': []}
sub = A['subs'][0]
morphs = sub.get('morphs', [])
if not cfg['options'] and morphs:                          # no character file: one slider per pair of morph targets
    cfg['options'] = [{'id': 'body', 'label': 'Body', 'type': 'morph', 'min': -1, 'max': 1, 'default': 0,
                       'below': morphs[0]['name'], 'above': morphs[-1]['name']}]


def data_url(path):
    if not path or not os.path.exists(path): return ''
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


masks = []                                                 # one per tone option, in order (the page takes the first two)
for o in cfg['options']:
    if o.get('type') == 'tone':
        masks.append(data_url(o['mask'] if os.path.isabs(o['mask']) else os.path.join(mdir, o['mask'])) if o.get('mask') else '')
tex = tex_path if isinstance(tex_path, str) else (tex_path[0] if tex_path else None)
if not tex or not os.path.exists(tex or ''):
    cand = os.path.join(mdir, base + '.png'); tex = cand if os.path.exists(cand) else None
names = A['bones']; J = rig_parts.joints(A)
head_y = J[names.index('head')][1] + 0.08 if 'head' in names else None
data = {'name': A.get('name', base), 'v': sub['v'], 'idx': sub['i'], 'morphs': morphs, 'bones': names, 'parent': A['parent'],
        'rest': A['rest'], 'inv': A['inv'], 'clips': A.get('anims', {}), 'idle': A.get('idle', ''), 'tex': data_url(tex),
        'masks': masks, 'options': cfg['options'], 'head_y': head_y, 'blends': cfg.get('clip_blends', [])}
page = open(os.path.join(here, 'character_page.html'), encoding='utf-8').read()
page = page.replace('__TITLE__', data['name'].replace('<', '')).replace('__DATA__', json.dumps(data))
os.makedirs(out, exist_ok=True)
dst = os.path.join(out, 'character.html'); open(dst, 'w', encoding='utf-8').write(page)
print('character viewer: %s (%d options: %s; %d morph targets; clips %s)' % (
    dst, len(cfg['options']), ', '.join(o['label'] for o in cfg['options']), len(morphs), ', '.join(data['clips']) or 'none'))
