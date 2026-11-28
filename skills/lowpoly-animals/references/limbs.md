# Limbs: building the muscle, not the bone

The detail behind SKILL.md §3, rule 2. Read it before building a limb.

**Polygons follow the muscle, not the bone.** Every mass that makes its own shape in the reference gets its own vertices,
and every place where two masses meet gets a fold. Masses include the thigh, the haunch, the shoulder, the upper arm, the
neck's muscle and the jaw muscles. Spend polygons on these shapes before anything else in the limb:
- **A lobe needs a ring at its widest,** in every view. The ring sits at the mass's fullest point, not at the joint, and
  not where a construction step happens to leave vertices.
  - **Measure it in the front view:** take the outline's half-width at each height. A thigh is fullest at about mid-leg,
    level with the lower flank over the hip joint, and tapers up to the back and down to the knee.
  - **In code:** `lib/lowpoly/tools/limb_widths.py` finds each leg from the rig and prints its half-width at each height from the knee to
    the hip (counting only the leg's own skin and the body's, never a wing, another leg or a side branch beside it), where it is widest (t: 0 the knee, 1 the hip) and the knee's width as a share of the widest. `lp check` warns
    when the hind legs are widest below t 0.25 or the knee is over 0.95 of the widest. Both are the same mistake: the leg's
    mass at the bottom, with the haunch pinched above it.
    - **The test builds:** the T. rex (round 15) and the fox were both widest at the knee before their fixes (fox: t 0, the
      knee the full width, the haunch over the hip 0.73 of the knee); after, both were widest at t 0.42 with the knee at 0.86
      of the widest. The cat built before this check still measures t 0.08 and 0.99.
    - **Not for birds** (`"body_plan": "bird"` in the spec): a bird's visible thigh is a feathered trouser, which flares
      toward its lower edge (the agent trial's bald eagle, 0.115 m at the knee against 0.093 m at the hip), not a muscle
      mass; `lp check` leaves both checks out for it.
    - **The exception:** short legs inside a broad body (the anteater) are widest at the hip, where the body's flank is,
      and taper down to the knee: t 1.0 with the knee at 0.93 passes. That is a taper, not a pinch.
    - **The fix,** as on the T. rex and the fox: move the haunch's lower flank (the leg hole's outer edge over the hip) out a
      little, put a ring at mid-thigh at the leg's fullest point, and bring the knee ring in to about square.
      - **Give the mid-thigh ring a face on its outside, not a point:** six points (front, front-out, back-out, back,
        back-in, front-in), as the T. rex's. The fox's first try used a 4-point diamond: its outer point stood out as a
        ridge below the haunch, with a dent at the hip above it, and a crease of 128 degrees down the back of the leg.
      - **Let the haunch carry the width up:** its lower flank about 0.85 of the thigh's widest, so the profile rises
        smoothly from the hip to mid-thigh instead of stepping out below a narrow haunch.
      - **Keep the knee ring about square:** a thin blade of a ring (the fox's was 0.012 m wide and 0.042 m deep) creases the
        leg's front and back. At 0.016 by 0.036 the creases fell to 106-113 degrees, about what any 4-sided ring makes.
  - **The test T. rex** was widest at the belly line instead (0.84 m there, pinched to 0.74 m above), so the leg's mass sat
    at the bottom of the torso. Moving the lower flank over the hip out and the rings below it in put the peak at 2.4 m
    (0.91 m), tapering to 0.65 m at the knee.
  - **Don't let a ring come to a point:** where its front or back vertex is far ahead of its neighbours, it makes a ridge
    down the limb. A 4-sided limb ring always creases at about 90 degrees; keep it about square.
  - **Thigh lobes:** front to back at the belly, 0.19–0.46 of the leg's length on the measured quadrupeds, and about 0.5
    on the T. rex reference.
  - **Taper to the knee:** for a long or heavy thigh, add a ring halfway down at about two thirds of the lobe's depth, so
    the thigh tapers to the knee as one pillar. Without it you get a shelf under the belly with a stick leg below.
- **A fold where masses touch.** Where the thigh meets the belly, put their edges close together over a short span (a
  narrow, deep crease), then join them. The bear's thigh and belly practically touch for a stretch before joining the
  torso. A wide V-notch or a smooth blend loses the fold.
  - **Model it, then paint it.** Pull the vertices of the ring at the fold in toward the body, the lowest the most, the
    upper ones less, and leave the ridge and spine alone so the fold fades toward the back. It needs no new vertices.
    Aim for 20–45 degrees between the faces either side of the fold: under about 15 it vanishes under smooth shading, and
    over about 90 it shows as a hard line.
  - **The paint:** a crease-and-rim pair along the same line (`references/texture.md`): a dark line in the groove and a
    lit edge on the mass that overhangs it.
  - **Between the thighs:** the belly's midline must sit above the thighs' inner edges, so each inner thigh rises into
    the torso. Where the belly hangs as low as the thigh, the inner thigh runs flat to the midline: from below it is a
    wide panel stretched across the groin, and a side-projected texture smears into streaks on it. On the test T. rex,
    raising the three groin vertices 10-30 cm (to 2.02, 1.88 and 1.80 m, over thigh edges at 1.72-1.84) turned the panel
    into a recess, at no cost in vertices.
  - **On the T. rex:** paint alone was lost under the viewer's lights. The waist ring's lower flank pulled in to 70% of
    its width (and the upper flank to 84%) made a groove of 22–44 degrees that reads at game distance.
- **A bone inside the outline is not a muscle inside it.** A skeletal drawing shows where the femur is. Only the muscle
  reconstruction, life art or photos show where the thigh is.
  - **The T. rex:** its femur lies inside the torso outline. Built from the skeleton alone, its first leg ring was the
    knee, so the leg left the belly as a thin column with no thigh.
  - **The reference:** a reconstruction's walk showed the thigh as a lobe about 1.5 m deep. Its front crease runs up the
    flank, it hangs below the belly, and it tapers to a knee at about belly height in mid-stance.
  - **When a skeletal drawing seems to show the thigh inside:** check the muscle reference before leaving the thigh out.
- **Check it against the reference in the side, front and rear views.** Count the outline's lobes and notches in each view:
  each lobe must have vertices at its extreme, and each notch a vertex at its bottom. A budget cut takes vertices from
  straight runs of the outline, never from a lobe or a fold. Overlay the model on the reference with the same height,
  ideally at several frames of a walk, and compare the legs' silhouettes. The T. rex's leg overlap with its reference rose
  from 0.37 to 0.39 with the thigh, on top of the walk fixes.

## The flank fold: the hole reaches forward past the knee (from SKILL.md §3, rule 2)

**The hole must reach forward past the knee: the flank fold.** In quadrupeds a fold of skin, the flank fold (*plica
lateralis*), runs from the side of the abdomen to the hind limb in front of the thigh, and the stifle (knee) sits in
line with the abdomen. In some species it is loose and low (a cat's belly pouch hangs right in front of the hind legs).
So the front edge of the hind leg's hole must be at or ahead of the kneecap:
- let the hole span three body rings, from behind the hip to ahead of the knee (on a quadruped: rump, haunch, waist),
  rather than two;
- weight the waist ring lightly to the thighs (body 0.6 / thighs 0.4 at the flank) so the fold stretches when the leg
  swings.

With the hole ending behind the knee, the thigh's front face folds back under the belly in a deep V-notch; the measured dog,
deer and bear have none. Check it in side, rear and underside renders of the hindquarters
(`lib/lowpoly/tools/region_views.py`).

## The haunch from behind (lp check rear.*, `lib/lowpoly/tools/rear_study.py`)

**The anatomy.** The haunch is one convex mass: the gluteals over the pelvis and the hip joint, and the biceps femoris and
the hamstrings down the back of the thigh to the stifle. From behind it is widest over the hip joint and the thigh's
muscle, and below the stifle the leg narrows evenly through the gaskin to the hock. A convex mass has no waist and no
corner, so from behind the outline runs down from the hip as one column. Read the widths from the species' own rear and
3/4-rear photos (and a rear plate where one exists) with the tail lifted or to one side, so it doesn't hide the contour.

**The failure** (a mountain lion, 2026-11-26). To make the thigh widest at mid-leg (limbs.hind_peak), its thigh ring was
widened until it stood out past the hips, while the body's lower flank round the leg's root kept the torso shape's
narrower side (0.85 of the half-width). From behind the outline went in at the leg's root, out to the thigh ring, and
in again to the shin: a saddlebag lobe with a waist above it (bulge 2.8% of the height, notch 2.6%, a 40-degree turn).
No side or front measure saw it.

**Build it as a column:**
- Push the lower flank round the hind leg's root out to the hip's width, so the leg's root doesn't make a waist.
- Size the thigh's widest ring from the muscle, just outside the hip's width at most, and taper the knee, gaskin and hock
  rings evenly below it.
- limbs.hind_peak asks where the thigh is fullest; it does not ask for it to stick out. Satisfy it by the ring's height,
  not by widening it past the body.

**Check it:** `lp check` rear.bulge, rear.notch and rear.corner measure the haunch band (the hock to just above the hip,
tail left out) in the bind pose and four walk frames. The limits allow for low-poly facets only; a convex mass itself has
no lobe, waist or corner. Look at the rear and 3/4-rear views of `lp preview` too.

## Both sides alike: check the symmetry after every topology change (from SKILL.md §8)

A mirrored model shares one pelt between its sides, so both sides must have the same triangles, mirrored. The pelt then fits
both. A side whose triangles differ samples the texture smeared, and shows a crease or a long triangle that the other side
doesn't have.

**What breaks it.** Several steps can, even when every vertex is placed symmetrically:
- **A stitch that sorts by angle round a fixed axis,** as when bridging a limb ring to its hole or an ear to the head. The
  axis has a handedness, so the two sides get different diagonals.
- **A loft's quads split with the same diagonal on every side.** The mirror of a +x quad's diagonal is the other diagonal of
  the -x quad.
- **Clean-up passes** (welding, flipping diagonals, collapsing slivers) that run on one region, or in vertex order.

**What it looks like:** a long triangle or a shading crease on one side only, or a texture smeared on one side only. On the
test T. rex:
- one inner thigh was streaked (`case-study-trex.md`, round 16);
- later, one side of the chest between the arms had a long triangle (round 21). The arms had been left out when the legs
  were fixed.

**Check it in code, for every mirrored pair, after every change to the topology.**
- **The pairs:** legs, arms, ears, wings, fins, and the body skin round their joins.
- **The check:** for each face whose corners are all on one side (or on the midline), look for a face with the mirrored
  corners (x to -x, matched by position). List the faces without a twin, by region.
- **Every pair:** don't stop at the part where the fault was first seen.

**Fix it** by rebuilding the worse side's faces as the mirror of the better side's (`lib/lowpoly/mesh_tidy.py`, `mirror_better_side`), region by
region, joins included.
- **Only where every vertex has a twin.** A region mirrors cleanly only if every vertex in it has a mirror twin among the
  other side's faces.
- **Stop short of the body's own asymmetry.** Where the body's own triangulation differs (a loft whose diagonals don't
  mirror), end the region before it. The test T. rex's arm region first failed on a neck vertex with no twin and had to
  stop at the chest.
- **Better at the source:** stitch each side with a mirrored axis (or in vertex order when the rings have the same count),
  and split the loft's -x quads with the mirrored diagonal.

## Heavy columnar legs (the Kodiak bear, hostile, 2026-11-24; *approved by lp check*: 43 checks, no warnings)

**A heavy animal's legs are columns under the body, not tubes out from it.** From the front the legs drop straight from the
shoulders and hips with their outer edges in line with the body's sides (a bear's forefeet stand 0.6 of the shoulder width apart;
each foreleg is a third of the shoulder width across, with its hair). Build the leg as a mass with its hair's silhouette:
- a 6-ring (front, front-out, back-out, back, back-in, front-in) where the mass is fullest (the elbow with its hair, the
  mid-thigh), 4-rings at the narrow joints below (wrist, knee, hock);
- the upper arm stays body: the hole sits at the belly line and the shoulder's muscle builds up into the hump from it;
- the hind leg's hole spans three rings (waist, hip, rump), the belly between the thighs raised above the thighs' inner edges;
- **zip a hole to the ring under it by hand.** A hole is a loop on the flank, its top edge outer and its bottom edge inner, over a
  horizontal ring: an angle-sorted bridge mis-orders a hole of six over three rings (open edges) and leaves slivers on a hole of
  four. Map the hole's outer-front corner to the ring's front-out vertex, its inner corners to the ring's front, front-in and
  back-in, and so round.
Measured on the Kodiak (1.50 m at the hump): elbow ring 0.26 x 0.32 m, wrist 0.13 x 0.15, mid-thigh 0.29 x 0.42, knee
0.24 x 0.28, hock 0.12 x 0.17; the hind leg widest at t 0.33, the knee 0.90 of it.

**Cut the leg hole beside the belly's midline, not out on the barrel** (the Kodiak, 2026-11-24, after the user saw
"unnecessary cuts" where the legs met the underbelly). Its holes were cut between the flank and the barrel's low corner,
which sat 0.78 of the half-width out, so a flat belly 0.5-0.6 m wide ran between each pair of legs, and the legs' inner faces
(0.14 m from the midline) met it through near-horizontal faces: a shelf with a crease at every join. Bring the hole's low
corner in over the leg's inner face, so the inner face runs straight up into the body, and shape the strip between the legs
as the animal's: the brisket a keel between the forelegs, the groin an arch between the thighs (the reference bear's inner faces rise to
the midline). Check it in front, rear and underside renders of each pair of legs (`lib/lowpoly/tools/region_views.py`).
The Kodiak's rear crossings fell from 19 to 6 with it. Don't overdo the groin's arch on a heavy animal: raised 12 cm, the Kodiak's hindquarters
read thin and high from below and behind; a heavy bear's rump is deep and low, its underside close to the tops of the
thighs (the arch at most a few centimetres).

