# Quadruped walk: the measured ranges and what the joints do

The detail behind SKILL.md §7. Read it before animating a four-legged walk.

The legs are half of a gait. The spine, the chest and the head move too (the hips and the chest each rise and fall,
offset from each other, and the head is a third mass offset again), an attack runs from the hind legs forward through
the spine to the head and paws, and an idle never holds still: `lowpoly-core/references/motion-principles.md` has the
rules, measured ranges for a horse's head, withers and pelvis, and the liveliness checks (`lp check` motion.sync,
motion.static, motion.gait_bounce and the rest).

**Quadruped walk, measured.** Use the range for the animal's group, never one animal. The deer is the outlier.

| | Dog, bear, cow, pig | Deer (light high-stepper) |
|---|---|---|
| Share of the cycle a foot is down | 0.58–0.92 (typically 0.7) | 0.56–0.67 |
| Lift, % of height | 2–8 | 9–21 |
| Stride (foot travel per cycle) | about 0.8–1.6 leg lengths | about 0.85 leg lengths |
| Front wrist or knee fold in the swing | dog 76°, cow and pig 41–67° | about 100°, the hoof flipping back |
| Swing of the top segment (shoulder or hip) | 43–78° | 15–53° |
| Footfall order | dog and pig: lateral sequence (LH, LF, RH, RF); bear and cow vary | LH, RF, RH, LF |

What the joints do, in general:
- **Front leg:** the shoulder blade moves. The front leg's top segment swings far (the dog's shoulder bone swings 60° or
  more). Let the shoulder joint slide forward and down as the leg reaches. A fixed shoulder on a straight foreleg
  can't reach a planted foot: the IK runs out of length and the foot floats. In the swing the foot lifts with the
  wrist flexed.
- **Hind leg, push-off:** the leg pushes off behind the hip. Digitigrade animals straighten it at toe-off almost into
  one line from hip to toe, with the heel high; the metatarsus follows most of the foot's roll. Plantigrade animals
  lift the heel late and less.
- **Hind leg, swing:** it folds into a Z: knee forward, hock bent, foot tucked. The metatarsus trails at toe-off and
  comes back under the hock by mid-swing.
- **Head carriage changes with the gait.** Walking predators carry the head lower and further forward than when
  standing (a neck drop of about 15°). Grazers drop it further. Keeping the standing head height in a walk
  looks stiff.

## Standing

**Standing: the feet under the centre of mass.** A standing animal's centre of mass must be over its ground contact, or
it is falling. Check every standing clip (idle, attack, stand), not just the walk.
- **Measure it:** the centre of mass from the closed skin's volume (uniform density is close enough), and the ground contact
  from the vertices within a few centimetres of the ground. The centre of mass must fall inside the contact, and near its
  middle.
- **Don't trust the bind pose:** it is built for modelling and weights, and its feet are wherever the build put them.
- **Where it goes wrong:**
  - a biped, whose two feet are the only support;
  - a long-tailed or heavy-headed animal, whose centre of mass sits far from the hip;
  - a walk whose stance was moved (§7 walk) while the standing clips kept the bind pose.
- **Measured by `lp check`** (`motion.balance`, with `lib/lowpoly/tools/stand_study.py`): the worst margin over the standing clips,
  where 1 is centred, 0 is on the edge of the ground contact, and a negative margin means falling. It fails below 0. The
  standing clips default to the idle and any clip named idle or stand; `standing_clips` in the spec lists others.
- **Measured by `lib/lowpoly/tools/stand_study.py <model.gltf> - [clips]` (and by `lp check`):** the worst margin per standing clip, where 1 is
  centred, 0 is on the edge of the ground contact, and a negative margin means falling.
- **Which clips:** only those where the animal stands still on planted feet (idle, stand, a planted-feet attack). A walk, a
  run, a lunge onto one foot or a fall is off balance for moments by design. On the measured bear, the idle passes and the
  run and the attack do not, as they shouldn't.
- **Planted feet don't slide** (`motion.planted`, from the same tool): each sole, anchored where it touches down, may not move
  along the ground while it stays there; a step that lifts and lands again starts a new anchor. Warns above 0.3% of the height.
  The usual cause is breathing: the housecat's idle tilted the chest bone 0.015 rad and the forelegs, parented to it, swung
  their toes 3.6 mm (0.83% of its height), which showed. The upper-arm bones now turn by minus the chest's angle, and the slide
  is 0.2 mm. The reference game's still-stand clips slide 0-0.11%; its fidgets paw and scrape by design (the pig drags a hoof
  21 cm), so leave such clips out of `standing_clips`.
