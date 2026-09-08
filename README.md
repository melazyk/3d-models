# 3d-models

Parametric 3D-printable models and remixes, targeting a **Bambu Lab P2S** (256³ mm)
and the **openGrid** wall system.

Every model is a small **CadQuery script** (`models/<name>/model.py`). `build.py`
turns it into `part.stl` + `part.step` + a `preview.png`, prints size / volume /
"is it a solid" metrics, and runs a few design-rule checks. Mounts (openGrid snaps,
Multiconnect slots) are fused on from real vendor geometry at build time.
`pytest` (or `python build.py --all`) rebuilds every model at once — run it after
touching anything shared so a change can't silently break an existing part.

---

## Creating a new model

### Option A — ask Claude (recommended)

1. **Write a prompt** — a short spec of what you want. Save it in `prompts/<name>.md`.
   See [`prompts/opengrid-1cell-box.md`](prompts/opengrid-1cell-box.md) for the shape
   of a good one. Cover:
   - **What it is / holds** and the rough size, or "fits N openGrid cells".
   - **How it mounts**: `snap` (clicks onto openGrid), `multiconnect` (slide-on
     slot), Gridfinity, or nothing.
   - Any **hardware it mates with** (screw sizes, a specific bottle/tool diameter).
   - **Print constraints** you care about (no supports, wall thickness, material).
   - Leave the rest — Claude reads `docs/design-rules.md` for tolerances and the
     P2S build volume.

2. **Run the skill:** type `/model prompts/<name>.md` (or just describe the part in
   chat and say "make a model"). The `model` skill:
   - scaffolds `models/<name>/model.py` from the template,
   - keeps every tunable in a `P` dataclass,
   - builds it, looks at `build/<name>/preview.png` and the metrics,
   - iterates until the checks pass (fits the P2S, watertight, no thin walls,
     mounts land on the body),
   - writes `models/<name>/README.md` (print orientation, supports, licence),
   - runs `pytest` if it touched any shared code.

3. **Iterate in chat**: "walls thinner", "10 mm deeper", "add a Multiconnect
   version". Claude edits `model.py` and rebuilds — it never hand-edits the STL.

4. **Print**: `build/<name>/part.stl` → Bambu Studio / OrcaSlicer.

### Option B — by hand

```bash
cp templates/model_template.py models/my-part/model.py
$EDITOR models/my-part/model.py          # geometry as code; params in the `P` dataclass
python build.py models/my-part           # -> build/my-part/{part.stl,part.step,preview.png}
python build.py models/my-part --no-png   # skip the render while iterating fast
pytest                                    # if you also changed lib/ or build.py
```

