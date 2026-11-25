# Skin types: scales, plates, wet skin, chitin and membranes

The skill's texture guidance (§6) is measured mostly on fur. This reference covers the other surfaces. It is measured on
the animal-like monster models of the same late-1990s game as the measured animals (scaled, plated, wet, chitinous and furred creatures, all invented or exaggerated, so the construction is what carries over) with `lib/lowpoly/tools/skin_study.py` (a side render of the texture alone, the model 720 pixels long). Their textures were also
looked at texel by texel.

## Step one: which skins does the animal have?

Most animals have more than one. Decide per body region (back, flank, belly, head, limbs, tail, wings) before painting
anything, and gather close-up reference photos of **each region** (lowpoly-core §1). A side photo of the whole animal shows a crocodile's
scales as noise.

| Animal group | Skin types, by region |
|---|---|
| Mammals | Fur (§6). Bare hide where the species has it (pig, elephant, rhino: wrinkled skin, no strokes); horn, hooves and claws as plates |
| Lizards, snakes | Small scales: pebbled (round, not overlapping) or imbricate (overlapping, pointing back). Snakes and many lizards have wide transverse belly plates. Bigger scales on the head |
| Crocodilians | Plates (rows of keeled scutes) on the back, small pebbled scales on the flanks and legs, rectangular plates in transverse rows on the belly, square scales in rings round the tail with crests on top. Wet sheen |
| Turtles, armoured beasts | Plates (large scutes or osteoderms with thick seams), wrinkled scaly skin at the joints |
| Fish | Imbricate scales with a pearly sheen; fins as membranes |
| Amphibians | Wet skin: smooth, glossy, often bright markings; warts on toads |
| Dragons and other invented reptiles | Imbricate scales on the body, plates on the head and back ridge, membranes on the wings |
| Insects, spiders, scorpions, crustaceans | Chitin: hard segmented plates; hair where the species has it (tarantulas, bees); membranes on insect wings |
| Worms, larvae, slugs | Wet skin in soft segments: ring folds, no plates |

## What each skin type measures as

