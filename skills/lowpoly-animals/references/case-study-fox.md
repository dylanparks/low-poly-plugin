# Case study: a red fox, built from this skill alone

A test of the skill itself: a red fox (*Vulpes vulpes*, 0.9 m from nose to tail tip) built from `SKILL.md` and its
references only, with no model or file from any game. It passed the skill's checks on the first full build. What it
found missing was folded back into the skill.

## The reference set (lowpoly-core §1)

| What | Source | Used for |
|---|---|---|
| Skeleton, side | A public-domain artist's anatomy plate of a **dog** (Ellenberger and Baum), standing | Joint positions as fractions of L, scaled to the fox's height |
| Skeleton and muscle, front | The same plates' front view (drawn in perspective) | The stance, the ribcage against the shoulders, the head against the body: ratios only |
| Skull and head muscle | The same plates' head plate | Muzzle length, the orbit, the jaw hinge |
| Photos, side | Two public-domain fox photos: standing (head lowered) and walking | The outline, the tail's carriage, the walk |
| Photo, face | A public-domain head-on fox photo | Eye spacing, ear size, the white cheeks |
| **Missing** | A top view of a fox or dog, and a side-view body muscle plate | Stated in the build script; every width is marked unverified |

No fox skeleton plate could be found, so a dog's stands in for it. The fox's own photos decide the outline.
Two files the user approved turned out not to be side views (a head close-up), so two more were asked for.

**Proportions written down** (L = chest front to rump = 0.50 m):

| Measure | Value |
|---|---|
| Height at the withers | 0.80 L |
| Chest depth | 0.44 L |
| Legs below the chest | 0.38 L |
| Head | 0.30 L long |
| Muzzle | 48% of the head |
| Tail | 0.86 L long, slanting back about 45°, a brush about 0.24 L thick |

## The build

| | Value |
|---|---|
| Vertices, triangles, bones | 230, 456, 26 (medium tier, slightly over, within "one tier up") |
| Head share | 28% |
| Blended vertices | 59% |
| Skin | closed: every edge on exactly two triangles |
| Construction | 8-sided torso and head rings (the spine vertex unrolls the back); legs grown from holes, the hind hole over three rings; ears closed into the skull's back corners; a 4-sided brush bridged to the tail-root ring; paws with flat soles at y = 0 on their own bones |
| Texture | 512 × 256: a two-density side pelt (body, then head); patches for the tail, the eyes (oblique, 35° off the front), the nose (head-on), the ear fronts and backs, the front and hind paws |

**Every texel was painted from the 3D point it maps to.** Each UV triangle was rasterised, its corners' 3D positions
interpolated per texel, and each texel painted by its 3D point and patch, every patch starting from the same pelt colour.
Seams came out at 0.010 median and 0.027 worst 10% (the skill asks for 0.10 and 0.25), with no fade tuned by hand.
The first build was 0.33 worst 10%, from two painted features that stopped at a patch edge: the nose leather (painted
in its patch but not on the pelt beside it) and the ear rims (orange on the front, black on the back).

## What the checks showed

| Check | Result |
|---|---|
| Side overlay on the skeleton plate | Paws, hock and shoulder on the plate's joints |
| Side overlays on the photos | Top line, underline, chest depth and legs agree. The tail first hung straight down; both photos show it slanting back and longer, so it was rebuilt |
| Head top line | Convex: each step down steeper than the one before |
| Eyes | Each eye once per side from the front, 3/4 and side |
| Creases | Under 90° round the eyes and muzzle; the ear bases are sharper (155°) |
| Slivers | Ear base 11.8, hock 10.6 (the limit is about 10) |
| Walk | Feet planted. Lift 5% (hind) and 6% (front, down from 9.7% after the wrist fold was reduced). Leg-body junction stretch 37% |

## What the skill was missing (now added)

1. **The scripts it names were not bundled.** The skill now says so and to write the equivalent.
2. **The overlay assumes the animal faces one way.** The fox photos faced the other way and the first overlays were
   wrong. The skill now says to flip each reference first.
3. **A stand-in renderer is not the engine.** The lit-view script rendered much brighter than the real viewer. Colours
   darkened to suit it looked dull in the viewer and had to be brought back. The skill now says to take the final colour
   decision from the real renderer.
