"""Render actual CC2 deposition layers. Does not contact a printer."""
from pathlib import Path
import json,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parent;WORK=OUT/'.slicer-work'
NOZZLE_OFFSET=[float(v) for v in json.loads((OUT/'profiles/machine.json').read_text())['extruder_offset'][0].split('x')]
PLANS={
 '01-print-in-place-bases':[.2,2.2,5.8,10.4,13.8,14.4,14.8,15.4,16.4,17.8,18.4,25.6],
 '02-sliding-board-tops':[.2,.6,1,2,3,4,4.2,4.6,4.8,5.6],
 '03-hatch-hook-and-three-axle-caps':[.2,1.2,2,2.6,3.2,3.4,4.2,5,6,7,7.8],
}

def parse(path):
 xyz={};role='';segments=[];relative=True;last=0
 for line in path.read_text().splitlines():
  if line.startswith(';TYPE:'):role=line[6:]
  cmd=line.split(';')[0].strip()
  if cmd=='M82':relative=False
  if cmd=='M83':relative=True
  if cmd.startswith('G92 '):
   match=re.search(r'E(-?\d*\.?\d+)',cmd)
   if match:last=float(match.group(1))
  if not re.match(r'^G[01] ',cmd):continue
  v={k:float(n) for k,n in re.findall(r'([XYZE])(-?\d*\.?\d+)',cmd)};old=xyz.copy();xyz.update({k:n for k,n in v.items() if k in 'XYZ'})
  if 'E' in v:
   amount=v['E'] if relative else v['E']-last;last=v['E']
   if amount>0 and role not in ('','Custom') and all(k in old and k in xyz for k in 'XYZ') and ('X' in v or 'Y' in v):segments.append((round(xyz['Z'],4),role,[(old['X']+NOZZLE_OFFSET[0],old['Y']+NOZZLE_OFFSET[1]),(xyz['X']+NOZZLE_OFFSET[0],xyz['Y']+NOZZLE_OFFSET[1])]))
 return segments

def main():
 report={}
 for name,requested in PLANS.items():
  segs=parse(WORK/f'{name}.gcode');levels=sorted({z for z,_,_ in segs});assert levels
  points=np.array([p for _,_,s in segs for p in s]);lo=points.min(0);hi=points.max(0)
  assert np.all(lo>.25) and np.all(hi<255.75)
  fig,axes=plt.subplots(4,3,figsize=(18,16));selected=[]
  for ax,want in zip(axes.flat,requested):
   z=min(levels,key=lambda x:abs(x-want));selected.append(z);layer=[(r,s) for zz,r,s in segs if zz==z]
   for sup,col,style in ((False,'#123957','solid'),(True,'#9a3150','dashed')):
    ax.add_collection(LineCollection([s for r,s in layer if r.startswith('Support')==sup],colors=col,linestyles=style,linewidths=.65))
   ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[1]-2,hi[1]+2);ax.set_aspect('equal');ax.set_title(f'Z = {z:g} mm',fontsize=17);ax.tick_params(labelsize=11);ax.grid(alpha=.2)
  for ax in axes.flat[len(requested):]:ax.set_visible(False)
  fig.suptitle(name.replace('-',' '),fontsize=23)
  fig.legend(handles=[Line2D([0],[0],color='#123957',lw=2,label='MODEL — solid'),Line2D([0],[0],color='#9a3150',lw=2,ls='--',label='SUPPORT — dashed')],loc='lower center',ncol=2,fontsize=18)
  fig.tight_layout(rect=(0,.045,1,.955));fig.savefig(OUT/'previews'/f'{name}-layers.png',dpi=130);plt.close(fig)
  report[name]={'levels':len(levels),'selected_z_mm':selected,'xy_centerline_bounds_mm':[lo.tolist(),hi.tolist()],'coordinate_frame':'Nozzle deposition; machine extruder_offset applied','extruder_offset_mm':NOZZLE_OFFSET,'fits_bed_with_half_bead':True,'visual_review':'pending','excluded_roles':['Custom','unlabelled start/end purge']}
 (OUT/'reports/layer-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Three actual deposition-layer sheets generated; bed bounds pass.')
if __name__=='__main__':main()
