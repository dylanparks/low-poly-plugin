# Humanoid races from the human base

A race is the human construction (`body.md`, `head-and-face.md`, `hands.md`) with its proportions and shapes changed. Its
numbers come from the real anatomy it borrows: a fossil human, a great ape, a child, a very large or a short-statured
person. Game and concept art supply shape language only, named as convention.

## How to adapt

1. **Pick the analog and write the race's measurement table.** Scale the human survey's table (ANSUR II's median man) by
   the analog: stature, the limbs against the trunk, head size, girths. This is the spec's `"measurements"` file;
   `body_measure.py` and `lp check` judge the model against it as they judge a human.
2. **Change the rings, not the construction.**
   - **Torso:** half-widths, depths and squareness by region.
   - **Limbs:** the ring positions along each limb (the segment lengths) and their girths.
   - **Head:** the face rings' positions and the jaw row.
   - **Ear:** the ear's parameter set.
   - **Hands:** the hand's ring spacing.

   Keep every rule that comes from how joints and tissue work: one-ring hinges, helper bones where tissue meets, contact in
   the folds, the thumb bending across the palm.
3. **Keep what the skeleton fixes.**
   - **The ear canal** sits at the side of the skull, at the back of the jaw. A pointed or larger ear changes its outline
     and size, not where it joins.
   - **The joints** sit where the bones meet. The jaw's corner sits under the ear.
4. **Mass changes thickness faster than length.** By elastic similarity a bone's diameter grows with mass^(3/8) and its
   length with mass^(1/4), so diameter grows as length^1.5 (McMahon 1973); geometric similarity would scale both alike.
   Measured mammal bones fall between the two models (Kokshenev; Christiansen 1999). For a design rule of thumb, a
   creature twice a man's height needs limbs nearly three times as thick (2^1.5 = 2.8), not twice.
5. **Budget by importance, not size** (lowpoly-core §2). A huge ogre the camera rarely sees up close can spend less on its
   face than a player character.
6. **Animate the analog's weight.** A heavy body has a shorter stride and a slower cadence. A stooped, long-armed body
   swings its arms lower and further.
7. **The body-type option still applies within a race.** Thin to muscular are morph targets on the race's own median.

## Orc (analog: Neanderthal, the robust human)

| What | Neanderthal (male) | Modern human (male) | Source |
|---|---|---|---|
| Stature | about 165 cm (164-168) | 175.5 cm (ANSUR II) | Helmuth 1998; Neanderthal anatomy (Wikipedia, citing the primaries) |
| Body mass | about 72-78 kg | | Froehle & Churchill 2009 (77.6 kg); Plavcan 2014 (about 72) |
| Brachial index (forearm / upper arm) | about 74 (derived from Trinkaus's mean limb lengths; unverified) | higher, rising with climate's warmth | Trinkaus 1981 |
| Crural index (shin / thigh) | about 79 (derived; within the modern range on average per Ochoa 2025) | higher | Trinkaus 1981; Ochoa 2025 |
| Pelvis (bi-iliac) breadth | about 31 cm (Saint-Césaire 1) | about 26 cm on early-modern proportions | Trinkaus et al. 1998, PNAS |
| Cranial capacity | about 1,640 cm³ | about 1,350 cm³ | Holloway 1985; Allen 2002 |

- **The body.** Short, heavy and wide: limbs short against the trunk (lower brachial and crural indices), a broad pelvis,
  heavy, robust limbs, a bulk at the extreme of high-latitude humans (Holliday 1997).
- **The ribcage.** Wide and deep, flaring at the bottom: bell-shaped. "Barrel chest" is a loose description.
- **The head.**
  - **Brow.** A rounded brow ridge (supraorbital torus).
  - **Face.** It projects forward of the skull's base (midfacial prognathism), with a large, wide nasal opening.
  - **Back of the skull.** An occipital bun.
  - **Chin.** Weak or absent: confirm with a primary source before relying on it.
- **Orc convention:** a wider head and jaw so it reads as non-human; tusks (no design source found stating where they
  grow: a design choice). On the human head:
  - **Brow ring:** forward, with a heavy shelf.
  - **Nose and face:** the nose ring wider, the mid-face rings forward.
  - **Chin:** the chin box back.
  - **Jaw:** wider and deeper. Keep its lower edge's angle readable.
- **Proportions on the human base:** stature about 0.94, the limbs' distal segments (forearm, shin) shortened a few
  percent against the proximal, girths and the pelvis up, the trapezius and neck heavy.

## Troll (analog: the great apes, long-armed and stooped)

| Species | Intermembral index (arm / leg × 100) | Source |
|---|---|---|
| Human | 72 (64-74) | Fleagle 2017; Jungers 2009 |
| Chimpanzee | 106 (100-114) | Fleagle; Schultz 1937 |
| Gorilla | 116 (110-125) | Fleagle; Schultz 1937 |
| Orangutan | 139 (135-151) | Fleagle; Schultz 1937 |

- **Male gorilla** (the Gorilla article on Wikipedia, citing field studies; secondary): 136-227 kg, 1.4-1.8 m tall, arm
  span 2.3-2.6 m (about 1.7 times body length); a sagittal crest. It knuckle-walks only about 60% of the time.
- **Hands.** Chimpanzees and orangutans have long fingers and a relatively short thumb; the gorilla's hand stayed close to
  the human's (Almécija, Smaers & Jungers 2015). A "short thumb" fits a chimp-like troll, not a gorilla-like one.
- **On the human base:**
  - **Arms.** Raise the arm-to-leg ratio from about 0.72 toward 1.0-1.2: lengthen the upper arm and forearm rings' spacing,
    and shorten the legs.
  - **Upper body and head.** The shoulders, chest and neck heavy; the head carried forward and low.
  - **Stance.** A standing pose flexed at the hips and knees, the hands near the knees.
  - **Gait.** A walk that can drop onto the knuckles: the hand's mitten as a knuckle pad (lowpoly-animals, the
    knuckle-walking foot).
- **Troll convention:** ape-like, long-armed, hunched (thin design sources: a design choice).

## Goblin (analog: a child's head on a small body)

- **The head's share of stature.** About a quarter at birth, about 1/7 to 1/7.5 in an adult (Britannica; art references
  use 7.5-8 heads). The art chart of 4 heads at 1 year, 5 at 2, 6 at 6 and 7 at 12 is credited to Stratz, unverified:
  use it as convention.
