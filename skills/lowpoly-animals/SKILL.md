---
name: lowpoly-animals
description: Build or critique a low-poly, game-ready 3D animal (mammal, bird, fish, reptile, insect or other creature, real or assembled from real parts) in the style of late-90s/early-2000s RPGs; for a person or a humanoid race (orc, ogre, troll, goblin) use lowpoly-characters instead. Use when generating an animal mesh in code, turning photos or a description into a low-poly animal, texturing, rigging or animating it, or when a procedural animal looks like tubes and capsules, has off proportions or moves like the wrong species. Load lowpoly-core first (the reference set, budgets, topology, weights, the texture method and the checks); this skill adds body plans, limb joins and the flank fold, feet and claws, heads, eyes, ears and opening mouths, fur, scales, plates, wet skin, chitin and membranes, wings, manes and other body parts as modules, planted-foot IK gaits, and an animal checklist.
---

# Low-poly animals (late-90s RPG style)

**Load `lowpoly-core` first.** It holds the method this skill builds on: the reference set and measuring against it (§1
there), budgets (§2), one-skin topology (§3), rigs and weights (§4), the texture method (§5), the motion checks (§6) and the
checks in code. Section numbers here are this skill's; "lowpoly-core §n" names that skill's. Paths starting
`lowpoly-core/` are in that skill.

**What the numbers come from.** Budgets and construction facts are measured on the 22 shipped ambient animal models of a
late-1990s commercial RPG: mammals, birds, fish, a gecko, a crab, insects (**the measured models**). Only the measurements
are used; no model, texture or file of that game is part of this skill. Topology, weights and locomotion are measured in
depth on five quadruped mammals: dog, bear, cow, pig and deer. Where a rule rests on less than that, it says so. The test
builds are in `references/case-study-*.md` (a 0.4 m housecat, a 12 m T. rex, a 0.9 m fox built from the skill alone). Feet,
eye lids, coats and the non-fur skins also draw on the same game's animal-like monster models, measured the same way.

**Reference files** (read the one for the step you are on; the sections say when):

| File | What it holds |
|---|---|
| `references/proportions.md` | the proportion table, L per body plan, the photo overlay, what to note from a side photo, the housecat and T. rex traced |
| `references/feet.md` | foot size, the wedge shape, soles, toes and claws |
| `references/heads.md` | the muzzle against the eyes, ears, jaws and mouths, long-faced heads, brows and sockets on very large heads, bird heads and beaks |
| `references/muzzles.md` | the muzzle by kind (leather pad, soft equine, muffle, disc, split lip, lipless): its end, nostrils, lips and chin as geometry, then painted as lit forms |
| `references/eyes.md` | side-facing, docile eyes: the almond, its tilt, the lids' shading outward, the tear duct at low pixel density, size against the model |
| `references/limbs.md` | building the muscle, not the bone: lobes, folds, the groin, the front view's widths; legs that bend as the anatomy does and keep their width in motion |
| `references/texture.md` | coat layers, eyes and pupils, noses, the head's coat and values, feet paint |
| `references/skin-types.md` | scales, plates, wet skin, chitin and membranes, and how to tell which an animal has |
| `references/reptile-skin.md` | reptiles: the scale for each zone, plates and beads, crossfades, colour matching, and the underbelly rolls contoured to the muscle |
| `references/locomotion.md` | planted-foot IK, the measured quadruped walk, the biped walk, checking a gait, standing balance, baked spring bones |
| `references/parts.md` | each body part (wings, beaks, jaws, feet, tails, manes, skins) as a module, and joining parts into composite or fantasy animals |
| `references/reference-measurements.md` | the measured data behind every number |
| `references/common-failures.md` | the animal failures from the test builds, how they looked, and the fix |
| `references/case-study-*.md` | the test builds, round by round |

**People and humanoid races** (an orc, an ogre, a goblin) are `lowpoly-characters`, not this skill: a person's joints,
texture charts, bind pose and checks differ, and that skill says where. A creature that mixes the two (a centaur, a
minotaur, a werewolf) takes its animal parts from here (`references/parts.md`) and its human parts from there.

