"""Reference geometry for previews only -- NEVER part of a printed model.

`build.py` renders one of these translucent behind the model so you can eyeball
grid alignment / how much sticks out behind the wall. Pick it in a model with:

    PREVIEW = {"fixture": "opengrid", "cols": 2, "rows": 2}   # openGrid wall board
    PREVIEW = {"fixture": "gridfinity", "nx": 2, "ny": 1}      # Gridfinity baseplate

or leave it off -- build.py infers an openGrid board from a snap/backer MOUNTS.
"""
from __future__ import annotations

import cadquery as cq

from lib import gridfinity as gf
from lib.mounts import OPENGRID_PITCH, OPENGRID_FULL_T


def opengrid_board(cols: int = 2, rows: int = 2, thickness: float = OPENGRID_FULL_T) -> cq.Workplane:
    """A slab of openGrid board behind the mounting face: z = -thickness .. 0,
    centred on the origin, with the 28 mm cell pattern cut through it."""
    w, h = cols * OPENGRID_PITCH, rows * OPENGRID_PITCH
    board = cq.Workplane("XY", origin=(0, 0, -thickness)).box(
        w, h, thickness, centered=(True, True, False)
    )
    cell = (
        cq.Workplane("XY", origin=(0, 0, -thickness - 0.5))
        .rarray(OPENGRID_PITCH, OPENGRID_PITCH, cols, rows)
        .rect(OPENGRID_PITCH - 3.2, OPENGRID_PITCH - 3.2)
        .extrude(thickness + 1.0)
        .edges("|Z").fillet(2.0)
    )
    return board.cut(cell)


def gridfinity_baseplate(nx: int = 1, ny: int = 1) -> cq.Workplane:
    """A Gridfinity baseplate positioned so its top mating face is at z = 0
    (a bin modelled feet-at-z=0 sits straight on it)."""
    return gf.base_plate(nx, ny).translate((0, 0, -gf.BASE_H))


def build_fixture(spec: dict) -> cq.Workplane | None:
    kind = (spec or {}).get("fixture")
    if kind in ("opengrid", "opengrid-board"):
        return opengrid_board(spec.get("cols", 2), spec.get("rows", 2))
    if kind in ("gridfinity", "gridfinity-baseplate"):
        return gridfinity_baseplate(spec.get("nx", 1), spec.get("ny", 1))
    return None


def infer_fixture(mount_spec: dict | None, part=None) -> dict | None:
    """Best-guess fixture when a model didn't declare PREVIEW."""
    if not mount_spec:
        return None
    items = (mount_spec.get("add") or []) + (mount_spec.get("cut") or [])
    if items:
        # item = [path, x, y, z, rot, mir] -- size the board to span the snaps + 1 cell
        xs = [it[1] for it in items]
        ys = [it[2] for it in items]
        cols = max(1, round((max(xs) - min(xs)) / OPENGRID_PITCH) + 1)
        rows = max(1, round((max(ys) - min(ys)) / OPENGRID_PITCH) + 1)
        return {"fixture": "opengrid", "cols": cols, "rows": rows}
    if mount_spec.get("backers"):
        return {"fixture": "opengrid", "cols": 2, "rows": 2}
    return None
