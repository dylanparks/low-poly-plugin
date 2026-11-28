# Heads: the muzzle against the eyes, ears, and very large heads

The detail behind SKILL.md §5. Read it for any head.

**Eyes against the snout (measured on the dog and bear).** In both, the eyes sit on brow-level faces **behind and
above** a distinct muzzle block, never on it:
- **Dog:** the eyes sit behind a visible stop. In front of the stop is a narrower muzzle block with its own paint: a
  lighter muzzle, a mouth line and a dark nose tip.
- **Bear:** small eyes sit at the brow-muzzle junction under a dark brow. In front of them a protruding muzzle block is
  painted lighter, with fur running along it to a black nose.
- **On both:** nothing painted for the eyes repeats on the muzzle.

Two rules follow:
- **Geometry: in the front view the muzzle's outline must pass below and between the eyes.**
  - Build the muzzle rings as a block: broad and low at the sides (a cat's whisker pads, a dog's lips), with a narrow
    bridge on top rising between the eyes.
  - The failure case is a muzzle ring as wide and as tall as the face ring. Its upper sides then sit at the eyes' own
    (x, y), so in the front view the muzzle covers the eyes, and a single front projection paints a second pair of
    eyes on the snout.
- **Texture: a muzzle gets its own head-on patch, separate from the eyes.**
  - The face patch holds only the eye band: the triangles from the eye ring to the muzzle's first ring.
  - Triangles wholly on the muzzle rings take a second front-projected patch, painted by the same painter with the
    eyes switched off. Give it the same pixel density as the face patch.
  - Pick the triangles **by ring, not by z.** The head rings tilt with the head, so one ring's vertices spread over
    several millimetres of z, and a z threshold misfiles them.
  - Fade both patches to the side pelt that is actually next to their edge. Beside the eyes that is the face plane;
    beside the muzzle it is the muzzle's own side, often a different colour (a mask, a lighter muzzle). Use one fade
    function for both patches, so their shared edge matches.
