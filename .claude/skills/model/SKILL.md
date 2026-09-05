---
name: model
description: Create or modify a parametric 3D-printable model in this repo (CadQuery), targeting a Bambu Lab P2S and the openGrid wall system. Use when the user asks to design, generate, model, or remix a part for 3D printing, or to add an openGrid/Multiconnect/Gridfinity mount to one.
---

# Making a 3D model in this repo

Target is fixed: **Bambu Lab P2S** (256³ mm), **openGrid** wall board (28 mm),
often **Multiconnect** / **openConnect** snaps or **Gridfinity** (42 mm).

## Token rules (do not violate)

- The model is the **CadQuery script**. Never open `*.stl` / `*.3mf` / large `*.step`.
- To judge a result: run `build.py`, then **Read the generated `preview.png`** and the
  printed metrics (bbox, volume, watertight). That's the feedback loop.
- Reusing a downloaded model: `cq.importers.importStep()` it in code and boolean —
  don't paste geometry. Connector snaps are vendored in `lib/connectors/`.

## Steps

1. **Clarify** only what changes the geometry: overall size / what it must hold,
   how it mounts (openGrid? freestanding? Gridfinity?), any hardware it mates with.
   Then proceed — don't over-ask.

2. **Read `docs/design-rules.md`** before choosing any dimension that has a fit
   (clearances, screw holes, wall thickness, grid pitches).

3. **Scaffold**: `cp templates/model_template.py models/<kebab-name>/model.py`.
   Keep every tunable in the `P` dataclass. Use `lib/`:
   - `lib/printer.py` — clearances (`CLEARANCE_NORMAL` …), `SCREWS["M3"]`, `report_fit`.
   - `lib/gridfinity.py` — `base_plate`, `bin_body`, `solid_bin`.
   - `lib/mounts.py` — set a module-level `MOUNTS`:
     `mounts.snaps("basic_full", cols=2, rows=2)` (permanent, clicks onto wall) or
     `mounts.slots("multiconnect", count=2)` (removable slot) or `mounts.combine(...)`.
     The body's mounting face must be on the XY plane (z=0, facing -Z), body in +Z.
     Connector STLs are already vendored in `lib/connectors/`. If a `MOUNTS` build
     prints "OpenSCAD not found", tell the user to run
     `bash lib/connectors/vendor/regenerate.sh` once.
     Note: `slots("multiconnect", ...)` pulls in CC-BY-NC geometry — put the
     attribution + non-commercial note in the model's README.

4. **Build & inspect**:
   ```
   python build.py models/<name>
   ```
   Read `build/<name>/preview.png`. Check: fits P2S, watertight True, no thin walls,
   sane print orientation. Iterate on `model.py`.

5. **Send** `build/<name>/preview.png` to the user with `SendUserFile`. Once they're
   happy, remind them the STL is at `build/<name>/part.stl` for slicing in Bambu Studio.

6. **Document**: add `models/<name>/README.md` — what it is, print orientation,
   supports, material, any test-print tuning. Link the source model if it's a remix.

7. **Commit** `models/<name>/` only (artifacts are gitignored). Ask before committing.

## Modifying an existing model in the repo

If it's a `.step`: import it, cut/add features parametrically, re-export.
If it's only `.stl` (mesh): re-model parametrically if feasible; otherwise say so and
propose Blender for mesh edits — don't try to edit mesh vertices in code.