4. **Painting texels from their 3D points** is now the skill's first suggestion for seam continuity.
5. **Where to find references:** public-domain artist anatomy plates, a close relative standing in, the licence checked,
   the user asked before downloading, and preview-sized copies where originals are rate-limited.

## Round 2: the eyes

A reviewer compared the fox's eye with the measured models' eyes and found it far simpler. The eye study
(`references/reference-measurements.md`, "Eyes") showed why: the amber eye was 0.08 *brighter* than the orange round it,
with no catchlight (its brightest texel 0.44), no rim (spread 0.03) and no socket. The old rule of soft eyes with no near-black
or near-white, followed by a blur over the whole patch, had removed every zone that makes an eye read.

Repainted as the eye stack (§6), from the fox photo:

| Zone | Painted | Measured after |
|---|---|---|
| Size | 1.45 times life size (13 × 7 mm half-axes) | 20 texels wide in the eye patch |
| Catchlight | about 1.5 texels, upper front | brightest 0.90 |
| Eye body | amber iris round a black vertical slit | darkest 0.01 |
| Rim | a black lid line all round, about 1.5 texels | 0.11 darker than the coat, spread 0.09 |
| Socket | about 0.30 darker, a little more above | about 0.09 under the fur beside it |
| Form strokes | paler fur above the inner corner; the dark line from the inner corner down toward the muzzle | — |
| Blur | none on the eye; the nose keeps its blur | — |

Problems along the way:
- The first catchlight was about 6 texels wide: a white patch, not a glint. Size it in texels.
- The first tear line ran level, not down toward the mouth.
- A bright amber iris clipped to yellow under the viewer's lights; it was darkened to about the coat's value plus the
  rim's contrast.

The seams did not change (0.009 median, 0.026 worst 10%), because the socket and the line fade out inside the patch.
The ring measure needed elliptical rings for an almond eye. Measured with round rings, the zones mixed eye and fur.

## Round 3: the nose and muzzle

The nose and muzzle study (`references/reference-measurements.md`, "Noses and muzzles") found the fox's muzzle painted as
flat colour. It failed four of the study's measures:
- the nose was a flat black cap: no lit top (+0.05), and nostrils no darker than the leather;
- the muzzle's top was no brighter than its side (0.19 against 0.18), because a "darker muzzle top" had been painted over
  the light;
- the mouth line sat at the very bottom edge of the muzzle, where nothing sees it, so it had no contrast (0.21 against
  0.22);
- the chin was lighter than the lip.

| Part | Repainted | Measured after |
|---|---|---|
| Nose | a lit band across its top (one function shared by the patch and the pelt, so the seam matches); a glossy highlight; two near-black nostrils, each under a lit rim | nose 0.05, nostrils 0.03; the band shows in the renders |
| Bridge | lit like the back: brighter toward the top of the muzzle; the darkening removed | bridge 0.25-0.29 against side 0.18-0.22 |
| Mouth line | dark, along the muzzle's lower-flank vertex row (the edge where the side turns under), from under the nose to the corner | 0.04-0.09, under a white lip of 0.40-0.42 |
| Upper lip | a white band above the mouth line | 0.40-0.42 |
| Chin and jaw | shaded below the mouth line | 0.20-0.26 |

The seams stayed clean (0.009 median, 0.028 worst 10%). A first try left one seam at 0.18 where the pelt's and the patch's
leather ended at different heights; one shared edge fixed it.

**A limit of the measure:** `nose_study.py` finds the nose as the pixels darker than the face, so a lit top brighter than
that threshold falls outside it. The fox's "brightest 5%" stayed at 0.10 although the band shows. Judge the lit top in the
renders, or measure the top rows of the nose separately.

## Round 4: the inner corner of the eye

The reviewer then found the inner corner of the eye drawn as a thin, long dark line, where a real fox's is a blended
transition. Measured on the fox photo, the corner is a dark pocket where the lid line widens. From it a soft wedge of
darker warm brown runs down and toward the nose, darkest at the corner and tapering and fading over about 1.3 eye widths.
The measured models grade the darkness out from the eye's edge over 2-4 texels too.

| Along the mark (eye widths) | 0.05 | 0.15 | 0.30 | 0.50 | 0.75 | 1.00 |
|---|---|---|---|---|---|---|
| Photo: darkening / width at half depth | 96% / 0.45 | 78% / 0.45 | 69% / 0.50 | 64% / 0.45 | 44% / 0.35 | 35% / 0.20 |
| The fox after: darkening / width | 84% / 0.60 | 72% / 0.55 | 62% / 0.45 | 43% / 0.35 | 36% / 0.20 | 22% / 0.50 |

