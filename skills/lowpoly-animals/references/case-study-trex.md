# Case study: a Tyrannosaurus rex, a bipedal theropod

The second test of the skill, and a different kind of animal: two legs, a 12 m body, a head that is a fifth of the length,
and a mouth that must open. Its build script is not bundled with the plugin yet (see the README). It has been rebuilt over 22 rounds,
and each taught the skill something.

## What was built (the current version)

| Measure | Value |
|---|---|
| Unique vertices / corners / triangles | 563 / 753 / 938 (the first version had 226 / 244 / 448) |
| Bones | 38: 26, plus a bone for each of the four toes on both feet and the two fingers on both hands |
| Of those: the mouth cavity, jaws and nose / chin | about 50 vertices, 120 triangles |
| Of those: the 46 teeth | 184 vertices, 184 triangles |
| Texture | 1024 × 512; about 82 px/m on the body, 141 px/m on the head |
| Clips | idle with a roar, walk, attack (a lunge and bite), stand |
| Closed skin | every edge shared by exactly two triangles, teeth included |
| Soles | 30 vertices at y = 0: the heel pads and the toes' undersides |
| Seam colour jump, median / worst 10% | 0.03 / 0.132 (the measured models: 0.07-0.10 / 0.16-0.26); it was 0.037 / 0.120 before the scale paint of round 10 |
| Head brightness spread / range | 0.121 / 0.03-0.87 |
| Standing | the centre of mass (0.44-0.46 m ahead of the hip joint) inside the feet's ground contact in every standing clip (round 14) |
| Walk | matched to a reference walk: a 2.97 s cycle, each foot down 0.60 of it, the planted foot sliding 2.1 m (about 1.2 m/s); the swing foot carried with the toes folded down, the claws about 0.2 m up at the swing's peak; the body bobs 0.13 m, lowest at double support; the skin at the leg joint stretches 22% at most |

## Round 1: built from published numbers, fixed by eye

The first build used published bone lengths and proportions and no reference image. It passed every topology check and looked
like a lean raptor. The faults, fixed by eye:

| Seen | Fix |
|---|---|
| The head looked small and narrow | Deeper skull, wider cheeks, a broad blunt snout |
| The legs were thin sticks, most obviously from behind | A wider thigh, knee and shin, and a bigger three-toed foot |
| The body was narrow from the front | Wider hips and chest |
| The head was blurry on a 512-wide pelt | A 1024-wide pelt, with the head on its own, denser stretch |

## Round 2: the mouth and the brow

The first version painted the mouth as a thin strip of skin between the two jaw vertices, with the teeth as texture. It opened
when the jaw bone rotated, and it looked fine as an idea. Looked at closely in the viewer it looked painted on: the strip's
texture stretched into streaks, the teeth were flat, and there was no inside. The reviewer's point was that polygon simplicity
that suits a 0.4 m cat does not suit a 12 m animal whose head fills the screen, and that the mouth should be a hole with 3D
teeth.

| Seen | Fix |
|---|---|
| A stretched, flat strip for a mouth | Each head ring from the hinge forward split into an upper and a lower closed tube, the skin between the lips removed, a palate, a floor with a tongue ridge and a dark throat wall in between |
| Teeth as texture | 34 small closed pyramids along both lips, on the head and jaw bones |
| A flat brow with painted eyes | A 10-sided ring from the hinge forward: eye sockets pulled in, brow ridges pushed out, a flat nasal ridge |
| The mouth patch gave seam jumps of 0.18 median | The patch fades to the lip's skin colour at its edge; the pelt's painted lip line was removed; the nose and chin cap triangles that touch the inside use the mouth patch |

## Round 3: checked against a skeleton reference, and rebuilt from it

The reviewer then supplied a side view of a walking T. rex with its skeleton drawn over the body outline, and asked for the
skill to start from accurate bones and muscle. The reference was measured (the body outline's top line and underline at
stations, and the position of the joints) and the model's bind pose was laid over it with the same total length, nose and
ground aligned (`lib/lowpoly/tools/ref_overlay.py`). The model was wrong in ways no earlier check had found:

| Measured against the reference | Before | After |
|---|---|---|
| Hip joint, from the nose | 49% of the length (z 0.1), at the rear of the pelvis | 41% (z 1.1), under the middle of the pelvis; the reference's femoral head and the model's hip joint land within a few pixels |
| The head and the top of the skull | 0.3-0.55 m too high; the neck arched above the head | The back of the skull is the highest point, as in the reference |
| The neck and chest underline | 0.4-0.65 m too high: a neck about half as deep as the muscle makes it | A deep wedge, 1.2-1.4 m at the base, the throat line straight from the jaw to the chest |
| The mid-back | 0.1-0.14 m too low | Within 0.03 m; the back peaks at 3.77 m over the pelvis |
| The tail | 26-42% too deep at the middle, and level to the tip | The reference's depths, 0.4 m at the middle, drooping to 2.0 m at the tip |
| The feet | Under the rear of the pelvis, 1 m from where the reference's stand | Under the rear of the ribcage, 1.0-1.4 m ahead of the hip joint |
| The thigh | A thigh ring below the belly, though in the reference the thigh is inside the torso and the knee is above the belly line | The leg shows from the knee down, with the hole where the femur is. **Wrong, reversed in round 13:** the femur is inside the outline, its muscle is not |
| The arm | About 25% too long, and 0.6 m behind the reference's shoulder | 0.8 m, hanging from the reference's shoulder position |

