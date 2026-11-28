# Texture for characters

## Charts

A standing person can't share an animal's side-view pelt: the chest, the face and the shins face forward and would be
edge-on in it. Each region is unwrapped round its own axis, ring by ring: a row per ring, the angle round the ring across.

- **Body and head.** The torso and the head span the front midline to the back midline, with no seam on either.
- **Limbs and hands.** The legs, feet, arms and hands wrap all the way round, the seam on the inside where the camera
  sees least.
- **Mirrored, except the hair.** Both sides share the left's texels. The hair isn't symmetric: its chart wraps the whole
  way round, each side its own texels.
- **Density.** The head and hair at twice the body's density, the ear 2.6 times on its front and 1.6 on its back. The
  first build's face ran about 2 mm a texel: an iris about 6 texels across.
- **A separate piece gets its own chart.** Mapped to the nearest ring, it shares that ring's texels: the old ear was a
  blob of ear colour painted on the side of the head. The ear's front and back are two charts, each flat in the ear's
  plane, so the paint knows which side it is on. A rim vertex is shared by both faces, so its normal can't tell them.

## Seams between regions

- **A strip that mixes two regions goes wholly to one.** The strip from the jaw down to the neck's top ring alternates
  triangles with two jaw corners and two neck corners. Assigned by majority, its triangles alternated between the head's
  chart and the body's, painted with two lights: a sawtooth of light and dark under the jaw. Give the whole strip to the
  head, and give its lower ring its own row in the head's chart. Left to the nearest ring's coordinates, the throat
  overlapped the mouth's texels and showed the mouth's lines.
- **Make the two paints agree where the seam sits.** Down the neck to its top ring, the head's baked light becomes the
  body's formula. Anything painted on one side only (stubble) fades out before the seam.

## Paint placed by where the skin faces

Position chooses what is painted where (lowpoly-core's rule: "paint by position, not by facing"; a zone or colour
switched on each face's normal draws a hard line along the faces' edges). Facing does two smaller jobs, always from the
smooth, interpolated normal and through a soft ramp:

- **The face's features belong on its front.** Paint limited by depth alone reaches the jaw's underside, which lies
  inside the face's depth: fade the mouth's lines and shadows out where the skin stops facing forward (a ramp on the
  normal's forward share from about 0.15 to 0.45).
- **Shade by the mesh's own surfaces wherever possible.** Downward faces are in shade: under the brow ridge, the nose and
  the lower lip, the jaw's underside. Then the shading stays matched when the mesh moves.
- **The head's baked light is gentler than the body's.** The face's forms are small and steep, and the renderer lights
  the mesh as well. Darkening downward faces about 15% on top of the renderer's own lighting made a heavy chin.

## Options the player changes: masks and tone ramps

- **An option is a mask plus a ramp.** Each option (skin tone, hair colour) is a greyscale mask of the texels it recolours
  plus a ramp of colours. The viewer and the game recolour masked texels by `tone / painted`, keeping the paint's shading,
  so paint everything in shades of one mid colour.
- **Skin tone ramp.** Palest to darkest natural skin, the dark end following the Monk Skin Tone Scale (Monk 07-10, CC BY
  4.0), its deepest two warmed a little so the warmth runs smoothly along the slider. A little sheen keeps the painted
  highlights on the deepest tones. The first build's ramp: (238, 204, 179), (222, 177, 142), (198, 148, 110),
  (165, 115, 80), (130, 92, 67), (96, 65, 52), (64, 47, 35), (48, 34, 26).
- **Masks are exactly what was painted, mixed by share.** The brows are in the hair colour's mask, not the skin's. Masks
  mixed one after the other, or a hair mask wider than the brow's paint, left a pale halo round the brows on dark skin.
- **Hair colour.** Its shadows soften toward the platinum end, and a sheen keeps the highlights on black.
- **Check every option at its extremes:** the darkest skin, the palest and darkest hair, every body type.

## Hair painted along its flow

- **Build the flow field.**
  - **Whorl.** At the back of the crown, about 2 cm off the midline on the part's side, clockwise in most people (about
    70%).
  - **The part.** Hair diverges from it on both sides.
  - **Combing.** The swept side runs across and forward into the fringe.
  - **Gravity.** It takes over on the sides and the back.
- **Paint along it.** Clumps and strands are noise smeared along the flow by short streamline tracing (line-integral
  convolution): big clumps about 1.4 cm, medium clumps inside them, a few strands, and the layers' ends shading the layer
  beneath.
- **Two highlights** across the strands (Kajiya-Kay): a narrow bright one shifted per clump so the band breaks up, and a
  wider dim one masked by strand noise for sparkle.
- **What failed first.** Stripes round the head's axis, parallel stripes and repeating lock tips all read as wood planks;
  noise without flow read as marble.
- **The hair's mesh.**
  - **Edge.** Tips and notches alternating column by column, long locks in the fringe, a clean taper over the ears, short
    tips at the nape. One sawtooth all round read as goop.
  - **Standoff.** Each edge vertex is set a few mm off the real skin: 2.5 mm, 5 at the nape.
  - **Clearances.** The fringe's tips stop above the brows. The edge over the ears clears the helix's top.

## Attached pieces: the ear

The general method (blend the piece's normals with the skin's, a broad root, the root painted in the skin's shaded
tone) is `lowpoly-core/references/texture-method.md`, "Attached pieces". On the ear: its normals fully the head's at
the helix's root, the tragus and the two root points, about 0.55 over the shell; its back and the head's contact shadow
round its root both 0.40 toward the skin's shade.

## Hair that moves

The first build's hair is rigid. Hair that swings (a ponytail, long locks) takes spring bones baked into the clips:
`lp bake-springs` (`lowpoly-animals/references/locomotion.md`, the spring bones).
