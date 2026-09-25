"""Tak folding board with the play face outside and piece channels in its wings.

Prototype geometry, millimetres. Three 2+1+2 row board sections enclose their
own storage channels. Two replaceable hinge pins and two channel end caps are
separate parts. Physical clearances must be printed and tested.
"""
from dataclasses import dataclass
import cadquery as cq

@dataclass(frozen=True)
class Dimensions:
    pitch: float = 41.0
    board_rows: int = 5
    board_skin: float = 4.0
    face_margin: float = 15.0
    face_pitch: float = 35.0
    grid_width: float = 2.4
    overlay_height: float = 0.8
    hinge_z: float = 0.0
    channel_side: float = 23.0
    channel_depth: float = 34.0
    core_depth: float = 40.0
    channel_wall: float = 1.2
    channel_length: float = 197.4
    channel_x: float = 2.8
    floor_depth: float = 20.1
    cap_extension: float = 8.0
    rook_diameter_max: float = 19.8
    rook_length: float = 25.4
    # Twenty-one 8 mm flats begin at X4.2 and end at X172.2. The keystone
    # pocket begins exactly there, at the very tip of the same magazine.
    rook_chamber_start_x: float = 172.2
    pin_diameter: float = 2.0
    bore_diameter: float = 2.4
    barrel_diameter: float = 4.0
    knuckle_length: float = 19.4
    knuckle_gap: float = 0.2
    knuckle_count: int = 10
    knuckle_margin: float = 4.9

    @property
    def board_size(self): return self.pitch * self.board_rows
    @property
    def seam_y(self): return (2*self.pitch, 3*self.pitch)

D = Dimensions()

def box(dx,dy,dz,x,y,z):
    return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z)).val()

def cylinder(radius,length,x,y,z):
    return cq.Solid.makeCylinder(radius,length,cq.Vector(x,y,z),cq.Vector(1,0,0))

def prism_yz(points,length,x,y):
    """Extrude a channel cross section along the board's X direction."""
    return (cq.Workplane('YZ').polyline(points).close().extrude(length)
            .translate((x,y,0)).val())

OUTER_CHANNEL=((0,0),(23,0),(23,-23.0),(13,-34.0),(10,-34.0),(0,-23.0))
INNER_CHANNEL=((1.2,-1.2),(21.8,-1.2),(21.8,-21.8),
               (12,-32.0),(11,-32.0),(1.2,-21.8))
ROOK_INNER=((1.5,-1.5),(23.5,-1.5),(23.5,-23.5),(1.5,-23.5))
ROOK_OUTER=((0.3,-0.3),(24.7,-0.3),(24.7,-24.7),(0.3,-24.7))

def channel(y0,d=D):
    """Integral tube with a support-free pitched roof and high-X mouth."""
    L,w=d.channel_length,d.channel_wall
    outer=prism_yz(OUTER_CHANNEL,L,d.channel_x,y0)
    void=prism_yz(INNER_CHANNEL,L-w,d.channel_x+w,y0)
    return outer.cut(void).clean()

def channel_void(y0,d=D):
    """Pitched stone passage, ending where the flat-roof chamber begins."""
    start=d.channel_x+d.channel_wall
    return prism_yz(INNER_CHANNEL,d.rook_chamber_start_x-start,start,y0)

def rook_void(y0,d=D):
    """Wider terminal keystone pocket in line with the 21-stone passage."""
    mouth=d.channel_x+d.channel_length
    return prism_yz(ROOK_INNER,mouth-d.rook_chamber_start_x,
                    d.rook_chamber_start_x,y0)

def poly_xy(points,height,z):
    return (cq.Workplane('XY').polyline(points).close().extrude(height)
            .translate((0,0,z)).val())

