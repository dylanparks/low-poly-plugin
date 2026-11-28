# lowpoly-modeling (draft)

A plugin draft. Three skills so far:

- `skills/lowpoly-core/`: the method every low-poly model shares: the reference set and measuring against it in every view,
  budgets, one-skin topology, rigs and weights, the texture method (seams, density, stretched faces, the engine's lights),
  temperament, the motion checks, and the failures that recur in any build. Loaded first.
- `skills/lowpoly-animals/`: what is particular to animals, on top of the core: body plans, limb joins, feet, heads, coats
  and skins, gaits. `references/parts.md` indexes the body parts the builds have solved (wings, beaks, jaws, feet, tails,
  manes, skins) as modules, the groundwork for composite and fantasy animals assembled from real parts;
  `references/reptile-skin.md` is the standard for a reptile's hide.
- `skills/lowpoly-characters/`: humans and humanoid races built on the human base: measuring a body against a survey, the
  torso and limbs from muscle, body types as morph targets and blend spaces, the head's planes, ears, eyes and mouth,
  hands and thumbs, joints that fold with soft tissue meeting, a character's charts and recolour options, hair, and
  `references/races.md` for orcs, ogres, trolls, goblins, dwarves and elves from the real anatomy each borrows. Its case
  study is the first player character, a median man.

The animal skills' measured ranges come from the shipped animal models of a late-1990s commercial RPG. The character
skill's numbers come from anatomy (a public body survey, clinical and art-anatomy references, biomechanics papers); that
game's human models were measured as era context only. Only measurements are used; no model, texture, file or name from
that game is part of this plugin.

## Plans

- `docs/automation-plan.md`: turning the process into a pipeline.
  - **Scripts:** an `lp` command in `bin/`, a shared build library and `targets.json` for every measured range.
  - **Agents:** one specialist per stage and a read-only reviewer.
  - **Hooks:** `SubagentStop`, `Stop` and `PreToolUse` refuse to move on until the checks pass.

## Commands

`bin/lp` (and `bin/lp.cmd` on Windows) runs `lib/lowpoly/cli.py`. Python 3.8 or newer; nothing else, except Pillow for
reading JPEG references in `silhouette_measure.py`. `lp --help` has the full usage.

| Command | What it does |
|---|---|
| `lp check <model> [--spec spec.json] [--stage mesh\|rig\|texture\|motion\|all] [--out dir]` | Runs the tools that apply to the spec and judges 91 checks against `lib/lowpoly/targets.json`; writes `report.json`, `report.md` and each tool's raw output; exits 1 on a check at the "fail" level |
| `lp waste <model>` | How the model spends its polygons: rendered vertices per position, each part's share of the triangles against its share of the surface, mirrored construction, and every edge that could be collapsed with almost no change. Run on the untextured blockout (gate 1) |
| `lp contract <spec.json> [--out brief.md]` | Resolves a style contract: the shared profiles in `lib/lowpoly/profiles/` (style, muzzle and eye kinds, species, colour, scale, temperament) layered under the model's own parts, palette and rules; prints the brief every part builder works from (`skills/lowpoly-core/references/contracts.md`) |
| `lp preview <model> [--clip c] [--phase p] [--out dir] [--refs refs.json]` | Six fixed views (3/4 front, 3/4 rear, side, front, rear, top) shaded as the viewer shades them, with a ground line and scale bar; `preview.html` to turn it round and play clips; with `--refs`, `compare.html` sets each view beside its references |
| `lp render <model> [--clip c] [--out dir]` | The head textured and lit, the hindquarters and the walk |
| `lp overlay <model> <refs.json> [--threshold 5] [--out dir]` | The model's landmarks and outlines against each reference's, aligned on two landmarks (optionally rotated), errors in metres and as a share of the span |
| `lp bake-springs <model> <springs.json> <out.gltf>` | Secondary motion (tails, feathers, ears, hair) baked into the clips as rotation keys: spring bones with stiffness, drag, gravity, colliders and the ground; per-clip settings and key counts |
| `lp export-viewer <dir> <id> <out.gltf>` | Converts a model from the viewer format the tools were first written for |

The spec (`lp --help`) says what the model is, so only the checks that apply run: body plan (a `flyer` skips the standing
checks; a `humanoid`, a person or humanoid race, skips the animal leg rules, while a `biped`, a two-legged animal, keeps
them), skin, feet, tier, eye (`"eyes": "glow"` for a pupil-less glow), open edges by design (`"cards"`), the references
(`"refs"`, `"ref_parts"`), a survey table for a body (`"measurements"`) and `"hero": true`, which makes the reference
checks fail instead of warn.

## Library

- `lib/lowpoly/build.py`: the half-model builder: arcs, strips, holes and loop bridges for the left half, `mirror_and_weld`,
  per-piece winding, a one-UV-per-vertex mirrored pelt, `pose_x` for an off-centre bind pose, `to_model` for `write_gltf`.
  `python -m lowpoly.build` runs its self-test.
- `lib/lowpoly/gltf_io.py`: glTF 2.0 in and out (.gltf with .bin, or .glb): skin, rest pose, clips, texture. A .bin that
  doesn't match its .gltf is refused.
- `lib/lowpoly/rig_parts.py`: the head, limbs and feet read from the rig (bone names, else the rig's shape), shared by the
  tools that once guessed them from the height.
- `lib/lowpoly/spring_bake.py`: the spring-bone baker behind `lp bake-springs` (the VRM spring-bone method, written from its
  description).
- `lib/lowpoly/animate.py`: building blocks for clips that read as alive: quaternions, a two-bone limb solved in three
  dimensions (a pelvis that turns and shifts over planted, pivoting or stepping feet), and timing curves (ease, overshoot,
  a damped settle, a lag down a chain). `python -m lowpoly.animate` runs its self-test.
- `lib/lowpoly/mesh_tidy.py`: removes slivers without changing the shape (welds, quad diagonals, mirrored stitching).
- `lib/lowpoly/targets.json`: every measured range the checks use, with its stage, level, what it applies to and the
  reference that explains it.

## Tools (`lib/lowpoly/tools/`, each prints its usage with `--help`)

| Area | Tools |
|---|---|
| Views | `preview.py` (behind `lp preview`), `lit_view.py` (viewer-shaded close-up at any angle), `head_views.py` and `head_textured.py` (the head untextured and textured), `region_views.py`, `walk_sheet.py` |
| References | `measure_overlay.py` (behind `lp overlay`), `ref_overlay.py` (draws a side view over a reference), `silhouette_measure.py` (dense outline measurements from a dead-on reference image) |
| Mesh and motion | `self_cross.py` (parts passing through each other, `--where`), `visible_area.py`, `thin_triangles.py`, `edge_angles.py`, `limb_widths.py`, `foot_study.py`, `stand_study.py`, `rig_study.py`, `topo_study.py` (behind `lp waste`: rendered vertices, triangle shares by part, mirrored construction, edges that shape nothing), `jaw_study.py` (the gape in every clip, modelled or painted teeth), `rear_study.py` (the haunch outline from behind: bulge, notch, corner), `leg_bend_study.py` (joints bent backwards, joint rings pinching, skin stretching along the legs, paired legs in lockstep, in every clip), `motion_quality.py` (whether each clip moves as a body with weight: parts all peaking at once, chains out of order, still bones, a head fixed to the trunk, feet that never shift or that slide, dead holds, mirrored limbs, the pelvis and chest in a gait; `--detail` lists every bone; behind `lp check`'s liveliness checks) |
| Texture | `uv_study.py`, `uv_reuse.py`, `body_study.py`, `skin_study.py`, `region_detail.py`, `eye_study.py`, `nose_study.py`, `ear_study.py`, `head_detail.py`, `foot_detail.py` |
| Characters | `body_measure.py` (a humanoid measured as a person against a survey table; behind `lp check`'s body.* checks), `character_view.py` (the character viewer: tone and morph options, clip blend spaces, orbit, pan and zoom; reads `<model>.character.json`) |

## Checks, by stage

- **Mesh:** budget per tier, closed skin (minus declared cards), loose pieces, slivers, feet, thighs, the overlay against the
  references, the reference set itself (`refs.views`, `refs.parts`, `refs.detail`: every view and named part has a
  measurable, dense reference), and a humanoid's body against its survey table (`body.*`).
- **Rig:** bones, blended corners.
- **Texture:** seams, stretch, coat layers (fur) or skin type, eyes, nose, limb detail and brightness.
- **Motion:** the walk's duty and lift, standing balance and planted feet that don't slide (not for flyers), parts crossing
  in any frame of any clip (a blend-space variant clip judged on its own morph body), joints bent backwards, and the animal
  leg rules (not for humanoids).

## Still to do

- `ref_overlay.py` (the drawing overlay) should flip a reference that faces the other way, as `lp overlay` does.
- The renderers now shade as the stand-in viewer does (three.js, Lambert); neither is checked against the game's own
  lighting.
- `body_study.py` reads its torso from the bind pose's middle band, so wings or a mane inside that band, or a small torso
  between spread wings, distort the coat checks.

## Not done yet

- **Examples.** The case studies' build scripts (`examples/`) are not bundled yet.
- **Outfits and equipment for characters** (the body, face, hands, hair and joints are in `skills/lowpoly-characters/`):
  outfits on top of the body (layers just outside the skin, pieces that bend with the joints, swappable slots that fit one
  body, body parts hidden under a piece), attached weapons and shields with their grip poses, and a larger clip set. The
  folded bird wing of the agent trial is the same layering problem in miniature: clearance where a layer lies on the body,
  a closed seam where it joins it.
- **A humanoid race built from the base.** `skills/lowpoly-characters/references/races.md` gives the method and the
  anatomy each race borrows; none has been built yet, and some of its numbers are marked unverified.

## Tests

- **Red fox (2026-11-21):** built from the animal skill alone (before the core was split out), with no game reference.
  See `skills/lowpoly-animals/references/case-study-fox.md`. It passed the skill's checks. The gaps it found are folded into
  the skill: the scripts weren't bundled (they are now), the overlay's orientation, the stand-in renderer's brightness, painting texels
  from their 3D points, and where to find reference plates.
- **The agent trial (2026-11-21 to 22):** three builders (a Nile crocodile, a bald eagle, an emperor scorpion) worked from the
  plugin alone, with a reviewer and the person between rounds. `docs/agent-trial-findings.md` has the patterns and what was
  built from them (`lp preview`, `rig_parts.py`, `lp overlay`, `lp bake-springs`); `docs/agent-trial-log.md` has every
  friction point.
- **The bats (2026-11-22 to 23):** a docile flying fox and a hostile giant vampire bat, the first membrane wings and the
  first temperament pair (`skills/lowpoly-core/references/temperament.md`). They drove `mesh.loose`, `motion.crossings`, the claw, ear, jaw,
  glowing-eye and white-coat guidance, and the per-clip spring settings.
- **The housecat QA (2026-11-23):** the oldest build re-checked against the newer checks and guidance; it led to the
  reference checks (`refs.*`), the dense measuring tool and the preview's viewer-matched shading (two post-mortems).
- **The alicorn (shipped at round 13, 2026-11-23):** the first fantasy animal assembled from parts (a horse, a swan's wings,
  a horn, a mane). Its wing and flight lessons are `skills/lowpoly-animals/references/parts.md` ("Wing on a quadruped")
  and `references/locomotion.md` ("Flying on a winged quadruped"); its swap overlap drove `motion.pieces`.
- **The gorilla (hostile, 2026-11-23):** a knuckle-walker and a threat display; it shipped a docile eye from a sentence in
  its rules, which led to the `temperament/hostile` profile and the hostile-eye warning in `lp contract`.
- **The small-tier housecats (2026-11-23):** the flame point and blue point at about 280 triangles, now the standard for
  animals about a housecat's size (`scale/small-animal`), with boot-shaped paws.
- **The eagle's head (2026-11-23 to 24):** rebuilt from the user's concept images; feathers painted at about 0.03 detail,
  the beak as smooth horn kept clear of the feather strokes.
- **The Komodo dragon (hostile, 2026-11-23 to 24):** nine texture rounds, measured against two reference reptiles' bellies
  mapped onto their meshes. Its lessons are `skills/lowpoly-animals/references/reptile-skin.md`: plates in a surface grid
  (not domes), the head's beads on the back and feet, broad crossfades, colour matching by measurement, and the
  underbelly as soft rolls contoured to the muscle. The hostile mobs' jaws were opened about 30% wider at the same time,
  and the glow eye sized to the face (0.09 of the head's width on a short face, 0.12 on a long or broad one).
- **The dragon-prep builds (2026-11-24):** five builders, each with a focus study, after a full QA of the plugin (which fixed
  `limb_widths` reading a hip bone as the thigh, and led to `eye.size` leaving horns out of the height and noting a stale
  spec eye size). A greater kudu (horns), a green iguana (crest spines), Temminck's ground pangolin (overlapping armour and
  a curl), a mute swan (a long neck) and a hostile Kodiak bear (heavy legs and feet, the aggressive stance, rearing). Their
  lessons are the "Horns", "Crests, spines and frills", "Overlapping armour" and "Long necks" modules in
  `skills/lowpoly-animals/references/parts.md`, the heavy legs and plantigrade feet in `limbs.md` and `feet.md`, and the
  aggressive stance and rearing in `skills/lowpoly-core/references/temperament.md`.
- **The player character (2026-11-26 to 27):** a median man from a body survey, with thin and muscular morph targets,
  skin-tone and hair-colour options, and idle, run and attack clips, reviewed round by round in the character viewer. It
  is the `lowpoly-characters` skill's case study (`skills/lowpoly-characters/references/case-study-human-male.md`), and
  drove the character tier, the `humanoid` body plan, the body.* checks, `body_measure.py`, `character_view.py`, the
  helper bones where soft tissue meets, and judging variant clips on their own morph body.
