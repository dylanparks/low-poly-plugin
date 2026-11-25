# Muzzles: the nose, nostrils, lips and chin, by kind of animal

The muzzle is the front of the face, where a docile animal is looked at most. Read this after `heads.md` (where the muzzle
sits against the eyes) and before painting the nose (`texture.md`, "Noses and muzzles").

**The failure this file comes from.** The first alicorn's muzzle looked as if the nostrils and mouth had been drawn on with
a marker. There were three causes:
- **The geometry ended in a point.** The head's last ring (lips and chin, 0.12 m wide) closed into a single tip vertex, so
  the end of the muzzle was a cone. A cone has no front face for the nostrils, no overhanging lip and no chin.
- **The nostrils were dots.** They were barely darker than the nose round them: 0.25 against a mean of 0.31.
- **The paint showed no form.** The bridge was only 0.07 brighter than the side, and the mouth line was 0.01 darker than
  the lip above it.

The reference game's lame mare does what a muzzle needs, with fewer than half the alicorn's texels on the front of the head
(25 × 20 against 34 × 35):
- the end is a blunt block, 0.128 m wide against 0.184 m across the cheeks;
- the nostrils are the darkest thing on the head (0.00), inside a nose of 0.04;
- a pale mealy ring (0.25) sets the nose off from the face (0.16);
- the bridge is lit at 0.49 against a side of 0.22;
- the mouth is a dark band (0.00) between darker lips, not a line;
- the chin has its own shaded value (0.18).

These were measured with `nose_study.py` on `head_textured.py` renders, which are flat-lit, so the numbers are the paint.

## Which muzzle the animal has

Identify the muzzle from the species' photos before building. Each kind has its own nose, nostrils, lips and chin.

| Kind | Animals | Nose | Nostrils | Lips and mouth | Chin |
|---|---|---|---|---|---|
| **Leather pad** (rhinarium) | dog, fox, wolf, cat, bear | a hairless pad at the tip, the darkest mass; its top catches the light | two commas in the pad's front, split by a groove that runs down into the upper lip | thin lips; the mouth line runs back under the whisker pads | small, shaded |
| **Soft muzzle, no pad** | horse, donkey, mule, zebra | none of its own: the whole end of the muzzle is soft, finely haired skin | large, mobile, C-shaped openings on the front corners, each with a fleshy rim and a hollow above it | a broad, rounded, mobile upper lip that overhangs the lower; the mouth runs back to a corner well behind the nostrils | a separate rounded lump under the lower lip, with a notch above and below it |
| **Muffle** | cattle, bison, buffalo | a broad, moist, hairless plate across the nostrils and down over the upper lip | wide commas at the plate's sides | thick lips; a wide mouth | broad, shaded |
| **Small bare nose** | deer, antelope | a small hairless patch round the nostrils | slits curving out and back | a hairy upper lip; on sheep and goats the lip is split down the middle | small |
| **Disc** | pig, boar (tapir: a short trunk) | a flat round disc at the end of a long snout | two holes in the disc's face | the mouth runs under the snout, its corner far back | small, under the snout |
| **Split lip** | rabbit, hare, rodents | a small pad | small slits, mobile | a Y-shaped split from the nose down through the upper lip | small |
| **No lips** | lizards, crocodiles, snakes | none | small holes near the tip, often on a raised bump (crocodiles) | the mouth line is the jaw's edge, lined with a row of larger lip scales | the lower jaw's tip |
| **Beak** | birds | `heads.md`, "Birds" | | | |

## Geometry: end the muzzle in a block, never a point

- **The last ring is a blunt end face, not a tip.** Never close a mammal's muzzle with one apex vertex. End it with a small
  flat cap of 4–6 vertices whose width is most of the nostril ring's. On the mare, the end face is 0.70 of the cheek width.
  Only a beak or a reptile's snout may come to a point, and then because the species' does.
- **The nostril ring** sits a short way behind the end.
  - **Horses:** it is wider than the mid-face, so the face narrows and then flares again (`heads.md`, "Long-faced heads").
  - **Where the vertices go:** put a vertex where each nostril's rim bulges out, at the ring's upper side corner.
  - **On a head the camera comes close to:** set one vertex just behind and above the rim, a little in from the surface.
    That makes the hollow over the nostril, which in a horse is the false nostril, the groove that runs up from it.
- **Lips:**
  - **In profile,** the upper lip is a rounded pad. On a horse it overhangs the lower lip.
  - **The mouth is a crease, not a painted line:** a row of vertices set in between the upper lip's ring and the lower
    lip's, running back to the corner.
  - **The corner:** measure where it is on the side photo. On a horse it is where the bit sits, about level with the end of
    the face's flat side.
