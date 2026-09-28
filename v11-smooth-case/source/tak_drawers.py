"""Inward-fold Tak board with two lift-off player magazines. Units: mm.

The board is three flat-backed PIP sections carrying an unobstructed 205 mm
play field. Two open-top magazines lift in local +Z from keyed perimeter posts;
when the board folds inward to -90 degrees their full-height rims form the
protective inner case. Hinges and guide posts are outside the playing field.
"""
from pathlib import Path
from functools import lru_cache
import math,struct
import cadquery as cq

ROOT=Path(__file__).resolve().parent
S=205.0
SEAMS=(82.0,123.0)
TOP=4.0
GRID_TOP=4.8
HINGE_Z=5.2
HINGE_R=3.0
HINGE_GUARD_R=5.2
PIN_R=1.5
PIN_CLR=.4
PANEL_GAP=.4
TRAY_BOTTOM=5.4
TRAY_FLOOR_TOP=7.0
TRAY_RIM_TOP=25.0
TRAY_WALL=1.2
TRAY_LIFT=4.5
FLAT_X=tuple(15.25+22.5*i for i in range(7))
FLAT_Y=(14.5,40.5,66.5)
FLAT_BOTTOM=TRAY_FLOOR_TOP
CAPSTONE_CENTER=(184.5,40.5)
CAPSTONE_X=(172.0,197.0)
CAPSTONE_CRADLE_TOP=7.6
CAPSTONE_DIMS={'cat':(25.0,15.5363903,15.54206848),
               'witch':(25.0,17.10588837,17.28754234)}
FITS={'A':.25,'B':.35,'C':.45}
KEY_FIT='B'
CLOSURE_FIT='B'
HINGE_LEFT=(-18.4,-9.4,-9.0,0.0)
HINGE_RIGHT=(205.0,214.0,214.4,223.4)
POST_Y=(13.0,69.0)
POST_HEAD_HALF=3.2
POST_NECK_HALF=2.0
POST_HEIGHT=8.0
CASE_X=(-20.4,225.4)
WING_CHEEK_Y=(0.0,72.0)
CHEEK_TOP=25.0
FRONT_RETURN=2.2
PRESS_Y=(34.0,52.0)
PRESS_Z=(11.0,23.5)
TONGUE_Y=(36.0,50.0)
TONGUE_X=(221.0,222.8)
PRESS_STOP_X=(219.8,220.2)
PRESS_TRAVEL=.8
RECEIVER_Y=(155.0,169.0)
RECEIVER_Z=(23.5,24.7)


def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()

def cyl(r,x0,x1,y,z):
    return cq.Solid.makeCylinder(r,x1-x0,cq.Vector(x0,y,z),cq.Vector(1,0,0))

def cone(r0,r1,x0,x1,y,z):
    return cq.Solid.makeCone(r0,r1,abs(x1-x0),cq.Vector(x0,y,z),cq.Vector(1 if x1>x0 else -1,0,0))

def posed(s,index,angle):
    if index==1:return s
    axis=SEAMS[0 if index==0 else 1]
    a=angle if index==0 else -angle
    return s.rotate((0,axis,HINGE_Z),(1,axis,HINGE_Z),a)

def _hinge_barrel(stock,x0,x1,axis,side):
    """Ø6 pin-bearing core under a smooth Ø10.4 protective heel fairing."""
    p=cyl(HINGE_R,x0,x1,axis,HINGE_Z).fuse(
        cyl(HINGE_GUARD_R,x0,x1,axis,HINGE_Z))
    p=p.fuse(box(x0,x1,axis-3.0,axis+3.0,0,HINGE_Z-HINGE_R+.4))
    if side<0:
        p=p.fuse(box(x0,x1,axis-7.5,axis-4.8,0,HINGE_Z))
        arm=box(min(x0,-.1 if x1<=0 else 204),max(x1,1.0 if x1<=0 else 205.1),axis-7.5,axis-5.6,0,TOP)
    else:
        p=p.fuse(box(x0,x1,axis+4.8,axis+7.5,0,HINGE_Z))
        arm=box(min(x0,-.1 if x1<=0 else 204),max(x1,1.0 if x1<=0 else 205.1),axis+5.6,axis+7.5,0,TOP)
    return stock.fuse(p).fuse(arm)