def face_overlay(index,d=D):
    """Raised black border and 5 x 5 grid, split at the existing hinges."""
    if index not in (0,1,2): raise ValueError(index)
    S,b,t=d.board_size,d.face_margin,d.overlay_height
    assert abs(2*b+5*d.face_pitch-S)<1e-6
    z=d.board_skin
    bars=[box(b,S,t,0,0,z),box(b,S,t,S-b,0,z),
          box(S-2*b,b,t,b,0,z),box(S-2*b,b,t,b,S-b,z)]
    for n in range(1,5):
        at=b+n*d.face_pitch-d.grid_width/2
        bars.append(box(d.grid_width,S-2*b,t,at,b,z))
        bars.append(box(S-2*b,d.grid_width,t,b,at,z))
    accent=bars[0]
    for bar in bars[1:]: accent=accent.fuse(bar)
    # Bold through-cut motifs expose the white board beneath the black border.
    # Every opening stays at least 2 mm from the border edges.
    for cx in (47.5,157.5):
        cy=7.5
        cat=poly_xy([(cx-5,cy+5),(cx-5,cy-2),(cx-6,cy-5),
                     (cx-2,cy-4),(cx,cy-1),(cx+2,cy-4),
                     (cx+6,cy-5),(cx+5,cy-2),(cx+5,cy+5),
                     (cx+3,cy+6),(cx-3,cy+6)],t,z)
        accent=accent.cut(cat)
    cx,cy=102.5,7.5
    hat=poly_xy([(cx-5,cy+3),(cx,cy-5),(cx+5,cy+3)],t,z)
    hat=hat.fuse(box(15,2,t,cx-7.5,cy+3,z))
    accent=accent.cut(hat)
    for cy in (50,155):
        cx=7.5
        star=poly_xy([(cx,cy-5),(cx+1.5,cy-1.5),(cx+5,cy),
                      (cx+1.5,cy+1.5),(cx,cy+5),
                      (cx-1.5,cy+1.5),(cx-5,cy),(cx-1.5,cy-1.5)],t,z)
        accent=accent.cut(star)
        cx=197.5
        accent=accent.cut(star.translate((190,0,0)))
    for cx in (47.5,157.5):
        cy=197.5
        outer=cq.Solid.makeCylinder(5,t,cq.Vector(cx,cy,z))
        inner=cq.Solid.makeCylinder(4.4,t,cq.Vector(cx+2.2,cy-.6,z))
        accent=accent.cut(outer.cut(inner))
    cx,cy=102.5,197.5
    accent=accent.cut(poly_xy([(cx,cy-5),(cx+1.5,cy-1.5),(cx+5,cy),
                               (cx+1.5,cy+1.5),(cx,cy+5),
                               (cx-1.5,cy+1.5),(cx-5,cy),(cx-1.5,cy-1.5)],t,z))
    y0=(0,2*d.pitch,3*d.pitch)[index]
    depth=(2*d.pitch,d.pitch,2*d.pitch)[index]
    return accent.intersect(box(S,depth,t,0,y0,z)).clean()

def cap(y0,ridges,d=D):
    """Removable rectangular cap matching the flat-roof rook chamber."""
    w=d.channel_wall
    x=d.channel_x+d.channel_length
    c=prism_yz(ROOK_OUTER,d.cap_extension,x,y0)
    c=c.cut(prism_yz(ROOK_INNER,d.cap_extension-w,x,y0))
    for rail in (
        box(1.2,12.0,0.6,x-1.2,y0+6.5,-1.65),
        box(1.2,0.6,12.0,x-1.2,y0+1.35,-18.0),
        box(1.2,0.6,12.0,x-1.2,y0+23.05,-18.0),
    ):
        c=c.fuse(rail)
    if ridges==1:
        c=c.fuse(box(0.8,0.8,4.0,x+d.cap_extension-1.0,y0+24.7,-13.5))
    else:
        for zz in (-17.0,-7.0):
            c=c.fuse(box(0.8,0.8,1.5,x+d.cap_extension-1.0,y0+24.7,zz))
    return c.clean()

