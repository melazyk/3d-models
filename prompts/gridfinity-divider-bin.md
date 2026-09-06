# Prompt — Gridfinity divider bin

Feed this to `/model`. Edit the numbers first.

---

Design a parametric **Gridfinity bin with compartments** as
`models/gridfinity-divider-bin/model.py`, built with `build.py`. Use
`lib/gridfinity.py` and `lib/printer.py`; follow `CLAUDE.md` token rules and read
`docs/design-rules.md` (Gridfinity section) before dimensioning.

## Intent

A Gridfinity bin that drops into a baseplate and holds small parts in a grid of
equal compartments. Footprint in Gridfinity cells, height in 7 mm units, number of
compartments across each axis — all parametric.

## Parameters (`P` dataclass)

| name | default | meaning |
|---|---|---|
| `nx` / `ny` | `2` / `1` | Gridfinity cells (42 mm) |
| `u` | `3` | height units (7 mm each) |
| `div_x` / `div_y` | `3` / `1` | compartments across X / Y |
| `wall` | `1.2` | outer wall |
| `floor` | `1.4` | floor above the base profile |
| `div_wall` | `1.2` | internal divider wall |
| `inner_fillet` | `1.6` | compartment corner radius |
| `magnets` | `False` | Ø6.5 × 2.4 magnet pockets in the feet |

## Geometry

- Start from `gridfinity.bin_body(nx, ny, u)` (feet + outer shell, feet at z=0).
- Interior footprint = cell grid minus `2*wall`; floor at `BASE_H + floor`.
- Cut `div_x × div_y` equal pockets separated by `div_wall`, filleted verticals,
  broken through the top.
- `magnets` → `gridfinity._add_holes(..., magnets=True)`.
- `PREVIEW = {"fixture": "gridfinity", "nx": nx, "ny": ny}` so the preview ghosts a
  baseplate under it. No `MOUNTS` (Gridfinity sits, it doesn't snap).

## Print

- Feet down, no supports. PLA, layer 0.20. State it in the README.

## Deliverables

1. `models/gridfinity-divider-bin/model.py`
2. `models/gridfinity-divider-bin/README.md` — params, print orientation, the
   note that the foot is an approximation, licence.
3. Build it; check `build/.../preview.png` (section shows dividers + floor) and
   that `pytest` stays green.
