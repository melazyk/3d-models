# Gridfinity divider bin

A Gridfinity bin (`nx × ny` cells, `u` height units) with the interior split into
`div_x × div_y` equal compartments. Feet mate a standard Gridfinity baseplate;
optional magnet pockets.

Default: **2 × 1 × 3U**, 3 compartments across → 83.5 × 41.5 × 21 mm.

## Parameters

`nx` / `ny` cells (42 mm) · `u` height units (7 mm) · `div_x` / `div_y` compartments ·
`wall` 1.2 · `floor` 1.4 · `div_wall` 1.2 (internal) · `inner_fillet` 1.6 ·
`magnets` (Ø6.5 × 2.4 pockets 13 mm off each cell centre).

```
python build.py models/gridfinity-divider-bin
```

## Print

- **Orientation:** as modelled — feet down on the plate. No supports.
- **Material:** PLA is fine. Layer 0.20.
- Magnets: press 6 × 2 mm discs into the foot pockets after printing (glue optional).
- The foot here is a single-chamfer approximation of the Gridfinity profile
  (see `lib/gridfinity.py`) — mates our own baseplate; test against commercial
  baseplates before committing to a batch.

## Licence

Gridfinity spec by Zack Freedman, CC BY 4.0. Geometry is our own parametric
implementation (`lib/gridfinity.py`), not a copy of gridfinity-rebuilt.
