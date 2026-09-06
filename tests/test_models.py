"""Regression tests: every model still builds, is solid, and fits the P2S.

Run:  pytest -q
Fast: pytest -q            (no PNG render)
Full: RENDER_PNG=1 pytest  (also exercises the preview renderer once)

A model directory with a `.modelignore` file is excluded (see build.py:iter_models
and docs/improvement-plan.md). New shared code that breaks an existing model must
fail here before it lands.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build_target, iter_models  # noqa: E402
from lib import mounts  # noqa: E402

MODELS = list(iter_models(ROOT))
IDS = [s.parent.name for s in MODELS]
WANT_PNG = os.environ.get("RENDER_PNG") == "1"
HAVE_OPENSCAD = mounts.resolve_openscad() is not None


@pytest.mark.skipif(not MODELS, reason="no models to test")
@pytest.mark.parametrize("script", MODELS, ids=IDS)
def test_model_builds(script: Path):
    res = build_target(script, want_png=WANT_PNG, tol=0.05, verbose=False)

    assert res.error is None, res.error
    assert res.fits_p2s is not False, f"{res.name} does not fit the P2S 256^3 volume"
    assert res.solid is not False, f"{res.name} mesh is not solid / watertight"

    if res.had_mounts and HAVE_OPENSCAD:
        assert res.mounts_applied, (
            f"{res.name} declares MOUNTS but they were not fused: {res.warnings}"
        )


def test_modelignore_is_respected():
    listed = {s.parent.name for s in iter_models(ROOT)}
    for d in (ROOT / "models").glob("*/"):
        if (d / ".modelignore").exists():
            assert d.name not in listed, f"{d.name} has .modelignore but was still listed"


@pytest.mark.skipif(not HAVE_OPENSCAD, reason="needs OpenSCAD to fuse the mount")
def test_checks_catch_a_floating_mount(tmp_path):
    d = tmp_path / "floating_mount"
    d.mkdir()
    (d / "model.py").write_text(
        "import cadquery as cq\n"
        "from lib import mounts\n"
        "def build():\n"
        "    return cq.Workplane('XY').box(20, 20, 10, centered=(True, True, False))\n"
        "MOUNTS = mounts.snaps('jp4', cols=1, rows=1, origin=(40, 0))\n"
    )
    res = build_target(d / "model.py", want_png=False, tol=0.05, verbose=False)
    assert res.uncovered, "a snap 40 mm off the body should be flagged as uncovered"
    assert not res.ok
