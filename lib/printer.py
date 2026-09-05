"""Bambu Lab P2S constants and FDM design-rule helpers.

Numbers mirror ../docs/design-rules.md. Tune from test prints.
"""
from __future__ import annotations

# --- Build volume -----------------------------------------------------------
BUILD_X = 256.0
BUILD_Y = 256.0
BUILD_Z = 256.0
SAFE_MARGIN = 3.0  # keep parts this far from each build-plate edge

NOZZLE = 0.4
LINE_WIDTH = 0.42
LAYER_H = 0.20

# --- Minimum feature sizes -------------------------------------------------
WALL_MIN = 0.8          # 2 perimeters
WALL_STRUCTURAL = 1.6
BOSS_MIN = 2.0

# --- Fit clearances (per side unless noted) -------------------------------
CLEARANCE_LOOSE = 0.45   # slides freely
CLEARANCE_NORMAL = 0.25  # assembles by hand
CLEARANCE_SNUG = 0.12    # press fit
ELEPHANT_FOOT_RELIEF = 0.5  # chamfer on bottom edges

# --- Fasteners: (tap, clearance, head_dia, heatset_hole) in mm ------------
SCREWS = {
    "M2": dict(tap=1.7, clear=2.4, head=3.8, heatset=3.2),
    "M3": dict(tap=2.5, clear=3.4, head=5.5, heatset=4.0),
    "M4": dict(tap=3.3, clear=4.5, head=7.0, heatset=5.6),
    "M5": dict(tap=4.2, clear=5.5, head=8.5, heatset=6.4),
}


def fits_build_volume(part, margin: float = SAFE_MARGIN) -> bool:
    """True if `part` (a cq.Workplane / Shape with a BoundingBox) fits the P2S."""
    bb = part.val().BoundingBox() if hasattr(part, "val") else part.BoundingBox()
    return (
        bb.xlen <= BUILD_X - 2 * margin
        and bb.ylen <= BUILD_Y - 2 * margin
        and bb.zlen <= BUILD_Z
    )


def report_fit(part) -> str:
    bb = part.val().BoundingBox() if hasattr(part, "val") else part.BoundingBox()
    ok = fits_build_volume(part)
    return (
        f"bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm  "
        f"({'fits' if ok else 'TOO BIG for'} P2S 256^3)"
    )
