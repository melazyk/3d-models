# Vendored connector geometry

These are the **official openGrid / Multiconnect connector shapes**, pre-rendered
to STL so `lib/mounts.py` can fuse them onto accessories. Claude never reads the
`.stl` files (they're just build inputs), so they cost ~0 tokens.

## Files (committed)

| File | What it is | Use |
|---|---|---|
| `snap_jp4_full.stl` | **openGrid snap, 4-way** — flex tab on every cell side, seats at any 90° rotation. Press-in, 3.4 mm proud. **DEFAULT.** | `mounts.snaps("jp4", ...)` |
| `snap_jp_directional_full.stl` | jp-embedded original, 2 flex tabs, directional | `mounts.snaps("jp", ...)` |
| `snap_jp_symmetric_full.stl` | same, symmetric (horizontal board) | `mounts.snaps("jp_sym", ...)` |
| `snap_jp_directional_thread_full.stl` | jp snap + M16.5 openGrid thread | `mounts.snaps("jp_thread", ...)` — screw-lockable |
| `snap_bare_full.stl` | openGrid snap body, 6.8 mm (full board), no thread — **mitufy** profile | `mounts.snaps("bare_full", ...)` — alternative profile |
| `snap_bare_lite.stl` | same, 4 mm (Lite board) | |
| `snap_basic_full.stl` | snap body + M16 openGrid thread cut, 6.8 mm | same, but a screw can lock it to the board so it can't pop off |
| `snap_basic_lite.stl` | same, 4 mm | |
| `snap_openconnect_full.stl` | snap + openConnect head (board side) | print standalone, snap into wall; accessory gets a matching openConnect **slot** |
| `snap_multiconnect_full.stl` | snap + Multiconnect dimple head (board side) | print standalone; accessory gets a Multiconnect **slot** |
| `screw_openconnect.stl` | openConnect screw | locks an openConnect-slot accessory to its head |
| `screw_multiconnect.stl` | Multiconnect screw | locks a Multiconnect-slot accessory |

Two mounting styles (set a module-level `MOUNTS` in the model):
- **Permanent** — `mounts.snaps("jp4", cols, rows)` unions openGrid snaps onto the
  z=0 face. Simplest; the whole accessory clicks onto openGrid.
- **Removable** — `mounts.slots("multiconnect", count=N)` fuses a Multiconnect
  slotted **back plate** onto the z=0 face (keyhole up, channel + dimple down). Print
  `snap_multiconnect_full` separately, snap it into the wall, slide the accessory
  down onto it. Add `screw_multiconnect` to lock.

The slotted-backer geometry lives in `scad/multiconnectSlotDesign.scad` and is
oriented + fused by `assemble.scad` at build time.

## Regenerating

`bash lib/connectors/vendor/regenerate.sh` — downloads a pinned OpenSCAD nightly +
BOSL2 into `vendor/` (gitignored) and re-renders every STL. Source versions are
pinned at the top of that script. Needs network; needs no root.

`build.py` also needs that OpenSCAD binary whenever a model declares `MOUNTS`
(it does the union/cut). Run `regenerate.sh` once to set it up, or point
`OPENSCAD` at your own OpenSCAD ≥ 2025.x (Manifold backend).

## Sources & licences

| Source | Author | Licence |
|---|---|---|
| `scad/jp/snap.scad`, `scad/jp/snap4.scad` (the `snap_jp*` STLs) | jp-embedded/opengrid (+ 4-way derivative) | **GPL-3.0** — models using these snaps inherit GPL-3.0 |
| `scad/opengrid_*.scad`, `scad/openconnect_lib.scad` | mitufy (github.com/mitufy/opengrid-projects) | CC BY 4.0 |
| openGrid system itself | David D — printables.com/model/1214361 | CC BY 4.0 |
| `scad/multiconnectSlotDesign.scad` | AndyLevesque/QuackWorks (desc. of cschneid/MultiConnectOpenSCAD); Multiconnect by @David D | **CC BY-NC 4.0** — non-commercial |
| `scad/openconnect_plate.scad`, `scad/oc_negative.scad` | mitufy/opengrid-projects | CC BY 4.0 |
| BOSL2 (build dependency) | BelfrySCAD | BSD-2-Clause |

Licence inheritance: `mounts.snaps("jp*")` → **GPL-3.0**;
`mounts.slots("multiconnect")` → **CC BY-NC** (non-commercial). The mitufy
`bare_*`/`basic_*` snaps and the openConnect slot are CC BY (commercial OK).
Keep attribution in each model's README.