After the rebuild the top line is within 0.03 m of the reference over most of the body (the mean difference is +0.06 m; the
worst, +0.24 m at the nose, is because the reference's head is pitched down about 28 degrees in its roaring stride), the
underline's rings are read off the reference and the overlay agrees, the ankle is about 0.1 m from the reference's, and the
head, neck and tail read as a T. rex's from every side.

What this showed:
- Proportions from numbers and a feel for the animal are not enough. The hip joint, the neck's depth and the head's height
  were each off by a measurable amount, and the model looked plausible anyway.
- The skeleton reference was worth more than any number of skin photos, because it showed where the joints are and where the
  muscle fills the outline.
- A reference in a different pose is still useful: the pelvis, ribcage, skull, shoulder, tail and the torso's outline do not
  change with the pose, and the bone lengths give the standing limbs.

## Round 4: the front and top views, and the muscle

The reviewer made the point that the skeleton drawing was only an example, and that the whole reference set has to be gathered
before anything else: the skeleton and the muscle, each in the side, front and top views. Two more references were supplied: a
front-view skeleton, and a top view of the skeleton with the tail's muscles (M. caudofemoralis and the others) drawn in, above a
side view with the same muscles. The model's widths had been the species' known proportions, never checked. The top view was
measured (the half-width at stations along the body, at 51.8 px/m so that its length matches the model's) and the model laid
over it; the front view, drawn in perspective with the head nearer the viewer, was used for ratios in one plane.

| Measured | Before | After |
|---|---|---|
| Ribcage and pelvis | 1.2-1.25 m wide, a quarter too narrow | 1.5-1.6 m, the top view's 1.65 m and the front view's ratios compromised (they disagreed) |
| The skull, from above | 1.0 m across the cheeks, 20% too wide; the snout 45% too wide at the nose | 0.82 m across the cheeks, 0.38 m at the nose |
| The neck, from above | 0.84 m at its base, 35% too wide | 0.62 m |
| The tail's root | 0.6 m wide at the rump, where the reference is 0.85 m (the caudofemoralis muscle) | 0.84 m, then the reference's taper: 0.22 m at 3.5 m, 0.05 m at 4.5 m |
| The tail from 3.5 m back | 30-80% too wide | The reference's widths |
| The feet | 0.52 m wide, 40% wider than the front view's ratio to the pelvis | 0.42 m, centred 0.38 m either side of the midline |
| The eyes | Painted on the flank, hidden from the front by the snout | In deeper, higher sockets on the forward-facing side of the head; still not visible in a straight front view |

What this showed:
- The earlier skeleton reference fixed the side view and left every width wrong. Each view answered different questions, and
  only the whole set did the job.
- Drawings disagree with each other (the ribcage's width differed by a fifth between the top and front views, because the
  front view is in perspective), so the disagreement is recorded and a choice made.
- The reference showed forward-facing eyes that the model's side-projected paint cannot show from the front. That led to a
  head-on eye patch in round 5, which round 6 reversed.

## Round 5: the head-on eye patch

The front reference shows both eyes facing forward. The model's eyes were painted in the side projection and were hidden from
the front. Adding a head-on patch took four tries:

| Try | What was seen | Fix |
|---|---|---|
| A head-on patch on the socket's faces | The socket's shadow ended in a hard rectangle, the iris was oversized, and the eyes were still hidden from the front | A smaller iris, and a shadow that fades out well inside the patch |
| The same, with the snout's corners lowered | Still hidden | A ray test along the view direction showed what blocked them: a skin triangle on the top-lateral slope, 0.2 m in front of the eye, which fell through the eye's height |
| The eye moved onto that slope, with the slope's faces and the socket's faces all in the patch | Both eyes showed from the front; from 3/4 a second, partial eye showed | Two surfaces projected to the same part of the patch |
| Only the slope's faces in the patch | Both eyes show once, from the front and from 3/4 | A dark hollow painted on the flank so the side view still reads as an eye socket |

The result: both eyes are visible from the front and at 3/4, in the viewer as well as in the posed renders; the skin is still
closed (666 triangles, unchanged). The trade-off: the eye is on a face that is edge-on from a pure side view, so the side view
shows a dark socket and no iris.

**A sharp edge round the eye.** The reviewer then pointed at a hard crease beside the eye in the viewer and suggested the slope
could have a slight angle instead of facing dead forward. The cause, measured as the angle between the two triangles' normals
across each edge: the brow's two edges folded 141 and 133 degrees, because the flank at the eye ring was 0.22 m inside the brow
(a ledge) and the slope fell away steeply above it. The fix changed only the head ring shapes: the flank came out to 80% of the
ring's width instead of 44%, the brow corners were lowered and pulled in a little, and the slope falls outward as well as
forward.

| Edge round the eye | Before | After |
|---|---|---|
| The sharpest crease | 141 degrees | 84 degrees |
| The second | 133 degrees | 73 degrees |
| Mean of the six sharpest | 78 degrees | 44 degrees |
| Sample points on the eye that reach the camera first | 5 of 5 | 5 of 5 |
| Seam colour jump, worst 10% | 0.266 | 0.246 |

The eye was still visible head-on, and straight on in the viewer both eyes showed under a smooth brow.

## Round 6: the eye goes back to where it belongs

The reviewer looked at the result in the viewer and pointed at the dark circle on the side of the head, the hollow that had been
left in the socket, and said the eyes should go there: the "super forward" eyes on the top slope looked like a painted sunglass
visor. They were right, and the head-on patch on the slope was the wrong design. It made the eyes visible from the front at
the price of putting them where no eye is.

| Seen | Fix |
|---|---|
| Eyes on the top slope read as a visor | The eye in the lateral socket, where the orbit is in the skeleton reference |
| Squeezed in the side projection | An oblique patch, projected from 55 degrees off the front, shared by both eyes |
| A dark hollow doubling as the socket | Removed; the patch paints the socket and the eye together |

The result: the eye reads as an eye from the side and at 3/4 (the angles a game camera uses), the skin is closed (666 triangles,
unchanged), the brow's sharpest edges stay at 84 and 73 degrees, and the seams are 0.064 median and 0.202 for the worst 10%.
Dead on from the front the eyes are only slivers at the sides of the head. The earlier statement that the eye must be visible
from the front was a mistake in what to optimise: a reference front view can show the eyes while the animal in life looks right
with them on the side.

## Round 7: a bright line along the lower jaw

The reviewer saw a bright green line along the lower jaw in the viewer. The flat-lit renders had never shown it. Nothing in the
texture was green, and no triangle's texel was, so the cause had to be in the lighting. Rendering the head with the viewer's
lights, smooth normals and bilinear texture (a new `lib/lowpoly/tools/lit_view.py`) reproduced a bright strip along the whole closed
mouth, and showed what it was:

| Cause | Fix |
|---|---|
| The lower lip's rim faces up, and was painted a pale pink gum; the preview of the time lit it at about 2.8 times its texel (a lighting error since fixed: the viewer itself renders it near its texel colour), so it read as clipping toward white | The gum, floor, tongue and palate in darker reds and browns, none over about 0.35 |
| A tongue ridge raised 0.1 of the head's depth above the lip line showed along the whole closed mouth as a glowing red strip | The ridge at the lip line's level or below: a closed mouth shows a dark gap |
| A flat, streaked band beside the eye, which the same render also showed: the patch's base colour was the skin sampled at one fixed z, so the scales' pattern varied only with height | The base colour is sampled at the point's true position, with its scales |

Seams improved as a side effect: 0.051 median and 0.131 for the worst 10% (from 0.064 and 0.202). The open mouth still looks
right, with darker reds, and the skin is closed (666 triangles). The reviewer's word for the colour was "green"; nothing in the
model is green, and the cause was found by reproducing the render, not by matching the description.

## Round 8: a bright sliver where the jaw meets the neck

The reviewer then found a thin, bright tan line across the lower jaw's side where the jaw meets the neck. Skinning was not the
cause: no triangle folded or stretched in any clip (the largest turn of a normal from its bind pose was 67 degrees, and only
on the mouth's own interior), and the posed triangles' shapes matched the bind pose's. The cause was in the bind pose. The ring
at the neck-head joint carried the thin mouth-line strip (its two lip vertices 0.06 of the depth apart) while the neck ring
behind it was tall, so the quad between them split into a sliver triangle (its longest edge 18 times its height, on the cheek at
z 4.0). Facing slightly up, it caught the sun as a bright diagonal.

| Seen | Fix |
|---|---|
| A sliver (aspect 18.5) on the cheek, behind the mouth's corner | The rings at the neck-head joint and the back of the skull got ordinary profiles, so the mouth line starts at the hinge ring |

Afterwards the thinnest visible triangles are a mouth corner (aspect 9-12) and the underside near the chin (7); the hidden throat
wall is the thinnest (18). Seams improved again to 0.037 median and 0.120 worst 10%, the skin is closed (666 triangles), and
the walk is unchanged. The search for it, `lib/lowpoly/tools/thin_triangles.py`, is a new tool.

## Round 9: feet with toes and claws

A foot study of the game's monster models (`lib/lowpoly/tools/foot_study.py`) found this animal's foot a flat rectangular slab:
- 9 vertices, no toes, splay 1.1, reach 0.1;
- where the clawed monsters build 3-4 toe wedges or claw spikes per foot (the drake's are 39 vertices on 6 bones).

**Rebuilt:**
- **The foot:** a sloping, splayed wedge (knuckle ring forward and lower than the heel, a 7-point sole).
- **The toes:** three forward toe wedges with claw tips (the middle one the longest) and a short first toe high on the
  inside. Each is a closed 6-vertex wedge on the foot bone, its base sunk in the foot, like the teeth.
- **Result:** 30 vertices per foot (7% of the model), 5 tips of which 3 are sharp claws, 17 ground contacts, footprint
  0.27 x 0.15 of the height.
- **Skin and walk:** the skin stays closed. The walk's roll now pivots on the middle claw, so the toes don't sink when the
  heel lifts (lift 8% of the height).

**The paint:** the foot patch now fades from the leg's colour over the height the knuckle ring spans. Its sides sit
lower on the wedge, and a fade sized for a box left a seam of 0.28 there. Seams: 0.051 median, 0.147 worst 10%.

## Round 10: refined against the later texture guidance

The animal was audited against the guidance added after it was built (the eye stack, the snout, the coat's layers, skin
types, the unrolled back) with the measuring tools, then repainted where it failed.

| Check | Before | After | Target |
|---|---|---|---|
| Skin type | scales as faint cells: crevices 1.2%, edges 4.2%, fine detail 0.039, gloss 0.5% | crevices 12.4%, edges 34%, fine detail 0.095, gloss 3.7% | the scale column of `skin-types.md`: 6-24%, 21-42%, 0.08-0.13, 2-20% |
| Eye | a bright yellow ring round a pupil; the one highlight blurred away (brightest 0.15) | the stack: catchlight 0.90, near-black eye body, a drawn lid line, a socket darker under the brow, a pocket at the front corner; no blur | §6, eyes |
| Snout | top as dark as the side (0.20 against 0.19-0.23); mouth line no darker than the lip; nostril a flat dot | top lit toward the tip (0.26 against 0.20); dark lines along both lips (0.05-0.07 under 0.22-0.26); a near-black nostril with a lit upper rim | §6, noses and muzzles |
| Unrolled back | already painted from the texture's own height | unchanged | §6, continuity |

**What was painted:**
- **Scales:** each scale is a pebbled cell with a deep crevice, its own value, lit on its upper side and shaded below, and a
  small soft gloss near its top on the upper body. The cells are larger along the back and smaller toward the face.
- **The leg scales:** got deeper crevices too.
- **The jaw:** shaded below the lip line.

**A seam problem on the way:** the first lip lines were painted exactly on the seam between the outer skin and the mouth's
own patch, and the seams jumped to 0.37 (worst 10%). Moved a few centimetres out onto the skin, they came back to 0.068
median and 0.147 worst 10%, the same worst figure as before the round. A high-contrast cell pattern makes every patch edge
show, so keep paint lines off seams.

**Not settled:** the snout's lit top is clear near the nose but measures level with the side further back. The head-render
measure also lights downward faces, so the chin reads lighter there than under the viewer's lights.

## Round 11: the toes on their own bones

The plugin's automated check (`lp check`, judging the foot as long-toed against the drake and the giant rat) warned that each foot
had one bone, where the drake's toes have six. On the foot bone alone, the toes moved as one rigid block: through the roll
they tipped up with the heel, pivoting on the middle claw's tip.

**What changed:**
- **Bones:** each toe and the spur on its own bone at its base, parented to the foot (8 new bones, 34 in all). Each toe
  wedge's base blends the foot and the toe half and half, so it bends at its root; the ridge's front and the claw ride the toe
  alone.
- **The roll:** it pivots on the middle toe's joint, not its claw. The forward toes undo the foot's pitch, so they stay
  flat on the ground while the heel rises 0.13 m before toe-off.
- **The swing:** the toes fold down by up to 0.30 rad (the claws 0.15 m below the toes' roots at mid-swing) and open
  again to land flat. The spur curls a little.

**What the curl cost:** at a first try of 0.55 rad, the 0.65 m middle toe dropped its claw about 0.33 m and the foot's
lowest point cleared the ground by only 0.015 m. With the curl at 0.30 rad the clearance was 0.08 m, so the swing's lift went
from 0.22 to 0.34 m. The foot now clears the ground by 0.20 m, 5% of the height. **A curl lowers the foot by the toe's
length times the curl's sine, so raise the swing to match.**

**A tool fix on the way:** the rig study took each toe that touches the ground for a separate limb, so it measured the leg
by its grounded toes and reported almost no lift. It now drops a limb that sits inside another limb's bones. The fox's and
the cat's numbers are unchanged.

**Still warned:** 5 tips (the tool counts the heel) and 17 ground contacts per foot, against the drake's 4 and 12.

## Round 12: the walk against a reference animation

**The reference:** a museum's published walk animation of one specimen at its estimated preferred walking speed. It is a
side view with a fixed camera, the animal walking in place. Twelve frames were taken over one cycle, and the model's
outline was drawn over each at the same phase, scaled to the same height, with the phase set by the best overlap of the
legs.

| | Reference | Before | After |
|---|---|---|---|
| Cycle | 2.97 s | 2.0 s | 2.97 s |
| Share of the cycle a foot is down | about 0.62 | 0.60 | 0.60 (it already matched) |
| Planted foot's travel; speed | about 2.1 m; about 1.2 m/s | 1.1 m; 0.9 m/s | 2.1 m; 1.2 m/s |
| Where the stance sits | the foot passes under the hip | 0.7 m ahead of the hip | centred 0.65 m further back |
| The swing foot | ankle raised, toes folded down and back, claws about 0.15 m up | foot lifted level, toes tipped up | ankle up to 1.27 m, toes folded down 0.60 rad, claws 0.13 m up |
| Body bob | about 3.5% of the height, lowest at double support | 1.9%, its phase unrelated to the steps | 3.5%, lowest at double support |
| Overlap of the legs' silhouettes | | 0.23 | 0.37 |

**Lessons:**
- **The timing was right, but the reach was half.** Footfall timing and the share of the cycle on the ground are what
  most walk tables give. A walk can match them and still shuffle: compare how far the feet spread at double support.
- **Centre the stance under the hip.** The bind pose's foot stood 0.7 m ahead of the hip, and the walk swung about it.
  A longer stride about that centre would have run out of leg. Centred under the hip, the leg stretches to 93% at most.
- **Long toes limit how far they can curl.** A 0.65 m toe folded by 0.85 rad put the claws on the ground at mid-swing;
  0.60 rad with the ankle 0.45 m up left 0.13 m. Start the curl late and open it early (sin squared), so the claws clear
  the ground at toe-off and landing.

## Round 13: the thigh, from the muscle rather than the bone

**What was wrong:** the person reviewing the model compared it with the reference animation. There the thigh is a lobe of its
own, with its front edge a crease running up the flank. It hangs below the belly and tapers to the knee. The model's leg left
the belly as a thin column. Round 3 had removed the thigh ring because the skeletal drawing put the femur inside the torso
outline. That reading was of the bone, not the muscle. The bear shows the same anatomy in its own way: its thigh and belly
practically touch for a stretch, a fold, before joining the torso.

**The reference, measured in the side view (scaled to the model):**
- the thigh about 1.5 m front to back at the belly, about 0.5 of the leg's length;
- its front crease near z = 1.95, rising up the flank to near the back;
- its back meeting the tail's underside near z = 0.4, at about 2.1 m;
- the knee about level with the belly (1.7 m) in mid-stance, lower when the leg is behind.

**What changed:**
- **Geometry:** two rings between the hip hole and the knee, 12 vertices and 24 triangles a side.
  - **The thigh lobe:** 6 points at 1.8-2.1 m, on the hips 0.35 and the femur 0.65. Its outer face sits a little outside the
    flank, its inner face close to the other thigh, and its back rises to the tail.
  - **A mid-thigh ring:** about two thirds of the lobe's depth, so the thigh tapers to the knee as one pillar. The first try
    went straight from the lobe to the knee. It read as a shelf under a rounder belly, with the same stick leg below.
  - **The knee:** a slightly smaller ring at 1.42 m.
- **Paint:**
  - the thigh painted in the flank's colour to its lower edge, not the belly's cream (in cream it read as more belly);
  - a dark fold along its front edge with a lit rim behind it;
  - a softer fold where its back meets the tail.

**Result:**
- **Leg overlap with the reference walk:** 0.37 before, 0.39 after.
- **In the viewer:** the legs read as drumsticks tapering to the knee from the front and three-quarter views, and the thighs
  bulge past the flank from behind.
- **Cost:** 481 vertices, 790 triangles. The surface stretched over 4:1 went from 6% to 9%, from the lobe's underside in the
  side-projected UVs.
- **The fold, modelled (a follow-up):** the painted fold alone was lost under the viewer's lights. The waist ring is the
  hip hole's front edge. Its lower flank vertices were pulled in to 70% of their width and raised 5 cm, and its upper flank to
  84%, with the ridge and spine left alone.
  - **Cost:** no new vertices.
  - **Angles:** the angle across the flank at that ring went from 5 to 22 degrees, and the fold's edges are 22-44 degrees,
    under the 90 where a crease turns into a hard line.
  - **Paint:** the painted fold was moved onto the groove.
  - **In the viewer:** a dark fold now runs down the flank between the rounded thigh and the belly.
  - **Checks:** seams 0.068 / 0.146, junction stretch over the walk 24%, leg overlap with the reference 0.39; `lp check`
    passes.

## Round 14: standing over the centre of mass

**What was wrong:** the person reviewing the model asked whether the feet stood where they should under the hip joints. They
did not. The standing clips (idle, attack, stand) used the bind pose's legs, whose feet are well ahead of the hip. Measured:
- **Centre of mass** (uniform density, from the closed skin): 0.46 m ahead of the hip joint, at z = 1.56 m.
- **Ground contact:** z = 1.87-2.95 m, starting 0.31 m ahead of the centre of mass. The animal would tip backward.
- **The walk:** already centred its stance near the centre of mass (round 12), so only the standing clips were wrong.
- **The reference:** at mid-stance, its planted foot spans about z = 1.33-2.18 m (scaled to the model), around the centre of mass.

**What changed:**
- **The feet:** the standing clips move each foot 0.75 m back with the walk's IK, level, giving a ground contact of
  z = 1.12-2.20 m around a centre of mass at 1.54 m.
- **The attack:** its lunge pitches the hips, which lifted the planted claws, so the thighs now undo the hips' rotation. The
  feet rise at most 2 cm during the lunge.

**Not changed:** the bind pose keeps the feet forward. It is only seen while modelling, and the geometry, UVs and weights
depend on it.

## Round 15: the thigh's mass at mid-leg, seen from the front

**What was wrong:** the person reviewing the model compared it with the reference from the front. The leg's mass sat at the
bottom of the torso, where it should be concentrated in the middle. Measured as the outline's half-width at each height over
the hips:

| Height | 1.5 m | 1.8 m | 2.1 m | 2.4 m | 2.7 m | 3.0 m |
|---|---|---|---|---|---|---|
| Before | 0.70 | **0.84** (widest) | 0.77 | 0.74 (narrowest) | 0.77 | 0.79 |
| After | 0.64 | 0.74 | 0.84 | **0.91** (widest) | 0.87 | 0.82 |

The thigh lobe of round 13 had its outer points under the belly line, so it bulged out there, and nothing bulged where the
thigh's muscle is fullest.

**What changed:**
- **The bulge, moved up:** the lower-flank vertices of the two rings over the hip joint (the hip hole's outer edge, already
  half on the femur) moved out to 0.90-0.92 m and up 6 cm.
- **Below it, brought in:** the thigh lobe's outer points to 0.72-0.74 m, the mid-thigh ring's to 0.63-0.65 m, and the knee
  narrowed to about square.
- **The thigh's front:** the lobe and mid-thigh rings each had one front vertex far ahead of their outer and inner points,
  which made a ridge down the front of the thigh (96-105 degrees between its faces). Their outer and inner front points moved
  forward to blunt it (now 67 degrees).
- **The back of the thigh:** the mid-thigh ring's back eases into the fold behind the knee (now 89 degrees).
- **Slivers:** the sliver pass (`mesh_tidy.py`) runs on the hind leg's rings, which also removed an 11.9 sliver on the inside
  of the thigh.

**Unchanged:** the 4-sided knee and shin rings still crease at about 100 degrees where they meet, as they did before; that
is the shape of a 4-sided limb.

**Checks:** `lp check` passes; seams 0.068 / 0.139; the skin at the leg joint stretches 22% at most over the walk; leg
overlap with the reference walk 0.39; balance 0.72. In the viewer, from the front, the hips bulge at mid-height and taper
into the knees.

## Round 16: one leg's inner thigh streaked

**What was wrong:** the person reviewing the model saw texture stretching on one hind leg's inner thigh, and not on the
other. The legs' shapes were mirror images, but 12-13 of each leg's 35 triangles had different diagonals: the ring-to-ring
stitch sorts each ring by angle, and mirrored rings sort differently. Both legs share one mirrored pelt, so the leg whose
triangles differed from the painted ones sampled the texture smeared.

**The fix:** the right leg's triangles are mirrored onto the left (`mesh_tidy.mirror_better_side`, the same step that matches
the ears).
- **The first try** left 3 open edges: one triangle on the left leg touched the belly's midline vertex, and the region that
  was mirrored left that triangle out on one side only. A face that touches the midline now belongs to the side its other
  corners are on.
- **Result:** 35 triangles on each leg, none different; the skin is closed; `lp check` passes as before (seams 0.068 /
  0.139); 790 triangles.

**Not checked by the measurement:** that the streak is gone from the same viewing angle. The person reviewing it confirms
that in the viewer.

## Round 17: the inner thighs tucked into the torso

**What was wrong:** after round 16 the streaks were on both inner thighs, so the mismatched triangles had not been their
cause. Seen from below, the inner thigh was a wide flat panel running from the thigh ring straight to the belly's midline.
The belly between the legs (the pubic region, 1.70-1.97 m) hung as low as the thighs' inner edges (1.80-1.92 m), so there was
nothing for the thigh to tuck into. A flat panel facing forward and down also takes the side-projected texture as streaks.

**Tried and dropped:**
- **Texture patches** for the legs' forward- and down-facing faces, painted with the pattern in their own plane: they made a
  seam all round the patch, and seams failed the check (median 0.107).
- **A crease ring** between the hip hole and the thigh lobe, its inner points tucked up: the thigh lobe's inner edge is
  closer to the midline and reaches further forward and back than the hole, so any ring between them folds back on itself
  (edges of 155-176 degrees). Stitching it also showed a flaw in the angle-sorting bridge: when the second ring sits up and to
  the side of the first, it misorders the first ring's vertices and leaves holes. Rings with one vertex per vertex are now
  stitched in order.

**What worked:** the three groin vertices on the midline went up (to 2.02, 1.88 and 1.80 m), and the thighs' inner edges
down a little (to 1.72-1.84 m). Each inner thigh now rises into a recess between the legs. In the rear and underside views,
the flat tent from thigh to midline is gone.
- **Cost:** no new vertices; still 790 triangles.
- **The crease along the groin:** at most 91 degrees.
- **Checks:** both legs have identical triangles, the skin is closed, `lp check` passes (seams 0.068 / 0.148), and the
  standing balance (0.72), the walk (22% stretch, leg overlap 0.39) and the front-view width profile are unchanged.
- **Confirmed:** the person reviewing the model checked the underside in the viewer and it looks right.
- **Not changed:** the thighs' front and underside faces still take the side projection. With the panel gone they are smaller,
  but up close the pattern still runs across them.

## Round 18: the jaws rebuilt from the anatomy

**What was wrong:** the lower jaw was smooth and ran into the neck, so the animal read as a small, slender theropod. The
head was one loft with one ring profile from the hinge forward, and four faults followed from it:
- the mouth line sat at the same fraction of every ring's depth, so the lower jaw was a constant 33% of the head's depth
  and the corner sat low and far back, at the hinge;
- the jaw's section was a V (two lips and a chin), with no sides and no lower edge;
- the jaw's underside was the neck loft's underside, with no back corner;
- the teeth were evenly spaced, the same top and bottom, and both rows showed.

**The references:**
- **Teeth:** per side 4 premaxillary, 12 maxillary and 13-14 dentary teeth, the front maxillary crowns the largest (Smith
  2005, citing Osborn 1912); always 4 premaxillary (Miyashita et al. 2010).
- **The lower jaw:** deepened at the back, for an enlarged jaw-muscle chamber.
- **Lips:** whether the teeth were covered is debated (Cullen et al. 2023). The reference animation shows the upper teeth and
  hides the lower, and the model follows it.
- **Measured on the animation:** the lower jaw under 10% of the head's depth at the chin and 46% at the back; the corner about
  half the depth down, just under the eye.

**What changed:**
- **Rings:** a 12-vertex head ring, with a margin vertex for the jaw's lower edge on each side.
- **The mouth line:** shaped ring by ring, its corner under the eye, with a closed cheek ring behind it, half on the jaw bone.
- **The jaw against the neck:** the throat tucked above and inside the jaw's back corner; the lower jaw narrower than the upper.
- **Teeth:** 4 small premaxillary and 9 maxillary teeth hanging from the upper lip's outer edge, and 10 smaller lower teeth
  inside.
- **Paint:** folds along the jaw's edge and its back border, and no painted lip lines. The mouth patch's floor is measured
  against the narrower lower lip, and its edge fades to the skin's real colour.

## Round 19: the head's proportions and section

| Seen | Cause | Fix |
|---|---|---|
| A long, pointed snout | The eye 1.32 m behind the tip (79% of the head); the reference has it about 0.88 m back (62%) | Every position ahead of the eye (rings, nose, teeth, paint) goes through one mapping that shortens it to 0.60 |
| The chin far behind the nose | The nose's cap reached 0.14 m forward | Both caps short and at the lips: the chin 0.11 m behind the nose, the front closed |
| From the front, round: as wide at the brow as at the teeth | The snout's upper sides stood upright | A trapezoid: the brow and upper flanks pulled in, the snout widest at the upper tooth row |
| A jagged jaw corner from above and behind | Too large a step from the jaw's corner to the neck | A smaller step: the jaw's back margin in, the throat less tucked |
| The jaw tapering to a thin edge at the chin | Its lower edge rose toward the front | The edge almost level (2.68-2.72 m), a squared chin |
| A collapsed front tooth | A tilted ring's rim ended short of the ring | Each tooth clamped inside its rim |

## Round 20: the jaw into the throat, the widest point and the overlap

- **A sheer drop from the jaw's corner down the throat,** seen from below and in front.
  - **Cause:** the neck rings tilted with the neck's steep rise, so their lower halves slid forward. The joint ring's throat
    vertex sat 3 cm *ahead* of the skull ring's, under the jaw, and the throat folded back on itself.
  - **Fix:** the neck and skull-back rings stand upright. The skull ring's lower flank sits just above and inside the jaw's
    corner, and the jaw's rear margin rises a little, so the underside curves up into the throat.
- **The head widest just behind the eye, and the lower jaw a flat box.**
  - **The references:** the skull is 0.53-0.66 as wide as it is long (Gignac & Erickson 2017), the width from a region
    behind the eyes widened for the jaw muscles (Molnar 1991).
  - **Fix:** the skull's back ring is now the widest (0.50 m half-width), then the cheek (0.48), the eye ring (0.41) and the
    snout. Each lower-jaw margin vertex moved in and up, so the jaw is round in section.
- **Too little overlap.** The upper lip now hangs below the lower lip along the tooth row, outside it: 3 cm at the nose,
  12 cm mid-row, none at the corner, as the person reviewing it drew it. The palate's edge sits over the lower lip, and a
  painted fold carries the lip line up and back over the cheek.

**Checks:**
- **Counts:** 535 vertices, 598 corners, 850 triangles.
- **`lp check`:** passes (seams 0.056 / 0.140, standing balance 0.71), with no thin triangles in the head. The eye patch moved
  two texels, so the spec's eye position was updated.
- **Open:** the jaw was looked at mid-bite, from the side.
- **Confirmed:** the person reviewing the model checked the head in the viewer and it looks right.
- **Not verified:** the jaw's widths come from published skull ratios, not a measured top view of a skull. The lower jaw
  keeps 10 teeth per side against the real 13-14.

## Round 21: the snout's front, the arms' joins, and the two sides alike

- **The snout's front was streaked.**
  - **Cause:** the nose's and chin's caps face forward but took the side projection, so each texel column was smeared
    across them in bands.
  - **Fix:** they get a front-projected patch (u = |x|, v = height), painted from the side pelt unrolled round the front.
    The bands are gone, and the seams are unchanged (0.059 / 0.187).
- **The arms' joins didn't read.**
  - **Cause:** each arm went straight from its hole in the chest to the elbow ring, as one tent of skin from the brisket.
  - **Fix:** a shoulder ring at the joint, the arm's widest part, bulging a little past the chest's side, gives the root a
    crease. Cost: 8 vertices and 16 triangles (543 / 866).
- **One side of the chest had a long triangle between the arms.**
  - **Cause:** the angle-sorted stitch gave the two shoulders different diagonals. The hind legs had been mirrored in
    round 16; the arms had not.
  - **Fix:** the better side's triangles are mirrored over, for the arms and the chest round them. The region stops short of
    the neck, where the loft's own diagonals don't mirror.
- **Still open:** a pink strip between the lips from the front, and a thin triangle (12.5) at the chin's cap.

## Round 22: clawed feet and hands, built like the drake's, shaped from the anatomy

**The study:** the drake's claws are welded into its skin, each with a root on the foot, a ring and a tip on its own bone,
and all of them share one painted claw strip (`references/feet.md`, "Claws and toes as part of the skin").

**What changed, in four steps:**
1. **Separate toe wedges replaced by welded toes.** The first try rooted each toe on a whole face of the foot box, so the
   toes read as spikes as wide as the foot's faces, and the spur sat on the sole. Inset roots made them digits.
2. **The foot rebuilt from the anatomy.**
   - **Shape:** a block over a broad heel pad. Toes II, III and IV grow from the block's front quads, III the longest. The
     first toe sits high on the inside back of the metatarsus.
   - **Proportions:** the track's proportions (Tyrannosauripus: about 0.96 m long and two thirds as wide, tapering toes, a
     large heel pad, a slender first toe facing inward).
3. **Scaled to this animal.** The reference animation's planted foot is 0.78-0.80 m long. The foot built to the track was
   0.97 m, 21% too long. From below, its toes were parallel blocks on a square pad, like a hand.
   - **Now:** the footprint is 0.79 m long and 0.60 as wide as it is long, with a rounded heel pad and side toes splayed
     from it.
   - **The first toe:** about 0.4 m up the back, pointing back (0.3 m in the reference).
4. **The hands:** two fingers where the stub was, the longer second finger outside. Each has its own bone, and they sit side
   by side on the wrist's split ring.

**The paint:**
- **The foot:** painted as the leg continuing down. Before, its own lighter palette made a step at the ankle.
- **The fingers:** their own row of the claw strip, with the arm's skin. They had shared the toes' row and turned dark when
  the toes did.
- **A trap in the viewer:** the viewer caches textures by name, so reloading only the model kept the old texture, and the
  claws showed no paint at all until the texture was reloaded too.

**Checks:**
- **`lp check`:** passes, with the skin closed. Seams are 0.03 / 0.132 (0.059 / 0.187 before), and standing balance is 0.88.
- **Per foot:** 39 positions, 68 triangles and 5 bones; the model has 563 positions, 938 triangles and 38 bones.
- **Warnings:** toe reach is 1.3 ankle depths (the measured range is 2-8.5; the foot follows the reference's length).
- **Confirmed:** the person reviewing the model checked the feet and hands in the viewer.
- **Not done:** the claws are straight cones, the fingers have no clip of their own, and the angle between the toes is set
  from the track's width ratio rather than a measured spread.

## What was not verified

- **The front view's widths:** the front drawing is in perspective and stylised, so only its ratios were used.
- **The walk:** compared with one reference animation (round 12), a reconstruction rather than footage of a living animal, in one view. The tail's motion could not be separated into side-to-side and up-and-down from that view.
- **The eyes from straight on:** only slivers show (see round 6), a choice rather than a fix.
- **The head's pitch:** the reference's head is pitched down in a stride, so the neutral pitch (about 10 degrees) is a choice.
- Looked at in the viewer, in bind-pose silhouettes and by overlay; the model is not reviewed by an anatomist.

## What worked first time

- **The leg holes.** A hole three rings long, as on the cat, joined the body without a notch.
- **The two-density pelt** (skill §6).
- **The planted-foot IK** from the quadrupeds, with two feet half a cycle apart.
