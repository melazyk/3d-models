#!/usr/bin/env python3
"""Build a model: model.py -> STL + STEP + preview.png + metrics.

Usage:
    python build.py models/<name>            # a model directory
    python build.py models/<name>/model.py   # or the script directly
    python build.py models/<name> --no-png   # skip the render
    python build.py --all                    # rebuild every model (regression)
    python build.py --all --strict --no-png  # CI: fail on any problem, fast

Convention: model.py must expose either
    result = <cq.Workplane>
or
    def build() -> cq.Workplane: ...

A model directory containing a `.modelignore` file is skipped by `--all` and is
not treated as a reference example (see docs/improvement-plan.md).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import cadquery as cq  # noqa: E402

from lib import printer  # noqa: E402

MODELIGNORE = ".modelignore"


def load_model(script: Path):
    spec = importlib.util.spec_from_file_location("model", script)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["model"] = mod  # so dataclasses / typing in the model can resolve it
    spec.loader.exec_module(mod)
    if hasattr(mod, "build"):
        part = mod.build()
    elif hasattr(mod, "result"):
        part = mod.result
    else:
        raise SystemExit(f"{script}: define `result = ...` or `def build(): ...`")
    return part, getattr(mod, "MOUNTS", None), getattr(mod, "PREVIEW", None)


def iter_models(root: Path = ROOT):
    """Every `models/<name>/model.py`, minus dirs that carry a `.modelignore`."""
    for script in sorted((root / "models").glob("*/model.py")):
        if (script.parent / MODELIGNORE).exists():
            continue
        yield script


def mesh_metrics(stl_path: Path) -> dict:
    """bbox / volume / solidity of the exported STL. Keys missing on failure."""
    try:
        import numpy as np
        import trimesh

        m = trimesh.load(str(stl_path))
        ext = m.bounding_box.extents
        # manifold3d is the authority on printability; trimesh.is_watertight
        # false-alarms on unshared STL vertices.
        solid = bool(m.is_watertight)
        try:
            import manifold3d

            mm = manifold3d.Manifold(mesh=manifold3d.Mesh(
                vert_properties=np.asarray(m.vertices, dtype=np.float32),
                tri_verts=np.asarray(m.faces, dtype=np.uint32),
            ))
            solid = "NoError" in str(mm.status())
        except Exception:  # noqa: BLE001
            pass
        return {
            "ext": (float(ext[0]), float(ext[1]), float(ext[2])),
            "volume_cm3": m.volume / 1000,
            "solid": solid,
            "tris": len(m.faces),
        }
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def fmt_metrics(mm: dict) -> str:
    if "error" in mm:
        return f"  (metrics unavailable: {mm['error']})"
    e = mm["ext"]
    return (
        f"  mesh: {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm | "
        f"vol {mm['volume_cm3']:.1f} cm^3 | solid {mm['solid']} | {mm['tris']} tris"
    )


WALL_HARD_FLOOR = 0.6  # below this a wall is barely 1 perimeter -- fail under --strict


@dataclass
class BuildResult:
    name: str
    ok: bool = True
    fits_p2s: bool | None = None
    solid: bool | None = None
    had_mounts: bool = False
    mounts_applied: bool = False
    wall_min: float | None = None
    uncovered: list = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def problems(self, strict: bool) -> list[str]:
        out: list[str] = []
        if self.error:
            out.append(self.error)
        if self.fits_p2s is False:
            out.append("does not fit P2S 256^3")
        if self.solid is False:
            out.append("mesh is not solid / watertight")
        if self.uncovered:
            out.append(f"mount(s) with no body behind them: {self.uncovered}")
        if strict and self.had_mounts and not self.mounts_applied:
            out.append("MOUNTS declared but not fused (OpenSCAD missing?)")
        if strict and self.wall_min is not None and self.wall_min < WALL_HARD_FLOOR:
            out.append(f"min wall ~{self.wall_min:.2f} mm < {WALL_HARD_FLOOR} mm")
        return out


def build_target(script: Path, *, want_png: bool, tol: float,
                 verbose: bool = True) -> BuildResult:
    name = script.parent.name
    res = BuildResult(name=name)

    def log(msg: str) -> None:
        if verbose:
            print(msg)

    try:
        part, mount_spec, preview_spec = load_model(script)
    except BaseException as e:  # noqa: BLE001  (SystemExit from load_model too)
        res.ok = False
        res.error = f"load/build failed: {e}"
        log(f"[{name}] ERROR {res.error}")
        return res

    if not isinstance(part, cq.Workplane):
        part = cq.Workplane(obj=part)

    res.had_mounts = bool(mount_spec)
    out = ROOT / "build" / name
    out.mkdir(parents=True, exist_ok=True)
    stl = out / "part.stl"
    step = out / "part.step"

    try:
        cq.exporters.export(part, str(step))
    except Exception as e:  # noqa: BLE001
        res.ok = False
        res.error = f"STEP export failed: {e}"
        log(f"[{name}] ERROR {res.error}")
        return res

    res.fits_p2s = printer.fits_build_volume(part)
    log(f"[{name}]")
    log(f"  body {printer.report_fit(part)}")

    if mount_spec:
        from lib import mounts

        body_stl = out / "_body.stl"
        cq.exporters.export(part, str(body_stl), tolerance=tol, angularTolerance=0.1)
        try:
            mounts.apply(mount_spec, str(body_stl), str(stl))
            res.mounts_applied = True
            parts = []
            if mount_spec.get("add"):
                parts.append(f"+{len(mount_spec['add'])} snap(s)")
            if mount_spec.get("cut"):
                parts.append(f"-{len(mount_spec['cut'])} slot pocket(s)")
            if mount_spec.get("backers"):
                parts.append(f"+{len(mount_spec['backers'])} Multiconnect backer(s)")
            log(f"  mounts: {', '.join(parts)}")
        except RuntimeError as e:
            res.warnings.append(f"MOUNTS skipped: {e}")
            log(f"  MOUNTS skipped: {e}")
            cq.exporters.export(part, str(stl), tolerance=tol, angularTolerance=0.1)
    else:
        cq.exporters.export(part, str(stl), tolerance=tol, angularTolerance=0.1)

    mm = mesh_metrics(stl)
    res.solid = mm.get("solid")
    log(fmt_metrics(mm))
    log(f"  wrote {stl.relative_to(ROOT)}, {step.relative_to(ROOT)}")

    # design-rule checks -- run on the mount-free body so vendored snap tabs
    # (deliberately thin) don't false-alarm.
    check_stl = out / "_body.stl"
    if not check_stl.exists():
        check_stl = stl
    try:
        import trimesh

        from lib import checks

        bmesh = trimesh.load(str(check_stl))
        res.wall_min = checks.min_wall(bmesh)
        if mount_spec and res.mounts_applied:
            res.uncovered = checks.uncovered_mounts(bmesh, mount_spec)
        if res.wall_min is not None:
            thin = res.wall_min < printer.WALL_MIN
            log(f"  min wall ~{res.wall_min:.2f} mm" + ("  <- below WALL_MIN" if thin else ""))
            if thin:
                res.warnings.append(
                    f"min wall ~{res.wall_min:.2f} mm < WALL_MIN {printer.WALL_MIN}"
                )
        if res.uncovered:
            log(f"  UNCOVERED MOUNTS: {res.uncovered}")
    except Exception as e:  # noqa: BLE001
        res.warnings.append(f"checks skipped: {e}")

    if want_png:
        from lib import fixtures, render

        fixture_stl = None
        try:
            fspec = preview_spec or fixtures.infer_fixture(mount_spec, part)
            fx = fixtures.build_fixture(fspec) if fspec else None
            if fx is not None:
                fixture_stl = str(out / "_fixture.stl")
                cq.exporters.export(fx, fixture_stl, tolerance=tol, angularTolerance=0.2)
        except Exception as e:  # noqa: BLE001
            res.warnings.append(f"preview fixture skipped: {e}")

        sec_axis = (preview_spec or {}).get("section_axis", "y")
        png = out / "preview.png"
        try:
            render.render_png(str(stl), str(png), section_axis=sec_axis,
                              fixture_stl=fixture_stl)
            log(f"  wrote {png.relative_to(ROOT)}")
        except Exception as e:  # noqa: BLE001
            svg = out / "preview.svg"
            render.render_svg(part, str(svg))
            res.warnings.append(f"PNG render failed: {e}")
            log(f"  PNG render failed ({e}); wrote {svg.relative_to(ROOT)}")

    res.ok = not res.problems(strict=False)
    return res


def _build_all(strict: bool, want_png: bool, tol: float) -> int:
    scripts = list(iter_models())
    if not scripts:
        print("no models found under models/")
        return 0
    results = [build_target(s, want_png=want_png, tol=tol) for s in scripts]
    print("\n=== summary ===")
    failed = 0
    for r in results:
        probs = r.problems(strict)
        tag = "ok  " if not probs else "FAIL"
        if probs:
            failed += 1
        extra = f"  ({'; '.join(probs)})" if probs else ""
        print(f"  {tag}  {r.name}{extra}")
        for w in r.warnings:
            print(f"        warn: {w}")
    print(f"{len(results) - failed}/{len(results)} ok")
    return 1 if failed else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="model dir or model.py")
    ap.add_argument("--all", action="store_true",
                    help="rebuild every model (skips dirs with a .modelignore)")
    ap.add_argument("--strict", action="store_true",
                    help="with --all: also fail when declared MOUNTS were not fused")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--tol", type=float, default=0.05, help="STL linear tolerance")
    args = ap.parse_args()

    if args.all:
        raise SystemExit(_build_all(args.strict, not args.no_png, args.tol))

    if not args.target:
        ap.error("give a model dir/model.py, or --all")

    target = Path(args.target)
    script = target if target.suffix == ".py" else target / "model.py"
    if not script.exists():
        raise SystemExit(f"not found: {script}")

    res = build_target(script, want_png=not args.no_png, tol=args.tol)
    probs = res.problems(args.strict)
    if probs:
        print(f"\n  PROBLEMS: {'; '.join(probs)}")
    raise SystemExit(0 if res.ok and not (args.strict and probs) else 1)


if __name__ == "__main__":
    main()
