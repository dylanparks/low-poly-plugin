# Case study: a Siamese flame point housecat, built and rebuilt with this skill

This is how the skill was tested. Each round fixed a real problem, and each problem became a general rule in
`SKILL.md`. The cat is a digitigrade predator with forward-facing eyes, about 0.38 m tall to the ear tips and
0.42 m in body length (L), so it sits between the measured "small" and "medium" budget tiers.

## v1: capsules (before the skill)

The cat was built from 10-sided tubes, a capsule body and a sphere head, at 555 vertices. It read as a toy. This led
to the topology and budget rules (§3, lowpoly-core §2) and the anti-patterns.

## v2: following the skill's first version

| Problem | What fixed it | Rule |
|---|---|---|
| Fur noise ran across the body | Low frequency along the hair, high frequency across it | §6 |
| Ears took the skull's colour; orange stripes on the head | Ears got their own UV strip; paint boundaries kept 6 mm off the skull line | §6 |
| Only 18% of vertices in the head | Brow, below-the-eye and nose rings added (30% now) | lowpoly-core §2 |
| A prey head: eyes on the sides, built after the deer | Head rebuilt with forward-facing eyes: widest at the eyes, a flat face plane, a short muzzle, both eyes painted head-on in a face patch | §5 |
| An "eyebrow lump" in profile: the head's peak at the brow, 59% along the head, with a sunken face below it | Crown made the peak (33%); brow, eye and face ring tops lowered onto one convex slope, bottoms unchanged | §5 |
| Body proportions borrowed from the deer and dog | See below | lowpoly-core §1 |

**Proportions, against two housecat photos.** The model's side projection, laid over the photos, showed five problems:
- **Back:** it sagged toward the rump. The photos show the rump level with the shoulders or higher.
- **Chest:** too shallow, 0.37 L deep against 0.40–0.50 L.
- **Hind paws:** 0.25 L ahead of the rump; the photos show 0.14 L.
- **Front view:** the legs stood wider than the body.
- **Tail:** a separate tube starting 1 cm behind a capped rump, at mid-rump height. It now starts at the top of the
  rump, bridged to the body.

The traced numbers are in `proportions.md`.

## v3: legs as body skin, flat feet, IK walk

v2's legs were tubes buried inside the body: 0 triangles joined body skin to leg skin.

**Problems found:**
- **Separate legs:** the walk looked like four sticks pivoting inside a barrel.
- **Feet:** a hind "sole" was a single point 1.2 cm under the ground, and the front paws were tilted.
- **Walk:** it was sine waves on each joint, flexing them about 20° and lifting the feet 6% of the height.

**Fixes:**
- **Legs from holes:** legs grow out of holes in the body's underside. That gave 52 joint triangles (the deer has 54),
  with the groin and brisket shared and the flanks weighted to the legs.
- **Paws:** each has a flat 5-vertex sole at y = 0 and its own bone.
- **One clean skin:** the whole skin is consistently wound and closed, so shared vertices shade smoothly.
- **Walk:** planted paws with 2-bone IK.

## v3, second round: the walk was the deer's

The walk had been tuned to the deer, the only animal measured by then. The cat high-stepped:
- the feet lifted 11–16% of the height;
- the front paw flipped back 85°;
- the stride was only 22% of the height;
- the paws were long and narrow like hooves.

**What fixed it:** measuring the dog, bear, cow and pig too, and using their range.

| Measure | Now |
|---|---|
| Lift | 6% |
| Wrist fold | 74° |
| Stride | about 0.85 leg lengths |
| Share of the cycle a foot is down | 0.75–0.81 |
| Paws | round, about 0.16 × 0.17 of leg length |
| Shoulder blade | slides with the reaching foreleg |

**Eyes:** hard-edged almond eyes with near-black rims looked like decals. Graded colours, a dusky surround, a soft
pupil and two 3 × 3 blur passes over the face patch fixed it.

## v3, third round: compared with a 12-frame cat walk sheet

Every number was now inside the group's range, but a side-silhouette sheet of the walk, set beside a reference cat walk
cycle, showed the hind legs were still wrong:

| Seen on the sheet | Fix |
|---|---|
| The thigh was a stick under an overhanging rump | The ring at knee level spans from the kneecap to the hamstring (10 cm deep on a 19 cm leg), so the back of the thigh continues the rump down to the hock |
| The push-off was short and the lower leg stayed vertical | Hind stance centred 1.2 cm further back, heel lift 0.95 rad at toe-off, the metatarsus following 85% |
| The swing was flat | It folds into a Z: knee forward, hock bent, paw tucked |
| A low flank hid the thigh | The flank is tucked up in front of the thigh |
| The head was carried at standing height | The neck drops about 16° while walking |
| Planted paws sank up to 8 mm | The body's bob is now included in the IK |

