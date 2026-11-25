# Measurements of the measured models

**Source:** the 22 shipped ambient animal models of a late-1990s commercial RPG, read with small parsers of the developer's
own formats. Only the measurements are kept here; no model, texture, file or name from that game is part of this skill.
The feet section adds seven of the same game's animal-like monster models (a wolf, a hound, a werewolf, a large lizard, a
rat, a spiny beast and a drake), measured the same way.
- **Corners:** the vertices as stored, including duplicates at UV seams.
- **Unique vertices:** distinct positions.
- **Motion:** measured by running each clip through the skeleton (forward kinematics) and skinning the mesh at each
  sampled frame.

## All 22 ambient models

| Model | Unique vertices | Corners | Triangles | Bones | Corners on 2+ bones | Texture | Height × length (m) | Separate pieces / open edges |
|---|---|---|---|---|---|---|---|---|
| Cow | 227 | 270 | 450 | 30 | 58% | 256 × 256 | 1.44 × 3.48 | 1 / closed |
| Pig | 227 | 293 | 450 | 26 | 51% | 256 × 128 | 0.60 × 1.16 | 1 / closed |
| Bear | 223 | 273 | 442 | 26 | 59% | 256 × 256 | 1.81 × 2.97 | 1 / closed |
| Mule (and a lame variant) | 219 | 283–295 | 436 | 33 | 57% | 256 × 128 | 1.73 × 2.90 | |
| Mule with pack loads | 301–448 | 428–719 | 580–829 | 33 | 27–44% | 256 × 256 | up to 2.22 × 2.90 | the mule plus rigid baggage |
| Sleeping Dog | 208 | 265 | 412 | 38 | 74% | 256 × 128 | 0.33 × 0.91 | |
| Dog | 199 | 255 | 394 | 33 | 76% | 256 × 128 | 0.64 × 1.28 | |
| Deer | 171 | 231 | 338 | 39 | 48% | 256 × 128 | 1.54 × 1.71 | |
| Chicken | 146 | 176 | 288 | 18 | 28% | 128 × 128 | 0.49 × 0.52 | 1 / closed |
| Gecko | 119 | 140 | 226 | 20 | 25% | 128 × 64 | 0.06 × 0.53 | 2 / 6 |
| Crab | 90 | 126 | 125 | 39 | 42% | 128 × 128 | 0.05 × 0.27 | 1 / 67 of 220 (card legs) |
| Rat | 54 | 58 | 104 | 6 | 26% | 64 × 64 | 0.15 × 0.55 | 1 / closed |
| Raven | 50 | 69 | 96 | 8 | 26% | 256 × 128 | 0.10 × 0.38 | 1 / closed (wings are flat slabs) |
| Seagull | 35 | 101 | 68 | 9 | 0% | 256 × 128 | 0.38 × 0.65 | 1 / closed, rigid segments |
| Bat | 25 | 25 | 46 | 7 | 32% | 64 × 32 | 0.02 × 0.15 | 1 / closed |
| Baby Spider | 24 | 24 | 8 | 4 | 0% | 32 × 64 | 0.03 × 0.20 | 8 / all (triangle cards) |
| Fish | 18 | 18 | 34 | 3 | 56% | 128 × 64 | 0.13 × 0.31 | 1 / closed |
| Bird | 17 | 17 | 16 | 12 | 29% | 64 × 64 | 0.15 × 0.20 | 1 / 16 of 32 (cards) |
| Butterfly | 15 | 30 | 26 | 5 | 7% | 32 × 32 | 0.05 × 0.13 | 1 / closed |

**Clips** (from their names): default stand, idle fidgets, walk, run, die, attack, fly, glide, graze, lie down and up,
sit down, up and fidget.

**General facts:**
- **The head takes the most vertices:**

  | Animal | Head bone corners | Share of corners |
  |---|---|---|
  | Deer | 47 | 20% |
  | Pig | 50 + 18 (jaw) | 23% |
  | Cow | 78 | 29% |

  In the small animals the head bone also leads: the raven's head has 31 of its 69 corners.
- **Mirrored texture:** every UV spot shared by two different vertices joins a left-side vertex to a right-side one
  (deer 69, pig 87, dog 108, cow 116). One painted side serves both.
