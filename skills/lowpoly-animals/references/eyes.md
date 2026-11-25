# Eyes on side-facing, docile animals: the shape, the lids and the corners

For horses, cattle, deer and other animals whose eyes sit on the sides of the head. The zones round any eye (catchlight, eye
body, rim, socket) are in `texture.md`, "Eyes". Docile against hostile eyes are in
`lowpoly-core/references/temperament.md`. This file is about what makes an eye read as an eye rather than a button.

**The failure.** The first alicorn's eye was a round dark dot: 2–4 texels across, with the white coat starting one texel
from its edge. It had no lids, no corners and no tilt.
- **Its size:** in round 4 its radius was 5.6 mm on a 1.97 m animal (0.28% of the height). Round 5 raised that to 0.88%.
  The reference game's animals have 1.4–2.5%.
- **Its edge:** it fell from the coat (0.77) to the eye body (0.03) in a single texel.

Small, round, hard-edged and lidless is exactly a button.

## What was measured

All values are luminance (0 black, 1 white).

| Source | Eye radius | Shape | Lids | Inner corner |
|---|---|---|---|---|
| The reference game's cow (white face), 158 texels/m | 18–21 mm, 1.46% of the height | an almond about 11 × 7 texels with the lids (70 × 44 mm), its long axis rising toward the back | warm and saturated (0.40–0.49 against the coat's 0.16): a deeper shade of the skin, not black. Both lids fade to the coat over about 4 texels | the darkest texels of the eye (0.02–0.04), a sharp point set low, and a soft dark streak running down and forward from it |
| The reference game's mare, 94 texels/m | 31 mm, 1.79% | a large dark oval, 5.8 texels wide | pale concentric lid rings | a notch where the rings meet |
| A grey horse, head-on photo | — | foreshortened almonds | no outline anywhere. Steps from the coat: rim −0.21 to −0.27, socket −0.14 to −0.17, surround −0.07 to −0.10, then the coat at 2.6 eye radii | — |
| A grey horse, side photo (stock preview, measure-only, by eye) | — | a relaxed almond, the upper lid lowered over the top of the eye, about 2.5–3 times as wide as it is open; set high, about 0.4 of the head's length back from the poll | a dark upper-lid line with lashes, thickest toward the back; a parallel crease above it; a soft grey shadow in the hollow above and behind the eye. The lower lid is softer and lighter | pointed and slightly lower than the outer corner |

The `lp check` eye.size check reads the painted eye's radius as a percentage of the model's height. It warns below 1.2%.

## The shape, in side view

- **An almond, not a circle.** An eye wide open is about 1.6–2 times as wide as it is tall. A relaxed, docile eye has its
  upper lid lowered a little and is about 2.5–3 times as wide as tall. That half-lowered lid is much of what reads as calm.
- **Tilted.** The long axis rises from the inner corner (toward the nose) to the outer corner, by about 10–25°.
- **The two lids are different curves:**
  - the upper lid is a high arch whose highest point is behind the middle;
  - the lower lid is flatter, with its lowest point ahead of the middle.
- **The corners:** the inner corner is a sharp point set lowest. The outer corner is softer and tucked under the upper lid.
- **Size:** paint the eye 1.5–2 times its real size, which is 1.4–2.5% of the model's height for its radius. A horse's eye
  is one of the largest of any land mammal: give it at least 1.6%. On a 1.97 m alicorn at 198 texels per metre on the
  head, that is a radius of 30 mm or more: an almond about 12 texels wide and 5–7 open, before the lids.

## The lids: the shading from the eye outward

Measured on the cow's eye at 158 texels/m, with its texture turned to the model's orientation (the coat is about 0.7):

| Direction | Texels out from the centre, luminance | What it is |
|---|---|---|
| **Up, through the upper lid** | 0.04, 0.04, 0.03, 0.05, 0.09, 0.14, 0.22, 0.48, 0.64 | the eye body's darkness carries 1–2 texels into the lid (the lid's edge and lashes), then fades to the coat over 3–4 texels |
| **Down, through the lower lid** | 0.04, 0.05, 0.02, 0.03, 0.07, 0.15, 0.34, 0.55, 0.67 | a narrower dark edge, then a fade over 4–5 texels, slightly softer than the upper lid's |
| **Down and forward from the inner corner** | 0.02–0.04 at the corner, then 0.24–0.40 for 3–5 texels | the tear trough: a short soft streak, darkest at the corner and fading as it goes |

- **The upper lid is the heavier of the two.** It is a dark edge with lashes, and it casts a shadow over the top third of the
  eye, so the eye body is darkest just under it. On a horse, add a crease one texel wide parallel to the lid, 2–3 texels above
  it, and a soft shadow in the hollow above and behind the eye.
- **The lower lid is lighter.** It is a narrower edge, often with a slightly lighter or warmer rim between the eye and the
  cheek: the cow's is warm yellow-brown, the mare's a pale ring.
- **The lids' colour is a deeper, more saturated shade of the skin,** never neutral black. A grey ("white") horse's skin is
  dark, and the bare skin round its eye shows as a charcoal ring that softens into the white hair, the same as its muzzle
  (`muzzles.md`).
- **No outline anywhere.** Every step out from the eye is a gradient over 2–4 texels, until the coat's own value is reached at
  about 2.6 eye radii. A one-texel ring of a single value round a dark disc is what makes a button.

## The tear duct, at this pixel density

At 90–200 texels per metre on the head, the inner corner is not painted as a pink blob. It shows in three ways:
1. **The almond's inner corner is a sharp point** that dips lower than the rest of the eye.
2. **The darkest texels of the whole eye are in that corner:** 0.02–0.04 on the cow, darker than the eye's centre.
3. **A short soft streak runs down and forward from it:** 3–5 texels long, about 0.25–0.40, fading as it goes.

At hero density (about 200 texels per metre or more, with an eye at least 10 texels wide), add a warm dark notch of 1–2
texels inside the corner, the caruncle, where the two lids' lines meet.

## Inside the eye

- **The body is dark brown, not pure black:** 0.02–0.12 on the cow, with a warm hue, and darkest under the upper lid.
- **The iris catches light:** a soft lighter crescent in the lower, rear part of the eye (0.24 on the cow).
- **The catchlight:** one bright texel or two (0.6 or more) in the upper front quarter. The cow has a second, dim one (0.3)
  on the back half.
- **The pupil:** a horse's is horizontal, but at this density it is not drawn.
- **The lashes:** a horse's upper lashes overhang and shade the eye. At hero density, a few dark ticks one texel wide along
  the back half of the upper lid.

## Check it

- **`eye_study.py`:**
  - `locate` finds the eye's texel;
  - `measure` gives the zones and the radius in mm;
  - `photo` measures the same zones on a reference photo.
  Compare the steps from the coat with the photo's: rim about −0.2, socket about −0.15, surround about −0.08.
- **The lid profiles:** read the luminance perpendicular to the eye's long axis, up and down, and compare with the table
  above. Turn the texture to the model's orientation first: the cow's texture is painted upside down (its v runs up the
  head).
- **`lp check`:**
  - eye.size (the radius against the height);
  - eye.catchlight, eye.body, eye.rim and eye.socket for the zones.
- **Render the head textured, from the side, at the game camera's distance.** The eye should read as an almond with a heavy
  upper lid and a pointed inner corner, not a dot.
