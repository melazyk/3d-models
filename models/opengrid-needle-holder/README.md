# openGrid needle holder

A small open tray with a row of holes in the lid, for needles / hook tools / awls,
that clicks onto an openGrid wall board.

- **Model:** [model.py](model.py) — parametric (`P` dataclass: size, wall, hole count/dia).
- **Build:** `python build.py models/opengrid-needle-holder`
- **Print:** snap side up (lay the tray on its front face), no supports. PETG for
  wall-mount rigidity.
- **Mount:** 2×2 `jp4` openGrid snaps (28 mm pitch) — 4 flex tabs each, seat at any
  90° rotation. Press onto the board.
- Swap `mounts.snaps(...)` for `mounts.slots("multiconnect", ...)` in `model.py` for a
  removable Multiconnect version (then print `lib/connectors/snap_multiconnect_full.stl`).

Connector geometry: `lib/connectors/scad/jp/snap4.scad`, derived from
[jp-embedded/opengrid](https://github.com/jp-embedded/opengrid), **GPL-3.0**;
openGrid system by David D.
