# Improvement plan — working file for the agent

This file is the backlog for making "generate a model in 1–2 prompts" reliable.
Work items **top to bottom**; do one item per PR/commit unless they're trivial.

## Ground rules for any change here

1. **Regression must stay green.** `pytest` rebuilds every model under `models/`
   (except dirs with a `.modelignore`) and asserts: builds without error, mesh is
   solid/watertight, fits the P2S 256³ volume, declared `MOUNTS` actually fuse,
   no mount floats free of the body. Run it before and after your change. New
   shared code that breaks an existing model is not done.
2. **Token discipline still applies** (see [../CLAUDE.md](../CLAUDE.md)). No reading
   `*.stl` / `*.3mf` / large `*.step`. Judge results from `preview.png` + metrics.
3. **`.modelignore`**: a model dir containing this file is excluded from `--all`,
   from the regression suite, and from being a reference example. Use it for vendor
   remixes that are deliberately not parametric (e.g. `Expo-Marker-Circle-Companion`).
4. When an item is finished, move its checkbox to **Done** with the commit hash.

## Backlog (priority order)

### 1. Prompt cookbook + golden examples
- **Goal:** 5–6 proven `prompts/<name>.md` → `models/<name>/` pairs covering the
  common shapes, so the `/model` skill has something to pattern-match.
- **Cover:** ~~Gridfinity bin with dividers~~; ~~Gridfinity baseplate~~; openGrid
  tray/shelf; openGrid hook; tool holder with a cavity sized to a given diameter;
  bottle/spray holder. _(2 of ~6 done — see Done.)_
- **Files:** `prompts/*.md`, `models/*/model.py`, `models/*/README.md`.
- **Acceptance:** each builds green in the regression suite; each prompt, fed cold
  to `/model`, reproduces a working model with ≤1 follow-up.

### 2. `models/INDEX.md` auto-generated gallery
- **Goal:** one table of every model (thumbnail + one-line "what it is + mount")
  so the agent finds a similar existing model to copy instead of starting cold.
- **Files:** new `tools/gen_index.py`, `models/INDEX.md`, hook into `build.py --all`.
- **Acceptance:** `python tools/gen_index.py` regenerates it; CI checks it's current.

### 3. Geometry helpers in `lib/printer.py`
- **Goal:** shrink the prompt. Add `screw_hole(part, face, "M3", "clear")`,
  `chamfer_bottom(part, ELEPHANT_FOOT_RELIEF)`, `pocket_for(diameter, fit="normal")`.
- **Files:** `lib/printer.py`, `docs/design-rules.md` (document them),
  `templates/` (use them).
- **Acceptance:** at least one golden example from item 1 uses each helper.

### 4. Variant builds without env vars
- **Goal:** replace `MOUNT=multiconnect python build.py ...` with
  `build.py <model> --variant multiconnect` → `build(variant=...)`.
- **Files:** `build.py`, `templates/model_template.py`, `models/opengrid-1cell-box/`.
- **Acceptance:** regression suite builds every declared variant of every model.

### 5. Multi-template scaffolding
- **Goal:** `templates/model_template_opengrid.py`,
  `templates/model_template_gridfinity_bin.py`, `templates/model_template_tray.py`
  instead of one generic box.
- **Files:** `templates/`, `.claude/skills/model/SKILL.md`, `README.md`.

### 6. Consolidate convention docs
- **Goal:** one canonical `docs/conventions.md` (axes, z=0 mounting face, `MOUNTS`,
  naming, licences). `CLAUDE.md`, `SKILL.md`, `README.md` link to it, don't restate.
- **Fixes existing drift:** template says `snaps("jp4")`, the 1-cell prompt says
  `basic_full`.

### 7. Decide Gridfinity fidelity
- **Goal:** either model the exact stepped foot profile + stacking lip in
  `lib/gridfinity.py`, or vendor `gridfinity-rebuilt-openscad` the way connectors
  are vendored. Until then, keep the "prototype, may not mate commercial bins"
  note prominent.
- **Files:** `lib/gridfinity.py`, `docs/design-rules.md`.

### 8. Requirements / setup hardening
- Pin versions in `requirements.txt`; add `numpy`; drop unused `numpy-stl` if the
  render path doesn't need it. Add a `make check` / `make build-all`.

## Done

- **Regression harness.** `build.py` refactored: `iter_models()`, `build_target()`
  returning a `BuildResult`, `python build.py --all [--strict] [--no-png]` with a
  pass/fail summary and non-zero exit. `tests/test_models.py` parametrizes over
  every non-ignored model. `pytest.ini` scopes collection. — _9141555_
- **`.modelignore` convention** + marker in `models/Expo-Marker-Circle-Companion/`.
  — _9141555_
- **Design-rule checks** (`lib/checks.py`): approximate min-wall (ray-cast into the
  solid, 1st percentile) and uncovered-mount detection (point-sample the body
  where each snap/backer attaches). Run on the mount-free body so vendored snap
  tabs don't false-alarm. Uncovered mount → always fails; thin wall → warning,
  `--strict` fails below `WALL_HARD_FLOOR` (0.6 mm). — _fbac0ae_
- **Preview overhaul** (`lib/render.py`, `lib/fixtures.py`): 4 labelled panels
  (iso + bbox dims, opening, mid-plane section via `vtkClipClosedSurface`, wall
  side); translucent reference fixture behind the part (openGrid board inferred
  from MOUNTS, or a model's `PREVIEW` dict for a Gridfinity baseplate / custom
  section axis). — _65f2e46_
- **Per-model `CHECKS` opt-out** (`{"min_wall": False}` / `{"mounts": False}`) via a
  module-level dict, read alongside `PREVIEW`. — _TBD_
- **Gridfinity golden examples**: `models/gridfinity-divider-bin/` (compartment
  grid) and `models/gridfinity-baseplate/` (basic baseplate), each with a
  `prompts/<name>.md`. First models to exercise `lib/gridfinity.py`. — _TBD_
