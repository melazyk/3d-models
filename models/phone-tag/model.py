"""Two-colour 2 mm phone-number tag with a hanging ear (one number per side).

Text is a flush inlay (P.inlay deep) on both faces, so the tag is perfectly flat:
colour 1 = plate, colour 2 = digits. The back-side number is mirrored so it reads
correctly when the tag is turned over around its vertical axis.

Print: flat on the bed (Z = thickness), no supports, PLA/PETG, 2 filaments (AMS).
Multi-colour: build.py writes build/phone-tag/part.3mf -- one object, two parts,
filament 1 (plate) / filament 2 (digits) already assigned. Open it in Bambu Studio.
Mounts to: n/a (hangs on a ring / hook through the Ø10 hole).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@dataclass
class P:
    """All tunables live here."""
    front_text: str = "+7 (915) 328-89-01"
    back_text: str = "+7 (916) 236-21-56"
    width: float = 100.0         # rectangular plate, X
    height: float = 28.0         # rectangular plate, Y
    thickness: float = 2.0       # total, Z
    corner_r: float = 4.0        # plate corner radius
    text_margin: float = 5.0     # min gap text <-> plate edge
    text_size: float = 9.0       # font cap size; auto-shrunk to fit width
    inlay: float = 0.6           # text depth per side (3 layers @ 0.2) -> 0.8 mm core
    text_bold: float = 0.15      # grow glyph strokes per side: ~1.4 -> ~1.7 mm, so
                                 # 4 x 0.42 mm lines fill a stroke with no gaps
    hole_d: float = 15.0         # hanging hole
    hole_offset: float = 20.0    # plate top edge -> hole centre
    ear_rim: float = 4.0         # ring width around the hole
    ear_base: float = 44.0       # width of the triangle where it meets the plate
    ear_fillet: float = 8.0      # smooth blend radius ear <-> plate
    plate_color: str = "#F2F2F2"  # preview / 3MF display colour, filament 1
    text_color: str = "#1A1A1A"   # filament 2


def _text(p: P, s: str, mirror: bool) -> cq.Workplane:
    def mk(size):
        return cq.Workplane("XY").text(s, size, p.inlay, fontPath=FONT,
                                      halign="center", valign="center")
    size = p.text_size
    bb = mk(size).val().BoundingBox()
    max_w, max_h = p.width - 2 * p.text_margin, p.height - 2 * p.text_margin
    k = min(1.0, max_w / bb.xlen, max_h / bb.ylen)
    t = mk(size * k)
    bb = t.val().BoundingBox()  # re-centre the actual glyph box
    t = t.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, 0))
    if p.text_bold > 0:
        # embolden: grow each glyph outline, shrink its counters (holes in 0/8/9)
        d = p.text_bold
        solids = []
        for f in t.faces("<Z").vals():
            outer = f.outerWire().offset2D(d, "arc")[0]
            inner = [w for iw in f.innerWires() for w in iw.offset2D(-d, "arc")]
            solids.append(cq.Solid.extrudeLinear(
                cq.Face.makeFromWires(outer, inner), cq.Vector(0, 0, p.inlay)))
        t = cq.Workplane("XY").add(solids).combine()
    if mirror:
        t = t.mirror("YZ")
    return t


def _ear(p: P) -> cq.Workplane:
    """Rounded triangle: arc around the hole, straight tangents down to the plate."""
    y0 = p.height / 2
    cy = y0 + p.hole_offset
    R = p.hole_d / 2 + p.ear_rim
    b = p.ear_base / 2
    # tangent point from (b, y0) to circle centre (0, cy), radius R (right side)
    dx, dy = b, y0 - cy
    d = math.hypot(dx, dy)
    a = math.atan2(dy, dx) + math.acos(R / d)
    tx, ty = R * math.cos(a), cy + R * math.sin(a)
    return (
        cq.Workplane("XY")
        .moveTo(-b, y0 - 1).lineTo(b, y0 - 1).lineTo(b, y0)
        .lineTo(tx, ty)
        .threePointArc((0, cy + R), (-tx, ty))
        .lineTo(-b, y0).close()
        .extrude(p.thickness)
    )


def parts(p: P = P()) -> tuple[cq.Workplane, cq.Workplane]:
    """(plate colour 1, text colour 2)."""
    plate = (
        cq.Workplane("XY")
        .rect(p.width, p.height).extrude(p.thickness)
        .edges("|Z").fillet(p.corner_r)
        .union(_ear(p))
    )
    # blend the two concave corners where the ear meets the plate edge
    y0 = p.height / 2
    plate = plate.edges(cq.selectors.BoxSelector(
        (-p.ear_base, y0 - 0.01, -1), (p.ear_base, y0 + 0.01, p.thickness + 1)
    )).edges("|Z").fillet(p.ear_fillet)
    hole_y = y0 + p.hole_offset
    plate = plate.cut(
        cq.Workplane("XY").center(0, hole_y).circle(p.hole_d / 2).extrude(p.thickness)
    )
    front = _text(p, p.front_text, mirror=False).translate((0, 0, p.thickness - p.inlay))
    back = _text(p, p.back_text, mirror=True)
    text = front.union(back)
    return plate.cut(text), text


def build(p: P = P()) -> cq.Workplane:
    plate, text = parts(p)
    return plate.union(text)


CHECKS = {"mounts": False}


def color_parts(p: P = P()):
    """Filament 1 = plate, filament 2 = digits (build.py -> part.3mf)."""
    plate, text = parts(p)
    return [("plate", p.plate_color, plate), ("text", p.text_color, text)]