- **Fix it in the standing clips** with the walk's own IK, the feet level. Where a clip moves the hips (a lunge), the thighs
  undo that rotation so the feet stay planted.
- **The test T. rex:** its centre of mass was 0.46 m ahead of the hip joint, but the bind pose's feet touched the ground from
  0.31 to 1.39 m ahead of the centre of mass, so it would have tipped backward. Moving the feet 0.75 m back put the contact
  at 1.12-2.20 m around a centre of mass at 1.54 m.

## Legged locomotion: planted feet, not swinging sticks (from SKILL.md §7)

**Legged locomotion: planted feet, not swinging sticks.** This applies to any legged animal:
- **Stance:** each foot stays planted flat while the body moves over it. In place, the foot slides back at a constant
  speed, like a treadmill. Every foot uses the same stance speed (stride ÷ stance time), or some will skate.
- **Push-off:** near the end of the stance the foot rolls the way its posture allows (§3, rule 5).
- **Swing:** the foot travels forward in an arc with the joints folded and lands flat.
- **How to drive it in code:**
  1. Define each foot's path and pitch over the cycle: planted, rolling, arcing.
  2. Solve the two bones above it with **2-bone IK**. Knees bend forward and elbows back on mammals; bird legs bend at
     the ankle.
  3. Set the foot bone so its world pitch matches the path.

  Sine waves on each joint can't keep feet planted: they slide and sink, and the joints barely bend.
- **Flat feet are carried level or toes-up in the swing, never toes-down.** A plantigrade hind foot pitched toes-down
  (the way a cat's heel-up paw is) keeps its toe on the ground all through the swing, so the foot drags. Test it:
  the lift measured from the lowest sole vertex must reach about 5% of the height. Digitigrade paws fold heel-up
  and still clear the ground; long flat soles don't.
- **IK must include every motion of the body** (bob, crouch, sway). Add the root offset to the IK roots, or planted
  feet sink or float by the size of the bob.
  - **Take the bone lengths from the rest pose:** the upper bone's length must come from the rest pose, not from the moved
    root to the rest elbow. On the fox, the shoulder slides with a reaching foreleg, and the length was taken from the slid
    shoulder. The solver saw an arm 2 cm too long early in the stance and 3 cm too short late in it. The planted paw hovered
    1.4 cm, then sank 1.9 cm, and the walk measured each foot down only 0.54 of the cycle against the 0.70 it was built with.
  - **Check:** track the planted foot's lowest corner frame by frame; it must stay at the ground through the stance.
- **Give each leg kind its own settings** (front and hind, or by segment count), not one shared set.

## Checking a gait against footage and in code (from SKILL.md §7)

**Compare against frame-by-frame reference.** Get a locomotion cycle of the species (a frame sheet, or frames grabbed
from video). Render your clip at the same phases as side-view silhouettes on a grid (`lib/lowpoly/tools/walk_sheet.py`): skin the mesh at each
phase, project onto `(z, y)`, head left, with the near limbs dark and the far limbs light. Compare phase by phase:
- where each foot is at contact, and how far back it goes at push-off;
- each limb's outline (a muscle mass or a stick);
- how the joints fold;
- head and tail carriage.

The numbers (lift, duty, joint angles) can all be in range while the shapes are still wrong. The sheet shows it at a
glance.

**Check it in code:** skin the mesh at every frame.
- Sole vertices are at y ≈ 0 and level in the stance frames.
- Lift, duty and stride are in range.
- Joint angles (side-view angles between segments) are like the reference group's.
- The joint edges stretch but nothing tears.

## Biped walk (built once: the T. rex, rounds 11, 12 and 14 of its case study)

- **Timing:** two legs half a cycle apart; each foot down about 0.6 of the cycle, so both feet share the ground briefly. The
  test animal's cycle (2.97 s) and stride (the planted foot slides 2.1 m, about 1.2 m/s) were matched to a reference animation.
- **The stance:** centred under the hip joint, not under the bind pose's foot. That keeps the leg within reach (93% of its
  length at most) and the centre of mass over the feet.
- **The roll:** about the middle toe's joint. The toes, each on its own bone, undo the foot's pitch, so they lie flat while
  the heel rises.
