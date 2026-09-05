/*
 * oc_negative.scad -- one openConnect slot as a NEGATIVE solid, centred on the
 * origin, ready to subtract from an accessory's back wall.
 *
 * Wraps mitufy's openconnect_plate.scad (slot_type = "negslot"). Output: the slot
 * void as a solid, x/y centred on (0,0), mouth on the z=0 plane, body in +Z
 * (2.7 mm deep). Subtract it from a body whose wall-facing face is at z=0.
 *
 *   openscad -o snap_oc_negative.stl --backend=manifold \
 *     -D 'grids_x=1' -D 'grids_y=1' scad/oc_negative.scad
 *
 * Needs BOSL2 + scad/lib on OPENSCADPATH.
 */
include <lib/opengrid_base.scad>
use <lib/openconnect_lib.scad>

grids_x = 1;
grids_y = 1;
$fa = 2;
$fs = 0.4;

_cfg = ocslot_cfg();

// openconnect_slot_grid builds the slot(s) anchored so the mouth is on one face.
// Centre the h*v grid on the origin; it is authored mouth-down, so flip to +Z.
translate([-(grids_x * OG_TILE_SIZE) / 2, -(grids_y * OG_TILE_SIZE) / 2, 0])
  openconnect_slot_grid(
    slot_cfg = _cfg, slot_type = "slot",
    horizontal_grids = grids_x, vertical_grids = grids_y,
    slot_position = "All", slot_lock_distribution = "All",
    slot_lock_side = "Left", slot_entryramp_flip = false,
    excess_thickness = 0
  );