- **No mirrored geometry:** no vertex has an exact mirror twin; the bind pose is a natural, slightly asymmetric stance.

## Heads: eye direction (bear, dog, wolf against deer, cow, pig)

**Method:**
- **Head:** the front 22% of the body length, above 45% of the height.
- **Front-facing triangle:** `|normal.z| > 0.55`.
- **Texture per area:** the UV area per 3D area of the front-facing head triangles, divided by the same for the
  side-facing ones.

| Model | Eyes | Front-facing head triangles | Texture per area, front against side | Face in the texture |
|---|---|---|---|---|
| Deer | side | 42 | 0.68 | profile, one eye per side |
| Cow | side | 54 | 0.89 | profile; snout painted |
| Pig | side | 8 | 0.92 | profile; snout disc painted |
| Bear | forward | 24 | 1.02 | head-on: both eyes and the nose painted as a frontal face |
| Dog | forward | 30 | 1.19 | three-quarter frontal, both eyes visible |
| Wolf (a monster model of the same game) | forward | 49 | 1.08 | three-quarter frontal, plus a mouth strip with teeth and flat fur strips |

**Head top line:** the crown (the highest point) is at 19% of head length on the bear, 31% on the cow and 39% on the
deer, measured from the back of the head.

**Eyes against the muzzle** (textured head renders, `lib/lowpoly/tools/head_textured.py`):
- **Dog:** the eyes sit behind a visible stop, above a narrower muzzle block painted separately (lighter, a mouth line,
  a dark nose tip).
- **Bear:** small eyes under a dark brow at the brow-muzzle junction. A protruding muzzle block, painted lighter with
  fur running along it, ends in a black nose.
- **Texel reuse** (`lib/lowpoly/tools/uv_reuse.py`): none of the eye texels repeat elsewhere on either head. Reuse in the measured models is for
  repeated parts: the dog's paws share one patch.

## Eyes: the zones round the eye (`lib/lowpoly/tools/eye_study.py`)

**Method:** the eye's texel and half-width were read off an enlarged crop of each texture. Brightness (luminance, 0-1) was
averaged in rings at multiples of the eye's radius, and in four sectors at 1.5-2.6 radii. "Step" is the difference from
the coat at 2.6-4 radii.

| Model | Eye width (texels) | Head texels/m | Eye radius on the model | Darkest / brightest in the eye | Eye body step | Rim spread (sd) | Socket step | Above / below | The rim |
|---|---|---|---|---|---|---|---|---|---|
| Dog | 7.0 | 214 | 16 mm | 0.00 / 0.62 | -0.09 (dark coat) | 0.15 | -0.07 | 0.28 / 0.23 | a pale lower lid; brow creases |
| Cow (white face) | 6.6 | 158 | 21 mm | 0.02 / 0.62 | -0.53 | 0.11 | -0.51 | 0.31 / 0.50 | a dark lid crease; brow shadow |
| Cow (brown face) | 6.6 | 158 | 21 mm | 0.04 / 0.31 | -0.28 | 0.13 | -0.33 | 0.25 / 0.33 | a saturated yellow lid, a dark crease beyond |
| Deer | 5.6 | 130 | 22 mm | 0.11 / 0.56 | -0.16 | 0.22 | +0.18 | 0.49 / 0.63 | a cream ring above and below; a dark line forward |
| Bear | 6.0 | 118 | 25 mm | 0.01 / 0.63 | -0.01 (coat 0.13) | 0.08 | -0.04 | 0.11 / 0.10 | a dark halo; the catchlight carries it |
| Pig | 5.2 | 178 | 15 mm | 0.06 / 0.89 | -0.30 | 0.17 | -0.11 | 0.60 / 0.64 | a dark lash line, a paler lid above, lashes |
| Mule | 4.4 | 93 | 24 mm | 0.00 / 0.78 | -0.17 | 0.16 | -0.05, a paler ring | 0.52 / 0.52 | concentric pale lid rings |
| The test red fox (before) | about 10 | 556 | 9 mm | 0.11 / 0.44 | +0.08 | 0.03 | +0.07 | 0.21 / 0.24 | none: an amber blob on orange |
| A red fox photo (two eyes) | — | — | — | 0.00 / 0.99 | -0.27 / -0.35 | 0.23-0.24 | -0.14 / -0.16 | 0.55 / 0.35 (near eye) | a black lid line all round; a dark line from the inner corner down the muzzle; paler fur above the inner corner |

