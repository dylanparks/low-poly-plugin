# Common failures: any model

Failures that are not about one kind of model, each found in a real build, with the habits that catch them. Animal
failures (limbs, feet, heads, coats, gaits) are in `lowpoly-animals/`references/common-failures.md`.

| Failure | What it looks like | Fix |
|---|---|---|
| Built from numbers or one reference, not the full set | A clean model with the hip joint a metre off, the head half a metre too high, the neck half as deep as the muscle makes it, the ribcage a quarter too narrow, the tail too wide | The skeleton and muscle in the side, front and top views first, measured by overlay in each (§1) |
| A shape fixed from a description, not a measurement | The housecat's chest rebuilt as "a narrow keel" from memory read as a plank on stilts from the front; the alicorn's head, built with no skull or head reference, was a round tube for three rounds | Every shape change takes its target from a reference in the view being changed (a by-eye "measured" entry counts); `lp check` refs.views / refs.parts flag the missing ones, and `lp preview --refs` puts them beside the model's views |
| A painter rewritten without all its layers | A rebuilt cat face painted only in smooth gradients read as cartoonish next to its sibling build: the new head's painter had dropped the hair strokes radiating from the nose (muzzle fine detail 0.020 against 0.036) | When a part's painter is replaced, list the old one's layers (light, form, markings, strokes, grain) and carry each over; compare the part's fine detail with the previous build and a sibling (`lp check` nose.detail) |
| A part patched round after round until it drifts | Five rounds of reshaping turned a cat's head into a long, pointed, stop-less snout with stretched side eyes and spike ears: a reptile, though each round passed its checks | When a part fails at a glance after repeated patches, rebuild it from the references with fresh eyes (a builder without the drift's history), keep the rejected renders as counter-examples, and check the rebuild beside them |
| A side-projected band catches every part at its height | A rainbow band painted on the crest from the withers back also painted a flat purple shelf across the wing roots and the bridge between them, since the pelt is projected from the side | Start such a band where nothing else stands at that height, or paint the other parts (a bridge, a root) in their own patch from each face's 3D point |
| Crossings counted on the main skin only | A separate piece (a resting wing shell, a swapped part) crosses the body 124-140 times through a swap while `lp check` motion.crossings reads 16, because it counts only the main skin | `lp check` motion.pieces now counts the separate pieces' crossings, leaving out the ones present in the bind pose or in every frame (a tooth in the gum, a shell's root sunk into the shoulder); report it beside motion.crossings, and check a swap densely (`lp self_cross model 96 clip`) |
| A pose snaps where a clip switches mode | A paw's rotation switched from the ground's to the raised one at half the lift (83 degrees in one frame), an elbow's pole switched (54), the toes switched from flat to following the paw at a gallop's lift-off (43 degrees, the claws 5 cm into the ground) | Blend every switch over a stretch of the motion (slerp the rotation, blend the pole); measure each joint's change per frame and the paw's rotation per frame through the clip |
| Skin through the ground | A tail sank 5.5 cm through the ground in the idle and walk, a swan's webs 3.3 cm in the swing, a bear's claws 5 cm at lift-off, and every other check passed (the balance counts only the feet as contact) | `lp check` motion.below_ground (every clip, every frame); lift a swinging foot by its hanging toes' drop; carry a tail off the ground |
| A clip resets what another layer set | A walk set the root's position afresh each frame and threw away the stance's shift over the feet (3.5 cm) | Add to the pose, don't assign: `loc = loc + bob`, not `loc = rest + bob` |
| Colours judged under the wrong lighting | Coats tuned until they looked right in a preview that lit up-facing surfaces about 2.8x brighter than the viewer: the giant bat's coat darkened flat, the housecat's cream turned beige | Judge colours in renders shaded the viewer's way (`lp preview` and lit_view.py now shade as the viewer does: sRGB, Lambert, 1/pi), and confirm in the viewer itself |
| A part checked only in the view its fix was about | It passes where it was fixed and fails from another side: a head right in profile and a box from the front, a foot repainted from above and black from the front | After any big change, the part's references and overlays in every view, and close-ups from every side and of its joins (`lowpoly-animals/references/proportions.md`, "After a big change") |
| Proportions drifting through fix rounds | Each round fixes one feature and moves something else (the mouth's corner moved the beak's base); after a few rounds the part no longer matches its reference | Keep the measured table; re-run the overlay after every round, not only after proportion changes (`lowpoly-animals/references/proportions.md`) |
| The reference animal's shape or motion copied | Technically clean, but the wrong animal: a cat with a deer's sagging back, shallow chest, hoof feet and high-stepping walk | Photos of the species, ranges across a group (§1, lowpoly-animals §7) |
| A thin part built as its own piece near the joint, not grown from it | A finger or thumb floating a few millimetres off the wrist, a crack between a wing membrane and its finger; invisible in a full-body preview, obvious when the camera gets close | Grow it from the joint's ring (§3); `lp check` mesh.loose measures how far loose pieces stand off the skin; look at every join close up |
| A wing or limb that passes through itself or the body in motion | Folded membrane panels and finger rods cutting through each other and the arm, a leg through a pincer, folded wing layers through the back; often only from below or behind | `lp check` motion.crossings counts the triangles crossing each other in the worst frame of every clip and names the bones (`lib/lowpoly/tools/self_cross.py` runs it alone); a clearance against the body alone misses a wing cutting through itself. Look from below and behind |
| Primitive parts: capsules, spheres, even-sided round tubes | A toy; pipes that waste vertices | Few-sided boxy rings, one skin (§3) |
| Uniform ring spacing | Budget spent on straight segments; blunt joints and face; a starved head | Rings at outline changes; measure the head share (§2, §3) |
| Flat colours with noise | Unlit plastic | Painted light, anatomy and strokes (§5) |
| A thin strip joined to a tall ring | A bright or dark diagonal line across a surface: a sliver triangle taking the light on its own | An ordinary profile on the rings before the strip starts; check the thinnest triangles (lowpoly-animals §5) |
| Pale colours on upward-facing surfaces | A bright line along a lip rim or a ridge, white blobs, a glowing tongue | Dark colours under about 0.35 there, and a lit render to check (lowpoly-animals §5, §5) |
| A patch's base colour sampled at one coordinate | Streaks or a flat band beside the patch | Sample at the true position (§5) |
| Hard switches in the paint code; unmatched patches | Seams and staircases on the model | Cross-faded painters, patches fading to the pelt (`lowpoly-animals/references/texture.md`, "Continuity") |
| Only the pair where a fault was seen mirrored | A long triangle or a smeared texture on one side of another pair (the arms, after the legs were fixed) | Check every mirrored pair and their joins in code after each topology change (`lowpoly-animals/references/limbs.md`, "Both sides alike") |
| A size taken from another individual (a track, a specimen) | A foot or skull a fifth too big for the body | Ratios from the source, sizes from the reference the model is matched to (§1) |
| A shared texture strip or paint changed for one part | Another part that uses it changes colour (hands darkened with the feet) | A row per skin colour; re-check every part that shares it |

## Habits that catch these failures

Each of these, done every time, would have caught one or more of the failures above before the person reviewing the
model did:

- **Anatomy first, construction second.** Study a reference model in code to learn how a part is built (welded or separate,
  weighted how, mapped where), then apply that to the species' own anatomy. Applying the construction to a guessed shape
  gave clean geometry that read as the wrong part.
- **Measure at the model's own scale.** A track, a specimen or a paper describes another individual: use its ratios, and
  take sizes from the reference the model is matched to. Measure the same thing on the model and on that reference, in
  code, before and after the change.
- **Look from every side, including below and behind.**
  - **Below:** the footprint and the groin.
  - **Above and behind:** the jaw's corner and the throat.
  - **From the front:** the mouth's front, the chest between the arms and the snout's caps.
- **A shared thing is changed for everyone.** A mirrored region, a texture strip or a paint function serves several parts.
  After changing it for one, re-check every part that uses it: the legs were mirrored but not the arms, and the feet's paint
  darkened the hands.
- **Re-check what moved with the change.** Geometry changes move painted features (the eye's texel moved twice) and the
  triangles a check measures; run the full check after every change, not only the measure you aimed at.
- **Look at the result in the real viewer, with fresh files.** A viewer may cache textures by name: reload the texture with
  the model, or the old one shows on the new geometry.
- **Find the cause in code before a third try.** If two fixes for a visible fault don't remove it, list the faces, vertices
  or texels involved (their part, patch and position) before changing anything else.
- **A build writes only its declared outputs.** A build script that also wrote a debug file into the project's root left a
  stray file there each time it ran; debug output goes beside the build's own files, or only behind a flag.
- **Keep a copy before each change,** and compare before and after on the same views and the same numbers.
