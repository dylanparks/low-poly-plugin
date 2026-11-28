# Plan: gaits from walk to sprint on a speed slider

> **Delete this file once the plan is implemented in the plugin.** When the gaits, the speed blend and the guidance
> below exist, what is worth keeping moves into `skills/lowpoly-core/references/motion-principles.md` and
> `skills/lowpoly-characters/references/joints-and-motion.md`, the README line that points here is removed, and this
> file goes.

Status: proposed, not started. The first humanoid has one gait, a jog-paced run (0.72 s a stride pair, about 2.2 m/s).

## Why

A character moves at more than one speed, and the gaits differ in where the motion is, not only in how much there is.
A walk sped up is not a run, and a run slowed down is not a walk. The game needs a clip for each state and a way to
move between them without the feet sliding.

## The five gaits

| | Walk | Fast walk | Jog | Run | Sprint |
|---|---|---|---|---|---|
| Speed | 1.3 m/s | 1.9 m/s | 2.5 m/s | 3.5 m/s | 7 m/s or more |
| Foot on the ground, share of the cycle | about 0.62 | about 0.58 | about 0.40 | about 0.31 | about 0.22 |
| Both feet down at once | yes | briefly | never (a flight) | never | never |
| Cycle time (a stride pair) | about 1.0 s | about 0.85 s | 0.74 s | 0.70 s | about 0.45 s |
| Stride length (a stride pair) | 1.35 m | 1.59 m | 1.86 m | 2.46 m | to be sourced |
| Arms | nearly straight, swinging from the shoulder | straight, a bigger swing | bent, a small pump | bent about 90 degrees, pumping | bent 90 degrees, the hands from hip to chin |
| Knee in the swing | about 60-65 degrees | a little more | about 94 | about 109 | the highest, the thigh near level in front |
| Trunk | upright | upright | a slight lean | a lean | a strong lean |
| The foot lands on | the heel | the heel | the heel or midfoot | the midfoot | the ball |

- **Measured:** the walking speeds, cadences, stride lengths and stance shares (1.00, 1.32 and 1.87 m/s: 101, 118 and
  141 steps a minute; 1.18, 1.35 and 1.59 m; stance 62.7% falling to 58.5%); the stance share in running (31%) and
  sprinting (22%); the jog's and run's cycle time, stride and knee flexion (2.5 and 3.5 m/s); the change of gait near
  2 m/s.
- **Not yet sourced with numbers:** the sprint column, the arms' description in every column, the walk's knee flexion,
  the trunk's lean. Source them before building; mark what stays by eye.
- **The speeds are the game's decision:** they set how fast the character moves in each state. Confirm them with the
  person before building.

## How to build it

1. **Reference first.** For each gait: photograph sequences from the side, front and rear (a walking and a sprinting
   plate beside the running plates already used), and the measured numbers above completed. The reference game's walk
   and run are a style check only.
2. **One gait function driven by speed**, not five hand-set clips: the cycle time, the foot's time on the ground, the
   stride, the foot's roll (heel, midfoot or ball), the knee's lift, the pelvis's turn, tilt and bounce, the chest's
   counter-turn, the arm's carriage (straight to bent) and pump, and the trunk's lean are each a curve over speed,
   with the measured values as its points. The first humanoid's run becomes the jog.
3. **Five clips baked from it** at the table's speeds, each with its thin and muscular variants (the arms' carriage and
   swing, the calf, the feet's track), as the run has now.
4. **A speed slider** (`"clip_blends"` extended from three clips on one option to any number: a list of clips with the
   value each sits at). The viewer and the game blend the two neighbours bone by bone, and play the result at the
   blended cycle time, so the ground speed follows the slider and the feet do not slide.
5. **One hard seam, between the fast walk and the jog** (about 2 m/s). A walk always has a foot down and a run has a
   flight, so the two do not blend: across the seam the slider cross-fades quickly at matched phase (each clip's left
   heel strike at phase 0), which is also how people change gait.
6. **Checks.** Each clip judged as a gait by the liveliness checks; the foot's ground speed against the clip's stated
   speed (planted means no sliding); the walk's duty over 0.5 and the others' under; every body type for crossings.
7. **Guidance.** The table and the method into `motion-principles.md` (the gait section) and the character's
   `joints-and-motion.md`; `"clip_blends"` in its new form documented with the character viewer.

## What it touches

- `lib/lowpoly/tools/character_view.py` and `character_page.html`: a blend over more than three clips, playback rate
  from the blend, the cross-fade at the seam.
- `lib/lowpoly/animate.py`: perhaps a shared stride helper (a foot's stance and swing from duty, stride and lift), if
  the first humanoid's gait function generalises.
- `lib/lowpoly/cli.py` and `targets.json`: a ground-speed check for gaits, if it earns its place.
- The skills' gait sections and the README.

## Sources so far

- Walking kinematics at three speeds: PMC1866234.
- Stance share in walking, running and sprinting: PMC7595692.
- "Biomechanics of walking, running, and sprinting": PubMed 7416353.
- Running at 2.5 and 3.5 m/s (Fukuchi 2017): PMC5426356.
- The walk-to-run transition near 2 m/s: reviews of the transition (Froude number 0.5).
