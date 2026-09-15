"""Minimal openGrid mounting tab: just a bar with 3 snaps in a row.

Not sized to any specific part -- it's the smallest strip that comfortably
holds 3 openGrid snaps on 28 mm pitch, one cell tall. Attach whatever it
carries to the tab's front (+Z) face however needed (screws, VHB tape,
glue); this model only solves getting a small, thin mounting point onto
openGrid.

Print: mounting face down (as modeled), no supports.
Mounts to: openGrid via 3x jp4 snaps in a single horizontal row (GPL-3.0
snap geometry, see lib/connectors/README.md).
"""
from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

from lib import mounts  # noqa: F401


@dataclass
class P:
    """All tunables live here."""
    pitch: float = 28.0       # openGrid grid pitch -- do not change
    gap: float = 0.8          # margin trim, same convention as opengrid-1cell-box
    cols: int = 3
    thickness: float = 1.6    # design-rules "structural" floor for a thin panel
    fillet: float = 2.0       # outer corner rounding


def build(p: P = P()) -> cq.Workplane:
    cell = p.pitch - p.gap             # one cell's footprint, minus a trim margin
    width = (p.cols - 1) * p.pitch + cell
    height = cell

    # Convention: the wall-facing mounting face is the XY plane (z = 0,
    # facing -Z); the tab body sits in +Z. build.py fuses MOUNTS onto z=0.
    body = (
        cq.Workplane("XY")
        .box(width, height, p.thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(p.fillet)
    )
    return body


MOUNTS = mounts.snaps("jp4", cols=P.cols, rows=1)
