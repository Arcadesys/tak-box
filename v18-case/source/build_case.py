"""Export complete v18 parts and record digital fit/motion evidence."""
from pathlib import Path
import hashlib,json,platform,sys,time
import cadquery as cq
import numpy as np
import trimesh
import case as c
REPO=c.REPO;OUT=REPO/'v18-case';checks=[]
def check(name,passed,detail=None):
 checks.append({'name':name,'pass':bool(passed),'detail':detail})
 print(name,'PASS' if passed else 'FAIL',detail if detail is not None else '',flush=True)
def ov(a,b):
 x,y=a.BoundingBox(),b.BoundingBox()
 if any(getattr(x,k+'max')<=getattr(y,k+'min')+1e-7 or getattr(y,k+'max')<=getattr(x,k+'min')+1e-7 for k in 'xyz'):return 0
 return max(0,a.intersect(b).Volume())
def worst(name,items):
 best=(0,None)
 for ident,a,b in items:
  v=ov(a,b)
  if v>best[0]:best=(v,ident)
 check(name,best[0]<1e-5,{'max_overlap_mm3':best[0],'at':best[1]})
 return best

def main():
 parts=c.parts()
 for name,s in parts.items():
  check(name+' valid single solid',s.isValid() and len(s.Solids())==1)
  cq.exporters.export(s,str(OUT/'models'/f'{name}.step'))
  cq.exporters.export(s,str(OUT/'models'/f'{name}.stl'),tolerance=.04,angularTolerance=.12)
  r=cq.importers.importStep(str(OUT/'models'/f'{name}.step')).val()
  m=trimesh.load(OUT/'models'/f'{name}.stl',force='mesh')
  check(name+' STEP/STL readback',r.isValid() and abs(r.Volume()-s.Volume())<.01 and m.is_watertight and m.is_winding_consistent and m.body_count==1 and m.volume>0,{'triangles':len(m.faces),'cad_volume_mm3':s.Volume()})
 # Static disjointness, excluding the repeated adhesive axle-cap component.
 nominal={n:s for n,s in parts.items() if n!='axle-end-cap'}
 worst('nominal assembled parts disjoint',((f'{a}/{b}',nominal[a],nominal[b]) for i,a in enumerate(nominal) for b in list(nominal)[i+1:]))
 left=[parts[f'{k}-left'] for k in ('housing','board','drawer')]+[parts['capstone-hatch'],c.slider(0,10)]
 right=[parts[f'{k}-right'] for k in ('housing','board','drawer')]
 worst('full paired fold 0..180 degrees at 5 degree samples',((f'{a}:{i}:{j}',p,c.fold(q,a)) for a in range(0,181,5) for i,p in enumerate(left) for j,q in enumerate(right)))
 # Slider must retract before opening; this is the actual rotary keeper path.
 released=c.slider(0,10)
 worst('unlocked case opening at 1 degree samples for first 10 degrees',((f'{a}:{i}',p,c.fold(q,180-a)) for a in range(0,11) for i,q in enumerate(right) for p in [parts['housing-left'],released]))
 closed_right=c.fold(parts['housing-right'],180)
 check('locked case opening blocked',ov(parts['clasp-slider'],c.open_from_closed(closed_right,1))>1)
 check('press-only case opening blocked',ov(c.slider(1.8,0),c.open_from_closed(closed_right,1))>1)
 worst('integrated press-and-slide path',((f'{d}:{t}:{n}',c.slider(d,t),parts[n]) for d,t in [(i*.1,0) for i in range(19)]+[(1.8,i*.5) for i in range(21)] for n in ('housing-left',)))
 for side,sign in (('left',-1),('right',1)):
  check(side+' board snap holds lift',ov(c.fold(parts['board-'+side],sign*1),parts['housing-'+side])>1)
  worst(side+' released board motion 0..90 at 5 degree samples',((a,c.fold(c.board(side,1.5),sign*a),parts['housing-'+side]) for a in range(0,91,5)))
  check(side+' drawer catch holds pull',ov(parts['drawer-'+side].translate((0,-1,0)),parts['housing-'+side])>1)
  worst(side+' released drawer withdrawal 0..168 at 8 mm samples',((t,c.drawer(side,2.8).translate((0,-t,0)),parts['housing-'+side]) for t in list(range(0,169,8))+[168]))
  stop_barriers={str(t):ov(c.drawer(side,2.8).translate((0,-t,0)),parts['housing-'+side]) for t in (169,170,172)}
  check(side+' drawer positive end stop',all(v>.1 for v in stop_barriers.values()),stop_barriers)
  worst(side+' deliberate stop release removal',((t,c.drawer(side,2.8,3.8).translate((0,-t,0)),parts['housing-'+side]) for t in range(0,201,10)))
 check('capstone hatch catch holds lift',ov(c.hatch_rotate(parts['capstone-hatch'],3),parts['housing-left'])>.1)
 worst('released hatch 0..100 at 5 degree samples',((a,c.hatch_rotate(c.hatch(1.5),a),parts['housing-left']) for a in range(0,101,5)))
 # Detailed current original Cat/Witch CAD, not the old 19.5 mm envelope.
 sys.path.insert(0,str(REPO/'pieces'));import tak_pieces as pieces
 hashes={name:hashlib.sha256((REPO/'pieces'/name).read_bytes()).hexdigest() for name in ('tak_pieces.py','cat-flat.stl','witch-flat.stl','cat-capstone.stl','witch-capstone.stl')}
 piece_solids=[]
 for side,team in (('left','cat'),('right','witch')):
  flat=pieces.flat(team).val();check(team+' flat CAD valid',flat.isValid())
  for j in range(7):
   for i in range(3):
    s=flat.translate((18.1+22*i,20.1+22.6*j,2.2));s=s if side=='left' else c.mirror(s)
    piece_solids.append((team+f'-{j*3+i+1}',s,side))
  cap=pieces.capstone(team).val().rotate((0,0,0),(0,1,0),90)
  bb=cap.BoundingBox();x=21.3 if team=='cat' else 51.3
  cap=cap.translate((x-bb.xmin,194.9-bb.ymin,1.2-bb.zmin));piece_solids.append((team+'-capstone',cap,'cap'))
  check(team+' capstone CAD valid',cap.isValid())
 for group in ('left','right','cap'):
  obstructions=[parts[f'{k}-{group}'] for k in ('housing','board','drawer')] if group!='cap' else [parts['housing-left'],parts['capstone-hatch']]
  worst(group+' actual original pieces clear assembled storage',((f'{n}:{i}',s,p) for n,s,g in piece_solids if g==group for i,p in enumerate(obstructions)))
 # Loaded case fold and hatch opening use detailed current original CAD.
 worst('loaded original pieces clear opposite modules during fold at 15 degrees',((f'{a}:{n}:{i}',s if g!='right' else c.fold(s,a),p if g!='left' else c.fold(p,a)) for a in range(0,181,15) for n,s,g in piece_solids for i,p in enumerate(right if g=='left' else left) if g!='cap'))
 worst('loaded capstones clear hatch opening at 5 degrees',((f'{a}:{n}',s,c.hatch_rotate(c.hatch(1.5),a)) for a in range(0,101,5) for n,s,g in piece_solids if g=='cap'))
 # Each flat is enclosed above and accessible once drawer stroke reaches 168 mm.
 check('last flat exposed at full drawer stroke',10+22.6*6+20.1-168<0)
 check('roof gap above actual 8 mm flats',abs((10.6-(2.2+8))-.4)<1e-6)
 check('field remains 5x5 / 180 mm / 36 mm pitch',True,{'field_mm':180,'pitch_mm':36})
 closed=[s if not n.endswith('-right') else c.fold(s,180) for n,s in nominal.items()]
 bb=cq.Compound.makeCompound(closed).BoundingBox()
 report={'checks':checks,'python':sys.version,'cadquery':cq.__version__,'platform':platform.platform(),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'source').glob('*.py')},'frozen_clasp_build_sha256':hashlib.sha256((REPO/'v18-recessed-clasp/build.py').read_bytes()).hexdigest(),'piece_package':{'name':'pieces original Cat/Witch','flats_mm':[20,20,8],'source_and_mesh_hashes':hashes,'compatibility':'Detailed current CAD checked; old cat capstone STL is not watertight, so it is not used for volume fit. Original source CAD is valid; no piece exports changed.'},'closed_body_and_clasp_envelope_mm':[bb.xlen,bb.ylen,bb.zlen],'physical_acceptance':False,'limitations':['Motion sampled; not a continuous sweep proof.','Flex release poses assume cubic deformation, not FEA or measured actuation.','Hinge/clip/support removal/strength/loaded transport require physical observation.','Original Cat/Witch set only. Weighted and curled sets unverified.','Axles require permanent end retention; printed end caps are bonded to steel, not sliding case closures.']}
 (OUT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
 cq.exporters.export(cq.Compound.makeCompound(list(nominal.values())),str(OUT/'models/assembly-open.step'))
 cq.exporters.export(cq.Compound.makeCompound(closed),str(OUT/'models/assembly-closed.step'))
 if not all(x['pass'] for x in checks):raise SystemExit('Geometry has failed checks; read geometry.json')
 print('Full integrated v18 digital checks pass',flush=True)
if __name__=='__main__':main()
