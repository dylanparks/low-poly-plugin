# Motion principles: clips that read as alive

Read this before writing any clip. A clip can pass every anatomy check (no joint bent backwards, nothing crossing, the
feet planted) and still look like a machine. What makes it look alive is weight, order and variance, and each can be
measured. `lp check` judges them at the motion stage (the motion.* checks listed under "The checks"), from
`lib/lowpoly/tools/motion_quality.py`; `lib/lowpoly/animate.py` has the building blocks.

Tags on the numbers: **[measured]** from a study of people or animals; **[craft]** an animator's rule of thumb;
**[ours]** a value from a build here. Frame counts in craft sources are at 24 fps; they are given here in seconds.

## What robotic looks like

The first humanoid's clips were each driven by one phase curve: every bone a multiple of the same number.

| Clip | What it did | Measured |
|---|---|---|
| Punch | the whole body turned as one piece and arrived in one instant; the head stayed where it was; the feet turned with the pelvis on the spot | sync 1.00; head turn 3 degrees under a trunk turning 34; no step |
| Run | the legs cycled under a pelvis that neither turned nor tilted; the arms swung from a still chest | sync 1.00; pelvis yaw 0, roll 0 |
| Idle | only the chest breathed; both arms were mirror images | 63% of the bones never moved; twin 1.00 |

Rebuilt by the rules below: the punch reads sync 0.35, order 0.89, head turn 25 degrees under a trunk turning 125, with
a step and a pivoting rear foot; the run sync 0.36, pelvis yaw 11 and roll 11 degrees, shoulders against hips -0.98; the
idle 19% still, twin 0.43. **[ours]**

## The rules, in the order they pay

1. **Nothing starts or arrives together.** A move runs along the body: each part starts and stops a little after the
   one that carries it. Everything arriving in one instant is the commonest fault. **[craft]**
   - Delays between neighbours: trunk to shoulders 0.04-0.08 s, shoulder to elbow 0.08-0.12 s, elbow to hand
     0.08-0.12 s; stops offset by 0.08-0.17 s. Heavier parts lag further and stop slower. **[craft]**
   - A fast strike compresses these: the punch here runs drive, pelvis, spine, chest, shoulder, elbow at 0.02-0.035 s
     apart. **[ours]**
   - Not everything overlaps: offset the big masses and the ends of chains, or it turns to mush. **[craft]**
2. **Force comes from the ground, through the hips, outward.** A throw or strike is proximal to distal: legs, pelvis,
   trunk, arm. **[measured]** The pelvis starts toward the target while the trunk is still turning away.
   **[measured]** Key the feet and pelvis first and hang the rest from them, never the hand first.
3. **Weight moves before the feet do.** The hips shift over the supporting foot before the other foot lifts (the
   pressure under the feet shifts 0.3-0.5 s before a step's heel leaves; postural adjustments start about 0.1 s before
   a self-paced move). **[measured]** A foot lifted from under a centred pelvis reads weightless. **[craft]**
4. **Weight shows in the up and down.** The body drops onto a landing leg, which bends, and is pushed up off it. The
   lowest point is just after contact, the highest at push-off or in flight. **[craft]**
5. **Anticipation, then the move, then a recovery longer than both.** A strike that bursts to full speed from rest
   looks weightless; the wind-up is small and opposite. Recovery is the longest phase. **[craft]**
6. **A fast move overshoots and settles.** The arriving part runs a little past its pose and comes back; the parts it
   carries settle after it (soft tissue 0.04-0.12 s, hair 0.17-0.33 s). **[craft]** No sourced size for the overshoot:
   the builds here use 8-12% of the move, damped within 0.3 s. **[ours]**
7. **A held pose keeps moving.** Breath, drift in the direction of the last move, the head settling: never a frame
   range in which nothing changes. **[craft]**
8. **The head is carried by the trunk and steadied by the neck.** It is neither fixed in space nor bolted to the chest.
   - Running: head pitch runs opposite to the head's rise and fall (about 180 degrees out of phase), keeping the gaze on
     a point ahead. **[measured]**
   - Turning: gaze first, head next, body last (walking into a turn, the head leads the path by about 11 degrees and
     0.2 s). **[measured]**
   - In a strike: the neck takes out part of the trunk's turn and pitch so the face stays on the target. The punch here
     gives the neck and head 0.45 and 0.40 of the trunk's turn back, 0.03-0.045 s late. **[ours]**
9. **Left and right are not twins.** Mirrored limbs moving in the same instant look lifeless. Shifting one side by a
   frame doesn't cure it: change the pose, the size and the timing. **[craft]** A gait's two steps do match each other,
   half a cycle apart, or the gait limps.
