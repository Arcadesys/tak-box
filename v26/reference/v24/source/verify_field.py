"""Probe the exported board STEP surfaces and recessed 5x5 grid."""
from pathlib import Path
import json
import cadquery as cq
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
boards=[cq.importers.importStep(str(OUT/'models'/f'board-{side}.step')).val() for side in ('left','right')]
def inside(x,y,z):return any(s.isInside(cq.Vector(x,y,z),1e-6) for s in boards)
checks=[]
for i in range(5):
 for j in range(5):
  x=26+36*i+(0.5 if i==2 else 0);y=28+36*j
  checks.append({'name':f'cell-{i+1}-{j+1}-playing-surface','pass':inside(x,y,16.2)})
for k in range(6):
 for x,y in ((8+36*k,28),(26,10+36*k)):
  checks.append({'name':f'grid-recess-{x}-{y}','pass':not inside(x,y,16.1) and inside(x,y,15.7)})
assert all(c['pass'] for c in checks),checks
(OUT/'reports/field.json').write_text(json.dumps({'checks':checks,'field_mm':[180,180],'cells':[5,5],'pitch_mm':36,'grid_groove_mm':{'width':.8,'depth':.6},'note':'Exported STEP material probes; central column has the retained 0.4 mm seam. Use contrasting grid fill for visual access.'},indent=2)+'\n')
print('Exported field PASS: 25 cell surfaces and 12 line-recess probes.')
