# Feet: size, shape, soles, toes and claws

The detail behind SKILL.md §3, rule 5. Read it before building any foot.

Foot size as a fraction of leg length, measured:

| Foot | Width | Length |
|---|---|---|
| Deer hoof | 0.05 | 0.09–0.11 |
| Dog paw | 0.11 | 0.13–0.17 |
| Cow or pig trotter | 0.14–0.21 | 0.16–0.19 |
| Bear paw | 0.25 | 0.31–0.34 |

- **Shape:** carnivore paws are roughly round, as wide as they are long. A long narrow foot reads as a hoof.
- **Every foot has a flat sole on the ground.** In the measured bind poses all sole vertices sit at one height, y = 0: the
  deer has 3, the cow 5, the bear 7.
  - Build the sole explicitly and horizontally, from a knuckle ring above the ground (set forward of and lower than
    the heel: the wedge below), a sole ring at y = 0 and a sole centre vertex. A ring built in the leg's own frame comes out tilted with the leg, leaving a
    single point (or a sunken corner) on the ground.
  - A hoof is a wedge with a flat base.
- **Shape the paw as a sloping, splayed wedge, not an upright box.** Measured on the feet of the ambient dog and bear
  and of the measured monster models (wolf, hound, werewolf, spiny beast, giant lizard, giant rat, drake) with `lib/lowpoly/tools/foot_study.py`
  (numbers in `references/reference-measurements.md`):

  | | Measured | A first build (box paws) |
  |---|---|---|
  | Width at the ground against the width at the ankle (splay) | 1.6-2.7 | 1.1-1.3 |
  | How far the sole runs forward of the ankle's front, in ankle depths | 0.8-1.6 | 0.1-0.7 |
  | Footprint, front to back by side to side, as a fraction of the animal's height | dog 0.13 x 0.09, wolf 0.20 x 0.11, bear 0.26 x 0.19; monsters up to 0.47 x 0.31 | fox 0.10 x 0.06, cat 0.14 x 0.08 |
  | Ground contacts | 5-8 (drake 12) | 5 |

  - **Side profile:** three steps, heel (or the back of the pad), a knuckle hump, then the toes sloping down to a
    rounded tip ahead of the leg. The wolf's paw is a tent widest at the ground; the dog's leans forward like a
    parallelogram.
  - **Front view:** a trapezoid or tent that widens to the ground, never vertical sides.
  - **Cost:** the same vertices as a box (10-15 per mammal paw). The box paws of the first builds had the count, put in
    the wrong places: a knuckle ring as wide as the sole, straight above it.
  - **Size:** the size table above is for the real animal. A game exaggerates feet that the camera should read: the
    monster models' paws are 1.5-3 times the real proportion.
- **Toes and claws as geometry, where the species shows them.** Mammal paws keep their toes in the paint (§6). Animals
  whose toes or claws make the silhouette build them:
  - the lizard, the rat, the spiny beast and the drake: 3-4 toe tips per foot, each a small wedge or hooked spike
    reaching past the foot's outline and down to the ground;
  - 17-39 vertices per foot, 7-11% of the model;
  - on the large ones (the drake), each toe on its own bone, up to 6 bones per foot.

  The 12 m test animal's foot was a flat rectangular slab of 9 vertices with no toes. Beside the measured drake and
  spiny beast it reads as a stump. A theropod wants three forward toes welded into the foot, each with its claw, and its first toe high on the inside
  (below: "A clawed foot from its anatomy first").
- **Long-toed feet (theropods, birds, drakes) are not paws.** Their toes run well ahead of the ankle, so the paw's splay
  and reach ranges don't apply. Only two measured models have such feet:
  - the drake: reach 8.4 ankle depths, 4 tips (3 forward and a spur), 12 ground contacts, 39 vertices, 6 bones;
  - the giant rat: reach 2.4, 3-4 hooked claws, 2-6 contacts, 17-27 vertices, 3 bones.

  `lp check` judges a spec with `"feet": "long-toed"` against those two, as warnings only. On a large animal, give each
  toe its own bone so the toes can curl in the walk.

## Claws and toes as part of the skin (measured on the drake)

How a clawed foot is built, read from a measured monster model: the drake, a 5.4 m biped with clawed feet and hands
(`lib/lowpoly/tools/foot_study.py`, and its mesh, weights and UVs read in code).

- **One skin, no loose pieces.** Every claw is welded into the foot or hand. The whole model is one welded piece of 1026
  triangles; its only loose parts are a few three-triangle spikes on the head.
- **Each claw: a root, a ring and a tip.**
  - **The root:** 3-4 of the foot's or hand's own vertices (a face of the foot's surface).
  - **Its own vertices:** a ring of 3 and a tip, 7-8 positions and 9-10 triangles per claw, 0.18-0.26 m long (about 5% of
    the height).
  - **Weights:** the root stays on the foot or hand bone, the ring and the tip ride the claw's own toe or finger bone.
  - **The result:** a claw can be placed and posed on its own and still grow out of the foot.
  - **Its shape is not the claw's.** One ring and a tip make a straight three-sided spike. A real claw is a hooked, side-
    flattened sheath on a digit with a knuckle and a pad: build it curved (`references/parts.md`, "Claw").
- **The rear claw** has its own bone, its root welded into the back of the foot and weighted 90-99% to the foot.
- **The texture:** every claw is its own UV island, and all 16 share one small strip of the texture (about 46 x 18 texels).
  The strip is painted along the claw: skin-dark at the root end, lightening to an ivory point. The root is a UV seam, and
  the change from scale to claw is in the strip's paint, not the geometry.
- **Cost:** a foot of 39 positions and 71 triangles, with 4 claws and up to 6 bones.

**How to build it:**
- **Weld each toe onto a face of the foot.**
  - **The root:** remove one of the foot's faces (a quad on the foot's front for each forward toe, or an inset triangle for
    a toe placed elsewhere) and use its vertices as the toe's root.
  - **The toe's own vertices:** a ring at the claw's base and the claw's tip.
  - **Shape:** shrink the ring across and in height separately, so a toe can be broad and low.
  - **Weights:** the root on the foot bone, the toe's own vertices on a bone per toe at its joint.
