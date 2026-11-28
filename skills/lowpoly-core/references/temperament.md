# Temperament: docile and hostile

**Status: draft.** It comes from the reviewer's brief for the first pair, a docile bat and a hostile giant bat. It will be
rewritten from what that comparison shows.

The same species can be ambient wildlife (docile) or an enemy (hostile), and the player reads which one it is at a glance.
That reading comes from a few features. The anatomy stays real either way: a hostile animal is still built from its
skeleton and muscle and measured against its references. Temperament changes which species and individuals are referenced,
and how a few features are shaped and posed.

## Ask first

If the request doesn't say which it is, ask before gathering references. A "giant bat" could be either, and a "fox" is
usually docile. The answer changes:
- the species the references come from (a hostile bat draws on a vampire bat; a docile one on a fruit bat);
- the head;
- the extremities;
- the idle and attack clips.

## What changes

| Feature | Docile ("this couldn't hurt me") | Hostile ("this is a threat") |
|---|---|---|
| **Eyes** | Round, large and dark, with a soft highlight; the lids relaxed; often set to the sides (a prey animal's eyes watch all round) | Front-facing, like a predator's: both eyes look at the viewer and show whole in a front view. Angular: the upper lid cut straight or slanted down toward the nose, under a modelled brow fold, with a bright or coloured iris (yellow, amber, red) that reads against a dark face |
| **Mouth and jaw** | Closed, no teeth showing | A jaw on its own bone, built as geometry, with visible teeth from the species' dental formula: the canines, the incisor rows and the cheek teeth that show when it opens (`lowpoly-animals/references/heads.md`, "Jaws and mouths"). Canines alone read as a mouth missing its teeth (the Kodiak bear, 2026-11-24). Held part open in the idle and fully open in the attack (`lowpoly-animals/references/heads.md`, "Jaws and mouths") |
| **Head shape** | Rounded cranium, smooth muzzle | Sharper planes: a heavier brow over the eyes, a blunt or snarling nose and wrinkles over the muzzle, ears set wide; follow the species (a vampire bat has a flat nose pad, no nose leaf, and upright pointed ears) |
| **Skin and coat** | Soft, fuzzy fur; even tones; clean edges | Rougher, straggly fur at the edges; higher contrast; darker overall, with the eyes and mouth the brightest points. Darken by shifting the whole value range, keeping its layers (large masses, form shading, fine hair, tufts) and the flow field: re-run `lp check`'s coat checks after darkening. The giant bat's near-black pass flattened every layer to almost nothing and ran every stroke one way |
| **Extremities** | Smooth curves | Longer, more hooked claws. Keep the real animal's outline otherwise: a ragged, torn wing edge was tried on the hostile giant bat and reverted, because the reviewer preferred a real bat's wing; the threat reads from the head, eyes, teeth and pose |
| **Pose and motion** | Relaxed: head level or lowered, slow breathing | Forward-leaning and tense: head low and forward, shoulders up, quick head turns, a gape or snarl in the idle. The attack from the species' own hunting behaviour, each leg on its own timing (below, "The attack") |

## Eyes: front-facing, under a brow

**Predator against prey.** A predator's eyes face forward, so both look at you; a prey animal's sit on the sides of the head.
That is much of why an animal reads as threatening, and it holds for most mammals and reptiles. It isn't a hard rule:
follow the species, and for insects use the eyes' colour and size instead.

**How the reference game's wolf builds it** (one of its monster models, measured on its head; not one of the 22 ambient
animals):
- The eyes are **painted, not modelled**: there is no eyeball geometry.
- Each eye sits on a facet angled forward beside the nose bridge, directly under a **brow fold**. The fold is an angled crease
  where the forehead plane meets the muzzle plane, sloping down toward the nose.
