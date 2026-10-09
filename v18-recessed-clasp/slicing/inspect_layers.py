from pathlib import Path
import re,json
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
P=Path('/tmp/V18-analysis-only.gcode');O=Path(__file__).parent
xyz={};role='';segs=[];relative=True;lastE=0
for line in P.read_text().splitlines():
 if line.startswith(';TYPE:'):role=line[6:]
 cmd=line.split(';')[0].strip()
 if cmd=='M82':relative=False
 if cmd=='M83':relative=True
 if not re.match(r'^G[01] ',cmd):continue
 v={k:float(n) for k,n in re.findall(r'([XYZE])(-?\d*\.?\d+)',cmd)};prev=xyz.copy();xyz.update({k:n for k,n in v.items() if k in 'XYZ'})
 if 'E' in v:
  ex=v['E'] if relative else v['E']-lastE;lastE=v['E']
  if ex>0 and all(k in prev and k in xyz for k in 'XYZ') and ('X' in v or 'Y' in v):segs.append((xyz['Z'],role,[(prev['X'],prev['Y']),(xyz['X'],xyz['Y'])]))
levels=sorted(set(round(z,4) for z,_,_ in segs));requested=[.2,2.4,2.6,2.8,6.6,18.6,26,26.2,30.2,33.2,39.8,40]
fig,axes=plt.subplots(4,3,figsize=(16,14))
for ax,want in zip(axes.flat,requested):
 z=min(levels,key=lambda v:abs(v-want));ss=[(r,s) for zz,r,s in segs if abs(zz-z)<1e-4]
 ax.add_collection(LineCollection([s for r,s in ss],colors=['#c956a9' if r.startswith('Support') else '#207699' for r,s in ss],linewidths=.45));ax.set_xlim(4,96);ax.set_ylim(3,46);ax.set_aspect('equal');ax.set_title(f'Z={z:g} mm');ax.grid(alpha=.15)
fig.suptitle('V18 actual dry-slice layers • Blue model / Magenta supports • Generic profile, not printer-ready',fontsize=16);fig.tight_layout(rect=(0,0,1,.97));fig.savefig(O/'layer-inspection.png',dpi=140)
# Deposition centreline envelope; allow half bead width separately.
pts=np.array([p for _,_,s in segs for p in s]);out={'unique_deposition_z_levels':len(levels),'xy_centerline_bounds_mm':[pts.min(0).tolist(),pts.max(0).tolist()],'bed_fit_with_half_bead_mm':bool(np.all(pts.min(0)>.225) and np.all(pts.max(0)<199.775)),'selected_layer_heights_mm':requested,'geometry_note':'Support-removal assessment is visual/CAD access only, not physical verification.'};(O/'layer-inspection.json').write_text(json.dumps(out,indent=2))
