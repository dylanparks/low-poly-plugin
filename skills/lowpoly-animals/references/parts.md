# Parts: each body part as a module

Every build so far solved a part: a beak, a folded wing, a sprawling leg, a clawed foot, a crested tail. This file indexes
them as modules: where each was built and checked, how to build, rig, fold and check it, and which references it needs.
It serves two purposes:

- **Real animals:** a new species reuses the closest module instead of solving the part again (an owl's wing starts from
  the eagle's wing, a monitor lizard's legs from the crocodile's).
- **Composite and fantasy animals** (a dragon, a griffin, a chimera): an animal that doesn't exist is assembled from parts
  that do. Fantasy illustrators build a dragon's wing on a bat's hand and a griffin's head on an eagle's, because the real
  part's structure is what makes the invented animal believable. So each part is built and checked by the rules of the real
  animal it comes from, against that animal's references, and the parts are joined by the joining rules below.

Each module's **status** says how far it has been tested: *approved* (built, checked in code and accepted by the person
reviewing it), *built* (built and checked in code, with known gaps), or *untested* (described from anatomy, not yet built).

## Wings

**Feathered wing** (bald eagle, agent trial; *approved*: the flap; *built*: the folded pose)
- **Structure:** arm, forearm and hand bones; the flight feathers carry the outline (the secondaries on the forearm, the
  primaries on the hand). The wing is a flat surface with a slight camber, about a third as deep as it is long at the arm.
- **Build it spread, fold it with the rig.** A wing built folded and stretched open is a scoop in flight (rounds 1-10).
  Model the open wing; one fold value turns the elbow and wrist together (pigeons couple them). Slotted primaries: three
  fit a 250-vertex budget with a clean fold; five didn't.
- **Two different motions:** at rest the wing folds onto the body like a cloak (the forearm and hand turned over: a
  Z-fold); in flight the elbow and wrist sweep within the wing's own plane (the hand back toward the body on the upstroke).
  Using the rest fold in flight makes the wing wave like an accordion.
- **Joins:** one skin with the body from the shoulder along the upper flank, so it stays attached at every angle; the
  leading edge lies on the shoulder skin when folded, no gap and no step.
- **Secondary motion:** feather bones (a primaries fan on the hand, a trailing bone per segment) baked with
  `lp bake-springs`: 10-15 degrees of lag in the flap, a visible droop in the soar.
- **References:** the spread wing from above and below, the folded wing from the side, behind and above, flight footage or
  frames for the stroke.
- **Known gaps:** the folded wing's layers still show steps behind the shoulder, and a strip of back shows between the
  wings from behind.

**Membrane wing** (a docile flying fox and a hostile giant vampire bat; *built*: the flap, the hang, the swooping attack; the fold on the ground still shows as a sail)
- **Structure:** the wing is the hand. The second to fifth fingers are very long, and skin is stretched between them and
  the body: in front of the arm (from shoulder to wrist), between the fingers, from the fifth finger to the flank and the
  hind leg, and in many species between the hind legs and the tail. The thumb is short and free, with a claw, and the
  animal walks and climbs on it.
- **The wrist has volume.** End the forearm in a small closed carpal block, root the thumb on one of its faces at the
  metacarpal's full thickness, and attach the membrane's wrist corners to the block's edges. Growing every digit from one
  hub vertex keeps the long fingers from crossing, but it pinches the thumb's root to a point: in the viewer the thumb read
  as a loose piece hanging off the wing's corner. The long fingers (d2-d5) may still taper from the block's distal face.
- **Consequences for the build:** each long finger needs its own bone (the membrane's shape between them is the wing's
  outline); the membrane joins the flank and the hind leg, so the wing and the leg move each other; it folds along the
  fingers like an umbrella, the fingers closing against the forearm and the membrane collapsing between them.
- **Rest pose:** many bats hang by their feet, head down, wings wrapped round the body; the ground-based checks (feet,
  balance) and the preview's ground line assume an animal standing, so say what a hanging pose does to each.
- **Skin:** thin, often translucent at the edges, with the fingers and the veins showing through
  (`references/skin-types.md`, membranes).
- **Folded on the ground: plan it in the build, not the pose.** On the hostile giant bat (three rounds), a wing whose
  folded membrane still showed as a large flat sail could not be fixed by posing or skinning alone. Three findings:
  - What shows of a membrane is set by its **boundary** (the arm's trailing edge, the free edge, the leg and the flank).
    Interior vertices only add pleats; the boundary has to move to shrink it.
  - The boundary can only move in as far as the arm can lie against the body. Plan the clearance when building the
    torso, shoulder and hip rings, the arm tube and the thigh's root: a body as narrow as the real animal's, and a thigh root
    placed so the folded elbow meets the flank and not the thigh. The crossings that blocked it were upper arm against
    thigh, and folded fingers against each other.
  - Fold the fingers in a fixed, layered fan in the forearm's own frame (each digit beside the next), not by world
    offsets plus a roll. Keep the membrane's boundary vertices blended between at least two bones: 100% on one bone
    tripled the crossings.
  - **Measure it:** the visible membrane area in the front, 3/4 and side views (`lib/lowpoly/tools/visible_area.py
    --bones` with the arm and finger bones), together with `lp check` motion.crossings (`self_cross.py --where` names the
    triangles).
- **No transparency:** the pipeline's textures have no alpha, so a torn or ragged membrane edge is geometry (notches
  between the fingertips, about 12 open edges for a bat), and the open edges it adds are declared as the spec's "cards".
