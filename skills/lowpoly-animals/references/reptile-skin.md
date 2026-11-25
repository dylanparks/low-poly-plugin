# Reptile skin: scales, plates, beads and the underbelly

The standard for painting a reptile's hide (a lizard, a monitor, a crocodilian, a dragon). It was built over nine rounds of
the Komodo dragon and measured against two of the reference game's reptile monsters, the reference drake and the reference dragon, with their texels mapped back
onto their meshes. Read `references/skin-types.md` first for the measures every skin is checked against; this file is how a
reptile meets them.

## 1. Zones: each part of the body gets its own scale

| Zone | Scale | Why |
|---|---|---|
| Head | Small irregular beads (10-15 mm), soft seams | Knobbly skull scales; the part the camera sees close |
| Back (top) | The head's beads, a little larger (15-18 mm), growing about 25% as they fade | The reference dragon's top and sides carry different scales; the user asked for the head's on the Komodo's top |
| Sides and legs | Plates in a wavy diamond grid | The grain shows which way the body runs |
| Feet and toes | The head's beads, finer (about 10 mm) | A grid laid round the leg's axis smears into streaks on splayed toes |
| Belly | Smooth skin in soft transverse rolls contoured to the muscle (section 5) | Both reference bellies |
| Tail underside | Plain rolls (about 0.085 m on the Komodo) | |

Every zone blends into the next over a broad band, and all of them share one colour scheme (section 4).

## 2. Lay the pattern on the surface, not in space

