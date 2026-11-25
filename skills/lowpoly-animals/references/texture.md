# Texture: coat layers, eyes, noses, the head and feet

The detail behind SKILL.md §6. Read it before painting. Skin types other than fur are in `skin-types.md`.

- **Paint the anatomy: the coat carries the form, in three layers of different sizes.** Measured on the torso of the dog,
  bear, deer, pig and mule in a side render of the texture alone (`lib/lowpoly/tools/body_study.py`; numbers in `references/reference-measurements.md`). The
  layers are separated by blurring over 5% and 1% of the body's length:

  | Layer | Size | What it is | Measured (brightness sd) | A first build that skips it |
  |---|---|---|---|---|
  | **Light and colour zones** | over 5% of the length | the top-down light, the belly, the markings | 0.035-0.043 | 0.026: about right |
  | **Form shapes** | 1-5% | the muscles, the ribs, the joints' creases and folds, the rims of bulges | 0.014-0.034; the darkest and lightest 5% at -0.023 to -0.048 and +0.023 to +0.050 | 0.009 (±0.015): flat |
  | **Fur strokes** | under 1% | the hair | 0.013-0.049 | 0.008 |

  What the form layer draws (look at the measured coats with the light and the strokes taken out):
  - **The big masses outlined:** the haunch as a ring of light with a dark edge behind the thigh (the mule's is a clear oval),
    the shoulder blade and the line of the upper arm, the ribcage's lower edge, the fold of the flank in front of the thigh;
  - **The joints as crease-and-rim pairs:** a dark crease on the inside of the bend, a light rim on the outside, at the elbow,
    the hock, the wrist and where each leg meets the body. The deer runs pale rims down the backs of its legs;
  - **Tendons and the shin's edges** as thin light and dark lines down the legs;
  - **Neck folds and the dewlap** as soft vertical bands.

  **The coat checks measure the torso's side only.** The Kodiak passed all of them and still read as one flat shade: its
  "dark" leg and belly colours were within 0.03 of the body's (the legs a little lighter). Give the zones real steps
  (a grizzled back, chocolate flanks, a darker belly, legs darkening to the paw tops, while every limb stays at 0.15 or
  more), and paint the muscle masses as relief: each a dome with a rim about a fifth of its radius wide, shaded by its
  slope under a light from above and ahead, a little lighter at the crest. Broad gaussian bulges land in the large band
  and leave the form band flat (0.018); rimmed domes put it at 0.029, the measured bear's. Turn the strokes round whorls
  at the shoulder, elbow, haunch and knee, and light the knuckles on the paw tops.
  Strength: about ±0.03-0.05 at the darkest and lightest 5% (the cow's spots push its numbers far higher). A first build
  that paints only the large light and a few blurred blobs reads as flat colour, however good its silhouette.
- **Surface: strokes that follow a flow over the form, not one direction.** Short directional strokes along the hair or
  feather flow, with slight hue and value noise and 2–4 base colours. The noise must be **low frequency along the flow and
  high frequency across it**; swapped, it paints stripes across the body. Use finer, weaker strokes on small parts.
  - **The flow changes direction over the body:** down the shoulder and the legs, along the back, round the haunch and the
    elbow, back from the face. Measured coherence of the strokes over the whole torso is 0.06-0.28 (0 = no shared direction,
    1 = all parallel). Within a window of 5% of the length it is 0.24-0.33, and the local directions spread over about ±70
    degrees.
  - **A single noise oriented along the body** gives coherence 0.74 everywhere: parallel scratches over the whole coat, with
    nothing to say where the shoulder or the haunch is. Drive the stroke direction from a flow field over the body: an angle
    per region, blended like the painters (`lowpoly-core/references/texture-method.md`, "Continuity").
  - **A flow field alone can still be too tidy.** The test fox and cat had flow fields and measured 0.37-0.40 overall and
    0.49-0.50 locally. What loosened them, measured on the side render each time:
    - the angle wandering by about ±50 degrees in clumps (it was ±40);
    - strokes 2-3.5 times longer than wide (they were 3-5 times);
    - 20-25% of the stroke layer as direction-free breakup.

    That gave 0.14-0.18 overall and 0.27-0.28 locally. The coherence is very sensitive to the length-to-width ratio: on the
    fox, 3.0 gave 0.16 and 2.0 gave 0.01. Looser strokes also put more contrast into the form band, so check the form layer's
    darks and lights again after.
  - **Bold markings skew the stroke numbers; judge the strokes without them.** The coherence is weighted by contrast, so
    one crisp, high-contrast line running along the body outweighs the whole coat of strokes. The test anteater's cream
    stripe on its black band held the torso at 0.37 overall and 0.35 locally with the strokes following a flow field. With
    the band and stripe painted out, the same coat measured 0.22 and 0.30, in range, and its form layer fell from 0.048 to
    0.026. The large and form layers read high for the same reason, as the cow's spots do.
    - **To judge the strokes,** build once with the markings painted out, measure, then put them back.
    - **Don't soften or hide a species' markings** to pass these checks.
    - **Scale the stroke length to the animal:** a stroke is under 1% of the body's length. Strokes 3.3 cm long on the 2 m
      anteater (1.6%) spilled into the form layer and turned the coat into camouflage blotches; at 1.4 cm they read as hair.
  - **Keep each layer at its own size.** Breaking the strokes up with a blotchy noise as big as the form shapes makes the
    coat camouflage-patterned and hides the anatomy under it. The test fox did this on its first try: the numbers were in
    range, the coat was not. Break strokes up with noise finer than a stroke, and let the form layer alone own the 1-5%
    sizes. Look at the form layer as an image, not only its numbers.
  - **Bend the hair round a mass; don't draw a whorl.** A flow that circles the haunch completely paints a bullseye. The ring
    on a measured haunch is the muscle's outline in the form layer, with the hair only bending round behind and below it.
- **Faces: small details are crisp at their centre and blend at their edges, never decals.** The eye, the nose and
  mouth, beaks, the species' colours and blur follow.
- **Eyes: a stack of zones, crisp at the centre and soft at the edge.** The shape, lids and corners of a side-facing eye
  (horse, cow, deer) are in `references/eyes.md`. Measured round the eye in the textures of the
  dog, cow, deer, bear, pig and mule (`lib/lowpoly/tools/eye_study.py`; the numbers are in `references/reference-measurements.md`). Every one paints
  the same stack, from the centre out:

  | Zone (in eye radii) | What it is | Measured |
  |---|---|---|
  | **Catchlight** | one or two texels, in the upper half of the eye | 0.55-0.89 brightness: the brightest texel round the eye, often of the whole head. Every model has one |
  | **Eye body** (0-0.8) | the iris and pupil, mostly one dark shape | 0.00-0.06 at its darkest; 0.25-0.63 below the coat on light and mid coats. On a dark coat (bear 0.13) the catchlight and the rim carry it |
  | **Rim** (0.8-1.2) | the lids: a band right round the eye, either a dark lid line (pig, cow, mule) or a pale ring (the deer's cream ring, the cow's yellow lid). A dark lid is **a deeper shade of the coat**, not black: densest at the eye's edge, fading out into the fur, the upper lid stronger than the lower | brightness spread 0.08-0.22 inside the band. Profiles across the lids (below): 6-63% darker than the fur, 1-4 texels wide at half depth, back to the fur's value within 1-3 texels, the coat's own hue |
  | **Socket** (1.2-2.6) | the eye's surround, one soft value shift away from the coat | darker on most (dog -0.07, pig -0.11, cow -0.2 to -0.5), lighter where the species has a pale ring (deer +0.18, mule +0.07); never the coat's own value |
  | **Above against below** (1.5-2.6) | brow shadow over a lighter cheek | differ by 0.05-0.19 on four of the six |
  | **Form strokes** | one-texel lines that follow the anatomy: the brow crease (dog, cow, pig), the lash line (pig), lid creases (mule), a line running forward and down from the inner corner (deer) | 1-3 per eye |

  - **Size, in texels:** the eye is 4.4-7 texels wide at the measured heads' 93-214 texels per metre, and the whole stack
    out to the socket's edge 12-17 texels. On the model that is a radius of 15-25 mm, about 1.5-2 times a real eye: eyes
    are enlarged to read. With a denser texture, scale every zone up in texels to the same size on the model.
  - **The species' colour lives inside the stack.** A bright iris (amber, blue, yellow) is a ring inside a dark rim, with a
    dark pupil and the catchlight. An iris near the coat's own value (amber on a red fox, brown on a brown dog) disappears
    unless the rim and pupil are dark: check the value step, not the hue.
  - **Crisp at the centre, soft at the edge.** The catchlight and the eye body's edge (where the lid meets the eye) stay
    sharp at the texel; a blur over them is what turns an eye into a smear. Paint near-black and near-white only there, a
    texel or two of each. **Everything outward of that edge fades:** the lid line and the socket grade into the fur.
  - **The lid line blends into the fur; it is not an outline.** Measured as brightness profiles across the upper and lower
    lids:

    Upper lids are 8-63% darker than the fur, lower lids 0-92% (usually less than the upper), 1-4 texels wide at half depth,
    and back to the fur's value within 1-3 texels (`references/reference-measurements.md`, "Eyes").

    - **Colour:** the lid keeps the coat's hue and only darkens it (the werewolf's lid is its own blue-grey, deeper and a
      little more saturated). Mix toward a darker shade of the surrounding paint, not toward a fixed black.
    - **Shape:** densest right at the eye's edge, then fading outward; the upper lid usually darker and wider than the lower.
    - **Near-black only** on a dark coat (the bear) or a species with a real black liner (a fox), and even then fading out.
    - **The failure:** the test cat's first lid was a near-black ring of one strength all round, crisp on both edges, as dark
      below the eye as above. A reviewer read it as a thick, harsh outline. Repainted as a deeper shade of the fur, about 50%
      darker at the upper lid and 30% at the lower, fading over several texels, it sat in the face.
  - **The corners blend: the lid line neither stops dead nor runs on as a line.** At the inner corner (toward the nose)
    the lid line widens into a dark pocket. Anything leaving it, such as a canid's or cat's tear mark, is a soft wedge that
    is darkest at the corner and tapers and fades away from it. Measured on a red fox photo, in eye widths along the mark:
    - the fur is darkened 96% at the corner, 64% at 0.5, 35% at 1.0 and 17% at 1.3;
    - its width at half depth goes from 0.45 to 0.15 of an eye width;
    - its colour is a darker, more saturated shade of the coat (a warm brown on a red fox), not grey;
    - the wet lid catches a thin, cool light rim along the pocket's edge.

    The measured models grade the darkness out from the eye's edge over 2-4 texels (mule 0.08 to 0.35, cow 0.08 to 0.52, pig
    0.29 to 0.59); none draws a full-strength line out of the corner. The test fox's first tear mark was a line about 1.5
    texels wide at one strength for its whole length, and a reviewer saw it at once as drawn on. See `references/reference-measurements.md`.
  - **Check it in code:** measure the zones round the eye's texel and compare with the table. The failure it catches is a
    single soft blob in the coat's value, which looks like an eye in the texture and disappears on the model: the test
    fox's amber eye was 0.08 *brighter* than the orange round it, with no catchlight (its brightest texel 0.44), a rim
    spread of 0.03 and no socket shift.
