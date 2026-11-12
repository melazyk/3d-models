"""Set of thin single-wall rings (OD 4.5 / 4.4 / 4.3 / 4.2 mm), 0.4 mm wall, 6 mm tall.

Print: flat on the bed as-is (axis along Z), no supports, any material.
Wall = one 0.4 mm extrusion line; slice with 1 perimeter / "arachne" and no infill.
Mounts to: n/a (loose parts).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq


@dataclass
class P:
    """All tunables live here."""
    outer_diameters: tuple = (4.5, 4.4, 4.3, 4.2)
    wall: float = 0.4      # one nozzle line
    height: float = 6.0    # 30 layers at 0.2 mm
    spacing: float = 8.0   # centre-to-centre in X


def build(p: P = P()) -> cq.Workplane:
    n = len(p.outer_diameters)
    result = None
    for i, od in enumerate(p.outer_diameters):
        x = (i - (n - 1) / 2) * p.spacing
        ring = (
            cq.Workplane("XY").center(x, 0)
            .circle(od / 2).circle(od / 2 - p.wall)
            .extrude(p.height)
        )
        result = ring if result is None else result.add(ring)
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(
        [o for o in result.vals()])])


CHECKS = {"min_wall": False, "mounts": False}
