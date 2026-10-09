"""Bounded continuous-filament motion assessment, not printable geometry."""
from pathlib import Path
import sys,json,math,hashlib,subprocess
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle
OUT=Path(__file__).resolve().parent
REF=OUT.parent/'reference/v24/source'
sys.path.insert(0,str(REF))
import case as c
from geometry_utils import ov
FACE=16.5; AXIS=17.5; RADIUS=1.75/2
D=9.5; Z=13.; A=np.array([98-D/2,Z]);B=np.array([98+D/2,Z])
# Convex hull bounds enclose the V24 playing body and raised outer lip.
L=np.array([[0,11.8],[97.8,11.8],[97.8,16.5],[1.6,17.5],[0,17.5]])
R=L.copy();R[:,0]=196-R[:,0];R=R[::-1]
WAYPOINTS=[(0,0),(0,-30),(90,-30),(90,180)]
def rot(a):
 t=math.radians(a);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def pose(alpha,phi):return (R-B)@rot(phi).T+A+rot(alpha)@np.array([D,0.])
def separate(a,b,margin=.10):
 for poly in (a,b):
  for edge in np.roll(poly,-1,axis=0)-poly:
   n=np.array([-edge[1],edge[0]]);n/=np.linalg.norm(n)
   x=a@n;y=b@n
   if x.max()+margin<=y.min() or y.max()+margin<=x.min():return True
 return False