def _male_pin(stock,face,d,axis):
    end=face+d*2.5
    return stock.fuse(cyl(PIN_R,min(face,end),max(face,end),axis,HINGE_Z)).fuse(
        cone(PIN_R,.3,end,end+d*1.2,axis,HINGE_Z))

def _female_socket(stock,mouth,d,axis):
    end=mouth+d*2.5
    stock=stock.cut(cyl(PIN_R+PIN_CLR,min(mouth-d*.05,end),max(mouth-d*.05,end),axis,HINGE_Z))
    return stock.cut(cone(PIN_R+PIN_CLR,.1,end,end+d*1.8,axis,HINGE_Z))

def _hinge(stock,axis,side,wing_owner):
    """One male wing and female center knuckle at each x end.

    Opposite-facing pins at the two ends capture a rigid wing axially.
    """
    for end in ('left','right'):
        if end=='left':
            wx0,wx1,cx0,cx1=HINGE_LEFT
            bx0,bx1=(wx0,wx1) if wing_owner else (cx0,cx1)
            face,mouth,d=wx1,cx0,1
        else:
            cx0,cx1,wx0,wx1=HINGE_RIGHT
            bx0,bx1=(wx0,wx1) if wing_owner else (cx0,cx1)
            face,mouth,d=wx0,cx1,-1
        stock=_hinge_barrel(stock,bx0,bx1,axis,side)
        stock=_male_pin(stock,face,d,axis) if wing_owner else _female_socket(stock,mouth,d,axis)
    return stock.clean()

def _post(stock,xside,y):
    """Vertical T key outside the x play-field edge; tray lifts off +Z."""
    if xside=='left':
        foot=box(-3,1,y-2,y+2,0,TOP)
        neck=box(-3,0,y-POST_NECK_HALF,y+POST_NECK_HALF,0,POST_HEIGHT)
        head=box(-7,-3,y-POST_HEAD_HALF,y+POST_HEAD_HALF,0,POST_HEIGHT)
        lx0,lx1=-8,-.2
    else:
        foot=box(204,208,y-2,y+2,0,TOP)
        neck=box(205,208,y-POST_NECK_HALF,y+POST_NECK_HALF,0,POST_HEIGHT)
        head=box(208,212,y-POST_HEAD_HALF,y+POST_HEAD_HALF,0,POST_HEIGHT)
        lx0,lx1=205.2,213
    # Two shoulders support the tray ear at 5.4 without touching the field.
    lo=box(lx0,lx1,y-5.4,y-3.0,TOP,TRAY_BOTTOM)
    hi=box(lx0,lx1,y+3.0,y+5.4,TOP,TRAY_BOTTOM)
    return stock.fuse(foot).fuse(neck).fuse(head).fuse(lo).fuse(hi)

def _rounded_wall(x0,x1,y0,y1,z1):
    # Fillet the upright corners and bevel both horizontal rims.  This yields
    # the same soft envelope without zero-length corner facets in the STL.
    return (cq.Workplane('XY').box(x1-x0,y1-y0,z1,centered=False)
            .translate((x0,y0,0)).edges('|Z').fillet(.7)
            .faces('>Z').edges().chamfer(.45)
            .faces('<Z').edges().chamfer(.35).val())

def _rounded_backing(x0,x1,y0,y1):
    p=(cq.Workplane('XY').box(x1-x0,y1-y0,TOP,centered=False)
       .translate((x0,y0,0)).edges('|Z').fillet(1.4))
    return p.faces('<Z').edges().chamfer(.35).val()

def _left(shape):
    return shape.mirror('YZ',(S/2,0,0))

def _press_window():
    # The outside opening has generous thumb area and rounded internal corners.
    return (cq.Workplane('XY').box(3.0,18.0,12.5,centered=False)
            .translate((223.0,34.0,11.0)).edges('|X').fillet(1.4).val())