## 1. The animal's references

The reference set, its views and how to measure against it are lowpoly-core §1; for an animal:
- **The set:** the species' skeleton and muscle in side, front and top views, plus the special parts (the skull, a foot, a
  hand or wing); photos in several poses and close-ups of each skin region (back, flank, belly, head, limbs, tail). For
  scales, plates or chitin, the cell size, shape and rows of each region (`references/skin-types.md`).
- **Where to look:** Ellenberger and Baum's plates of the dog, horse, cow, goat and lion (Wikimedia Commons) give skeleton
  and muscle together. A close relative stands in when the species has none (a dog's skeleton for a fox): say so.
- **L per body plan,** the proportion table's measures in each view, and what to note from the side photo (the masses, the
  leg segments and which way each joint bends, the foot posture, the head, the colour zones) are in
  `references/proportions.md`. Fix every mismatch the photos agree on; where they disagree because of pose, aim between them.
- **A composite or fantasy animal** (a griffin, an alicorn) is assembled from real parts, each referenced and checked as the
  real animal it comes from (`references/parts.md`); name each part in the spec's `"ref_parts"`.

## 2. Body plans: start from the closest construction

| Body plan | How the measured models build it | Notes |
|---|---|---|
| Quadruped mammal | One closed skin with 7-sided torso rings, 4-sided limb rings at the joints, legs grown from the body, ears closed into the head skin. 26–39 bones | The rest of this skill is written for it in most detail |
| Bird | Raven: 50 vertices, 8 bones (head, body, tail, two per wing). The wings are flat slabs inside one closed skin. Seagull: 0% blended corners (rigid segments). Chicken: 146 vertices, 18 bones, one closed skin | Wings get two bones each (inner and outer) and are flat, not tubes. Legs are thin 3–4-sided rings with a flat foot |
| Biped theropod (built once, see `case-study-trex.md`) | One closed skin of 8-sided rings, a 17-ring body-neck-head (12-sided from the jaw hinge forward), a 4-sided tail bridged to the rump, two holes in the belly for the legs, two in the chest for tiny arms. 563 vertices, 938 triangles, 38 bones | A hollow mouth with 46 pyramid teeth, the upper jaw overlapping the lower and a jaw bone (§5), a brow with eye sockets. A thigh lobe under the hip hole tapers through a mid-thigh ring to the knee (§3, rule 2), then the shin and a foot of three welded toes and a high first toe, each on its own bone. The hip joint sits 41% of the length from the nose. Its numbers come from the species |
| Fish | 18 vertices, 34 triangles, 3 bones (head, body, tail), one closed skin | Fins are painted or flat cards. Swimming is a side-to-side wave carried down to the tail |
| Lizard or sprawling animal | Gecko: 119 vertices, 20 bones, low and wide | The legs leave the body sideways and the elbows and knees point outward. The feet are flat and splayed |
| Arthropod | Crab: 125 triangles, 39 bones (one per leg segment), the legs partly open cards. Spider: 8 triangles as separate cards | Each leg segment is a card or a thin 3-sided prism with its own bone |
| Flying insect or bat | Butterfly: 26 triangles, 2 bones. Bat: 46 triangles, 7 bones | Wings are cards on wing bones; the body is a few triangles. A larger bat's membrane wing is in `references/parts.md` |

The cards (open edges) are for parts too thin to need volume. Everything else is one closed skin. A flyer's spec says
`"body_plan": "flyer"`, which skips the standing checks.

## 3. Topology for animals

