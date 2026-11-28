---
name: lowpoly-characters
description: Build or critique a low-poly, game-ready humanoid character (a human, or a humanoid race built on the human base such as an orc, ogre, troll, goblin, dwarf or elf) in the style of late-90s/early-2000s RPGs. Use when generating a person or humanoid mesh in code, adapting the human base to another race or body type, texturing a face, skin or hair, rigging hands and joints, or animating an idle, run or attack, or when a character's face, jaw, ears, hands, armpits, elbows or knees look wrong. Load lowpoly-core first (the reference set, budgets, topology, weights, the texture method and the checks); this skill adds measuring a body against a survey, the torso and limbs built from muscle, body types as morph targets and blend spaces, the head's planes, ears, eyes, brows and mouth, hands and thumbs, joints that fold with soft tissue meeting, the texture charts and recolour masks of a character, hair, and how to change proportions for other races.
---

# Low-poly humanoid characters (late-90s RPG style)

**Load `lowpoly-core` first.** It holds the method this skill builds on: the reference set and measuring (§1 there),
budgets (§2), one-skin topology (§3), rigs and weights (§4), the texture method (§5), the motion checks (§6) and the checks
in code. Section numbers here are this skill's; "lowpoly-core §n" names that skill's.

**What the numbers come from.** Anatomy first: a body survey (ANSUR II, 4,082 US Army men, public), clinical and
art-anatomy references for the face, ears and hands, and biomechanics papers for the joints and gaits. Every rule was
built and checked on the plugin's first player character, a median man (`references/case-study-human-male.md`), with a
reviewer looking at it in the viewer from every side. The reference game's human models were measured as era context
(how much a face is modelled versus painted, how a jaw is cut); they are named generically and are never a target.

**This is a base to adapt.** The human build is written as rings, a body-type parameter and parts built from parameter
sets (the ear, the thumb, the hair's edge), so an orc, ogre, troll or goblin is a change of proportions and shapes on the
same construction. `references/races.md` says what to change and what to keep for each.

**Reference files** (read the one for the step you are on):

| File | What it holds |
|---|---|
| `references/body.md` | measuring a body against a survey; the torso's rings; limbs from muscle; the neck, shoulders, armpits and glutes; body types as morph targets |
| `references/head-and-face.md` | the face's thirds and fifths, the profile, the head's planes, the jaw and chin, the throat, ears, eyes, brows and mouth, and the era's painted shading |
| `references/hands.md` | the mitten hand, the thumb's anatomy and joints, and the hand at rest, in a fist and on a grip |
| `references/joints-and-motion.md` | single-hinge knees and elbows, helper bones where soft tissue meets, contact versus crossing, the idle, the run, blend spaces |
| `references/texture.md` | a character's charts, seams between regions, recolour masks and tone ramps, the face's mask, hair painted along its flow, normal transfer for attached pieces |
| `references/races.md` | adapting the base: ogres, trolls, orcs, goblins, dwarves, elves, from the real anatomy each borrows |
| `references/case-study-human-male.md` | the first character, round by round: every fault the reviewer found, its cause and the fix |

## 1. The character's references

The reference set and its views are lowpoly-core §1; for a character:
- **A body survey for the proportions.** ANSUR II's medians (or another survey's) for heights, breadths, depths, girths and
  lengths, written to the spec's `"measurements"` file. `body_measure.py` measures the model as an anthropometrist would,
  over its clothes, and `lp check` judges it (body.median at most 4%, body.worst at most 15%; a girth over clothes may run
  8% over). A race starts from the human survey and scales it by the race's analog (`references/races.md`).
- **Anatomy plates** for the skeleton and the muscles in front, side, top and back views; the head's planes (Loomis,
  Reilly, Proko's planes of the head); clinical norms for the face's profile, the ear and the jaw; the hand's joint
  ranges.
- **Photos and drawings from the reviewer** win over a rule when they show the specific character. A sketch of a hairline
  or a fist is a reference: measure it.

## 2. Budget and parts

