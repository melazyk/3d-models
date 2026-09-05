/*
 * multiconnectSlotDesign.scad
 * From AndyLevesque/QuackWorks (Modules/multiconnectSlotDesign.scad), which is
 * the maintained descendant of cschneid/MultiConnectOpenSCAD. Credit: @David D
 * (Multiconnect) and Jonathan / Keep Making (Multiboard).
 * Licence: CC BY-NC 4.0.
 *
 * Local changes: the file-scope demo call and customiser globals are turned into
 * explicit parameters of multiconnectBack() / slotTool() so the file is safe to
 * `use` without rendering stray geometry. Geometry is byte-for-byte the upstream
 * v2 slot (keyhole + straight channel + v2 snap cutout, or v1 dimple).
 */

//BEGIN MODULES
//Slotted back Module
// backWidth, backHeight:  outer dimensions of the backer plate (mm).
// distanceBetweenSlots:   slot pitch (25 mm = standard Multiboard).
// version:   "v2" (snap cutout, default) or "v1" (dimple).
// dimples:   true -> include the locking feature; false = quick-release (smooth).
// onRamp:    true -> add the on-ramp cones for easy mounting of tall items.
// slotTolerance / dimpleScale / slotDepthMicroadjustment / onRampEveryXSlots:
//   printer-fit tweaks, upstream defaults.
module multiconnectBack(backWidth, backHeight, distanceBetweenSlots,
                        version = "v2", dimples = true, onRamp = true,
                        slotTolerance = 1.00, dimpleScale = 1,
                        slotDepthMicroadjustment = 0, onRampEveryXSlots = 1)
{
    _slotQuickRelease = !dimples;

    let (backWidth = max(backWidth, distanceBetweenSlots),
         backHeight = max(backHeight, 25),
         slotCount = floor(backWidth / distanceBetweenSlots),
         backThickness = 6.5)
    {
        difference() {
            translate(v = [0, -backThickness, 0]) cube(size = [backWidth, backThickness, backHeight]);
            for (slotNum = [0:1:slotCount - 1]) {
                translate(v = [distanceBetweenSlots / 2 + (backWidth / distanceBetweenSlots - slotCount) * distanceBetweenSlots / 2 + slotNum * distanceBetweenSlots, -2.35 + slotDepthMicroadjustment, backHeight - 13]) {
                    slotTool(backHeight, version, _slotQuickRelease, onRamp,
                             slotTolerance, dimpleScale, onRampEveryXSlots, distanceBetweenSlots);
                }
            }
        }
    }

    module slotTool(totalHeight, multiConnectVersion, slotQuickRelease, onRampEnabled,
                    slotTolerance, dimpleScale, onRampEveryXSlots, distanceBetweenSlots) {
        scale(v = slotTolerance)
        let (slotProfile = [[0,0],[10.15,0],[10.15,1.2121],[7.65,3.712],[7.65,5],[0,5]])
        difference() {
            union() {
                //round top
                rotate(a = [90,0,0,])
                    rotate_extrude($fn=50)
                        polygon(points = slotProfile);
                //long slot
                translate(v = [0,0,0])
                    rotate(a = [180,0,0])
                    union(){
                        difference() {
                            linear_extrude(height = totalHeight+1)
                                polygon(points = slotProfile);
                            if (slotQuickRelease == false && multiConnectVersion == "v2")
                                translate(v= [10.15,0,0])
                                rotate(a= [-90,0,0])
                                linear_extrude(height = 5)
                                    polygon(points = [[0,0],[-0.4,0],[0,-8]]);
                            }
                        mirror([1,0,0])
                            difference() {
                                linear_extrude(height = totalHeight+1)
                                    polygon(points = slotProfile);
                                if (slotQuickRelease == false && multiConnectVersion == "v2")
                                    translate(v= [10.15,0,0])
                                    rotate(a= [-90,0,0])
                                    linear_extrude(height = 5)
                                        polygon(points = [[0,0],[-0.4,0],[0,-8]]);
                            }
                    }
                //on-ramp
                if(onRampEnabled)
                    for(y = [1:onRampEveryXSlots:totalHeight/distanceBetweenSlots])
                        translate(v = [0,-5,-y*distanceBetweenSlots])
                            rotate(a = [-90,0,0])
                                cylinder(h = 5, r1 = 12, r2 = 10.15);
            }
            //dimple
            if (slotQuickRelease == false && multiConnectVersion == "v1")
                scale(v = dimpleScale)
                rotate(a = [90,0,0,])
                    rotate_extrude($fn=50)
                        polygon(points = [[0,0],[0,1.5],[1.5,0]]);
        }
    }
}
