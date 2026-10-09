"""Check captive CAD pivots and running gaps in actual sliced extrusion."""
from pathlib import Path
import hashlib,json
import cadquery as cq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import case as c
import inspect_case_layers as layers
from verify_pin_toolpaths import hits
OUT=c.OUT

def bead_ranges(segments,y,radius=.25):
 # Exact horizontal intersection with constant-width segment capsules.
 intervals=[]
 for _,points in segments:
  a,b=np.array(points[0]),np.array(points[1]);delta=b-a;length=np.linalg.norm(delta)
  values=[]
  for point in (a,b):
   dy=abs(point[1]-y)
   if dy<=radius:
    dx=(radius*radius-dy*dy)**.5;values.extend([point[0]-dx,point[0]+dx])
  if length>1e-9:
   normal=np.array([-delta[1],delta[0]])/length*radius
   poly=[a+normal,b+normal,b-normal,a-normal]
   for p,q in zip(poly,poly[1:]+poly[:1]):
    if abs(q[1]-p[1])>1e-10 and min(p[1],q[1])<=y<=max(p[1],q[1]):values.append(p[0]+(q[0]-p[0])*(y-p[1])/(q[1]-p[1]))
  if values:intervals.append((min(values),max(values)))
 merged=[]
 for lo,hi in sorted(intervals):
  if merged and lo<=merged[-1][1]+1e-9:merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
  else:merged.append((lo,hi))
 return merged

def toolpath_checks(path,shift,rear_shift=0,preview='07-captive-hinge-gaps'):
 segs=layers.parse(path);checks=[];views=[]
 P=np.array([[pts[0][0],pts[0][1],z] for z,_,pts in segs]);Q=np.array([[pts[1][0],pts[1][1],z] for z,_,pts in segs]);support=np.array([r.startswith('Support') for _,r,_ in segs])
 levels=sorted({z for z,_,_ in segs});digest=hashlib.sha256(path.read_bytes()).hexdigest()
 for index,(mouth,end) in enumerate(((3.2,6.4),(193.6,196.8))):
  face=mouth;d=1
  extra=rear_shift if index else 0;face+=extra;mouth+=extra
  axis=np.array([98,0,c.base.AX[1]])+np.array(shift)
  end+=extra;lo=mouth+.15;hi=end-.15
  a=axis+np.array([0,lo,0]);b=axis+np.array([0,hi,0])
  found=hits(P[support],Q[support],a,b,2.4)
  checks.append({'name':f'pivot {index+1} no support centerlines inside bearing cavity','pass':not bool(found.any()),'intrusions':int(found.sum()),'gcode_sha256':digest})
  y=axis[1]+(lo+hi)/2
  for dz in (-1,-.6,-.2,.2,.6,1):
   z=min(levels,key=lambda zz:abs(zz-(axis[2]+dz)))
   crop=[(r,pts) for zz,r,pts in segs if zz==z and max(p[0] for p in pts)>axis[0]-5 and min(p[0] for p in pts)<axis[0]+5 and max(p[1] for p in pts)>axis[1]+min(face,mouth,end)-1 and min(p[1] for p in pts)<axis[1]+max(face,mouth,end)+1]
   # 0.50 mm assumed bead width conservatively covers the configured widths.
   occupied=bead_ranges(crop,y)
   pin_indices=[i for i,v in enumerate(occupied) if v[0]<axis[0]+1.2 and v[1]>axis[0]-1.2]
   gaps=[]
   if pin_indices:
    first,last=min(pin_indices),max(pin_indices)
    if first>0 and last+1<len(occupied):gaps=[occupied[first][0]-occupied[first-1][1],occupied[last+1][0]-occupied[last][1]]
   passed=len(gaps)==2 and min(gaps)>.1
   checks.append({'name':f'pivot {index+1} radial running gaps at Z={z}','pass':bool(passed),'estimated_bead_edge_gaps_mm':gaps,'gcode_sha256':digest})
   if dz in (-.2,.2):views.append((f'Pivot {index+1}, Z={z:g}',crop,axis,y,gaps))
  # Probe each fixed/moving axial face on both sides of the post.
  faces=((mouth-.4,mouth),(end,end+.4))
  z=min(levels,key=lambda zz:abs(zz-axis[2]))
  for dx in (-3,3):
   crop=[(r,[(p[1],p[0]) for p in pts]) for zz,r,pts in segs if zz==z and max(p[0] for p in pts)>axis[0]-5 and min(p[0] for p in pts)<axis[0]+5 and max(p[1] for p in pts)>axis[1]+mouth-3 and min(p[1] for p in pts)<axis[1]+end+3]
   occupied=bead_ranges(crop,axis[0]+dx)
   for lower,upper in faces:
    target=axis[1]+(lower+upper)/2
    gaps=[hi-lo for (_,lo),(hi,_) in zip(occupied,occupied[1:]) if lo<target<hi]
    checks.append({'name':f'hinge {index+1} axial face gap {lower:g} at X offset {dx}', 'pass':bool(len(gaps)==1 and gaps[0]>.1),'estimated_bead_edge_gaps_mm':gaps,'gcode_sha256':digest})
 fig,axes=plt.subplots(2,2,figsize=(14,12))
 for ax,(title,crop,axis,y,gaps) in zip(axes.flat,views):
  for sup,col,style in [(False,'#123957','solid'),(True,'#9a3150','dashed')]:ax.add_collection(LineCollection([pts for role,pts in crop if role.startswith('Support')==sup],colors=col,linestyles=style,linewidths=1.4))
  ax.axhline(y,color='black',ls=':');ax.set_xlim(axis[0]-5,axis[0]+5);ax.set_ylim(y-4,y+4);ax.set_aspect('equal');ax.set_title(title+'\nMeasured gaps: '+', '.join(f'{v:.2f} mm' for v in gaps),fontsize=17);ax.tick_params(labelsize=11)
 fig.suptitle('Captive hinge gaps — actual sliced paths',fontsize=23);fig.tight_layout(rect=(0,0,1,.94));fig.subplots_adjust(hspace=.35);fig.savefig(OUT/'previews'/f'{preview}.png',dpi=130);plt.close(fig)
 return checks