The general rules (one skin, holes and bridges, rings, winding, normals, bind pose) are lowpoly-core §3. For animals:
1. **How limbs join the body (measured on the deer).** The top of a leg *is* a hole in the body's underside. 54 of the
   deer's 338 triangles join body-only vertices to leg-weighted ones.
   - **Cut the hole.** Remove the quad between the belly vertex and the lower-flank vertex of the two body rings that
     bracket the top of the leg. Its 4 vertices are the leg's first ring; bridge the next leg ring to it.
   - **Shared skin.** The belly vertex between the two legs (groin or brisket) is shared by both, and the thigh and upper
     arm are body skin: that is what makes the haunch and shoulder stretch when the leg swings. Weight them as in §4.
   - **Fallback.** A flattened root ring buried in the flank is only for code that cannot cut a hole; say so if used.
   - **Wings and side-mounted legs** (lizards) attach the same way: a hole in the flank, not a tube against it. A wing on a
     quadruped is in `references/parts.md`.
2. **The upper limb takes the shape of the muscle mass, not the bone.** Seen from the side, a quadruped's upper hind leg is
   a broad triangle: the front edge from the flank down to the kneecap, the back edge the hamstring continuing the rump down
   to the hock. **Details and the T. rex's numbers are in `references/limbs.md`: read it before building a limb.** In brief:
   - **Lobes:** every mass the reference shows (thigh, haunch, shoulder, upper arm) gets a ring at its fullest point, in
     every view. A thigh is fullest at about mid-leg in the front view; a long thigh gets a ring halfway down so it tapers to
     the knee. Keep limb rings about square, never pointed.
   - **Folds:** where masses touch (thigh and belly), pull the ring at the fold in, for 20-45 degrees between its faces,
     then paint a crease-and-rim pair. The belly's midline between the thighs sits above their inner edges.
   - **Checking:** count lobes and notches in the side, front and rear views. Budget cuts come from straight runs of the
     outline, never from a lobe or a fold.

   The first ring below the body spans the kneecap to the hamstring: its depth as a fraction of leg length is 0.19–0.20 on
   the slim deer and cow, 0.27 on the dog, 0.28–0.46 on the heavy pig and bear. A narrow knee ring set forward of the hole
   makes the rump overhang a stick-thin leg, which shows at once in a walk.

   **The hole must reach forward past the knee (the flank fold):** let it span three body rings, from behind the hip to
   ahead of the knee, and weight the waist ring lightly to the thighs. A hole ending behind the knee leaves a deep V-notch
   between belly and thigh (`references/limbs.md`).
3. **The underline follows the species.** Where the species has a tucked flank (cats, dogs, deer, horses), the underline
   rises from the chest to the flank, so the top of the hind leg shows. Heavy-bellied animals (pig, cow, bear) keep a low
   belly, but the thigh's front edge must still read.
4. **Where the triangles go** (lowpoly-core, "What a model is for"): from the species' anatomy, not another model's
   shares. Start from each part's share of the surface on the blockout built from the references, then move triangles
   toward where the outline turns in the side, front, top and rear views (a muscle's fullest point, a joint's crease) and
   where joints bend in the clips, and away from straight runs. `lp waste` lists the edges that shape nothing;
   budget.head_density catches a head that took the body's share. (The reference game's split is recorded as era context
   in `references/reference-measurements.md`, "Where the triangles go"; it is not a target.)
   **Ring counts.** Torso: the measured mammals use 7 sides (one belly vertex, two on each near-vertical flank, a two-vertex
   ridge on the back, so the body is taller than wide), 8 with a spine vertex for an unrolled back. Rings at the chest front,
   behind the elbows, the waist, the front of the haunch, the rump, the tail root. Limbs: rings only at knee or elbow, hock
   or wrist, then the foot. Tail: 3–4 sides tapering to a point, or a flat card for a bushy tail. Ears: part of the head skin
   (§5). Head: about five rings at its landmarks, more on a very large head (§5).