- **Checking it:**
  - Render the head textured, front and 3/4, with a second copy where each triangle is tinted by its UV patch
    (`lib/lowpoly/tools/head_textured.py`). Each eye should appear exactly once per side.
  - Count texels that two places on the same side of the head both map to (`lib/lowpoly/tools/uv_reuse.py`): there should be
    none. The measured models reuse texels on purpose for repeated parts (its dog's paws share one), so reuse matters only for unique
    features like eyes.

**Ears (measured on the dog, deer, bear and mule).** Every measured ear is closed into the head skin: no open edges and
no loose cards. Each one shares 5–9 vertices with the head. There are two ways to build them:

| | Peak of the head skin | Its own part, on its own bones |
|---|---|---|
| Used by | dog (pointed), bear (rounded tab) | deer (large cupped leaf), mule (tall narrow pyramid) |
| Geometry | 2–6 tip vertices pulled up out of the skull's top corners; 3–7 triangles per ear | a small closed shell or pyramid: 7–10 vertices, 7–11 triangles per ear |
| Bones | the head bone only (the ears can't move) | one bone per ear (mule) or a two-bone chain (deer: base and tip bones, vertices on the base bone); the base vertices stay 100% head or blend head and ear |

**Large thin ears are cupped shells, not pyramids** (bats, and any ear taller than about half the head). An ear is a thin
sheet of skin with a crescent cross-section: cupped in front, convex behind, thin at the rim, thick only at its base. A base
quad, a flared ring and a tip make a symmetric double pyramid with a square cross-section, which reads as a gem; the hostile
giant bat's first ears did. Build it instead:
- **Rows:** the 4 skull vertices as the base; a middle row at about 40% of the height (inner and outer rim at the widest
  point, a cup vertex set back behind the line between the rims by 15-20% of the width, and a back vertex just behind it, so
  the shell is about a tenth of the width thick); an upper row at about 75% (two rims and one recessed point); the tip.
  About 8-10 vertices of its own and 14-18 triangles, closed.
- **The opening faces where the animal listens:** a predator's forward and out (30-45 degrees off straight ahead), a prey
  animal's more to the side. A bat's tragus is a 1-vertex spike inside the cup's base.
- **Paint:** the cup dark, a thin paler rim on both edges, the back in coat.
- **Check:** from the side the ear is a thin leaf with a visible hollow; from the front, a cup.

**Size and placement:**

| | Dog | Bear | Deer | Mule |
|---|---|---|---|---|
| Height, as a fraction of head length | 0.26 | 0.23 | 0.44 | 0.51 |
| Base width, as a fraction of head width | 0.33 | 0.32 | 0.27 | 0.20 |
| Tilt | 28° out, 30° forward | 14° out, 19° forward | 38° out, 26° back | 15° out, 26° forward |

- **Where they sit:** at the back-top corner of the skull, 0.8–1.0 head widths behind the nose tip and 35–61% of the
  half-width out from the midline.
- **Bases sunk into the skull:** the bases sit 2–4 cm below the skull's top line. The ears grow out of the upper
  sides and corners of the skull, and are not perched on its top.

**The head shape round the ears:** the skull is squared off at the back. It is flat-topped between the ears, and widest
at the ear and eye level. The ear bases are its top corners. A bear's head is a box with the ears on its top corners; a
dog's skull is flat between two pyramids. With a round or tapering skull, the ears have nothing to stand on.

**Ear texture:**
- **Front (the opening):** it gets **its own small patch**, with 0–10% of its pixels shared with the rest of the head.
  It is painted as a dark almond or teardrop (the inside of the ear), with a lighter rim of fur: dog, mule, deer. The
  bear's small furry tabs have no opening drawn, only fur.
- **Back:** plain coat, often reusing the head or neck fur (the dog and mule backs are thin slivers of it). The deer
  gives its large ears a separate back patch.
- **Density:** 0.75–1.1 times the head's pixel density.
- **Contrast:** brightness spread 0.08–0.15, range down to 0.0–0.1 (the inside of the ear) and up to 0.56–0.73.
- **Front against back:** the front is darker than the back (dog, mule, deer); the bear's two sides match.

**The opening: take it from front-on and side photos of the species.** For a cat, for example:
- **Shape:** the ear is a broad triangle with its base about as wide as it is tall. Its outer edge continues the side
  of the head.
- **The opening:** a broad triangle, widest at the base, filling only the lower 60–70% of the ear's front. The tip and
  a rim of fur on both edges stay coat-coloured.
- **The dark recess:** small, low and toward the inside.

A long narrow opening running up to the tip reads as a slit and makes the ear look too long.

**Checking it in code:**
- Measure each ear's open edges (0), the vertices it shares with the head (5 or more), and its height against head
  length.
- Render close-up side, front and top views of the head with the ear triangles tinted, to judge how they sit
  (`lib/lowpoly/tools/head_views.py`, `lib/lowpoly/tools/ear_study.py`).
- A two-triangle card perched on a round skull reads as a blade from the side.

**A cat's head: what makes it read as a cat (from the flame point's rebuild).** After five rounds of patches a cat's head
read as a reptile; rebuilt from the references it read as a cat at a glance. The must-haves, each measured on the photos:
- **A short muzzle with a stop.** Eye to nose tip about 0.30-0.34 of the head's length, and a clear break where the
  forehead meets the bridge (the rebuilt head: forehead 57 degrees, bridge 34, a 23-degree stop at eye level).
- **Cheekbones widest at or just below the eyes,** the head 1.1-1.2 times as wide as tall from the front. From the front
  the lower face is lobes, not one oval: a rounded cheek at about nose level, stepping in at a jaw corner under the
  whisker pad, then a small rounded chin set back from the pads.
- **Rounded whisker pads** either side of a small leather nose, the mouth a W under them with a notch at the philtrum.
- **A flat face plane for forward eyes** (§5, the forward-facing face), the eyes about 0.36 of the head's width apart and
  a fifth to a quarter of it wide, painted head-on, never stretched along the sides.
- **Wide-based triangular ears** (base about a third of the head's width) on the skull's top corners, the openings forward.
- **The reptile failure** is the absence of these: no stop, a long tapering snout, eyes on the sides, spike ears, no
  cheeks, pads or chin. Each round of that build passed its checks; it was caught by eye, beside the photos.

**Jaws and mouths: build each jaw from its bones and muscles (built on the 12 m test animal).** Needed for any mouth
that opens; a mouth painted as a line on a small animal needs only the outline checks at the end. The test animal's first
jaw used one ring profile for the whole head: the lower jaw was a constant third of the head's depth, the mouth line ran
level to the hinge, the jaw's section was a V and its underside ran straight into the neck. It read as a small, slender
theropod, not the species (`case-study-trex.md`, rounds 18-20). Anatomy first, then simplify around it.

*Measure first,* from the skull and muscle references in the side, front and top views and the species' dental formula:
- **The head's landmarks:** the eye's position along the head, the snout's depth at its front, and where the chin sits
  against the nose. Fix these before the jaw: a snout a third too long reads as the wrong animal whatever the jaw does.
- **The lower jaw:** its depth at the chin, the middle and the back, and its lower edge's height along the head.
- **The mouth line:** its height at each ring, and its corner.
- **Widths, ring by ring:** at the brow, the flank, the tooth row and the jaw's edge, and where the head is widest.
- **The teeth:** counts per jaw region, the size gradient, which teeth show with the mouth closed, and which jaw overlaps.

*Build:*
- **The lower jaw has its own sides and edge.** Give each jaw ring a margin vertex on each side for the jaw's lower edge,
  so the jaw has upright sides. Where a throat lies between the jaw halves (reptiles, dinosaurs, many mammals), the
  midline sits a little above the margins. Put each margin vertex on the curve between the midline and the lip, not level
  with the midline, or the jaw reads as a box from the front and below.
- **The lower jaw keeps its depth.** Most jaws don't taper to a blade at the chin: the dentary keeps a fairly even depth
  and ends in a squared chin. It is deeper at the back only where the jaw muscles attach and the mouth line rises.
- **The mouth line follows the species.**
  - Its corner is just under or behind the eye on theropods, crocodilians and lizards, far back on a dog, short on a
    herbivore.
  - Between the corner and the jaw joint the cheek closes over the jaw muscles. Half of it goes on the jaw bone, so it
    stretches when the mouth opens.
  - The cavity starts at the corner, not at the joint.
- **The widest point is where the skeleton and the muscle put it.** Read it from a top view of the skull and the jaw
  muscles. In predators with big bites the jaw-closing muscles widen the back of the skull over the jaw joints: a
  T. rex skull is 0.53-0.66 as wide as it is long, the width coming from the region behind the eyes. So the head is widest
  behind the eye and narrows from there to the nose. From the front, such a snout is a trapezoid: narrow on top, widest
  at the upper tooth row, the lower jaw tucked in under it.
- **Which jaw overlaps decides which teeth show.**
  - **Upper teeth outside the lower jaw** (theropods, most mammals' canines and incisors): make the lower jaw narrower,
    and hang the upper lip below the lower lip along the tooth row, outside it. Overlap most in the middle of the row,
    less at the nose, none at the corner. The upper teeth hang from the lip's outer edge. Seat the palate's edge right
    over the lower lip, so the jaws don't cross, and carry the lip line on up and back past the corner as a painted fold
    over the cheek.
  - **Rows interlocking in plain view** (crocodilians): keep the jaws the same width.
- **Teeth from the dental formula.** The visible row keeps its count, spacing and the longest tooth's position; a low-poly
  row can drop teeth that never show. A T. rex has 4 premaxillary, 12 maxillary and 13-14 dentary teeth per side; the test
  model shows 4 small premaxillary teeth close-set at the tip and 9 maxillary teeth, longest at the third and fourth, and
  keeps a smaller lower row inside, hidden when the mouth is closed. Clamp each tooth inside its lip's rim: a tilted ring's
  rim can end short of the ring's position, and a tooth placed past it collapses.
- **Close the front.** Bring the lips together at the nose and the chin, so the mouth's inside doesn't show from the front
  with the jaw closed.
- **Separate the jaw from the neck.** The throat sits a little above and inside the jaw's back corner, the jaw is a little
  wider than the neck right behind it, and a painted fold runs from the mouth's corner to the jaw's angle. A continuous
  underline from the chin to the chest makes the jaw read as throat.
- **Let the jaw's corner curve into the throat.**
  - Keep the step between the jaw's back corner and the ring behind it small, so the corner reads as a rounded angle.
  - Keep the rings in order where the neck climbs. A ring tilted square to a steep loft slides its lower half forward, so
    under a raised head the throat's vertices end up under or ahead of the jaw, and the skin folds into a sheer drop.
  - Check that each ring's lowest vertex is behind the next ring's, and stand the rings upright where it isn't.

*Check it* against the references, in code where you can:
- **Side:** the lower jaw's edge and depth at the chin, middle and back; the corner; the overlap; which teeth show and
  which is longest.
- **Front:** the trapezoid, the overlap and a closed front. **Top:** the widest point.
- **From below and in front, and from above and behind:** the jaw's corner running into the throat.
- **Open,** in the attack clip, from the front and the side: the jaws part without crossing (`lib/lowpoly/tools/lit_view.py`, then the
  viewer).
- **The gape, in numbers,** in every clip: `lib/lowpoly/tools/jaw_study.py` (the angle at the hinge between the upper lip's
  front and the chin, the lip gap, the snout's pitch at the widest, and whether the teeth are modelled or painted).

**Era context: the reference game's painted snarl** (not a standard; the reference game's wolf, 248 vertices, re-measured
2026-11-26 with `jaw_study.py`; numbers in `reference-measurements.md`, "Jaws and mouths"). This is how the one shipped
model with a mouth that opens is built. It is not the rest of this section: those rules come from this plugin's own builds
(the 12 m T. rex, the Kodiak, the gorilla), which are larger or hero builds seen closer.
- **The jaw is a small wedge:** 8 vertices and 8 triangles on its own bone (16% of the head's 49), a V from the two mouth
  corners to a chin point, the same width as the upper lip at the front: the rows face the camera rather than overlapping.
- **No cavity:** the upper and lower lip rims are left as open edges (8 of them, the model's only ones). Nothing closes the
  mouth behind the teeth; the gap reads dark.
- **The teeth are painted,** on 12 triangles that face forward and down: 7 under the snout (upper row, head bone) and 5 on
  the jaw's front (lower row, jaw bone), from one 68 x 44 texel strip of gums and white teeth on near-black.
- **Never fully shut:** 7 degrees and a 2.7 cm lip gap (2.6% of the height) in the bind pose and every moving clip, so the
  painted teeth always show.
- **The corner** is 3-5 cm ahead of the hinge; the upper lip 0.19 m ahead of it.
- **Not the default for a hostile mob.** Copied onto a medium-tier mountain lion (2026-11-26), painted teeth behind a short
  opening read from the game camera as a pink slit; the wolf's own teeth face the camera on its snout's underside and its
  mouth is held open in every pose, which the lion's closed cavity did not give them. A hostile mob gets a modelled row at
  every tier (`lowpoly-core/references/temperament.md`, "Which to build"): about 8 pyramids, 32 vertices, at the medium
  tier. How far a jaw opens comes from the species' anatomy (`lowpoly-core/references/temperament.md`, "Open the jaw wide").
- **The motion that goes with it** (snapping bites with the head up) is in
  `lowpoly-core/references/temperament.md`, "Open the jaw wide".

**A very large head (built on the 12 m test animal).** When the camera fills the screen with the head, the simple forms
that suit a small animal look painted on. Build as geometry what the camera can see into or around.

*The mouth: build the hole, not a stretched strip.* A thin strip of skin between two jaw vertices, painted with teeth and
stretched open by a jaw bone, looked painted on: the texture streaked and the teeth were flat.
- **Two jaws.** From the jaw hinge forward, split each head ring along the mouth line into an upper loop and a lower loop.
  Each is a closed tube: the outer skin, the lip rim turning inward, and the palate (upper) or the floor (lower). Each ends
  in its own nose or chin point. Remove the strip of skin between the two lips.
- **Start the mouth line only where the mouth does.** The rings behind the mouth's corner have ordinary profiles, with no
  thin strip between the lips. A thin strip running back into a tall neck ring makes a sliver triangle (on the test animal
  its longest edge was 18 times its height), which catches the light as a bright diagonal across the cheek. Keep visible
  triangles under an aspect of about 10 (`lib/lowpoly/tools/thin_triangles.py`).
- **The cavity.** Close it at the hinge ring with a dark throat wall, and close the two mouth corners. The tongue is the
  floor's middle vertex, at or below the lip line: closed, the lips nearly touch and only a dark gap shows.
- **The lower jaw: three profiles, from the mandible.**
  - **Front:** the two halves meet at the midline, so the chin narrows to a rounded U: narrow (about the nose pad's width)
    with a rounded underside of two or three vertices. A flat quad reads as sliced off; a single midline spike reads as a
    beak (the hostile giant bat's first and second jaws).
  - **Side:** the lower edge is ONE smooth, gently convex curve: down and back from a rounded chin, then rising gradually
    into the throat. A straight underside parallel to the skull's top makes the head a box; a jaw angle modelled as a
    dropped vertex, or sides flared out below the lip, make triangular bumps (both happened on the hostile giant bat, and
    the reviewer redrew the line as one curve). At low poly, set the lower-edge vertices' heights from one spline, with
    smooth normals along it.
  - **Below and from the front:** one shallow U from corner to corner of the mouth through the chin's bottom, with no
    facets sticking out.
  - **Measure it** on a side view of the skull with its jaw (`lp overlay`, aligned on the nose and the hinge): the chin's
    front and lowest point, the ramus's lowest point and the jaw angle.
- **Build the formula's whole visible row, not the canines alone.** The Kodiak shipped four canines and nothing else (a
  temperament note said "canines first") and read as a mouth missing teeth; the gorilla's first round did the same until
  its third added incisor blocks and cheek-tooth blocks. A bear (I 3/3, C 1/1, P 4/4, M 2/3) shows, per jaw: the I1-I2 pair
  and I3 a side, the canines (the lower in front of the upper), a gap, and a long low row of cheek teeth: 12 pyramids beside
  the canines, 48 vertices. Paint each tooth's gum colour at its root, not in a band at one height.
- **Teeth: small closed pyramids** (4 vertices, 4 triangles, as simple as the measured dog and cow ears, only many more; this
  plugin's standard for a head seen close, not the measured wolf's, whose teeth are painted). Their
  bases lie in the lip rims, a centimetre sunk into them. Upper teeth stand on the outer part of the rim and lower teeth on
  the inner part, so the two rows pass each other when the jaw closes. Make the middle teeth the longest and the front and
  back ones short. Upper teeth are on the head bone, lower teeth on the jaw bone.
- **Bones.** The lower jaw (chin, lower lip, floor, lower teeth) is 100% on the jaw bone ahead of the hinge ring and about
  50% on it at that ring.
- **Texture.** The palate, floor, teeth and throat get their own small patches, because the side projection squeezes
  surfaces that face up and down into slivers: a palate with cross ridges, a tongue with a groove, darker toward the throat,
  a gum along the lip, ivory teeth with a gum-coloured base. **Keep it dark:** an upward-facing surface such as the lower
  lip's rim catches both the sky and the sun, so it is the brightest surface on the head (in the viewer, close to its own
  texel colour, where side faces render darker); a pale gum or a raised tongue then reads as a bright strip along the
  closed mouth. Keep those colours under about 0.35. (An earlier preview lit up-facing texels about 2.8 times too bright;
  judge this in `lp preview`, which now shades as the viewer does.) At the lip's own edge the
  patch fades to the outside skin colour, or the seam shows (`lowpoly-core/references/texture-method.md`, "Continuity"); nose and chin cap triangles with an inner
  vertex also take the mouth patch.
- **Cost on the 12 m animal:** the 46 teeth are 184 vertices and 184 triangles, plus the cavity, the jaws' rims and the caps. Check the
  opened mouth in a posed render and in the viewer, from the front and the side.

*The brow and the eye sockets.* From the hinge forward use a 12-sided ring: the chin, the jaw's lower edge, the two lips, a flank vertex at eye
level, a brow corner vertex, and the spine. At the eye ring pull the flank vertex in a little (a socket, about 0.8 of the
half-width) under a brow corner at about the head's width, with the spine vertex a little lower, so the front view shows two
ridges and a dip between them. Relax it toward the nose, where the brow corners become the edges of a flat nasal ridge.
**Round the edges:** a brow that overhangs a deep socket makes a knife edge that shows as a hard line through smooth shading
(141 degrees between the two triangles' normals on the first try, with the flank 0.22 m inside the brow; 84 degrees after
the flank came out to 0.8 of the half-width and the brow corner was lowered and pulled in). Keep the sharpest crease round
an eye under about 90 degrees, and measure it (`lib/lowpoly/tools/edge_angles.py`) rather than judging a flat-lit render.

*The eyes go in the lateral sockets,* where the orbit is in the skeleton reference, even on an animal that looks forward:
1. **Give the socket's triangles their own patch, projected obliquely** from the direction the orbit faces (about 55 degrees
   off the front for the T. rex: `u = |x| cos - z sin`, `v = y`), mirrored so that both eyes share it. It reads as an eye
   from the side and from 3/4, the angles a game camera uses.
2. **Don't force a dead-on front view.** Straight on, such an eye is a sliver at the side of the head, as a real animal's is
   when the cheeks are wider than the snout. Moving the eyes onto a surface that faces dead forward, to show them from the
   front, made them look like a painted visor.
3. **Keep the patch to the socket's own surfaces** (the strips between the lip, the flank and the brow). If two surfaces
   project to the same part of the patch, the eye shows twice at 3/4. Fade the dark socket out well inside the patch, not
   at its edge, or it ends in a hard rectangle, and sample the skin underneath at the point's true position (lowpoly-core §5).
4. **Check it from the front, 3/4 and side,** with the engine's lights (`lib/lowpoly/tools/lit_view.py`) and in the viewer.

**Extras in the measured models:** a wolf model from the same game has a separate mouth strip of painted gums and teeth (the
painted snarl above). Its texture also holds two long fur strips, but no triangle of its one mesh uses them: the tail is a
closed volume (17 vertices) and the model has no cards (re-measured 2026-11-26; an earlier note said it had flat fur cards
for its tail brush and ruff).

**Birds: heads and beaks (from the bald eagle of the agent trial).** A bird's head is not a mammal's with a muzzle: the
beak is a horn sheath on its own bones, and the mammal top-line rule (SKILL.md §5) does not hold. The test eagle's beak was
measured at 0.32 of the head from a close-up photo, then drifted to 0.49 over rounds of feature fixes (a deeper base, the
mouth's corner moved under the eye and the beak's base with it), with its top edge sloping down from base to tip. It read as
a toucan.
- **The parts, named so they can be measured:** the cere (bare skin at the beak's base, with the nostril), the culmen (the
  beak's top edge), the tomium (the cutting edge: the mouth line), the gape (the mouth's fleshy corner), the hook (raptors,
  parrots), the lower mandible.
- **What runs where:** the horn and the cere stop in front of the eye; in raptors only the gape line runs back under the
  eye. Moving the mouth's corner back moves the gape, never the beak's base.
- **A raptor's profile:** a flat crown; a brow ridge that overhangs the eye (the "frown"); a step down from the brow to the
  cere; the culmen nearly level from the cere, bending into a short hook over its last part, the tip below the gape line;
  the skull clearly taller than the beak's base. Other birds differ (a heron's beak outruns its head, a finch's is a short
  cone), so take no raptor numbers for them: measure.
- **Measure it, don't draw it:** in a side photo of the species' head, mark the beak tip (`nose`), the cere's front edge on
  the culmen, the gape corner, the eye's centre, `head_top`, `head_back` and the hook's lowest point, and run `lp overlay`
  with the non-rig ones under `model_landmarks`. Write down beak length over head length, base depth over beak length, the
  hook's drop below the gape and the eye's distance behind the cere, and re-measure them after every round.
- **The front view of a bird's head** (the test eagle passed a side overlay and was a wide flat-topped box from the front,
  with a thin spike of a beak and the eyes hidden on the sides): get a head-on photo of the species and measure it too. Mark
  both eyes' centres, the head's width at the eyes, the crown's top, the beak's base width (the cere) and the gape's corners.
  In the eagle's two front photos the crown is rounded, the eyes face partly forward (both show head-on, under heavy brows),
  the beak is broad at the cere and tapers to the hook, and the gape spreads wider than the beak. Build the head's rings
  rounded over the crown, with the brows standing out over the eyes, not as a flat-topped box.
- **Building it:** two or three rings from the cere (the deepest) to a hook ring and the tip, the culmen's vertices nearly
  level until the hook; the gape a vertex at the mouth's corner on the head's eye ring, not the beak's base ring.

## Long-faced heads (horse, deer, cow, goat): build the skull's planes before any paint

The first alicorn's head passed QA as a rounded tube with a horn: four or five circular rings tapering to a soft point, with
nothing of a horse's head in the geometry. A horse's head is recognised by its planes, so they must be modelled:
- **The reference set for the head:** a skull in side, front and top views, the head's superficial muscles (the masseter,
  the jaw's long muscles), and photos of real heads from the side, front, 3/4 and below. Measure the landmarks below on
  them.
- **Side profile:** a straight or slightly convex line from the poll to the nose; a flat forehead between the eyes; the
  nasal bone running long and straight to the nostrils; the nose's soft end rounded and slightly overhanging the mouth.
- **The jaw:** the cheek is a large flat round plate (the masseter over the mandible's broad ramus), its lower edge the
  jaw line, curving from below the ear down and forward, then running straight along the underside to the chin. Below
  and behind it, the throatlatch is a clear notch between the jaw and the neck. Even with no working jaw (a docile mouth
  that never opens), the closed jaw is modelled: the lips meet in a line, the chin is a small rounded lump under the
  mouth.
- **The face's cross-section:** from the front, the head is a long wedge: wide across the cheeks and eyes, narrowing down
  a nearly flat-sided face to the muzzle, then widening slightly at the nostrils. The eyes sit on the sides, at the top
  corners of the cheeks, with a bony ridge above each one.
- **Rings:** each ring is a polygon with flat faces where the head is flat (the forehead, the face's sides, the cheek
  plate) and corners where its edges turn, not a circle. Put rings at the poll, the eyes, the cheek's end, mid-face, the
  nostrils and the muzzle's end, and give the cheek plate and jaw line their own vertices.
- **Check it** with head_views (untextured, from the side, front, top, 3/4 and below) against the skull and photos before
  any texture is painted; then with head_textured.

**A bear's ear is a rounded tab, and two tips make it pointed** (the Kodiak, 2026-11-24). A tent ear with an inner and an
outer tip reads from the front as a cat's or a wolf's pointed ear. Give it three top vertices: the inner and outer corners
and a raised centre between them, so the outline is a rounded five-sided tab like the reference bear's; set it on the skull's top back
corners. A rounded tab can still read as a hound's ear from the side: the Kodiak's, 9.5 cm tall and facing straight forward, was a thin
spike in profile. Keep it a low half-disc about half as tall as wide (6 cm on the Kodiak), and turn its plane forward and out
(the inner corner forward, the outer back) so the side view sees part of its round face. Three top vertices still leave corners: the user's reference wanted
a round D, which took five along a semicircle (the low inner and outer points, two between, the top), with the cup
painted darker inside a lighter rim. **A broad nose needs a broad tip:** with one vertex at the top of the muzzle's tip its
front is a triangle, and a painted nose pad reads as a downward wedge; split it into a left and right corner (one more
vertex) so the front is a four-sided pad, and paint the pad as a rounded block with two comma nostrils low on its front,
a soft highlight across its top and a short groove to the lip.
