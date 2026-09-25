"""Crop the real lid/hinge/keystone geometry into a small print-first sample."""
from pathlib import Path
import cadquery as cq
import tak_case as m

HERE=Path(__file__).resolve().parent
OUT=HERE/'fit-coupon'
OUT.mkdir(exist_ok=True)
shell,lid=m.lid_pair(0)
crop=m.box(45,83,30,160,-2,-21)
shell=shell.intersect(crop).clean()
lid=lid.intersect(crop).clean()
pin=m.cylinder(m.D.pin_diameter/2,45,160,0,1)

def print_pose(shape,face_down=False):
    if face_down:shape=shape.rotate((0,0,0),(1,0,0),180)
    return shape.translate((0,0,-shape.BoundingBox().zmin))

parts={'well-end-shell':print_pose(shell),
       'lift-up-lid':print_pose(lid,True),
       'lid-hinge-pin':print_pose(pin)}
for name,shape in parts.items():
    assert shape.isValid() and len(shape.Solids())==1,name
    cq.exporters.export(shape,str(OUT/f'{name}.stl'),tolerance=.08,angularTolerance=.1)
    b=shape.BoundingBox()
    print(name,[round(v,2) for v in (b.xlen,b.ylen,b.zlen)])