**What they share:** a catchlight (0.55-0.89, one or two texels, upper half) in every model; a near-black eye body; a rim
that is drawn (spread 0.08-0.22) rather than faded; a socket that is never the coat's own value; and, on most, a darker
brow than cheek. The eyes are 1.5-2 times life size on the model.

**The lid lines** (brightness profiles straight up and down through each eye, across the upper and lower lids):

| Eye | Upper lid, darker than the fur by | Lower lid | Width at half depth | Back to the fur within |
|---|---|---|---|---|
| Werewolf | 57% | 33% | 2-4 texels | 2-3 texels |
| Dog | 38% | about 0 | 2 texels | 2 texels |
| Pig | 29% | 6% | 1 texel | 1-2 texels |
| Mule | 8% | 17% | 1 texel | 1-3 texels |
| Cow | 32% | 92% | 2-4 texels | 5 texels |
| Bear (a dark coat) | 63% | 74% | 4-5 texels | 3-6 texels |

- **Colour:** each lid keeps the coat's hue, only darker (the werewolf's is its own blue-grey, deeper).

**The inner corner** (a red fox photo, the near eye, 76 pixels wide; profiles across the mark at distances along it, down and
toward the nose, in eye widths):

| Along | 0.05 | 0.15 | 0.30 | 0.50 | 0.75 | 1.00 | 1.30 |
|---|---|---|---|---|---|---|---|
| Darkening of the fur | 96% | 78% | 69% | 64% | 44% | 35% | 17% |
| Width at half depth | 0.45 | 0.45 | 0.50 | 0.45 | 0.35 | 0.20 | 0.15 |

- **Colour:** the pocket's darkest third is RGB 0.09 0.05 0.03; the wedge's is 0.34 0.12 0.01, against fur of 0.60 0.32 0.10. It
  is the coat's hue, darker and more saturated.
- **The measured models:** the darkest value in a 5-texel column, stepping out from the eye's edge 0 to 4 texels toward the
  front:
  - mule 0.08, 0.26, 0.35, 0.37;
  - cow 0.08, 0.08, 0.10, 0.34, 0.52;
  - pig 0.29, 0.28, 0.34, 0.53;
  - deer 0.14, 0.25, 0.37, then its short dark line;
  - dog 0.02, 0.16, 0.18 (a dark mask round the eye).

## Noses and muzzles (`lib/lowpoly/tools/nose_study.py`, on `head_textured.py` renders)

**Method:** each head rendered textured and flat-lit, so the pixels are the texture's colours whatever the UV layout.
- **Front view:** the nose is the largest dark blob in the lower middle of the face. The ring is the muzzle up to 6 pixels
  round it. The face is measured between the eyes.
- **Side view:** columns at 10%, 22% and 35% of the head's length back from the tip. The bridge is the top quarter and the
  side the next quarter; the mouth line is the darkest 3-pixel run in the lower half.

| Model | Nose width / muzzle | Nose mean | Nostrils (darkest 10%) | Lit top (brightest 5%) | Ring - nose | Muzzle - face | Bridge / side, 10% back | Mouth line (lip above) | Chin |
|---|---|---|---|---|---|---|---|---|---|
| Dog | 0.42 | 0.05 | 0.00 | 0.19 | +0.19 | +0.03 | 0.38 / 0.35 | 0.07-0.09 (0.16-0.27) | 0.00-0.21 |
| Bear | 1.02 (pad) | 0.11 | 0.03 | 0.22 | +0.01 | -0.16 | 0.33 / 0.14 | 0.01-0.05 (0.06-0.10) | 0.09-0.11 |
| Cow | 1.03 (pad) | 0.10 | 0.05 | 0.24 | +0.34 | -0.28 | 0.69 / 0.28 | 0.00-0.04 (0.05-0.08) | 0.06 |
| Deer | 0.66 | 0.12 | 0.10 | 0.19 | +0.13 | -0.03 | 0.36 / 0.33 | 0.07-0.21 (0.08-0.33) | 0.15 |
| Pig | 0.11 (disc) | 0.19 | 0.13 | 0.27 | +0.23 | -0.12 | 0.61 / 0.48 | none: the pig's mouth is unpainted | 0.54 |
| Mule | 0.33 | 0.06 | 0.02 | 0.15 | +0.23 | +0.05 | 0.33 / 0.24 | 0.09-0.20 (0.10-0.46) | 0.25-0.34 |
| The test red fox (before) | 0.32 | 0.05 | 0.03 | 0.10 | +0.17 | -0.03 | 0.19 / 0.18 | 0.15-0.21 (0.16-0.22) | 0.28-0.31 |

