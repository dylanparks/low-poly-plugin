# Joints and motion

## A hinge is one joint

A knee bends at one ring on the joint's line, its weights split between the two bones (the first build: thigh 0.55, shin
0.45). The ring above belongs to the upper bone alone and the ring below to the lower. The first build's elbow has no
ring on its line, for the budget: the rings either side share the bend (0.75 upper arm and 0.25 forearm above the joint,
the reverse below). Spreading the change over three rings is how an animal's leg is weighted to keep its width; on a
human it bends the leg in two places, a knee block between two creases. With
`"body_plan": "humanoid"`, `lp check` leaves out the animal leg rules (motion.leg_rings, motion.leg_stretch_min,
motion.lockstep); motion.hyperextended and motion.leg_stretch_max still apply. A two-legged animal is `"biped"` and
keeps them all (`lowpoly-animals/references/limbs.md`, "Legs that bend").

## Where soft tissue meets: helper bones

As a joint closes, the masses on either side of the fold press together. Weighted between the joint's two bones alone,
the skin there opens a V-shaped notch instead. A helper bone inside each mass, a child of the bone the mass rides on,
carries part of the fold's skin. As the joint closes, it is moved (a translation key, from the joint's angle) into the
fold.

| Fold | Helpers | Moved by | Weights | Moves (fully closed) |
|---|---|---|---|---|
| Behind the knee | calf (child of the shin) in the gastrocnemius' belly a third of the way down; hamstrings (child of the thigh) above the knee's back | the knee's flexion, from 35 to 80 degrees | the knee ring's back points: thigh .2, hamstrings .2, shin .2, calf .4; the ring above's back: thigh .35, hamstrings .65 | the calf up 2.4 cm and back 4 cm; the hamstrings down 2.4 cm and back 2.8 cm (scaled by build) |
| Inside the elbow | biceps' lower belly (child of the upper arm); the forearm's flexors (child of the forearm) | the elbow's flexion, from 40 to 100 degrees | the elbow rings' front point .55, its neighbours .35 | each 1.2-1.6 cm toward the joint and 3.2 cm forward |
| The armpit | the armpit's fold (child of the chest) | the arm coming down from the A-pose toward hanging | the hole's floor .25-.30; the arm root's two inner points .25 | 1.8 cm out against the arm, 0.6 cm down |

- **The calf in the run** also moves with the stride: a small jiggle at the strike, flatter in mid-stance, shortening and
  bulging 5 mm at push-off.
- **Too small a weight does nothing visible.** At 35% weight a 2.4 cm push moved the elbow's corner 8 mm; at 55% and
  3.2 cm the fold closed.
- **Cost.** Each helper is a bone: the three folds take five a side, ten in all, on a 32-bone skeleton. The character
  tier's bone range (24-44) allows for them.

## Contact versus crossing

`lp check`'s motion.crossings counts triangles passing through others. Where tissue meets in a fold (the calf and
hamstrings, the fingertips in a fist, the thumb on the fingers, the arm against the chest), crossings are contact, as
real. Judge them in the renders, not by the count. What is wrong is a slit or notch where they should meet, or a part
passing through another part deep into its volume.

Each blend-space variant clip is judged on its own body: `self_cross` applies the variant's morph target while it poses
it. Judged on the average body, a thin idle's arms cut into the median hips that the thin body doesn't have.

## The idle

- **Relaxed standing arms** (upright CT study):
  - **Elbows** bent about 15 degrees (13-18).
  - **Forearm** turned so the palm faces the thigh.
  - **Carrying angle** about 11 degrees in men.
- **Muscle mass carries the arms out.** The lats insert on the front of the upper arm and turn it inward, so a muscled
  man's arms rest further from the body, palms turned back. A thin build's arms hang closest.
- **The first build's three idles:**

  | Build | Arm out from vertical | Elbow | Inward turn |
  |---|---|---|---|
  | Thin | about 4 degrees | 14 | 6 |
  | Average | about 8 | 15 | 10, palms toward the thighs |
  | Muscular | about 20 | 24 | 26, palms turned back |

  Each was set on its own morph body: at 13 degrees out the muscular arms pressed into the lats.

- **Thin-build hands stay clear of the thighs.** Hung straighter, they tucked against the thighs; carried slightly out,
  they align with the shoulders.
- **The fingers** take the measured relaxed curl (`hands.md`).

## The run

- **Planted means no sliding.** Whatever is on the ground (heel, flat foot, ball) moves at one ground speed. The stance
  swept 56 cm in 0.26 s, about 2.2 m/s: the game must move the character at the clip's speed.
- **Swing retraction.** The foot swings just past its landing point and is pulled back, landing already moving at ground
  speed.
- **The ankle follows the shin in the swing.** Held level while the shin swung back, it bent 40-55 degrees up, past what
  an ankle does.
- **Measured angles** (real running in brackets):

  | Joint | Moment | Build | Real |
  |---|---|---|---|
  | Ankle | toe-off | -15 | -20 to -25 |
  | Ankle | mid-stance | +22 to +25 | about +20 |
  | Knee | strike | 22 | about 20 |
  | Knee | mid-stance | 46-55 | 40-45 |
  | Knee | swing | about 95 | 90-110 |

- **The toe's tip** is on the toe bone alone. A 30% share on the foot dragged it 11 mm into the ground as the heel rose.
- **The arms carry the build.**

  | Build | Arm drop from the A-pose (rad) | Swing (rad) | Calf bulge |
  |---|---|---|---|
  | Thin | 0.58 | ±0.46 | ×0.6 |
  | Average | 0.52 | ±0.46 | ×1.0 |
  | Muscular | 0.27 (the arms carried well out) | ±0.33, centred further forward (shorter, mostly off the back) | ×1.4 |

  The drop is from the A-pose, in radians: a smaller drop carries the arms further out. At 0.46 the muscular arm passed
  through the bulked lat as it swung back.

## Blend spaces for body types

Where mass changes the pose (the idle's arms, the run's arms and calf), build a variant per body type (`stand_thin`,
`stand_muscular`, `run_thin`, `run_muscular`). The character file's `"clip_blends"` names each clip's variants and the
option that drives them. The viewer, and the game, blends them bone by bone by the option's value (a 1D blend space) and
hides the variants from the clip list.

## An attack

The first build's punch (an unarmed right cross, 1 s):
- **Guard.** Fists up by the chin, knees soft.
- **Wind-up and drive.** A short turn back, then the hips, trunk and shoulder turn through as the arm drives straight at
  chest height and the rear heel rises.
- **Return.** The arm snaps back to guard, then down to the stand.

Let the shoulder blade protract and lift a little with the punch (about 7 degrees forward and 3 up at the clavicle), and
the arm turn the rest from there. Taken wholly at the shoulder joint, the turn over-stretched the armpit's skin.
