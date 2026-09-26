"""Hinge alternatives to the sealed filament-pin hinge, as 59 mm test strips.

The current case hinges are walled shut at both ends (nothing is open from
x=0..4.75 or x=200.75..205), so a filament pin cannot be fed in. Two pin-free
options, both printed flat on the bed with the hinge axis horizontal and no
supports:

  pip   print-in-place: each A knuckle grows a cone-tipped pin that sits in a
        conical socket in the neighbouring B knuckle (0.4 mm clearance), so the
        strip comes off the bed already hinged.
  snap  A knuckles carry two Ø3 stub axles ("nipples"); B is a C-clip barrel,
        cut into three fingers, that is pressed straight down onto them.

Geometry, millimetres. Plates are 3 thick and lie on z 0..3. The hinge axis
runs along X at y=0, z=3 (the top face), so folding B upward closes the two top
faces together. Knuckle length 19.4, axial gap 0.4, barrel Ø6. Axis-side
clearance between a plate edge and the other side's barrel is 0.4.
"""
import cadquery as cq

L=19.4          # knuckle length
GAP=0.4         # axial gap between knuckles
R=3.0           # barrel radius
T=3.0           # plate thickness
AX=(0.0,3.0)    # hinge axis (y, z)
PLATE_D=24.0    # plate depth away from the hinge
EDGE=R+0.4      # plate edge distance from the axis
KNUCKLES=3      # A B A
W=KNUCKLES*L+(KNUCKLES-1)*GAP

def kx(k): return k*(L+GAP)     # start x of knuckle k

def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()

def cyl(r,x0,x1,y=AX[0],z=AX[1]):
    return cq.Solid.makeCylinder(r,abs(x1-x0),cq.Vector(min(x0,x1),y,z),cq.Vector(1,0,0))

def cone(r0,r1,x0,x1,y=AX[0],z=AX[1]):
    """Cone along X from x0 (radius r0) to x1 (radius r1); x1 may be < x0."""
    d=1 if x1>x0 else -1
    return cq.Solid.makeCone(r0,r1,abs(x1-x0),cq.Vector(x0,y,z),cq.Vector(d,0,0))

def knuckle(k,side):
    """Barrel + lug to the plate + a 45 deg fillet so it prints flat, no supports."""
    x0=kx(k); x1=x0+L
    s=cyl(R,x0,x1)
    lug=box(x0,x1,-EDGE,0,0,T) if side=='A' else box(x0,x1,0,EDGE,0,T)
    s=s.fuse(lug)
    # solid under the barrel up to its 45-degree tangent point (no overhang)
    s=s.fuse(box(x0,x1,-2.12,2.12,0,0.88))
    return s

def plate(side,depth=PLATE_D):
    if side=='A': return box(0,W,-EDGE-depth,-EDGE,0,T)
    return box(0,W,EDGE,EDGE+depth,0,T)

def mark(shape,n,side,depth):
    """n round dimples (Ø1.4 x 0.6) on the plate's top face label a test variant."""
    y=(-1 if side=='A' else 1)*(EDGE+depth*0.5)
    for i in range(n):
        shape=shape.cut(cq.Solid.makeCylinder(0.7,0.7,cq.Vector(5+3*i,y,T-0.6),cq.Vector(0,0,1)))
    return shape

def build_pip(clr=0.4,depth=PLATE_D,label=0):
    a=plate('A',depth); b=plate('B',depth)
    for k in range(KNUCKLES):
        side='A' if k%2==0 else 'B'
        if side=='A': a=a.fuse(knuckle(k,'A'))
        else: b=b.fuse(knuckle(k,'B'))
    # A knuckles grow a Ø3 pin with a 45-degree tip into the B knuckle's socket
    PIN_R,CLR,CYL_LEN,CONE_LEN=1.5,clr,2.5,1.2
    for k in (0,2):
        x0=kx(k); x1=x0+L
        face,d=(x1,1) if k==0 else (x0,-1)       # face that looks at the B knuckle
        p_end=face+d*CYL_LEN
        a=a.fuse(cyl(PIN_R,face,p_end)).fuse(cone(PIN_R,PIN_R-CONE_LEN,p_end,p_end+d*CONE_LEN))
        bface=face+d*GAP
        s_end=bface+d*(CYL_LEN-GAP)+d*GAP           # socket cylinder ends level with the pin cone start
        b=b.cut(cyl(PIN_R+CLR,bface-d*0.05,s_end))
        b=b.cut(cone(PIN_R+CLR,0.1,s_end,s_end+d*(PIN_R+CLR-0.1)))
    if label: b=mark(b,label,'B',depth)
    return a.clean(),b.clean()

def build_snap(mouth=2.5,depth=PLATE_D,label=0):
    a=plate('A',depth); b=plate('B',depth)
    for k in range(KNUCKLES):
        side='A' if k%2==0 else 'B'
        if side=='A': a=a.fuse(knuckle(k,'A'))
        else: b=b.fuse(knuckle(k,'B'))
    STUB_R,STUB_LEN=1.5,9.3
    for k in (0,2):
        x0=kx(k); x1=x0+L
        face,d=(x1,1) if k==0 else (x0,-1)
        end=face+d*STUB_LEN
        a=a.fuse(cyl(STUB_R,face,end-d*0.5)).fuse(cone(STUB_R,STUB_R-0.5,end-d*0.5,end))
    # B: C-clip barrel. Bore Ø3.4, mouth 2.5 wide facing the bed (-Z), lead-in flare.
    bx0,bx1=kx(1),kx(1)+L
    b=b.cut(cyl(1.7,bx0-0.1,bx1+0.1))
    hw=mouth/2
    b=b.cut(box(bx0-0.1,bx1+0.1,-hw,hw,-0.1,AX[1]))
    flare=(cq.Workplane('YZ').polyline([(-hw-1.05,-0.1),(hw+1.05,-0.1),(hw,1.2),(-hw,1.2)]).close()
           .extrude(L+0.2).translate((bx0-0.1,0,0)).val())
    b=b.cut(flare)
    # relief slits split the clip into three fingers so each arm flexes on its own
    fw=(L-2*0.8)/3
    for i in (1,2):
        sx=bx0+i*fw+(i-1)*0.8
        b=b.cut(box(sx,sx+0.8,-R-0.2,0.3,-0.1,2*R+0.2))
    if label: b=mark(b,label,'B',depth)
    return a.clean(),b.clean()

def rotate_b(shape,deg):
    return shape.rotate(cq.Vector(0,AX[0],AX[1]),cq.Vector(1,AX[0],AX[1]),deg)

def sweep(a,b,label,step=10,limit=110):
    worst=0.0
    for deg in range(0,limit+1,step):
        v=a.intersect(rotate_b(b,deg)).Volume()
        worst=max(worst,v)
    print(label,'A/B overlap over 0..%d deg: max %.4f mm3'%(limit,worst))
    return worst

if __name__=='__main__':
    for name,fn in (('pip',build_pip),('snap',build_snap)):
        a,b=fn()
        for n,s in (('A',a),('B',b)):
            bb=s.BoundingBox()
            print(name,n,'valid',s.isValid(),'size %.1f x %.1f x %.1f'%(bb.xlen,bb.ylen,bb.zlen),'vol %.0f'%s.Volume())
        sweep(a,b,name)