**A red fox photo** (boxes on the face photo): nose 0.26, its top band 0.38 (highlights 0.66-0.86), nostrils 0.13 (darkest
0.00); white upper lip 0.97; mouth line 0.51 (darkest 0.20); chin 0.60; muzzle bridge 0.73, side 0.75; face 0.59.

**What they share:** a nose that is the muzzle's darkest mass, with a lighter top and darker nostrils inside it; fur round
it set off from it; a lit bridge; a dark mouth line; a shaded chin. The pig is the exception for the colour (a pink disc)
and the mouth (none painted), not for the lighting.

## Coats: light, form and strokes on the torso (`lib/lowpoly/tools/body_study.py`)

**Method:** a side render of the texture alone (unlit), the model 720 pixels long. The torso is the part between the rearmost
and frontmost feet, above 45% of the height. Its brightness is split by blurring over 1% and 5% of the length: large shapes
over 5%, form shapes 1-5%, fur strokes under 1%. Stroke direction comes from the structure tensor of the fine layer, over
the whole torso and in windows of 5% of the length.

| Model | Large (sd) | Form (sd) | Form darks / lights (5% / 95%) | Strokes (sd) | Stroke coherence, whole / local | Local directions (10-90%) |
|---|---|---|---|---|---|---|
| Dog | 0.035 | 0.025 | -0.039 / +0.046 | 0.019 | 0.11 / 0.33 | -42 to +90 deg |
| Bear | 0.043 | 0.029 | -0.043 / +0.050 | 0.049 | 0.06 / 0.30 | -78 to +72 deg |
| Deer | 0.043 | 0.034 | -0.048 / +0.049 | 0.024 | 0.08 / 0.25 | -66 to +55 deg |
| Pig | 0.038 | 0.014 | -0.023 / +0.023 | 0.013 | 0.24 / 0.27 | -4 to +1 deg (bristle along the body) |
| Mule | 0.035 | 0.022 | -0.033 / +0.040 | 0.019 | 0.28 / 0.33 | -83 to +89 deg |
| Cow (spots) | 0.233 | 0.164 | -0.281 / +0.263 | 0.068 | 0.13 / 0.24 | -77 to +66 deg |
| The test red fox (before) | 0.026 | 0.009 | -0.016 / +0.014 | 0.008 | 0.74 / 0.74 | -1 to +2 deg |

**Where the form shapes are** (the form layer drawn as an image):
- **Mule:** a ringed haunch, vertical rib bands, the shoulder line, tendon lines on the legs.
- **Deer:** a flank shadow above the hind leg, the elbow line, pale rims down the backs of the legs.
- **Dog and bear:** swirls of strokes round the muscle groups.
- **The fox:** none, only its colour zones' edges.

**Paint against the geometry, per vertex** (the share of rays from each vertex that hit the mesh nearby, against its
neighbours): weak and mixed on the measured models (r from -0.13 to +0.26). Their shading is painted at the texel scale,
finer than the low-poly mesh, so judge it in the texture, not per vertex.

## Feet as geometry (`lib/lowpoly/tools/foot_study.py`)

