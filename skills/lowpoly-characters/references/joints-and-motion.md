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

## Motion that reads as alive

`lowpoly-core/references/motion-principles.md` has the rules, the build order and the checks. On a character:
- **The legs are solved, not posed.** The feet's places are written first (planted, pivoting on the ball, stepping);
  the pelvis then shifts, turns and tilts, and each leg is solved from its hip to its foot
  (`animate.limb_rotations`), the knee pointing between where the pelvis and the foot face.
- **The helper bones follow the solved joints.** The calf, hamstring, biceps, flexor and armpit helpers are moved from
  the joint angles after the pose is solved, so every clip gets them.
- **Each body type is checked after a motion change.** A narrower run track or a lower arm that clears the average
  body cut into the muscular one (the thighs, the lats).

## The idle

- **It never stops.** One breath per 4 s running belly, chest, shoulders; the pelvis swaying 11 mm over the feet with a
  little roll and turn, the legs solved to the planted feet; each arm, hand and finger group on its own phase.
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

- **The pelvis and chest work against each other.** The pelvis turns about 11 degrees and tilts about 11 (the swing
  side's hip drops); the chest turns the other way and carries the arm swing; the body rises and falls 4% of its
  height; the head pitches against the bounce. The arm, elbow and hand each run a little later than the chest.
- **The feet's track** is 5.5 cm either side of the midline, the swing foot 2 cm wider, and 7.7 cm on the muscular
  build: at the 2-4 cm measured on runners the swing foot passed through the standing shin.
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

Where mass changes the pose, build a variant per body type (`stand_thin`, `stand_muscular`, `run_thin`,
`run_muscular`, and the same for the stance and each attack). The character file's `"clip_blends"` names each clip's
variants and the option that drives them. The viewer, and the game, blends them bone by bone by the option's value (a
1D blend space) and hides the variants from the clip list.

Every clip with the arms near the body needs them, not only the idle and the run. In a guard or a strike the
difference is small and in the arms alone, so the move stays the same move: the first build's muscular guard carries
the upper arms 7 degrees further from the ribs, opens the elbows 7 degrees (a big biceps and forearm meet sooner, so
the drawn-back hand closes to about 117 degrees where the others reach 127-132) and turns the upper arm in 6 degrees;
the thin build tucks 2 degrees closer. The feet, legs, trunk, head and timing are untouched. Write the offsets once (a
table per build) and apply them to every fighting arm pose, so a new attack gets its variants for free.

## A combat stance, and the attack from it

Moves start from the pose they belong to. A fighter does not punch from hanging arms: the character has a combat-ready
stance clip (the first build's `spar`), and each attack's first and last frames are that clip's first frame, so the game
goes stance, attack, stance with no blend through the idle. The character file names it:
`"clip_stances": {"attack": "spar"}`. Build the stance as a function that takes what a move adds to it (the turn, the
travel, a step, a pivot), and the attack as those additions, so the two cannot drift apart.

**Build the stance to a reference of that stance**, as a body is built to a survey: photographs of a fighter in it from
the front, the side and three-quarters, and what its teachers say of the feet and the weight. The first build's first
stance was made from an idea of a guard and came out square-on with the feet a step apart: a man waiting, not a
fighter. Compared with a photograph of a side-on fighting stance it was wrong in every part.

The first build's stance (`spar`, a 2 s loop), side-on, the left side leading. A second pass measured the reference
game's unarmed fighting stance and moved further the same way: longer, more side-on, the feet on one line.
- **Feet.** On one line to the opponent, the ankles 59 cm apart (the reference game's 67 cm on a 1.72 m figure; taught
  as one and a half to two shoulder widths). The lead foot turned in about 16 degrees, the rear turned out about 95.
  Weight on the balls of the feet, the rear heel off the ground.
- **Legs.** Both knees bent (about 40 and 55 degrees), each pointing where its foot points; the pelvis 8.5 cm lower.
- **Body.** Bladed and upright: the hips turned 68 degrees from the opponent and the shoulders 63 (the reference
  game's 70 and 61), the lead shoulder toward them. The head turned back over that shoulder to face them. Leaning
  forward read as a hunch.
- **Guard.** The lead fist 36 cm out in front, a little below shoulder height, its elbow bent about 110 degrees; the
  rear fist in front of the chest, elbow about 100. With both forearms level at chest height and square-on it read as
  a sleepwalker's arms.
- **The weight shifts lightly between the back leg and the front,** once a second: the pelvis travels 8 cm, sits
  1.4 cm lower on the back leg, and the hips open 7 degrees as it goes back (the reference game's idle: 7 cm, 1.8 cm,
  7 degrees, once a second); the heels rise and settle with it, the chest a beat behind the pelvis, the fists riding
  it. It reads as ready to step in or back.
- **It never holds still.** One breath per loop, each fist drifting and clenching on its own timing. A fist held dead
  still is 10 of the 31 bones not moving (`lp check` motion.static).

The first build's punch (an unarmed right cross, 0.75 s, from the stance and back):
- **Load.** A short turn back onto the rear leg as the lead foot lifts.
- **Step.** The lead foot goes 12 cm forward and lands before the fist does.
- **Drive.** The rear foot pivots about 60 degrees on its ball with the heel rising, and the pelvis, spine, chest,
  shoulder and elbow turn through one after another, 0.02-0.035 s apart. **The whole body commits:** the hips turn 87
  degrees and the shoulders 143 to bring the rear shoulder through, the pelvis travels 20 cm forward and drops 5 cm
  onto the front leg, the head goes 26 cm with it. A first version turned 45 and 81 degrees and travelled 9 cm, and
  read as a polite reach; the reference game's cross measures 101 and 147 degrees and 22 cm. The fists tighten for
  the impact.
- **The head** turns back against the trunk (the neck and head take out 0.45 and 0.40 of the turn, and part of the
  lean), so the face stays on the target while the head travels with the body. Keep its lag short in a fast turn (10-18 ms
  here): at 30-45 ms the face swung 50 degrees off the target mid-punch.
- **The guard hand** draws back to the chin, the upper arm after the chest and the forearm after it.
- **Return.** A hold of two frames with a small overshoot; the elbow comes back first and the body unwinds behind it;
  the lead foot steps back into the stance.

Let the shoulder blade protract and lift a little with the punch (about 7 degrees forward and 3 up at the clavicle), and
the arm turn the rest from there. Taken wholly at the shoulder joint, the turn over-stretched the armpit's skin.