10. **Planted feet stay planted; moving feet step, pivot or rise.** A foot on the ground turns about its own ball or
    heel and nothing else. If the pelvis turns over it, the leg absorbs the turn (`animate.limb_rotations`).
11. **Arcs, eased, but not everywhere.** Limbs travel on arcs with eased ends. A reach has a bell-shaped speed that
    peaks near the middle (peak about 1.75-1.9 times the mean). **[measured]** A strike is the exception: slow out of
    the hold, fastest at contact.

## Building a clip

Build in this order, each layer hung from the one before:
1. **The ground plan.** Where each foot is in every phase: planted (fixed to the ground), pivoting (fixed at the ball),
   stepping (lifted along an arc) or cycling (a gait). Write the feet's world positions first.
2. **The pelvis.** Its travel (over the supporting foot, down onto a landing, forward with a drive), its turn and its
   tilt. Solve the legs from the pelvis to the feet (`animate.limb_rotations`, with the knee's pole turned with the
   pelvis and foot), so the feet stay where the plan put them whatever the pelvis does.
3. **The spine, as a chain.** One curve sampled later for each bone up the spine (`animate.chain`), plus the
   counter-move: in a gait the chest turns against the pelvis; in a strike the trunk winds back before it follows.
4. **The head.** Lagged behind the chest, with the neck taking out part of the trunk's turn and pitch.
5. **The arms, shoulder girdle first.** The clavicle, then the upper arm, forearm and hand, each later than the last;
   the hand and fingers drag behind the forearm and settle after it.
6. **Settle and variance.** A damped wobble on what stopped fast (`animate.wobble`), a different phase or period for
   each side, breath under everything.

`animate.py`: `two_bone`, `limb_rotations` (a leg or arm solved in three dimensions), `smooth`, `ease_in`, `ease_out`,
`bump` (a move out and back), `overshoot`, `wobble` (a damped settle), `lagged` and `chain` (one curve run later down a
chain). Quaternions are (x, y, z, w).

With few bones, the same rules hold with fewer steps: a three-bone spine still runs pelvis, chest, head; a one-bone
hand still lags the forearm. A pure sine on every bone is the robot again: give each bone its own phase, and reshape or
sum two periods where a cycle would otherwise repeat exactly.

## By kind of clip

### Idle
- **Breath as a wave** from the belly up: belly, chest, shoulders, each a little later; the head rides it by
  millimetres. **[craft]** Rate 12-18 a minute at rest **[measured]**, 20-25 alert, 25-30 in a fighting stance
  **[craft]**; the chest travels 1-2 cm **[craft]**.
- **Weight shift** from foot to foot over 4-8 s **[craft]**; in long standing, shifts of about 22 mm side to side
  about once a minute **[measured]**. The pelvis moves over a foot, tilts and turns a little, and the legs are solved
  to the planted feet.
- **Asymmetry:** each arm, hand and finger group on its own phase and period.
- **Loop** 2-4 s for a simple idle, 8-12 s for one with fidgets. **[craft]** A longer loop made of periods that divide
  it (4 s breath in an 8 s shift) hides the repeat.
- First humanoid: one breath per 4 s running belly, chest, shoulders 0.06 and 0.11 of the cycle apart; pelvis sway
  11 mm with roll and yaw. **[ours]**

### Gait (a human run; walks scale down)

| Quantity | Measured (running, 2.5-3.5 m/s) | First humanoid run |
|---|---|---|
| Stride time | 0.74 s at 2.5 m/s; 0.70 s at 3.5 | 0.72 s |
| Rise and fall of the body | 77-91 mm (about 4.4-5.2% of height) | 5.1% |
| Pelvis turn about the vertical, range | 14 ± 4 degrees (5-28 between runners) | 18 |
| Pelvis side tilt, range | 14 ± 4 degrees | 11 |
| Pelvis forward tilt, range | about 8 degrees | not measured (the chest pitches 1) |
| Upper body turn, range, arms swinging | about 30 degrees (a simulation) | 30 |
| Step width | 2-4 cm | 5.5 cm at the ankle (see below) |
| Knee flexion in the swing | 94-109 degrees | 106 |
| Hip flexion / extension | 44-53 / 4-8 degrees | |
| Contact time | about 0.29 s (duty about 0.4) | 0.26 s |

- **The chest turns against the pelvis** (antiphase), and the arms swing with the chest: arm extremes with leg extremes.
- **Within the measured range, choose the lively end.** A run set at the middle of every measured range read as
  timid beside the style's own runs; at the top of the ranges (and with the elbows pumping, 40 degrees of open and
  close) it reads as a run. Past the ranges it bounds. **[ours]**
