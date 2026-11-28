# Proportions: tracing the requested animal, with the housecat and the T. rex as worked examples

All ratios are relative to **L**, the body length measured horizontally in a side view, defined per body plan below.

## The proportion table, the photo overlay and the side-photo notes (from SKILL.md lowpoly-core §1)

**Write a proportion table, normalised by body length L.** Define L for the body plan, and keep the table as comments
in the build script:

| Body plan | L |
|---|---|
| Quadruped | chest front to back of rump, horizontally |
| Bird | breast to tail base |
| Biped on two legs (theropod, ostrich) | chest front to rump back, horizontally; the neck, head and tail are measured against it |
| Fish | snout to tail fork |
| Lizard | snout to vent |

Take every number from the reference set above (or the photos), not from memory:

| View | Measure (adapt to the body plan) |
|---|---|
| Side | top line (where it rises and falls), body depth, underline (tucked, level or hanging), ground clearance |
| Side | head length and height, how high and how far forward the head is carried, neck length |
| Side | where each limb leaves the body and where its foot stands, joint heights and directions |
| Side | tail, fins or wings: root position, thickness, carriage, length |
| Front | head width against body width, stance width (feet under the body or splayed), body width against depth |
| Top | widths in order from head to tail; where the body is widest |

**Overlay the photos too,** the same way as the skeleton references (side projection over each side photo, aligned on
two landmarks and the ground line; front and top too). Fix every mismatch the photos agree on; where they disagree because
of pose, aim between them. This catches what a 3/4 render hides: a sagging back, a shallow chest, limbs in the wrong place,
a tail leaving the body at the wrong height.

Then note from the side photo:
- **Masses:** ribcage, haunch, shoulder, neck, skull, muzzle or beak, and how they overlap. They are rarely one
  sausage.
- **Leg segments and joint directions.** Which segments show below the body, and which way each joint bends. A
  quadruped's hind "knee" seen from the side is usually the hock (ankle), pointing back; front "knees" are wrists.
  Birds' backward "knees" are ankles too.
- **Foot posture:** plantigrade, digitigrade or unguligrade (§3, rule 5).
- **Head:** eye position and direction, brow, stop, muzzle or beak length, jaw, ears or crest.
- **Colour zones:** the 2–4 tones that make the species recognisable, plus markings (stripes, points, masks, bars).

## Worked examples

Measure from the reference set of the species you are building (SKILL.md lowpoly-core §1): its skeleton and muscle in side, front and
top views, and photos in two or more poses. The numbers below are examples of the method, **not defaults for other
animals**.

**Method:**
1. On each reference, mark the two ends of L and the ground line.
2. Read every landmark off it as a fraction of L: heights, depths, limb and foot positions, head size and
   carriage, tail root.
3. Record a range across the poses, then choose a value inside it for the bind pose, noting which pose each value
   leans toward.
4. Verify with an overlay (`lp overlay`: `lowpoly-core/references/measuring.md`; or `lib/lowpoly/tools/ref_overlay.py`),
   not by eye in a 3D view.

## Housecat, from two side photos

The photos show an adult domestic cat standing alert, and one walking. Ranges span the two poses.

| Measure | Standing (alert) | Walking | Used in the model |
|---|---|---|---|
| Back height at the rump | 0.79 L | 0.56 L | 0.66 L |
| Rump vs withers | rump higher | about level | rump level or slightly higher |
| Body depth (back to belly) | 0.50 L | 0.40 L | 0.39 L at the ribcage |
| Belly clearance | 0.27 L | 0.17 L | 0.26 L |
| Belly line | low, primordial pouch hanging in front of the hind legs | same | lowest at the ribcage and chest, pouch kept at the waist |
| Hind paw ahead of the rump back | 0.14 L | 0.15 L | 0.15 L |
| Front paw behind the chest front | about 0.1 L | about 0.1 L | about 0.1 L |
| Head length (back of skull to nose) | 0.28 L | 0.20 L | 0.20 L |
| Neck | short and thick; the back of the head sits over the chest | same | neck nearly as wide as the head from above |
| Tail root | top of the rump, continuing the back line | same | top of the rump, bridged to the body |
| Tail thickness at the root | about 0.09 L | about 0.07 L | 0.09 L |
| Tail carriage | raised (alert) | hanging, tip curling forward | hanging, tip curling forward |

