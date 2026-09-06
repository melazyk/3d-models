# openGrid 1-cell tiling box

A small open-top pocket for an openGrid wall board. The wall-facing panel is
**27.2 × 27.2 mm** — inside a single 28 mm openGrid cell — so identical boxes
tile edge-to-edge in every direction. The default body is a **cube** (27.2 mm
each way); set `depth` for a deeper or shallower pocket. The opening faces up.

## Two versions, one model

`P.mount` (or `MOUNT=… python build.py …`):

| `mount` | attachment | notes |
|---|---|---|
| `"snap"` (default) | one **4-way** openGrid snap (`jp4`), centred on the back | flex tabs on all 4 cell sides → presses in at any 90° rotation. Engages the tile's internal groove, 3.4 mm proud. |
| `"multiconnect"` | a **Multiconnect v2** slotted back plate (6.5 mm) fused onto the back | QuackWorks slot geometry (keyhole + channel + v2 snap cutout). Print `lib/connectors/snap_multiconnect_full.stl` separately, snap it into the board, slide the box **down** onto the stud. On a 27 mm-tall box the channel is short (~14 mm — the backer keeps 13 mm solid above the keyhole); fine for light items, use the snap for anything heavy. |

```
python build.py models/opengrid-1cell-box                   # snap version
MOUNT=multiconnect python build.py models/opengrid-1cell-box # Multiconnect version
```

## Parameters

`cell` 28 (fixed) · `gap` 0.8 (clearance to neighbours) · `depth` 0 = cube (else mm) ·
`wall` **0.84** (exactly 2 perimeters at 0.42 line width — the practical minimum;
push to 0.42 for 1-perimeter/vase-thin, raise to 1.2+ for anything load-bearing) ·
`corner_r` 0.8 (keep ≤ `wall` or the outer fillet eats through the corner) ·
`lip` 0 (inward retaining rim at the opening).

## Print

- **Orientation:** lay the box on its **front face** (the closed end, opposite the
  wall) so the **snap points straight up** and prints flat — this is the clean
  orientation for the snap tabs. The open top then faces sideways; the cavity is a
  simple 3-wall channel, no supports. (Opening-up also works but prints the snap
  sideways.)
- **Material:** PLA is fine for light items; PETG if it will carry weight.
- Layer 0.20. Set the slicer to **exactly 2 wall loops** (0.84 mm wall = 2 × 0.42);
  more loops than that just get clipped. Quick print at this size.

## Multiconnect version

Backer = `multiconnectBack` from [AndyLevesque/QuackWorks](https://github.com/AndyLevesque/QuackWorks)
(`Modules/multiconnectSlotDesign.scad`), v2 profile — same geometry as the common
Multiboard customiser models. Check the "wall side" panel of the preview. Fit
tweaks in `model.py`: `mounts.slots(..., y_adjust=±1)` (vertical position),
or edit the `multiconnectBack(... slotDepthMicroadjustment=)` call in
`lib/connectors/assemble.scad` if the stud is tight/loose.

## Licence

- openGrid snap geometry (`jp4`): derived from [jp-embedded/opengrid](https://github.com/jp-embedded/opengrid)
  `snap.scad` (`lib/connectors/scad/jp/snap4.scad`), **GPL-3.0** — the snap version
  inherits GPL-3.0. openGrid system by David D.
- Multiconnect slot geometry (multiconnect version only): AndyLevesque/QuackWorks,
  **CC BY-NC 4.0** — that version is non-commercial.
- Swap `mounts.snaps("jp4")` for `mounts.snaps("basic_full")` (mitufy, CC BY-4.0) if
  GPL-3.0 is a problem — but test the fit, the profiles differ.
