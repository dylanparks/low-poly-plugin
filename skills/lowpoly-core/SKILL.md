---
name: lowpoly-core
description: The shared method for building or critiquing any low-poly, game-ready 3D model (an animal, a creature, a character) in the style of late-90s/early-2000s RPGs. Use whenever a low-poly model is generated in code, built from photos or a description, textured, rigged, animated or reviewed, before any skill for one kind of model (load lowpoly-animals after it for animals). Covers the reference set and measuring the model against it in every view, budgets scaled to size and camera distance, one-skin topology (holes and bridges, rings at landmarks, winding, normals, bind pose), rigs and skin weights, the painted mirrored texture (continuity and seams, density, stretched faces, lighting judged as the engine shades it), docile against hostile temperament, secondary motion and parts crossing in motion, the lp check pipeline, and the failures that recur in every build.
---

# Low-poly game models: the shared method (late-90s RPG style)

The goal is a model that reads as the real thing at a glance from a 3/4 game camera, on a small budget. The detail goes
into the **silhouette, the joints and the painted texture**, not into round geometry.

This skill is the method every kind of model shares. A skill for one kind of model (`lowpoly-animals`) adds what is
particular to it: body plans, limbs, feet, heads, coats, gaits. Load this one first; its numbers and rules hold for both.

**What the numbers come from.** Budgets and construction facts are measured on the 22 shipped ambient animal models of a
late-1990s commercial RPG (**the measured models**), in depth on five quadruped mammals. Only the measurements are used; no
model, texture or file of that game is part of this skill. Where a rule rests on less than that, it says so.

**Reference files** (read the one for the step you are on):

| File | What it holds |
|---|---|
| `references/measuring.md` | turning the request into search subjects (colour words, fantasy parts), the overlay, `lp overlay`, using the reference set, filling gaps from the wider web, dead-on views measured densely, every view needing a reference, re-measuring after a change |
| `references/texture-method.md` | continuity and seams, the engine's lights, texel density, faces the projection stretches, limb detail on large models, pale surfaces painted as form |
| `references/temperament.md` | docile against hostile: what makes a model read as threatening (eyes, mouth, silhouette, motion) |
| `references/common-failures.md` | failures that are not about one kind of model, and the habits that catch them |
| `references/contracts.md` | style contracts: shared profiles (style, muzzle and eye kinds, species, colour), parts with budgets, `lp contract`, the parts.* checks |

Paths starting `lowpoly-animals/` are in the animal skill.

**Checks in code.** Every "check it" step says what to measure. The tools are in the plugin's `lib/lowpoly/tools/`, read
glTF 2.0 and print their usage. **Run `lp check <model.gltf> --spec spec.json`**: it runs them and judges every number
against `lib/lowpoly/targets.json`. A check passes when its report says so, not when it looks right. **Judge the look with
`lp preview`**: six fixed views, rear and top included, shaded as the viewer shades; its sheet goes in every report.

**Priority order.**
0. **The reference set, gathered first (§1).** The subject's skeleton and muscle, each in the side, front and top views,
   plus photos of its surface. Nothing else starts until it exists; if part of it is missing, ask the user. One reference is
   never enough, and published numbers are not a substitute.
1. **The skeleton and muscle,** read from that set: where each joint is, how long the bones are, how wide and deep the
   muscle makes each part. Every later choice rests on this, and it is never traded away for polygons.
2. Then the outline they give, in the side, front and top views.
3. Then how to build it, working back from the anatomy to the limits: budget, construction, topology, rig, texture. Spend
   polygons where the anatomy reads, simplify where it doesn't, and never move a joint or a mass to save a vertex.
4. Then motion, checked against reference frames of the subject.

Reference models (the measured ones or any others) tell you **how to build**, never **what the subject looks like or how
it moves**: study one in code for its construction (welded or separate, weighted how, mapped where), then apply that to the
subject's own anatomy, sized from your own reference. Copying a reference model's proportions or motion onto another subject
gives a clean model of the wrong thing; use the range across several of a group, not one example.

## What a model is for

Read this before anything else: every rule below follows from it, and a build that keeps the rules but misses this comes out
tidy and wrong.

