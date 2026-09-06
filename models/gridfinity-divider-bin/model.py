"""Gridfinity bin with a grid of compartments.

`nx x ny` Gridfinity cells, `u` height units (7 mm each). The interior is split
into `div_x x div_y` equal compartments by internal walls. Feet mate a standard
Gridfinity baseplate; optional magnet holes.

Print: as modelled (feet down) on the plate, no supports. PLA is fine.
Build:  python build.py models/gridfinity-divider-bin
"""
from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

from lib import gridfinity as gf
from lib import printer  # noqa: F401


@dataclass
class P:
    nx: int = 2  # Gridfinity cells in X (42 mm each)
    ny: int = 1  # Gridfinity cells in Y
    u: int = 3  # height units, 7 mm each (total height = u * 7)
    div_x: int = 3  # compartments across X
    div_y: int = 1  # compartments across Y
    wall: float = 1.2  # outer wall
    floor: float = 1.4  # floor above the base profile
    div_wall: float = 1.2  # internal divider wall
    inner_fillet: float = 1.6
    magnets: bool = False  # Ø6.5 x 2.4 magnet pockets in the feet


P_ = P()
PREVIEW = {"fixture": "gridfinity", "nx": P_.nx, "ny": P_.ny}


def build(p: P = P_) -> cq.Workplane:
    total_h = p.u * gf.HEIGHT_U
    body = gf.bin_body(p.nx, p.ny, p.u)

    # usable interior footprint (inside the outer wall)
    in_w = p.nx * gf.GRID - gf.CLEAR - 2 * p.wall
    in_d = p.ny * gf.GRID - gf.CLEAR - 2 * p.wall
    z0 = gf.BASE_H + p.floor
    pocket_h = total_h - z0 + 1.0  # +1 breaks through the top cleanly

    # each compartment, minus its share of the divider walls
    cell_w = (in_w - (p.div_x - 1) * p.div_wall) / p.div_x
    cell_d = (in_d - (p.div_y - 1) * p.div_wall) / p.div_y
    for ix in range(p.div_x):
        cx = -in_w / 2 + ix * (cell_w + p.div_wall) + cell_w / 2
        for iy in range(p.div_y):
            cy = -in_d / 2 + iy * (cell_d + p.div_wall) + cell_d / 2
            pocket = (
                cq.Workplane("XY", origin=(cx, cy, z0))
                .box(cell_w, cell_d, pocket_h, centered=(True, True, False))
                .edges("|Z").fillet(min(p.inner_fillet, cell_w / 2 - 0.1, cell_d / 2 - 0.1))
            )
            body = body.cut(pocket)

    if p.magnets:
        body = gf._add_holes(body, p.nx, p.ny, magnets=True, screws=False)
    return body
