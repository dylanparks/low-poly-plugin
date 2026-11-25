"""Style contracts: a model's spec.json, layered on shared profiles. Standard library only.

A contract is a spec.json that may name profiles. Each profile is one layer of shared rules, from the most general to the
most specific:
  style/    the game's look, for every model (lighting, gradients, no outlines, parts matching the body)
  muzzle/   a kind of muzzle (leather-pad, soft-equine, muffle, small-bare, disc, split-lip, lipless, beak)
  eyes/     a kind of eye (side-almond, forward)
  species/  an animal (horse, red-fox, housecat): picks its kinds and adds its own rules and numbers
  colour/   a colour variety of a species (grey-horse, flame-point-siamese): its palette and which skin shows
  scale/    a size standard (small-animal: a housecat's size): the tier, the budget's range, how to split it
  temperament/  how the model behaves toward the player (hostile): it changes features the other layers describe (a hostile
            mob's eye glows), so temperament layers always resolve after every other profile, wherever they are listed
The contract itself is the top layer: the build's parts and their budgets, its palette, its own exceptions.

Profile format (lib/lowpoly/profiles/<layer>/<name>.json):
  {"about": "...", "extends": ["muzzle/soft-equine"], "set": {"muzzle": "soft-equine"},
   "checks": {"eye.size": {"min": 1.6}}, "palette": {"skin": "charcoal"}, "rules": ["..."], "ref": "skill reference",
   "supersedes": ["the start of an earlier layer's rule"]}   (a superseded rule is dropped from the brief and listed as replaced)
Contract keys on top of the spec's: "profiles": [names], "checks": {id: {min, max, level}}, "parts": {name: {...}}
(lowpoly/tools/parts_study.py), "palette": {...}, "rules": [...].

Resolution: each profile's "extends" first (depth first, each profile once), then the profile, in the listed order, then the
contract. "set" values fill spec keys the contract leaves out (the contract always wins); check overrides and palette
entries go to the last layer that names them; rules accumulate. Every value remembers the layer it came from."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, 'profiles')
CONTRACT_KEYS = {'profiles', 'checks', 'parts', 'palette', 'rules'}


class ContractError(Exception):
    pass


def load_profile(name):
    p = os.path.join(PROFILES, *name.split('/')) + '.json'
    if not os.path.isfile(p):
        have = sorted('%s/%s' % (d, f[:-5]) for d in os.listdir(PROFILES) if os.path.isdir(os.path.join(PROFILES, d))
                      for f in os.listdir(os.path.join(PROFILES, d)) if f.endswith('.json'))
        raise ContractError('unknown profile %r (have: %s)' % (name, ', '.join(have)))
    try: return json.load(open(p, encoding='utf-8'))
    except ValueError as e: raise ContractError('profile %s is not valid JSON: %s' % (name, e))


def layers(names, seen=None, chain=()):
    """the profiles in resolution order: each one's extends first, every profile once"""
    seen = set() if seen is None else seen; out = []
    for n in names:
        if n in chain: raise ContractError('profile cycle: %s' % ' -> '.join(chain + (n,)))
        if n in seen: continue
        prof = load_profile(n)
        out += layers(prof.get('extends', []), seen, chain + (n,))
        if n not in seen: seen.add(n); out.append((n, prof))
    return out


def resolve(spec):
    """(the spec with every layer's values filled in, the resolution: sources, check overrides, palette, rules, parts)"""
    P = layers(spec.get('profiles', []))
    P = [l for l in P if not l[0].startswith('temperament/')] + [l for l in P if l[0].startswith('temperament/')]
    L = P + [('contract', {k: spec[k] for k in ('checks', 'palette', 'rules') if k in spec})]
    merged = dict(spec); src = {k: 'contract' for k in spec if k not in CONTRACT_KEYS}
    checks, palette, rules, superseded = {}, {}, [], []
    for name, prof in L:
        for k, v in (prof.get('set') or {}).items():
            if k not in spec: merged[k] = v; src[k] = name          # a later profile overrides an earlier one, the contract all
        for cid, o in (prof.get('checks') or {}).items(): checks[cid] = dict(o, source=name)
        for k, v in (prof.get('palette') or {}).items(): palette[k] = (v, name)
        for pre in prof.get('supersedes') or []:
            for item in [x for x in rules if x[1].startswith(pre)]: rules.remove(item); superseded.append(item + (name,))
        for r in prof.get('rules') or []: rules.append((name, r))
    return merged, dict(layers=[n for n, _ in L], sources=src, checks=checks, palette=palette, rules=rules, superseded=superseded,
                        parts=spec.get('parts') or {}, refs={n: p.get('ref') for n, p in L if p.get('ref')})


def describe(spec, res, tiers=None):
    """the resolved contract as Markdown: the brief every builder of a part reads"""
    m, out = spec, []
    out += ['# Contract: %s' % m.get('name', '(unnamed)'), '', 'Layers, general to specific: ' + ' > '.join(res['layers']), '']
    out += ['## What the model is', '', '| Key | Value | From |', '|---|---|---|']
    for k in sorted(res['sources']):
        if k in ('eye', 'refs', 'standing_clips', 'walk_clip', 'ref_parts', 'name'): continue
        out.append('| %s | %s | %s |' % (k, json.dumps(m[k]) if not isinstance(m[k], str) else m[k], res['sources'][k]))
    if res['checks']:
        out += ['', '## Check ranges this contract sets', '', '| Check | Range | Level | From |', '|---|---|---|---|']
        for cid, o in sorted(res['checks'].items()):
            rng = '%s-%s' % (o.get('min', ''), o.get('max', '')) if 'min' in o and 'max' in o else ('at least %s' % o['min'] if 'min' in o else 'at most %s' % o.get('max'))
            out.append('| %s | %s | %s | %s |' % (cid, rng, o.get('level', '(default)'), o['source']))
    if res['parts']:
        out += ['', '## Parts', '', '| Part | Bones | Triangle budget | Density x body | Joins | Contrast |', '|---|---|---|---|---|---|']
        total = 0
        for n, p in res['parts'].items():
            total += p.get('triangles') or 0
            out.append('| %s | %s | %s | %s | %s | %s |' % (n, ', '.join(p.get('bones', [])), p.get('triangles', '-'),
                       '-'.join(str(x) for x in p.get('density', [0.6, 2.5])), p.get('joins', 'body'), 'yes' if p.get('contrast') else 'no'))
        tier = (tiers or {}).get(m.get('tier', ''))
        if tier and total: out += ['', 'Part budgets total %d triangles; the %s tier allows %d-%d for the whole model%s.'
                                   % (total, m['tier'], tier['triangles'][0], tier['triangles'][1],
                                      ' (over: the body has nothing left)' if total >= tier['triangles'][1] else '')]
    if res['palette']:
        out += ['', '## Palette', '', '| Where | Colour | From |', '|---|---|---|']
        out += ['| %s | %s | %s |' % (k, v, s) for k, (v, s) in res['palette'].items()]
    if res['rules']:
        out += ['', '## Rules']
        cur = None
        for s, r in res['rules']:
            if s != cur: out += ['', '**%s**%s' % (s, ' (%s)' % res['refs'][s] if s in res['refs'] else '')]; cur = s
            out.append('- ' + r)
    if res.get('superseded'):
        out += ['', '## Rules replaced by a later layer', '']
        out += ['- %s, replaced by %s: %s' % (s, by, r) for s, r, by in res['superseded']]
    return '\n'.join(out) + '\n'