- **The hip drops on the swing side** as the body lands; the spine bends the other way so the head stays level.
- **The head** pitches against the bounce and faces the direction of travel. **[measured]**
- **Poses:** contact (leg nearly straight), down (lowest, support knee bent), push-off, flight (highest; at least a
  frame or two with both feet off the ground). **[craft]**
- **Step width on a low-poly leg:** at the measured 2-4 cm the swing foot passed through the standing shin. Widen to
  what clears, and wider again for a heavier build (5.5 cm from the midline; 7.7 cm on the muscular build). **[ours]**
- **Faults:** a foot landing too far ahead reads as braking; too much hip drop a stomp; too much trunk turn a washing
  machine; a foot sliding back before it lifts was planted too long. **[craft]**

### Action (a strike)

| Quantity | Measured (rear-hand straight punch) | First humanoid punch (0.75 s, from its stance) |
|---|---|---|
| Fist's first move to contact | about 0.11 s | 0.085 s (shoulder from 0.24 s, elbow 0.275-0.325 s) |
| Retraction to guard | 0.17-0.24 s (skilled quicker) | 0.15-0.16 s (elbow 0.375-0.52 s, shoulder 0.39-0.55 s) |
| First move to back in guard | 0.40-0.45 s | 0.31 s, after a hold of 0.05 s at full reach |
| Fist speed at contact | about 8 m/s | |
| Load at contact | front foot about 60%, rear 40% | pelvis 5 cm forward over the front foot |
| Share of the force | rear leg 38%, trunk turn 37%, arm 24% | |

- **Start from the stance the move belongs to.** A model that fights has a combat-ready stance clip (a guard, a
  crouch, a bristling stand), and each attack's first and last frames are that clip's first, not the idle's: a punch
  thrown from hanging arms spends a third of its time getting ready. The stance is an idle and is judged as one.
  Build it to photographs of that stance and compare the render with them from the same angle: a stance made from an
  idea of one came out square-on and narrow.
- **Phases:** stance, weight onto the rear foot and a short step of the lead foot, a small wind back, the drive (rear
  foot pivots on its ball, heel rising; pelvis, spine, chest, shoulder, elbow in turn), contact, overshoot and settle,
  retraction (the elbow first), recovery to the idle.
- **The lead foot lands and braces** before contact; the pelvis turns over it. **[measured, qualitative]**
- **The guard hand stays at the face**; the body does not fall past the front foot. **[craft]**
- **Commit the whole body.** A strike that only turns the trunk a little and reaches reads as timid. The reference
  game's unarmed cross turns the hips about 100 degrees and the shoulders about 150, carries the pelvis 22 cm forward
  and drops it 10 cm (on a 1.72 m figure); the first humanoid's now measures 87, 143, 20 and 5. **[ours, style]**
- **Game timing:** a player's light attack 0.1-0.2 s of wind-up and 0.7-1.2 s in all; enemy attacks signal for at
  least 0.34 s and hold the end pose 0.17 s or more, so they can be read. **[craft]**
- **Not found in any source read:** the pelvis's and trunk's rotation in degrees, the lags between segments in
  milliseconds, the heel's lift, the head's travel. The clip's values for these are judged by eye and by the checks.

### Four legs
- **Two walkers joined by a spine.** The hips and the chest each rise and fall, offset from each other, and the head is
  a third mass offset again. **[craft]** A rigid spine and head over cycling legs is the quadruped robot.
- **Measured on horses** (ranges over a stride; each oscillates twice per stride):

  | | Walk | Trot |
  |---|---|---|
  | Head, vertical | 79-117 mm | 61-78 mm |
  | Withers, vertical | 27-36 mm | 47-92 mm |
  | Pelvis, vertical | 66-79 mm | 56-89 mm |
  | Phase | head opposite the withers, with the croup | all three together, lowest near mid-stance |

- **Faster gaits bend the spine more** (a gallop folds and opens it). **[craft]**
- **The tail last,** as baked springs (`lp bake-springs`).
- **Not found:** head bob or spine motion measured on dogs or cats. Use footage (`walk_sheet.py`).
- Gait timing, duty factors and what each leg joint does: `lowpoly-animals/references/locomotion.md`.

## The checks