## Legs that bend (lp check motion.leg_rings, motion.leg_stretch_*, motion.hyperextended, motion.lockstep; `lib/lowpoly/tools/leg_bend_study.py`)

A leg built with the right widths can still lose them in motion: a joint folds further than its ring of skin can follow, or
a short band of skin behind a joint stretches by a third. Read how the species' joints bend before animating, and measure
every clip.

**Not for a human (body_plan biped).** These ring and crush checks, and lockstep, were set on a mountain lion's legs. They
push a joint's bend across two or three rings to keep the leg's width. On a human knee that spreading bends the leg in two
places: a "knee block" between two creases. A person's knee is one hinge: the ring above on the thigh alone, the ring
below on the shin alone, and only the knee's own ring, at the joint line, shared. The skin behind a deeply bent human
knee really does compress, and the calf and hamstrings press together there. Model that contact (the calf's belly pushed
up into the fold by a helper bone) instead of keeping the ring's width. A standing human attack plants both feet, so its
legs move alike. `lp check` skips motion.leg_rings, motion.leg_stretch_min and motion.lockstep for bipeds;
motion.leg_stretch_max (skin over-stretched across a joint's front) still applies.

**How a quadruped mammal's joints bend** (the carnivore and ungulate limb; check the species' own):
- **Hinges bend one way only.** The elbow folds with its point (the olecranon) behind; the knee with its point in front; the
  hock (the tarsus) with its point behind. None straightens past its line: a knee or elbow bent backwards reads as a break.
  The shoulder and the hip swing forward and back over a range; they don't flip either.
