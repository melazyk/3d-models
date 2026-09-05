#!/usr/bin/env python3
"""Build a model: model.py -> STL + STEP + preview.png + metrics.

Usage:
    python build.py models/<name>            # a model directory
    python build.py models/<name>/model.py   # or the script directly
    python build.py models/<name> --no-png   # skip the render

Convention: model.py must expose either
    result = <cq.Workplane>
or
    def build() -> cq.Workplane: ...
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import cadquery as cq  # noqa: E402

from lib import printer  # noqa: E402


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
    return part, getattr(mod, "MOUNTS", None)


def metrics(stl_path: Path) -> str:
    try:
        import numpy as np
        import trimesh

        m = trimesh.load(str(stl_path))
        ext = m.bounding_box.extents
        # manifold3d is the authority on printability; trimesh.is_watertight
        # false-alarms on unshared STL vertices.
        solid = m.is_watertight
        try:
            import manifold3d

            mm = manifold3d.Manifold(mesh=manifold3d.Mesh(
                vert_properties=np.asarray(m.vertices, dtype=np.float32),
                tri_verts=np.asarray(m.faces, dtype=np.uint32),
            ))
            solid = "NoError" in str(mm.status())
        except Exception:  # noqa: BLE001
            pass
        return (
            f"  mesh: {ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm | "
            f"vol {m.volume / 1000:.1f} cm^3 | "
            f"solid {solid} | {len(m.faces)} tris"
        )
    except Exception as e:  # noqa: BLE001
        return f"  (metrics unavailable: {e})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="model dir or model.py")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--tol", type=float, default=0.05, help="STL linear tolerance")
    args = ap.parse_args()

    target = Path(args.target)
    script = target if target.suffix == ".py" else target / "model.py"
    if not script.exists():
        raise SystemExit(f"not found: {script}")
    name = script.parent.name

    part, mount_spec = load_model(script)
    if not isinstance(part, cq.Workplane):
        part = cq.Workplane(obj=part)

    out = ROOT / "build" / name
    out.mkdir(parents=True, exist_ok=True)
    stl = out / "part.stl"
    step = out / "part.step"
    cq.exporters.export(part, str(step))

    print(f"[{name}]")
    print(f"  body {printer.report_fit(part)}")

    if mount_spec:
        from lib import mounts

        body_stl = out / "_body.stl"
        cq.exporters.export(part, str(body_stl), tolerance=args.tol, angularTolerance=0.1)
        try:
            mounts.apply(mount_spec, str(body_stl), str(stl))
            parts = []
            if mount_spec.get("add"):
                parts.append(f"+{len(mount_spec['add'])} snap(s)")
            if mount_spec.get("cut"):
                parts.append(f"-{len(mount_spec['cut'])} slot pocket(s)")
            if mount_spec.get("backers"):
                parts.append(f"+{len(mount_spec['backers'])} Multiconnect backer(s)")
            print(f"  mounts: {', '.join(parts)}")
        except RuntimeError as e:
            print(f"  MOUNTS skipped: {e}")
            cq.exporters.export(part, str(stl), tolerance=args.tol, angularTolerance=0.1)
    else:
        cq.exporters.export(part, str(stl), tolerance=args.tol, angularTolerance=0.1)

    print(metrics(stl))
    print(f"  wrote {stl.relative_to(ROOT)}, {step.relative_to(ROOT)}")

    if not args.no_png:
        from lib import render

        png = out / "preview.png"
        try:
            render.render_png(str(stl), str(png))
            print(f"  wrote {png.relative_to(ROOT)}")
        except Exception as e:  # noqa: BLE001
            svg = out / "preview.svg"
            render.render_svg(part, str(svg))
            print(f"  PNG render failed ({e}); wrote {svg.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
