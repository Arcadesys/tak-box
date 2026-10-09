"""Team Cat vs Team Witch Tak pieces, millimetres.

Each team has 21 flat stones (20 x 20 x 8) and one pawn capstone that fits the
well and keystone-recess envelopes modelled in tak_case.py (round, D19.8 x 25.4). Both large faces of
every piece carry the team emblem, recessed 0.6 mm, so a stone reads the same
lying flat, flipped over, or standing as a wall.
"""
import cadquery as cq

FLAT=(20.0,20.0,8.0)
ENGRAVE=0.6
CAP_WIDTH=19.4     # keystone envelope is 19.8 wide, 25.4 long
CAP_HEIGHT=25.4
CAP_THICK=12.0
CAP_ENGRAVE=0.6

# ---------------------------------------------------------------- 2D emblems
# A spec is (recess primitives, raised-island primitives). Primitives are
# ('poly', points) or ('circ', cx, cy, r) in emblem coordinates.

def scaled(prims,s):
    out=[]
    for p in prims:
        if p[0]=='poly': out.append(('poly',[(x*s,y*s) for x,y in p[1]]))
        else: out.append(('circ',p[1]*s,p[2]*s,p[3]*s))
    return out

def cat_emblem(s):
    recess=[('circ',0,-0.5,4.6),
            ('poly',[(-0.6,2.6),(-4.7,0.6),(-3.9,5.4)]),
            ('poly',[(0.6,2.6),(4.7,0.6),(3.9,5.4)])]
    keep=[('circ',-1.9,-0.2,0.95),('circ',1.9,-0.2,0.95),
          ('poly',[(-0.8,-1.9),(0.8,-1.9),(0,-2.8)])]
    return scaled(recess,s),scaled(keep,s)

def witch_emblem(s):
    recess=[('poly',[(-7,-5.2),(7,-5.2),(7,-3.6),(-7,-3.6)]),
            ('circ',-7,-4.4,0.8),('circ',7,-4.4,0.8),
            ('poly',[(-4.4,-3.6),(4.4,-3.6),(2.5,1.0),(2.0,4.0),(4.6,6.4),
                     (-0.2,5.2),(-1.6,1.4),(-2.8,-1.4)])]
    keep=[('poly',[(-5,-3.6),(5,-3.6),(5,-2.2),(-5,-2.2)])]
    return scaled(recess,s),scaled(keep,s)

def prims_solid(prims,make_wp,length,mirror):
    out=None
    for p in prims:
        wp=make_wp()
        if p[0]=='poly':
            pts=[(-x if mirror else x,y) for x,y in p[1]]
            shape=wp.polyline(pts).close().extrude(length)
        else:
            shape=wp.moveTo(-p[1] if mirror else p[1],p[2]).circle(p[3]).extrude(length)
        out=shape if out is None else out.union(shape)
    return out

def emblem_cutter(spec,make_wp,length,mirror):
    recess,keep=spec
    cutter=prims_solid(recess,make_wp,length,mirror)
    if keep:cutter=cutter.cut(prims_solid(keep,make_wp,length,mirror))
    return cutter

# --------------------------------------------------------------------- flats
def flat(team):
    w,d,h=FLAT
    body=(cq.Workplane('XY').box(w,d,h,centered=(True,True,False))
          .edges('|Z').fillet(2.0).faces('>Z or <Z').edges().chamfer(0.6))
    spec=cat_emblem(1.25) if team=='cat' else witch_emblem(1.2)
    top=emblem_cutter(spec,lambda:cq.Workplane('XY',origin=(0,0,h-ENGRAVE)),
                      ENGRAVE+0.1,False)
    bottom=emblem_cutter(spec,lambda:cq.Workplane('XY',origin=(0,0,-0.1)),
                         ENGRAVE+0.1,True)
    return body.cut(top).cut(bottom)

# ----------------------------------------------------------------- capstones
def slab(profile):
    """Extrude an XZ-plane profile CAD object symmetrically in Y."""
    return profile.extrude(CAP_THICK/2,both=True)

def xz(): return cq.Workplane('XZ')