## v3, fourth round: feet, ears and the face against the measured models' detail

**Feet:** the paws were plain gradients of the leg colour.
- **Fix:** each paw now has its own wrap-around texture patch (warped so the toes get two-thirds of the width), with
  four lit toes and three dark gaps, like the measured dog.
- **Result:** brightness spread 0.04 → 0.13.

**Ears:** they were flat two-triangle cards, open-edged and not joined to the skull. Every measured ear is closed into the
head skin.
- **Fix:** each ear now grows out of a 6-vertex hole cut in the back-top corner of the skull, bridged to a 3-vertex
  ring and a tip. That makes a closed, slightly cupped pyramid with 8 shared base vertices and 12 triangles, its base on
  the head bone and its tip on the ear bone.
- **Skull:** squared off at the back so the ears have corners to grow from (upper-flank vertices raised, a wider flat
  top).
- **Texture:** the front has its own patch, a pink opening with a dark hollow at the base and pale tufts inside a flame
  rim. The back is flame fur.

**Face:** the brightness range was 0.17–0.94, with no darks. It now has:
- dark pupils and nostrils;
- a warm, darker eye socket;
- a darker chin;
- light down the nose bridge;
- hair strokes radiating from the nose;
- the side mask as one soft shape.

The range is now 0.09–0.95. The first attempt at the socket was too strong and read as a grey smudge round the eyes,
so it was warmed and lightened.

## v3, fifth round: ear openings and seamless texture

**The ear opening looked too long.** It was a narrow slit up to 92% of the ear's height. Front-on and side photos of
real cats show a broad triangular opening in the lower ~65% with fur at the tip and edges, and the recess low inside.
The opening was repainted to match, and the ear was given a wider middle ring.

**Seams and staircases on the cat and the anteater** (the second test animal). These showed on the model:
- a stepped line at the cat's chest and leg;
- a hard edge at the anteater's tail root.

`lib/lowpoly/tools/uv_study.py` found three causes, given in lowpoly-core's §5 and `lowpoly-core/references/texture-method.md`, "Continuity". Fixing them brought the seam jumps from a
median of 0.15–0.19 to 0.02–0.04, with the worst 10% at 0.08–0.09 (the measured models: 0.07–0.10 and 0.16–0.26):
- the painters became cross-faded parts;
- the patches fade to the pelt at their seams;
- the ear base ring was mapped to its patch's edge row.

**The back, unrolled.** The remaining stretch was the ridge strip along the spine, squashed into one pixel row. Each
torso and head ring got a spine vertex, mapped above the silhouette in the texture. The results:
- up- and down-facing faces stretched more than 4:1 went from 31% to 3% (cat) and from 35% to 5% (anteater);
- the density spread went from ×12–15 to ×2.2–2.6;
- the cost was 17 vertices (cat, 238 in all) and 14 (anteater, 210).

**The thigh-belly notch.** From a low rear angle the cat showed a deep angular cut where the hind leg met the belly. The
cause was the leg's knee ring, whose front sat 3.7 cm ahead of the front edge of the hole the thigh grew from, so the
thigh folded back under the belly. Anatomy sources describe the flank fold running from the abdomen to the stifle.
Renders of the measured dog, deer and bear show the belly flowing into the thigh's front. The hole was extended over three
rings, rump to waist, with the waist weighted lightly to the thighs: the notch is gone, the skin stays closed, and the
walk is unchanged. The anteater had the same notch and got the same fix.

## v3, sixth round: eyes bleeding onto the snout

**The problem:** the eye texture showed on the cat's snout.

**The cause:** the face patch was one front projection over every forward-facing triangle. The whisker-pad and muzzle
rings were as wide and as tall as the face plane, so their upper sides sat at the eyes' own (x, y) and took the eye
texels. Textured renders of the measured dog and bear show the opposite layout: eyes on brow-level faces behind and above a
narrower muzzle block, which is painted separately (lighter, with a mouth line and a dark nose).

**The fix:**
- **Geometry:** the whisker-pad and muzzle rings got a muzzle-block shape: broad, low whisker pads and a narrow nose
  bridge rising between the eyes. In the front view the muzzle now passes below and between the eyes.
- **Texture:** the triangles wholly on the muzzle rings got their own eyeless head-on patch, at the face patch's
  density. They are picked by ring, since a z threshold misfiled them all: the tilted head rings spread over several mm.
- **Fade:** both patches fade to the side pelt at the depth of their edge. Beside the whisker pads that is the flame
  mask, not the cream of the face plane.

**The result:**
- Each eye shows once.
- The skin stays closed, with the same 238 vertices.
- The seam jumps are median 0.040 and worst 10% 0.087, still below the measured models'.

## Not done: a skeleton check

