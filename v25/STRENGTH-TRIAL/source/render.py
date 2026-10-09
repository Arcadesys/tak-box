"""Render actual exported strength-trial CAD and its measured axle section."""
from pathlib import Path
import importlib.util
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
OUT=Path(__file__).resolve().parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
r=module('render_common',OUT.parent/'source/render.py');r.OUT=OUT
b=module('strength_build',OUT/'source/build.py')
def main():
 r.render('01-open',r.load('S2-assembly').Solids(),'V25 S2 — filament hinge strength trial','Two fixed bearings support the moving bearing; both filament ends are heat formed',(-90,-85,90))
 shapes=[b.hinge('left',.35,'S2'),b.c.fold(b.hinge('right',.35,'S2'),180),b.headed_filament()]
 cq.exporters.export(cq.Compound.makeCompound(shapes),str(OUT/'models/S2-closed.step'))
 r.render('02-closed',r.load('S2-closed').Solids(),'V25 S2 — folded 180 degrees / actual CAD','Recessed heads block axle escape in both directions; printed durability remains untested',(0,-90,70))
 r.render('03-rounded-boards',r.load('S2-with-boards').Solids(),'V25 — rounded underside board samples','Flat playing faces retained; local hinge trial, full case integration still required',(-80,-60,55))
 r.render('04-print-plate',[r.load(p.stem) for p in sorted((OUT/'models').glob('*.stl'))],'V25 — eight printed trial parts','S1 / S2 / S3 bearing fits and two board samples; use ordinary filament as the axle',(-100,-180,260))
 fig,ax=plt.subplots(figsize=(13,8))
 for s,col in zip(r.load('S2-assembly').Solids(),['#385566','#b8c9d4','#b06c0e']):
  section=s.intersect(b.c.box(97.99,98.01,-.5,10,12,23))
  vs,fs=section.tessellate(.02,.08);v=np.array([[q.x,q.y,q.z] for q in vs]);ax.add_collection(PolyCollection(v[np.array(fs)][:,:,[1,2]],facecolors=col,edgecolors='none'))
 ax.set(xlim=(-1.2,10.8),ylim=(11.8,24.1),aspect='equal',xlabel='Along axle / mm',ylabel='Height / mm')
 ax.set_title('S2: actual CAD section through the filament axis',fontsize=21,pad=20)
 ax.tick_params(labelsize=13);ax.xaxis.label.set_size(15);ax.yaxis.label.set_size(15)
 for text,x in [('FIXED',1.55),('MOVING',4.8),('FIXED',8.05)]:ax.text(x,22.8,text,fontsize=14,ha='center',weight='bold')
 ax.annotate('Two formed heads\n3.2 mm diameter',(.6,17.5),(2.0,14),bbox=dict(fc='white',ec='none',pad=5),fontsize=15,arrowprops=dict(arrowstyle='->',lw=2),ha='center')
 ax.annotate('',(9,17.5),(2,14),arrowprops=dict(arrowstyle='->',lw=2))
 ax.annotate('1.75 mm filament\ninside 2.10 mm moving bore',(4.8,17.5),(4.8,20.4),bbox=dict(fc='white',ec='none',pad=5),fontsize=15,ha='center',arrowprops=dict(arrowstyle='->',lw=2))
 ax.annotate('3.5 mm head recess\n0.1 mm axial allowance',(8.7,18.8),(8,12.5),bbox=dict(fc='white',ec='none',pad=5),fontsize=14,ha='center',arrowprops=dict(arrowstyle='->',lw=2))
 ax.axhline(17.5,color='#667',ls=':',lw=.7);ax.grid(alpha=.2)
 fig.text(.5,.015,'Heads are reference hardware made from filament — no printed pin or cap.',ha='center',fontsize=15)
 fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'previews/05-axle-section.png',dpi=160);plt.close(fig)
 print('Five actual CAD previews exported')
if __name__=='__main__':main()
