"""openGrid 1-cell tiling box -- small open-top wall pocket.

The wall-facing panel fits inside one 28 mm openGrid cell, so identical boxes tile
edge-to-edge in every direction. Depth (protrusion from the wall) is free.

Mounts, switched by `P.mount` (or `MOUNT=... python build.py ...`):
  "snap"        -> one openGrid basic_full snap on the back (permanent click-on)
  "multiconnect"-> a Multiconnect v2 slotted back plate fused on (QuackWorks geometry;
                   slide down onto a stud; CC BY-NC; ~14 mm channel at this size)

Print: back panel down on the plate, no supports. PLA fine; PETG if load-bearing.
Build:  python build.py models/opengrid-1cell-box
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import cadquery as cq

from lib import mounts, printer  # noqa: F401


@dataclass
class P:
    cell: float = 28.0        # openGrid pitch -- do not change
    gap: float = 0.8          # total clearance to neighbours (0.4 mm per side)
    depth: float = 40.0       # protrusion from the wall = interior box depth
    wall: float = 0.84        # side / front / floor -- exactly 2 perimeters @ 0.42
    corner_r: float = 0.8     # outer vertical corner fillet (<= wall, or corners breach)
    lip: float = 0.0          # inward retaining lip at the opening (0 = none)
    mount: str = "snap"       # "snap" | "multiconnect"


_P = P(mount=os.environ.get("MOUNT", P.mount))


def build(p: P = _P) -> cq.Workplane:
    w = p.cell - p.gap                        # against-wall panel is w x w
    back = p.wall

    # Wall face on XY (z=0), box extends +Z by depth, "up" is +Y, opening faces +Y.
    box = (
        cq.Workplane("XY")
        .box(w, w, p.depth, centered=(True, True, False))
        .edges("|Y").fillet(p.corner_r)
    )

    open_x = w - 2 * p.wall
    open_z = p.depth - back - p.wall
    cavity = (
        cq.Workplane("XY", origin=(0, -w / 2 + p.wall, back))
        .box(open_x, w, open_z, centered=(True, False, False))
    )
    box = box.cut(cavity)

    if p.lip > 0:
        rim_t = 1.6
        frame = cq.Workplane("XY", origin=(0, w / 2 - rim_t, back)).box(
            open_x, rim_t, open_z, centered=(True, False, False)
        )
        hole = cq.Workplane("XY", origin=(0, w / 2 - rim_t - 0.01, back)).box(
            open_x - 2 * p.lip, rim_t + 0.02, open_z - 2 * p.lip,
            centered=(True, False, False),
        )
        box = box.union(frame.cut(hole))

    return box


_W = _P.cell - _P.gap
MOUNTS = {
    "snap": mounts.snaps("basic_full", cols=1, rows=1),
    "multiconnect": mounts.slots("multiconnect", count=1, width=_W, height=_W),
}[_P.mount]