- **The swing:** the ankle rises, the foot tips slightly toes-up, and the toes fold down. A curl lowers the claws by the toe's
  length times the sine of the curl, so raise the swing to match: the test animal's claws cleared the ground by 0.13 m.
- **The body:** it bobs twice a cycle, lowest at double support and highest at mid-stance (3.5% of the height), and the IK
  roots follow it. The pelvis rolls and turns a few degrees, the chest the opposite way, the tail swings against the hips,
  and the head bobs.

## Flying on a winged quadruped (the alicorn, rounds 12-13)

**Takeoff** (2.4 s, plays once): a crouch with the hooves planted (IK, drifting at most about 1 cm), the shoulders turning
up and the wings unfolding in the first flare (the rest shell swaps out there: `references/parts.md`), push-off and the
first downstroke at about 0.4 s, then two beats rising into the hover. Its last frame must equal the hover's first
exactly (every bone, sprung ones included). The spring baker loops every clip, so a one-shot clip is left out of it and
its mane and tail are blended into the looped clip's baked keys over its last part.

**Hover** (a loop of two slow beats, about 1.15 s each): the body pitched about 15 degrees nose-up and bobbing with the
beats, the neck and head held level, big strokes with the hand folding on the upstroke, the tail streaming down and back,
the hind legs dangling lower than the forelegs and swinging after each beat. Report the centre of mass against the lift
(the wings' area seen from above): the alicorn's sat 0.15 m ahead of the lift centroid, between the root and mid-chord.

**The forelegs tuck like a jumping horse's** from push-off: the upper arm swung forward about 35 degrees, the forearm
forward to about level, the knee (carpus) folded 130-145 degrees so the cannon lies back under the forearm with the soles
to the rear. In flight the legs are free: no planted IK, no stance code, and no counter-rotation against the breathing.
The alicorn's forelegs hung straight down in the first hover, though nothing constrained them: the forearm's and cannon's
local turns had opposite signs and cancelled. Measure each joint's angle in the posed frame (and the hoof against the
elbow) rather than trusting the local values.

## Secondary motion: baked spring bones

Parts that hang off the body should lag, swing and droop rather than move with the bone that carries them: a tail behind a
walk, a bird's primaries on the downstroke, ears, a crest, a trunk. The engine plays baked clips, so the motion is simulated
once and stored as keys: `lp bake-springs model.gltf springs.json out.gltf` runs spring bones (the VRM spring-bone method:
inertia, a pull back toward the animated pose, drag, gravity, a fixed bone length, collision spheres and the ground) over
each clip as a loop and writes the result back as rotation keys.

- **Chains:** list each part's bones parent first, `{"bones": ["tail2", "tail3", "tail4"], "stiffness": 5, "drag": 0.4,
  "gravity": 1}`. Leave the first bone of a tail or wing (the one that sits in the body) out of the chain, so the root
  stays where the animation puts it.
- **Branches and clips:** a part that branches (feather bones on the arm, forearm and hand) is one chain per branch. A
  chain can name its `clips`, so the same bones can be loose in one clip and stiff in another (a soaring wing's
  primaries droop 30 degrees; in the flap the same bones lag 10-15) in one config and one pass.
- **Per clip:** `"per_clip": {"attack": {"stiffness": 12}}` on a chain changes its stiffness, drag or gravity in one clip
  (a swoop's accelerations flop ears that hang well in a hover), and `"clip_keys": {"hover": 84}` gives a long clip more
  baked keys (24 keys over a 4 s loop is too coarse).
- **Tuning:** stiffness in bone lengths per second (4-8 follows the animation with a lag; 0 hangs free), drag 0.3-0.5,
  gravity 0-2. It prints each bone's largest turn away from the animation: a tail's tip 15-25 degrees behind a walk reads as
  weight; over about 45 degrees it flops.
- **Colliders:** spheres on the thighs, the body or the back keep a tail or a wing's feathers outside the skin; the ground
  (the bind pose's lowest point by default) keeps them above the floor.
- **Loops:** each clip runs a few warm-up loops first, so the baked loop closes; the report gives the seam before closing
  (raise `warmup` if it says so).
- **The test:** the fox's tail (`tail2`-`tail4`, stiffness 5, drag 0.4, gravity 1) lags its walk by 13-19 degrees, root to
  tip; with stiffness 0 and gravity 6 it hangs straight down and its tip rests on the ground.
