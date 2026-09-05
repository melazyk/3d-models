# 3d-models

Parametric 3D-printable models and remixes, targeting a **Bambu Lab P2S** (256³ mm)
and the **openGrid** wall system.

Every model is a small **CadQuery script** (`models/<name>/model.py`). `build.py`
turns it into `part.stl` + `part.step` + a `preview.png` and prints size / volume /
"is it a solid" metrics. Mounts (openGrid snaps, Multiconnect slots) are fused on
from real vendor geometry at build time.

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
   - iterates until it fits the P2S, is watertight, and has no thin walls,
   - writes `models/<name>/README.md` (print orientation, supports, licence).

3. **Iterate in chat**: "walls thinner", "10 mm deeper", "add a Multiconnect
   version". Claude edits `model.py` and rebuilds — it never hand-edits the STL.

4. **Print**: `build/<name>/part.stl` → Bambu Studio / OrcaSlicer.

### Option B — by hand

```bash
cp templates/model_template.py models/my-part/model.py
$EDITOR models/my-part/model.py          # geometry as code; params in the `P` dataclass
python build.py models/my-part           # -> build/my-part/{part.stl,part.step,preview.png}
python build.py models/my-part --no-png   # skip the render while iterating fast
```

`model.py` must expose `def build() -> cq.Workplane` (or `result = ...`). To add a
mount, set a module-level `MOUNTS` (see below). Open `build/<name>/preview.png`
(iso / opening / wall side / top) to check it.

### Writing the prompt — example

```md
Design a parametric <thing> as models/<name>/model.py, built with build.py.
Use lib/mounts.py and lib/printer.py; read docs/design-rules.md first.

Intent: <one paragraph — what it holds, where it lives, what's fixed vs free>.

Parameters (P dataclass): <name = default  # meaning> ...

Geometry: <orientation — mounting face on XY at z=0, body in +Z, "up" is +Y>,
<walls, floor, fillets, the opening>.

Mount: MOUNTS = mounts.snaps("basic_full", cols=1, rows=1)   # or mounts.slots(...)

Print: <orientation, supports, material>.

Deliverables: model.py, README.md, build it and show the preview.
```

---

## Mounts

Set a module-level `MOUNTS` in `model.py`. Body convention: the wall-facing face is
the **XY plane (z = 0)**, the body is in **+Z**, "up" is **+Y**.

```python
from lib import mounts

MOUNTS = mounts.snaps("basic_full", cols=2, rows=2)      # openGrid snaps (click-on)
MOUNTS = mounts.slots("multiconnect", count=2, height=45)  # Multiconnect v2 slotted backer
MOUNTS = mounts.combine(mounts.snaps(...), mounts.slots(...))
```

- `snaps(kind, cols, rows)` — `kind` = `bare_full/lite`, `basic_full/lite`
  (`basic` adds the M16 openGrid thread for a locking screw). `_full` = 6.8 mm
  board, `_lite` = 4 mm.
- `slots("multiconnect", count, width, height)` — fuses the standard Multiconnect
  slotted back plate (QuackWorks geometry). Print `lib/connectors/snap_multiconnect_full.stl`
  separately to snap into the board. **CC BY-NC** — non-commercial.

`build.py` fuses these via OpenSCAD's manifold backend. First run needs OpenSCAD:
`bash lib/connectors/vendor/regenerate.sh` (downloads it locally, no root).

Worked examples: [`models/opengrid-needle-holder/`](models/opengrid-needle-holder/)
(2×2 snaps), [`models/opengrid-1cell-box/`](models/opengrid-1cell-box/) (snap +
Multiconnect from one model, `MOUNT=multiconnect python build.py ...`).

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
| `build.py` | `model.py` → STL + STEP + preview + metrics |
| `CLAUDE.md` | how the AI workflow keeps token cost down (models as code, never read meshes) |

STL / 3MF / gcode are build artifacts and gitignored (except the vendored connector
STLs in `lib/connectors/`). `lib/connectors/vendor/` (OpenSCAD, BOSL2) is gitignored
too — recreate with its `regenerate.sh`.

## Setup

```bash
pip install -r requirements.txt                 # cadquery, trimesh, manifold3d
bash lib/connectors/vendor/regenerate.sh         # OpenSCAD + BOSL2, only if you use MOUNTS
```