The `character` tier (lowpoly-core §2): 400-720 vertices, 760-1400 triangles, 24-40 bones. A human with a face, hands
and joints that read as human, and modelled hair, takes nearly all of it: the first build ended at 707 vertices, 1398
triangles and 42 bones (two over: the armpits' helpers, kept by choice).

- **Pieces.** One closed skin for the body and head. The hair, the ears and anything worn are separate closed pieces whose
  edges sink into the skin (lowpoly-core §3; `mesh.loose` reads 0 when an edge passes through).
- **Where the triangles go.** On the first build the head's skin took 14% of the triangles at 2.5 times the body's
  density, and the hair, a separate piece, another 22%. Move triangles to where the outline turns (the jaw's angle, the cheekbone, a muscle's fullest point) and where
  joints fold; take them from flats hidden by the hair or the clothes (a scalp under hair can be a fan).
- **When the budget is spent,** spend paint before polygons: an ear's antihelix, the mouth's line and the eyes' sockets
  are painted; a rim's thickness or a finger's third joint is what the tier can't buy.

## 3. Topology for characters

The general rules are lowpoly-core §3. For a humanoid:
1. **Torso: half rings from the front midline to the back.** Each ring is a superellipse (squareness 2 an ellipse, below
   2 a diamond, above 2 a boxier rectangle) with its own half-width, front depth and back depth from the survey. The
   chest near 2, the shoulders 2.2 (seen from above a man's shoulder top is a rounded rectangle; at 1.35 it came to a point,
   at 1.9 an almond), the waist and hips 1.35-1.4 (`references/body.md`).
2. **Limbs from the muscle, not the bone.** Arm rings round their own axis, from a hole between the axilla and shoulder
   rings; leg rings from a loop round the hip. A ring at every mass's fullest point (the deltoid, the biceps, the calf a
   third of the way down from the knee) and at each joint's line.
3. **The head in planes.** Rings at the head's horizontal breaks (chin, lips, nose base, nose tip, eyes, brow, forehead);
   the lower face's rows local to the mouth's barrel, the cheek one plane from the cheekbone to the jaw. Rows wrapped round
   the whole head draw bands across the cheek (`references/head-and-face.md`).
4. **The ear, thumb and hair are parts built from parameter sets**, so a race changes numbers, not the construction.
5. **Build one half and mirror it; break the symmetry after.** Hair is never symmetric: an asymmetry pass after the mirror
   moves each side's hair on its own, and the hair's chart wraps all the way round.

## 4. Rig and skin weights

The general rules are lowpoly-core §4. The humanoid rig: root, spine, chest, neck, head; per side a clavicle, upper arm,
forearm, hand, two finger bones (the mitten's knuckles and middle joint), three thumb bones (base, knuckle, end joint),
thigh, shin, foot and toe; and the helper bones where soft tissue meets (`references/joints-and-motion.md`).

- **A hinge is one joint.** A knee or elbow bends at one ring set on the joint's line, shared between the two bones; the
  rings above and below belong to their own bone. Spreading the bend over three rings is how an animal's leg keeps its
  width: on a human it makes a second joint, a block between two creases. (`lp check` leaves the animal leg rules off for
  `"body_plan": "biped"`.)
- **Where soft tissue meets in a fold, it touches.** The calf against the hamstrings behind a bent knee, the forearm's
  flexors against the biceps, the arm's inner side against the chest, the fingertips into the palm, the thumb on the
  fingers: a helper bone presses the tissue into the fold as the joint closes. Skin that crosses there is contact, not a
  fault; judge it in the renders. A slit, notch or V where they should meet is the fault.
- **The thumb bends across the palm,** about its own axis, its pad toward the index; it never curls with the fingers.

## 5. Heads, faces and ears

In `references/head-and-face.md`. In brief:
- **Proportions:** thirds about 1 : 1 : 1, the eyes at half the head's height, the rule of fifths across the eyes; the
  survey's head length, breadth, menton-sellion and bizygomatic breadth.
- **Profile:** the chin on the nasion's vertical, the lower lip a few mm behind the nose-chin line, nasofacial angle 30-40,
  nasolabial 90-95, a dip under the lip 4-6 mm deep.
- **Jaw:** the lower edge, menton to gonion, at about 25 ± 5 degrees to the Frankfort line; the gonion under the ear; the
  gonial angle 120-125 in men; a man's jaw stays nearly as wide as its angle until it turns to the chin.
- **Ears:** 64 x 36 mm, standing 23 mm off the head; the top at the brow's outer end, the lobe at the nose's tip, the tragus
  about an ear's length behind the eye socket's rim, tilted back about 20 degrees; seen from the front a C, widest in its
  upper half; joined along a broad root, lit with the head's normals.
- **Paint at the era's level:** sharp dark lines a texel wide (lids, pupil, mouth) inside broad soft shadows (the eye's
  socket, under the nose, under the lower lip); the eye's white never brighter than the cheek.

