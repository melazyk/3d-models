#!/usr/bin/env bash
# Regenerate the vendored connector STLs in lib/connectors/ from source.
#
# Needs network. Downloads a pinned OpenSCAD nightly AppImage + BOSL2 + the
# openGrid OpenSCAD libs (already copied into ../scad/), renders each connector
# variant headlessly, and drops the STLs in lib/connectors/.
#
# Run from anywhere:  bash lib/connectors/vendor/regenerate.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONN="$(dirname "$HERE")"           # lib/connectors
SCAD="$CONN/scad"

# --- pinned sources ------------------------------------------------------------
OPENSCAD_URL="https://files.openscad.org/snapshots/OpenSCAD-2025.12.30.ai30275-x86_64.AppImage"
BOSL2_COMMIT="master"   # BOSL2 is API-stable; pin a SHA here if a change ever breaks a render
# openGrid libs in ../scad/ come from github.com/mitufy/opengrid-projects (CC BY 4.0)
# multiconnectSlotDesign.scad from cschneid/MultiConnectOpenSCAD via Arucious (CC BY-NC 4.0)

cd "$HERE"

if [ ! -x squashfs-root/AppRun ]; then
  echo ">> downloading OpenSCAD nightly"
  curl -sSL -o openscad.AppImage "$OPENSCAD_URL"
  chmod +x openscad.AppImage
  ./openscad.AppImage --appimage-extract >/dev/null
fi
OS="$HERE/squashfs-root/AppRun"

if [ ! -d BOSL2 ]; then
  echo ">> cloning BOSL2"
  git clone --depth 1 https://github.com/BelfrySCAD/BOSL2.git BOSL2
  [ "$BOSL2_COMMIT" != "master" ] && (cd BOSL2 && git fetch --depth 1 origin "$BOSL2_COMMIT" && git checkout "$BOSL2_COMMIT")
fi

export OPENSCADPATH="$HERE:$SCAD"        # $HERE holds the BOSL2/ dir
export QT_QPA_PLATFORM=offscreen
S="$SCAD/opengrid_parametric_snap.scad"

render() {
  local out="$CONN/$1"; shift
  echo ">> $out"
  "$OS" -o "$out" --export-format binstl --backend=manifold "$@" "$S" 2>&1 \
    | grep -E 'Status:|Facets:|WARNING|ERROR' || true
}

render_scad() {                          # render an arbitrary .scad (not the snap file)
  local out="$CONN/$1"; local scad="$2"; shift 2
  echo ">> $out"
  "$OS" -o "$out" --export-format binstl --backend=manifold "$@" "$SCAD/$scad" 2>&1 \
    | grep -E 'Status:|Facets:|WARNING|ERROR' || true
}

COMMON=(-D 'thickness_text_mode="None"')
render snap_bare_full.stl         -D 'generate_snap="Bare"'          -D 'snap_thickness=6.8' "${COMMON[@]}"
render snap_bare_lite.stl         -D 'generate_snap="Bare"'          -D 'snap_thickness=4'   "${COMMON[@]}"
render snap_basic_full.stl        -D 'generate_snap="Basic Threads"' -D 'snap_thickness=6.8' "${COMMON[@]}"
render snap_basic_lite.stl        -D 'generate_snap="Basic Threads"' -D 'snap_thickness=4'   "${COMMON[@]}"
render snap_openconnect_full.stl  -D 'generate_snap="openConnect"'   -D 'snap_thickness=6.8' "${COMMON[@]}"
render snap_multiconnect_full.stl -D 'generate_snap="multiConnect"'  -D 'snap_thickness=6.8' "${COMMON[@]}"
render screw_openconnect.stl      -D 'generate_snap="None"' -D 'generate_screw="openConnect"'  -D 'threads_type="Blunt"' "${COMMON[@]}"
render screw_multiconnect.stl     -D 'generate_snap="None"' -D 'generate_screw="multiConnect"' -D 'threads_type="Blunt"' "${COMMON[@]}"

# openConnect slot NEGATIVE (1 cell), re-centred on the origin afterwards
render_scad snap_oc_negative_raw.stl oc_negative.scad -D 'grids_x=1' -D 'grids_y=1'
python3 - "$CONN/snap_oc_negative_raw.stl" "$CONN/snap_oc_negative.stl" <<'PY'
import sys, trimesh
m = trimesh.load(sys.argv[1], process=True)
c = m.bounds.mean(axis=0)
m.apply_translation([-c[0], -c[1], -m.bounds[0][2]])
m.export(sys.argv[2])
PY
rm -f "$CONN/snap_oc_negative_raw.stl"

echo "done."
