"""Export Team Cat / Team Witch pieces: single-part STL+STEP and print plates."""
from pathlib import Path
import cadquery as cq
import tak_pieces as p

OUT=Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)

for team in ('cat','witch'):
    for name,obj in (('flat',p.flat(team)),('capstone',p.capstone(team))):
        assert obj.val().isValid()
        bb=obj.val().BoundingBox()
        if name=='capstone': assert bb.xlen<=19.8 and bb.ylen<=19.8 and bb.zlen<=25.41,bb  # D19.8 x 25.4 keystone
        cq.exporters.export(obj,str(OUT/f'{team}-{name}.stl'),tolerance=.02,angularTolerance=.1)
        cq.exporters.export(obj,str(OUT/f'{team}-{name}.step'))
    stones,cap=p.team_plate(team)
    plate=cq.Compound.makeCompound([s.val() for s in stones]+[cap.val()])
    bb=plate.BoundingBox()
    assert bb.xlen<256 and bb.ylen<256
    cq.exporters.export(cq.Workplane().add(plate),str(OUT/f'{team}-print-plate.stl'),
                        tolerance=.02,angularTolerance=.1)
    print(team,'plate',round(bb.xlen,1),round(bb.ylen,1),round(bb.zlen,1))
