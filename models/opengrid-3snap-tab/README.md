# openGrid 3-snap mounting tab

Minimal bar with 3 openGrid snaps in a row -- not sized to any specific
part. It's just the smallest strip that comfortably carries 3 snaps on the
standard 28 mm pitch, one cell tall. Whatever needs mounting attaches to
the tab's front (+Z) face separately (screws, VHB tape, glue) -- this
model only solves getting a small, thin mounting point onto openGrid.

- Tab: 83.2 x 27.2 x 1.6 mm (3 cells wide, 1 cell tall, 0.8 mm trim margin
  per side -- same convention as `opengrid-1cell-box`), 2 mm corner
  rounding.
- Mount: 3x `jp4` openGrid snaps, 28 mm pitch, press-fit into the wall
  board. GPL-3.0 snap geometry (derived from jp-embedded/opengrid) -- see
  `lib/connectors/README.md`.

All dimensions are tunable via the `P` dataclass in `model.py`
(`cols`, `thickness`, `fillet`, ...).

## Print

Mounting face down (as modeled), no supports needed, PLA is fine.

## Build

```
python build.py models/opengrid-3snap-tab
```
