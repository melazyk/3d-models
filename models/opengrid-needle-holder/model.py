"""Needle / hook-tool holder for the openGrid wall board.

Print: back face down, no supports. Material: PETG.
Mounts: openGrid via 2x2 basic snaps (lockable with M16 openGrid screws).
"""
from __future__ import annotations
from dataclasses import dataclass
import cadquery as cq
from lib import mounts


@dataclass
class P:
    width: float = 70.0
    height: float = 60.0
    depth: float = 28.0
    wall: float = 2.0
    holes: int = 5
    hole_d: float = 4.5


def build(p: P = P()) -> cq.Workplane:
    # mounting face on XY (z=0, facing -Z), tray grows in +Z
    tray = (
        cq.Workplane("XY")
        .box(p.width, p.height, p.depth, centered=(True, True, False))
        .edges("|Z").fillet(4)
        .faces(">Z").shell(-p.wall)
    )
    # row of needle holes in the top face
    tray = (
        tray.faces(">Z").workplane()
        .rarray(p.width / p.holes, 1, p.holes, 1)
        .circle(p.hole_d / 2).cutThruAll()
    )
    return tray


MOUNTS = mounts.snaps("jp4", cols=2, rows=2, origin=(0, 0))