- **Fantasy use:** the dragon's wing in most illustration is this wing scaled up, with the thumb kept as a claw on the
  wing's leading edge.

**Wing on a quadruped (pegasus, alicorn, griffin)** (the alicorn, rounds 5-13; *shipped*: the spread wing, the resting
shell, flap, takeoff and hover. The first wings were panels hinged straight off the back, which read as two boards bolted on)
- **It is an arm, and a big one.** A third pair of limbs: a shoulder mass rising out of the withers, an arm, a forearm and a
  hand carrying the feathers, thick at the root and tapering to the wrist. A 1.7 m half span read as "too small to lift the
  horse"; what the user drew was about 6 m tip to tip (3.7 body lengths), a root chord of about 1.1 m reaching back past the
  loin, widest at mid-wing, swan proportions (arm : forearm : hand with primaries about 0.18 : 0.17 : 0.65 of the half span).
  Feathered all the way: tertials at the body, secondaries on the forearm, slotted primaries on the hand, the length tapering
  evenly from the tip to the root, with no bare arm. Ask for the span in a top-view mockup before building.
- **The root is at the shoulder, and it is a fillet, not a block.** Root it at the front of the withers, just above and
  behind the foreleg's shoulder joint (where the scapula is), its shoulder bone parented to the chest. Cut the hole one body
  quad wide, so the back line runs on between the wings with no ledge. Bridge it with a mid ring (4 vertices was enough)
  that curves up out of the withers into the wing's inner face; from above the root sweeps back as a tapering, scapula-shaped
  chevron. Give the bridge its own texture patch painted from each face's 3D point: the side-projected pelt streaked it.
- **The flight wing is one continuous surface** in the eagle's construction: a leading edge on the arm, forearm and hand
  bones (blended across the elbow and wrist), a hinge row at mid-chord half on the segment bone and half on its own
  trailing-edge bone, and the notched trailing edge on the trailing-edge bones (about 4 bones a wing more than the hinged
  version). Build it spread, as the bind pose.
- **Hinged feather pages fail at the fold, and rows don't rescue them.** With separate arm, forearm and hand pages, a shared
  corner at a 50-60 degree fold dragged one layer through the next (106-144 crossings); split corners closed by thin walls
  passed the crossings but left 101-261 slivers and dark hairlines at the elbow and wrist on the spread wing; 40 more
  triangles of interior rows (rounds 9-10) still read as flat panels, because no layer could bulge without cutting the
  next. Change the construction, not the row count.
- **The resting wing: a sculpted shell that swaps with the flight wing.** The user's rest pose was raised and half folded,
  arching about 0.65 m over the back with the primaries drooping behind the croup to mid-thigh: a shape no flight wing
  folds into cleanly. Build it as its own closed, cupped shell (the arch, a covert tier, a notched lower edge of primary
  tips) on two bones a side, and swap it with the flight wing inside the takeoff's first wing-flare, where the motion
  hides it.
  - **Hiding a piece with only rotation and position keys** (the viewer has no scale or visibility keys): weight every
    vertex of the piece half to a pivot bone and half to a second bone; turning the second bone 180 degrees about an axis
    through the pivot collapses the piece onto that axis, and part of the way shrinks it smoothly. Collapse it inside the
    body (the flight wing onto a point in the shoulder hump, the shell onto a short line across the barrel). The visible
    pose then needs its bones at twice their offset from the pivot, which falls short by cos of the angle: about 10-15% on
    a folding hand.
  - **The swap still overlaps for about 0.1 s** (124-140 crossings counting the shells), and finishing the shell's shrink
    earlier made it worse. `lp check` motion.crossings counts only the main skin; motion.pieces counts the separate
    pieces' new crossings (118 here, a warning), and `lp self_cross` names the bones.
- **A raised wing's underside goes black in the engine.** The viewer lights a ground-facing surface with the ground colour
  alone and no sun: the underside measured 0.21-0.36 of the top's brightness. The normals were right. Shade the lower
  sheet with the upper sheet's normal, as the thin feather sheet it is (0.75-1.0 of the top). For it to read a little
  greyer than the top, give it its own texture patch.
- **Feather paint follows the shafts.** Painted as horizontal bands, the wing read as sailcloth. Fan each feather's shaft
  from the wing's base toward the tip: coverts as tile rows growing toward the trailing edge, secondaries broad with lit
  rounded tips over the shadow of the next, primaries long and tapered with separate tips; all within the coat's whites.