**Front view (known proportions, no photo):**
- **Width and depth:** the head is about as wide as the chest, and the body is taller than it is wide.
- **Stance:** the forelegs come down under the chest with the elbows tucked in. The paws are about 0.16 L apart
  (centre to centre), well inside the body's outline.

**Top view (known proportions, no photo):**
- **Hips and ribcage:** the hips are about as wide as the ribcage, and the ribcage is the widest point. The waist
  is a little narrower.
- **Neck:** only a little narrower than the head (fur and muscle), not a stalk.

## Tyrannosaurus rex, from a skeleton-and-outline drawing and published numbers

The second test animal. The first version used published bone lengths and proportions only, and was wrong in several
places. It was then measured against a side view of a walking T. rex with its skeleton drawn over the body outline
(supplied by the user), 1163 px nose to tail tip. Scale: 98 px/m at the model's 11.9 m length; the Field Museum's "Sue" is
about 12.3 m, femur 1.3-1.4 m, skull 1.4-1.5 m, humerus about 0.4 m. The reference shows a mid-stride pose with the head
pitched down about 28 degrees and the mouth open, so the head pitch and the limb angles are not taken from it.

| Measure | Value used |
|---|---|
| Hip joint | under the middle of the pelvis, 41% of the length from the nose (4.8 m), 3.0 m high; the first version had it at 49% and 2.7 m |
| Back height | 3.4 m over the shoulders, 3.77 m over the pelvis (the highest part of the back), sloping to 3.36 m at the tail root |
| Belly line | 2.0 m under the shoulders, 1.7 m under the pelvis (the pubic boot), rising to the tail |
| Femur / tibia / metatarsus / toes | 1.4 / 1.2 / 0.7 / 0.6-0.9 m, with the thigh inside the torso: the knee is 2.0 m high, above the belly line |
| Feet | standing under the rear of the ribcage, 1.0-1.4 m ahead of the hip joint; the ankle is about 0.8-1.0 m high |
| Neck | a deep wedge of muscle: 1.2-1.4 m deep at its base, the throat line running straight from the jaw hinge (2.7 m high) to the chest (2.0 m) |
| Head | the back of the skull is the highest point of the animal (3.97 m), above the shoulders (3.5 m); the skull is 1.5 m from the nose to the jaw hinge |
| Widths (from the top view, 51.8 px/m) | skull 0.82 m across the cheeks, 0.44 m at the mid-snout, 0.38 m at the nose; neck 0.6 m; ribcage and pelvis 1.5-1.65 m (the front view suggests about 1.35 m for the ribcage: the two disagree); tail 0.9 m at the root, 0.4 m at 2.4 m, 0.2 m at 3.5 m, 0.05 m at 4.5 m |
| Stance (from the front view) | feet about 0.75 m apart centre to centre, each 0.42 m wide; the knees bow out to about 1.2 m apart; the shins are vertical |
| Arms | about 0.8 m, from a shoulder joint 2.7 m from the nose and 2.35 m high |
| Tail | 6.0 m beyond the pelvis (half the length), 0.9 m deep at the root, 0.4 m deep at the middle, level to two thirds of its length, then drooping to 2.0 m at the tip |

The first build looked like a lean raptor, and its mouth looked painted on. The measured differences, and what fixed them,
are in `case-study-trex.md`.


The overlay snippet, `lp overlay`, using the reference set, filling gaps, dense measuring and re-measuring after a
change are in `lowpoly-core/references/measuring.md`.
