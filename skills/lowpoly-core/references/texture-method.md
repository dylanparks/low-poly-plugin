# Texture method: continuity, lights, density, stretched faces, limb detail, pale surfaces

The painting method behind SKILL.md §5, for any skin. What is painted on an animal (coat layers, eyes, noses, feet,
pupils) is in `lowpoly-animals/references/texture.md`.

- **Blur sparingly.** The era's soft look comes from the texel size, not from blurring: paint at the game's density
  and let the texels soften it. If a patch is blurred, leave the eye's centre out, and blur patches that share an edge the
  same way, or their seam shows (the test cat's face and muzzle patches jumped 0.4 when only one of them was blurred).
- **Continuity: the texture must not change at a hard line anywhere on the skin.** measured on the dog, deer,
  cow, mule and bear (`lib/lowpoly/tools/uv_study.py`):

  | | Measured models | A first build that ignores the rules below (typical) |
  |---|---|---|
  | Colour jump across UV seams (RGB distance, median) | 0.07–0.10 (cow 0.34, its spots) | 0.15–0.19 |
  | Worst 10% of seam jumps | 0.16–0.26 | 0.40–0.68 |
  | Up- and down-facing faces stretched more than 4:1 | 8–19% | 31–35% |
  | Pixel-density spread (1 sd) | ×1.4–2.1 (deer 3.5) | ×12–15 |

  **The simplest way to get there: paint every texel from the 3D point it maps to.** Rasterise each UV triangle into
  the texture, interpolate its corners' 3D positions per texel (and spread the result a few texels past the edges), and
  paint each texel by its 3D point and its patch. When every patch starts from the same pelt colour at the same 3D point and
  adds its own detail (an eye, a nose, toes) only inside, the two sides of a seam match by construction, and a patch needs
  no hand-tuned fade to the pelt or inverse mapping back to the body. On the test fox this gave a seam jump of 0.010 median
  and 0.027 worst 10% on the first build, with seven patches. **One exception:** the fur strokes and noise on the side
  pelt follow the texture's own unrolled height, not the 3D point (below, "the ridge strip").

  Three causes, all invisible in the texture image and obvious on the model:
  1. **Hard switches in the paint code.** A painter that picks a branch per region (`if y < belly: legs`,
     `if z < tail_root: tail`, `if z > neck: head`) changes colour, painted light and fur noise all at once at that
     line. The fix: write each part as its own painter, then make the pelt a cross-fade of them over a transition zone
     (2–6 cm: body to legs below the belly line, body to tail at the root, body to head at the neck). One fur-stroke
     function, scaled, everywhere.
  2. **Stretch turns a hard line into a staircase.** A planar side projection smears pixels across faces that point
     up or down (the back, belly, brisket) and forward or back. Any hard line crossing those faces shows as one-pixel
     stairs blown up to centimetres. Keep everything there smooth and low-frequency along the stretch, and never put a
     region boundary on a stretched face.

     **The worst case is the ridge strip along the spine.** A torso ring's two ridge vertices sit at the same height
     and are mirror twins in a mirrored pelt, so the whole strip along the back maps to a single pixel row. The fix is
     to unroll the back, the way the measured pelts lay it out:
     - give each torso and head ring a **spine vertex** on the midline (7 sides become 8);
     - in the UVs, lift that vertex above the side silhouette by about 0.8–0.9 × the ridge's half-width (its arc
       length over the back), so the back gets its own band of texture above the flank;
     - paint that band as the back: the painter's height fraction just clamps to 1 above the silhouette top.
     - **Key the fur and the noise to the band's own height (the texture's v), not to the point's true height.** Across
       the band the true height hardly changes, so strokes keyed to it vary only along the body. On the model they show as
       stripes across the top of the back and the head. The test fox did this when its texels were painted from their 3D
       points, and the reviewer saw bands across its forehead: the same stretch the band exists to prevent. Take the colour
       zones, the light and the form from the 3D point, and the strokes from the unrolled layout. Near a patch's edge, blend
       back to the true height so the seam still matches.

     Keep the band clear of any patch painted above the body in the texture. It costs one vertex per ring and takes
     the badly stretched up- and down-facing faces from about a third to under 5%. A single belly vertex with sloping
     faces each side needs no unrolling.
  3. **Patches that don't match the pelt at their seams.** A separately painted face, foot or ear patch borders the
     pelt along a UV seam. Make both sides match:
     - put the seam ring of vertices on the patch's edge row (not at a computed height that misses it);
     - fade the patch toward the pelt's own colour at the same 3D point over its outer 20–35%;
     - where a patch has two sides (ear front and back), give both the same fur colour at the shared edges.

  **Check it in code after every texture change:** for each UV seam edge, compare the texture colour on its two sides
  at a few points along it. The median jump should be at or below about 0.10 and the worst 10% at or below about 0.25.
  List the worst seams' 3D positions to find them. Also keep paint boundaries a few millimetres off silhouette lines:
  vertices on a silhouette sample both sides of a boundary and show as stripes.
