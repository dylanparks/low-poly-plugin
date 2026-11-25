# Automating the low-poly pipeline: scripts, specialist agents and enforced checks

**The problem.** The skill describes a long process: references, anatomy, mesh, rig, texture, motion and checks. An agent
following it from prose can skip steps, misremember numbers or grade its own work generously. The test builds show all
three:
- the 12 m animal was built before its references were gathered;
- the fox's eye was called done while it measured 0.08 brighter than the fur;
- the cat's black lid passed every check until a person looked.

The work is also repetitive. 41 functions are copied verbatim into all four build scripts (830-1,070 lines each), and the
18 measuring tools (about 1,700 lines) are run by hand.

**The approach,** in one line: let scripts do everything that has one right answer, give each judgment-heavy stage to a
narrow agent, and let hooks refuse to move on until the scripts say the stage passed. The model writes species data and
looks at pictures; it does not hold numbers in its head or decide that a check passed.

## What Claude Code offers (from the plugins, sub-agents, hooks and skills docs)

| Feature | What it gives here |
|---|---|
| **Plugin layout** | `skills/`, `agents/`, `hooks/hooks.json`, `commands/` (skills preferred for new work), `bin/`, and scripts anywhere. Executables in `bin/` are on the Bash path while the plugin is enabled. `${CLAUDE_PLUGIN_ROOT}` resolves in hook commands and in skill, agent and command bodies, but not inside Bash-tool commands, so put the entry point in `bin/`. Don't write state under the plugin root: it changes on update. |
| **Skills** | Keep SKILL.md under 500 lines and move detail to reference files the SKILL.md names. Bundled scripts are executed, not loaded into context. `allowed-tools` can pre-approve a script. |
| **Subagents** (`agents/*.md`) | Frontmatter `name`, `description`, `tools` (an allowlist), `disallowedTools`, `model`, `skills` (preloaded into the agent), `maxTurns`, `effort` and others. The main agent delegates on the description. Plugin agents ignore their own `hooks`, `mcpServers` and `permissionMode`. |
| **Hooks** | `PreToolUse` can deny a tool call. `PostToolUse` feeds stderr back. `Stop` and `SubagentStop` with exit code 2 (or `"decision": "block"` plus a `reason`) refuse to let the agent stop, and hand it the reason. Matchers take tool names (`Edit\|Write`) or regexes. Plugin hooks merge with the user's. |

## 1. Scripts: one command-line tool, `lp`, in `bin/`

Everything measurable becomes a script that writes JSON, so a stage's result is a file, not a claim.

| Command | Does | Replaces |
|---|---|---|
| `lp init <species>` | Creates `lowpoly/<species>/` in the user's project with `spec.json` (the stages, empty tables, the reference checklist) | the hand-made header of each build script |
| `lp refs check` | Verifies the reference manifest: the skeleton in side, front and top views, the muscle, photos of each skin region, a licence and source for every file, and a flag for each missing view. Fails if a view is missing and hasn't been declared unverified | step zero of §1, today honour-system |
| `lp overlay <ref>` | The overlay in side, top or front view, flipping the reference automatically. Writes the differences of the top line, underline, widths and joints to JSON | `ref_overlay.py` plus reading the picture by eye |
| `lp build` | Builds the model from `spec.json` with the shared library below, and writes glTF 2.0 plus a viewer preview | 900-line per-species scripts |
| `lp check [--stage mesh\|rig\|texture\|motion\|all]` | Runs every measurement and compares it with `targets.json`. Writes `report.json` and `report.md`: a pass or fail line per check, with the value, the range and the source | 18 tools run by hand |
| `lp render` | Contact sheets for review: head textured (front, 3/4, side), lit view, walk sheet, region views, the eye and foot close-ups | 6 tools |

**What `lp check` measures,** per stage:

| Stage | Checks |
|---|---|
| Mesh | closed skin and winding; vertex and triangle budget for the tier; head share; ring sides; slivers (aspect over 10); creases round the eyes (over 90 degrees); the leg holes reaching past the knee; feet (splay, reach, contacts, sole at y = 0) |
| Rig | bones at the joint table; blended corners in range; junction weights |
| Texture | seam jumps; stretch; texel density; coat layers and stroke coherence; the skin type's signature; the eye stack (catchlight, rim profile, socket); the nose and muzzle; head contrast; foot paint; gloss clipping under the engine's lights |
| Motion | planted soles; lift, share of the cycle on the ground, stride; joint stretch; whether the IK runs out of reach |

