# openGrid needle holder

A small open tray with a row of holes in the lid, for needles / hook tools / awls,
that clicks onto an openGrid wall board.

- **Model:** [model.py](model.py) — parametric (`P` dataclass: size, wall, hole count/dia).
- **Build:** `python build.py models/opengrid-needle-holder`
- **Print:** back face (–Z) down, no supports. PETG recommended for wall-mount rigidity.
- **Mount:** 2×2 `basic_full` openGrid snaps (28 mm pitch). Push onto the board; drop an
  M16 openGrid screw through each snap from behind if you want it locked.
- Swap `mounts.snaps(...)` for `mounts.slots("multiconnect", ...)` in `model.py` for a
  removable Multiconnect version (then print `lib/connectors/snap_multiconnect_full.stl`).

Connector geometry: openGrid snaps from [mitufy/opengrid-projects](https://github.com/mitufy/opengrid-projects)
(CC BY 4.0); openGrid system by David D.
