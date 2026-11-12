# thin-ring-set

Four loose single-wall tubes for fit/tolerance testing.

| Part | Outer Ø | Inner Ø | Wall | Height |
|---|---|---|---|---|
| 1 | 4.5 mm | 3.7 mm | 0.4 mm | 6 mm |
| 2 | 4.4 mm | 3.6 mm | 0.4 mm | 6 mm |
| 3 | 4.3 mm | 3.5 mm | 0.4 mm | 6 mm |
| 4 | 4.2 mm | 3.4 mm | 0.4 mm | 6 mm |

Overall 28.4 × 4.5 × 6 mm (spacing 8 mm, set in `P.spacing`).

## Print

- Orientation: upright as modelled (axis along Z), no supports, no mounts.
- Slicer: 1 wall loop, 0 infill, no top/bottom solid layers needed (open tube).
  Wall equals one 0.4 mm extrusion line; make sure line width is ~0.4 mm.
- Slow down (~30–50 mm/s) — tall thin walls wobble. Add a brim if they detach.
- Material: PLA/PETG.

Build: `python build.py models/thin-ring-set` → `build/thin-ring-set/part.stl`.