- **Judge the colours under the viewer's lights, with smooth normals.** A flat-lit render hides faults that show only in the
  engine: an upward-facing surface is the brightest on the model and a strip of one, like a lip rim, can read as a glowing
  line, while side and lower faces fall into shadow. Render with the viewer's shading, its smooth vertex normals and its
  bilinear texture (`lib/lowpoly/tools/lit_view.py` or `lp preview`, which since 2026-11-23 shade as the viewer does: sRGB, Lambert, 1/pi).
  An earlier version of these renderers lit up-facing texels about 2.8 times too bright, and colours darkened to suit it
  came out muddy in the viewer (`references/common-failures.md`).
  **Then confirm it in the engine or viewer itself.** A stand-in renderer only approximates the engine's light falloff and
  colour handling: on the test fox the stand-in rendered far brighter than the viewer, so colours darkened to suit it looked
  dull and brown in the viewer and had to be brought back up. Take the final colour decision from the real renderer.
  Reload the texture with the model: a viewer that caches textures by name shows the old texture on new geometry, which
  once made freshly painted claws look unpainted.
- **Sample a patch's base colour at the point's true position, not at one fixed coordinate.** A patch painted over the skin by
  sampling the pelt at a constant z came out streaked in horizontal bands, because the scales' pattern then varies only with
  height; take z from the patch's own mapping.

## Texel density and skipped pixels (from SKILL.md §5)

- **Pixel density: the head gets more than the body.** The player looks at the head, which holds 20-30% of the vertices
  but a small part of the length. Map the side projection in two stretches of z, with the break at a head ring: the body
  and tail get the first part of the texture's width, the head the rest. The painter works in world coordinates, so only
  the pixel size changes. On the 12 m test animal this gave about 80 px/m on the body and 140 px/m on the head (measured
  heads: 120-200 px/m). Put the break exactly on a ring, or triangles that cross it sample the wrong place.
- **Skip pixels no triangle uses.** On a large pelt most pixels are empty. Rasterise the UV triangles first (with a few
  pixels of margin) and paint only those: it cuts the paint time to a few seconds.

## Faces the projection stretches: give them their own patch (from SKILL.md §5)

A planar projection paints well only the faces that face along its axis. Faces turned away from it get a sliver of texture
smeared across them, in bands: under the side projection, these are faces that face forward or back, up or down.
- **Measured:** the measured models have 8-19% of their up- and down-facing faces stretched more than 4:1.
- **The check:** `lp check` reports the share (`texture.stretch`). List the worst faces by position too, to see which part
  they belong to.

**First ask whether the shape is right.** A flat panel that the anatomy doesn't have is better fixed in the geometry, and
that removes its stretch too:
- the unrolled spine band above;
- the T. rex's groin, raised into a recess (`lowpoly-animals/references/limbs.md`).

**Then give each remaining group its own patch,** projected along the group's own direction. Forward- and back-facing
groups are things like:
- a blunt nose and chin;
- the front of a chest or a foot;
- a tail's tip.

For the front, use u = |x| (mirrored, the midline at one edge) and v = height. The patch's vertices are duplicated along the
seam, so they keep their own UVs.