def _tongue(tooth_fit):
    """Recessed compliant tongue with a ramped, protected interlock tooth."""
    p=box(*TONGUE_X,*TONGUE_Y,3.6,27.6)
    # The ramp only meets the opposite wall while the wing is being closed.
    tip=223.4+FITS[tooth_fit]
    tooth=(cq.Workplane('XZ',origin=(0,49,0))
           .polyline([(222.7,26.6),(223.0,26.6),(tip,27.05),
                      (tip,27.55),(222.7,27.55)])
           .close().extrude(12).val())
    return p.fuse(tooth).clean()

def _closure_a(p,fit):
    assert fit in FITS
    for mirror in (False,True):
        orient=_left if mirror else (lambda s:s)
        # A hard backstop limits thumb travel before the cantilever reaches a key.
        p=p.fuse(orient(box(*PRESS_STOP_X,37,49,4,17)))
        p=p.fuse(orient(_tongue(fit)))
    return p.clean()

def _closure_b(p):
    # Blind pockets leave a 1.2 mm exterior skin; the tooth never sticks out.
    pocket=box(223.0,224.2,*RECEIVER_Y,*RECEIVER_Z)
    for mirror in (False,True):
        p=p.cut(_left(pocket) if mirror else pocket)
    return p.clean()

def closure_tongue(end,fit=None):
    """The two guarded flex members, in open-board coordinates."""
    assert end in ('left','right')
    selected=CLOSURE_FIT if fit is None else fit
    assert selected in FITS
    t=_tongue(selected)
    return _left(t) if end=='left' else t

def wing_released(fit=None,travel=PRESS_TRAVEL):
    """Virtual release pose for clearance checks; printed tongues stay integral."""
    assert 0<=travel<=PRESS_TRAVEL
    selected=CLOSURE_FIT if fit is None else fit
    base=wing(0,selected)
    for end in ('left','right'):
        base=base.cut(closure_tongue(end,selected))
    for end,direction in (('left',1),('right',-1)):
        base=base.fuse(closure_tongue(end,selected).translate((direction*travel,0,0)))
    return base.clean()

def _wing_cheeks(p,index):
    """Rounded end skins, rooted in each panel's plain outside backing."""
    y0,y1=WING_CHEEK_Y if index==0 else (S-WING_CHEEK_Y[1],S)
    for left in (True,False):
        bx0,bx1=(CASE_X[0],1) if left else (204,CASE_X[1])
        wx0,wx1=(CASE_X[0],-18.4) if left else (223.4,CASE_X[1])
        p=p.fuse(_rounded_backing(bx0,bx1,y0,y1))
        # A low back return fills the short broad-side recess above each
        # rounded hinge. It stops before the other panel's fairing sweep.
        rx0,rx1=(-18.45,1) if left else (204,223.45)
        ry0,ry1=(71.8,74.4) if index==0 else (S-74.4,S-71.8)
        p=p.fuse(box(rx0,rx1,ry0,ry1,0,TOP))
        # Make the key shoulder/backing joint volumetric where it meets the
        # backing boundary.  A line-only join leaves a nonmanifold mesh edge.
        for y in (POST_Y if index==0 else tuple(S-u for u in POST_Y)):
            rx0,rx1=(-8,-.2) if left else (205.2,213)
            p=p.fuse(box(rx0,rx1,y-5.5,y+5.5,3.8,4.15))
        wall=_rounded_wall(wx0,wx1,y0,y1,CHEEK_TOP)
        if index==0:
            wall=wall.cut(_left(_press_window()) if left else _press_window()).clean()
            # A shallow bevel avoids a sharp snag edge around the broad mouth.
            outer='<X' if left else '>X'
            wall=cq.Workplane(obj=wall).faces(outer).edges().chamfer(.35).val()
        p=p.fuse(wall)
    return p.clean()

def _front_return(p,index):
    """One broad rounded free-edge wall closes the top of the folded case."""
    wall=_rounded_wall(CASE_X[0],CASE_X[1],-FRONT_RETURN,.2,CHEEK_TOP)
    # Above the board, all of the return stays outside the 205 mm play field.
    wall=wall.cut(box(-.05,S+.05,0,.25,TOP,CHEEK_TOP+.1)).clean()
    if index==2:wall=wall.mirror('XZ',(0,S/2,0))
    return p.fuse(wall).clean()