5. **Feet: match the species' foot posture and size, never the reference animal's.**

   | Posture | Examples | What touches the ground | Push-off |
   |---|---|---|---|
   | Plantigrade | bear, rodents, people | the whole sole, heel included | the heel lifts last, a short roll |
   | Digitigrade | cat, dog, birds | the toes only; the heel (hock) is high | a long roll onto the toes, the heel rising high |
   | Unguligrade | deer, cow, horse, pig | the hoof tip | the hoof pivots at its tip |
   | Knuckle-walking (forefoot) | giant anteater, gorillas | the knuckles: the paw is a mitten whose flat sole is the knuckle pad, claws curled under or behind | a short roll; in the swing the paw folds back |

   **Size, shape, toes and claws are in `references/feet.md`: read it before building a foot.** In brief: a flat sole at
   y = 0 on the foot's own bone; paws as sloping, splayed wedges (1.6-2.7 times wider at the ground, toes 0.8-1.6 ankle
   depths ahead); clawed toes welded into the foot's skin side by side, shaped from the species' foot anatomy at its
   reference's size, the claws coloured as the species' are, the footprint checked from below.

## 4. Rig and skin weights for animals

The general rules are lowpoly-core §4. The bones per body plan:
- **Spine:** root, pelvis, 2–5 spine bones. **Each leg:** a shoulder or hip bone, then upper, lower, (metapodial,) and foot.
- **Head end:** 1–3 neck bones, the head, the jaw if needed, and one per ear if the ears move (§5).
- **Tail:** 2–4 bones. **Birds:** two per wing. **Fish:** head, body and tail. **Arthropods:** one per leg segment.

**Leg-body junction (the measured deer):**

| Vertex | Weights |
|---|---|
| Flank vertices round the top of the leg | about ⅓ each to the hip, the upper leg and the spine |
| Groin vertex | 50/50 to the left and right thighs |
| Thigh below the body line | 100% upper leg |

Flank vertices with 30% or more of their weight on a leg reach 54–57% of the animal's height. A working start for a 7-sided
torso: the groin or brisket vertex body 0.3–0.5, the rest split between the two legs; the lower flank body 0.4, leg 0.6; the
upper flank above the leg body 0.75, leg 0.25.

## 5. Heads, eyes and faces

**Build the head from planes, not a sphere.**
- **Rings:** about five, at the neck joint, the back of the skull, the eyes (the widest ring), the stop or face, and the
  muzzle or beak, plus a nose or tip.
- **Jaw:** its own rings, shaped from its bones and muscles, one smooth curve from chin to throat (`references/heads.md`,
  "Jaws and mouths"). A closed mouth still shows the jaw's line.
- **Ears:** cupped shells closed into the skull's back corners (`references/heads.md`, "Ears"). **Armour scales:** painted from one direction field, modelled only on the outline (`references/parts.md`, "Overlapping armour"). **Long necks:** bones before rings, no bend tighter than about 1.7 neck radii, the head kept level (`references/parts.md`, "Long necks"). **Horns:** a separate closed piece of few sides swept along its centre line, sunk into a boss on skin weighted to the head only (`references/parts.md`, "Horns"). **Crests and frills:** a welded fin strip, not cards (`references/parts.md`, "Crests, spines and frills").

**The top line of a mammal's head.** In profile, the head's highest point is the crown, in the back third of the head
(measured: bear 19%, cow 31%, deer 39% of head length). From there the top line runs in one convex slope to the nose,
growing steeper and never stepping down; a brow ring taller than the crown, then a steep drop, reads as an eyebrow lump.
Check it in code: ring tops highest at or behind the ears, each step at least as steep as the last. **Not for birds:** a
raptor's crown is flat, its brow overhangs the eye, its beak is its own shape (`references/heads.md`, "Birds"). Long-faced
heads (a horse) are measured from the skull, with the head about 0.34-0.40 of the withers height (`references/heads.md`).

**Where the eyes point decides how the face is built.** This holds well beyond "predator or prey".

| | Side-facing eyes (most prey mammals, most birds, fish, lizards) | Forward-facing eyes (cats, dogs, bears, primates, owls) |
|---|---|---|
| Head shape | Usually long or narrow. The muzzle is half the head length or more in many mammals; a bird's beak is its own proportion, measured (a raptor's about a third of the head) | Broad skull, about as wide as long. Short muzzle: cat 20–30% of head length, dog or wolf 40–50% |
| Eyes in the texture | Painted in **profile** on the side pelt, one eye per side | In their own patch, projected from the direction the orbit faces: **head-on** on a flat face (cat, owl, primate), **oblique** on a long skull whose orbits face forward and outward (the measured dog and wolf, the T. rex) |
| Measured (texture per area, front faces against side faces) | Deer 0.68, cow 0.89, pig 0.92 | Bear 1.02, dog 1.19, wolf 1.08 (the dog and wolf are three-quarter frontal) |