- **An inset root** (a smaller triangle inside the face, with a band of three quads round it) keeps a toe from starting
  as wide as a whole face of the foot. Tidy the band afterwards: a thin face makes thin band triangles.
- **Mirror the feet before welding,** so both feet offer the same root faces, and build the right foot's toes on the
  mirror of the left's.
- **One shared strip, one row per skin.**
  - **Shared:** every claw maps onto one strip, painted along the digit: the skin's scales, a dark cuticle, then horn
    lightening to the tip.
  - **A row per skin colour:** where the claws grow from skins of different colours (dark feet, pale arms), give each its own
    row with that skin at the root and the same claw. One row for both made the fingers as dark as the toes.

## A clawed foot from its anatomy first (built on the 12 m test animal)

The drake shows how to build a claw, not what the species' foot looks like. The test animal's first welded toes copied
the drake's construction onto a foot built with no anatomy: they read as flat spikes, then as a hand of parallel blocks seen
from below. Rebuilt from the anatomy, the same construction reads as a theropod's foot.
- **The anatomy, from the skeleton and the tracks:** which toes bear weight (a theropod walks on three, II, III and IV, with
  III the longest), where the first toe sits (high on the inside of the metatarsus, off the ground), the heel pad (the
  metatarsophalangeal pad), and how the toes taper and splay.
- **The size, from the reference animal the model is matched to.** A track or a specimen comes from another individual: take
  its ratios (a tyrannosaur track's width is about two thirds of its length) and the size from your own reference.
  - **The test animal:** the 0.96 m track came from a larger individual. The reference animation's planted foot is
    0.78-0.80 m in all 12 frames. A foot built to the track was 21% too long.
  - **A rough cross-check:** hip height about 4-5 times the footprint's length in large theropods.
- **The shape, checked from below.** Render the footprint and measure it:
  - its length and width;
  - a compact, rounded heel pad;
  - the middle toe longest, the side toes splayed from the pad and ending at about 55% of the length;
  - the inner toes clear of the other foot.

  Parallel toes on a square pad read as a hand.
- **The paint: the foot is the leg continuing down.** Paint the foot's patch with the leg's own colour and darkening at each
  height, its shading and its scale size where they meet, finer toward the toes. Don't paint toes, gaps or claws on the foot
  when they are geometry.
  - **On the test animal:** a foot patch in its own lighter palette made a step in tone at the ankle. Painted as the leg, the
    median seam jump fell from 0.057 to 0.03.
- **Cost on the test animal:** 39 positions, 68 triangles and 5 bones per foot (the drake: 39, 71 and up to 6). The toes
  touch down at 0.00 m in the stance and lift about 0.2 m in the swing (`case-study-trex.md`, round 22).

## Large plantigrade feet with claws as geometry (the Kodiak bear, hostile, 2026-11-24; *approved by lp check*: 43 checks, no warnings)

**A heavy plantigrade foot (a bear; the dragon's forefoot).** Build the paw as a flat sole at y = 0 fanned from one heel vertex
to a row of six toe-front vertices at the ground, a knuckle pair above the toes, and the ankle's 4-ring (front, out, back, in)
over the heel. Grow one claw from each of the five front faces between neighbouring toe-front vertices and a knuckle:
- **Two vertices for a long curved claw** (a cuticle on the claw's back at about 0.4 of its length and well up, a tip ahead and
  just above the ground), joined symmetrically: the cuticle to the knuckle and both toe corners, the tip to the cuticle and both
  toe corners. One vertex (a pyramid) for a short, blunt claw. Measured on the Kodiak: 23 vertices and 40 triangles per forefoot
  with the wrist ring, 18 and 30 per hind foot.
- **Paint the horn only on the claw's slender outer half.** The welded claw's root is the whole toe's front, so neighbouring claws
  share corners; painted pale to the root they read from the front as a row of teeth. Pale from the tip to about 0.6 of its
  length, dark horn to the cuticle, the toe's fur behind.
- **The sizes from the species.** A bear's forefoot is about as wide as long without its claws; the hind foot 0.6 as wide as long,
  heel included. Fore claws about the toe's own length, curved 35-55 degrees, pale; hind claws half as long and darker.
- **The measure's bands.** lp's feet checks read the paw's width and reach in the bottom 15% of the foot zone and count contacts
  within 1% of the height: set the claw tips just above the contact band but inside the bottom 15% (1.6-1.7 cm on a 1.5 m animal),
  or a resting claw tip, hovering naturally higher, drops out of the reach and the splay.
- **The splay comes from a narrow ankle.** The wrist and the hock are narrower than the paw (0.12-0.13 against 0.20 m on the
  Kodiak); a hock ring as wide as the sole fails the splay however wide the paw is made.
