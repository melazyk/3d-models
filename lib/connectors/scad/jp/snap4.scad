/*
 * snap4.scad -- 4-way symmetric openGrid snap.
 *
 * Derived from jp-embedded/opengrid  snap.scad  (GPL-3.0).  Changes: the flex
 * tabs and their relief slices are placed on ALL FOUR sides of the tile instead
 * of two, and the directional top hook is dropped -- so the snap seats into an
 * openGrid cell at any 90 deg rotation (0/90/180/270), tabs flexing in and
 * springing back.  Same tab/groove profile as upstream.
 *
 *   openscad -o snap4.stl --backend=manifold \
 *     scad/jp/snap4.scad
 *
 * Output: insert body at z = 0 .. tile_height/2 (3.4 mm), XY centred on the tile.
 * Needs BOSL2 on OPENSCADPATH.
 */
include <BOSL2/std.scad>

/* [Hidden] */
part_gap = 0.2;
tile_size = 28;
tile_height = 6.8;
tile_edge_width = 1.5;
$fa = 2;
$fs = 0.4;
e = EPSILON;

module tile(grove = true, gap = 0)
{
    difference() {
        cuboid([tile_size + e, tile_size + e, tile_height]);
        cuboid([tile_size - tile_edge_width * 2 - gap * 2,
                tile_size - tile_edge_width * 2 - gap * 2, tile_height + e]);
        grove_h = 2;
        chamf_y = (tile_height - grove_h) / 2;
        chamf_x = chamf_y * 0.7;
        if (grove)
            diff() cuboid([tile_size - 1.6, tile_size - 1.6, tile_height])
                edge_profile() mask2d_chamfer(x = chamf_x, y = chamf_y);
    }
    intersection() {
        c = adj_opp_to_hyp(4.2, 4.2) / 2 + 2.6 + gap;
        cuboid([tile_size + e, tile_size + e, tile_height]);
        zrot_copies(n = 4) move([tile_size / 2, tile_size / 2, 0]) zrot(45)
            cuboid([c * 2, 100, tile_height], chamfer = 1.4);
    }
}


// one flex tab on the LEFT edge (upstream side_snap), gap-relieved so it can flex
module side_tab()
{
    snap_l = 8;
    flatten = 0.4;
    difference() {
        grove_h = 2;
        chamf_y = (tile_height - grove_h) / 2;
        chamf_x = chamf_y * 0.7;
        intersection() {
            diff() cuboid([tile_size - 1.6, snap_l, tile_height])
                edge_profile(except=[FRONT+TOP,FRONT+BOTTOM,BACK+TOP,BACK+BOTTOM])
                    mask2d_chamfer(x = chamf_x, y = chamf_y);
            up(1.85) diff() cuboid([tile_size - 1.6, snap_l + 1, tile_height])
                edge_profile(except=[FRONT+TOP,FRONT+BOTTOM,BACK+TOP,BACK+BOTTOM])
                    mask2d_chamfer(x = chamf_x, y = chamf_y);
        }
        left(tile_size/2 - 1.5 - part_gap - e) cuboid([50, 10, 10], anchor=LEFT);
        left(tile_size/2 - 0.8 - flatten) cuboid([10, 10, 10], anchor=RIGHT);
    }
}

module snap4()
{
    difference() {
        up(e) cuboid([tile_size, tile_size, tile_height/2 - 2*e], anchor=BOTTOM);
        tile(grove = false, gap = part_gap);

        // relief slices on all 4 sides so each tab can flex
        cut_recess = 0.8;
        cut_indent = 3.5;
        down(cut_recess) zrot_copies(n = 4) {
            right(tile_size/2 - cut_indent) cuboid([0.5, 14, tile_height + e], anchor=LEFT);
            up(tile_height/2) right(tile_size/2 - 3) cuboid([10, 14, 0.2], anchor=LEFT+TOP);
        }

        // ease all 4 corners for angled insert
        c = adj_opp_to_hyp(4.2, 4.2) / 2 + 2.6;
        zrot_copies(n = 4) up(1.3) move([tile_size/2, tile_size/2, 0]) zrot(45) yrot(10)
            cuboid([c * 2, 100, tile_height], anchor=TOP);

    }
    zrot_copies(n = 4) side_tab();
}

// clip anything below z=0 (a little corner-ease bleed) so the mating face is flat
difference() {
    snap4();
    up(e) cuboid(200, anchor = TOP);   // remove z < ~0, leaving a flat mating face
}