`lp check --stage motion` runs `motion_quality.py` over every clip and judges the worst clip of each kind. All are
warnings: each one is a place to look, and a clip may break one on purpose (a stiff golem, a statue's idle). A clip's
kind is read from its name (idle, stand, rest, sleep, spar, guard, stance...; walk, run, trot, fly, swim...; anything else is an action);
the spec's `standing_clips`, `walk_clip` and `"clip_kinds": {"prowl": "gait"}` override it.

| Check | Measure | Range | Clips |
|---|---|---|---|
| motion.sync | share of moving parts whose fastest moment is within 12 ms of three others' (a hand or foot counts once; a gait's legs are left out) | at most 0.5 | action, gait |
| motion.order | along pelvis-to-hand and pelvis-to-head chains, share of neighbours peaking in order, nearer first (needs three pairs) | at least 0.6 | action |
| motion.static | share of skinned bones that never turn half a degree | at most 0.25 | all |
| motion.hold | longest stretch in which nothing moves | at most 0.15 s | all |
| motion.twin | left and right limbs as mirror images in the same instant | at most 0.85 | idle, action |
| motion.head_follow, motion.head_fixed | the head's turn over the upper trunk's, where the trunk turns over 10 degrees | 0.2 to 0.95 | action |
| motion.head_travel | how far the head's joint travels | at least 1.5% of height | action |
| motion.feet_shift | a foot's travel where the body's mass travels over 3% of height | at least 1% of height | action |
| motion.action_slide | slide of the lowest foot bone while it is on the ground | at most 1.5% of height | action |
| motion.gait_bounce | rise and fall of the skin's mean point | at least 0.8% of height | gait |
| motion.pelvis_yaw, motion.pelvis_roll | the pelvis's turn and side tilt | at least 4 and 3 degrees | gait, humanoid |
| motion.counter | correlation of the pelvis's turn with the chest's turn against it | at most -0.5 | gait, humanoid |

`python lib/lowpoly/tools/motion_quality.py model.gltf [clip ...] --detail` prints each bone's range and the moment it
moves fastest, which is how to find what is crowding a sync or breaking an order.

The measured mountain lion, built before these rules, reads: sync 0.52 in its pounce, 32% of its bones still in the
idle and 29% in the walk (the spine, chest and head never move), and its paws sliding 18% of its height in the pounce.
Those are what its next motion pass fixes.

What the checks cannot see: whether a pose reads, whether the timing has the right feel, whether the motion suits the
character. Look at every clip.

## Looking at a clip

1. At full speed: note the one to three things that bother first.
2. At half speed: pops, and spacing that changes gear.
3. Frame by frame: contacts holding, one-frame glitches.
4. As a silhouette, and from a second angle: does each key pose read, do the arcs hold in three dimensions.
5. Follow one point at a time: the nose, a hand, a heel. A hitch in the head usually starts in the trunk.
6. Ask: does anything start or stop with everything else; are left and right twins; do planted feet slide; do the hips
   reach a foot before the other lifts; does the settle end.

A contact sheet of the clip's phases from the side, the front and three-quarters (the viewer page, or `walk_sheet.py`
for a gait) shows the stance, the step, the wind, the strike and the recovery in one picture.

## Sources

Craft:
- Cooper, "The 12 principles of animation in video games" (Game Developer).
- Totten, "12 principles for game animation" (Game Developer).
- "Follow through and overlapping action" (RebusFarm blog): per-joint delays and settle times.
- "Adding weight to your game design, part 5: follow-through and overlap" (Game Developer).
- Williams, *The Animator's Survival Kit* (weight, run timing), read through a student's transcription with page numbers.
- Zirpolo, "Animating the run cycle" (Game Developer); "Key poses of a run cycle" and "Animating nothing" (AnimSchool blog).
- Idle and melee animation guides (MoCap Online blog); an analyst's measurements of enemy attack phases in an action RPG
  (Game Developer).
- "Animating four-legged beasts" (Game Developer).
- Holden, "Spring-It-On" (springs: damping, frame-rate independence).

Measured (PMC numbers are PubMed Central articles):
- Punch timing with instrumented gloves: PMC8659887.
- Punch force, fist speed and foot loading (Dinu & Louis 2020): PMC7739747.
- Punch reviews and the kinetic chain: PMC10414587; Filimonov 1985, Cabral 2010 and Turner 2011 as summarised in a
  university sports-science blog.
- Running joint angles, cadence and stride (Fukuchi 2017): PMC5426356.
- Running pelvis ranges: PMC12852323; between runners (Folland 2017): PMC5473370.
- Vertical oscillation: PMC9687194.
- Upper-body rotation with arm swing (a simulation): PMC11929735.
- Head pitch against vertical translation in running: PMC2768006.
- Gaze and head leading a turn: Frontiers in Human Neuroscience 2015, 9:312.
- Quiet standing: PMC10170532; weight shifts in long standing: Duarte & Zatsiorsky 1999 (abstract).
- Horse head, withers and pelvis at walk and trot: PMC9657284.
- Proximal-to-distal sequencing: Putnam 1993.

Read only as abstracts or search summaries, so treat as approximate: step width, contact time, the anticipatory
adjustment and step-initiation timings, the weight-shift size in long standing, the thorax-pelvis antiphase in running.
