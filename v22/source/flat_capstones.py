"""V22 single-piece Cat/Witch capstones: flat in storage and during play, mm."""
from functools import lru_cache
import cadquery as cq
BODY_H=6.8
HEIGHT=8.0
ENVELOPE=(26.0,20.0,HEIGHT)

def union(*shapes):
 out=shapes[0]
 for shape in shapes[1:]:out=out.fuse(shape)
 return out.clean()

def raised_polygon(points):
 return cq.Workplane('XY').workplane(offset=BODY_H-.02).polyline(points).close().extrude(HEIGHT-BODY_H+.02).val()

def bar(x,y,length,width,angle=0):
 s=cq.Workplane('XY').box(length,width,HEIGHT-BODY_H+.02,centered=(True,True,False)).edges('|Z').fillet(width*.4).val()
 return s.rotate((0,0,0),(0,0,1),angle).translate((x,y,BODY_H-.02))

@lru_cache(None)
def capstone(team):
 if team=='cat':
  outline=[(-12,-5),(-11,0),(-12.5,9),(-5.4,5.8),(-2,7),(2,7),(5.4,5.8),(12.5,9),(11,0),(12,-5),(7.2,-9.3),(-7.2,-9.3)]
  details=[bar(-4.1,.5,4.2,1.5,-15),bar(4.1,.5,4.2,1.5,15),raised_polygon([(-1.9,-2),(1.9,-2),(0,-4.1)]),bar(-7.7,-3.2,3.7,1.2,10),bar(7.7,-3.2,3.7,1.2,-10)]
 elif team=='witch':
  outline=[(-13,-9.5),(13,-9.5),(13,-6.2),(5,-5.4),(1.5,5.2),(5.5,6.5),(-2.6,10),(-4.2,3.6),(-7,-5.4),(-13,-6.2)]
  details=[raised_polygon([(-5.1,-4.7),(4.4,-4.7),(3.6,-2.4),(-4.4,-2.4)]),raised_polygon([(-1.2,-.8),(-.3,1.2),(1.6,2.1),(-.3,3),(-1.2,5),(-2.1,3),(-4,2.1),(-2.1,1.2)])]
 else:raise ValueError(team)
 body=cq.Workplane('XY').polyline(outline).close().extrude(BODY_H).edges('|Z').fillet(.6).val()
 # Clip raised detail to the silhouette; each remains fused through the top.
 keep=cq.Workplane('XY').polyline(outline).close().extrude(HEIGHT+.01).val()
 return union(body,*[d.intersect(keep) for d in details]).clean()
