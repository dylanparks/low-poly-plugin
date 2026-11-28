# The body: measured as a person, built from muscle

## Measure it as a person

- **The table.** A survey's medians in metres, grouped (heights, head, torso, arm, leg), in the spec's `"measurements"`
  file. ANSUR II's median man: stature 1.755, acromion 1.439, axilla 1.328, chest 1.289, waist 1.055, trochanter 0.899,
  crotch 0.845, mid-knee 0.487; head 0.200 long and 0.154 wide; chest 0.289 x 0.253 (girth 1.056); waist 0.325 x 0.234
  (0.937); hips 0.344; biceps 0.357 (flexed), forearm 0.310, wrist 0.176; hand 0.193 long, 0.088 across; foot 0.271 x 0.102.
- **How it is taken.** `body_measure.py` slices the skin as a tape measure goes round it (the convex outline of a level
  slice; the arm square to its own axis), over the clothes, in the bind pose. The first build: 2.3% median, 11.8% worst.
- **A race** scales this table by its analog's proportions (`races.md`) and writes its own file; the checks are the same.

## The torso

- **Half rings, front midline to back, each a superellipse** with a half-width, a front depth, a back depth, a centre and
  a squareness. The first build's rings: hip, glute, pelvis, waist, abdomen, ribs, chest, axilla, shoulder, trapezius,
  neck base, neck: 12 rings of 7 points.
- **Squareness by region.** Waist and hips about 1.35 (a rounded diamond), the ribs 1.5, the chest 2.0, the axilla 1.9.
  The shoulder ring 2.2: from above, a man's shoulder top is a rounded rectangle, the deltoid's end 11-12 cm deep. At 1.35
  the shoulder came to a point from above, at 1.9 an almond. The trapezius 1.8, the neck base and neck about 1.
- **The arm's hole** is the side of the torso between the axilla and shoulder rings. The hole's floor follows the arm about
  half; its front and back points sit 2.5 cm below its middle, so the armpit's folds (the pectoral in front, the lat behind)
  slope from the torso down onto the arm. On 35% the folds stayed on the torso: a shelf. Lowering them 4 cm stretched the
  texture and closed no gap.
- **The shoulder.** The trapezius slopes about 20 degrees from the neck to the acromion, and the deltoid, not the torso,
  makes the shoulder's outer point: bideltoid 0.509 against biacromial 0.415. The shoulder ring's outer points ride half
  on the arm, so the deltoid caps the joint in every pose.

## Body types: morph targets and the blend of muscle

One parameter, from -1 (very thin) through 0 (the survey's median) to +1 (a bodybuilder), scales each ring: per ring a
(half-width thin, buff, front depth thin, buff, back depth thin, buff, rise when buff). The mesh is built at -1, 0 and +1;
the model is the median with two morph targets, and the viewer's slider blends them.

What each region does, and what the first build found:
- **Very thin.** The ribcage is bone: the chest keeps 93-94% of its width and loses depth. At 86% it pulled away from the
  arms and opened a slot down from the armpit. The arm's root and upper arm keep 78% and 72%: a thin man's deltoid still
  caps the joint.
- **Bodybuilder.**
  - **Chest and back.** The chest deepens. The lats widen the axilla.
  - **Upper back.** The trapezius climbs the neck and thickens with the muscles between the shoulder blades into a hump,
    each ring's back behind the one above. It never grows wider than the shoulder ring below it.
  - **Shoulder and arm.** The shoulder grows 1.62 times and the upper arm 1.65. At 1.80-1.86 the arms sank into the
    torso's sides as they hung: 50-59 crossings.
  - **Neck.** It grows at the back (the trapezius) and at the front corners (the sternocleidomastoids). The throat stays
    where the larynx and hyoid hold it, so the line under the chin keeps about 4 cm and the cervicomental angle 105-120.
    Grown 32-40% at the front, the throat came 2 cm forward and the chin all but vanished from the side. Squared up
    (squareness 1.3), its front corners stood out under the jaw. Keep the neck's ring round, about as wide as the jaw's
    angle.
  - **Glutes.** They project, and the buttock's top rounds into the lower back. A pelvis ring left behind a large glute
    ring stepped 6 cm in 5.5 cm of height, a shelf from the side; spread the volume up into the pelvis ring.
  - **The back of the thigh** grows less, so the fold under the buttock shows.
  - **The jaw's angle** widens with the masseter. The waist stays narrow.
- **Every bone-led part keeps its size**: the skull, the jaw's angle on a thin build (it shows more, it doesn't shrink),
  the hands' length, the feet.

## Limbs

- **Rings at the masses.** The upper arm: the deltoid ring deep front to back (it wraps the joint), the biceps' fullest
  ring, the elbow's two rings, the forearm's fullest a third of the way down, then the wrist. The leg: the thigh just under
  the crotch (its back grows less than its front at full muscle: the glute's fold), mid-thigh, above the knee, the knee on
  the joint's line, below the knee, the calf, the shin, the ankle.
- **The calf** is widest about a third of the way down from the knee, where calf girth is measured (13 cm below a knee at
  48.5 cm). The gastrocnemius' medial head is larger and reaches lower: the ring's back-medial points come back 4 mm.
- **Seen from the front** a leg is fullest at about mid-thigh, the knee narrower than the thigh (`lp check`'s
  limbs.hind_peak and limbs.hind_knee).

## The armpit with the arm down

The arm is built in an A-pose (45 degrees down); hanging, the points shared by the chest and the arm follow it only part
way. The arm's root swung 1-2 cm inside the chest's side line, its inner face sloping out below: a V-shaped slit from the
armpit down. An armpit helper bone presses the hole's floor and the arm root's inner points out against the arm as it
comes down (`joints-and-motion.md`). The arm's inner side then rests on the chest along a crease.
