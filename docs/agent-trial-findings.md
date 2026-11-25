# Agent trial: three builders on the plugin alone

Three Sonnet-level builders each built one animal using only this plugin (the skill, its references, `lp`, `gltf_io`,
`mesh_tidy` and the tools). A reviewer did the visual QA a person would: loaded each build into an engine-like viewer,
compared it with the builder's own references, and sent feedback. The animals were picked to hit gaps: a Nile crocodile
(sprawling reptile, scutes), a bald eagle (bird, feathers, wings) and an emperor scorpion (arthropod, chitin, 8 legs).

## Outcome

| Animal | Rounds to approval | What the rounds were about |
|---|---|---|
| Crocodile | 4 | Tail and crests, then box-section legs, then the legs' pose (level "shelves" instead of an arch) |
| Scorpion | 4 | Pincers and legs from a wrong-genus reference, zebra-striped paint, then leg length overshooting both ways, then the stinger |
| Eagle | 4 | Board-like wings and bare legs, then whole-body proportions (pillar legs, ground-length tail), then a flight-only tail shape used at rest |

All three end inside their budgets and read as the animal from every angle. Known gaps left: the eagle's spread wing is
a narrow strip; the scorpion has 29% unmirrored triangles (on-axis quads).

**The plugin works standalone** in the sense that every builder finished without asking questions. But every build needed
the reviewer for things no check caught, and every builder wrote tools the plugin should have shipped. 51 friction points
were logged; they collapse into the patterns below, ordered by how many review rounds each would have saved.

## The patterns

1. **No builder ever saw what the reviewer saw.** All three judged their work from home-made renderers (too bright,
   blank slivers, wrong framing) and none looked from behind or above. Most round-2 and round-3 feedback concerned views the
   builder never rendered (the crocodile's legs from behind, the eagle's wings from the rear, the scorpion's hidden legs).
2. **Checks that pass while the model is wrong, and fail while it is right.** Bright stripes passed `chitin.gloss` (the
   zebra scorpion); a correctly dark crocodile failed four scale checks; quadruped checks warned on a bird's thigh; the
   foot study's fixed height zone forced three builders to bend their models around it (a tail lifted off the ground, a
   knee held high, a feather cuff counted as toes).
3. **"Lines up closely" without numbers.** Overlays were looked at, not measured, so a club-shaped pincer passed as
   "close" and leg-length corrections overshot both ways for lack of a target number.
4. **References with no metadata.** A wrong-genus photo went unnoticed for a round; flight photos were used for a
   perched pose; candidates were approved blind because no builder could preview them.
5. **Body plans the skill only names.** No arthropod L or budget, no bird wing construction, no checklist of the parts that
   decide the read for a group (a raptor's trousers, hooked beak and closed tail).
6. **Missing build helpers.** Every builder reverse-engineered `write_gltf`'s layout, and wrote its own ring stitch,
   mirror check, ring-angle and proportion measures.
7. **Tools that crash on non-quadrupeds**, and `lp check` reporting FAILED with zero failures when a tool crashed.

## Recommendations

### Scripts and commands (highest value first)

1. **`lp preview <model.gltf>`** *(done, 2026-11-21)*: writes the six fixed views (3/4 front, 3/4 rear, side, front, rear,
   top) under the engine's lights as one sheet, and a self-contained WebGL page to orbit the model and play its clips. The
   builder attaches the sheet to every report, so builder and reviewer judge the same pictures. Run on the three trial
   builds, its front and rear views show at once what took the reviewer a round to find (the crocodile's flat-ended
   thighs). *(Patterns 1, 7.)*
2. **A measuring overlay, `lp overlay`** *(done, 2026-11-21: `measure_overlay.py`; its first run on the trial's crocodile
   found its feet 10% of the body length ahead of the photo's, where the builder had reported them in agreement)*: landmarks marked once per reference in `refs.json` (nose, eye, each joint, each
   foot tip, tail stations) and found on the model from the rig; prints a table of differences per part, per reference,
   with the reference's basis. Feedback then quotes a target and a tolerance from that table. *(Pattern 3.)*
3. **Rig-based framing in every tool** *(done, 2026-11-21: `lowpoly/rig_parts.py`)*: the head, limbs and feet are read
   from the rig in the head tools, the eye tool, the lit views, the foot study and the standing balance. The scorpion's
   `lp check` now runs every stage (it said FAILED with no failed check), its `lp render` no longer crashes, the
   crocodile's head close-ups are no longer blank, and the eagle's two feet are no longer counted as one. Reference
   numbers unchanged. Still on the height rule: `limb_widths.py`'s limb search (it skips sprawling legs) and
   `rig_study.py`'s walk lift. *(Patterns 2, 7.)*
4. **New `lp check` measures:**
   - `symmetry`: triangles without a mirror twin, with quads on the midline named rather than counted.
   - `limb_pose`: each limb's segment angles from behind and above, judged against the body plan's range.
   - `proportions`: standing height, belly height, visible leg, tail tip and ground clearance as shares of the height,
     against the reference table.
   - `interpenetration`: vertices of one part inside another's volume (the eagle's tail through its wing).
   - `rings`: each limb ring's corner angles, which flags box sections.
5. **Honest verdicts**: INCOMPLETE when a tool crashes, n/a with a reason when a check doesn't apply to the body plan,
   and a time budget per tool (the feathers stage ran past ten minutes). Warnings name their worst faces by bone and
   position.
6. **`lp refs search` / `lp refs prep`**: search Commons and other free sources by species, fetch small previews under a
   standing approval for triage, then download, convert and scale the approved set.

### Templates

1. **`refs.json` manifest**: one entry per reference with species, view, pose state (rest, walking, flying), licence,
   source, scale and landmarks. The approval step becomes one table; the build script's header is generated from it.
2. **Starter build script** with a documented `build_model(verts, faces, weights, bones, clips)` and the helpers builders
   kept writing: an unequal-ring stitch, a weld that carries vertex attributes, mirror-by-construction rings with a
   vertex on the midline, and scale keys in `gltf_io` animations.
3. **Fixed report template**: status, `lp check` line, the six `lp preview` views, the overlay table, decisions with
   sources, unverified items, friction. A missing section is then obvious.

### Skill and reference changes

1. **Body-plan profiles** in `targets.json` and §3 (arthropod, bird, sprawling reptile), each with its L, budget tier,
   which checks apply, and a reference checklist: the views to gather, which usually have to come from photos, and the
   parts that decide the read.
2. **A bird reference** like `feet.md`: the folded wing's outline and weld, the spread wing's chord and slotted primaries,
   a rig that folds one into the other, and rest versus action states (tail closed perched, fanned in flight).
3. **Checks relative to the builder's photos**, not fixed ranges: gloss and value steps measured against the pelt's own
   mean, with a rule that a range is a sanity bound and the reference decides.
4. **§1 additions**: a fallback order when a muscle plate doesn't exist, a licence line, how to use a mounted skeleton,
   where absolute size comes from, and a priority for conflicting numbers (bone lengths from the reference first, then
   the pose).

## What the reviewer loop itself taught

- Feedback naming a shape gets a shape fix. When the real cause is a pose or a whole-body proportion, say that, and ask
  for the rear and top views.
- Feedback per part drifts the whole body; ask for the whole-body proportion numbers every round.
- Give target numbers, not directions, and check them against the size the part needs to read on screen.
- The reviewer's own feedback can be wrong (a perched tail described from flight photos). The reference's state has to be
  part of the reference.
