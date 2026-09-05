/*
 * assemble.scad -- final mount assembly step, driven by build.py / lib/mounts.py.
 * All parameters come in via -D; nothing here is meant to be hand-edited.
 *
 *   openscad -o out.stl --backend=manifold \
 *     -D 'body_file="body.stl"' \
 *     -D 'add=[["snap_bare_full.stl", x, y, z, rotz], ...]' \
 *     -D 'cut=[["snap_oc_negative.stl", x, y, z, rotz], ...]' \
 *     -D 'backers=[[cx, cy, w, h, pitch, onramp, yadj], ...]' \
 *     lib/connectors/assemble.scad
 *
 * One body convention: wall-facing mounting face on the XY plane (z = 0), body in
 * +Z, "up" is +Y.
 *   - add     : openGrid snap STLs, mirrored to occupy z = 0 .. -thickness.
 *   - cut     : negative STLs (e.g. openConnect slot), subtracted at z = 0 .. +depth
 *               so the pocket opens toward the wall (-Z).
 *   - backers : Multiconnect slotted back plate fused on at z = -6.5 .. 0.
 */
use <scad/multiconnectSlotDesign.scad>

body_file = "body.stl";
add = [];
cut = [];
backers = [];
$fa = 2;
$fs = 0.4;

module _place(items, mir) {
  for (a = items)
    translate([a[1], a[2], a[3]]) rotate([0, 0, a[4]]) {
      if (mir) mirror([0, 0, 1]) import(a[0]);
      else import(a[0]);
    }
}

module _backer(s) {
  yadj = len(s) > 6 ? s[6] : 0;
  translate([s[0], s[1] - s[3] / 2 + yadj, 0])
    mirror([0, 1, 0]) rotate([90, 0, 0])
      translate([-s[2] / 2, 0, 0])
        multiconnectBack(backWidth = s[2], backHeight = s[3],
                         distanceBetweenSlots = s[4], dimples = true,
                         onRamp = (len(s) > 5 ? s[5] != 0 : false));
}

union() {
  difference() {
    import(body_file);
    _place(cut, false);
  }
  _place(add, true);
  for (s = backers) _backer(s);
}