**Building a forward-facing face:**
1. Make the eye ring the widest ring of the head. Put the next ring very close in front of it, almost as wide but shorter.
   The triangles between them point forward and form the flat face the eyes sit on. Keep both rings' tops on the top line.
2. Add a short muzzle ring, a nose ring and the tip.
3. **Unwrap the forward-facing triangles separately:** a front projection (`u = x`, `v = y`) into a free area of the
   texture, with duplicate vertices along the seam. Paint the face there head-on: both eyes, the nose, the markings and the
   mouth. The rest of the head stays on the side pelt.
4. Make the eyes large enough to read: a cat's eye is about a quarter of the face width. Paint the eye stack (§6).
5. Large upright ears (cats, foxes) face forward, so their opening shows from the front.

A hostile animal's eyes face forward under a brow fold and glow without a pupil: add `temperament/hostile` to the spec's
profiles, which sets `"eyes": "glow"` and replaces the species' pupil eye (`lowpoly-core/references/temperament.md`).

**More in `references/heads.md`: read it for any head.**
- **Eyes against the snout:** the eyes sit behind and above a distinct muzzle block, whose outline in the front view passes
  below and between them; the muzzle gets its own eyeless patch, picked by ring rather than by z.
- **Ears:** sizes, tilts, placement, the cupped shell and texture.
- **Muzzles** (`references/muzzles.md`): find the species' kind first. The end is a blunt face, never a point; the nostrils
  are rimmed hollows; the upper lip overhangs a crease and a chin. Paint each as a lit form, never a line. A grey ("white")
  horse's nose, lips and chin are dark skin.
- **Side-facing eyes** (`references/eyes.md`): an almond tilted up toward the back, never a round dot. The upper lid is heavy
  and the lower lighter, each fading to the coat over 3-5 texels. The inner corner is a low sharp point, darkest of all, with
  a short tear streak. The radius is 1.4-2.5% of the height (`lp check` eye.size).
- **Jaws and mouths:** each jaw from its bones and muscles: the lower jaw's own sides, edge and depth, the mouth's corner,
  the widest point over the jaw muscles, which jaw overlaps, teeth from the dental formula, the jaw's corner into the throat.
  A hostile mob gets modelled teeth at every tier: canines and incisor blocks as sunk pyramids, the mouth running back to
  its corner, a rounded chin, a dark inside (`lowpoly-core/references/temperament.md`, "Which to build"). The reference
  game's painted snarl is era context (`references/heads.md`), not the default. Measure every clip's gape with
  `lib/lowpoly/tools/jaw_study.py` and keep it within the species' maximum bony gape (temperament.md, "Open the jaw wide").
- **A very large head:** a mouth hole between two jaws with 3D teeth, brow and sockets as geometry, eyes in the lateral
  sockets with an oblique patch; creases round the eye under about 90 degrees, slivers under an aspect of about 10.

## 6. Texture: what is painted on an animal

The pelt, density, lighting, continuity and the engine's lights are lowpoly-core §5. For an animal:
- **First, name the skin types, region by region:** fur, scales, plates (scutes and armour), wet skin, chitin and membranes
  are painted and measured differently (`references/skin-types.md`; an alligator: keeled plates on the back, pebbled scales
  on the flanks, rectangular plates on the belly, ringed scales on the tail, a wet sheen). Each type's measured signature
  comes from `lib/lowpoly/tools/skin_study.py`. The fur rules below are the fur entry of that table.
