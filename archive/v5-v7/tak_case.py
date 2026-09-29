"""CAD prototype: two lift-up playing panels over mirrored loose-stone wells."""
import cadquery as cq

# Reuse the established 205 mm board dimensions and decorative overlay.
import tak_box_base as old

D=old.D
box=old.box
cylinder=old.cylinder


def wing_y(index):
    if index not in (0,2):raise ValueError(index)
    return 0.0 if index==0 else 123.0


def shell(index,d=D):
    """A wing well or fixed center row, with replaceable main hinge knuckles."""
    if index not in (0,1,2):raise ValueError(index)
    if index==1:
        part=box(205,41,4,0,82,0)
        # Match the two wing floors so all three sections rest on the table.
        for x in (0,203):part=part.fuse(box(2,37,20.1,x,84,-20.1))
    else:
        y0=wing_y(index)
        part=box(205,82,1,0,y0,0)
        part=part.fuse(box(200,74,21.1,2.5,y0+4,-20.1))
        outer_y=y0 if index==0 else y0+78
        part=part.fuse(box(200,4,21.1,2.5,outer_y,-20.1))
        fixed_y=y0+79.5 if index==0 else y0
        part=part.fuse(box(205,2.5,3,0,fixed_y,1))
        # Broad flat well, then a separate sideways keystone recess.
        well_y=y0+(8 if index==0 else 10)
        part=part.cut(box(152,64,19.2,8,well_y,-18.1))
        part=part.cut(box(29,24,19.7,168,y0+29,-18.6))
    for seam_i,edge_y in enumerate(d.seam_y):
        if index not in (seam_i,seam_i+1):continue
        left=index==seam_i
        step=d.knuckle_length+d.knuckle_gap
        for k in range(d.knuckle_count):
            x=d.knuckle_margin+k*step
            owns=(k%2==0)==left
            if owns:
                part=part.fuse(cylinder(d.barrel_diameter/2,d.knuckle_length,
                                        x,edge_y,d.hinge_z))
                lug_y=edge_y-2.4 if left else edge_y
                part=part.fuse(box(d.knuckle_length,2.4,2,x,lug_y,0))
                part=part.cut(cylinder(d.bore_diameter/2,d.knuckle_length+.04,
                                       x-.02,edge_y,d.hinge_z))
            else:
                part=part.cut(cylinder(d.barrel_diameter/2+.2,d.knuckle_length+.1,
                                       x-.05,edge_y,d.hinge_z))
    if index in (0,2):
        # Opposing floor-edge magnets retain the complete folded case.
        axis_y=d.seam_y[0 if index==0 else 1]
        unwind=-90 if index==0 else 90
        for x in (12.0,68.0,129.0,185.0):
            pad_y=96.1 if index==0 else 102.9
            face_y=102.1 if index==0 else 102.9
            direction=cq.Vector(0,-1 if index==0 else 1,0)
            pad=box(8,6,5,x,pad_y,-80)
            hole=cq.Solid.makeCylinder(2,2,cq.Vector(x+4,face_y,-77.5),direction)
            pad=pad.rotate((0,axis_y,0),(1,axis_y,0),unwind)
            hole=hole.rotate((0,axis_y,0),(1,axis_y,0),unwind)
            part=part.fuse(pad).cut(hole)
    return part.clean()


def lid_blank(index):
    y0=wing_y(index)
    lid=box(205,79.5,3,0,y0 if index==0 else y0+2.5,1)
    # Thin only above the keystone, leaving 1.4 mm of playing-face roof.
    lid=lid.cut(box(29,24,1.6,168,y0+29,1))
    # Thumb access is in the 15 mm border, away from the playing squares.
    edge_y=y0+79.5 if index==0 else y0+2.5
    return lid.cut(cq.Solid.makeCylinder(6,4,cq.Vector(7,edge_y,.5))).clean()


def lid_pair(index,d=D):
    """Cut alternating outer-edge hinge knuckles into shell and lid."""
    base,lid=shell(index,d),lid_blank(index)
    axis_y=0 if index==0 else 205
    step=d.knuckle_length+d.knuckle_gap
    for k in range(d.knuckle_count):
        x=d.knuckle_margin+k*step
        barrel=cylinder(2,d.knuckle_length,x,axis_y,1)
        clearance=cylinder(2.2,d.knuckle_length+.1,x-.05,axis_y,1)
        bore=cylinder(1.2,d.knuckle_length+.04,x-.02,axis_y,1)
        if k%2==0:
            base=base.fuse(barrel).cut(bore)
            lid=lid.cut(clearance)
        else:
            lid=lid.fuse(barrel).cut(bore)
            base=base.cut(clearance)
    # Two inset Ø4 × 2 mm magnet pairs hold each playing panel shut.
    latch_y=75 if index==0 else 130
    for x in (42,163):
        base=base.cut(cq.Solid.makeCylinder(2,2,cq.Vector(x,latch_y,1),
                                            cq.Vector(0,0,-1)))
        lid=lid.cut(cq.Solid.makeCylinder(2,2,cq.Vector(x,latch_y,1),
                                          cq.Vector(0,0,1)))
    return base.clean(),lid.clean()


def lid_open(lid,index,degrees):
    axis_y=0 if index==0 else 205
    return lid.rotate((0,axis_y,1),(1,axis_y,1),
                      degrees if index==0 else -degrees)


def posed(shape,index,degrees):return old.posed(shape,index,degrees)


def main_pin(seam_i):return old.pin(seam_i)


def lid_pin(index,d=D):
    length=(d.knuckle_count-1)*(d.knuckle_length+d.knuckle_gap)+d.knuckle_length
    return cylinder(d.pin_diameter/2,length,d.knuckle_margin,
                    0 if index==0 else 205,1)


def pieces(index,d=D):
    """One-layer nominal placement; the well has room for two layers."""
    y0=wing_y(index)
    row_y=9 if index==0 else 134
    flats=[box(20,20,8,10+21*col,row_y+21*row,-17.6)
           for row in range(3) for col in range(7)]
    k=cylinder(d.rook_diameter_max/2,d.rook_length,
               169.8,y0+41,-8)
    return flats+[k]


def overlay(index,d=D):
    """Attach black accent to the movable panel, leaving 2 mm by main hinge."""
    original=old.face_overlay(index,d)
    if index==1:return original
    y0=0 if index==0 else 125.5
    accent=original.intersect(box(205,79.5,d.overlay_height,0,y0,4))
    edge_y=79.5 if index==0 else 125.5
    return accent.cut(cq.Solid.makeCylinder(6,2,cq.Vector(7,edge_y,3.5))).clean()
