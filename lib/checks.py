"""Cheap printability / mount checks run by build.py.

All approximate -- a safety net, not a slicer. `min_wall` ray-casts from the
surface into the solid; `uncovered_mounts` point-samples the body where each
snap / backer attaches. Both take a trimesh mesh.
"""
from __future__ import annotations


def min_wall(mesh, samples: int = 800) -> float | None:
    """~1st-percentile local thickness in mm (distance from each surface sample,
    along -normal, to the opposite wall). None if it can't be measured."""
    try:
        import numpy as np
        import trimesh  # noqa: F401

        pts, fidx = _sample(mesh, samples)
        if len(pts) == 0:
            return None
        normals = mesh.face_normals[fidx]
        origins = pts - normals * 1e-3
        locs, ray_idx, _ = mesh.ray.intersects_location(
            origins, -normals, multiple_hits=False
        )
        if len(locs) == 0:
            return None
        d = np.linalg.norm(locs - origins[ray_idx], axis=1)
        d = d[d > 1e-3]
        return float(np.percentile(d, 1)) if len(d) else None
    except Exception:  # noqa: BLE001
        return None


def _sample(mesh, n):
    import trimesh

    try:
        pts, fidx = trimesh.sample.sample_surface_even(mesh, n)
        if len(pts):
            return pts, fidx
    except Exception:  # noqa: BLE001
        pass
    return trimesh.sample.sample_surface(mesh, n)


def uncovered_mounts(body_mesh, mount_spec: dict,
                     probe_z=(0.15, 0.3, 0.5)) -> list[tuple[float, float]]:
    """(x, y) of every snap / backer whose attach point has *no* body material
    just inside the z=0 mounting face -- i.e. the mount would fuse onto thin air.
    This is a presence test, not a wall-thickness test. Empty if all are anchored."""
    try:
        if not body_mesh.is_watertight:
            return []
        items = list(mount_spec.get("add") or []) + list(mount_spec.get("cut") or [])
        centers = [(it[1], it[2]) for it in items]
        centers += [(b[0], b[1]) for b in (mount_spec.get("backers") or [])]
        bad = []
        for x, y in centers:
            pts = [[x, y, z] for z in probe_z]
            if not any(body_mesh.contains(pts)):
                bad.append((round(x, 1), round(y, 1)))
        return bad
    except Exception:  # noqa: BLE001
        return []