## 6. Texture

In `references/texture.md`. A character's texture is one chart per region, each unwrapped round its own axis and shared by
both sides (the head mirrored, the hair a full wrap of its own), the head and hair at twice the body's density. Every
option a player can change (skin tone, hair colour) is a mask of the texels it recolours plus a tone ramp; shading stays
in the paint, so the recolour keeps it. A strip that mixes two regions' vertices goes wholly to one chart, with the two
paints made to agree on the ring where the seam sits.

## 7. Animation

In `references/joints-and-motion.md`. Every body type gets its own variants of the clips where mass changes the pose (the
idle's arms, the run's arm swing and the calf), blended by the body-type option as a blend space; the checks judge each
variant on its own morph body. A run's feet keep one ground speed (planted, nothing slides), and the game must move the
character at the clip's speed.

## 8. Checklist (before calling it done)

- [ ] `lp check` passes, with every warning explained (a deliberate asymmetry, a contact fold, a budget over by choice).
- [ ] Body measures against the survey (or the race's scaled table): median within 4%, the worst within 15%.
- [ ] Every body type viewed: thin, median and muscular, front, side, back, three-quarters, above and below; the idle and
      every clip played at each.
- [ ] Joints folded in every clip with nothing open where tissue meets: knees, elbows, armpits, the fist.
- [ ] The face against its proportions and profile, the jaw's angle, the ears from the front, side and back.
- [ ] No seam, sawtooth or stray line where two charts meet (the throat, the hairline, an ear's root); every option's
      mask checked at its extremes (the darkest skin, the palest hair).
- [ ] The studies written (what was measured, against what, the numbers before and after), so the next character starts
      from them.

## Common failures

| What showed | Cause | Fix |
|---|---|---|
| A V-shaped cutout behind a bent knee, inside a bent elbow or down from the armpit | the skin there blended between two bones only, so the fold opened as the joint closed | a helper bone presses the tissue into the fold (calf and hamstrings, biceps and flexors, the armpit's fold) |
| The knee bent in two places, a block between creases | the bend spread over three rings, as an animal's leg is weighted | one shared ring at the joint's line |
| The thumb stood out like a thorn | a separate spike bending about the fingers' curl axis | a jointed tube grown from the palm, bending across the palm about its own axis |
| The fist had a tunnel through it | the mitten's middle joint folded no further than one real finger joint | fold it past either real joint (126 degrees): it stands for two |
| The ears hung like fangs from the front | the lower ear stood furthest off the head | the upper back of the rim furthest out, the lobe tucked in |
| The ear looked stuck on | its back fanned to one sunk point (a stalk); lit by its own faces | a broad root under the skin; normals blended with the head's |
| A sawtooth of light and dark under the jaw | the jaw-to-neck strip split between the head's and body's charts, painted with two lights | the strip on one chart; the lights blended to agree at the seam |
| Lines across the throat | the mouth's paint placed by height alone, landing on the jaw's underside | the face's lines on front-facing skin only |
| A hair lock clipped through the bridge of the nose | the fringe's long lock swept onto the midline below the brow | the fringe's tips stop above the brows |
| Hair like wood planks, then marble | stripes and noise with no flow | paint along a flow field from the whorl and the part, clumps big, medium and small |
| The lower face heavy, the line under the chin long | the jaw's lower edge at 14 degrees, near level | about 25 degrees to the Frankfort line |
| No chin from the side on a muscular build | the throat pushed forward with the neck's growth | the neck grows at the back and sides; the throat stays where the skeleton holds it |
| The whites of the eyes glared | the white brighter than the skin | the white at 0.65-0.9 of the cheek, in the socket's shadow |
| The variant clips judged wrong | checked on the average body | judge each variant clip on its own morph body |
