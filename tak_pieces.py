"""Team Cat vs Team Witch Tak pieces, millimetres.

Each team has 21 flat stones (20 x 20 x 8) and one capstone that fits the
well and keystone-recess envelopes modelled in tak_case.py. Both large faces of
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

def cat_capstone():
    """Chubby cat head: wide rounded skull, short wide ears, sleepy face."""
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

def witch_capstone():
    """Witch hat: wide brim, concave crooked cone, bent tip, engraved band+star."""
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

# -------------------------------------------------------------------- teams
def capstone(team): return cat_capstone() if team=='cat' else witch_capstone()

def team_plate(team,columns=7,pitch=22.0):
    """21 flats in a 7 x 3 grid, plus the capstone on its back."""
    stones=[]
    for n in range(21):
        c,r=n%columns,n//columns
        stones.append(flat(team).translate((c*pitch,r*pitch,0)))
    cap=(capstone(team).rotate((0,0,0),(1,0,0),-90)   # face-down print: back on bed
         .translate((columns*pitch+8,pitch,CAP_THICK/2)))
    return stones,cap

if __name__=='__main__':
    for team in ('cat','witch'):
        f=flat(team);c=capstone(team)
        for name,obj in (('flat',f),('capstone',c)):
            bb=obj.val().BoundingBox()
            print(team,name,round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2),
                  'valid',obj.val().isValid(),'vol',round(obj.val().Volume(),1))
