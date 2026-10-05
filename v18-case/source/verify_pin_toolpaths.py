"""Check actual nozzle extrusion centerlines against nominal filament passages."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Rectangle
import cadquery as cq
import case as c
import inspect_case_layers as layers
OUT=c.REPO/'v18-case';regions={}
RP=np.array([[0,0,1],[0,1,0],[-1,0,0]]);I=np.eye(3);RX=np.array([[1,0,0],[0,0,1],[0,-1,0]]);RY=np.array([[0,0,-1],[0,1,0],[1,0,0]])
def placement(part,xy,R):
 s=cq.importers.importStep(str(OUT/'models'/f'{part}.step')).val()
 if np.array_equal(R,RX):s=s.rotate((0,0,0),(1,0,0),-90)
 elif np.array_equal(R,RP):s=s.rotate((0,0,0),(0,1,0),90)
 elif np.array_equal(R,RY):s=s.rotate((0,0,0),(0,1,0),-90)
 b=s.BoundingBox();return np.array([xy[0]-b.xmin,xy[1]-b.ymin,-b.zmin])
def region(plate,label,part,xy,R,start,end,radius=.875):
 d=placement(part,xy,R);a=R@np.array(start)+d;b=R@np.array(end)+d
 regions.setdefault(plate,[]).append((label,a,b,radius))
for side,plate,xy in [('left','01-left-housing-hook-pivot-and-cap-compartment',(10,7)),('right','02-right-housing-and-hook-pin',(10,10))]:
 for a,b in c.base.FAMILIES['tray-'+side]:
  lo,hi=a+.3,b-.3
  if side=='right' and a==0:hi=4.4
  if side=='left' and a==193.2:lo=194.4
  region(plate,'main '+side+f' Y={a}', 'housing-'+side,xy,RX,(98,lo,16.3),(98,hi,16.3))
for a,b in [(0,12),(75,87)]:
 region('01-left-housing-hook-pivot-and-cap-compartment','fixed hatch '+str(a),'housing-left',(10,7),RX,(a+.3,219.8,23.2),(b-.3,219.8,23.2))
for side,xy in [('left',(7,7)),('right',(115,7))]:
 for a,b in c.base.FAMILIES['board-'+side]:
  region('03-board-leaves','board '+side+f' Y={a}','board-'+side,xy,I,(98,a+.3,16.3),(98,b-.3,16.3))
region('05-hatch-hook-and-five-axle-caps','moving hatch','capstone-hatch',(7,7),RY,(14.3,219.8,23.2),(72.7,219.8,23.2))
region('01-left-housing-hook-pivot-and-cap-compartment','hook fixed pivot','housing-left',(10,7),RX,(-2.9,94,7),(.7,94,7))
region('05-hatch-hook-and-five-axle-caps','moving hook','side-hook',(45,7),RP,(-6.5,94,7),(-3.9,94,7))
for i in range(5):
 region('05-hatch-hook-and-five-axle-caps','collar '+str(i+1),'axle-end-cap',(110+12*i,50),I,(0,0,.4),(0,0,3.6))

def hits(P,Q,a,b,radius):
 axis=b-a;length=np.linalg.norm(axis);axis=axis/length
 rel=P-a;delta=Q-P;ax=rel@axis;step=delta@axis
 moving=np.abs(step)>1e-10
 lower=np.zeros(len(P));upper=np.ones(len(P))
 lower[moving]=np.maximum(0,np.minimum(-ax[moving]/step[moving],(length-ax[moving])/step[moving]))
 upper[moving]=np.minimum(1,np.maximum(-ax[moving]/step[moving],(length-ax[moving])/step[moving]))
 valid=(lower<=upper)&(moving|((ax>=0)&(ax<=length)))
 radial=rel-ax[:,None]*axis;dr=delta-step[:,None]*axis
 denom=(dr*dr).sum(1);t=np.zeros(len(P));vary=denom>1e-12
 t[vary]=-(radial[vary]*dr[vary]).sum(1)/denom[vary];t=np.clip(t,lower,upper)
 distance=np.linalg.norm(radial+t[:,None]*dr,axis=1)
 return valid&(distance<radius-.02)

def main():
 report={'scope':'Extrusion centerlines inside a nominal 1.75 mm pin core, cropped at passage ends. No bead-width/force/physical-fit proof.','extruder_offset_mm':layers.NOZZLE_OFFSET,'checks':[]}
 views=[]
 for plate,rows in regions.items():
  path=layers.WORK/(plate+'.gcode');segs=layers.parse(path)
  P=np.array([[pts[0][0],pts[0][1],z] for z,_,pts in segs]);Q=np.array([[pts[1][0],pts[1][1],z] for z,_,pts in segs]);roles=np.array([role for _,role,_ in segs])
  for label,a,b,r in rows:
   levels=np.array(sorted({z for z,_,_ in segs}));z=float(levels[np.argmin(abs(levels-(a[2]+b[2])/2))])
   crop_min=np.minimum(a[:2],b[:2])-3;crop_max=np.maximum(a[:2],b[:2])+3
   subset=[(role,pts) for zz,role,pts in segs if zz==z and np.all(np.maximum(pts[0],pts[1])>=crop_min) and np.all(np.minimum(pts[0],pts[1])<=crop_max)]
   views.append((plate[:2]+' / '+label,z,a,b,r,subset,crop_min,crop_max))
   found=hits(P,Q,a,b,r);types={role:int(np.sum(found&(roles==role))) for role in sorted(set(roles[found]))}
   report['checks'].append({'name':plate+'/'+label,'pass':not bool(found.any()),'start_mm':a.tolist(),'end_mm':b.tolist(),'intrusions_by_role':types,'gcode_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 for page in range((len(views)+5)//6):
  fig,axes=plt.subplots(3,2,figsize=(16,13))
  for ax,row in zip(axes.flat,views[page*6:page*6+6]):
   label,z,a,b,r,subset,lo,hi=row
   for sup,col,style in [(False,'#123957','solid'),(True,'#9a3150','dashed')]:
    ax.add_collection(LineCollection([pts for role,pts in subset if role.startswith('Support')==sup],colors=col,linestyles=style,linewidths=1.2))
   if np.linalg.norm(a[:2]-b[:2])<.01:ax.add_patch(Circle(a[:2],r,fill=False,edgecolor='black',linestyle=':',linewidth=2))
   else:
    lower=np.minimum(a[:2],b[:2]);upper=np.maximum(a[:2],b[:2]);flat=np.argmin(upper-lower);lower[flat]-=r;upper[flat]+=r
    ax.add_patch(Rectangle(lower,*(upper-lower),fill=False,edgecolor='black',linestyle=':',linewidth=2))
   ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_aspect('equal');ax.set_title(f'{label}\nLayer {z:g} mm',fontsize=16);ax.tick_params(labelsize=11)
  for ax in axes.flat[len(views[page*6:page*6+6]):]:ax.set_visible(False)
  fig.suptitle('Filament passages — actual sliced extrusion',fontsize=24)
  fig.text(.5,.02,'Solid: model    Dashed: support    Dotted outline: nominal filament core',ha='center',fontsize=17)
  fig.tight_layout(rect=(0,.05,1,.95));fig.savefig(OUT/'previews'/f'06-pin-passages-{page+1}.png',dpi=130);plt.close(fig)
 report['preview_sheets']=[f'06-pin-passages-{i+1}.png' for i in range((len(views)+5)//6)]
 (OUT/'reports/pin-toolpaths.json').write_text(json.dumps(report,indent=2)+'\n')
 failed=[x for x in report['checks'] if not x['pass']]
 for x in failed:print(x['name'],x['intrusions_by_role'])
 assert not failed,'Pin core obstructed by actual sliced extrusion; see pin-toolpaths.json'
 print(f'{len(report["checks"])} nominal filament toolpath passages PASS.')
if __name__=='__main__':main()