def main():
 checks=[]
 def check(name,ok,detail=None):
  checks.append(dict(name=name,passed=bool(ok),detail=detail));assert ok,(name,detail)
 left=c.board('left');right=c.board('right')
 check('source axis and playing-face assumptions',c.base.AX==(98.,17.5) and left.BoundingBox().zmax==17.5)
 single=[]
 for label,z in [('current',17.5),('flush_filament',15.625),('one_mm_roof',14.625)]:
  q=right.rotate((98,0,z),(98,1,z),-180)
  collision=ov(left,q)
  entry=dict(name=label,axis_z_mm=z,filament_top_above_face_mm=z+RADIUS-FACE,closed_face_gap_mm=2*(z-FACE),actual_board_overlap_mm3=collision)
  single.append(entry)
  check(label+' expected fixed-axis outcome',collision<1e-5 if label=='current' else collision>1,entry)
 # Bound test for the double-axis board-only path. No knuckle/spine body is assumed.
 check('two-axis closed playing-face gap',abs(D-2*(FACE-Z)-2.5)<1e-9)
 for start,end in zip(WAYPOINTS,WAYPOINTS[1:]):
  count=int(max(abs(start[0]-end[0]),abs(start[1]-end[1]))*4)
  for i in range(count+1):
   t=i/count;alpha=start[0]+t*(end[0]-start[0]);phi=start[1]+t*(end[1]-start[1])
   check(f'board hull alpha {alpha:.2f} phi {phi:.2f}',separate(L,pose(alpha,phi)),dict(spine_deg=alpha,right_board_world_deg=phi))
 closed=pose(90,180)
 check('closed board X alignment',abs(closed[:,0].min())<1e-9 and abs(closed[:,0].max()-97.8)<1e-9)
 # Verify the proposed axes cannot simply be applied to unchanged V24 case bodies.
 body_l=c.housing('left');body_r=c.housing('right');body=[]
 for phi in [0,-1,-2,-3,-4]:
  q=body_r.rotate((float(B[0]),0,Z),(float(B[0]),1,Z),-phi)
  body.append(dict(right_board_world_deg=phi,unchanged_case_overlap_mm3=ov(body_l,q)))
 check('unchanged full case rejects the board-only path',body[0]['unchanged_case_overlap_mm3']<1e-5 and body[2]['unchanged_case_overlap_mm3']>1,body)
 plt.rcParams.update({'font.size':14,'axes.titlesize':17,'axes.labelsize':14})
 fig,axes=plt.subplots(1,2,figsize=(16,7))
 ax=axes[0]
 for poly,col in [(L,'#334f63'),(R,'#b6c8d4')]:ax.add_patch(Polygon(poly,fc=col,ec='#102c40',lw=1.5))
 ax.add_patch(Circle((98,AXIS),RADIUS,fc='#d99200',ec='#513300',lw=2))
 ax.axhline(FACE,color='#111',ls='--',lw=1.5)
 ax.annotate('Continuous filament rises 1.875 mm\nabove the flat playing face',(98,18.375),(87.5,20),arrowprops={'arrowstyle':'->'},fontsize=16)
 ax.set(xlim=(87,109),ylim=(10.5,22),aspect='equal',title='One axle on the current axis',xlabel='Across the centre seam / mm',ylabel='Height / mm')
 ax=axes[1];z=15.625
 q=(R-np.array([98,z]))@rot(180).T+np.array([98,z])
 for poly,col in [(L,'#334f63'),(q,'#b6c8d4')]:ax.add_patch(Polygon(poly,fc=col,ec='#102c40',lw=1.5,alpha=.7))
 ax.axhline(FACE,color='#111',ls='--',lw=1.5)
 ax.annotate('Lowering the fixed axle to make\nfilament flush causes board overlap',(94,15.5),(87.5,20),arrowprops={'arrowstyle':'->'},fontsize=16)
 ax.set(xlim=(87,102),ylim=(10,22),aspect='equal',title='Same axle lowered, case closed',xlabel='Across the centre seam / mm',ylabel='Height / mm')
 fig.suptitle('V25 continuous-filament study — single fixed axle conflicts with flat inward-folding faces',fontsize=20)
 fig.tight_layout();fig.savefig(OUT/'01-single-axis-conflict.png',dpi=150);plt.close(fig)
 fig,axes=plt.subplots(1,4,figsize=(20,6))
 for ax,(alpha,phi),title in zip(axes,WAYPOINTS,['Open','Tilt moving board outward','Lift on offset spine','Close board inward']):
  q=pose(alpha,phi);bb=A+rot(alpha)@np.array([D,0.])
  for poly,col in [(L,'#334f63'),(q,'#b6c8d4')]:ax.add_patch(Polygon(poly,fc=col,ec='#102c40',lw=1.5))
  ax.plot([A[0],bb[0]],[A[1],bb[1]],'--',color='#a35400',lw=3,label='Axis spacing only')
  for p in [A,bb]:ax.add_patch(Circle(p,RADIUS,fc='#d99200',ec='#513300'))
  bounds=np.concatenate([L,q]);lo=bounds.min(axis=0);hi=bounds.max(axis=0)
  ax.set(xlim=(lo[0]-8,hi[0]+8),ylim=(lo[1]-10,hi[1]+12),aspect='equal',title=title,xlabel='X / mm',ylabel='Z / mm');ax.grid(alpha=.15)
 fig.suptitle('Two-axis board-envelope path — case bodies and hinge/link solids are NOT cleared',fontsize=20)
 fig.tight_layout(rect=(0,0,1,.92));fig.savefig(OUT/'02-board-only-path.png',dpi=150);plt.close(fig)
 report=dict(passed=True,assessment='single fixed axle rejected; two-axis board-only path passes, unchanged case collides',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=OUT,text=True).strip(),reference_v24_revision='8085e9d79ffff3c69f07a1cca67595994237869e',source_case_sha256=hashlib.sha256((REF/'case.py').read_bytes()).hexdigest(),study_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,cadquery=cq.__version__,units='mm',single_axis=single,two_axis=dict(axis_spacing_mm=D,axis_z_mm=Z,filament_d_mm=1.75,closed_face_gap_mm=2.5,waypoints=WAYPOINTS,sample_step_deg=.25,separating_axis_margin_mm=.1,full_case_integration=False,hinge_link_solids_checked=False),unchanged_case_probes=body,checks=checks,physical_acceptance=False,printable_release=False,printer_started=False)
 (OUT/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS',len(checks),'study checks; single axle rejected; two-axis board path passes; existing case collision confirmed',flush=True)
if __name__=='__main__':main()