The cat (and the anteater) were built before the skill's rule that the skeleton comes first. Their proportions were traced from
side photos and checked against the measured measurements, but no skeleton reference was laid over them, so their hip joints, the
depth of their necks and the position of their feet were never measured against the bones. The T. rex found errors of this kind
that every other check missed (`case-study-trex.md`), so this check is the next one to run on them.

## Final numbers

| Measure | Cat v3 |
|---|---|
| Unique vertices / triangles | 238 / 472 |
| Bones | 26 |
| Head share | 31% |
| Corners on 2+ bones | 58% |
| Seam colour jump, median / worst 10% | 0.040 / 0.087 |
| Up- and down-facing faces stretched more than 4:1 | 4% |
| Soles | 5 vertices each at y = 0, flat in every standing frame |
| Walk | 0.9 s cycle, lateral sequence (LH, LF, RH, RF), lift 5–6% of height |

## A later round: paw shape

A foot study of the game's monster models and ambient dog and bear (`lib/lowpoly/tools/foot_study.py`) found this build's paws upright
boxes:
- splay 1.1-1.2 and reach 0.1-0.5;
- the measured paws are sloping, splayed wedges: splay 1.6-2.7, reach 0.8-1.6.

**Rebuilt:**
- **The paw:** a knuckle ring set forward and lower than the heel over a 7-point sole, larger (front 0.054 m long, hind
  0.056 m).
- **Result:** footprint 0.12-0.17 x 0.09-0.10 of the height, reach 0.8-0.9, 8 ground contacts.
- **The walk:** the roll pivots on the new toe tips.

## A later round: refined against the later texture guidance

Audited with the measuring tools against the guidance added after this build (the eye stack, the snout, the coat's
layers), then repainted where it failed.

| Check | Before | After | Target |
|---|---|---|---|
| Coat: strokes | one noise along the body: coherence 0.90 overall and locally, fine detail 0.020 | a flow field (along the back, down and back over the shoulder, back along the neck, down the chest and legs, bending round behind the haunch): coherence 0.37 overall, 0.49 locally; fine detail 0.036 | 0.06-0.28 / 0.24-0.33; 0.013-0.049 |
| Coat: form | 0.014, darkest and lightest areas ±0.022 | 0.030, ±0.048: the shoulder blade, the elbow's crease and point, the ribs' lower edge, the flank fold, the haunch, the knee, the hock, the wrist, neck folds, placed from this cat's own bones | 0.014-0.034, ±0.023-0.050 |
| Eye | blurred: no catchlight (brightest 0.19), no drawn rim | the stack: a catchlight 0.93-0.98, a near-black slit pupil, a drawn lid line, a socket darker under the brow, a pocket at the inner corner; no blur on the face | §6, eyes |
| Nose | a flat pink cap | a lit top band and a lit rim over each nostril; the nostrils darker | §6, noses |

**Lessons from this round:**
- **Strength depends on the coat's value.** On a pale coat the same shade change measures stronger: the fox's form
  strength gave this cream coat 0.046. It was scaled down to 0.75 of the fox's.
- **Stroke length counts in proportion to the animal's length.** Strokes 1.4 cm long are 3% of this cat's length, so they
  landed in the form layer's sizes. They were made 7 mm long.
- **Blur differences between patches show at their edges.** Removing the blur from the face patch alone made its edge with
  the still-blurred muzzle patch jump; both are now unblurred.
- **The muzzle patch must not get the eye's socket.** Painting the socket there to match the face patch put it on the
  muzzle's upper sides, which sit at the eyes' own front-view position. That is the reason the muzzle is painted with the
  eyes off, and the jump rose to 0.60. The face patch's socket instead fades out above the muzzle's ring.

**Seams:** 0.052 median and 0.166 worst 10%, inside the limits (0.039 and 0.125 before the round). A few short edges on the
face patch's border jump 0.3-0.4 at their ends (0.26 before, hidden by the blur), while their middles match.

## The lid line, corrected

The reviewer found the refined eye's border too thick and too dark next to the game's werewolf, whose dark lids blend into
the fur. Profiles across the measured lids showed the lid is a deeper shade of the coat, not black:
- 6-63% darker than the fur;
- densest at the eye's edge and back to the fur within 1-3 texels;
- the upper lid usually stronger than the lower.

This cat's lid had been a near-black ring of one strength all round, crisp on both sides.

**Repainted:** a deeper shade of the surrounding paint, crisp only where it meets the eye and fading outward, about 50%
darker along the upper lid and 30% along the lower. The inner-corner pocket became a soft-edged deeper shade too.