def _center_guards(p):
    """Low rounded spine cheeks cover both PIP end modules without sweep hit."""
    # Outer y ends coincide with the broad folded wing backs (76.8,128.2),
    # so the spine does not protrude as two feet from the purse silhouette.
    for left in (True,False):
        x0,x1=(CASE_X[0],-18.7) if left else (223.7,CASE_X[1])
        guard=(cq.Workplane('YZ',origin=(x0,0,0))
               .moveTo(82,0).lineTo(123,0)
               .threePointArc((126.676955,1.523045),(128.2,5.2))
               .lineTo(128.2,8.5).lineTo(126,14).lineTo(79,14)
               .lineTo(76.8,8.5).lineTo(76.8,5.2)
               .threePointArc((78.323045,1.523045),(82,0))
               .close().extrude(x1-x0).edges('|X').fillet(.5).val())
        outer='<X' if left else '>X'
        guard=cq.Workplane(obj=guard).faces(outer).edges().chamfer(.3).val()
        p=p.fuse(guard)
        # Central bridge deliberately misses both hinge axes and wing barrels.
        bx0,bx1=(CASE_X[0],1) if left else (204,CASE_X[1])
        p=p.fuse(_rounded_backing(bx0,bx1,93,112))
    return p.clean()

@lru_cache(None)
def wing(index,closure_variant=None):
    assert index in (0,2)
    if index==0:
        p=box(0,S,0,81.8,0,TOP)
        axis=82;side=-1;ys=POST_Y
    else:
        p=box(0,S,123.2,S,0,TOP)
        axis=123;side=1;ys=tuple(S-y for y in POST_Y)
    p=_hinge(p,axis,side,True)
    for y in ys:
        for xside in ('left','right'):p=_post(p,xside,y)
    p=_wing_cheeks(p,index)
    p=_front_return(p,index)
    return _closure_a(p,CLOSURE_FIT if closure_variant is None else closure_variant) if index==0 else _closure_b(p)

@lru_cache(None)
def center():
    p=box(0,S,82.2,122.8,0,TOP)
    p=_hinge(p,82,1,False)
    p=_hinge(p,123,-1,False)
    # Two underside mortises accept zero-gap stop shoes after PIP release.
    # Their bottoms finish flush at z=0 and never touch the playing face.
    for x0,x1 in ((0,5),(200,205)):
        p=p.cut(box(x0,x1,82.2,122.8,-.1,1.2))
    p=_center_guards(p)
    # The broad guard bridge crosses these x strips, so finish the mortises
    # after it is joined.  Its material above z1.2 still ties into the panel.
    for x0,x1 in ((0,5),(200,205)):
        p=p.cut(box(x0,x1,82.2,122.8,-.1,1.2))
    return p.clean()

def stop_shoe(end):
    assert end in ('left','right')
    x0,x1=(0,5) if end=='left' else (200,205)
    return box(x0,x1,81.8,123.2,0,1.2)

@lru_cache(None)
def grid(index):
    name=('grid-a','grid-center','grid-b')[index]
    return cq.importers.importStep(str(ROOT/'references'/(name+'.step'))).val().clean()

def _female_key_void(xside,y):
    # 0.3 mm planar clearance around the structural T post.
    if xside=='left':
        neck=box(-3.3,.3,y-2.3,y+2.3,5.3,9.7)
        head=box(-7.3,-2.7,y-3.5,y+3.5,5.3,9.7)
    else:
        neck=box(204.7,208.3,y-2.3,y+2.3,5.3,9.7)
        head=box(207.7,212.3,y-3.5,y+3.5,5.3,9.7)
    return neck.fuse(head)