**`targets.json`, one source for every number.** The measured ranges (budget tiers, coat layers, eye and lid profiles, nose,
seams, feet, walk) move out of the prose into data that the scripts read. SKILL.md and the references cite them, but the
model never has to recall a number to judge a pass.

**A shared build library, `lowpoly/`,** extracted from the four builds:

| Area | Contents |
|---|---|
| Geometry | `loft`, `ring_frame`, the torso, head and leg profiles, `bridge`, leg holes, `diamond`, the paw wedge, toe wedges, ears, the mouth with jaws and teeth, `orient`, normals |
| Rig | `wblend`, `setw`, the junction weights |
| Texture | the UV layout (two densities, the spine lift, patches), the texel rasteriser that paints every texel from its 3D point, cross-faded painters, `strokes` with a flow field, the form layer's lines, the eye-stack and nose painters, the scale, plate, chitin and wet-skin painters from `skin-types.md` |
| Motion | the IK walk generator (quadruped and biped), idle |
| Output | the glTF and viewer writers |

A species then becomes mostly data in `spec.json`: rings, bones, legs, colours, form lines, flow regions, the skin regions.
Only truly unusual parts need new code.

**The regression test for the library:** rebuilding the cat, fox and T. rex from specs must reproduce their current check
numbers within tolerance. The old scripts become the golden reference.

## 2. Specialist agents, one per stage, each with narrow tools

Each agent preloads only the references for its stage (the `skills` field), works on its own files, and ends by running
`lp check --stage <its stage>`. A separate reviewer grades the work.