- **Chin:** a small rounded lump under and just behind the lower lip. There is a notch between the lip and the chin, and
  another between the chin and the jaw's underline. On a low budget one or two vertices pushed out do it.
- **Budget:** a horse's muzzle needs about 16–20 vertices, not counting a mouth that opens:
  - the nostril ring (6–8);
  - the lip ring with its mouth crease (6);
  - the end cap (4);
  - the chin (1–2).
  The mare's front quarter of the head has only 8 triangles, and its paint carries the rest. On a hero model the
  geometry carries the rims, the overhang and the chin, and the paint lights them.
- **Check it** with `head_views.py` (untextured) from the front, below and the side:
  - **From the front:** the end of the muzzle is a face, not a point. The nostrils are at its upper corners, and the
    muzzle's outline passes below and between the eyes (`heads.md`).
  - **From the side:** the profile shows the lip's overhang, the mouth's crease and the chin's notch.

## Paint: light the forms first, then put the species' colours on top

The values below are flat-lit, as `nose_study.py` measures them (0 black, 1 white).

| Part | Brown horse (the reference game's mare) | Grey ("white") horse, from photos |
|---|---|---|
| **Nostrils** | the darkest value on the head (0.00): large ovals facing forward and out, each about a third of the muzzle's width | near-black inside. The rim is the muzzle's own grey skin, lit on its upper and outer side |
| **Above each nostril** | a soft crescent of shadow: the fleshy rim's fold | the same groove, shaded |
| **The muzzle zone** | a pale mealy ring (0.25) between the face (0.16) and the dark end of the nose (0.04) | **dark where the hair is thinnest.** The nose (0.29), the nostrils (0.04–0.06) and the lips and chin (0.11) are dark skin under thin hair, against a face of 0.33; the band just above the nostrils can stay pale and lit (0.51). Freckled with dark specks, with no outline at its edge |
| **Bridge against side** | 0.49 against 0.22, 10% back from the tip: the end of the muzzle is a box lit from above | the same lighting, in greys |
| **Mouth** | a dark band (0.00) about two thirds of the way down, between dark lips (0.02 above, 0.07 below) | a shadowed crease under the overhanging upper lip. The lips are bare dark skin |
| **Chin** | its own shaded value (0.18), with a lit top | grey skin, shaded under the lip's notch |
| **Whiskers** | n/a | optional: a few dark dots along the lips' lower edge |

A side photo of a grey mare (a stock preview, measure-only, read by eye) shows the same: the face darkens from about mid-face
to a charcoal nose and lips. The nostril is a dark comma with a paler rim, and the dark skin shows again at the hooves and hocks.

- **Get the coat's skin right.** A white or grey coat does not mean a white muzzle. Almost every "white" horse is a grey: its
  skin is dark, and the skin shows wherever the hair is thin (the nose, the lips and chin, the eyes, the dock). Painting the muzzle the same
  white as the face, with dark dots for nostrils, is exactly the "drawn on" look. Only a true white horse (rare, born
  white) has pink skin there. Say which one you chose.
- **Every feature is a form with a lit side and a shadow side, never a line.**
  - A nostril is a hollow: dark inside, a lit rim, a shadow above it.
  - A mouth is a crease under a bulge.
  - A chin is a lump with a lit top.
  The mare does this on 25 × 20 texels. Use the texel budget on the head (`lowpoly-core/references/texture-method.md`,
  "Texel density") to paint the gradients, not to sharpen the outlines.
- **Paint on the geometry's own faces.** Give the end face and the nostril ring their own head-on patch
  (`heads.md`, "Eyes against the snout") so the nostrils aren't stretched across the side projection.

## Check it in code

- **`head_textured.py` then `nose_study.py`:** run on the head, front and side, and compare against the table above. The
  `lp check` nose.* checks run the same measures.
- **What the first alicorn should have shown:**
  - a nose narrower than the muzzle: `nose_study.py` found its "nose" spanning 0.81 of the muzzle's width, because nothing
    set it apart (the mare 0.31; measured models 0.33-0.66);
  - nostrils that are the darkest values on the head, 0.13 or below (its darkest 10% were 0.25; the mare's 0.00);
  - the bridge brighter than the side by at least 0.1 (it had 0.07);
  - the mouth line clearly darker than the lip above it (it had 0.01).
- **For a grey horse, also check the lips and chin are dark skin,** well below the face between the eyes (a head-on photo:
  lips and chin 0.11 against a face of 0.33), while the top of the muzzle may stay pale.
