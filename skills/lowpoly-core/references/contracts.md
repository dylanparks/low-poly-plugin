# Style contracts: one look, shared by every part and every model

A model is built in parts (the body, the head, a mane, wings), often by several builders over several rounds. Without a
written look, the parts drift.

**The first alicorn showed what drift looks like.** Each part passed its own review, and put together:
- the mane was thin ribbons;
- the folded wings were flat grey slabs painted at twice the body's texel density;
- the eye was a 2-texel dot;
- the muzzle was a cone;
- the parts together came to 908 triangles on a 720 tier.

A **contract** writes the look down once, in layers, so that `lp check` can judge every part against it, and against the
other parts.

## The layers

A contract is the model's `spec.json`, naming shared profiles from `lib/lowpoly/profiles/`. Each profile is one layer, from
the most general to the most specific:

| Layer | What it holds | Shared by | Examples |
|---|---|---|---|
| `style/` | the game's look: painted light and form, gradients over 2-4 texels, no outlines, parts matching the body | every model | `style/late-90s-rpg` |
| tier and body plan | budgets and texture size (`targets.json` tiers; the spec's `tier`, `body_plan`) | every model of a size | very-large, quadruped |
| `muzzle/`, `eyes/` | a kind of part, with its rules and check ranges | every animal with that kind | `muzzle/soft-equine` (horse, donkey, zebra), `eyes/side-almond` (horse, cow, deer) |
| `species/` | an animal: picks its kinds, adds its own rules and numbers | every build of that animal | `species/horse`, `species/red-fox`, `species/housecat` |
| `colour/` | a colour variety: its palette, and which skin shows through | every animal of that colour | `colour/grey-horse` (dark skin at the nose, lips and eyes), `colour/flame-point-siamese` |
| `scale/` | a size standard: the tier, the budget's range and how to split it | every animal of that size | `scale/small-animal` (housecat-sized: about 140 vertices, 280 triangles, 256 x 128) |
| `temperament/` | how the model behaves toward the player: changes features the other layers describe. Always resolves after every other profile | every mob of that temperament | `temperament/hostile` (the glowing eye, `references/temperament.md`) |
| the contract | this build only: its parts with their bones and budgets, its palette, its exceptions | one model | `agent_builds/alicorn/spec.json` |

**How the layers combine.**
- Each profile's `extends` comes first. `colour/grey-horse` extends `species/horse`, which extends `muzzle/soft-equine` and
  `eyes/side-almond`.
- Later layers override earlier ones, and the contract overrides them all.
- `"set"` fills in what the model is (`"muzzle": "soft-equine"`). Those values choose which checks run.
- `"checks"` sets ranges, for example eye.size at least 1.6 for a horse.
- `"palette"` and `"rules"` are for the builders.
- `"supersedes"` lists the starts of earlier layers' rules that this layer replaces. The brief drops them and lists them
  under "Rules replaced by a later layer", so a builder never reads two rules that disagree (a pupil eye and a glow).

A contract for a red fox is only a few lines. It names its profiles, and everything else comes from them:

```json
{"tier": "medium", "profiles": ["style/late-90s-rpg", "species/red-fox"],
 "parts": {"head": {"bones": ["head", "ear_*"], "triangles": 160},
           "tail": {"bones": ["tail*"], "triangles": 60},
           "legs": {"bones": ["thigh_*", "shin_*", "foot_*", "hpaw_*", "arm_*", "fore_*", "paw_*"], "triangles": 200}}}
```

## Parts

`"parts"` names each part by the bones that carry it, written as patterns. A triangle belongs to the part whose bones carry
most of its weight, and every other triangle is the body. For each part `lib/lowpoly/tools/parts_study.py` measures:

| Check | What it compares | Default | Measured |
|---|---|---|---|
| parts.budget | the part's triangles against its `"triangles"` | over by 0 | the first alicorn's legs 50 over |
| parts.density | its texels per metre against the body's, within its `"density"` range | 0.6-2.5 times the body | approved builds 0.81-1.14; the first alicorn's wings 2.15 |
| parts.joins | the brightness step across its join to what it grows from (`"joins"`, default the body), on the triangles either side | at most 0.12 | approved builds 0.01-0.08; the first alicorn's head 0.13 |

- **Contrast parts.** A part meant to differ from what it joins (a rainbow mane on a white neck, a dark hoof on a pale leg)
  is marked `"contrast": true`. Its step is reported but not judged.
- **Budgets.** Give the parts budgets that leave the body its share of the tier. `lp contract` adds them up against the
  tier.

## Using it

1. **Write the contract before building.** Choose the profiles from the reference translation
   (`references/measuring.md`, "Turning the request into search subjects"). A white unicorn becomes `colour/grey-horse`, plus
   parts for the horn, mane and wings.
2. **Brief every builder from it.** `lp contract spec.json --out brief.md` prints the resolved contract: each layer, what it
   sets, the check ranges, the parts with their budgets, the palette, and the rules with the skill reference each comes
   from. A builder of one part reads the whole brief, so the part comes out in the same style as the others.
3. **Check every merge against it.** `lp check model.gltf --spec spec.json` runs the profile-tied checks for its kinds
   (nose.nostrils and nose.width for a soft or bare muzzle, eye.size with the species' minimum) and the parts.* checks. Each
   result names the layer its range came from.
4. **When a new animal or variety comes up,** add a profile, not a one-off rule. A donkey is `species/donkey` extending
   `muzzle/soft-equine` and `eyes/side-almond`. A dun horse is a `colour/` profile on `species/horse`. Rules that hold
   across species belong in the kind layer.
