"""Package existing study exports without changing geometry. Units mm."""
from pathlib import Path
import json
import cadquery as cq
import export_utils as e

OUT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 if not ok: raise RuntimeError(name)
e.check=check
def part(name,x,y,flat=False):
 s=cq.importers.importStep(str(OUT/'models'/f'{name}.step')).val()
 if flat:s=s.rotate((0,0,0),(1,0,0),90)
 b=s.BoundingBox()
 return name,s.translate((x-b.xmin,y-b.ymin,-b.zmin))
def plate(name,items):
 for i,(label,s) in enumerate(items):
  a=s.BoundingBox()
  check(label+' within bed',a.xmin>=3.99 and a.ymin>=3.99 and a.xmax<=252 and a.ymax<=252 and a.zmin>=-1e-6)
  for label2,t in items[i+1:]:
   b=t.BoundingBox()
   gap=max(b.xmin-a.xmax,a.xmin-b.xmax,b.ymin-a.ymax,a.ymin-b.ymax)
   check(label+' separated from '+label2,gap>=3.99,round(gap,3))
 e.plate(name,items)
 return items

board=[part('board-left',4,4),part('board-right',110,4),part('rear-cap-compartment',4,225.8)]
trial=[part(n,x,225.8,True) for n,x in [('latch-mount',100),('latch-lever',120),('latch-hook',132),('latch-keeper',145)]]
plate('01-boards-cap-compartment-and-latch-trial',board+trial)
plate('02-drawer-housings',[part('housing-left',4,4),part('housing-right',110,4)])
plate('03-piece-drawers',[part('drawer-left',4,4),part('drawer-right',96,4)])
plate('04-latch-trial-only',[part(n,x,4,True) for n,x in [('latch-mount',4),('latch-lever',24),('latch-hook',36),('latch-keeper',49)]])
(OUT/'reports'/'combined-plates.json').write_text(json.dumps({'bed_mm':[256,256],'checks':checks,'limitations':['Generic unsliced 3MF. No slicer profile or supports assigned.','Full case remains an incomplete motion study, not a print release.','Steel hinge axles are hardware reference models and are intentionally excluded.','Plate 04 duplicates latch parts on plate 01; print only one copy.']},indent=2))
print('Four combined 3MF files written; plate 04 is an optional duplicate latch-only trial.')
