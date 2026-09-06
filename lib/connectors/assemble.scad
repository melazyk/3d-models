/*
 * assemble.scad -- final mount assembly step, driven by build.py / lib/mounts.py.
 * All parameters come in via -D; nothing here is meant to be hand-edited.
 *
 *   openscad -o out.stl --backend=manifold \
 *     -D 'body_file="body.stl"' \
 *     -D 'add=[[stl, x, y, z, rotz, mirror01], ...]' \
 *     -D 'cut=[[stl, x, y, z, rotz, mirror01], ...]' \
 *     -D 'backers=[[cx, cy, w, h, pitch, onramp, yadj], ...]' \
 *     lib/connectors/assemble.scad
 *
 * One body convention: wall-facing mounting face on the XY plane (z = 0), body in
 * +Z, "up" is +Y.  Each add/cut item carries its own z offset and a mirror flag
 * (mirror01 = 1 flips in z -- mitufy snaps need it; jp snaps and cut negatives
 * don't, they are authored with a z offset instead).
 *   - add     : openGrid snap STLs, ending up behind z = 0.
 *   - cut     : negative STLs (e.g. openConnect slot), subtracted so the pocket
 *               opens toward the wall (-Z).
 *   - backers : Multiconnect v2 slotted back plate fused on at z = -6.5 .. 0.
 */
use <scad/multiconnectSlotDesign.scad>

body_file = "body.stl";
add = [];
cut = [];
backers = [];
$fa = 2;
$fs = 0.4;

// item = [path, x, y, z, rot_z, mirror_z(0/1)]  (mirror flag optional, default 0)
module _place(items) {
  for (a = items)
    translate([a[1], a[2], a[3]]) rotate([0, 0, a[4]]) {
      if (len(a) > 5 && a[5] != 0) mirror([0, 0, 1]) import(a[0]);
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
    _place(cut);
  }
  _place(add);
  for (s = backers) _backer(s);
}