- **The rest is in `references/texture.md`: read it before painting.** In brief:
  - **Coat layers:** the large light and colour zones, the form shapes (the masses outlined, the joints as crease-and-rim
    pairs, tendons, folds) and the strokes, each at its own size and measured against the measured coats. The strokes follow
    a flow field over the body, never one direction.
  - **Eyes:** a stack: a catchlight, a dark eye body, a lid that is a deeper shade of the coat fading into it, the upper
    lid stronger, a socket off the coat's value, and blended corners. The pupil's shape is the species' (a cat's vertical
    lens, a horse's horizontal bar, a reptile's slit).
  - **Noses:** a lit box with a structured nose (a lit top, nostrils with lit rims), a lit bridge, a dark mouth line and a
    shaded chin.
  - **One coat from rump to nose,** strong values on the head, feet painted in their own patch, soft-edged markings.
  - **Limbs and wings** painted as fully as the body, even on a large animal (`lp check` texture.limb_detail).

## 7. Animation

**Clips in the measured models** (from their names):
- **Everyone:** default stand, idle fidgets (graze, look around, scratch, several variants), walk, run, die.
- **Some animals:** attack, sit down and up, lie down and up, fly, glide.

Walk cycle length scales with size: pig 0.67 s, dog 0.75 s, bear 1.33 s, cow and deer 1.5 s.

**Idle:** keep it small: breathing, the tail, ear flicks, head turns. Feet stay planted.

**Legged locomotion: planted feet, not swinging sticks** (details in `references/locomotion.md`):
- **The cycle:** each foot stays planted while the body moves over it, rolls at push-off as its posture allows (§3, rule 5),
  swings forward in an arc and lands flat. Every foot uses the same stance speed.
- **Driving it:** each foot's path and pitch over the cycle, plus 2-bone IK on the two bones above it, never sine waves on
  each joint.
- **The IK:** add the body's bob to the IK roots and take bone lengths from the rest pose. Track each planted foot's lowest
  corner frame by frame.
- **Feet and legs:** carry flat feet level or toes-up in the swing, and give each leg kind its own settings.

**Biped walk** (built once, matched to one reference animation: round 12 of `references/case-study-trex.md`): two legs half
a cycle apart, each foot down about 0.6 of the cycle, the stance centred under the hip. The foot rolls about the toes' joint
with the toes flat, swings with them folded down, and lands flat. The body is lowest at double support.

**Quadruped walk:** use the measured ranges for the animal's group, never one animal: the share of the cycle a foot is down
(typically 0.7), lift (2-8% of the height; the high-stepping deer 9-21%), stride, how far the joints fold, and the footfall
order. Let the shoulder slide with a reaching foreleg, fold the hind leg into a Z in the swing, and carry the head lower in a
walk. The table and the notes on each joint are in `references/locomotion.md`.

**Legs that bend** (details and the measured numbers in `references/limbs.md`, "Legs that bend"):
- **Joints fold as the species' do.** Elbows, knees and hocks are hinges that bend one way and never straighten past their
  line (`lp check` motion.hyperextended fails on one frame of it); a carpus folds both ways of straight.
- **The skin keeps its width.** Keep each blended joint ring's fold under about 50° from the bind pose (a ring blended
  across a joint shrinks to cos(bend / 2)); spread a deep pose over the neighbouring joints; cap the wrist's turn against
  the forearm in the IK (the lion: 22-23°) and tip the pastern beyond it (motion.leg_rings, motion.leg_stretch_*).
- **Each leg on its own in an action clip:** its own timing, height and path; feet left behind follow the body
  (motion.lockstep). An attack follows the species' hunting behaviour (`lowpoly-core/references/temperament.md`).

**Standing:** the centre of mass inside the feet's contact in every standing clip (lowpoly-core §6). Don't trust the bind
pose's feet; fix it in the standing clips with the walk's own IK (`references/locomotion.md`).

**Other locomotion (construction measured, motion not studied in depth):**
- **Fish:** a side-to-side body wave growing toward the tail. The measured fish does it with 3 bones.
- **Flying birds and bats:** wing beats on two bones per wing, a glide with the wings held out, and a hover; an attack from
  the hover needs a recovery of a flap or two before the next. A winged quadruped's takeoff, hover and tucked forelegs:
  `references/locomotion.md`, "Flying on a winged quadruped".