**Paint it from the neighbouring projection, unrolled round the edge.**
- **The rule:** paint a point a distance d in from the edge it shares with the side as the side pelt d further along.
- **On the T. rex's nose:** z = the last ring's z at that height, plus that ring's half-width there minus |x|.
- **What you get:** the patch matches the side faces along the seam with no fade, and the scales keep their size across
  the turn.
- **The alternative:** painting each texel from its 3D point (above) works too, as long as the pattern isn't keyed to the
  axis that barely changes across the patch. If it is, the patch comes out banded.

**Put it in a free area** at the region's density, add it to the painters' order and to the pixels that get painted, and
render it front-on and at 3/4 under the engine's lights.
- **On the T. rex:** the nose and chin caps faced forward and showed bands of smeared scales. With their own front patch,
  the bands were gone and the seams were unchanged (`lowpoly-animals/references/case-study-trex.md`, round 21).
- **Keep the mouth's colours off the outside.** Cap triangles that touch the inside of a mouth can show from outside. Give
  them the skin's patch too, or the palate's or floor's colour shows between the lips.
- **A strip shared by several parts needs a row per skin colour.** Parts mapped onto one strip (claws, teeth, toes) take the
  same colour at their roots, so the strip's root must match every skin they grow from. Where those skins differ (dark feet,
  pale arms), give each skin its own row with the same detail, or a change made for one part shows on the others.
- **Paint a part's patch as the neighbouring skin continuing,** not in its own palette: the same colour and darkening at each
  height, the same shading and the same pattern size where they meet. A foot painted in its own lighter palette showed a
  step at the ankle; painted as the leg continuing down, the seams halved.

## Detail on the limbs and wings of large animals

Measured on the reference game's large creatures (a bear, a drake, a dragon, a dark boss, a mechanical suit) with `lib/lowpoly/tools/region_detail.py`
(painted contrast at 2 cm and 8 cm over each region's brightness):
- **They keep a modest density and paint every part.** They have 55-200 texels per metre, even on a 15 m dragon, and their
  legs, arms and wings carry about as much detail as their bodies (fine + mid 0.17-0.64). The dark boss's limbs carry more.
- **No limb is near black.** The darkest limb measured is 0.17 mean brightness.
- **The giant bat had the resolution, not the paint.** At 235-241 texels per metre, its legs and wings were painted almost flat
  (0.13-0.15) at 0.08-0.09 brightness, so in the engine they read as black shapes while the head and body carried all the work.
- **Paint the limbs with the body.** Legs need muscle shading, joint creases, hair and pads; a membrane wing needs tone along
  and between the fingers, veins, fibres and wrinkles. `lp check` warns on texture.limb_detail (below 0.17) and
  texture.limb_brightness (below 0.15).


## White and pale coats: paint the form, not noise

A white animal is the hardest coat to read in low poly, because the geometry is coarse and white shows no colour change to
carry the shape. The form must be painted. Measured on the measured cow against the first alicorn (`region_detail.py`, plus the white
texels' brightness):
- **The cow's white is painted as forms.** The whites run from about 0.62 to 0.87, a warm grey-ivory, never pure white.
  Each mass has painted shading: a darker band under the belly, behind the shoulder, in the flank fold, down the backs of the
  legs, round the hooves and joints; lighter on the shoulder's top, the hip, the ribs' upper half, the forehead and the
  bridge of the nose. Form-scale contrast (8 cm) 0.15-0.19 on the body and legs; fine (hair) 0.08-0.12.
- **The alicorn's white was noise.** Its body measured fine 0.04 and mid 0.03 (about a quarter of the cow's): a uniform grey
  speckle laid over a flat value, so the body read as a white blob with grain, and the wings as a grey ruled sheet.
- **Paint it like a photo of a white horse:** the shadow side of every muscle (the shoulder's back edge, the forearm's inner
  face, the barrel's underside, the gaskin, the stifle, the hamstring line), the bones showing at the point of the hip and
  shoulder and the withers, the soft creases at the elbow, flank and throatlatch, a cool grey in the shadows and a warm
  cream in the lights. Hair direction comes second, as short soft strokes following the flow field.
- **Check it:** `lp check` coat.form and texture.limb_detail on the white regions, and the viewer, not only the preview.