What was painted:
- a near-black pocket widening the lid line at the corner, with a faint cool wet rim along its lower edge;
- a dark core just under the corner;
- the wedge, with a Gaussian cross-section whose depth and width follow the photo's profile.

The seams were unchanged. The wedge fades out a little faster than the photo's between 0.5 and 1.0 eye widths.

## Round 5: the coat

The reviewer found the coat flat beside the measured coats, which show where the joints meet and give the body depth. The
coat study (`references/reference-measurements.md`, "Coats") measured three layers on the torso. The fox's large light was
about right (0.026), but its form layer was 0.009 (measured 0.014-0.034) and its strokes 0.008 (0.013-0.049). The strokes
were all one horizontal direction: coherence 0.74, against 0.06-0.28.

| | Measured | Before | After |
|---|---|---|---|
| Large (sd) | 0.035-0.043 | 0.026 | 0.027 |
| Form (sd); darks / lights | 0.014-0.034; ±0.023-0.050 | 0.009; ±0.015 | 0.024; ±0.039 |
| Strokes (sd) | 0.013-0.049 | 0.008 | 0.018 |
| Stroke coherence, whole / local | 0.06-0.28 / 0.24-0.33 | 0.74 / 0.74 | 0.42 / 0.49 |

What was painted:
- **The form layer:** soft lines placed from the skeleton:
  - the shoulder blade's lit spine and the groove behind it;
  - the lit front of the upper arm;
  - the crease behind the elbow and the lit point of the elbow;
  - the ribcage's lower edge and faint rib bands;
  - the flank fold and the thigh's lit front edge;
  - the haunch's lit dome and the hamstring groove;
  - the crease behind the knee and the lit kneecap;
  - the hock's lit point with its tendon, and the crease in front of it;
  - the wrist's point and its crease;
  - two neck folds.
- **The strokes:** a flow field: along the back and belly, down and back over the shoulder, back along the neck, down the
  chest and legs, bending round behind the haunch. The angle wanders in clumps, and strokes in six fixed directions are
  blended so they bend smoothly.

Two tries failed first:
- A clump noise of about the form shapes' size gave numbers in range and a camouflage-patterned coat that hid the anatomy.
- A flow circling the haunch drew a bullseye.

Seams stayed clean (0.008 median, 0.039 worst 10%). The strokes are still more aligned than the measured coats', mostly
because the fox's torso is long flank.

## Round 6: stripes across the top of the head

Seen from the front and above, the forehead and the top of the neck showed bands across them. The mesh was not the cause:
the back's spine vertices were unrolled in the UVs as the skill asks. The cause was the painting. Every texel was painted
from its 3D point, and across the unrolled band the true height hardly changes, so the new fur strokes there varied only
along the body. The skill already said to paint the band by its own height, which is how the cat and the anteater were
painted; the newer advice to paint from the 3D point had overridden it without saying so.

**Fix:**
- The colour zones, the light and the form still come from the 3D point.
- The strokes and the colour noise use the texture's own height (v), blended back to the true height at the nose patch's
  edge.
- Seams: 0.010 median, 0.038 worst 10%.

Both copies of the skill now say this in the unroll step, with a row in the failures table.

## Round 7: paw shape

The same foot study found the fox's paws upright boxes: splay 1.1-1.3, reach 0.1-0.7, footprint 0.10 x 0.06 of the
height.

**Rebuilt:**
- **The paw:** a sloping, splayed wedge, enlarged to about the measured dog and wolf.
- **Result:** footprint 0.13 x 0.09-0.10, splay 2.0, reach 0.8-1.4, 8 ground contacts.
- **The walk:** lift 2-2.8% of the height (lower than before, still in range).
- **Seams:** 0.016 median, 0.055 worst 10%, after the paw patch's fade was matched to the wedge's knuckle ring.

## Round 8: small refinements

- **Strokes:** the angle wanders more (±40 degrees), so they are less aligned: coherence 0.40 overall, 0.50 locally (from
  0.42 and 0.54).
- **The mouth line:** a little wider and softer, so it no longer stair-steps where it crosses stretched faces.
- **Seams:** 0.011 median, 0.058 worst 10%.