def cat_capstone_slab():
    """Superseded flat slab capstone, kept for reference."""
    body=xz().center(0,9.5).rect(CAP_WIDTH,19).extrude(CAP_THICK/2,both=True)
    body=body.edges('|Y').edges('>Z').fillet(7.0)
    body=body.edges('|Y').edges('<Z').fillet(2.5)
    for sx in (-1,1):
        ear=(xz().polyline([(sx*0.6,17.0),(sx*9.3,13.5),(sx*6.6,CAP_HEIGHT+1.9)])
             .close().extrude(CAP_THICK/2,both=True).edges('|Y').fillet(1.6))
        body=body.union(ear)
    for r in (1.4,1.0,0.6):
        try: body=body.faces('>Y or <Y').edges().fillet(r);break
        except Exception: continue
    face=([('circ',-3.6,12.8,1.4),('circ',3.6,12.8,1.4),
           ('poly',[(-1.2,10.0),(1.2,10.0),(0,8.6)]),
           ('poly',[(-8.6,11.2),(-5.2,11.6),(-5.2,10.8)]),
           ('poly',[(8.6,11.2),(5.2,11.6),(5.2,10.8)]),
           ('poly',[(-8.2,8.8),(-5.2,10.0),(-5.2,9.2)]),
           ('poly',[(8.2,8.8),(5.2,10.0),(5.2,9.2)])],[])
    return engrave_capstone(body,face)

def witch_capstone_slab():
    """Superseded flat slab capstone, kept for reference."""
    brim=(xz().center(0,1.7).rect(CAP_WIDTH,3.4).extrude(CAP_THICK/2,both=True)
          .edges('|Y').fillet(1.5))
    cone=(xz().polyline([(-7.6,2.6),(7.6,2.6),(4.4,10.5),(3.6,16.5),
                         (7.3,CAP_HEIGHT+1.0),(0.4,21.6),(-2.6,15.5),(-4.7,9.0)])
          .close().extrude(CAP_THICK/2,both=True).edges('|Y').fillet(0.9))
    body=brim.union(cone)
    for r in (1.2,0.8,0.5):
        try: body=body.faces('>Y or <Y').edges().fillet(r);break
        except Exception: continue
    star=[(0,-4.2),(1.1,-1.1),(4.2,0),(1.1,1.1),(0,4.2),(-1.1,1.1),(-4.2,0),(-1.1,-1.1)]
    star=[(x*0.75,y*0.75+14.0) for x,y in star]
    face=([('poly',[(-5.6,4.6),(5.6,4.6),(5.0,6.4),(-5.0,6.4)]),
           ('poly',star)],[])
    return engrave_capstone(body,face)

def engrave_capstone(body,spec):
    t=CAP_THICK/2
    front=emblem_cutter(spec,lambda:cq.Workplane('XZ',origin=(0,-t+CAP_ENGRAVE,0)),
                        CAP_ENGRAVE+0.1,False)
    back=emblem_cutter(spec,lambda:cq.Workplane('XZ',origin=(0,t+0.1,0)),
                       CAP_ENGRAVE+0.1,True)
    return body.cut(front).cut(back)

# ------------------------------------------------------------- pawn capstones
# Revolved about Z, so they fit the round keystone envelope (D19.8 x 25.4) in
# any roll. Overhangs stay at or above 45 deg from the bed, so each prints
# upright on its base with no supports.
PAWN_R=9.7        # base radius (envelope radius is 9.9)
PAWN_H=CAP_HEIGHT
PAWN_DEPTH=0.5    # face / hat engraving depth, measured on the surface
FRONT_HALF=(cq.Workplane('XY').box(30,10,40,centered=(True,False,True))
            .translate((0,-10,0)))                       # keeps the -Y face only

def revolve_profile(pts):
    """Revolve an (r, z) polygon 360 deg about the Z axis."""
    return cq.Workplane('XZ').polyline(pts).close().revolve(360,(0,0,0),(0,1,0))

def sphere(r,z):
    return cq.Workplane('XY').sphere(r).translate((0,0,z))

def pawn_base_pts():
    """(r, z) outline from the axis up: foot, flare, waist, collar, neck."""
    flare=[(9.3,2.7),(8.0,3.2),(6.2,4.2),(4.6,6.0),(3.7,7.0)]
    return ([(0,0),(9.3,0),(PAWN_R,0.5),(PAWN_R,2.0)]+flare+
            [(5.2,8.5),(5.6,9.0),(5.2,9.5),(3.4,9.8)])

def pawn_base():
    return revolve_profile(pawn_base_pts()+[(0,9.8)])