- **Motion:** `references/locomotion.md`, "Flying on a winged quadruped".

**Overlapping armour (scales, scutes, plates): one field, painted first, geometry only on the outline** (Temminck's
ground pangolin, 2026-11-24, with a curl-up clip; *approved by lp check*)

- **Measure the armour before drawing it.** Count, from references:
  - the rows across the back (pangolin 13) and the transverse rows along it;
  - the marginal scales of the tail;
  - each region's exposed length and width, as fractions of the body's length;
  - the share of each scale that shows (pangolin 0.42-0.52).

  Record where the armour stops: the hem.
- **Map the directions as a field.** Tailward on the back and tail; turning steadily to down-and-back on the flanks
  (pangolin: 0° at the spine to 58° at the hem); distal on the limbs; back toward the neck on the crown. Let each row
  sweep forward as it goes down the flank. Rows that stay square to the spine read as stripes.
- **One scale list drives everything.** List the scales once (tip position in surface coordinates, direction, length,
  width, layer). The painter, the modelled scales and the counts all read that list.
  - **The layer rule:** the scale whose tip lies further up-stream along its own direction is on top. One key per scale
    handles the flank's turn and every boundary between regions.
- **Paint each scale from its own coordinates** (t along it, x across it):
  - colour graded base to tip (dark where it leaves the row above, lit and worn at the free edge);
  - a dome across it;
  - grooves from base to tip, at least 3 texels apart;
  - a bright lip 1-3 texels inside the free edge and a dark one-texel rim at the edge;
  - **the cast shadow of the row above**: 0.15 of a scale long, 60-75% dark. Without it the rows don't read.
- **Size the cells in texels.** A back plate needs at least 18 texels to read as a scale from the 3/4 camera, any cell at
  least 6. Check the head's and the legs' cells at the sheet you will ship, and take the larger sheet rather than lose
  them (the pangolin needed 512 × 256 at the medium tier).
