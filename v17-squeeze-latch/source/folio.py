"""Two-piece side-release buckle trial. mm; not yet integrated into case."""
import cadquery as cq
def box(x0,x1,y0,y1,z0,z1):
 return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
def prism(points):
 return cq.Workplane('XY').polyline(points).close().extrude(8).val()
def arm():
 # Long flexible arm, broad pull-bearing shoulder and sloped insertion nose.
 p=box(1.8,3.2,4,29,0,8)
 tooth=prism([(1.8,30),(3.2,30),(3.2,22),(-1.2,22),(-1.2,25.5)])
 return p.fuse(tooth).clean()
def male():
 p=box(0,24,0,5,0,8)
 a=arm();p=p.fuse(a).fuse(a.mirror('YZ',(12,0,0)))
 # Central rigid guide prevents twisting and helps center insertion.
 p=p.fuse(box(10.8,13.2,4,32,0,8))
 # Raised assembly label, outside sliding surfaces.
 label=cq.Workplane('XY').workplane(offset=8).center(12,2.5).text('A',3,.4,combine=False).val()
 return p.fuse(label).clean()
def female():
 p=box(-2,26,15,46,-1,9)
 p=p.cut(box(0,24,14.9,39,-.2,8.2))
 for x0,x1 in ((-2.1,1.0),(23.0,26.1)):
  p=p.cut(box(x0,x1,21.8,30.5,-.1,8.1))
 label=cq.Workplane('XY').workplane(offset=9).center(12,42.5).text('B',3,.4,combine=False).val()
 return p.fuse(label).clean()