def cat_capstone():
    """Cat pawn: pawn foot and collar, chubby round head with two conical
    ears and a sleepy engraved face."""
    HEAD_R,HEAD_Z=7.6,17.0
    # chin cone at 45 deg so the head grows out of the neck without overhang
    chin=revolve_profile([(0,9.6),(3.4,9.6),(3.4,9.8),(5.37,11.63),(3.0,13.0),(0,13.0)])
    head=sphere(HEAD_R,HEAD_Z)
    body=pawn_base().union(chin).union(head)
    for sx in (-1,1):
        ear=cq.Workplane('XY').add(cq.Solid.makeCone(
            2.5,0.6,5.3,pnt=cq.Vector(sx*3.8,0,20.2),      # base buried in the skull
            dir=cq.Vector(sx*0.42,0,0.91)))
        body=body.union(ear)
    # face: closed sleepy eyes, tiny nose, two whiskers per side
    cz=HEAD_Z
    def eye(sx):
        x=sx*2.9
        return (xz().center(x,cz+0.6).circle(1.45).extrude(12,both=True)
                .cut(xz().center(x,cz+1.5).circle(1.45).extrude(12,both=True)))
    parts=[eye(-1),eye(1),
           xz().polyline([(-0.9,cz-1.1),(0.9,cz-1.1),(0,cz-2.1)]).close().extrude(12,both=True)]
    for sx in (-1,1):
        for dz,ang in ((-1.4,0.18),(-2.5,-0.18)):
            x0,x1=sx*4.6,sx*7.2
            z0,z1=cz+dz,cz+dz+ang*(x1-x0)*sx
            parts.append(xz().polyline([(x0,z0-0.3),(x1,z1-0.3),(x1,z1+0.3),(x0,z0+0.3)])
                         .close().extrude(12,both=True))
    face=parts[0]
    for part in parts[1:]: face=face.union(part)
    shell=head.cut(sphere(HEAD_R-PAWN_DEPTH,HEAD_Z))        # uniform-depth skin
    return body.cut(face.intersect(FRONT_HALF).intersect(shell))

def bent_tip():
    """Curled witch-hat tip: lofted circles whose centres drift toward +X."""
    rings=[(20.8,2.6,0.0),(22.6,2.0,0.7),(24.1,1.4,2.0),(PAWN_H,0.8,3.6)]
    wp=cq.Workplane('XY').workplane(offset=rings[0][0]).center(rings[0][2],0).circle(rings[0][1])
    for (z0,_,cx0),(z1,r1,cx1) in zip(rings,rings[1:]):
        wp=wp.workplane(offset=z1-z0).center(cx1-cx0,0).circle(r1)
    return wp.loft(combine=True)

BRIM_R=8.6
def witch_profile(inset=0.0):
    """(r, z) outline: pawn foot, a 45 deg brim flaring straight out of the
    waist, and a tall concave crown up to the bent tip."""
    def s(r): return max(r-inset,0.0) if r>0 else 0.0
    foot=pawn_base_pts()[:9]            # axis, foot, flare down to the waist
    brim_z=7.0+(BRIM_R-3.7)
    crown=[(4.4,16.0),(3.5,18.5),(2.6,20.8)]
    pts=foot+[(BRIM_R,brim_z),(BRIM_R,brim_z+1.1),(5.0,13.9)]+crown+[(0,20.8)]
    return [(s(r),z) for r,z in pts]

def witch_capstone():
    """Witch pawn: waist flares into a 45-degree brim under a tall concave
    crown with a bent tip; band and star engraved on the front."""
    body=revolve_profile(witch_profile()).union(bent_tip())
    inner=revolve_profile(witch_profile(0.6))
    star=[(0,-4.2),(1.1,-1.1),(4.2,0),(1.1,1.1),(0,4.2),(-1.1,1.1),(-4.2,0),(-1.1,-1.1)]
    star=[(x*0.42,y*0.42+18.0) for x,y in star]
    band=[(-8,14.6),(8,14.6),(8,15.3),(-8,15.3)]
    marks=None
    for pts in (star,band):
        prism=xz().polyline(pts).close().extrude(12,both=True)
        marks=prism if marks is None else marks.union(prism)
    crown_zone=revolve_profile([(0,14.0),(6,14.0),(6,20.8),(0,20.8)])
    shell=body.cut(inner).intersect(crown_zone)
    return body.cut(marks.intersect(FRONT_HALF).intersect(shell))

# -------------------------------------------------------------------- teams
def capstone(team): return cat_capstone() if team=='cat' else witch_capstone()

def team_plate(team,columns=7,pitch=22.0):
    """21 flats in a 7 x 3 grid, plus the pawn capstone standing beside them."""
    stones=[]
    for n in range(21):
        c,r=n%columns,n//columns
        stones.append(flat(team).translate((c*pitch,r*pitch,0)))
    cap=capstone(team).translate((columns*pitch+14,pitch,0))   # upright on its base
    return stones,cap

if __name__=='__main__':
    for team in ('cat','witch'):
        f=flat(team);c=capstone(team)
        for name,obj in (('flat',f),('capstone',c)):
            bb=obj.val().BoundingBox()
            print(team,name,round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2),
                  'valid',obj.val().isValid(),'vol',round(obj.val().Volume(),1))