- **Geometry goes only where it changes the outline.** At a medium budget about 40 vertices are spare, enough for 2-3% of
  a pangolin's scales. Spend them on:
  - **the tail's marginal scales**, as a saw edge in the skin itself: a tooth vertex between rings on the edge row,
    1 vertex and 2 triangles a tooth, no separate pieces;
  - **the dorsal line**, as separate wedges: 4 vertices and 4 triangles each, closed;
  - **on a large or hero model, the scutes the camera sees against the sky** (a dragon's spine plates and shoulder armour).

  A scale seen face-on adds nothing that the paint doesn't.
- **A separate plate rides the skin on the skin's own weights at its root.** That means the skin's weight function at the
  point, or, where the skin is hand-weighted, the barycentric blend of the triangle under it. Each vertex of the plate
  takes the same weights, or the base takes the skin's and the tip the root's (hinged); both measured within 1 mm. Then:
  - **sink the base** by about 0.2 of the ring spacing (8 mm on the pangolin), the chord the skin cuts at a bent joint.
    Bases sunk 2 mm showed by 9 mm in the curl.
  - **stand the free edge off the skin** by the sag of the most concave bend it will meet (6 mm). On a concave bend tips
    press into the next row.
- **How plates behave when the body folds** (measured on the curl):
  - **The outside of a bend stretches** (pangolin spine 1.3-1.8). A rigid row stays closed only while the worst
    segment's strain is under 1/exposure (0.46 exposed: 2.17). Keep it there by spreading the joint blend over more skin
    (±5 cm, not ±3), not by lengthening the plates. A blend too narrow concentrated 2.2 at one joint and opened a gap.
  - **On the outside the free edges lift and fan** (6 → 27 mm). That is the armoured look of a curled pangolin or a
    dragon's arched neck, and it comes from the curvature, not from animation.
  - **The inside of a bend compresses** (pangolin belly 0.15-0.9). **Put the hem of rigid armour at the neutral axis**
    (the pangolin's flank, 0.88-1.01) and leave the compressed side bare skin, soft bands or small painted scales. Its
    own reason to be bare is that plates there would have to pass through each other. A dragon's belly plates are
    transverse bands, each on the ring under it, with the gap between bands taking the squash.
  - **Painted scales stretch and squash with the skin.** That reads as fanning at game distance and never opens a gap or
    crosses. Prefer paint wherever the strain leaves 0.75-1.6.
- **Check it:**
  - a strain study in code (the pangolin build wrote one): the strain per segment, the overlap left, the tip height, the exposed base, through
    every frame of every clip;
  - `self_cross` for the skin;
  - judge shingles by the tip height and the exposed base. `motion.pieces` also counts their sunk bases (18 for 8 wedges in
    the curl, none visible).

**For the dragon specifically.** Armour on the forelegs and shoulders is a limb case:
- the plates point distally and the proximal ones lie on top;
- the elbow's outside stretches and its inside folds;
- plate the outside of the elbow and the front of the shoulder;
- leave the inside of the elbow and the armpit as small painted scales or bare skin, as the pangolin leaves its inner legs.

**Protruding scales: wedges built from the painted scale list** (the pangolin, 2026-11-24, at the user's request: "small
polygon detail elements that stick out where a real pangolin's scales stick out, aligned exactly to the texture"). On a
pangolin those are the median row down the spine (the scalloped top line) and the lowest flank row (the skirt); the
tail's edge is already a saw edge. Build each as a closed wedge (4 vertices, 4 triangles) from its own entry in the
scale list that paints the texture (the tip at the painted free edge's centre, lifted 10-12 mm along the skin's normal;
the base under the row in front), and paint it from that scale's colours: the wedge then sits exactly on its painted
scale (0.00 mm off). Check it the same way: each tip a lift from its own scale's painted edge, and that edge visible
(not under a tail scale). Sink the base and keel past the low-poly skin's chord (16-20 mm on a 0.3 m animal: at 8 mm a
wedge floated 5 mm off a flat face, which lp check's mesh.loose fails), and skip the rows over a leg's hole, where the
leg's skin stands past the body's surface and buries the wedge. 16 wedges cost 64 vertices and 64 triangles.

**Long necks (swan, goose, heron; giraffe, camel, llama; plesiosaur, sauropod; a dragon's arched neck)** (the mute swan, 2026-11-24;
*approved by lp check*, 0 crossings in every clip)

- **Trace the rest curve from a dead-on side photo; don't draw an S.** A neck drawn from "forward, up, forward" bends
  wherever the drawing put its curves, and usually too tightly at the base. Mark the neck's centreline between its front and
  back edges every few percent of its length and measure its thickness perpendicular to the centreline along it. Get the
  skeleton too: it shows where the vertebrae turn inside the body, which the skin does not follow.
- **The base belongs to the body.** The lowest vertebrae of a long neck turn inside the breast or shoulders (a swan's
  cervicodorsals, a giraffe's lower neck under the withers). The skin there is the breast; put the neck's first joint where
  the neck leaves the body and let the chest bone carry the breast ring.
- **No bend tighter than about 1.7 neck radii on the inside** (curvature x radius at most 0.6), at rest or in any pose. Past
  that the inside rings fold over each other: a kink at rest, a throat squashed to a quarter, the head driven into the neck.
  A real animal's tightest pose (a swan's busking U-turn, a heron's folded neck) is often tighter than its own radius: open
  it to the limit and keep the order of the bends; the pose still reads.
- **Bones before rings.** One ring of 5-6 sides at each joint, weighted 50/50, joints at equal arc length (the bends move
  along the neck from pose to pose, so no spacing suits them all). The silhouette's kink at a joint is the joint's own angle:
  for a neck that turns 180 degrees or more in a pose, about 8 bones (a swan's display: 37 degrees at the worst ring with 8,
  48 with 4). Rings between the joints help only if each ring is weighted across three bones (a B-spline over the bone
  centres); with ordinary weights they add vertices and fold on the inside.
- **Budget:** a long-necked animal's neck may take a quarter of the vertices and triangles; the head keeps its 20-30%.
- **Pose with a bend profile, not per-joint angles.** Describe each pose as how much the neck bends where along its length
  (pitch in its own plane, lateral about each bone's throat axis) and give each joint the integral over its share. The same
  profile then drives any bone count, and sways become waves travelling along the neck.
- **Keep the head level.** After posing the neck, set the head's local rotation to the inverse of the neck's accumulated
  rotation, then add the look (yaw about world up, pitch). Give the upper neck 50-60% of a head turn as twist spread over its
  top three bones, or the ring at the skull wrings.
- **Counterbalance by solving, not by guessing.** In a walk the body rolls and sways; bend the neck's lower half against it
  by an amount solved each frame so the head travels a fraction (a quarter) of the chest's sideways travel. A bend guessed
  from the roll's phase doubled the swan's head sway.
- **Check it in code:** the posed outline's worst kink beyond rest, the shortest posed segment against rest (fold below
  about 0.3), the twist between rings, the head's tilt off level and its travel per clip, and crossings densely (96 frames)
  through the deepest pose. Look at the deepest pose from the side and the front.
- **Paint the bends:** the inside of each rest bend in shadow and the outside a lit rim, scaled by curvature x radius; the
  feathers or hair or scales painted in the neck's own coordinates (length along it, angle round it) from each texel's 3D
  point, so they follow it through every bend. Unroll the neck's texture strip line by line (each lengthwise line by its
  own length), not by the centreline: the inside of a bend is shorter than the outside.
- **Kinds:**
  - *Swan, goose:* round section, nearly constant thickness (a swan's 90-97 mm over most of its length, 66 mm under the
    head), the head carried bill-down at 45-50 degrees, the S's tight bends inside the breast and under the skull.
  - *Giraffe:* deeper than wide (a mane ridge on top), thick at the withers and tapering evenly; the neck moves mostly as a
    lever from the base (fewer, longer bends): 5-6 bones, the first carrying the most.
  - *Plesiosaur, sauropod:* the neck is a cantilever, held in a gentle arc, never an S; side-to-side sweeps more than up and
    down; thick at the base (as wide as the body there), tapering to a small head; 6-8 bones, lateral waves along it.
  - *A dragon's arched neck:* the swan's construction scaled up (a long gentle arch, the head level and alert), with its
    crest spines as a welded fin strip (above, "Crests, spines and frills"), never cards; at boss size raise the ring count to 8 sides for a silhouette the camera fills, keep
    the bend limit (it scales with the neck's radius), and put the scale texture in the neck's own coordinates so the rows
    follow the arch.

**The breast under a long neck is the body's, not the neck's** (the mute swan, 2026-11-24: the user saw "a weird polygon cut
angle" at the chest). The neck's first ring, square to a neck that leaves the body steeply, lay almost flat (a collar 4.6
cm tall and 16 cm long) with its throat corner jutting forward, and the body's last upright ring lofted to it as one flat
diagonal face from the belly to that corner. Give the breast its own upright ring, furthest forward at mid-depth (the
pectorals over the keel; the swan's at 0.27 m up, at the measured breast front), its top kept under the nape and clear of
the wing roots, the throat set back above it; zip it to the first neck ring by hand (an angle-sorted bridge turned faces
inside out once the rings no longer faced each other). The swan's crossings stayed at 0 in every clip.

**Check the breast and the neck's thickness in a dead-side view on a grid** (the swan's second side QA, 2026-11-24, from the
user's marked side view). The breast ring's lowest front point jutted forward as a prow with the breast's middle set back
behind it: make the breast convex, fullest low on the breast and rounding back under into the chest, with the underline
lowered to meet it (the swan's chest went 1-3 cm deeper). A long neck also tapers both ways: slimmer at the throat over
its top fifth, where the jaw meets it, and swelling at the nape where it joins the back. From the front the head must be
wider than the neck: a swan's cheeks swell out past the eyes, fullest at and just below eye level (about 1 cm a side on a
7 cm head). Plot the bind pose's side projection on a 5 cm grid to place each change. Give the breast a vertex on
the midline at its front: with only side vertices, filling the sides out left the midline as one edge from the breast's
bottom to the throat about 4 cm behind them, a V-groove down the chest that the user saw from the front.

**Place a bird's legs from the standing photo, then check the balance against the solid's own centroid** (the swan's leg QA,
2026-11-24, the user: "are the legs in the right position on the side view?"). An earlier round had moved the swan's feet
back to satisfy the balance check, until the leg left the body 56% back from the breast against the photo's 39%. The
volume centroid (signed tetrahedra over the closed skin) is the real centre of mass. Move the legs toward the photo as far
as the contact patch still covers it, and move the leg's hole in the belly with them: a heel ahead of its hole stretches the
leg into a thin slanted wedge (the worst aspect went from 11.6 to 30).

**Horns: every kind** (greater kudu, 2026-11-24, its spiral horns; *approved by lp check*. The reference photos showed
about 2 turns, not the published 2.5: count the turns on a head-on photo, don't trust the number in a book)

**References first, in this order:** a head-on photo of a live adult with the horns clear of the background (the turns, the
spread, the bases), a side photo, a 3/4, and a skull or a frontlet with the horns on (the base on the bone, the section).
Count the turns of the centre line on the head-on photo (the outer and inner extremes), not the published "twists"; trace the
centre line and fit the horn to it in code. Without a scale in the horn's photo, measure against the head (eye spacing, head
length) and say so. Check the species: horned-skull photos are often misnamed.

**Name the kind; each has its own centre line:**

| Kind | Examples | Centre line | Section | Rings |
|---|---|---|---|---|
| Open spiral | kudu, eland (tight), markhor, blackbuck, a unicorn's narwhal tusk (a twisted straight cone) | a conical helix about an axis that leaves the skull back, up and out, the coil starting on the inner side of the axis | keeled: one vertex on the coil's convex side, pulled out; rounding to the tip | 5 per turn for the game camera, 6-7 for a hero seen from the side; never under 4 |
| Lyre | impala, hartebeest, gazelles | an S in the front view (out, in, out again) on a backward sweep | round to oval, ringed | 6-8 |
| Curved | cattle, buffalo (with a boss), ibex, sheep (a coil: treat as a spiral of 1-1.5 turns) | a plane curve; sheep and ibex sweep back and out, cattle out and up | oval, or a flattened triangle (ibex front ridges, sheep) | one ring per 30° of bend, at least 4 |
| Straight | oryx, a unicorn | a line, slightly curved back | round, ringed at the base | 2-3 plus the tip; the rings go into the paint |
| Swept-back crown (a dragon) | several horns a side, each a curved horn on the skull's back edge | each a curved horn following the skull's top line back, the largest at the back corners, smaller ones fanning forward | 3 sides, flattened, a keel on the top edge | 3-5 per horn; the cost is in the count of horns, so share one ring layout |

**Construction:**
- **Sweep a ring of few sides along the centre line.** 3 sides is enough for any horn at game distance: the section changes the
  silhouette less than one ring step does, and a 3-sided ring with one vertex pulled out *is* a keeled horn. Put the keel vertex
  on the radial (convex) side of the coil and split its normals (a hard edge there, smooth elsewhere): the lit ridge winding round
  is what makes a spiral read in the 3/4 view.
- **Rings by the bend, not by length:** count the degrees the centre line turns (or the coil turns), and place a ring every 60-75°.
  Under that a spiral reads as a bent stick with corners. End the last ring at about 94% of the length and close with one tip
  vertex.
- **Taper** about `(1-t)^0.55`: thick through the first turn, thin only near the tip.
- **A horn is a separate closed piece sunk into a boss**, not grown out of the head skin: cap its first ring, sink it 1.5-2.5 cm along
  its own direction, and raise the head's vertices round it into the boss. Sink it only into skin weighted 100% to the head bone;
  sunk into a ring the neck shares, it cuts the neck in every head turn. (One skin with the head costs more triangles, saves no
  vertex, smooths the base into a fleshy cone and loses the skin between two close bases.)
- **Budget:** a pair of spiral horns at 3 sides and 10 rings costs 62 vertices and 116 triangles, about a quarter of the large tier.
  Pay for it from the body's straight runs (a mid-face ring, a neck ring, a tail ring, a hoof's coronet), never from a lobe or a
  fold, and give the horns a part in the contract.

**Rig:** each horn on its own bone, a child of the head at the horn's root, never animated: rigid to the head, and nameable as a
part. Check every clip with `self_cross` for horn x neck and horn x back, and build a test idle with the head turned 60-90° and the
chin raised up to 110° (the way a horned animal lays its horns back): two horns whose axes lean out 15-25° straddle the neck; horns
that rise parallel from close bases will not. Ears under a horn flick back, not up.

**Paint the horn in its own strip,** unrolled along it (u along the arc, v round the section, the seam away from the keel), from the
horn's own coordinates (t along, the angle round), both horns sharing it:
- dark and rough at the base, lighter and smoother along it, the species' tip colour over the last 8-10% (kudu ivory, oryx black);
- growth ridges as transverse lit-edge-and-shadow pairs, 3-6 texels apart, closest at the base and fading by the middle;
- the keel a pale lit line that winds with the spiral, the side away from it darker;
- a gloss streak on the upper faces of the smooth middle;
- the base blending into the head's fur over 3-4 cm; contrast part (`"contrast": true`) for the joins check;
- density 1.1-1.3 times the body's.

**Check it:** trace the centre line on a head-on photo and overlay the horn's turn extremes and tips (align a horn reference on its
own base and tip, not on the eyes: on the eye spacing a 5 cm error reads 30%); render the whole model from the game's 3/4 camera at
game size with the chosen ring count and with twice as many, and keep the cheaper one when the two can't be told apart.
`lp check`'s eye.size leaves the contract's horn and antler parts out of the height.

**For the dragon's crown:** the same rules hold per horn; spend the rings on the two or three largest horns at the back corners (one
ring every 60° of bend), make the smaller ones 3-ring cones that share the layout, sink every root into skin weighted to the head
only, and test the crown against the neck with the head raised and turned, because a swept-back crown lies along the neck by design.

**Crests, spines and frills: a welded fin strip** (green iguana, 2026-11-24, its dorsal crest and dewlap spines;
*approved by lp check*, 0 crossings). A row of spines along the midline (an iguana's or a dragon's back crest, a dragon's
head spines, a frill's edge) is a fin strip welded into the back, not cards, separate spines or paint.
- **Measure it from photos, not bones.** A lizard's crest is enlarged scales; the skeleton doesn't follow it. From a
  dead-on side photo take the height above the top line at every station, the spacing, the shape (height to base) and
  where it steps, stops or has gaps. The iguana: 0.11 of the snout-vent length over the neck and shoulders, 0.05 along the
  back, stepping to 0.026 over the tail's base, serrated to 0.55-0.6 of the tail; spacing 0.02; no gap over the hips.
- **Model the profile, paint the spines.** From the 3/4 game camera a real spine is under a pixel: what reads is the
  crest's outline (tall over the shoulders, low on the back, stepping at the tail) and a pale broken line. Space the
  modelled teeth about 2.5 px apart on screen (one per 1-1.5 real spines where the camera comes close, one per about 3
  along the back) and paint the real spines on each tooth at their measured spacing. A crest that is only painted
  disappears at game distance.
- **Build.** Split each ring's top vertex into a ridge pair (about 3-4 mm apart on a 0.1 m back) and run a zigzag free
  edge on the midline between them, with a valley directly over every ring's pair and at most two teeth per ring span: a
  third tooth, or a valley that misses its station, leaves an edge no base vertex can reach without folding the fin (7
  crossings in the walk). Lean the tips back, but never past the next valley (at most about 12% of the tooth's width on
  tall blades); carry the curve in the paint. Expect slivers of aspect 13-16 under tall, narrow blades; they lie flat and
  don't show. The iguana's: 45 vertices and 90 triangles for 17 teeth, 19% of a 480-triangle model.
- **Rig.** Weight each tooth's tip to the spine at its base's middle, its valleys and the ridge pair like the back under
  them. Side-to-side bending is free; pitch is the danger: adjacent spines of height h and spacing d touch when the bones
  under them pitch more than about atan(d / h) against each other (14 degrees for the iguana's neck spines). Keep the
  neck's pitch under tall spines well inside that, and bob with the head and the forelegs instead.
- **Paint.** Both faces from one side-view patch at about 1.5 times the body's density (about 7 texels per real spine),
  with the fin's own normals (a crease at the root). The base dark, in the same tone as a band painted on the ridge beside
  the root, so the join reads without a texture seam; a coloured blade, a pale, warm, translucent tip, a lit leading edge
  and a dark trailing edge; dark gaps between the painted spines, stopping short of the outline.
- **Rejected, with numbers:** separate sunk spines (twice the cost, 31 crossings as the back bends under their roots); a
  zero-thickness card (70 open edges, 62 crossings, one-sided shading); an alpha card (the pipeline writes an opaque
  material and an RGB texture: untested).
- **For the dragon:** a 10-15 m dragon sees its spines 7-10 times larger on screen, so each real spine earns its own tooth
  and its head spines become geometry. Keep the rules (the welded ridge pair, valleys on the stations, at most two teeth a
  span); if a crest needs more teeth than the rings allow, add rings under it first. Over a neck that arches, spread the
  arch over enough bones that no joint under tall spines bends more than about atan(d / h).
- **Still open:** the dewlap's spines, modelled as four teeth on a straight edge, read as steps close up (a curved edge
  would help).

**Mane and tail: a flowing mass** (*untested* as written; from the reviewer's brief for the alicorn)
- **What it is:** a heavy mass of hair that flows with gravity, like a thick liquid: it rises from the crest and the
  forelock, falls in both directions (over the forehead past the horn, and down both sides of the neck, heavier on one),
  and breaks into clumped locks that taper and curl at their ends. It is not one sheet and not a row of blades.
- **In low poly:** build it as 5-9 locks, each a tapered closed volume (a 3- or 4-sided ring at the root, one or two middle
  rings, a point), rooted along the crest and on the poll in front of the ears. Each lock drapes: it leaves the crest
  upward or sideways, curves over, and falls, overlapping its neighbours, with a few long locks running past the neck's
  base and onto the shoulder. The forelock is two or three locks parting round the horn. The tail is the same: a thick
  root, several locks fanning out and down, tips curling.
- **Paint:** each lock darker in its crevices and between neighbours, lighter along its outer curve, strand lines running
  along it; for a rainbow mane, the bands follow the flow down each lock.
- **Motion:** one or two spring bones per lock, so they swing and settle with gravity.

## Heads

**Beak, raptor** (bald eagle; *built*) — `references/heads.md`, "Birds: heads and beaks": the parts (cere, culmen, gape,
hook), what runs where, a raptor's profile and front view, the landmarks to measure in side and front photos.

**Jaws with teeth** (T. rex, crocodile; *approved*) — `references/heads.md`, "Jaws and mouths": each jaw from its bones and
muscles, the upper jaw overlapping the lower, teeth from the dental formula, the corner into the throat.

**Mammal head with ears** (fox, housecat, anteater; *approved*) — `references/heads.md`: the eyes against the muzzle, ears
closed into the skull, the top line.

## Limbs and feet

**Upright leg with a muscled thigh** (fox, housecat, T. rex; *approved*) — `references/limbs.md`: the thigh as a lobe,
widest at mid-leg from the front, the flank fold.

**Sprawling leg** (crocodile; *approved*) — the thigh slopes down and back to a knee that is the leg's outermost point; from
behind each leg is an arch, not a shelf. Check the pose from behind and above.

**Clawed foot** (T. rex, the drake study; *approved*) — `references/feet.md`: toes welded into the foot, claws with their own
texture strip, the footprint from the reference.

**Long-toed bird foot** (bald eagle; *approved*) — four toes on their own bones, the hallux behind; feathered trousers, not
a muscled thigh (the thigh-width checks don't apply).

**Claw** (every clawed digit; *untested* as written: the bats' and the T. rex's claws were straight spikes and are the
reason for this entry)
- **Anatomy:** the digit's last bone (the ungual phalanx) carries a sheath of horn (keratin) that is longer than the bone.
  The sheath:
  - curves toward the palm or sole along its whole length;
  - is flattened from the sides: at its base it is taller than wide, about 1.5-2 to 1;
  - has a top edge that is one smooth arc, an underside that is nearly straight or hollow, and a sharp tip.
  Its base is as deep as the digit's tip, so the claw continues the digit's top line, with a cuticle line in the paint where
  skin meets horn.
- **The digit comes first.** A claw ends a finger or toe of its own: segments with a knuckle between them, and a pad
  underneath where the animal walks on it.
  - A bat's thumb: a metacarpal, then a first phalanx with a pad (a vampire bat walks on these), then the hooked claw.
  - One cone tapering from the hand to a point reads as a spike or a blade, not a thumb.
- **Curvature, measured, not guessed.** Use a side photo of the species' claw. Draw the chord from base to tip and measure the
  angle the outer (top) arc makes over it: the outer-curvature method of Pike and Maitland (2004), used by Birn-Jeffery et
  al. (2012).
  - Claws follow use: ground walkers' are the flattest and deepest, climbers' and hangers' the most curved, perchers' and
    predators' in between. A bat's thumb and toes, which climb and hang, are strongly hooked.
  - A theropod's hand claws are hooked; its weight-bearing foot claws are broad and flatter (a tyrannosaur's are blunt).
  - Record the angle and its source in the build script, as with any landmark.
- **Digits side by side, not a fan.** A foot's toes lie nearly parallel in a row as wide as the foot, each a short skin
  segment ending in its own claw, all hooking the same way (a bat's hind foot is a comb of five hooks). Claws radiating from
  one point read as a flower of blades. Build a foot plate and root the toes along its front edge; neighbouring toes can
  share the plate's vertices.
- **Colour from the species, not a default.** Many claws are dark horn: a bat's are near-black or grey-brown, lightening only
  a little at the tip. Ivory-tipped claws suit some animals (a theropod's, a big cat's), not all. Paint the claw from a photo
  of the species.
- **Build it curved:**
  - the root (the digit's last ring);
  - at least one middle ring, turned toward the palm by about half the claw's arc and shrunk;
  - the tip, carried on round the arc.
  - Give the rings a three-sided section taller than it is wide, with a keel on top.
  - This costs 3 vertices and 6 triangles per claw more than the straight root-ring-tip spike in `references/feet.md`.
    With many claws (ten toes and two thumbs on a bat) use the cheap form: a two-vertex middle (top and underside) and toe
    roots shared along the foot plate's front edge, about 7 triangles per toe.
  - Weight the claw to the digit's last bone.
- **Check:**
  - In a side close-up, the top edge is one continuous arc whose angle is within about 15 degrees of the photo's.
  - From the front, the claw is narrower than it is tall.
  - In a planted pose, the tip doesn't go through the ground and the pad carries the contact.

**Pincer arm** (emperor scorpion; *approved*) — elbowed out to the side, a round palm, two separate fingers about the
palm's length.

## Tails

**Low reptile tail with a crest** (crocodile; *approved*) — tapers continuously and lies on the ground; the serrated crest
is geometry (teeth on the midline), not paint.

**Brush tail** (fox; *approved*) — a few rings; the lag behind a walk can be baked with `lp bake-springs` (tested on the fox:
tail2 to tail4, stiffness 5, 13-19 degrees).

**Segmented arched tail** (emperor scorpion; *approved*) — beaded segments arching forward over the back, a bulb and a
hooked stinger.

**Fanned bird tail** (bald eagle; *approved*) — closed and narrow at rest, fanned by side bones in flight.

## Skins

Fur (fox), scutes and osteoderms (crocodile), chitin (scorpion), feathers (eagle): `references/skin-types.md` and
`references/texture.md`. Two rules learned on them: a dark animal keeps its relief by contrast inside each scale (lit tops
against near-black gaps), and every painted cell is at least about 6 texels across at its region's density.

## Joining parts (composite animals)

1. **Each part from its own references.** Measure the part against the real animal it comes from (`lp overlay` with that
   animal's photos, aligned on the part's own landmarks), then scale it to the new animal. A dragon's wing is measured on a
   bat's hand, not drawn.
2. **Scale with care.** A part scaled up keeps its shape but not its strength: a 10 m wing on a bat's proportions is far
   thinner than a heavy body needs. Write down which ratios are kept from the source and which are changed, and why.
3. **One skin.** Parts join by holes bridged into the body, as limbs do (SKILL.md §3); a part added as a separate shell
   reads as stuck on in motion.
4. **Each part keeps its rig pattern** (the wing's fold, the tail's chain, the jaw's hinge); the joins get blended weights
   so the skin stretches across them.
5. **Check every view after joining** (`lowpoly-core/references/measuring.md`, "After a big change"): each part against its
   references, and every join from every side.
6. **Budget:** add the parts' costs and say what was simplified; the head and the parts the camera looks at come first.
