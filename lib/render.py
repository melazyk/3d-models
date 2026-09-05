"""Offscreen preview rendering for CadQuery parts (no display needed).

Produces a single PNG with iso / front / top / right views so one image is enough
to judge a model. Uses OCP's VTK bridge; falls back to an SVG if GL is unavailable.
"""
from __future__ import annotations

import os

os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")

import cadquery as cq  # noqa: E402


def _polydata(shape):
    from OCP.IVtkOCC import IVtkOCC_Shape, IVtkOCC_ShapeMesher
    from OCP.IVtkVTK import IVtkVTK_ShapeData

    vs = IVtkOCC_Shape(shape.wrapped)
    sd = IVtkVTK_ShapeData()
    IVtkOCC_ShapeMesher().Build(vs, sd)
    return sd.getVtkPolyData()


def render_png(part, out_path: str, size: int = 500) -> str:
    """Write a 2x2 multi-view PNG. `part` is a cq.Workplane/Shape or a path to an
    STL file. Returns out_path. Raises on failure."""
    import vtkmodules.vtkRenderingOpenGL2  # noqa
    import vtkmodules.vtkInteractionStyle  # noqa
    from vtkmodules.vtkFiltersCore import vtkTriangleFilter
    from vtkmodules.vtkIOGeometry import vtkSTLReader
    from vtkmodules.vtkIOImage import vtkPNGWriter
    from vtkmodules.vtkRenderingCore import (
        vtkActor,
        vtkPolyDataMapper,
        vtkRenderer,
        vtkRenderWindow,
        vtkWindowToImageFilter,
    )

    tf = vtkTriangleFilter()
    if isinstance(part, str):
        rd = vtkSTLReader()
        rd.SetFileName(part)
        tf.SetInputConnection(rd.GetOutputPort())
    else:
        shape = part.val() if hasattr(part, "val") else part
        tf.SetInputData(_polydata(shape))
    tf.Update()

    # (direction from focal point to camera, view-up). Covers: overall shape, the
    # opening (often +Y), the wall-facing -Z face where the mounts live, and plan.
    views = {
        "iso":       ((1, -1, 0.7), (0, 0, 1)),
        "opening":   ((-0.55, 1, 0.85), (0, 0, 1)),
        "wall side": ((0.5, -0.6, -1), (0, 1, 0)),
        "top":       ((0, 0, 1), (0, 1, 0)),
    }
    rw = vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(size * 2, size * 2)

    for i, (name, (direction, up)) in enumerate(views.items()):
        m = vtkPolyDataMapper()
        m.SetInputConnection(tf.GetOutputPort())
        m.ScalarVisibilityOff()
        a = vtkActor()
        a.SetMapper(m)
        a.GetProperty().SetColor(0.78, 0.80, 0.86)
        a.GetProperty().SetInterpolationToPhong()
        ren = vtkRenderer()
        ren.AddActor(a)
        ren.SetBackground(1, 1, 1)
        col = i % 2
        row = 1 - i // 2
        ren.SetViewport(col / 2, row / 2, (col + 1) / 2, (row + 1) / 2)
        cam = ren.GetActiveCamera()
        cam.SetFocalPoint(0, 0, 0)
        cam.SetPosition(*direction)
        cam.SetViewUp(*up)
        if name != "iso":
            cam.ParallelProjectionOn()
        ren.ResetCamera()
        ren.ResetCameraClippingRange()
        rw.AddRenderer(ren)

    rw.Render()
    w2i = vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    wr = vtkPNGWriter()
    wr.SetFileName(out_path)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    return out_path


def render_svg(part: cq.Workplane, out_path: str) -> str:
    cq.exporters.export(part, out_path)
    return out_path