> A model is **a silhouette that deforms**, read from a three-quarter game camera 10-20 m away, among dozens of others, and
> paid for in **rendered vertices and texels**. A triangle earns its place only if it (a) changes the outline from that
> camera, (b) lets a joint bend without collapsing, or (c) holds a texture feature the pelt cannot. Everything else is painted.

**Where this comes from.** The measured models were made for a 333 MHz machine with an 8 MB video card, in a world that
streams without loading screens, so every creature competed for memory and for per-vertex work every frame. Lighting was per
vertex, so form had to be painted. The artists built from a side drawing: trace the outline, give it half the width, build
**one half, mirror it and weld the centre**, pose it, lay it out as one side-view pelt, paint over photos. Those limits are
gone; the discipline is what makes the look, so the plugin keeps it. **The reference game's models are context for that
style** (how simple the polygons are, how a pelt maps), never a standard: every proportion, width, angle and limit the
plugin measures comes from the subject's own anatomy references (§1).

**The cost model.**
- **Rendered vertices, not triangles.** Every UV seam and hard edge duplicates a vertex for the renderer. One mirrored pelt
  (§5) keeps it near one per position by construction; a first mountain lion, cut into 43 texture charts, had 249 positions
  and 612 rendered vertices (2.46), and rebuilt on one pelt 1.06. `lp check` budget.corners warns past 1.3.
