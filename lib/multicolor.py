"""Multi-colour (multi-filament) output.

A model opts in by defining

    def color_parts() -> list[tuple[str, str, cq.Workplane]]:
        return [("plate", "#F2F2F2", plate), ("text", "#1A1A1A", text)]

(name, hex colour, body); the first entry is filament 1, the next filament 2, ...
Bodies must not overlap (cut the inlay out of the base body).

`write_3mf` writes ONE object made of several parts, with the per-part extruder
already assigned in Bambu Studio's `Metadata/model_settings.config`, so opening
`part.3mf` in Bambu Studio / OrcaSlicer gives a ready multi-colour object.
"""
from __future__ import annotations

import zipfile
from xml.sax.saxutils import escape

import cadquery as cq

_CT = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="config" ContentType="text/xml"/>
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""


def _mesh(body: cq.Workplane, tol: float):
    shape = body.val() if len(body.vals()) == 1 else cq.Compound.makeCompound(body.vals())
    verts, tris = shape.tessellate(tol, 0.1)
    # OCC tessellates face by face with duplicated seam vertices -> an open mesh
    # that slicers mis-repair (glyph counters turn into plate). Weld it.
    import trimesh

    m = trimesh.Trimesh([(v.x, v.y, v.z) for v in verts], tris, process=True)
    m.fix_normals()
    if not m.is_watertight:
        raise RuntimeError("multicolour part mesh is not watertight after welding")
    return m.vertices.tolist(), m.faces.tolist()


def write_3mf(parts, path: str, *, name: str = "model", tol: float = 0.02) -> None:
    objs, comps, cfg_parts = [], [], []
    colors = "".join(
        f'<base name="{escape(n)}" displaycolor="{c.upper()}FF"/>' for n, c, _ in parts
    )
    for i, (pname, _color, body) in enumerate(parts):
        oid = i + 1
        verts, tris = _mesh(body, tol)
        vs = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in verts)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
        objs.append(
            f'<object id="{oid}" type="model" name="{escape(pname)}" pid="100" pindex="{i}">'
            f"<mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>"
        )
        comps.append(f'<component objectid="{oid}"/>')
        cfg_parts.append(
            f'  <part id="{oid}" subtype="normal_part">\n'
            f'   <metadata key="name" value="{escape(pname)}"/>\n'
            f'   <metadata key="extruder" value="{i + 1}"/>\n'
            f"  </part>\n"
        )
    top = len(parts) + 1
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '<metadata name="Application">BambuStudio-01.10.00.00</metadata>\n'
        f'<resources><basematerials id="100">{colors}</basematerials>'
        + "".join(objs)
        + f'<object id="{top}" type="model" name="{escape(name)}"><components>'
        + "".join(comps)
        + "</components></object></resources>"
        f'<build><item objectid="{top}" transform="1 0 0 0 1 0 0 0 1 128 128 0"/></build>'
        "</model>"
    )
    cfg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
        f' <object id="{top}">\n'
        f'  <metadata key="name" value="{escape(name)}"/>\n'
        '  <metadata key="extruder" value="1"/>\n'
        + "".join(cfg_parts)
        + " </object>\n</config>\n"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CT)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", cfg)


def hex_rgb(c: str) -> tuple[float, float, float]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