- **The trunk against the legs** (sitting height / stature):

  | Age | Ratio |
  |---|---|
  | Birth | about 0.66 |
  | 2 years | about 0.64 |
  | Puberty | about 0.51 |
  | Adult | about 0.52 |

  Legs grow faster than the trunk through childhood. These are summarised growth-study values: re-check before
  relying on them.
- **Eyes.** On a child's head they sit below the middle (convention; no measurement found).
- **On the human base:**
  - **Size and proportions.** Stature about 0.6-0.7 of the man, and the head scaled up toward a child's share (5-6 heads
    tall).
  - **Body.** The trunk long against short legs; the limbs thin.
  - **Ears and nose.** Large (`head-and-face.md`, ears: a larger `length`, `breadth` and `protrusion`, a long `tip`).
- **Goblin convention:** a big head and ears, thin limbs (no design source states it: a design choice).

## Ogre (analog: gigantism and acromegaly, the heaviest strongmen)

- **Acromegaly and gigantism** (StatPearls; MSD Manual):
  - **Face.** Coarse: a prominent brow (frontal bossing), a jaw grown forward with gaps between the teeth, an enlarged
    nose, ears and lips.
  - **Hands and feet.** Large hands with stubby fingers, large feet.
  - **Soft tissue.** The face's coarsening and the hands' and feet's swelling are mostly soft tissue, and come first.
- **Elite strongmen** average about 153 kg at a BMI of about 43.5, among the largest male athletes (Kraemer et al. 2020).
- **On the human base:**
  - **Size and limbs.** Stature 1.3-1.6 times; limb girths by the mass rule above (diameter as length^1.5).
  - **Belly and head.** A big belly (the waist and abdomen rings' front depth well past the chest's); a head small
    against the body (keep it near human size while the body grows).
  - **Face.** The jaw and brow grown forward, the nose and lips large.
  - **Hands.** Large, with stubby fingers: the mitten's finger rings shorter against a wider palm.
- **Ogre convention:** a square heavy jaw with fangs over the upper lip, a big belly.

## Dwarf (analog: short stature, the limbs short against the trunk)

- **Achondroplasia, adults** (Merker et al. 2018; Gerver & de Bruin 2011; MedlinePlus):

  | Measure | Achondroplasia | Typical |
  |---|---|---|
  | Height (untreated, male) | about 131 cm | |
  | Sitting height | only about 7 cm below average | |
  | Sitting-height ratio | about 0.66 | about 0.52 |
  | Legs | almost 50% shorter | |
  | Arm span (male) | about 122 cm | 186 cm |

  The trunk is near average size. Proportionate short stature keeps the typical ratio.
- **On the human base:** stature about 0.75 of the man; the trunk near human size; the limbs shortened (the legs most); the
  hands broad; the head near human size; heavy girths (a robust dwarf also borrows from the orc's analog).

## Elf (analog: a slender human)

The human base with the body type toward thin and long:
- **Body.** Stature up, the limbs a little longer against the trunk.
- **Face.** A narrow face and jaw.
- **Ears.** Pointed (`head-and-face.md`, ears).
  - **Tolkien's elf:** only slightly pointed, a leaf; move the helix's back-top point 15-25% of the ear's length up and
    back, the tilt 25-30.
  - **Game-style long points:** up to about three times the human ear (one artist's tutorial, not a standard).

## Temperament, and creatures that are part animal

- **Hostile or docile** (`lowpoly-core/references/temperament.md`) is settled first, as for any model. That file was
  written from animals, and its `temperament/hostile` profile sets a glowing, pupil-less eye and modelled teeth. On a
  humanoid, hostility reads first from the brow, the jaw, tusks or teeth and the posture; whether a hostile orc or ogre
  also takes the glowing eye is the user's choice: ask.
- **Part animal** (a centaur, a minotaur, a werewolf): the human parts from this skill, the animal parts from
  `lowpoly-animals` (`lowpoly-animals/references/parts.md` joins parts into composites), each checked against its own references.
  The spec's `body_plan` follows the legs: `"humanoid"` on human legs, `"biped"` or `"quadruped"` on an animal's.

## What stays fixed in every race

- **Joints:** one-ring hinges, and helper bones where tissue meets, scaled to the race's masses.
- **Ears:** the canal at the side of the skull at the back of the jaw; the antihelix's Y and the bowl kept, the outline
  changed.
- **Thumb:** bending across the palm about its own axis.
- **Texture:** the charts, masks and tone ramps (a race's skin ramp is its own: greens, greys or blues on the same
  `tone / painted` recolour), and normal transfer for attached pieces (ears, tusks, horns).
- **Checks:** the same checks, against the race's own measurement table.
