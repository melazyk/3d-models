"""openGrid / Multiconnect / openConnect mounting.

The connector shapes are the authors' real geometry, pre-rendered to STL in
lib/connectors/ (see that folder's README). Fusing them onto an accessory is done
by OpenSCAD's manifold backend at build time -- robust, and no need to reconstruct
snap profiles in CadQuery.

Usage in a model.py:

    import cadquery as cq
    from lib import mounts

    def build():
        body = (cq.Workplane("XY")               # mounting face on XY, body in +Z
                .box(80, 60, 15, centered=(True, True, False)))
        return body

    # permanent: snaps click the whole accessory onto the wall
    MOUNTS = mounts.snaps("jp", cols=3, rows=2)

    # or removable: a Multiconnect female slot; print snap_multiconnect_full separately
    # MOUNTS = mounts.slots("multiconnect", count=2, height=45)

`build.py` reads the module-level `MOUNTS` and applies it.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

CONN = Path(__file__).parent / "connectors"

# --- grid pitches --------------------------------------------------------
OPENGRID_PITCH = 28.0
MULTICONNECT_PITCH = 25.0

OPENGRID_FULL_T = 6.8
OPENGRID_LITE_T = 4.0

# snap kind -> (stl filename, z_offset, mirror_z)
# The two families need different placement:
#   jp-embedded  -- authored right-side-up, insert 0..3.4; drop by 3.4 so the
#                   accessory-bond face lands on z=0.  (GPL-3.0 geometry)
#   mitufy       -- authored 0..thickness; mirror in z so it goes behind z=0.
#                   (CC BY-4.0 geometry, has the printed M16 locking thread)
SNAPS = {
    # 4-way symmetric (flex tabs on all 4 sides) -- seats at any 90 deg rotation. DEFAULT.
    "jp4":        ("snap_jp4_full.stl", -3.4, 0),                   # press-in, no thread
    # jp-embedded/opengrid, 2 flex tabs
    "jp":        ("snap_jp_directional_full.stl", -3.4, 0),        # directional (vertical wall)
    "jp_sym":    ("snap_jp_symmetric_full.stl", -3.4, 0),          # symmetric, still 2-way
    "jp_thread": ("snap_jp_directional_thread_full.stl", -3.4, 0),
    # mitufy/opengrid-projects
    "bare_full":  ("snap_bare_full.stl", 0.0, 1),
    "bare_lite":  ("snap_bare_lite.stl", 0.0, 1),
    "basic_full": ("snap_basic_full.stl", 0.0, 1),                 # + M16 locking thread
    "basic_lite": ("snap_basic_lite.stl", 0.0, 1),
}
SLOT_PITCH = {
    "multiconnect": MULTICONNECT_PITCH,
    "multiboard": MULTICONNECT_PITCH,
}


# --- placement helpers --------------------------------------------------
def snap_positions(cols: int, rows: int, pitch: float = OPENGRID_PITCH,
                   origin: tuple[float, float] = (0.0, 0.0)):
    ox, oy = origin
    return [
        (ox + (ix - (cols - 1) / 2) * pitch, oy + (iy - (rows - 1) / 2) * pitch)
        for ix in range(cols)
        for iy in range(rows)
    ]


def snaps(kind: str = "jp4", *, cols: int = 2, rows: int = 2,
          pitch: float = OPENGRID_PITCH, origin: tuple[float, float] = (0.0, 0.0),
          rot: float = 0.0) -> dict:
    """A `cols` x `rows` grid of openGrid snaps fused onto the body's z=0 face,
    engaging the board behind it. `kind` in SNAPS -- default `"jp4"`: 4 flex tabs
    (one per cell side) so it seats at any 90 deg rotation. GPL-3.0 geometry
    (derived from jp-embedded/opengrid)."""
    if kind not in SNAPS:
        raise ValueError(f"unknown snap kind {kind!r}; pick from {list(SNAPS)}")
    stl, zoff, mir = SNAPS[kind]
    path = str((CONN / stl).resolve())
    return {"add": [[path, x, y, zoff, rot, mir]
                    for x, y in snap_positions(cols, rows, pitch, origin)]}


OC_NEGATIVE = "snap_oc_negative.stl"
OC_SLOT_DEPTH = 2.7   # how far the openConnect pocket cuts into the back wall


def openconnect(*, cols: int = 1, rows: int = 1, pitch: float = OPENGRID_PITCH,
                origin: tuple[float, float] = (0.0, 0.0), rot: float = 0.0) -> dict:
    """Cut a `cols` x `rows` grid of openConnect slots into the body's z=0 face.

    Same body convention as `snaps()`. Each slot is a ~21 x 22 mm pocket 2.7 mm
    deep, opening toward the wall (-Z); the back wall must be >= ~3 mm there. The
    accessory then pushes straight onto an openConnect head snapped into the board
    (`snap_openconnect_full.stl`). openConnect is openGrid's native connector
    (mitufy, **CC BY 4.0** -- commercial OK), and one slot fits a single 28 mm
    cell exactly -- the right choice for small tiling accessories."""
    path = str((CONN / OC_NEGATIVE).resolve())
    return {"cut": [[path, x, y, 0.0, rot, 0]
                    for x, y in snap_positions(cols, rows, pitch, origin)]}


def slots(kind: str = "multiconnect", *, count: int = 2, width: float | None = None,
          height: float = 40.0, center: tuple[float, float] = (0.0, 0.0),
          onramp: bool = False, y_adjust: float = 0.0) -> dict:
    """A Multiconnect slotted **back plate** fused onto the body's mounting face.

    Same body convention as `snaps()`: mounting face on the XY plane (z=0), body
    in +Z, "up" is +Y. The standard slotted backer (cschneid/MultiConnectOpenSCAD,
    6.5 mm thick) is added at z = -6.5 .. 0; its slot channel runs vertically so
    you slide the accessory down onto Multiconnect studs on the board.

    `count` slots across, standard 25 mm pitch; `width` defaults to count*pitch.
    `height` is the backer's vertical size (>= 25 mm). `onramp=True` adds tall-item
    entry chamfers. CC BY-NC geometry -- see lib/connectors/README.md."""
    pitch = SLOT_PITCH[kind]
    w = width if width is not None else count * pitch
    cx, cy = center
    return {"backers": [[cx, cy, w, max(height, 25.0), pitch,
                         1 if onramp else 0, y_adjust]]}


def combine(*specs: dict) -> dict:
    out: dict = {"add": [], "cut": [], "backers": []}
    for s in specs:
        for k in out:
            out[k].extend(s.get(k, []))
    return {k: v for k, v in out.items() if v}


# --- build-time application (called by build.py) -----------------------
def resolve_openscad() -> str | None:
    env = os.environ.get("OPENSCAD")
    if env and Path(env).exists():
        return env
    local = CONN / "vendor" / "squashfs-root" / "AppRun"
    if local.exists():
        return str(local)
    return shutil.which("openscad") or shutil.which("openscad-nightly")


def apply(spec: dict, body_stl: str, out_stl: str) -> None:
    """Run assemble.scad to fuse snaps / Multiconnect backers onto the body.
    Raises if OpenSCAD is missing."""
    osc = resolve_openscad()
    if not osc:
        raise RuntimeError(
            "OpenSCAD not found. Run `bash lib/connectors/vendor/regenerate.sh` once "
            "(downloads it), or set $OPENSCAD to an OpenSCAD >= 2025.x."
        )
    scad = CONN / "assemble.scad"
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen",
               OPENSCADPATH=f"{CONN}:{CONN / 'scad'}:{CONN / 'vendor'}")
    cmd = [
        osc, "-o", out_stl, "--export-format", "binstl", "--backend=manifold",
        "-D", f'body_file="{Path(body_stl).resolve()}"',
        "-D", f"add={_scad_lit(spec.get('add', []))}",
        "-D", f"cut={_scad_lit(spec.get('cut', []))}",
        "-D", f"backers={_scad_lit(spec.get('backers', []))}",
        str(scad),
    ]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if r.returncode != 0 or not Path(out_stl).exists():
        raise RuntimeError(f"OpenSCAD assemble failed:\n{r.stdout}\n{r.stderr}")


def _scad_lit(v) -> str:
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(_scad_lit(x) for x in v) + "]"
    if isinstance(v, bool):
        return "true" if v else "false"
    return repr(float(v))