- **The carpus (wrist) is the exception.** It stands near straight, a little dorsiflexed, under the weight, and in the swing
  it folds far the other way (the paw tucks back). Both sides of straight are anatomical, so `lp check` judges it only when
  the bind pose shows it clearly bent (a hock, a plantigrade wrist).
- **Big folds share the joints.** A crouch, a pounce's gather, a swing: a cat folds its shoulder, elbow and wrist (hip, knee
  and hock) together, each part of the way, never one joint all of it.

**What the skin can follow.** The viewer skins by linear blend: a ring of skin weighted half and half across a joint shrinks
to about cos(bend / 2) of its width as the joint folds away from its bind angle:

| Fold from the bind pose | 30° | 50° | 70° | 90° |
|---|---|---|---|---|
| The joint ring's width | 0.97 | 0.91 | 0.82 | 0.71 |

- **Keep each blended ring's fold under about 50° from the bind** (motion.leg_rings warns under 0.90). A deeper pose spreads
  the fold over the neighbouring joints, or bends from a bind pose closer to it.
- **Short bands stretch most.** The skin between a wrist ring and a knuckle ring is a few centimetres long; turning the wrist
  50° against the forearm stretches its back edges by a third. Cap the wrist's turn in the leg IK and tip the pastern with the
  forearm beyond it: on the mountain lion, 22-23° (`WRIST_LIM`, `WALK_WRIST_LIM` in its builder). motion.leg_stretch_* warn
  outside 0.70-1.35.