- **Triangles follow the outline and the joints, not the face.** Spend them where the species' anatomy makes the outline
  turn and where joints bend (§2). The first mountain lion put 32% of its triangles on a head of 8% of its surface, 7 times
  the body's density, and too few on the haunches, where the silhouette and the walk are; rebuilt from its references it
  read better at 3.8. budget.head_density warns past 4 (the plugin's own builds; teeth left out).
- **A thin triangle that buys outline is a good one.** mesh.slivers and texture.stretch are warnings to look at, never
  reasons to move a triangle off the silhouette the anatomy gives.
- **Paint what the camera cannot see round.** Toes, nostrils, the eye: painted at the medium tier and below; geometry for
  them belongs to a very large animal or a hero build whose head fills the camera (§2). **Teeth are the exception on a
  hostile mob:** its threat reads from the mouth, so it gets a modelled row at every tier (temperament.md, "Which to
  build"). A painted snarl on a medium-tier mountain lion read as a pink slit from the game camera (2026-11-26).

**The build order** (the stage gates below hold you to it):
1. The side outline from the references, then the widths: stations where the outline bends (§1, §3).
2. **One half,** mirrored and welded (`lib/lowpoly/build.py`), so both sides match by construction (§3).
3. Spend the tier's triangles by part (§2), then run `lp waste` and move what shapes nothing to where the outline is coarse.
4. Pose the bind pose off-centre, as the animal stands (§3, rule 7).
5. One mirrored pelt, one UV per vertex (§5). Then paint.

## Stage gates

A shape error found after the texture is painted costs a round of everything. The first mountain lion's legs 0.6 times too
thin, its dog-length muzzle and its bloated head were all found after its paint was finished. Pass each gate before starting
the next stage:

| Gate | Run | Must hold before going on |
|---|---|---|
| **1. Blockout** (untextured, no clips) | `lp check <model> --spec spec.json --stage mesh`, `lp waste <model>`, `lp preview` | the overlay within 5% in every view that has a reference; budget.corners, budget.head_density, mesh.mirror and mesh.sides clean; the wasted edges moved or justified; the six-view sheet reads as the animal |
| **2. Rig and motion** | `--stage rig`, `--stage motion` | joints at the skeleton's; every clip free of crossings; feet planted |
| **3. Texture** | `--stage texture` | seams, coat, eye and nose checks; colours judged in `lp preview` |

## The core idea in one paragraph

Gather the subject's skeleton and muscle in side, front and top views, and measure the joints, bone lengths and outline as
numbers. Build **one continuous skin** with **boxy cross-sections of very few sides**. Put vertex rings **only where the
outline changes**: joints, the widest point of each mass, and the head's landmarks. Pose it in a natural stance, rig one
bone per real joint, and blend weights across every joint so the skin stretches instead of the parts sliding. Then
**paint** everything the geometry can't show: lighting, the surface, muscle shading, markings, eyes that are crisp at the
centre and blend at the edge, as a single side-view "pelt" both sides share. Check every number in code and every view by
eye, under the engine's lights.

## 1. References first, then anatomy

Do this before any topology. A model that is clean to the vertex but has its joints in the wrong places or the wrong widths
is wrong, and no painting or polygons repair it. The 12 m test animal passed every topology check and still had its hip
joint a metre too far back, its head half a metre too high, its neck half as deep as it should be, its ribcage a quarter too
narrow and its tail twice as wide at the tip as the muscle makes it, because it was built from published numbers and a feel
for the animal, not from a full set of references.

**Step zero: the temperament, then the reference set.** If the request doesn't say whether the subject is docile or hostile
(a giant bat could be either), ask: it changes the species referenced, the eyes, the mouth and the silhouette
(`references/temperament.md`). Then translate the request into real subjects you can photograph, and record the translation:
a white unicorn is a grey horse (dark skin at the nose, lips and eyes) plus a narwhal's tusk (`references/measuring.md`, "Turning the
request into search subjects"). Then gather the set; nothing below starts without it. If any is missing, **ask the user**.
`lp check` refs.views and refs.parts warn on a view or special part with no measurable reference (fail with "hero").

| What | In which views | What it gives |
|---|---|---|
| **Skeleton** | Side, front (or rear) and top, plus the special parts: the skull, a foot, a hand or wing | The joints, the bone lengths, the stance and the widths of the skull, ribcage, pelvis and tail |
| **Muscle** and the outline over the skeleton | The same views: an anatomy plate, a muscle reconstruction, or life art with the skeleton showing through | How deep and how wide the muscle makes each part. Where the outline stands far from the bones, muscle fills it |
| **The outside** | Photos or art of the subject in several poses, and close-ups of each surface region | The surface, colours, markings, the head and the extremities |
| **Motion** | Footage or a frame sheet | The animation (§6) |

Where to look: public-domain anatomy plates drawn for artists (on Wikimedia Commons) cover many subjects in side and front
views, skeleton and muscle together. A plate of a close relative stands in when the subject has none: say so, and let the
subject's own photos decide the outline. Check each licence, ask before downloading, and fill any gap from the wider web as a
measure-only reference (`references/measuring.md`, "Filling gaps"); a preview-sized copy is enough to measure. Prefer a
dead-on view measured densely (`silhouette_measure.py`) to many oblique ones (`references/measuring.md`, "Quality over
quantity").

How to use the set (details in `references/measuring.md`): each view answers different questions (the side lengths and
depths, the top widths, the front the stance and ratios); one drawing is one example, so use two sources and write down
where they disagree; take metric widths from the top view, as front views are in perspective; record each source; and if a
view cannot be found, say so and mark what rests on it as unverified.

**Start from the skeleton.**
1. **Read off the landmarks, as a table:** the joints (skull-neck, jaw hinge, shoulder, elbow, hip, knee, ankle, tail base,
   ground contact), the bone lengths, the widths (top view; stance and foot width from the front) and the muscle outline: a
   top line and an underline (side), a half-width (top) along the body.
2. **Give every measurement as a fraction of a body length,** so scale and the reference's pose don't matter.
3. **If the reference's pose differs from your bind pose,** use only what doesn't change (skull, pelvis, ribcage, shoulder,
   the torso's outline, the bone lengths) and rebuild the limb angles from the bone lengths and the subject's posture.
4. **Look for what the muscle hides.** A bone inside the outline does not mean its muscle is: the T. rex's femur sits inside
   the torso, but the thigh's muscles make a lobe of their own that hangs below the belly to the knee.
5. **Put the model's bones where the skeleton's joints are.** The rig is the skeleton: a hip bone 1 m from the real hip
   swings the wrong mass.

**Measure the model against the set in code, not by eye:** mark each reference's landmarks and outlines once (`refs.json`),
run `lp overlay`, fix everything over ~5% and quote the table ("lines up closely" is not a result). **After any big change
to the model or a part** (a rebuild, new proportions, a new fold or shape): gather that part's references in every view
(side, front, top, rear), overlay it in each, and look at it from every angle before reporting. A shape is fixed from a
measurement, never from a description of one (`references/common-failures.md`).

## 2. Budget: scale it to the size and importance

Budgets of the measured models:

| Size | Unique vertices | Triangles | Bones | Texture |
|---|---|---|---|---|
| Large: cow, bear, horse or mule | 219–227 | 436–450 | 26–33 | 256 × 256 or 256 × 128 |
| Medium: dog, pig, deer | 171–227 | 338–450 | 26–39 | 256 × 128 |
| Small: chicken, gecko, crab | 90–146 | 125–288 | 18–39 | 128 × 128 or 128 × 64 |
| Tiny or background: rat, raven, seagull | 35–54 | 68–104 | 6–9 | 64 × 64 to 256 × 128 |
| Swarm or ambient: fish, bird, bat, butterfly, spider | 15–25 | 8–46 | 3–12 | 32 × 32 to 128 × 64 |

- **Pick a tier** for the size and how close the camera gets, and say which. Up to about 3.5 m a hero may go one tier up (at
  most about 250 vertices, 480 triangles); past that, `lp check`'s very-large tier: 300–450 vertices, 500–720 triangles.
- **The small-animal standard** (approved on a housecat, 2026-11-23): an animal about a housecat's size (a body up to about
  0.5 m) is built to the small tier by default: about 140 vertices, 280 triangles and a 256 x 128 texture (128 x 128 lost
  the face's detail), the head about a third of the triangles, the bones the motion needs. Add `scale/small-animal` to the
  contract's profiles; a medium build of such an animal is the exception and says why.
- **Detail scales with size on screen, in polygons as well as pixels.** The simple forms that suit a 0.4 m cat (a mouth
  painted as a line, a smooth brow) look painted on a 12 m animal whose head the camera fills. For a very large model:
  - raise the budget for the parts the player sees close up (the head, the mouth, the claws) and keep the body simple;
  - build as geometry what the camera can see into or around (a mouth, an eye socket, a brow);
  - use a bigger texture, 1024 × 512, give the head its own denser stretch of the pelt, and paint the limbs as fully as the
    body (`references/texture-method.md`, "Detail on the limbs").
- **Head share:** in the medium and large tiers the head takes the most vertices, about 20–30%, not counting teeth and a
  mouth's interior. After the head comes the torso's silhouette, then the joints. Straight shafts get almost nothing.
- **Blended vertices** (on two or more bones): the measured mammals blend 48–76% of corners; rigid-part models (birds, tiny
  animals) 0–33%; bodies that bend along their length more (the fish 56%).

## 3. Topology

0. **Build one half.** Define the left half only (x >= 0), then mirror and weld: `lib/lowpoly/build.py` (`Half`,
   `mirror_and_weld`, `fix_winding`, `pelt_uv`, `pose_x`, `to_model`). Both sides then match in vertices, triangles,
   winding and texels by construction; a builder that makes each side separately drifts (an ear at another angle, teeth
   inside out, three times in one animal). `lp check` mesh.mirror and mesh.sides read it back from the model.
1. **One continuous skin.** Limbs, neck, head and tail grow out of the torso by sharing its vertices.
   - **Never** place capped tubes or capsules against the body.
   - **Never** bury a separate limb tube inside the body: it looks attached when still, and slides through in motion.
   - **Thin parts grow from their joint** (a finger, a thumb, a claw): a piece built beside the joint floats in motion.
     `lp check` mesh.loose counts loose pieces and their gaps.
2. **Holes and bridges.** A limb's top *is* a hole cut in the body (remove the quads where it leaves; their vertices are the
   limb's first ring), bridged to the next limb ring, so the skin round it is shared and stretches when it swings. The animal
   skill has the measured joins (`lowpoly-animals` §3).
3. **Few sides, boxy shapes, rings at landmarks.** Rings go where the outline changes, never at even spacing: torso 6–8
   sides, neck 5–6, limbs 3–4 (deeper front-to-back than side-to-side), rings only at the joints and at the fullest point of
   each muscle mass. Thin parts (fins, membranes, crests) are flat two-sided cards on their own bone, declared in the spec
   (`"cards"`).
4. **Bridge rings with different vertex counts.** Walk both rings in angle order round their shared axis and emit a triangle
   each time one of them advances. Every part must be bridged: a cap plus a separate tube leaves a gap from every angle.
5. **Wind every triangle consistently outward.** Flip across shared edges until each piece is consistent, then make it
   outward by signed volume. The skin is closed: every edge has two triangles, except declared cards.
6. **Smooth normals across the whole skin.** Low poly plus smooth shading gives the soft look. Hard edges only on hooves,
   horns, beaks and shells.
7. **Bind pose = the subject's natural stance, not a T-pose:** joints angled as in the reference, feet flat on the ground,
   the head at its natural height. **Pose it after mirroring** (`build.pose_x`), as the species' own standing photos show
   it (a puma often mid-stride, one forefoot ahead). Symmetry belongs to the construction, not the stance.

**Clean triangles.** No triangle with an aspect over about 10 (the longest edge squared over twice the area): weld vertices
a few millimetres apart, flip the diagonals of nearly flat quads (`lib/lowpoly/mesh_tidy.py`). **Mirrored pairs alike:**
both sides have the same triangles, mirrored, for every pair and the skin round their joins, checked after every topology
change; angle-sorted stitches differ side to side, and the unlike side samples the pelt smeared. Mirror the better side over.

## 4. Rig and skin weights

- **One bone per real joint,** at the skeleton's joint: a spine of root, pelvis and 2–5 spine bones; a chain per limb; the
  neck, the head, a jaw if the mouth opens, ears that move; 2–4 tail bones. Each foot gets its own bone so its sole can stay
  flat. The lists per body plan are in the animal skill.
- **Joint rings:** split about 50/50 between the two bones that meet there. Rings mid-segment are 100% one bone. Torso rings
  blend along the spine; neck rings between the neck bones and the head.
- **Where a limb meets the body,** the skin round the hole blends body and limb so it stretches (a working start: the
  shared groin vertex 50/50 to the two limbs, the lower flank body 0.4 / limb 0.6, the upper flank 0.75 / 0.25).
- **Rest rotations:** identity is fine; a bone's animation key is then simply its bend.
- **Check it:** `lp check` rig.* (bones, blended share), and every clip for parts crossing (§6).

## 5. Texture: a painted, mirrored pelt

The texture does most of the work.
- **Name the surface types, region by region,** before painting: each is painted and measured differently (fur, scales,
  plates, wet skin, chitin, membranes for animals: `lowpoly-animals/references/skin-types.md`).
- **Layout:** paint **one side** as a flattened side view, a "pelt", that both sides share (a planar side projection: `u`
  along the body, `v` = height, `x` ignored). **One UV per vertex is the target** (`build.pelt_uv`; budget.corners): every
  extra chart duplicates rendered vertices along its seam, so a patch must earn its place as a triangle does. With a mirrored pelt, add a vertex on the spine so the back can be unrolled.
  - **Overlapping parts** in the side view (legs, ears, wings over the back) get their own strip, or they take the colour of
    what they overlap.
  - **Own patches:** forward-facing faces, eyes on a long or large head, a mouth's interior and teeth, feet, and any group
    the side projection stretches over 4:1, painted from the pelt unrolled round its edge (`references/texture-method.md`,
    "Faces the projection stretches").
- **Density and paint time:** give the head more texels than the body (the break exactly on a ring), and paint only the
  pixels a triangle uses (`references/texture-method.md`, "Texel density").
- **Paint the lighting in,** lit from above: lighter along the back and the top of the head; darker under the belly, inside
  the limbs, behind the elbow and thigh, under the jaw; soft occlusion where the limbs meet the body.
- **Paint the form, not noise.** The masses outlined, the joints as crease-and-rim pairs, strokes that follow a flow over the
  body. A pale surface is painted as the shadow sides of its forms, never as a flat value with grain
  (`references/texture-method.md`, "White and pale coats").
- **Continuity: no hard line anywhere.** Cross-faded painters, patches that match the pelt at their seams (painting every
  texel from its 3D point does this by construction), the back unrolled. **The check:** seam jumps, median at or below about
  0.10, worst 10% at or below about 0.25 (`references/texture-method.md`, "Continuity").
- **Judge colours as the engine shades them,** in `lp preview` or `lit_view.py` (sRGB to linear, Lambert, the viewer's
  hemisphere and sun), then confirm in the real viewer with fresh files. A preview lit too brightly once had a coat darkened
  until it was muddy (`references/common-failures.md`).

## 6. Motion: checks every clip needs

The gaits and clip sets of animals are in `lowpoly-animals` §7. These hold for any model:
- **Compare against frame-by-frame reference,** then check in code: render the clip at the footage's phases as silhouettes
  (`walk_sheet.py`) and compare contact, the limbs' outlines, how the joints fold and the head's carriage. Numbers in range
  don't prove the shapes are right.
- **Standing: the centre of mass over the support.** In every standing clip the centre of mass, from the skin's volume,
  falls inside the ground contact, near its middle (`lp check` motion.balance; not for flyers). **The planted feet stay put:**
  a bone that breathes or sways (the chest, the hips) drags the legs hung from it, so those legs turn back by the same amount
  (`lp check` motion.planted).
- **Joints bend as the anatomy does and the skin keeps its width.** No hinge (a knee, an elbow, a hock) bends backwards in
  any frame; no blended joint ring folds so far that it pinches, no short band of skin behind a joint stretches; in an action
  clip the paired limbs move each on their own (`lp check` motion.hyperextended, motion.leg_rings, motion.leg_stretch_*,
  motion.lockstep; `leg_bend_study.py`; `lowpoly-animals/references/limbs.md`, "Legs that bend").
- **Nothing passes through itself or the body** in any frame of any clip (`self_cross.py`, `lp check` motion.crossings;
  `--where` names the bones).
- **Secondary motion** (tails, ears, hair, feathers, a mane) as baked spring bones: `lp bake-springs`, with stiffness, drag,
  gravity, colliders, the ground and settings per clip (`lowpoly-animals/references/locomotion.md`).
- **Idle and hover clips need variance:** a few overlapping cycles of different lengths, not one nod repeated.

## 7. Checklist (before calling it done)

`lp check` runs the measurable items; the report goes with the preview sheet in every review.
- [ ] The three stage gates passed in order; built as one half and mirrored; rendered vertices within 1.3 of positions; the
  head no more than 4 times the body's triangle density; `lp waste` run and its edges moved or justified.
- [ ] A contract written before the build (profiles from the reference translation, parts with budgets), every part briefed
  from `lp contract`, and the parts.* checks clean at every merge (`references/contracts.md`).
- [ ] The temperament was settled and the reference set gathered **first**, in every view, each dead-on view measured
      densely; anything missing was asked for or its absence stated; sources, scales and poses recorded (§1).
- [ ] The joints, bone lengths and widths are in a table, and the rig's bones sit at those joints.
- [ ] `lp overlay` against every view: nothing over ~5%, the table quoted; after every big change, re-measured in every view.
- [ ] A budget tier chosen and met, or a very large model spending the extra where the camera looks (§2).
- [ ] One closed, consistently wound skin; cards only where declared; holes and bridges, no caps, capsules or buried tubes;
      thin parts grown from their joints; no loose pieces (§3).
- [ ] Rings only at joints and outline changes; no sliver over aspect 10; mirrored pairs alike on both sides (§3).
- [ ] Joint rings blended 50/50, the limb joins blended, blended corners in range for the size (§4).
- [ ] Surface types named per region; a mirrored pelt with painted light and form; own patches for stretched faces; seams
      in range; colours judged under the engine's lights and confirmed in the viewer (§5).
- [ ] Every clip checked for crossings; standing clips balanced; motion compared with reference frames (§6).
- [ ] No joint bent backwards, no joint ring pinched or band of skin stretched, paired limbs independent in action clips (§6).
- [ ] Seen at game distance from a 3/4 angle, the subject is obvious without labels.

## Common failures

`references/common-failures.md` has the failures that recur in any build, what each looks like and the fix, with the habits
that catch them: read it when a build looks wrong, and run its habits before every review. The animal skill has its own.
