# Measuring: the reference set against the model

The detail behind SKILL.md §1: overlaying, measuring every view densely, filling gaps from the wider web, and
re-measuring after a change. The proportion table and its worked examples (a housecat, a T. rex) are in
`lowpoly-animals/references/proportions.md`.

## Overlay snippet (browser, no libraries)

Draw the side projection of the bind pose over a side photo. Here the photo's animal faces left and the model faces
+z; swap the sign if yours differ.
`R.nose`, `R.rumpX` and `R.ground` are pixel positions read off the photo. `pts` holds the bind-pose positions and
`tris` the triangles.

```js
const s = (R.rumpX - R.nose[0]) / (noseZ - rumpZ);          // pixels per metre
const X = z => R.nose[0] + (noseZ - z) * s, Y = y => R.ground - y * s;
g.drawImage(img, 0, 0); g.fillStyle = 'rgba(30,90,255,0.35)';
for (const t of tris) { g.beginPath(); t.forEach((i, k) => (k ? g.lineTo : g.moveTo).call(g, X(pts[i][2]), Y(pts[i][1]))); g.fill(); }
```

For the front view use `(x, y)`, and for the top view `(x, z)`, at one fixed scale.

## Locomotion sheet (same idea, for animation)

Skin the mesh at N evenly spaced phases of a clip (N = the reference sheet's frame count, often 8–12). Project each
frame onto `(z, y)` with the head to the left, and fill the triangles into a grid of panels. Draw the far-side limbs
lighter than the near-side ones (sort the triangles by `x`), and draw a ground line in each panel. Lay the sheet beside
the reference frames and compare phase by phase.

## Measuring the model against the reference set (from SKILL.md §1)

**Measure the model against the set in code, not by eye.** Overlay the bind pose on each reference in turn with the same total
length (`lib/lowpoly/tools/ref_overlay.py` draws the side, top and front views): the side view with the nose and ground aligned, the top
view with the nose and midline aligned, the front view for the ratios. **Flip each reference so the animal faces the same way
as the projection** (the bundled overlay draws the nose at the left): an unflipped photo puts the model off the image or back
to front, and the mismatch looks like a proportion error. Then list the differences of the top line and the
underline, the half-widths along the body, and the position of each joint. Fix everything off by more than about 5% of the
body's depth, width or length. After the fixes on the test animal the top line was within a few centimetres over most of the
body, the half-widths followed the top view, and the hip joint and ankle matched the reference's.

**Only then work backwards to the polygon limits** (§2, §3): put rings at the skeleton's joints and where the outline changes,
and choose what to simplify. The anatomy decides where the detail goes.

**Then the photos of that species,** for the outside: the skin, the colours, the head and the extremities, the pose.

**Photo references.** Get photos of **that species**; ask the user, or use what they gave.
- **Side views:** two or more in plain poses, because one pose can mislead. An alert animal stands tall; a walking one
  crouches.
- **Front and top views.** These are part of the reference set above, not an extra: ask for them.

### Measuring against the references: `lp overlay`

`ref_overlay.py` draws; `lp overlay <model.gltf> refs.json` measures. In the agent trial a builder called its overlay "close"
while the pincers were a club and the legs reached two thirds as far as the reference's, and the crocodile's report said its
feet agreed with the photo when, measured, they stood 10% of the body length too far forward. Corrections given as a
direction then overshot both ways. Mark each reference once, in `refs.json` beside its licence and notes:

```json
{"refs": [{"file": "refs/07_basking.jpg", "species": "Crocodylus niloticus", "view": "side", "facing": "left",
           "pose": "basking", "landmarks": {"nose": [731, 790], "tail_tip": [1873, 902], "fore_toe": [1069, 869]},
           "align": ["nose", "tail_tip"], "ground_y": 905, "outline": {"top": [[731, 785], [800, 777], [865, 779]]}}]}
```

- **Landmarks are read off the reference in pixels** (a gridded crop helps) and found on the model from the rig: `nose`,
  `head_top`, `head_back`, `jaw_low`, `back_top`, `belly`, `tail_base`, `tail_tip`, and per limb `_top` (hip or shoulder),
  `_knee`, `_ankle`, `_toe`, `_heel` (`L_hind_knee`; in a side view `hind_knee` means the side facing the camera). Name
  anything else under `"model_landmarks"`, by bone or by position.
- **Two landmarks align** the views (`align`, by default the nose and the tail tip), and `ground_y` stands the model on the
  ground row. Errors are shares of the span between the align landmarks; `px_per_m` (a scale bar) adds the real size.
  A subject tilted in the frame (a head turned, a skeleton laid at an angle) takes `"rotate": true`: the two align
  landmarks then fix the angle too, and the errors are given in the model's own directions.
  Left and right are the animal's own: in a front view its left is on the image's right, in a rear view on the image's left.
- **Outlines** are traced points: `top` and `bottom` in side, front and rear views, `left` and `right` in a top view. Each is
  compared with the model's silhouette at the same station, so the top line, the underline and the half-widths get numbers.
- **Say what each reference is:** its species (and when it stands in for the modelled one), its view and its pose. Every
  row of the table carries them, so a measurement against a relative or a walking pose is not mistaken for one against the
  animal standing. Compare like with like.
- **Heads and other small parts:** mark their own landmarks too (an eye, a beak's base, the mouth's corner, an ear's tip)
  under `"model_landmarks"`, aligned on two points of that part, so a head's proportions are measured at the head's scale.
- **Every round, not once:** keep the measured table and re-run the overlay after every round, whatever it fixed. A fix to
  one feature moves others: the test eagle's mouth corner, moved back under the eye, took the beak's base with it.
- **The report quotes the table,** and feedback gives a target from it ("the fore toe 0.39 m back, within 0.15 m"), not a
  direction. `lp check` runs it when the spec names the file (`"refs": "refs.json"`) and warns over 5%.

## Using the reference set (from SKILL.md §1)

How to use the set:
- **Each view answers different questions.** The side view gives lengths and depths. The top view gives widths along the
  body, and the tail's. The front view gives the stance, how the limbs bow, and the head's width against the body's. The
  muscle reconstructions give the bulk. The test animal's front and top views changed its ribcage, pelvis, skull, neck, tail
  and feet.
- **One drawing is one example.** It is one pose of one individual by one artist. Use two sources for a view where you can,
  and where they disagree, write the disagreement down and say which you chose (the T. rex's ribcage was 1.65 m wide in the
  top view and about 1.35 m in the front view).
- **Drawings are in perspective or are stylised.** A front view usually has the head nearer the viewer than the hips, so the
  head looks too large and the vertical scale is squashed. Take metric widths from the top view, and use the front view for
  ratios within one plane: the stance, the foot width, how the skull narrows toward the nose.
- **Record each source and its scale,** and the pose it shows, in the build script's header.
- **If a view really cannot be found** after the wider search ("Filling gaps" below) and asking the person, say so plainly, mark every number that rests on it as unverified, and keep it in the
  report. It is not a quiet gap.

## Turning the request into search subjects (from SKILL.md §1)

A request names what to build, and that is rarely what can be photographed. Nobody photographs a white unicorn, and a search
for "white horse" mostly finds paintings and statues. Before any search, translate the request into real, searchable
subjects, and write the translation down. The first alicorn was referenced as "horse" and painted white all over: a grey
horse's muzzle is dark skin under thin hair, and the build missed it (`lowpoly-animals/references/muzzles.md`).

1. **Split the request into its parts:**
   - the base animal, as a real species, and a breed or type where one fits (a riding horse of Arabian or Andalusian type,
     not "a horse");
   - the colour or coat, in that species' own words (step 2);
   - each borrowed or fantasy part, mapped to a real donor (step 3);
   - the build, age and sex, when given (a foal, a draft horse, an old male).
2. **Translate colour words into the species' real colour names.** They decide the skin, the eyes and the dark points as
   well as the hair:

   | Request says | Search for | Why |
   |---|---|---|
   | white horse, white unicorn | **grey horse** (Lipizzaner, Andalusian, Arabian greys) | almost every white horse is a grey: white hair on dark skin, dark at the nose, lips, eyes and hooves. A true white is rare and pink-skinned; say which you chose |
   | black panther | melanistic leopard or jaguar | a real colour phase with rosettes showing in raking light |
   | golden horse | palomino | a gold coat with a pale mane and tail |
   | red horse, red cat | chestnut or sorrel horse; ginger or red tabby cat | each species names its own red |
   | blue cat or dog | grey breeds: Russian Blue, Korat, Weimaraner | "blue" is grey |
   | blue point (Siamese, Ragdoll) | blue point cats of that breed | the points are a dilute, nearly neutral slate grey at about half the body's value; the body is off-white, never blue-tinted |
   | Siamese, flame point, any point colour | ask or decide the TYPE, then search both words: "modern Siamese" (show type: wedge head, big ears, tubular body) or "traditional / applehead Siamese", "colourpoint domestic shorthair" | the colour names the points; the type is the body and head. A flame point is often a sturdier domestic colourpoint, and building the show type for it was a round wasted |
   | white tiger, white lion | white Bengal tiger, white lion | real variants: photograph them, not a tinted orange one |
   | a fantasy colour (a rainbow mane, a blue dragon) | the real animal's normal colouring | reference the form and the lighting from the real animal, and treat the colour as paint on top |

3. **Map every fantasy or borrowed part to a real donor,** each referenced and checked as that animal
   (`lowpoly-animals/references/parts.md`):
   - a unicorn's horn: a narwhal's tusk for the spiral, or a markhor's horn;
   - feathered wings: a bird of the right span (a swan, an eagle);
   - membrane wings: a bat;
   - a dragon's body and skin: a crocodile or a monitor lizard;
   - a griffin: an eagle in front and a lion behind;
   - a centaur: a horse, and a human for the torso (the human part from `lowpoly-characters`).

4. **Write a search list:** every subject against every view and close-up the reference table asks for, as concrete phrases
   in the subject's real name. Add the scientific name for anatomy, and the region for close-ups. Examples: "grey horse head
   front", "grey horse muzzle", "grey Andalusian side", "Equus caballus skull lateral", "narwhal tusk", "mute swan wing
   spread". Then fill the gaps as below.
5. **Record the translation** at the top of `refs.json` and in the report, so a reviewer can see what was referenced and
   why. For example: "white unicorn: grey horse (Andalusian type) for the body, head, coat and muzzle; narwhal tusk for the
   horn; rainbow mane: a horse's mane for the form, the colour painted".

## When references disagree: which one wins

References rarely agree, and a build that averages them all pleases none. Rank them, follow the highest-ranked one that
covers the view, and record each conflict (what disagreed, by how much, which you followed) in refs.json and the report:

1. **The user's own markup** over a render of the model (red lines on a screenshot): their intent, stated directly.
2. **A reference the user names as the hard one** ("use this as a hard reference").
3. **Dead-on photos of the subject's own type** (a standing side view, a straight front).
4. **Oblique, sitting or turned photos:** heights and ratios only, not lengths along the turned axis.
5. **Illustrations, other breeds or other artists' 3D models:** a cross-check, weighted alongside the photos, never above them.
6. **Silhouettes and anything read by eye:** marked unverified.

- **A generated image the user made and cleared** may be traced, not only measured. It is still checked against the
  anatomy (joint places, stance, leg count), and the anatomy wins where it slips.
- **When a deliberate conflict moves an alignment landmark** (the user's markup pulls the forechest back 1.7 cm), an
  overlay aligned on that landmark shifts everything else: report it aligned on two landmarks the conflict doesn't move.

## Filling gaps: searching the wider web, measure-only (from SKILL.md §1)

The free sources (Wikimedia Commons, public-domain plates, free-licence photo sites) rarely hold every view the reference
table asks for. The bat of the agent trial had no muscle plate, no front or top skeleton of its species, no head-on photo
and no flight footage there; the person found a spread skeleton, a four-view skull and a drawn flight cycle elsewhere in
minutes. Gaps are searched for, not accepted.

1. **List the gaps first,** against the table in SKILL.md §1 and the parts the animal has (`lowpoly-animals/references/parts.md`): each
   view of the skeleton, the special parts (skull, hand, wing, foot), the muscle, each skin region, the head in profile and
   head-on, the rest pose, the motion. Say which free source covers each, and which nothing covers yet.
2. **Search the wider web for each gap:** museum collection databases (specimen photos, often in several views), figures in
   scientific papers (anatomy, skeletons, wing and gait diagrams), university and museum teaching pages, 3D specimen
   repositories (CT scans and surface models; check their terms), field guides and natural-history illustration, stock-photo
   previews, and frames from footage for motion. Search by the species' scientific name and by the part ("skull lateral
   dorsal", "wing skeleton", "myology", "flight sequence").
3. **Such files are measure-only.** They are used to read numbers (proportions, landmarks, bone lengths, angles, cell sizes,
   a colour sampled for comparison) and never enter the model: not traced into its geometry, not copied or projected into
   its texture, not bundled or shipped with it. They stay in the build's workspace. Record each in `refs.json` with
   `"use": "measure-only"`, the source page, what is known of its licence (often "unknown" or "all rights reserved") and
   who supplied it; `lp overlay` labels their rows.
4. **Approval as usual:** list the candidates (source, what gap each fills, the view, the species, the size) and download only
   what the person approves. Files the person supplies are logged the same way.
5. **Check the species and the view,** not the caption alone: stock and gallery sites label loosely ("bat"); confirm the
   species from the source's own record or a second source, mark a relative as a stand-in and say how close, and look at
   the image before measuring it (a skull with an insect-eater's teeth is not a fruit bat's).
6. **The fallback order** for a view nothing shows: the species' own plate or specimen; a close relative's (say how close);
   a CT scan or museum photo; a paper's figure or a reconstruction; the builder's estimate, marked unverified in the report.

## Quality over quantity: dead-on views, measured densely

One dead-on view measured at twenty stations beats ten photos read for three ratios each. The housecat's reference set had
four entries giving 5 numbers for the front and 5 for the top; the alicorn's top view had 7. Everything between those
numbers was guessed, and that is where the shapes went wrong.

**What to look for, for the whole animal and for each part the build depends on (the head, a wing, a foot):** a side, a
front (or rear) and a top view, each square to the animal: an orthographic or near-orthographic image, the animal standing
square and still, the camera far away. A 3/4 view, a close-up with perspective, a walking or posed animal, or a mounted
skeleton in a stalking pose is a second choice: say so in the entry's "pose", and use only what the pose does not change.

**Where to look, in this order:**
1. Conformation and anatomy diagrams that show several views at one scale (veterinary and breed-standard plates, artists'
   anatomy references, "<animal> front and side view diagram", "<animal> orthographic", "<animal> 3-view"), skulls and
   skeletons in the same views (museum and textbook plates). Public-domain plates on Wikimedia Commons and the
   Biodiversity Heritage Library come first.
2. Freely licensed photos taken square to the animal (Wikimedia Commons categories such as "side views of ...", "front
   views of ...", "... seen from above").
3. A general image search (Google Images and stock-photo previews). Measure-only: view them in the browser, or download
   only with the person's permission, never ship or trace them, and record the address as the entry's "source".
4. Last: 3D artists' model sheets and sculpt studies. They are someone's interpretation; mark them as such.

**One animal, one build.** Every reference describes the same breed or population and says which pose it shows. A
stand-in (another breed, a related species, a skeleton in a stalking pose) is labelled as one in its "species", and where it
disagrees with the main reference, the main reference wins. The housecat, a Siamese, was built from ordinary housecats'
photos, a crouched skeleton and ordinary-cat front and top ratios: its chest came out 0.61 of the withers height against
the Siamese's 0.55, its body 1.56 against 1.36. After a change to one proportion (the legs lengthened), re-measure the
others against the main reference: the cat's body stayed at its old height, so its longer legs bent instead.

**How to measure:** `lib/lowpoly/tools/silhouette_measure.py` reads a view's whole outline from a plain background: the top
line and underline at 16-24 stations along the body (side), the width at 16-24 heights (front, rear) or along the body
(top), all as fractions of the reference height or length, and writes a refs.json "measured" entry. Add named landmarks
(the joints, the eye, the chin) for what an outline cannot show. `lp check` refs.detail warns when the thinnest of the
side, front-or-rear and top views gives fewer than 12 measurements (fails with "hero").

## Every view needs a reference, even one you cannot download

**When a host refuses downloads** (Wikimedia's upload server answered HTTP 429 to every request for the red fox v2, even
spaced 20 s apart), open the image in a browser, scale it so the animal fills the viewport, and use the browser's saved
screenshot as the reference file: mark the landmarks in the screenshot's pixels and say so in the notes. The search and
file pages still load in the browser; fetch the file list through the site's API from the page itself.

`lp check` refs.views counts the side, front or rear, and top views that have a measurable reference, and refs.parts the
special parts named in the spec's `ref_parts` (a head, a wing). A photo that can't be downloaded (rate limits, a stock
site) still counts: read its ratios by eye and record them as a `"measured"` entry with the photo's address in `"source"`:

```json
{"view": "top", "source": "https://...", "use": "measure-only",
 "measured": {"waist_over_head_width": [0.8, 0.9], "haunch_over_head_width": [1.1, 1.2]}}
```

Shape fixes come from these numbers, never from a description of the animal (the housecat's keel chest and the alicorn's
tube head were both described, not measured).

## After a big change: every view, with its references

**In every fix round, before changing a shape:** name the reference that gives the target in the view being changed, and
review with `lp preview --refs refs.json`, whose compare.html sets each view beside its references. No reference, no
shape change: find one, or record a by-eye "measured" entry from a photo you can see, first.

**Whenever a big structural change is made to the model or one part of it** (a rebuild, new proportions, a new fold, a
reshaped head, beak, foot or wing), the QA for that round covers the part from every side, not only the view the change was
about, and against references for each of those views. The agent trial's fixes repeatedly passed in the view they were
made in and failed in another: an eagle's head rebuilt to two side photos was a flat box from the front (no front photo of
the head existed in its set); a crocodile's foot repainted and checked from above was black from the front; a wing pushed
off the body to clear it came away from the shoulder, seen only close up from above the shoulder.
1. **Gather the part's references first.** For each view the part has (side, front, top, rear; for a head, also a close-up
   of the face; for a foot, the sole), check the reference set has a usable image of that part in that view, of the species,
   in a comparable pose. A view that is missing is found and approved before the rebuild, not after (a front photo of a
   head thrown back with the beak open is not a front view of the head).
2. **Overlay it in every view that has a reference:** landmarks for the part in each (`lp overlay`, with the part's own
   landmarks under `model_landmarks`), within 5% in each, the table in the report.
3. **Look at it from every angle:** `lp preview` for the whole body, plus close-ups of the changed part from the front,
   side, rear, top and below, and of every join it touches (head with neck, wing with shoulder, foot with leg), lit as the
   viewer lights them. Say what each view shows.
4. **Then re-check what the change could have moved:** the neighbouring parts' landmarks, the folded and spread poses of
   anything that folds, and the colour where the part meets the body.
