"""Shared center-row split (front/back halves with alignment nipples and holes)."""
import cadquery as cq
import tak_case_pip as p

SPLIT=102.5
NIPPLE_X=(40.0,102.5,165.0)
NIPPLE_R,NIPPLE_LEN,NIPPLE_Z=1.2,4.0,2.0     # Ø2.4 x 4, mid-thickness of the 4 mm plate
HOLE_R,HOLE_DEPTH=1.4,4.4                     # 0.2 mm clearance per side, 0.4 mm slack

def center_halves():
    center=p.sol(p.shell(1))
    cut=p.box(205,SPLIT-70,40,0,70,-30)
    front=center.intersect(cut); back=center.cut(cut)
    for x in NIPPLE_X:
        front=front.fuse(cq.Solid.makeCylinder(NIPPLE_R,NIPPLE_LEN,cq.Vector(x,SPLIT,NIPPLE_Z),cq.Vector(0,1,0)))
        back=back.cut(cq.Solid.makeCylinder(HOLE_R,HOLE_DEPTH,cq.Vector(x,SPLIT,NIPPLE_Z),cq.Vector(0,1,0)))
    return front.clean(),back.clean()