| Agent | Preloads | Tools | Writes | Done when |
|---|---|---|---|---|
| `reference-gatherer` | §1, `skin-types.md` (for the skin regions) | WebSearch, web reading, Read, `lp refs` | `refs/manifest.json` | `lp refs check` passes, or the missing views are listed for the user. It asks before any download |
| `anatomy-measurer` | §1, `proportions.md` | Read, `lp overlay` | the joint and proportion tables in `spec.json` | every joint and width has a source and a value |
| `mesh-builder` | §2-§5, `feet.md`, `heads.md` | Read, Edit (`spec.json` and the species' custom code only), `lp build`, `lp check` | the geometry and rig parts of the spec | the mesh and rig checks pass |
| `texture-painter` | §7, `texture.md`, `skin-types.md` | Read, Edit (the texture part of the spec), `lp build`, `lp check`, `lp render` | colours, form lines, flow regions, skin regions | the texture checks pass, and the renders were looked at |
| `rig-animator` | §8, `locomotion.md` | Read, Edit (the motion part of the spec), `lp build`, `lp check` | the gait settings | the motion checks pass |
| `qa-reviewer` | the checklist and common failures | Read, `lp check --stage all`, `lp render`; **no Edit or Write** | `review.md`: the failed checks, plus what the pictures show that the numbers don't | always runs last, and hands the findings back |

**Why separate agents help:**
- **No skipped steps:** each agent sees only its stage's rules, so nothing gets lost in a long context.
- **Least privilege:** the tool allowlists stop, for example, the texture agent from moving joints.
- **Independent review:** the reviewer can't edit, so it can't fix things quietly or grade its own work. The cat's lid ring
  and the T. rex's lip seams were caught by looking, which is the reviewer's job.

**The orchestrator** is a skill, `/lowpoly:build-animal <species>`. It runs the stages in order, delegating each to its
agent, and does not start a stage until the previous stage's report passes. It shows the user each stage's report and
renders at the points where a person should look: after the references, after the mesh, after the texture.

## 3. Hooks that make the order and the checks unskippable

| Hook | Rule | How |
|---|---|---|
| `SubagentStop` | A stage agent can't finish while its stage's checks fail | Run `lp check --stage <the agent's stage>`. On failure, exit 2 with the failing lines as the reason, so the agent keeps working on exactly those |
| `Stop` | The main agent can't call a build done while `report.json` is missing, older than the model, or failing | the same, for `--stage all` |
| `PreToolUse` on `Edit\|Write` | The reports and `targets.json` can't be hand-edited, and nothing writes into a game folder | deny with a reason |
| `PreToolUse` on the `lp build` command | Stages run in order: no mesh before the reference check passes, no texture before the mesh check passes | read `spec.json`'s stage status; deny with the missing stage named |
| `PostToolUse` on `Edit` of `spec.json` | Fast feedback | run the quick checks (closed skin, budget) and return the failures |
| `SessionStart` | Resume where the work stopped | print the current species' stage and its last report |

Plugin agents ignore their own `hooks` field, so these hooks live in the plugin's `hooks/hooks.json` and tell the stages
apart by the subagent's name.

## 4. Context and cost

- **SKILL.md:** keep it under 500 lines: the rules and the "when to read which reference" map. It is about 600 after this
  split; the next cut is to move the body-plan table and the walk prose to references.
- **Agents:** preload only their references, so no single context carries the whole skill.
- **Scripts:** run rather than read. A check costs one command and a small report, not 1,700 lines of tool code.

## 5. Order of work

| Phase | Work | Proof it worked |
|---|---|---|
| 1 ✅ | Port the 18 tools to read glTF; put `targets.json` and `lp check` in `bin/` | `lp check` on the three current builds gives today's numbers. **Done 2026-11-21** (see below) |
| 2 | Extract the build library; write `spec.json`s for the cat, fox and T. rex | the rebuilt models match their current check numbers |
| 3 | Add the agents and the orchestrator skill | a new species (an alligator, to exercise `skin-types.md`) built end to end |
| 4 | Add the hooks | a deliberately broken eye or seam is refused at `SubagentStop` |
| 5 | Evals: `claude plugin eval` suites that ask for an animal and check the stages ran in order and the reports passed | the suite runs in CI |

**Risks:**
- **Windows:** hooks need a Python on the path; put a small launcher in `bin/` that finds one.
- **The renders:** the stand-in renderer was brighter than the engine (fixed 2026-11-23: it now shades as the viewer does). The texture stage's final colour check stays a person
  looking at the real viewer, and the orchestrator asks for it.
- **Tool ports:** porting the tools to glTF is the largest single piece of work. Phase 1 is worth doing even without the
  agents.

## Phase 1 result (2026-11-21)

- **Ported:** 19 tools (the 18 plus `foot_detail`, whose PNG reader the others share) now read glTF through
  `lib/lowpoly/gltf_io.py`. Each was run on the cat, fox and T. rex both ways, on the source viewer data and on the glTF
  export, and printed the same text and wrote byte-identical pictures. The glTF round trip itself is exact: corners,
  indices and rest pose identical, inverse binds within 1.3e-6, animation within 4.8e-7.
- **`lp check`** runs the tools that apply to the spec, judged 34 checks from `targets.json`, and takes 5-24 s a model.
  - On the cat: one fail, the narrowest paw's splay (1.3 against 1.6-2.7).
  - On the fox: one fail, the share of the walk a foot is down (0.54 against 0.58-0.92).
  - On the T. rex: no fails. Its foot is judged as `"feet": "long-toed"`, a range added for theropods, birds and drakes.
    That range rests on two measured models (the drake and the giant rat), so every check in it only warns. It warns that
    the foot has 5 tips, 17 ground contacts and 1 bone, where the drake has 4, 12 and 6. The paw ranges failed it on reach,
    contacts and tips, because they were measured on four-legged paws.
  - Warnings on all three: the stroke coherence (0.37-0.40 against 0.06-0.28) and slivers over 10.
- **What it found about the tools:** `foot_study` divides by the ankle's width, which is almost nothing on a collapsed ring
  (a splay of 37,050). `lp check` leaves such ratios out and says so.
- **Added since:** a long-toed foot type (5 checks, warnings), and a standing-balance check (`motion.balance`, from
  `stand_study.py`). It fails a T. rex whose standing clips kept the bind pose's feet (-1.28), and passes the fixed one (0.74),
  the fox (0.96), the cat (0.99) and the measured bear's idle. 40 checks in all. Later: where the hind legs are widest from the front (`limb_widths.py`: `limbs.hind_peak`,
  `limbs.hind_knee`, warnings), after the T. rex and the fox were both built with the mass at the knee. 42 checks. Later still: the measuring overlay against the builder's references (`measure_overlay.py`:
  `overlay.landmarks`, `overlay.outline`, warnings), after the agent trial. 44 checks. Since then (2026-11-22 to 23), from the bat, alicorn and housecat rounds: `mesh.loose`, `motion.crossings`, `texture.limb_detail` and `texture.limb_brightness`, `refs.views`, `refs.parts` and `refs.detail`, with the spec's `cards`, `eyes: glow`, `ref_parts` and `hero`, and flyers skipping the standing checks. 51 checks.
- **What the spec must give:** the eye's texel position (and its half-width and half-height for an almond eye). Without it
  the eye checks are skipped, never guessed. A wrong position silently measures fur, so phase 2 should derive it from
  the build.