- **Noses and muzzles: a lit box with a dark, structured nose.** The table is for a nose with a pad (dog, bear, cow, pig). A
  horse has no pad, and a grey horse's muzzle is dark skin under thin hair: build and paint those from `references/muzzles.md`. Measured on textured head renders of the dog, bear,
  cow, deer, pig and mule, where every model's paint is seen in the same front and side views (`lib/lowpoly/tools/nose_study.py`;
  the numbers are in `references/reference-measurements.md`):

  | Part | What it is | Measured |
  |---|---|---|
  | **Nose** | the darkest mass of the muzzle | mean 0.05-0.12 (the pig's pink disc 0.19, still 0.23 under the muzzle round it). 0.33-0.66 of the muzzle's width in front (dog, mule, deer), or the whole front as a pad (bear, cow) |
  | **Its lit top** | a lighter band or rim across the top of the nose | the brightest 5% is 0.07-0.17 above the nose's mean (0.15-0.27). On a fox photo, a glossy band of 0.38 with highlights to 0.66 and above |
  | **Nostrils** | two dark commas or ovals, darker than the nose, each with a lit rim on its upper or outer side | 0.00-0.13 |
  | **The muzzle round it** | fur set off from the nose, often lighter than the face (a mealy muzzle, a pale band behind the nose) | 0.13-0.34 brighter than the nose; muzzle against face from -0.28 to +0.05, by species |
  | **Bridge against side** | the muzzle's top is lit like the back: it is a box under a light from above | the bridge is 0.03-0.41 brighter than the side near the nose (dog 0.03, mule 0.09, pig 0.13, bear 0.19, cow 0.41) |
  | **Mouth line** | a dark line from under the nose back to the corner of the mouth | 0.00-0.21, near-black on the dog, bear and cow; 0.05-0.25 darker than the lip above it. On the fox photo, dark under a white lip |
  | **Chin and lower jaw** | shaded, even where the fur is white | darker than the lip on most (dog, bear, cow 0.00-0.16). The fox photo's white chin is 0.60 against a 0.97 lip |

  - **Paint the species' colours on top of this lighting**, not instead of it. A white lip still has a dark line under it
    and a shaded chin; an orange muzzle still has a lit bridge.
  - **The nose is not one flat dark shape.** Its lit top and its nostrils are what make it read as a nose. A flat dark cap
    reads as a hole or a smudge, under the engine's lights especially.
  - **Check it in code:** render the head textured and flat-lit, front and side, and measure the parts in the table.
    The test fox failed on four of them: its nose had no lit top (+0.05) and no nostrils darker than the leather; the
    bridge was no brighter than the side (0.19 against 0.18); the mouth line had no contrast with the lip (0.21 against 0.22);
    and the chin was lighter than the lip.
- **Beaks:** darker toward the tip, with a lit ridge along the top.
- **The species' colours stay** (a pink snout, a yellow beak) but are graded, darker toward the nostrils or the tip.
- **One coat from rump to nose: the head grows out of the neck, it isn't a separate decal.** measured on the mule
  and deer in slices along the body:
  - the head is the same tone as the body (mule 0.35 against 0.34, deer 0.44 against 0.40);
  - the same hair-stroke style runs the whole length;
  - only the detail rises, gradually, over the last three or four slices toward the face (spread 0.05 → 0.12–0.17);
  - no step between neighbouring slices is bigger than about 0.14 (RGB distance), except the species' own markings.

  If the head is painted by its own code path, blend it in over the length of the neck rather than switching at one z.
  Otherwise the pelt shows a vertical seam, and markings that cross it (a throat band) are cut off. Use one stroke
  noise everywhere, scaled finer toward the face, not speckles on the body and streaks on the head.
- **Soft is not flat: the head still needs strong values.** Measured inside the head's UV footprint of the measured heads:

  | | Brightness spread (sd) | Darkest to lightest | Edge strength (per pixel) |
  |---|---|---|---|
  | Dog, bear, pig | 0.10–0.12 | about 0.0–0.6 (pig 0.13–0.82) | 0.06–0.09 |
  | Deer, cow | 0.17–0.31 | 0.0–0.96 | 0.10–0.11 |

  Every one has a dark jaw and underside, light painted along the bridge of the nose, hair strokes toward the nose,
  the eye in a darker socket with one small, bright catchlight, and a lit nostril rim. A head painted in one dark tone with a
  blurred eye reads as a smear even at a higher pixel density. Measure the spread and range in code after painting.
  Edge strength falls as resolution rises, so compare it at similar pixels per metre (measured heads: 120–200 px/m).
- **Feet: what is painted on them.** Their shape is geometry (§3, rule 5: a splayed wedge, with toe and claw geometry on
  clawed species); the rest is paint. Measured on the foot triangles
  (centre below 8% of the animal's height) of the measured bear, dog, cow, deer and pig:
  - **Pixels:** 85–235 px/m, about the same as the leg. Most feet get **their own small patch** of the texture, not
    just the bottom of the leg strip: the bear's paws have a strip each, the dog's front paw has a patch, and the
    pig's sole is a top-down disc.
  - **Contrast:** feet are among the most contrasty areas: brightness spread 0.09–0.31, range about 0.0–0.7, edge
    strength 0.06–0.17.
  - **What is drawn:**

    | Animal | Painted on the foot |
    |---|---|
    | Bear | Fur strokes running down onto the toes, dark gaps between the toes, long pale claws as light vertical strips |
    | Dog | Three or four dark notches between the toes, lighter toe tops, small dark nails |
    | Cow, deer | A solid dark hoof band or wedge, with the cleft between the two toes as a light line |
    | Pig | The sole unwrapped as a disc: pink skin, a dark rim, the two toe tips at the front with a dark split |

  - **What is left out (the mammals' paws and hooves):** individual toe geometry, modelled claws or nails, separate hoof
    halves, dewclaws and pads. Reptiles, rodents and clawed beasts build their toes and claws as geometry (§3, rule 5).
    The underside is mostly untextured, except the pig's disc.
  - **Colour against the leg:** hoofed feet are darker than the leg (pig −0.13, deer −0.24). Clawed paws are a little
    lighter (bear +0.04, dog +0.06) from the pale claws and toe tops.
  - **How to give a foot its own patch in code:** the side-view pelt squeezes the front of a paw into a sliver, so toes
    can't be painted there.
    - **The unwrap:** map the paw triangles all round: u = the angle round the paw centre (toes in the middle, the heel
      at both edges, mirrored for the far side), v = the height from the top of the paw to the sole.
    - **Give the toes more room:** warp u so the front half gets about two-thirds of the width, with a finite slope
      at the toes, or the middle stretches.
    - **The heel seam:** unwrap triangles that cross it, give them their own duplicate corners, and keep a few pixels of
      margin painted.
    - **What to paint there:** chunky features, 2+ pixels wide. One-pixel toe lines vanish.
  - **The test:** a foot painted as a plain gradient of the leg colour (brightness spread under about 0.05) reads as a
    stump.
- **Beaks and horns:** dark or saturated accents with soft edges.
- **Markings** (bellies, points, stripes, masks, wing bars) become clear shapes with soft edges.

## Pupil shapes by animal

The pupil's shape tells the viewer what animal it is as much as the iris colour does:
- **Cats (and foxes):** a vertical lens, widest at the middle and tapering to soft points top and bottom. In daylight a calm
  cat's is about a third of the iris wide. A constant-width dark bar reads as a reptile's slit (the housecat's first eyes).
  Add faint radial fibres and a darker ring at the iris's edge.
- **Reptiles (crocodiles, geckos, snakes):** the narrow constant-width slit is right here.
- **A slit pupil and the eye checks:** `lp check` finds the eye's radius from its dark core. A slit (a core 2.5 or more times
  longer than it is wide) is recognised, and the eye is then measured to the iris's edge: before that, a fox's rings fell
  inside its amber iris (the red fox v2 read catchlight 0.41, socket 0 and size 0.94 with a 0.90 catchlight painted). If
  the report's eye width still looks like the pupil's, give the iris's half-width and half-height in the spec's `"eye"`.
- **Dogs, wolves, bears, birds of prey:** round.
- **Horses, goats, sheep, deer:** a horizontal bar or oval.
- **Hostile mobs** (`lowpoly-core/references/temperament.md`): often no pupil at all, a soft glow.


Continuity and seams, the lights, texel density, stretched faces, limb detail and pale coats are in
`lowpoly-core/references/texture-method.md`.