- **Where the leg meets the body** the armpit and the groin stretch as the shoulder or the hip swings: real skin does too.
  It is the last stretch left on a well-built leg (1.3 on the lion); a junction past 1.35 needs the swing reduced or the
  junction's weights moved toward the leg.

**Each leg on its own in an action clip.** A clip that moves the left and right legs as one reads as a puppet. In an attack,
a roar or a rear, give each leg its own timing (a few hundredths of the clip apart), height and path, and let the feet that
the body leaves behind follow it (a pounce's hind feet hop after it as the forepaws land, then step back one at a time).
motion.lockstep warns when a pair's joint angles correlate past 0.95 over an action clip. Gaits and standing clips are not
judged: their pairs move in phase or counterphase by design.

**The mountain lion's pounce and walk (2026-11-26), measured with `leg_bend_study.py`:**

| | First pounce | Rebuilt |
|---|---|---|
| Narrowest joint ring | 0.86 (elbow, crouch) | 0.91 |
| Edge length along the legs | 0.74-1.30 | 0.76-1.32 |
| Hind pair correlation | 1.00 (lockstep) | 0.90 |
| The walk's left wrist against its forearm | 69° in the swing, edges to 1.39 | capped at 22°, 1.27 |

The fixes: a shallower crouch, the wrist rising onto the toes as the elbow folds, the wrist cap, each leg's own timing and
path, and the hind feet following the body. The pounce's sequence (crouch, spring and rear, grab, one held neck bite, drop,
recover) came from the species' hunting behaviour (`lowpoly-core/references/temperament.md`, the attack).
