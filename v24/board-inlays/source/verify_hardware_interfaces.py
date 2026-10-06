"""Focused checks for the new coloured surfaces against unchanged V24 hardware."""
import hashlib,json
import cadquery as cq
import inlays as c
from geometry_utils import ov
checks=[]
def check(name,value,tolerance=1e-5):
 row={'name':name,'pass':value<tolerance,'value':value};checks.append(row)
 assert row['pass'],row
 print(name,'PASS',flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
boards={s:c.union([cq.importers.importStep(str(c.OUT/'models'/f'board-{s}-{r}.step')).val() for r in c.ROLES]) for s in ('left','right')}
hardware=list(c.case.hook_hardware().values())
check('new board surfaces clear fixed hardware through paired fold',max(ov(c.case.fold(boards['right'],a),h) for a in range(0,181,5) for h in hardware))
check('new board surfaces clear fixed hardware through release and slide',max(ov(c.case.slide(c.complete(s,c.case.BOARD_RELEASE),s,d),h) for s in ('left','right') for d in range(0,107,2) for h in hardware))
check('folding board clears parked side hook',max(ov(c.case.fold(boards['right'],a),c.case.side_hook(90)) for a in range(0,181,5)))
closed=[boards['left'],c.case.fold(boards['right'],180)]
check('closed coloured boards clear full hook rotation',max(ov(b,c.case.side_hook(a)) for b in closed for a in range(0,91,5)))
closed += [c.case.housing('left'),c.case.fold(c.case.housing('right'),180),c.case.tray('left'),c.case.fold(c.case.tray('right'),180),c.case.side_hook(),*hardware]
b=cq.Compound.makeCompound(closed).BoundingBox();envelope=[b.xlen,b.ylen,b.zlen]
check('closed envelope unchanged at 102.5 x 200 x 35 mm',max(abs(x-y) for x,y in zip(envelope,[102.5,200,35])),1e-4)
files=[*list((c.OUT/'models').glob('board-*.step')),c.OUT.parent/'source/case.py',c.OUT/'source/inlays.py',__import__('pathlib').Path(__file__)]
report={'checks':checks,'closed_envelope_mm':envelope,'sources_sha256':{str(p.relative_to(c.REPO)):sha(p) for p in files},'physical_acceptance':False,'sampled_not_continuous':True}
(c.OUT/'reports/hardware-interfaces.json').write_text(json.dumps(report,indent=2)+'\n')