- The painted upper lid lies on that crease, so the brow shades the lid and the glare holds from every angle.
- **The mouth is painted on open geometry, not modelled teeth** (re-measured 2026-11-26 with `lib/lowpoly/tools/jaw_study.py`;
  an earlier version of this note said the wolf's teeth were closed pyramids, which the file does not bear out). The jaw is a
  small wedge of 8 vertices (16% of the head's) on its own bone, held 7 degrees open in every pose, a 2.7 cm gap. There is no
  cavity: the two lip rims are left as open edges. The teeth are painted on a 68 x 44 texel strip of gums and teeth, mapped
  onto 12 triangles that face forward and down: 7 under the snout (the upper row, on the head bone) and 5 on the jaw's front
  (the lower row). From the game's 3/4 camera that reads as a snarl full of teeth for no extra vertices.
- **Which to build: a hostile mob gets modelled teeth at every tier.** The reference game's painted mouth is era context, not
  the default. Tried on a medium-tier mountain lion (2026-11-26), teeth painted on the palate and floor behind a 4 cm
  opening at the snout's tip read from the game camera as a pink slit: no jaw, no teeth. Rebuilt as below it read at once,
  in the idle snarl and in the attack. The same lesson as the T. rex's (a painted mouth looked painted on), the Kodiak's and
  the gorilla's (canines alone read as a mouth missing teeth):
  - **A visible row of closed pyramids, sunk in the lip rims:** per side an upper and a lower canine (the lower in front)
    and an upper and a lower incisor block, painted as three incisors with two dark gaps. The cheek teeth may be painted
    along the rim behind the canines. 8 pyramids, 32 vertices and 32 triangles: pay for them from the body's straight
    runs, not the head's landmarks (the lion gave back two barrel rings and a tail ring).
  - **A mouth as long as the species':** the corner under the eye's front on a cat or dog, the lower jaw swinging from
    there (the corner half on each jaw), not a slit at the snout's tip.
  - **The jaw's front a rounded U** (the giant bat), and the inside kept dark (`lowpoly-animals/references/heads.md`).
  - A docile animal keeps its mouth closed, and needs no teeth. Say in the report which you built.

**The glow: no pupil, and smaller than you think.** A hostile mammal's or bird's eye reads best as a small, soft glow with no
pupil and no slit. **The fierce glare the user settled on** (the Kodiak, 2026-11-24, from their reference image): bulky
half-moons, not slits (a flat top over a deep round bottom, about as deep as half their width), the top sloping steeply
down toward the nose (about 0.5 of its run); a flat, bright yellow core going to an orange band at the edge, with a hard
border about a texel wide, no soft fade; set deep in a dark socket that hugs the glow on every side, a heavy brow shadow
on its top along the slope, the brow ridge lit above, frown creases between the brows, and darkness under it. What read
sad before was a small, soft glow with the slope the wrong way and a soft ring round it: the anger comes from the steep
slope and the brow, and the dark socket gives the bright glow its contrast.
The measured wolf's is about 6 x 3 texels, core luminance 0.75 against a 0.13 surround. A slit pupil and a large almond
read as a cartoon villain, not an elite enemy. Size it to the face, though: 0.09 of the head's width suits a short face
(the wolf, the giant bat), but on a long or broad head it read as a pinprick, and the user asked for bigger glows on the
gorilla (about 0.12 of its head's width, a 37 mm almond) and the Komodo dragon (a 20 mm almond). Don't go past that: on
the Kodiak bear's broad, short face (0.40 m wide) a 48 mm glow, 0.12, read a little big, and the user had it brought down to
42 mm, about 0.105. Aim at 0.10-0.12 and judge it on the rendered face. A reptile takes the glow too (the Komodo dragon's, approved by the user); keep a slit pupil only when the contract asks for it. The eye
checks' catchlight and rim thresholds come from pupil eyes; for a glow, report them as not applying.

**Ask for it with the profile, not a sentence.** A hostile silverback gorilla shipped a docile brown eye with a catchlight:
its colour profile said "dark brown, small and deep-set", its eye kind (`eyes/forward`) asked for a catchlight and a rim, and
"hostile" was only a word in its rules, so every layer the builder read described a pupil eye and the pupil-eye checks
passed it. Add `temperament/hostile` to the contract's profiles: it sets `"eyes": "glow"` (the pupil-eye checks then
don't apply), puts the glow in the palette and replaces the eye kind's pupil rule, and it resolves after every other layer
wherever it is listed. `lp contract` and `lp check` note a spec whose name or rules say hostile without it; a hostile
animal that keeps a real pupil on purpose (a reptile's slit) sets `"eyes": "pupil"` in the contract.

**So for a hostile head:**
- Angle the eye facets about 25-40 degrees off straight ahead.
- Add a brow fold over each eye (a vertex or two pulled out to make the crease). Optionally push the eye's centre in a
  little for a shallow socket; paint its shadow on the brow above the eye, not as a ring round it.
- Paint the eye on those facets. No eyeball mesh is needed.
- Check it in a dead-front view: both eyes whole.
- **Measure which way the eye's face points, in the head's own frame** (the head is often pitched in the bind pose). The
  Kodiak's eye was painted on the forehead's slope, inward of the brow line: its face pointed 39 degrees up and 11 out, so
  the eyes looked at the sky and read even from directly above. Put the eye on the face under the brow, at the corner of
  the face, and pull the brow vertex out and a little forward until that face points 25-40 degrees out and level (the bear:
  42 degrees out, 4 down). Then test the eye's visibility by casting from the camera onto its skin, not from its centre,
  which sits inside the head.
- **Then check the eye against the species' skull, front and side.** Facing alone isn't placement: moved to the corner of the
  face to face forward, the Kodiak's eyes sat 0.85 of the head's half-width out, at the face's corners; a bear's sit close
  beside the nose bridge, about 0.4 of the half-width out, at about 0.35-0.43 of the head's length from the nose (the user's
  front photo). To have them there and facing forward, steepen the stop (bring the forehead's front vertices forward) so
  the face beside the bridge looks ahead. **Draw a forward-facing eye's shape across the face** (x out from its centre), not
  along the head (s): on a face that looks forward, s barely changes across it, and the glow smeared into a bar.
- **An angry glow slants down toward the nose, and the anger is in the brow, not a ring.** The Kodiak first read sad: its slant
  was measured along a coordinate that ran the other way once the eye faced forward (the inner corners high: a worried
  brow), and a dark ring round each eye read as sunken and tired. Slant the glow's top down toward the nose, lay a heavy brow
  shadow right on that top along the same slant, light the brow ridge above it, add two frown creases pinching between the
  brows (each leaning outward as it rises, a "\ /" that meets low over the nose: leaned the other way, a "/ \", they read
  as a raised, worried brow, which the user caught on the Kodiak), and darkness under it; then make the glow bulky, bright and hard-edged in a deep dark socket (below). Check the slant's direction on the rendered face, both eyes.
  Keep the socket and the under-eye dark off the snout: a socket stretched along the slant carries its low inner end down
  the side of the muzzle, and on the Kodiak it read as a streak of black paint under each eye (the user, 2026-11-24).
  Tighten the socket toward the nose and below the glow, and fade the under-eye shade to nothing at the inner corner.
- **Paint the face by position, not by facing.** Snout terms that switched on each face's normal (a lit bridge, a shaded
  side) drew a hard line along the edge between the bridge's faces and the side's, right past the eye's inner corner.
  (Position chooses what is painted where. The smooth, interpolated normal may shade it or fade it through a soft ramp,
  never switch it face by face: `lowpoly-characters/references/texture.md`, "Paint placed by where the skin faces".)
- **Open the jaw wide when it threatens.** The user found the first hostile mobs' gapes too timid and asked for them wider
  (2026-11-24). What shipped: the giant bat's bite 70 degrees at its peak (from 58), its snarls 38; the Komodo's threat
  and lunge about 40 (from about 31); the gorilla's roar about 40 (from 30) and its charge 24. Leave the idle's resting
  gap alone. A wider jaw can drive the chin into the chest: the gorilla's threat went from 18 to 34 crossings until the
  head tipped back 0.12 radians with the gape (a roaring animal lifts its head anyway), which brought it to 16.
- **How far a jaw can open is the species' anatomy** (measure every clip with `lib/lowpoly/tools/jaw_study.py`: the angle at
  the hinge between the upper lip's front and the chin):
  - **The limit:** no clip opens past the species' maximum bony gape. A modern cat's is about 65 degrees (the puma is the
    worked example in Kitchener, Van Valkenburgh and Yamaguchi, "Felid form and function"); measured domestic cats average
    45-51 degrees at full opening (Renner et al., Journal of Veterinary Dentistry, 2023). Look up the species' figure, or its
    family's, before animating, and cite it: a gape past it reads as a broken jaw, not a threat.
  - **The threat uses most of it:** a hostile attack or roar near the maximum, the idle's snarl a third to a half of it.
  - **At rest and on the move** the mouth is shut, unless the species pants or the contract asks for a snarl.
  - **The head follows the bite:** lift the head as the jaw opens until the chin clears the chest (motion.crossings), as the
    gorilla's threat needed; how high comes from the species' own footage, not another model.
  - Snapping bites (open, shut within a few frames, open again) are an animation style of the reference game's era: use them
    when the contract asks for that look.

## By body plan

- **Mammals and reptiles** have every row available; the jaw and teeth carry the most.
- **Birds:** the beak's hook, the eyes (a fixed glare under a heavy brow ridge), raised hackles.
- **Insects and arthropods** have no jaw to show. The eyes do the work, with their colour, brightness and shape, along with
  the mouthparts (mandibles held open), spines and the stinger's carriage.

## References

A hostile build still needs the real animal's skeleton, muscle and photos (SKILL.md §1). Style references (concept art, a
costume, a painted texture) are good for the mood: the eye shape, the ragged edge, the contrast. Use them to describe
features and to compare against, never to trace geometry or texture from.

## The aggressive stance and rearing (the Kodiak bear, hostile, 2026-11-24; *approved by lp check*: 43 checks, no warnings)

**The aggressive stance** of a heavy quadruped, in the idle: the weight forward onto braced forelegs (the root 5% of the length
forward and a little down, the centre of mass toward the forefeet), the shoulders up (the chest raised on straight forelegs, so
the hump or withers bunch), the head low and thrust forward below the back line with the face turned up to look ahead, the ears
pinned back, the jaw part open on the canines, heavy breathing with a huff, and sudden small moves (a bear's jaw pops, a low
swing of the head). The feet stay planted by the IK.

**Rearing onto the hind legs must be balanced on the hind feet** (motion.balance) from the moment the forefeet leave the ground
until they land again. Order it by the balance, not by the look: first *gather* (the hind feet step forward under the body, the
forefeet step back, the hips sit back) until the centre of mass is over the hind toes; then pitch up about the hips, lifting the
forefeet as soon as the arms can no longer reach (by then the weight is already back); hold; on the way down the forefeet reach
the ground before the centre of mass passes the hind toes, then the heavy landing, then the feet step back. Measure the centre
of mass every frame while tuning. On the Kodiak: hind feet 0.26 m forward, forefeet 0.16 m back, hips 0.18 m back; pitch 1.52
rad; standing 1.87 times the hump's height; worst margin 0.38. Bake a clip with stepping feet at 30 keys a second or more: the
engine interpolates between keys, not the IK, and a step's foot slides between sparse keys.

**The forelegs raised in a threat** are held before the chest at about shoulder height and out to the sides (the elbows out),
palms forward with the claws spread (the toe bones extended); held higher, the upper arm's skin crumples at the shoulder
(17 crossings on one arm on the Kodiak until the wrists came down to shoulder height).

**Check a rear frame by frame** (the Kodiak's rear QA, 2026-11-24: a script that poses every frame with the clip's own pose
function and measures each leg):
- **Blend every switch.** A paw rotation that switched from the ground's to the raised one at half the lift snapped 83
  degrees in one frame, and an elbow pole that switched at 30% flipped the elbow 54 degrees. Slerp the paw's rotation over
  the middle of the arm's travel (flat before it touches down), and blend the pole from the rest bend to the raised one.
- **Untwist the IK.** A 2-bone IK that swings each bone from rest leaves the lower bone twisted against the upper (38
  degrees at the elbow) and the paw against the lower (45 at the wrist): candy-wrapped skin. Roll the upper bone about its
  own axis to take the elbow's twist (a hinge has none), and give the lower bone half the paw's twist, as the radius turns
  over the ulna. Both fell under 10 degrees.
- **A standing foreleg is nearly straight** (99.5% of its reach on the bear), so as the chest rises the paw is dragged off
  the ground on a locked arm unless it first rolls onto its toes (heel up at most about 34 degrees, let go as the lift
  starts). Keep the claws flat while the paw is down: rolled with it, they dipped 3 cm below the ground.
- **Place the raised paw from the shoulder joint**, forward and a little out and down, so the elbow opens to 100-120
  degrees. Folded to 79 degrees, with the paw at the chest's side, the forelegs read from the front as paws without arms.
  Palms forward and a little down (the sole about 75 degrees from straight down), not up (136 read as begging).
- **Turn the shoulder blade up as the arm rises**, as a bear's does: it kept the upper arm at 0.82-0.85 of its thickness.
- **Weight the flank fold to the pelvis, not the spine above it.** The spine pitches past the pelvis as the body rises,
  and a fold weighted to it stretched 2.76 times; on the pelvis, with the thigh ring's front sharing a little of it, 1.64.
- **Measure:** each joint's interior angle and its change per frame (the worst left: about 23 degrees in a frame at the
  landing's touchdown), the twist at each joint, the paw's height and sole angle, the skin's stretch on each leg's edges
  (1.33 on the forelegs, 1.64 on the hind) and each segment's thickness against rest.


**For the dragon:** its heavy stance is this bear's: columns under the shoulders and hips, the weight on braced forelegs, the
head low and forward. Its forefeet gripping rock are the bear's forefeet on rock: plantigrade palms on the stone with the
claws hooked over its edge, so build the forefoot with two-vertex claws, give the toe bone a curl so the claws can close round
an edge, and plant it with the same IK, its sole pitched to the rock's face.

## The attack: the species' own hunting behaviour

Build the attack from how the species kills, read from its references (wildlife agencies, field guides, footage), not from
another model's clip. Write the sequence down first, with its sources, then animate it in place, starting and ending on the
stand so it repeats in melee.
- **The mountain lion (2026-11-26):** an ambush hunter that stalks as close as it can, bursts in two or three bounds, leaps
  onto the prey, holds it with the forepaws and kills with one sustained bite to the neck or the base of the skull (NPS,
  Yellowstone cougar; California Department of Fish and Wildlife). The clip: a crouch with the hind feet treading and the
  tail tip twitching, a spring that rears the forequarters about 30 degrees with the forelegs reaching high and wide, the
  grab and one clamped bite held through a wrench of the head, the drop and a recovery a leg at a time. A first version
  snapped twice and lunged with the legs in lockstep; the reviewer asked for the species' own attack.
- **Retractile claws stay sheathed.** A cat's claws are hidden at rest and on the move; modelled claws on the lion were
  removed at the reviewer's request, the paws reading as paws. Hooked claws as geometry belong to species that show them.
- **The legs move each on their own** and bend as the anatomy does (`lowpoly-animals/references/limbs.md`, "Legs that bend").
