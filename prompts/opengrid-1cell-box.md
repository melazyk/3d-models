# Prompt — openGrid 1-cell tiling box

Feed this to `/model` (or paste it as a task). Edit the numbers first if needed.

---

Design a parametric **open-top wall box for the openGrid system** as
`models/opengrid-1cell-box/model.py`, built with `build.py`. Use `lib/mounts.py`,
`lib/printer.py`, `lib/render.py`; follow `CLAUDE.md` token rules and read
`docs/design-rules.md` before dimensioning.

## Intent

A small open-top pocket that hangs on an openGrid wall board. The panel that sits
against the wall must fit **inside a single 28 mm openGrid cell**, so identical
boxes tile edge-to-edge in every direction on the grid. Depth (how far it sticks
out from the wall) is the free, usable dimension.

## Parameters (`P` dataclass, all tunables here)

| name | default | meaning |
|---|---|---|
| `cell` | `28.0` | openGrid pitch — do not change |
| `gap` | `0.8` | total clearance to neighbouring boxes (0.4 mm per side) |
| `depth` | `40.0` | protrusion from the wall = interior box depth, parametric |
| `wall` | `2.0` | side/front wall thickness |
| `floor` | `2.0` | bottom thickness |
| `corner_r` | `2.0` | vertical corner fillet |
| `lip` | `0.0` | optional inward retaining lip at the opening (0 = none) |
| `mount` | `"snap"` | `"snap"` → 1 openGrid `basic_full` snap on the back; `"slot"` → 1 Multiconnect female slot. **One model, switched by this flag.** |

## Geometry

- Against-wall panel = `(cell - gap)` square ≈ 27.2 × 27.2 mm.
- Hollow, **open on the top face** (the up side when hung); straight walls; flat
  floor at the bottom; rounded vertical corners (`corner_r`).
- Interior = panel inset by `2*wall`, depth reduced by `floor`.
- Canonical build orientation: wall face on the XY plane (z = 0), box extends +Z
  by `depth`, open top faces +Y.

## Mounting (two versions from the one model)

- `mount == "snap"`: `MOUNTS = mounts.snaps("basic_full", cols=1, rows=1)`.
  Snap (24.8 mm) sits centred in the cell with ~1 mm margin. No extra back-wall
  thickness needed — the snap is fused on behind the panel.
- `mount == "slot"`: reorient the body to the slot convention (mounting face on
  the XZ plane at y = 0), then
  `MOUNTS = mounts.slots("multiconnect", count=1, height=P.cell - P.gap)`.
  Reserve **≥ 6.5 mm** of material in the back wall for the slot (thicken just the
  back wall, keep the outer footprint at 27.2 mm). Multiconnect forces a slot
  backer ≥ 25 mm tall — 27.2 mm is fine.
  The Multiconnect slot geometry is **CC BY-NC** — put the attribution and the
  non-commercial note in the model README.

## Print

- Choose the plate orientation that needs no supports (likely back-panel-down);
  state it in the README.
- `snap` version: PLA ok; PETG if it will carry weight.

## Deliverables

1. `models/opengrid-1cell-box/model.py`
2. `models/opengrid-1cell-box/README.md` — both mount options, print orientation,
   licence note for the slot version.
3. Build **both** versions (`P.mount = "snap"` and `"slot"`), check each
   `build/.../preview.png`: footprint ≤ 28 mm, watertight, snap centred, walls
   ≥ 0.8 mm. Send both previews.