`model.py` must expose `def build() -> cq.Workplane` (or `result = ...`). To add a
mount, set a module-level `MOUNTS` (see below). Open `build/<name>/preview.png`
(iso / opening / section / wall side) to check it — see
[Checking a model](#checking-a-model--regression) for what `build.py` verifies.

### Writing the prompt — example

```md
Design a parametric <thing> as models/<name>/model.py, built with build.py.
Use lib/mounts.py and lib/printer.py; read docs/design-rules.md first.

Intent: <one paragraph — what it holds, where it lives, what's fixed vs free>.

Parameters (P dataclass): <name = default  # meaning> ...

Geometry: <orientation — mounting face on XY at z=0, body in +Z, "up" is +Y>,
<walls, floor, fillets, the opening>.

Mount: MOUNTS = mounts.snaps("jp4", cols=1, rows=1)   # or mounts.slots("multiconnect", ...)

Print: <orientation, supports, material>.

Deliverables: model.py, README.md, build it and show the preview.
```

---

## Mounts

Set a module-level `MOUNTS` in `model.py`. Body convention: the wall-facing face is
the **XY plane (z = 0)**, the body is in **+Z**, "up" is **+Y**.

```python
from lib import mounts

MOUNTS = mounts.snaps("jp4", cols=2, rows=2)               # openGrid snaps (click-on)
MOUNTS = mounts.slots("multiconnect", count=2, height=45)  # Multiconnect v2 slotted backer
MOUNTS = mounts.combine(mounts.snaps(...), mounts.slots(...))
```

- `snaps(kind, cols, rows)` — `kind` = `jp4` (default): **4 flex tabs**, press-in,
  seats at any 90° rotation, **GPL-3.0**. Also `jp`/`jp_sym` (2 tabs), or the
  mitufy family `bare_full/lite`, `basic_full/lite` (CC BY-4.0) — different profile,
  test-print the fit. Print the accessory snap-side-up so the tabs print flat.
- `slots("multiconnect", count, width, height)` — fuses the standard Multiconnect
  v2 slotted back plate (QuackWorks geometry). Print `lib/connectors/snap_multiconnect_full.stl`
  separately to snap into the board. **CC BY-NC** — non-commercial.

`build.py` fuses these via OpenSCAD's manifold backend. First run needs OpenSCAD:
`bash lib/connectors/vendor/regenerate.sh` (downloads it locally, no root).

Worked examples (each has a matching `prompts/<name>.md`):
- [`models/opengrid-needle-holder/`](models/opengrid-needle-holder/) — 2×2 snaps
- [`models/opengrid-1cell-box/`](models/opengrid-1cell-box/) — snap + Multiconnect
  from one model (`MOUNT=multiconnect python build.py ...`)
- [`models/gridfinity-divider-bin/`](models/gridfinity-divider-bin/) — Gridfinity
  bin with a grid of compartments
- [`models/gridfinity-baseplate/`](models/gridfinity-baseplate/) — basic baseplate

---

## Checking a model / regression

`build.py` runs the same checks whether you build one model or all of them, and its
exit code is non-zero if anything is wrong — it drops straight into CI.

### One model

```bash
python build.py models/<name>            # build + preview + checks
python build.py models/<name> --no-png   # skip the render (faster) while iterating
python build.py models/<name> --strict   # treat warnings as failures
```

What it prints, and what fails the build:

| line in the output | meaning | fails? |
|---|---|---|
| `body bbox … (fits / TOO BIG for P2S)` | bounding box vs the 256³ volume | yes if too big |
| `mesh: … solid True/False …` | watertight / manifold (checked with `manifold3d`) | yes if `False` |
| `mounts: +N snap(s)` / `MOUNTS skipped` | were the snaps / backers fused on | `--strict` only |
| `min wall ~X mm` | roughest wall, ray-cast estimate | warns; `--strict` fails below 0.6 mm |
| `UNCOVERED MOUNTS: [(x, y)…]` | a snap / backer with no body behind it at z≈0 | **yes, always** — fix the body or the `MOUNTS` origin |

### Every model (the regression check)

```bash
python build.py --all                     # rebuild all → pass/fail summary
python build.py --all --strict --no-png    # CI: strict + fast
pytest                                     # the same, as a test suite (~2 s)
```

The committed `models/*/model.py` **are** the regression fixtures. `--all` / `pytest`
re-runs each one through your current `lib/` + `build.py`; a test goes red when a
model that used to build no longer does — build error, not watertight, doesn't fit,
lost its mount, grew a thin wall. **Run it after any change to `lib/`, `build.py`,
or `templates/`, and keep it green before committing.** It does *not* compare exact
geometry — an invariant has to actually break for it to notice.

### Excluding a model — `.modelignore`

A `models/<name>/.modelignore` file (contents are just a note for humans) takes that
model out of `--all`, `pytest`, and reference-example matching. Use it for a vendor
remix kept as downloaded geometry rather than a parametric `model.py` (e.g.
[`models/Expo-Marker-Circle-Companion/`](models/Expo-Marker-Circle-Companion/)).

### Per-model overrides in `model.py`

Two optional module-level dicts, read by `build.py`:

```python
# translucent reference ghosted behind the model in the preview, and the cut plane
PREVIEW = {"fixture": "gridfinity", "nx": 2, "ny": 1}   # or "opengrid" + cols/rows
PREVIEW = {"section_axis": "x"}                          # section plane, default "y"

# opt out of a check that genuinely doesn't apply to this part
CHECKS = {"min_wall": False}    # e.g. a basic Gridfinity baseplate is thin by design
CHECKS = {"mounts": False}      # skip the mount-coverage check
```

If a `MOUNTS` build prints `MOUNTS skipped: OpenSCAD not found`, run
`bash lib/connectors/vendor/regenerate.sh` once.

---

## Layout

| Path | What |
|---|---|
| `models/<name>/model.py` | one part, parametric (CadQuery). The only thing committed per model. |
| `models/<name>/README.md` | print orientation, supports, material, licence |
| `prompts/<name>.md` | the spec Claude built it from (optional but keep it) |
| `templates/model_template.py` | starting point for a new model |
| `lib/printer.py` | P2S constants + FDM fit clearances (`CLEARANCE_*`, `SCREWS`) |
| `lib/gridfinity.py` | Gridfinity base / baseplate / bin |
| `lib/mounts.py` | openGrid / Multiconnect mounting — `snaps()`, `slots()`, `combine()` |
| `lib/connectors/` | official snap/screw/slot geometry as STL + `vendor/regenerate.sh` |
| `docs/design-rules.md` | dimensions, tolerances, grid specs — read before dimensioning fits |
| `build.py` | `model.py` → STL + STEP + preview + metrics; `--all` rebuilds every model |
| `tests/` | `pytest` — regression: every model still builds solid / fits P2S / fuses mounts |
| `docs/improvement-plan.md` | repo backlog for the agent (regression rules, `.modelignore`, roadmap) |
| `CLAUDE.md` | how the AI workflow keeps token cost down (models as code, never read meshes) |

STL / 3MF / gcode are build artifacts and gitignored (except the vendored connector
STLs in `lib/connectors/`). `lib/connectors/vendor/` (OpenSCAD, BOSL2) is gitignored
too — recreate with its `regenerate.sh`.

## Setup

```bash
pip install -r requirements.txt                 # cadquery, trimesh, manifold3d, pytest
bash lib/connectors/vendor/regenerate.sh         # OpenSCAD + BOSL2, only if you use MOUNTS
pytest                                           # sanity-check the install: builds every model
```