def board_section(index,d=D):
    if index not in (0,1,2): raise ValueError(index)
    y0=(0,2*d.pitch,3*d.pitch)[index]
    depth=(2*d.pitch,d.pitch,2*d.pitch)[index]
    panel=box(d.board_size,depth,d.board_skin,0,y0,0)
    # The white structure stays flat; black grid/border parts attach above it.
    # This preserves the support-free face-down print orientation.
    # Structural cores on the backs of the wings fill most of the closed
    # volume. Each has a pitched, close-fitting piece passage. The core
    # heights are complementary in the folded case, with a 2 mm vertical
    # clearance between them and space at the floor for magnet pads.
    if index==0:
        core=prism_yz(((34,0),(78,0),(78,-d.core_depth),
                       (40,-d.core_depth),(34,-d.channel_depth)),
                      d.channel_length,d.channel_x,0)
        panel=panel.fuse(core).cut(channel_void(50.0,d)).cut(rook_void(50.0,d))
        # Fixed bottom leaf: projects down from the free edge when open,
        # and turns inward to form half the box floor when closed.
        panel=panel.fuse(box(d.board_size,2.0,d.floor_depth,0,0,-d.floor_depth))
        panel=panel.fuse(box(d.channel_length,5.0,d.floor_depth,
                             d.channel_x,2.0,-d.floor_depth))
    elif index==2:
        core=prism_yz(((173,0),(198,0),(198,-d.core_depth+8.0),
                       (190,-d.core_depth),(173,-d.core_depth)),
                      d.channel_length,d.channel_x,0)
        panel=panel.fuse(core).cut(channel_void(173.0,d)).cut(rook_void(173.0,d))
        panel=panel.fuse(box(d.board_size,2.0,d.floor_depth,0,d.board_size-2.0,-d.floor_depth))
        panel=panel.fuse(box(d.channel_length,5.0,d.floor_depth,
                             d.channel_x,d.board_size-7.0,-d.floor_depth))
    else:
        panel=panel.fuse(box(d.channel_length,d.pitch-4.0,4.0,
                             d.channel_x,d.seam_y[0]+2.0,-4.0))
        # Two short end walls support the center row at the same 40 mm table
        # height as the wing cores. Their X positions clear the passages and
        # caps throughout the fold.
        for x in (0.0,d.board_size-2.0):
            panel=panel.fuse(box(2.0,d.pitch-4.0,d.core_depth,
                                 x,d.seam_y[0]+2.0,-d.core_depth))
    if index in (0,2):
        # Four blind magnet seats on the mating floor edges. Their solid pads
        # belong to the wings and face one another across a 0.8 mm closed gap.
        # Define each seat in closed case coordinates, then unfold it with its
        # wing. Ø4 × 2 mm magnets are installed from the exposed pad ends.
        axis_y=d.seam_y[0 if index==0 else 1]
        unwind=-90 if index==0 else 90
        for x in (12.0,68.0,129.0,185.0):
            pad_y=96.1 if index==0 else 102.9
            face_y=102.1 if index==0 else 102.9
            pocket_dir=cq.Vector(0,-1 if index==0 else 1,0)
            pad=box(8.0,6.0,5.0,x,pad_y,-80.0)
            hole=cq.Solid.makeCylinder(2.0,2.0,
                 cq.Vector(x+4.0,face_y,-77.5),pocket_dir)
            pad=pad.rotate((0,axis_y,d.hinge_z),(1,axis_y,d.hinge_z),unwind)
            hole=hole.rotate((0,axis_y,d.hinge_z),(1,axis_y,d.hinge_z),unwind)
            panel=panel.fuse(pad).cut(hole)
    # Replaceable-pin hinge knuckles. Ownership alternates along X.
    for seam_i,edge_y in enumerate(d.seam_y):
        if index not in (seam_i,seam_i+1): continue
        left=index==seam_i
        step=d.knuckle_length+d.knuckle_gap
        active=d.knuckle_margin+(d.knuckle_count-1)*step+d.knuckle_length
        panel=panel.cut(cylinder(d.bore_diameter/2,active-d.knuckle_margin,
                                  d.knuckle_margin,edge_y,d.hinge_z))
        for k in range(d.knuckle_count):
            x=d.knuckle_margin+k*step
            owns=(k%2==0)==left
            if owns:
                panel=panel.fuse(cylinder(d.barrel_diameter/2,d.knuckle_length,x,edge_y,d.hinge_z))
                lug_y=edge_y-2.4 if left else edge_y
                panel=panel.fuse(box(d.knuckle_length,2.4,d.board_skin/2,
                                     x,lug_y,0))
                panel=panel.cut(cylinder(d.bore_diameter/2,d.knuckle_length+.04,
                                         x-.02,edge_y,d.hinge_z))
            else:
                panel=panel.cut(cylinder(d.barrel_diameter/2+.2,d.knuckle_length+.1,
                                         x-.05,edge_y,d.hinge_z))
    return panel.clean()

def pin(seam_i,d=D):
    return cylinder(d.pin_diameter/2,
                    (d.knuckle_count-1)*(d.knuckle_length+d.knuckle_gap)+d.knuckle_length,
                    d.knuckle_margin,d.seam_y[seam_i],d.hinge_z)

def posed(section,index,angle,d=D):
    # Positive angle folds wings *away* from play face and around storage.
    if index==1:return section
    hinge_y=d.seam_y[0 if index==0 else 1]
    a=angle if index==0 else -angle
    return section.rotate((0,hinge_y,d.hinge_z),(1,hinge_y,d.hinge_z),a)

def assembly(angle=0,d=D):
    return [posed(board_section(i,d),i,angle,d) for i in range(3)]

def piece_envelopes(channel_index,d=D):
    """21 flat stones and one capstone inside one integral channel."""
    if channel_index not in (0,1): raise ValueError(channel_index)
    y0=(50.0,173.0)[channel_index]
    flats=[box(8.0,20.0,20.0,4.2+8.0*i,y0+1.5,-21.5)
           for i in range(21)]
    capstone=cylinder(d.rook_diameter_max/2,d.rook_length,
                      172.5,y0+12.5,-12.5)
    return flats+[capstone]

if __name__=='__main__':
    for i,s in enumerate(assembly()):
        b=s.BoundingBox()
        print(i,'valid',s.isValid(),'solids',len(s.Solids()),'bounds',
              tuple(round(v,2) for v in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)))
