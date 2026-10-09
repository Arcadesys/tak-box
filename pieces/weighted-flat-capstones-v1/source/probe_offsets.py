from pathlib import Path
import sys
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'v26/reference/v24/source'))
import flat_capstones as flat
for team in ('cat','witch'):
 shape=flat.capstone(team);face=cq.Workplane(obj=shape).faces('<Z').val();wire=face.outerWire()
 for off in (1.2,1.4,1.8,2.0):
  try:
   wires=wire.offset2D(-off);print(team,off,'wires',len(wires),[(w.isValid(),cq.Face.makeFromWires(w).Area()) for w in wires],flush=True)
  except Exception as e:print(team,off,type(e).__name__,str(e),flush=True)
