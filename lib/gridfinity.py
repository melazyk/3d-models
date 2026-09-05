"""Parametric Gridfinity primitives (CadQuery).

Gridfinity spec is public and stable; numbers below match ../docs/design-rules.md.
Not a full clone of gridfinity-rebuilt -- just the pieces we reuse: the base
mating profile, a basic baseplate, and a simple solid/pocketed bin. The foot here
uses a single 45 chamfer instead of the exact stepped profile (0.8/1.8/2.15); it
is self-consistent (our bin mates our baseplate) and close enough to commercial
parts for most uses. If you need the exact profile, model it explicitly.

    import cadquery as cq
    from lib import gridfinity as gf

    plate = gf.base_plate(2, 1)                      # 2x1 baseplate
    bin_  = gf.solid_bin(1, 1, u=3, magnets=True)    # 1x1, 3 height-units
"""
from __future__ import annotations

import cadquery as cq

GRID = 42.0          # X/Y grid unit
HEIGHT_U = 7.0       # Z height unit for bins
FOOT = 41.5          # bin footprint per cell (42 - 0.5 clearance)
R_TOP = 4.0          # outer corner radius at top of base
CLEAR = 0.5          # total footprint clearance

_H1, _H2, _H3 = 0.8, 1.8, 2.15
BASE_H = _H1 + _H2 + _H3      # 4.75
_CHAMFER = _H1 + _H3          # 2.95, single-chamfer approximation

MAGNET_D = 6.5
MAGNET_H = 2.4
SCREW_D = 3.0
SCREW_H = 6.0
HOLE_OFFSET = 13.0   # from cell centre on each axis


def _cell_centres(nx: int, ny: int):
    for ix in range(nx):
        for iy in range(ny):
            yield (ix - (nx - 1) / 2) * GRID, (iy - (ny - 1) / 2) * GRID


def _foot(cx: float, cy: float, size: float = FOOT) -> cq.Workplane:
    """One Gridfinity foot, bottom at z=0, top of profile at z=BASE_H."""
    return (
        cq.Workplane("XY")
        .transformed(offset=(cx, cy, 0))
        .box(size, size, BASE_H, centered=(True, True, False))
        .edges("|Z").fillet(R_TOP)
        .faces("<Z").chamfer(_CHAMFER - 0.01)
    )


def _feet(nx: int, ny: int, size: float = FOOT) -> cq.Workplane:
    out = None
    for cx, cy in _cell_centres(nx, ny):
        f = _foot(cx, cy, size)
        out = f if out is None else out.union(f)
    return out


def base_plate(nx: int, ny: int, magnets: bool = False, screws: bool = False) -> cq.Workplane:
    """A basic Gridfinity baseplate (mating profile only, no weight/skeleton).
    Origin centred, sits on z=0, top face at z=BASE_H."""
    body = (
        cq.Workplane("XY")
        .box(nx * GRID, ny * GRID, BASE_H, centered=(True, True, False))
        .edges("|Z").fillet(R_TOP)
    )
    plate = body.cut(_feet(nx, ny, size=FOOT + CLEAR))
    return _add_holes(plate, nx, ny, magnets, screws)


def bin_body(nx: int, ny: int, u: int) -> cq.Workplane:
    """Outer solid of a bin: feet + a rounded box to u*HEIGHT_U total height.
    Origin centred, z=0 at the bottom of the feet."""
    total_h = u * HEIGHT_U
    body = (
        cq.Workplane("XY", origin=(0, 0, BASE_H))
        .box(nx * GRID - CLEAR, ny * GRID - CLEAR, total_h - BASE_H,
             centered=(True, True, False))
        .edges("|Z").fillet(R_TOP)
    )
    return body.union(_feet(nx, ny))


def solid_bin(nx: int, ny: int, u: int = 2, *, pocket: bool = True,
              wall: float = 1.2, floor: float = 1.4,
              magnets: bool = False, screws: bool = False) -> cq.Workplane:
    """A simple usable bin. `pocket=True` scoops a single compartment."""
    b = bin_body(nx, ny, u)
    if pocket:
        total_h = u * HEIGHT_U
        inner = (
            cq.Workplane("XY", origin=(0, 0, BASE_H + floor))
            .box(nx * GRID - CLEAR - 2 * wall, ny * GRID - CLEAR - 2 * wall,
                 total_h - BASE_H - floor + 1, centered=(True, True, False))
            .edges("|Z").fillet(max(R_TOP - wall, 0.5))
        )
        b = b.cut(inner)
    return _add_holes(b, nx, ny, magnets, screws)


def _add_holes(part, nx, ny, magnets, screws):
    if not (magnets or screws):
        return part
    for cx, cy in _cell_centres(nx, ny):
        for sx in (-1, 1):
            for sy in (-1, 1):
                px, py = cx + sx * HOLE_OFFSET, cy + sy * HOLE_OFFSET
                if magnets:
                    part = (part.faces("<Z").workplane(origin=(px, py, 0))
                            .circle(MAGNET_D / 2).cutBlind(MAGNET_H))
                if screws:
                    part = (part.faces("<Z").workplane(origin=(px, py, 0))
                            .circle(SCREW_D / 2).cutBlind(SCREW_H))
    return part
