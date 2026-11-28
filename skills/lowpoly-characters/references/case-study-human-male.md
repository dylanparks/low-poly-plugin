# Case study: the first player character, a median man

A human male in a shirt, trousers and boots: ANSUR II's median man (1.755 m), built in code with the plugin's half-model
builder and reviewed in the character viewer from every side, with three body types (very thin, median, bodybuilder) as
morph targets, a skin-tone and a hair-colour option, and idle, run and attack clips.

**End state:**
- **Budget.** 707 vertices, 1398 triangles, 42 bones (the tier is 720 / 1400 / 44).
- **Checks.** `lp check` passes: body median 2.3%, worst 11.8%.
- **The warnings that remain, each explained:**
  - the hair's deliberate asymmetry (mesh.mirror, mesh.sides);
  - contact in the fist and the folds (motion.crossings);
  - the skin crushed inside the knee's fold (motion.leg_stretch_max);
  - slivers, waste, a few measures past their limits (body.past).

The reviewer's findings, in the order they came, each with its cause and fix. Most are general; the section each became
is named.

| Found | Cause | Fix | Now in |
|---|---|---|---|
| A spike at the trapezius | a ring set deeper than the one below | each ring's back behind the one above | body.md |
| Hair like a circus tent, then wood planks | a cone over the top; stripes without flow | rebuilt from a reference cut; painted along a flow field | texture.md |
| Hair symmetric | mirrored with the body | an asymmetry pass after the mirror, a full-wrap chart | SKILL.md §3 |
| Hair helmet-like, edges goopy | a uniform 2-3 cm standoff; one sawtooth all round | the edge a few mm off the skin (2.5, 5 at the nape), about 1 cm on the sides, the volume on top; edges by region | texture.md |
| Features high, chin short | rings placed by eye | the thirds, the fifths, the survey's nasion-menton | head-and-face.md |
| Profile: weak chin, no lips, a deep dip | too few midline points | the profile's own points, against clinical angles | head-and-face.md |
| A band across the cheek | lower-face rows wrapped round the head | rows local to the mouth's barrel | head-and-face.md |
| A dent for the nasolabial fold | modelled | painted, lightly | head-and-face.md |
| A white halo round the brows on dark skin | masks mixed in sequence; a hair mask wider than the brow | masks by share, exactly the paint | texture.md |
| The darkest skin too light, the warmth uneven | a ramp by eye | the Monk scale's dark end, warmed smoothly | texture.md |
| Idle arms like a gunslinger's | one pose for every build | the measured relaxed posture, a blend space by build | joints-and-motion.md |
| The run's toes sliding and sinking; the ankle held level in the swing | two ground speeds; the foot not following the shin | one ground speed, swing retraction, the toe tip on the toe bone | joints-and-motion.md |
| A V-cutout behind the bent knee; the knee a second joint | skin between thigh and shin only; the bend over three rings (animal logic) | one hinge ring; calf and hamstring helpers pressing into the fold | joints-and-motion.md |
| A gap at the very thin build's armpit | the chest narrowed with the fat | the ribcage keeps its width | body.md |
| Muscular armpit crossings | the arm and torso grown past each other | the muscular widths trimmed; variants judged on their own body | body.md, joints-and-motion.md |
| The shoulder pointed from above | a diamond ring | squareness 2.2 | body.md |
| The glute's top a shelf | the pelvis ring left behind the glute | the volume spread into the pelvis | body.md |
| No chin on the muscular build | the throat grown forward | the neck grows at the back and sides; round, not squared | body.md |
| The thumb a thorn | a spike bending with the fingers | a jointed tube from the palm, bending across it | hands.md |
| The fist a hollow ring | fingers and thumb kept apart; a shallow middle joint | contact allowed; the middle joint folded for two | hands.md |
| The elbow's V | as the knee | biceps and flexor helpers | joints-and-motion.md |
| The jaw thin | the jaw tapering early; the angle shrinking on a thin build | wider to the chin's turn; the angle is bone | head-and-face.md |
| A hair lock through the nose bridge | the fringe's lock swept below the brow | the fringe stops above the brows | texture.md |
| The ear a flat flap, then fangs from the front, then stuck on | a two-point bump; the standoff low; a stalk, lit alone | a parametric cupped shell, the anatomy's standoffs, a broad root, normal transfer | head-and-face.md, texture.md |
| The face flat round the eyes | lines without soft shadows | the era's level of painted shading | head-and-face.md |
| The jaw's lower edge near level | 14 degrees | about 25 to the Frankfort line | head-and-face.md |
| A sawtooth under the jaw | a mixed strip split between two charts | one chart, lights agreeing at the seam | texture.md |
| The armpit's slit with the arms down | the shared points following the arm part way | an armpit helper | joints-and-motion.md |

**What worked as a method:**
- **Measure before changing.** The model's own vertices, the texture through its UVs, the posed and morphed mesh in a
  clip's frame. Several first guesses were wrong in ways only the numbers showed: a skin width under the ear, a sclera's
  brightness, a joint's crossing that was really contact.
- **Change the construction, not one vertex,** so the fix holds at every build and in every clip.
- **Look from every side** (front, back, above, below) and at every build, in the viewer, before calling a fix done.
- **Write each study** with its sources and its before and after.
