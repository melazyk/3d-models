# Design rules & reference dimensions

Read before putting a number on anything that has to *fit* something.
Everything here is a starting point — tune from test prints and record what worked
in the model's own README.

## Bambu Lab P2S

| Property | Value |
|---|---|
| Build volume | 256 × 256 × 256 mm (X Y Z) |
| Usable footprint (keep margin) | ~250 × 250 mm |
| Nozzle | 0.4 mm |
| Typical layer height | 0.20 mm (0.08–0.28) |
| Extrusion width | ~0.42 mm (0.4 nozzle) |
| Enclosure | yes (good for PETG/ABS/ASA) |
| Plate | textured PEI — first layer gets a matte texture, ~0.15 mm "grip" |

Rule of thumb wall thickness: **≥ 0.8 mm** (2 perimeters), **1.2–1.6 mm** for
anything structural. Bosses/pins: ≥ 2 mm.

## FDM tolerances (PLA/PETG on a well-tuned P2S)

| Fit | Nominal gap (diametral / per-side) |
|---|---|
| Loose clearance (parts slide freely) | 0.40–0.50 mm |
| Normal clearance (assembles by hand) | 0.20–0.30 mm |
| Snug / press fit | 0.10–0.15 mm |
| Interference (hammer / heat) | 0.00 to −0.10 mm |
| Threaded rod / bolt through-hole | +0.4–0.6 mm on nominal |

Helpers in `lib/printer.py`: `CLEARANCE_LOOSE`, `CLEARANCE_NORMAL`, `CLEARANCE_SNUG`.

Holes print undersized — add ~0.1–0.2 mm to vertical holes, more to horizontal ones.
First layer elephant-foot: chamfer bottom edges 0.4–0.6 mm or add a 0.2 mm × 45° relief.

Bridging: fine up to ~30 mm. Overhangs to ~45° print clean, to ~60° acceptable with
good cooling. Design the print orientation first, geometry second.

## Fasteners

| Screw | Tap hole (into plastic) | Clearance hole | Head Ø (socket cap) | Heat-set insert hole |
|---|---|---|---|---|
| M2 | 1.7 mm | 2.4 mm | 3.8 mm | 3.2 mm |
| M3 | 2.5 mm | 3.4 mm | 5.5 mm | 4.0 mm |
| M4 | 3.3 mm | 4.5 mm | 7.0 mm | 5.6 mm |
| M5 | 4.2 mm | 5.5 mm | 8.5 mm | 6.4 mm |

Heat-set insert boss OD ≥ insert OD + 2 mm wall.

## openGrid (wall board) — 28 mm system

| Property | Value |
|---|---|
| Grid pitch | **28.0 mm** |
| Full board thickness | 6.8 mm |
| Lite board thickness | 4.0 mm (has built-in screw holes for direct wall mount) |
| Lite snap thickness | 3.4 mm |
| Multiconnect footprint on openGrid | ~20 × 20 mm, threaded center hole |

Accessories mount to openGrid via **snap connectors** that engage the 28 mm holes:
- **openConnect** — openGrid's native snap.
- **Multiconnect** — cross-compatible snap (originated on Multiboard, 25 mm), the
  most widely supported standard. Center hole is a printed thread for a bolt so the
  accessory can be locked/removed.

The exact snap engagement profile is **not published as clean numbers** and must not
be reconstructed from memory. The official shapes are already vendored as STL in
`lib/connectors/` (rendered from mitufy's CC-BY OpenSCAD libs — see that README).
Design your accessory with a **flat mating face on the XY plane** and let
`lib/mounts.py` + `build.py` fuse the snaps:

```python
MOUNTS = mounts.snaps("basic_full", cols=2, rows=2)   # permanent: clicks onto wall
MOUNTS = mounts.slots("multiconnect", count=2)         # removable: female slot
```

Snap kinds: `bare_full` / `bare_lite` (plain), `basic_full` / `basic_lite`
(+ M16 openGrid thread so a screw can lock it). `_full` = 6.8 mm board, `_lite` = 4 mm.

Official sources: https://www.opengrid.world/ ; mitufy/opengrid-projects on GitHub ;
openGrid ecosystem on MakerWorld / Printables.

## Multiconnect (standalone, Multiboard-origin) — 25 mm system

| Property | Value |
|---|---|
| Grid pitch | 25.0 mm |
| Connector | dovetail stem that slides into a channel + detent |
| Board thickness assumed by the slot backer | 6.5 mm |

`mounts.slots("multiconnect", count=N)` fuses the standard slotted **back plate**
(`multiconnectBack` from `lib/connectors/scad/multiconnectSlotDesign.scad`, **CC BY-NC**)
onto the body's z=0 face: keyhole entry at the top, channel + dimble below, 6.5 mm
thick, sits at z = -6.5..0. The mating male part is
`lib/connectors/snap_multiconnect_full.stl` — print it separately, snap it into the
openGrid board, slide the accessory **down** onto it; add `screw_multiconnect.stl`
to lock. The backer keeps ~13 mm solid above the keyhole, so a backer shorter than
~40 mm gives a short channel — for small parts that's fine, otherwise prefer snaps.

## Gridfinity — 42 mm system (spec is public and stable)

| Property | Value |
|---|---|
| Grid unit (X, Y) | 42.0 mm |
| Height unit (Z, for bins) | 7.0 mm |
| Bin footprint per cell | 41.5 mm (42 − 0.5 clearance) |
| Top corner radius | 4.0 mm (outer) |
| Base profile, bottom→top | 0.8 mm @45° out, 1.8 mm vertical, 2.15 mm @45° out (4.75 mm total) |
| Stacking lip | mirrors the base profile |
| Magnet hole | Ø 6.5 mm × 2.4 mm deep |
| Screw hole | Ø 3.0 mm × 6 mm deep |
| Magnet/screw hole centers | 13 mm from cell center on each axis (26 mm spacing) |
| Baseplate height (basic) | 4.75 mm (just the mating profile) |

Implemented in `lib/gridfinity.py` — use `base_plate(nx, ny)`, `bin_body(nx, ny, u)`,
`solid_bin(nx, ny, u, magnets=..., screws=...)`.
