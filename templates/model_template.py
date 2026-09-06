"""<one-line description of the part>

Print: <orientation>, <supports?>, material <PLA/PETG>.
Mounts to: <openGrid via snaps / Multiconnect slot / Gridfinity / n-a>.
"""
from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

# repo root is on sys.path when run via build.py
from lib import printer  # noqa: F401
from lib import mounts, gridfinity  # noqa: F401  (import what you use)


@dataclass
class P:
    """All tunables live here."""
    width: float = 60.0
    depth: float = 40.0
    height: float = 25.0
    wall: float = 1.6
    fillet: float = 2.0


def build(p: P = P()) -> cq.Workplane:
    # Convention: the wall-facing mounting face is the XY plane (z = 0, facing -Z);
    # build the part in +Z. build.py fuses any MOUNTS onto that face.
    body = (
        cq.Workplane("XY")
        .box(p.width, p.depth, p.height, centered=(True, True, False))
        .edges("|Z").fillet(p.fillet)
        .faces(">Z").shell(-p.wall)
    )
    return body


# --- preview (optional) -------------------------------------------------------
# build.py draws a translucent reference behind the model and cuts a section.
# Auto-inferred from MOUNTS; override here if needed:
#   PREVIEW = {"fixture": "opengrid", "cols": 2, "rows": 2, "section_axis": "x"}
#   PREVIEW = {"fixture": "gridfinity", "nx": 2, "ny": 1}


# --- how it mounts (delete if it doesn't) --------------------------------------
# Permanent: snaps click the whole accessory onto the openGrid wall.
MOUNTS = mounts.snaps("jp4", cols=2, rows=2)

# Removable instead: a Multiconnect female slot in the -Y face; print
# snap_multiconnect_full.stl separately and slide the accessory onto it.
# MOUNTS = mounts.slots("multiconnect", count=2, height=35)

# Both, or a custom grid:
# MOUNTS = mounts.combine(
#     mounts.snaps("bare_lite", cols=3, rows=1, origin=(0, 20)),
#     mounts.slots("multiconnect", count=2),
# )