- **Insects:** wing flaps on a couple of bones. **Many-legged animals:** alternate legs in groups, feet planted as above.

For all of these, compare against footage of the species (lowpoly-core §6): soles flat at y = 0 in the stance, lift, duty,
stride and joint angles in range, and the joint edges stretching without tearing.

## 8. Checklist (before calling it done)

Run lowpoly-core's checklist first; then, for an animal:

**Shape:**
- [ ] The skeleton, muscle and photos of the requested species (or of each real part of a composite) in every view; L and
      the proportion table written; the top line, underline, half-widths, head size and carriage, joint positions, stance,
      limb positions and tail or fin roots agree with the overlay (§1).
- [ ] The head takes about 20–30% of the vertices (medium and large animals; teeth and a mouth's interior not counted).
- [ ] Construction matches the body plan (§2).

**Topology:**
- [ ] Limbs, neck and tail grow out of the body: triangles join body-only vertices to limb-weighted ones (§3, rule 1).
- [ ] Upper limbs take the shape of the muscle masses (the thigh triangle), and the underline suits the species.
- [ ] The hind leg's hole reaches forward past the kneecap (flank fold, about three rings): no V-notch between the belly and
      the thigh in the side or rear view.
- [ ] Every muscle mass the reference shows has a ring at its widest and a fold where it meets the body (side, front, rear);
      measured from the front, each thigh is widest at mid-leg, not the knee (§3, rule 2).
- [ ] Feet match the species' posture, anatomy and size (the footprint against the reference, seen from below), with flat
      soles at y = 0 and their own bones; paws are sloping, splayed wedges; clawed toes are welded into the skin side by
      side, each on its own bone (§3, rule 5).

**Head:**
- [ ] The top line is convex from crown to nose.
- [ ] The jaws were measured as separate structures (§5): the lower jaw's depth at chin, middle and back, the mouth's
      corner, the widest point, the overlap and the tooth rows. An opening mouth is a hole between two jaws with 3D teeth and
      its own bone, looked at open from the front and side; a very large head has a geometric brow and sockets.
- [ ] The eyes are where the skeleton's orbits are: in profile for side-facing eyes, in their own patch from the orbit's
      direction for forward-facing ones, each showing once per side in a textured head render, with no crease round it
      sharper than about 90 degrees (§5).
- [ ] Forward faces: the front view shows the muzzle outline below and between the eyes; the muzzle has its own patch.
- [ ] Ears closed into the head skin (no open edges, 5 or more shared vertices) at the skull's back corners, bases sunk
      below its top line; the front has its own patch, with a dark opening and a fur rim where the species shows one.

**Rig:**
- [ ] The leg-body junction weighted as in §4, and blended corners in range for the size.

**Texture:**
- [ ] The skin types were named per region (`references/skin-types.md`) and each painted to its type; scales, plates, wet
      skin and chitin measure in their column there (crevices, edges, painted gloss, cell size).
- [ ] The coat's three layers measured against the coat table; strokes follow a flow over the body (§6).
- [ ] Eyes painted as the stack, with the species' pupil (or a glow for a hostile mob); the nose with a lit top and
      nostrils, a lit muzzle bridge, a dark mouth line and a shaded chin, measured on a textured head render (§6).
- [ ] Head paint has the measured heads' contrast: brightness spread about 0.1 or more and a range of about 0.0–0.6.
- [ ] Feet painted, not just tinted: toe gaps, claws or nails, or a hoof band with its cleft, in their own patch.

**Motion:**
- [ ] Planted feet, IK legs including the body's motion, per-leg-kind settings and values from the group's range.
- [ ] Locomotion compared phase by phase with reference frames of the species.

## Common failures

The animal failures found in the test builds, what each looks like and the section that fixes it, are in
`references/common-failures.md`; the failures any model can have, and the habits that catch them, are in
`lowpoly-core/references/common-failures.md`. Read both when a build looks wrong, and run the habits before every review.
