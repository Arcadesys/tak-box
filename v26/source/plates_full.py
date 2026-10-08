"""Full V26 board and matching capstone plates from exported CAD, mm."""
from pathlib import Path
import sys, json, hashlib
import cadquery as cq
import build as b
import board_plate as bp
import flat_capstones
OUT=Path(__file__).resolve().parents[1]

def main():
    groups=[]
    specifications={}
    for side,x in (('left',7),('right',121)):
        parts={role:cq.importers.importStep(str(OUT/'models'/f'board-{side}-{role}.step')).val() for role in b.ROLES}
        for role,shape in parts.items():
            mesh=bp.mesh(shape)
            path=OUT/'models'/f'board-{side}-{role}.stl'
            mesh.export(path)
            specifications[f'board-{side}-{role}']={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'watertight':True,'mesh_bodies':mesh.body_count}
        groups.append(('board-'+side,parts,(x,7)))
    bp.project('02-V26-FULL-SIZE-FOUR-COLOUR-tab-free-boards',groups)
    items=[]
    for team,x in (('cat',7),('witch',45)):
        shape=flat_capstones.capstone(team)
        bb=shape.BoundingBox()
        shape=b.b.pkg.on_bed(shape.translate((x-bb.xmin,7-bb.ymin,-bb.zmin)))
        label='capstone-'+team
        specifications[label]=b.b.export(label,shape)
        items.append((label,shape))
    b.b.e.plate('03-V26-flat-capstones',items)
    for label,shape in items:
        bb=shape.BoundingBox()
        bp.check(label+' bed bounds',bb.xmin>6.9 and bb.ymin>6.9 and bb.xmax<249 and bb.ymax<249 and abs(bb.zmin)<.002)
    report={'passed':True,'checks':bp.checks+b.checks,'specifications':specifications,'command':[sys.executable,str(Path(__file__).resolve())],
            'board_filament_slots':{role:data[0] for role,data in bp.ROLES.items()},'board_origins_mm':[[7,7],[121,7]],
            'sources_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__).resolve(),OUT/'source/board_plate.py')},
            'physical_acceptance':False,'printer_started':False}
    (OUT/'reports/full-plates.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(bp.checks+b.checks),'full board and capstone plate checks',flush=True)

if __name__=='__main__':main()