## Not verified

- Every width (no top view).
- The muscle bulk of the body (no side muscle plate).
- The walk against frame-by-frame footage (only one walking photo was used).

## A later round: the walk's duty, from an IK bug

`lp check` failed the fox's walk: the lowest foot was down 0.54 of the cycle, against 0.58-0.92 measured and 0.70 built.

**The cause was a bug, not the gait.** The foreleg's shoulder slides with the reaching leg (§7), and the IK took the upper
arm's length from that slid shoulder to the rest elbow.
- **Early in the stance:** the shoulder is forward and the arm looked 2 cm long, so the planted paw hovered up to 1.4 cm.
- **Late in the stance:** the arm looked 3 cm short, so the paw sank 1.9 cm into the ground. In the last frames the leg also
  ran out of reach (fully straight).

**The fix:** the bone lengths come from the rest pose. Results:
- the front paw now sits at 0.0 cm through the whole stance;
- the leg stretches to 96% at most;
- the lowest foot is down 0.79 of the cycle (front 20 of 24 frames, hind 19);
- the swing still lifts 3.4% of the height.

The cat's build had the same line and got the same fix.

## A later round: clearing the remaining warnings

`lp check` warned on five things. Each was fixed at its cause:

| Warning | Before | After | Cause and fix |
|---|---|---|---|
| Slivers | 11.8 | 8.4 | One ear's ring was stitched to the head with different diagonals from the other's, leaving a sliver at one ear's base only. The better side is now mirrored onto the other. A tidy pass also welds vertices under 4 mm apart and flips the diagonals of nearly flat quads (`mesh_tidy.py`): 1 weld, 8 flips, 480 to 476 triangles |
| Stroke coherence, overall | 0.40 | 0.18 | The angle wanders ±50 degrees in clumps (was ±40), strokes are 3.3 times longer than wide (was 5.1), 20% direction-free breakup |
| Stroke coherence, locally | 0.50 | 0.28 | the same |
| Nose: lit bridge over the side | 0.00 at the stop | 0.03 | The lit band on the muzzle's top now runs back to the stop, and a little light falls on the stop's top |
| Mouth line under the white lip | 0.36 | 0.21 | The line was near-black at 80%. It is now a dark brown at 55%, still clearly drawn |

Seams went from 0.011 / 0.058 to 0.012 / 0.066. The fox now passes every check with no warnings.

## A later round: the thigh's mass, measured from the front

**Found in a QA pass against the later skill:** measured as the outline's half-width at each height from the knee to the hip,
the fox's hind leg was widest at the knee (0.073 m at 0.195 m) and pinched over the hip joint (0.053 m at 0.30 m). The leg ran
from its hole straight to a knee ring wider than the haunch, with no ring where the thigh is fullest: the T. rex's mistake of
its round 15.

**Fixed:** the haunch's lower flank (the hole's outer edge over the hip) moved out to 0.060 m, a ring at mid-thigh (0.248 m)
takes the fullest point (outer edge 0.078 m), and the knee ring came in to about square (outer edge 0.067 m).
- **Measured** (`limb_widths.py`): widest at t 0.42 between the knee (0) and the hip (1). Before: t 0 and 1.00.
- **A second pass, after a review in the viewer:** the first mid-thigh ring was a 4-point diamond, and its outer point
  stood out as a bump below the haunch with a dent at the hip above it. It became a 6-point ring with a flat outer face
  (0.075 m), the haunch's lower flank came out to 0.064 m and the rump's to 0.055 m, and the knee ring went from a thin
  blade (0.012 by 0.042 m) to 0.016 by 0.036 m. The profile now rises smoothly: 0.061 m at the hip, 0.075 m at mid-thigh,
  0.068 m at the knee (the knee 0.91 of the widest); the creases down the leg fell from 128 to 106-113 degrees.
- **Cost:** 12 vertices and 24 triangles in all (252 / 500: both now warn against the medium tier's 250 / 480).
- **Checks:** `lp check` passes (seams 0.012 / 0.066; stretch 5%, at its limit).
- **The check now in `lp check`:** `limbs.hind_peak` and `limbs.hind_knee`, written from this round and the T. rex's. The
  build before the fix warns on both.
- **Not done:** the two sides are not triangulated alike (306 of 476 triangles had no mirror twin); the widths still rest on a
  dog's front plate, with no top or rear view of a fox.