**Method:** a foot is a connected piece of the mesh below 12% of the animal's height that reaches the ground.
When the rig shows the limbs, only skin the feet's bones carry (each limb's ankle bone and below, `lowpoly/rig_parts.py`)
counts, so a low knee, a tail on the ground or a feather cuff is not a foot; on every reference animal here the result is
unchanged.
- **Splay:** the width at the ground against the width at the top of the zone (the ankle).
- **Reach:** how far the sole runs forward of the ankle's front, in ankle depths.
- **Tips:** vertices sticking out of the foot's outline further than all their neighbours.

| Model | Vertices, triangles per foot | Footprint (of height) | Splay | Reach | Tips | Contacts | Bones |
|---|---|---|---|---|---|---|---|
| Dog (ambient) | 10, 13 | 0.13 x 0.09 | 2.0 | 0.9 | 1 | 5 | 2 |
| Bear (ambient) | 15, 22-23 | 0.22-0.26 x 0.18-0.19 | 1.6-1.8 | 1.1-1.2 | 1-2 | 6-7 | 3 |
| Deer (ambient, hoof) | 6, 7 | 0.07-0.09 x 0.03 | - | - | 1 | 3 | 2 |
| Wolf (monster) | 10-12, 14-18 | 0.20-0.21 x 0.11-0.12 | wide (a tent) | 0.3-1.1 | 1 | 6-8 | 2-3 |
| Hound (monster) | 10, 13 | 0.29-0.38 x 0.20-0.22 | 2.0 | 0.8-0.9 | 1 (a claw) | 5 | 2 |
| Werewolf (monster) | 14, 22 | 0.13 x 0.13 | 1.6 | 1.6 | 2 | 5 | 3 |
| Spiny beast (monster) | 15, 22 | 0.47 x 0.31 | 1.8 | 0.5 | 3 toe ridges | 8 | 2 |
| Giant lizard (monster) | 24, 41 | 0.23-0.24 x 0.14 | 1.0-1.7 | 0.1-0.9 | 3 splayed toes | 2 | 2 |
| Giant rat (monster) | 17-27, 28-45 | 0.18-0.27 x 0.10-0.15 | 0.9-1.9 | 2.4 | 3-4 hooked claws | 2-6 | 3 |
| Drake (monster) | 39, 71 | 0.14 x 0.07 | 2.7 | long toes | 4 (3 forward, a spur) | 12 | 6 |
| The test fox (box paws) | 9-13, 12-20 | 0.10 x 0.06-0.07 | 1.1-1.3 | 0.1-0.7 | 1 | 5 | 2 |
| The test cat (box paws) | 9-13, 12-20 | 0.09-0.14 x 0.08 | 1.1-1.2 | 0.1-0.5 | 1 | 5 | 2 |
| The 12 m test animal (a slab) | 9, 12 | 0.18 x 0.11 | 1.1 | 0.1 | 2 | 5 | 1 |

**Shapes seen in the close-ups:**
- **Wolf:** a tent, widest at the ground, stepping down from the ankle over the knuckles to the toe tip.
- **Dog:** a trapezoid splayed at the ground and leaning forward.
- **Bear:** a low slab.
- **Spiny beast:** a low mound with toe ridges.
- **Giant lizard:** splayed toe points.
- **Giant rat:** claws hooking down past the foot.
- **Drake:** four toe pyramids with claws.
- **The test builds:** upright boxes, and a slab.

## Ears (dog, deer, bear, mule; measured with `lib/lowpoly/tools/ear_study.py` and `lib/lowpoly/tools/head_views.py`)

| | Dog | Deer | Bear | Mule |
|---|---|---|---|---|
| Built as | a peak of the head skin | its own part, a 2-bone chain (base and tip) | a peak of the head skin | its own part, 1 bone |
| Per ear: tip vertices / shared base vertices / triangles | 2 / 5 / 3 | 10 / 9 / 11 | 6 / 5 / 7 | 7 / 6 / 7 |
| Open edges | 0 | 0 (a thin cupped closed shell) | 0 | 0 (a 4-sided pyramid) |
| Height, as a fraction of head length | 0.26 | 0.44 | 0.23 | 0.51 |
| Base width, as a fraction of head width | 0.33 | 0.27 | 0.32 | 0.20 |
| Base: head widths behind the nose / % of half-width out / below the skull top | 0.81 / 54% / 1.7 cm | 1.00 / 35% / 3.6 cm | 1.02 / 61% / 3.8 cm | 0.96 / 48% / 2.0 cm |
| Tilt (outward, back) | 28°, −30° | 38°, 26° | 14°, −19° | 15°, −26° |
| Base weights | head 100% | neck and head, some with the ear bone | head 100% | head 100% |
| Texture: texels, px/m (head px/m) | 178, 216 (195) | 291, 101 (133) | 554, 94 (110) | 370, 80 (93) |
| Spread, range | 0.107, 0.00–0.34 | 0.107, 0.10–0.73 | 0.076, 0.02–0.56 | 0.152, 0.02–0.64 |
| Shared with head texels | 10% | 3% | 6% | 0% |
| Front vs back colour | front darker (dark opening) | front darker; separate back patch | the same (fur only) | front darker (dark opening) |