**Measured across the iris side after:**
- upper lid 0.30 against fur at 0.80 (the socket's shade included);
- lower lid 0.35 against 0.60;
- back to the fur over about 5 texels at this face patch's density, roughly a fifth of the measured models' texel size.

The fox's black liner, which is real, and the T. rex's lid were softened the same way. Seams were unchanged on all three.

## A later round: the paws' splay, and the walk's IK

**Splay:** `lp check` failed the front paws' splay at 1.3, against 1.6-2.7 measured (the sole's width at the ground over the
width at the wrist). The sole's half-width went from 1.8 to 2.5 cm on the front paws, and from 1.9 to 2.5 cm on the hind.
- **Result:** the splay is now 1.9.
- **Unchanged:** reach (0.8), contacts (8) and the sole at y = 0.
- **The look:** in the viewer the paws splay at the ground without looking oversized, about 1.4 times life size.

**The hind paws** still give no splay ratio. Their tops are only 1.6 cm high, so the foot study's slice at the top of the
foot zone catches almost nothing, and `lp check` leaves the ratio out and says so. That is a limit of the measurement, not a
fault in the paws.

**The walk:** the fox's IK bug (the upper bone's length taken from the moved shoulder) was in this build too.
- **The fix:** the bone lengths now come from the rest pose.
- **After it:** the front paw sits at 0.0 cm through the stance; the lowest foot is down 0.75 of the cycle (was 0.79); the
  swing lifts 4.6% of the height (was 3.8%).

## A later round: clearing the remaining warnings

`lp check` warned on five things:

| Warning | Before | After | Cause and fix |
|---|---|---|---|
| Triangles | 496 (budget 480) | 474 | 12 from the tidy pass (welding vertex pairs 3-6 mm apart at the nose, eyes and brow: the weld limit is 6.5 mm on this 8 cm head), and 8 from dropping a tail ring that sat 6 mm off the straight line between its neighbours |
| Slivers | 21.0 | 7.8 | Near-duplicate vertices in the face (welded; a vertex on the midline stays there, so the face stays mirrored), one ear stitched differently from the other (mirrored), and one vertex almost on the line between two others at the nose (collapsed into its neighbour) |
| Stroke coherence, overall / locally | 0.37 / 0.49 | 0.13 / 0.27 | Angle wander ±55 degrees, strokes 2 times longer than wide (was 3), 25% direction-free breakup |
| Eye rim spread | 0.23 | 0.21 | The catchlight's edge reached into the rim band. It moved a little toward the eye's centre, and the lid is a little lighter (about 45% darker than the fur at the upper lid, 25% at the lower) |
| Form band's darks and lights | (0.051 after the stroke change) | 0.044 | The looser strokes put more contrast in that band; the strokes' strength went from 0.20 to 0.17 and the form lines from 0.75 to 0.62 |

The nose's lit bridge, which the welds had brought to 0.02, was lifted back to 0.03. Seams are 0.043 / 0.164. The cat now
passes every check with no warnings.

## The small tier: the standard for animals this size (2026-11-23)

The flame point was rebuilt at the small tier as a separate viewer entry to compare: 141 vertices, 278 triangles, 26 bones
and a 256 x 128 texture, against the medium build's 242, 480, 26 and 512 x 256 (the reference game's chicken: 146, 288, 18,
128 x 128). The body went to 6-sided rings (7 instead of 11), the legs to 3-sided rings, the head to 8 points a ring with
every landmark kept, the ears to cupped pyramids. 128 x 128 was tried and lost the nose detail, the eye sockets and the
nostrils. The user judged it great and made it the standard for animals of this size: the `scale/small-animal` profile
(lowpoly-core SKILL.md §2).

## The fork: a blue point on the show body, a flame point rebuilt (2026-11-23)

The user's flame point turned out to be a sturdier traditional colourpoint, not the modern show Siamese the build had
followed. The build was forked:
- **The blue point** kept the show-type mesh and recoloured the finished texture by hue. "Blue" first came out
  blue-tinted; three reference photos showed an off-white body (saturation 0.03-0.10) and nearly neutral slate points at
  about half its value, and the recolour was corrected.
- **The flame point** was rebuilt from the user's photos, then from a hard side reference the user generated and cleared
  for tracing (body and legs within 5% of it), then from the user's red-line markups of the head, neck and face.
- **Its head drifted into a reptile** over five rounds of reshaping, each passing its checks. A builder without that
  history rebuilt it from the references in one round (`heads.md`, "A cat's head"); the rejected renders were kept as
  counter-examples. The rebuilt head's painter had dropped the hair strokes radiating from the nose, which made the face
  read as cartoonish until they were restored (`lp check` nose.detail now catches it).
- **Smaller lessons:** a standing cat holds its head over the forechest and lowers it to walk; a breathing chest drags
  the forelegs unless they turn back against it (motion.planted); the neck pinches in behind the skull from above; the
  user's markup outranks every photo (`lowpoly-core/references/measuring.md`, "When references disagree").
