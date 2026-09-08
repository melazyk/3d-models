"""Gridfinity baseplate -- `nx x ny` cells of the standard 42 mm mating profile.

The basic profile only (no weighted / skeletonised variant): a slab with the
Gridfinity foot cut from each cell, top face at z = BASE_H. Optional magnet /
screw holes for bolting it down.

Print: as modelled, flat on the plate, no supports.
Build:  python build.py models/gridfinity-baseplate
"""
from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

from lib import gridfinity as gf
from lib import printer  # noqa: F401


@dataclass
class P:
    nx: int = 3  # cells in X (42 mm each)
    ny: int = 2  # cells in Y
    magnets: bool = False  # Ø6.5 x 2.4 pockets, 13 mm off each cell centre
    screws: bool = False  # Ø3 x 6 pilot holes at the same points


P_ = P()

# The "basic" baseplate is deliberately thin at the cell mouths (that's why
# weighted baseplates exist) -- the min-wall heuristic would only cry wolf.
CHECKS = {"min_wall": False}


def build(p: P = P_) -> cq.Workplane:
    return gf.base_plate(p.nx, p.ny, magnets=p.magnets, screws=p.screws)