What the ear fronts show:
- **Dog:** a dark teardrop opening with an orange fur rim.
- **Mule:** a long dark almond opening with a darker edge and a lighter rim.
- **Deer:** an elongated leaf with a dark inside and a lighter rim; its back is a separate furred patch.
- **Bear:** a furry tab in the head's own fur, with no opening drawn.


## Limbs: the junction, thickness and feet

**The leg-body junction (deer):**
- **Shared skin:** 54 of 338 triangles join body-only corners to limb-weighted corners. 26 corners blend body and
  limb bones.
- **Hind leg, top:** flank vertices at y 0.70–0.83 m (the deer is 1.54 m tall) are weighted about ⅓ each to the hip bone,
  the thigh bone and a spine bone.
- **Groin:** a vertex at x ≈ 0, y 0.65 m is weighted 50/50 to the left and right thigh bones.
- **Thigh below the body:** 100% thigh bone.
- **Joints:** the knee (y ≈ 0.36 m) is 50/50 thigh and shin; the lower joint (y ≈ 0.07–0.09 m) is about 50/50 shin and
  foot.
- **Sole:** 3 vertices at y ≈ 0, all on the foot bone.
- **How far up the legs reach:** corners with 30% or more of their weight on a limb reach 54–57% of the height.
- **Stretch:** junction edges stretch up to 62% over the walk.

**Upper hind leg depth** (front-to-back extent of the corners on the thigh bone, as a fraction of leg length):

| Deer | Cow | Dog | Pig | Bear |
|---|---|---|---|---|
| 0.19 | 0.20 | 0.27 | 0.28 | 0.46 |

**Feet** (width × length, as a fraction of leg length):

| Animal | Front foot | Hind foot |
|---|---|---|
| Deer | 0.05 × 0.09 | 0.05 × 0.11 |
| Dog | 0.11 × 0.17 | 0.11 × 0.13 |
| Cow | 0.16 × 0.16 | 0.14 × 0.16 |
| Pig | 0.21 × 0.19 | 0.18 × 0.16 |
| Bear | 0.26 × 0.34 | 0.25 × 0.31 |

**Foot texture** (triangles with their centre below 8% of the height; measured with `lib/lowpoly/tools/foot_detail.py`):

| Animal | Foot triangles | Texels | px/m | Brightness spread | Range | Edge strength | Foot against lower leg |
|---|---|---|---|---|---|---|---|
| Bear | 90 | 1410 | 99 | 0.107 | 0.00–0.78 | 0.142 | +0.04 (pale claws) |
| Dog | 44 | 335 | 230 | 0.099 | 0.03–0.69 | 0.108 | +0.06 |
| Cow | 56 | 577 | 85 | 0.307 | 0.02–0.94 | 0.115 | −0.07 |
| Deer | 28 | 160 | 87 | 0.216 | 0.00–0.67 | 0.165 | −0.24 (black hooves) |
| Pig | 64 | 501 | 236 | 0.093 | 0.10–0.63 | 0.057 | −0.13 |

**What each foot shows:**
- **Bear:** each paw has its own strip, with fur strokes, dark toe gaps and long pale claws.
- **Dog:** the front paw has its own patch, with dark notches between the toes and nails. The hind paw sits at the end
  of the leg strip, with little detail.
- **Cow and deer:** dark hooves with a light cleft line.
- **Pig:** a separate top-down disc for the sole.