A pattern with a grain needs a coordinate on the skin itself.
- **Body:** along = the distance from the nose; around = the angle from the spine, read from the top line, the bottom line
  and the half-width at that station (`phi`: 0 on the spine, 1 on the belly's midline), times the half-perimeter.
- **Legs:** along = the distance down the nearest leg segment; around = the angle round its axis times the leg's radius.
- **Choose zones by position, never by facing.** Weighting the belly by a normal that points down switched pattern and
  colour face by face: a hard tan-to-grey line on a low-poly body. Use `phi`.
- A 3D Voronoi with no surface coordinate is fine for beads, which have no grain. Plates and belly rolls need the surface
  coordinate.

## 3. Plates (the sides) and beads (the head, back, feet)

**Plates.** A wavy diamond grid in the surface coordinate, about 1.35 times longer along the body than across, warped by
low-frequency noise (the drake's rows wave). Each plate is lit on its upper, leading edge with a bright rim just inside
the seam, darkens toward its lower, trailing edge, and has a thin shadow under that edge. The seam is a narrow line in a
deep shade of the plate's own colour. Sizes grade: largest on the flank, smaller down the side, at the neck and on the
tail.

**Not domes.** Round cells lit from their centres and ringed by near-black grout, with no grain, read as cobblestones
(the Komodo, round 2).

**Beads.** Irregular cells of uneven size (weights 0.8-1.2) with soft, wide seams (the seam ramp 0.04-0.17 of a cell), a
lit dome, a dry glint on a few, a scatter of pale speckles (about 7% of cells) and of darker cells (about 10%).

**Texel density.** At least 8 texels across a plate. The Komodo went from 260 to 330 texels a metre on the body by
filling half of a 512 x 512 sheet that had been left empty: check how full the sheet is before accepting a low density.

## 4. Crossfades and one colour scheme

**Fade broadly.** The back's beads meet the side's plates over a broad, noisy band: the pattern over about a quarter of
the way round the body (`phi` 0.24-0.48 on the Komodo), the colour over a wider band (0.18-0.56), so the plates take the
top's colour before the beads take over, and the beads warm toward the sides as they thin out. A band a tenth as wide
read as an abrupt line. The feet blend in up the lower leg the same way.

**Match the colours by measurement.** Measure each zone's mean hue, saturation and value (in the texture, or by sampling
the paint function at points in each zone) and bring them within a few points of each other. The Komodo started with a
grey back (39 degrees, saturation 0.23) on ochre sides (36 degrees, 0.40), a grey head (0.20) and grey feet (0.24).
Matched, every zone sits at 37-38 degrees and saturation 0.29-0.36, with the feet a little darker (value 0.55 against 0.61),
as feet should be. What moved the gap was adding the sides' ochre to the top; adding grey to the sides alone barely did.
Then lay **one large warm-cool mottle over every zone**, so colour patches cross the boundaries.

## 5. The underbelly: soft rolls contoured to the muscle

**Measured on both reference bellies:**
- **Rolls, not lines.** A stack of soft transverse rolls, about 15 texels each (the drake 9-20, the dragon 13-22). Thin dark
  crease lines on a pale belly read as a sketch.
- **Against the mesh.** The drake's belly is one quad wide a side, from the midline to a side vertex 0.17-0.28 m out. A
  groove lies on every row of belly vertices (within a texel or two of all six rows: where the mesh bends), and most quads
  get one more between. The dragon tiles one belly strip along its whole underside instead, its grooves ignoring the rows.
- **The groove:** a soft U, its floor 0.6 of the roll's brightness (0.43 against 0.70), in the skin's own hue, darker and
  more saturated (hue 62 degrees in both, saturation 0.39 against 0.28): never grey, never black.
- **The highlight:** blurred and blotchy, about 40% of the way down each roll from the groove above.
- **Across the belly:** the grooves are deepest just off the midline and gone at the belly's edge. The belly is shaded as a
  cylinder, brightest on the midline (0.68) and darkest at its edge (0.31), and about twice the flank's brightness.
- **The edge:** the flank's scales lose their detail over 15-20 texels; the drake adds a soft dark valley about 6 texels
  wide where they end.

**Contour to the muscle, in a few large masses.** Grooves placed by the distance from the nose alone make flat rings: the
user asked why the belly ignored the muscles, and then said the next version had far too many ripples next to the drake's
abdomen (two pectorals, a rib line, about three rows of abdominal masses). Lay the belly out in regions, each with its own
groove field and a deeper groove on every boundary, and shade each mass as a swell, brightest at its crown:
- **Throat:** a few loose transverse gular folds (about 0.06 m apart on the Komodo), sagging back toward the midline.
- **Chest:** the deep pectoral, one swell a side, two or three folds fanning from the armpit toward the breastbone, and a
  soft V between the swells with its point back on the midline.
- **Ribcage:** an arc closing the chest, its apex back on the midline.
- **Abdomen:** rectus segments of about 0.10 m on a 1.3 m trunk (four of them), bowing toward the tail at the midline and
  split by a shallow midline groove.
- **Groin:** two or three folds fanning from each thigh toward the vent, narrowing in a V.
- **Grooves a third of a roll wide** once the rolls are this large, not half.

**Lit from below.** A face that points down gets the ground light only (a dim blue-grey hemisphere colour in the viewer),
so a belly painted pale reads grey from below, its highlights barely show, and the grooves carry the form. Paint the belly
paler and warmer than the flank, and keep the grooves shallower than the measured 0.6 (the Komodo's floor: 0.74), or they
read as stripes.

## 6. Checks

1. **Draw the belly flat first**, with the midline down the middle and the nose at the top, before painting it on the
   model. It showed the Komodo's first chest (a dozen lengthwise arcs) and its ripple count at once.
2. **Look from below and from the 3/4 camera** in the viewer, zoomed in on the flank, the boundary between top and side,
   the feet and the belly.
3. **Measure each zone's hue, saturation and value** (section 4).
4. **lp check:** the scales checks (crevices 6-24, edges 21-42, fine 0.08-0.13, gloss 2-20) and the texture seams. The
   Komodo held 13-15 / 38-41 / 0.088-0.094 / 3.0-3.7 through every round.

## 7. What each Komodo round taught

| Round | Change | Lesson |
|---|---|---|
| 2 | Round beads in a 3D Voronoi over the whole body; a belly grid switched by facing | Cobblestones, and a hard line at the belly |
| 3 | Diamond plates on the surface; the belly by position; 260 to 330 texels a metre | The grain and the plate shading make scales read as 3D |
| 4 | Belly rolls measured on the drake and the dragon | Rolls, not lines; shallow grooves under ground light |
| 5 | Rolls contoured to the muscle regions | Masses with grooves between them, not rings |
| 6 | Fewer, larger masses; the head's beads on the back and feet | About four abdominal segments; no grid on toes |
| 7 | A broad crossfade, the colour wider than the pattern | A narrow band reads as a line |
| 8-9 | Every zone colour-matched by measurement | One hue and saturation everywhere; one shared mottle |
