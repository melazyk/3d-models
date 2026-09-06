"""Offscreen preview rendering for CadQuery parts (no display needed).

One PNG, four labelled panels -- iso / opening / mid-plane section / wall side --
so a single image is enough to judge a model: overall shape, the opening, wall
thickness and internal fit (the section), and how the mount sits against the wall.
An optional translucent fixture (openGrid board / Gridfinity baseplate) is drawn
behind the part. Falls back to an SVG if GL is unavailable.
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


def _source(part):
    """A vtkAlgorithm output port producing triangulated polydata for `part`
    (a cq.Workplane/Shape or a path to an STL)."""
    from vtkmodules.vtkFiltersCore import vtkTriangleFilter
    from vtkmodules.vtkIOGeometry import vtkSTLReader

    tf = vtkTriangleFilter()
    if isinstance(part, str):
        rd = vtkSTLReader()
        rd.SetFileName(part)
        tf.SetInputConnection(rd.GetOutputPort())
    else:
        shape = part.val() if hasattr(part, "val") else part
        tf.SetInputData(_polydata(shape))
    tf.Update()
    return tf


def _bounds_extent(algo):
    b = [0.0] * 6
    algo.GetOutput().GetBounds(b)
    return (b[1] - b[0], b[3] - b[2], b[5] - b[4]), b


def render_png(part, out_path: str, size: int = 500, *,
               section: bool = True, section_axis: str = "y",
               fixture_stl: str | None = None) -> str:
    """Write a 2x2 multi-view PNG. `part` is a cq.Workplane/Shape or a path to an
    STL file. `section_axis` ("x"/"y") is the cut-plane normal. Raises on failure."""
    import vtkmodules.vtkRenderingOpenGL2  # noqa
    import vtkmodules.vtkInteractionStyle  # noqa
    from vtkmodules.vtkCommonDataModel import vtkPlane, vtkPlaneCollection
    from vtkmodules.vtkFiltersGeneral import vtkClipClosedSurface
    from vtkmodules.vtkIOImage import vtkPNGWriter
    from vtkmodules.vtkRenderingCore import (
        vtkActor,
        vtkPolyDataMapper,
        vtkRenderer,
        vtkRenderWindow,
        vtkTextActor,
        vtkWindowToImageFilter,
    )
    from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor  # noqa: F401

    src = _source(part)
    (dx, dy, dz), _ = _bounds_extent(src)

    fixture_src = _source(fixture_stl) if fixture_stl and os.path.exists(fixture_stl) else None

    # section: clip the closed surface on the Y=0 plane, keep y<=0, so the cut
    # face is filled -- this is the view that shows wall thickness.
    sec = None
    cut_x = section_axis == "x"
    if section:
        pl = vtkPlane()
        pl.SetOrigin(0, 0, 0)
        pl.SetNormal(1, 0, 0) if cut_x else pl.SetNormal(0, 1, 0)
        pc = vtkPlaneCollection()
        pc.AddItem(pl)
        clip = vtkClipClosedSurface()
        clip.SetInputConnection(src.GetOutputPort())
        clip.SetClippingPlanes(pc)
        clip.SetActivePlaneId(0)
        clip.GenerateFacesOn()
        try:
            clip.Update()
            if clip.GetOutput().GetNumberOfCells() > 0:
                sec = clip
        except Exception:  # noqa: BLE001
            sec = None

    # (direction from focal point to camera, view-up, label, parallel?)
    views = [
        ((1, -1, 0.7), (0, 0, 1), f"iso  {dx:.1f} x {dy:.1f} x {dz:.1f} mm", False),
        ((-0.55, 1, 0.85), (0, 0, 1), "opening (+Y)", True),
        ((-1, 0, 0) if cut_x else (0, -1, 0), (0, 0, 1),
         (f"section @ {section_axis}=0") if sec else "section (n/a)", True),
        ((0.5, -0.6, -1), (0, 1, 0), "wall side (-Z, mounts)", True),
    ]

    rw = vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(size * 2, size * 2)

    keep = []  # hold python refs so VTK objects survive to Render()
    for i, (direction, up, label, parallel) in enumerate(views):
        ren = vtkRenderer()
        ren.SetBackground(1, 1, 1)

        body_src = sec if (i == 2 and sec) else src
        m = vtkPolyDataMapper()
        m.SetInputConnection(body_src.GetOutputPort())
        m.ScalarVisibilityOff()
        a = vtkActor()
        a.SetMapper(m)
        a.GetProperty().SetColor(0.78, 0.80, 0.86)
        a.GetProperty().SetInterpolationToPhong()
        if i == 2 and sec:
            a.GetProperty().SetColor(0.90, 0.78, 0.70)  # section: warm, stands out
        ren.AddActor(a)
        keep += [m, a]

        if fixture_src is not None and not (i == 2 and sec):
            fm = vtkPolyDataMapper()
            fm.SetInputConnection(fixture_src.GetOutputPort())
            fm.ScalarVisibilityOff()
            fa = vtkActor()
            fa.SetMapper(fm)
            fa.GetProperty().SetColor(0.55, 0.62, 0.72)
            fa.GetProperty().SetOpacity(0.22)
            ren.AddActor(fa)
            keep += [fm, fa]

        txt = vtkTextActor()
        txt.SetInput(label)
        txt.GetTextProperty().SetFontSize(int(size * 0.05))
        txt.GetTextProperty().SetColor(0.1, 0.1, 0.1)
        txt.GetTextProperty().SetBackgroundColor(1, 1, 1)
        txt.GetTextProperty().SetBackgroundOpacity(0.7)
        tc = txt.GetPositionCoordinate()
        tc.SetCoordinateSystemToNormalizedViewport()
        tc.SetValue(0.03, 0.03)
        ren.AddActor2D(txt)
        keep.append(txt)

        col = i % 2
        row = 1 - i // 2
        ren.SetViewport(col / 2, row / 2, (col + 1) / 2, (row + 1) / 2)

        cam = ren.GetActiveCamera()
        cam.SetFocalPoint(0, 0, 0)
        cam.SetPosition(*direction)
        cam.SetViewUp(*up)
        if parallel:
            cam.ParallelProjectionOn()
        ren.ResetCamera()
        ren.ResetCameraClippingRange()
        rw.AddRenderer(ren)
        keep.append(ren)

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