def _tray_a(variant='B'):
    assert variant in FITS
    p=box(1,204,1,81,TRAY_BOTTOM,TRAY_FLOOR_TOP)
    # Continuous 18 mm transport rim: no escape-sized finger openings.
    for y0,y1 in ((1,2.2),(79.8,81)):
        p=p.fuse(box(1,204,y0,y1,TRAY_FLOOR_TOP,TRAY_RIM_TOP))
    for x0,x1 in ((1,2.2),(202.8,204)):
        p=p.fuse(box(x0,x1,1,81,TRAY_FLOOR_TOP,TRAY_RIM_TOP))
    # Broad blind grip on the outer x-end wall: no through-hole in transport.
    p=p.cut(box(203.55,204.1,32,50,17,23))
    # Two broad lanes separate rows but do not grip individual flat stones.
    for y in (26.9,52.9):p=p.fuse(box(5,166,y,y+1.2,TRAY_FLOOR_TOP,TRAY_FLOOR_TOP+3))
    # The larger witch capstone is 25 x 17.2875 x 17.1059 sideways.
    for x0,x1,y0,y1 in ((170.8,171.6,31.0,50.0),
                         (197.4,198.2,31.0,50.0),
                         (171.6,197.4,30.7,31.5),
                         (171.6,197.4,49.5,50.3)):
        p=p.fuse(box(x0,x1,y0,y1,TRAY_FLOOR_TOP,CAPSTONE_CRADLE_TOP))
    # Four T-keyed ears carry the tray. Through slots make local +Z lift-off
    # possible without dragging the playing surface.
    for y in POST_Y:
        for xside in ('left','right'):
            x0,x1=(-8,2) if xside=='left' else (203,213)
            ear=box(x0,x1,y-5,y+5,TRAY_BOTTOM,9.6)
            p=p.fuse(ear).cut(_female_key_void(xside,y))
            hx0,hx1=(-6.5,-3.5) if xside=='left' else (208.5,211.5)
            # Only the last ~2.4 mm of vertical seating rubs this small pad.
            p=p.fuse(box(hx0,hx1,y+3.5-FITS[variant],y+3.5,5.6,6.4))
    return p.clean()

@lru_cache(None)
def tray(index,variant=None,closure_variant=None):
    assert index in (0,2)
    key_fit=KEY_FIT if variant is None else variant
    assert key_fit in FITS
    p=_tray_a(key_fit)
    return p if index==0 else p.mirror('XZ',(0,102.5,0))

def lift_tray(shape,index,lift):
    assert index in (0,2) and lift>=0
    return shape.translate((0,0,lift))

def top_assembly():return cq.Compound.makeCompound([wing(0),center(),wing(2)])

def assembly(angle=0,with_trays=True,with_grid=True,with_pieces=False,lift=0,variant=None,closure_variant=None,with_stops=True):
    parts=[]
    if with_stops:parts.extend((stop_shoe('left'),stop_shoe('right')))
    for i in (0,1,2):
        parts.append(posed(center() if i==1 else wing(i,closure_variant),i,angle))
        if with_grid:parts.append(posed(grid(i),i,angle))
        if i!=1 and with_trays:parts.append(posed(lift_tray(tray(i,variant,closure_variant),i,lift),i,angle))
    if with_pieces:
        for i in (0,2):
            for y in FLAT_Y:
                yy=y if i==0 else S-y
                for x in FLAT_X:
                    parts.append(posed(box(x-9.75,x+9.75,yy-9.75,yy+9.75,FLAT_BOTTOM,FLAT_BOTTOM+8),i,angle))
            cy=CAPSTONE_CENTER[1] if i==0 else S-CAPSTONE_CENTER[1]
            _,dy,dz=CAPSTONE_DIMS['cat' if i==0 else 'witch']
            parts.append(posed(box(*CAPSTONE_X,cy-dy/2,cy+dy/2,FLAT_BOTTOM,FLAT_BOTTOM+dz),i,angle))
    return cq.Compound.makeCompound(parts)

def print_pose(shape):
    b=shape.BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))

def mechanical_parts():
    return {'wing-a':wing(0),'center':center(),'wing-b':wing(2),
            'tray-a':tray(0),'tray-b':tray(2),
            'grid-a':grid(0),'grid-center':grid(1),'grid-b':grid(2),
            'stop-shoe-left':stop_shoe('left'),'stop-shoe-right':stop_shoe('right')}