No measured foot models its toes, claws, hoof halves or pads.

**Soles in the bind pose:** every sole vertex sits at one height (deer 3 vertices at ≈ 0; cow 5 at −0.0023; bear 7 at
−0.0067). The idle clips keep every sole on the ground in all sampled frames, tilting 0.1–1% of the height.

## Walk clips (48 samples per cycle)

H is the animal's height and L the leg length.

| Animal | Cycle | Share of the cycle a foot is down | Lift, % H | Stride, % H | Top-segment swing | Footfall order |
|---|---|---|---|---|---|---|
| Dog (0.64 m) | 0.75 s | 0.58–0.85 | 3.5–8.3 | 59–91 | 43–69° | LH LF RH RF |
| Bear (1.81 m) | 1.33 s | 0.67–0.92 | 2.2–3.8 | 81–90 | 58–78° | LH RH LF RF |
| Cow (1.44 m) | 1.50 s | 0.56–0.81 | 3.5–7.0 | 62–70 | 47–53° | LH RF LF RH |
| Pig (0.60 m) | 0.67 s | 0.83–0.90 | 2.4–5.0 | 77–96 | 59–66° | RH RF LH LF |
| Deer (1.54 m) | 1.50 s | 0.56–0.67 | 9.3–21.4 | 45–53 | 15–53° | LH RF RH LF |

**Joint flex in the swing** (side-view angle between segments, change from the bind pose):

| Animal | Front | Hind |
|---|---|---|
| Dog | wrist −76/+41° | hock −63/+46° |
| Cow, pig | knee −41 to −67° | |
| Deer | wrist up to about −100°, then the foot flips back about 100–120° | hock flexes up to 58°; the hoof segment curls up to 100° |

The deer's pastern and foot hold their bind angle through the stance (flat), and its upper leg sweeps about ±20°.

**Sole roll while the foot is down** (heel or tip lift before toe-off): deer 0.1–24%, cow 10–12%, bear 15–22% of
height.

**Deer run:** the foot is down 6–9 of 32 frames, and the lift is 57–63% of H.

## Deer construction, as an example of a medium quadruped

**Rig, 39 bones:** a root, five spine bones, a hip and a shoulder centre, a hip or shoulder bone per leg, three or four
segments per leg and a foot, three neck bones, the head, a two-bone chain per ear, and the tail.

The hip and scapula bones sit at the top of each limb, inside the body.

**Geometry:**
- **Torso cross-section:** 7 vertices at mid-body, about 34 cm wide and 38 cm deep:
  - one under the belly;
  - two on each near-vertical flank;
  - a two-vertex ridge on top (a narrow plateau, not a single top vertex).
- **Torso side:** about 38 distinct stations along the body. The detail follows the silhouette lengthwise.
- **Legs:** 4-vertex rings at the joints only. Mid-leg they are about 4 cm × 1.5–4 cm, a flattened diamond. The upper
  legs are part of the body's flank. The hock sits behind the knee in a zig-zag. The hoof is a 3-vertex wedge.
- **Neck and head:** about 8 vertices per neck bone; the head bone has about 40.

**Photo against model, where the simplification happens:**

| Feature | Real deer | Measured deer |
|---|---|---|
| Body volume | round barrel, deep chest, tucked belly, muscular haunch | 7-sided boxy rings; the outline is kept, the roundness painted |
| Shoulder and haunch | visible muscle masses | flank vertices weighted to the hip and shoulder bones; the mass painted as light and shadow |
| Legs | slender, tendon-defined | 4-sided flattened prisms with rings at the joints only; the bind pose keeps the hock angle |
| Hooves | split, glossy, black | a 3-vertex wedge painted near-black |
| Head | long tapered skull, eyes, ears, wet nose | the densest area; eyes, nose and markings painted; ears are closed cupped shells on their own bones |
| Fur and colour | thousands of hairs, white belly and rump | hand-painted strokes in 3–4 tones, white patches as soft-edged shapes, lighting baked in |
| Texture layout | — | one 256 × 128 side pelt shared by both sides |
| Motion | complex | idle fidgets, walk, run and die clips on 39 bones |
