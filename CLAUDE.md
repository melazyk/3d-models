# 3d-models — working notes for Claude

Repo for **parametric** 3D-printable models and modifications of downloaded ones.

## Token discipline (most important)

- **Models are code, not meshes.** Author every new part as a CadQuery script
  (`models/<name>/model.py`). A `.step`/`.stl` is 10k–400k tokens; the script is ~100 lines.
- **Never read `*.stl`, `*.3mf`, or a large `*.step` into context.** They are build
  artifacts. To "see" a model, run `build.py` and look at the generated preview PNG,
  plus the `trimesh` metrics it prints (bbox, volume, watertight).
- When modifying a downloaded model: prefer re-modeling parametrically. If you must
  reuse vendor geometry, import the `.step` in code (`cq.importers.importStep(...)`)
  and boolean it — do not paste its contents.
- Vendor connector geometry lives in `lib/connectors/` and is loaded by path, never read.

## Target hardware — fixed

- **Printer: Bambu Lab P2S.** Build volume **256 × 256 × 256 mm**. 0.4 mm nozzle,
  enclosed CoreXY, textured PEI plate. Assume PLA/PETF unless told otherwise.
- **Wall system: openGrid** (28 mm pitch). Mounts usually attach via **Multiconnect**
  snaps or openGrid's own **openConnect** snaps.
- Also common: **Gridfinity** (42 mm pitch) bins/baseplates, and
  **Multiconnect** (25 mm pitch, Multiboard-origin) connectors.

Full numbers, clearances and FDM design rules: **`docs/design-rules.md`** (read it
before dimensioning anything with a fit).

## Libraries

- `lib/printer.py` — P2S constants + design-rule helpers (`fits_build_volume`, clearances).
- `lib/gridfinity.py` — parametric Gridfinity base / baseplate / simple bin (from spec).
- `lib/mounts.py` — openGrid / Multiconnect mounting. `mounts.snaps(kind, cols, rows)`
  and `mounts.slots(kind, count)` return a spec you assign to a module-level `MOUNTS`
  var; `build.py` fuses the real (vendored) connector geometry onto the body via
  OpenSCAD. Model convention: mounting face on the XY plane (z=0, facing -Z), body in +Z.
- `lib/connectors/` — the official openGrid/Multiconnect shapes as STL (committed) +
  `regenerate.sh` (downloads OpenSCAD, re-renders them). Models with `MOUNTS` need
  that OpenSCAD binary at build time — run `regenerate.sh` once, or set `$OPENSCAD`.
  The Multiconnect **slot** geometry is CC BY-NC — note it in any model that uses it.

## Workflow for a new part

1. `cp templates/model_template.py models/<name>/model.py`
2. Edit params + geometry. Keep all tunables in a `P` dict / dataclass at top.
3. `python build.py models/<name>` → writes `build/<name>/{part.stl,part.step,preview.png}`
   and prints metrics.
4. Look at `build/<name>/preview.png`, iterate.
5. Commit `models/<name>/model.py` (+ README if non-trivial). Artifacts are gitignored.

## Don't break existing models

- After any change to `lib/`, `build.py`, or `templates/`, run **`pytest`** (or
  `python build.py --all --no-png`). It rebuilds every model and checks solid /
  fits-P2S / mounts-fuse. Keep it green.
- A model dir with a **`.modelignore`** file is excluded from `--all`, the tests,
  and reference-example matching — it's a deliberate non-parametric vendor remix
  (e.g. `models/Expo-Marker-Circle-Companion/`). Don't pattern-match new models on it.
- Larger roadmap for this repo lives in **`docs/improvement-plan.md`** — read it
  before proposing structural changes; update its "Done" section when you land one.

## Slicing

Sliced in Bambu Studio / OrcaSlicer by the user. Design so the "natural" print
orientation needs minimal supports; call out orientation + support needs in the
model's README or a docstring.