| | Fur | Scales | Plates | Wet skin | Chitin |
|---|---|---|---|---|---|
| Measured on | a wolf (and the coat study) | a dragon, a drake, a giant lizard, a crocodile-like beast, a sea serpent | an armoured beast | an amphibian, a fleshy burrower, a grub | three spiders, a scorpion, a wasp, a flying stinger, a crab-like walker |
| Crevices (pixels 0.10 darker than their surroundings) | 3% | 6-24% | 7% | 2-17% (the amphibian: markings and folds) | 3-12% |
| Edges (pixels changing by 0.12 to a neighbour) | 8% | 21-42% | 19% | 5-24% | 9-25% |
| Fine detail (sd) | 0.05 | 0.08-0.13 | 0.08 | 0.05-0.13 | 0.06-0.10 |
| Painted highlights (share; their saturation) | 1.5% (0.09) | 2-20% (0.17-0.51) | 9% (0.19) | 2-19%, broad and soft (0.04-0.43) | 6-15% (0.13-0.48: coloured gloss) |
| Repeat (a cell size, % of the body's length) | none | 1-6% (lizard 1, crocodile 1.5, drake 1.5-2.6, dragon 3, sea serpent 5.5) | 4-6% | none | segments along the body (4-6%) |
| Brightness range (5-95%) | 0.29-0.67 | 0.01-0.70 (the sea serpent to 0.99) | 0.06-0.63 | 0.02-0.92 | 0.00-0.78: near black to bright |
| Saturation | 0.16 | 0.18-0.44 | 0.22 | 0.11-0.43 | 0.22-0.78 |

**What separates them:**
- **Fur** has almost no painted highlights and few hard edges. Its detail is strokes (§6).
- **Scales** are the edgiest surface: a cell pattern with dark crevices round every cell.
- **Wet skin** has no cells. It has broad soft highlights and deep folds.
- **Chitin** spans the widest brightness range (near black to bright), with saturated, coloured gloss, bold symmetric
  markings and hard gaps between segments.

The engine has no specular light, so every gloss is painted, and the share of gloss is what tells wet skin, chitin and
scales from fur.

## How each is painted (from the texels)

**Scales** (the dragon, drake, sea serpent, lizard, fish):
- **Cells:** each scale is a cell with a dark grout line round it (1 texel at the game's density), a lit upper edge and a
  shaded lower part: a tiny dome lit from above. Give each cell its own small colour and value change (about ±0.05).
- **Imbricate scales** (the dragon, fish, the sea serpent's leaf scales) are offset row by row like bricks and point back and
  down; each one's free tip is lit. **Pebbled scales** (lizards) are round cells with no overlap; at small sizes the game
  paints them as a diamond lattice of dark lines 3-4 texels apart, with a coloured fleck in some cells.
- **Size grades over the body:** larger on the back, smaller on the flanks and at the bends (neck, elbows), wide
  transverse plates on the belly where the species has them.
- **Reptiles** (lizards, monitors, crocodilians, dragons): `references/reptile-skin.md` holds the full standard: which
  scale each zone gets, plates in a diamond grid on the surface (not domes), beads on the head, back and feet, broad
  crossfades, every zone colour-matched by measurement, and the underbelly.
- **Fish scales:** large rounded cells with a pearly interior of several hues, and coloured specks along the grout.

**The reptile underbelly** is soft transverse rolls contoured to the muscle, never crease lines: `references/reptile-skin.md`, section 5.

**Plates** (the armoured beast, crocodilian back scutes, turtle scutes, armour):
- **Overlapping armour** (a pangolin's scales, an armadillo's bands, a dragon's armour): `references/parts.md`,
  "Overlapping armour": one direction field, painted first, geometry only on the outline, and how plates behave when
  the body folds (rigid armour down to the neutral axis, the compressed side bare or painted).
- **Cells:** large cells (25-40 texels in the game's textures) with a thick dark seam (2-3 texels).
- **Each plate:** a lighter rim just inside the seam, a domed interior lit at the top, and often a single glint or a keel (a
  lit ridge line) or a spike.
- **Layout:** in rows along the body.

**Wet skin** (the amphibian, the burrower, worms, grubs):
- **The base:** smooth and low in fine detail.
- **The sheen:** broad, soft highlights on the top of each convex form, 10-20% of the surface on the glossy ones, smeared
  along the form rather than dotted. Deep dark creases at folds.
- **Markings:** spots, blotches or slime streaks, saturated, with soft edges.
- **Segmented bodies** (worms, larvae): ring folds, each ring lit along its top and dark in the crease below, sometimes
  pores.
- **Warts:** small domes, lit on top and dark below.

**Chitin** (the spiders, scorpion, wasp, crab, stinger):
- **Plates and gaps:** hard plates with dark gaps between segments, along the abdomen and on every leg segment.
- **Gloss:** each plate has a sharp, bright highlight stripe along its ridge or rim, often tinted. The base is dark and
  saturated.
- **Markings:** bold, mirrored about the midline, often with a coloured halo at their edges (the spider's yellow-orange-purple
  rims), which reads as iridescence.
- **Hair:** sparse fine strokes only where the species is hairy.

**Membranes** (dragon and bat wings, insect wings, fins):
- **Veins:** a network of veins (a Voronoi-like web of light or dark lines) with larger cells toward the trailing edge.
- **Values:** translucent mid-values, darker along the leading edge.
- **Insect wings:** high contrast: pale cells in black veins.
- **Moth wings:** dusty speckle with eyespots as concentric bands.

## Rules that carry over from fur

- **Key the pattern to the pelt's own layout,** not the 3D height (`lowpoly-core/references/texture-method.md`, "Continuity"). Cells keyed to the true height stretch
  across the unrolled back into stripes, exactly as fur strokes did.
- **Size cells on the surface, in texels.** Choose the cell size in metres from the photos, then check it in texels at the
  texture's density.
  - **Below about 3 texels a cell can't read:** paint a lattice or mottling at 3-4 texels instead (the measured lizard), or
    exaggerate the size.
  - **Large plates need 25 texels or more** for the rim and dome to show.
- **Mirror symmetry:** a mirrored pelt makes the back symmetric about the spine. Put a row of scutes or a marking centred on
  the midline so the mirror looks deliberate.
- **Light and form still come first** (§6, the coat's three layers). The cell pattern is the fine layer: under it, the
  large light, the colour zones (a dark back, a pale belly) and the form shapes still have to read.
- **Check the gloss under the engine's lights** (§6): painted highlights at 0.7-0.99 clip on surfaces that face up.

## Worked example: an alligator

**1. Decide the skin regions** (crocodilian, from the table):

| Region | Skin |
|---|---|
| Back | Plates: keeled scutes in transverse rows, about six across the middle of the back |
| Flanks and legs | Small pebbled scales |
| Belly | Rectangular plates in transverse rows, pale |
| Tail | Square scales in rings; two crests of raised scutes along the top, joining into one |
| Head | Small tight scales, knobbly over the skull ridges, smooth along the jaws |
| Whole animal | A moderate wet sheen (semi-aquatic) |

**2. Gather references:** photos of the back from above, the flank, the belly, the tail and the head, besides the skeleton
and the outline set of lowpoly-core §1. From them, measure as fractions of the body's length:
- the back scute (about 1.5% on an adult), the rows across the back, and the rows from the neck to the hips;
- the flank scale (about 0.3%) and the belly plate (about 1% by 1.5%);
- the colour zones: a near-black back, cream belly, the flank between them, darker bands across the tail.

**3. Map it:**
- **Side pelt:** carries the flank and tail. The back's scute rows go on the unrolled band.
- **Belly:** it faces down and is squeezed in a side projection, so it gets its own patch projected from below, laid out so
  the plate rows run straight.
- **Head:** a patch projected from above for the cranial scales.

**4. Paint each region from its own painter, cross-faded at the boundaries:**
- **Back:** a grid of plate cells, about 1.5% of the length, with a thick seam and a lit keel line per scute.
- **Flanks:** at a game texture the 0.3% flank scale is under 3 texels, so paint a pebbled lattice at 3-4 texels instead.
- **Belly:** rectangular cells in rows, pale, low-contrast seams.
- **Tail:** rings of square cells, with crests as lit spikes along the top (raised scutes are worth building as small
  geometry, like the feet's claws).
- **Over all of it:** the large light (darker toward the belly's turn, lighter along the back), and a few soft wet
  highlights on the back's convexities, 5-10% of the surface.

**5. Check it:** `lib/lowpoly/tools/skin_study.py` should put the scaled regions in the scale column above:
- crevices 6-24%, edges 20% or more, a repeat at the chosen cell size, painted highlights within range;
- the lit render (§6) should show no clipped gloss.
"""
