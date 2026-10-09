"""Render actual exported reinforced-B-trial CAD and its measured axle section."""
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
 r.render('01-open',r.load('B-assembly').Solids(),'V25 B — filament hinge reinforced B trial','6 mm coupon floors; selected middle fit retained; both filament ends are heat formed',(-90,-85,90))
 shapes=[b.hinge('left',.35,'B'),b.c.fold(b.hinge('right',.35,'B'),180),b.headed_filament()]
 cq.exporters.export(cq.Compound.makeCompound(shapes),str(OUT/'models/B-closed.step'))
 r.render('02-closed',r.load('B-closed').Solids(),'V25 B — folded 180 degrees / actual CAD','Recessed heads block axle escape in both directions; printed durability remains untested',(0,-90,70))
 r.render('03-rounded-boards',r.load('B-with-boards').Solids(),'V25 — rounded underside board samples','Flat playing faces retained; local hinge trial, full case integration still required',(-80,-60,55))
 r.render('04-print-plate',[r.load(p.stem) for p in sorted((OUT/'models').glob('*.stl'))],'V25 — four printed trial parts','B middle fit; reinforced sample bodies and two board samples',(-100,-180,260))
 fig,ax=plt.subplots(figsize=(13,8))
 for s,col in zip(r.load('B-assembly').Solids(),['#385566','#b8c9d4','#b06c0e']):
  section=s.intersect(b.c.box(97.99,98.01,-.5,10,12,23))
  vs,fs=section.tessellate(.02,.08);v=np.array([[q.x,q.y,q.z] for q in vs]);ax.add_collection(PolyCollection(v[np.array(fs)][:,:,[1,2]],facecolors=col,edgecolors='none'))
 ax.set(xlim=(-1.2,10.8),ylim=(11.8,24.1),aspect='equal',xlabel='Along axle / mm',ylabel='Height / mm')
 ax.set_title('B: actual CAD section through the filament axis',fontsize=21,pad=20)
 ax.tick_params(labelsize=13);ax.xaxis.label.set_size(15);ax.yaxis.label.set_size(15)
 for text,x in [('FIXED',1.55),('MOVING',4.8),('FIXED',8.05)]:ax.text(x,22.8,text,fontsize=14,ha='center',weight='bold')
 ax.annotate('Two formed heads\n3.2 mm diameter',(.6,17.5),(2.0,14),bbox=dict(fc='white',ec='none',pad=5),fontsize=15,arrowprops=dict(arrowstyle='->',lw=2),ha='center')
 ax.annotate('',(9,17.5),(2,15.2),arrowprops=dict(arrowstyle='->',lw=2))
 ax.annotate('1.75 mm filament\ninside 2.10 mm moving bore',(4.8,17.5),(4.8,20.4),bbox=dict(fc='white',ec='none',pad=5),fontsize=15,ha='center',arrowprops=dict(arrowstyle='->',lw=2))
 ax.annotate('3.5 mm head recess\n0.1 mm axial allowance',(8.7,18.8),(8,12.5),bbox=dict(fc='white',ec='none',pad=5),fontsize=14,ha='center',arrowprops=dict(arrowstyle='->',lw=2))
 ax.axhline(17.5,color='#667',ls=':',lw=.7);ax.grid(alpha=.2)
 fig.text(.5,.015,'Heads are reference hardware made from filament — no printed pin or cap.',ha='center',fontsize=15)
 fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'previews/05-axle-section.png',dpi=160);plt.close(fig)
 fig,ax=plt.subplots(figsize=(12,6))
 fixed=r.load('B-assembly').Solids()[0]
 section=fixed.intersect(b.c.box(74,91,15.99,16.01,-4.5,4))
 vs,fs=section.tessellate(.02,.08);v=np.array([[q.x,q.y,q.z] for q in vs])
 ax.add_collection(PolyCollection(v[np.array(fs)][:,:,[0,2]],facecolors='#385566',edgecolors='none'))
 ax.set(xlim=(74,94),ylim=(-5,5),aspect='equal',xlabel='Across sample / mm',ylabel='Height / mm')
 ax.set_title('B fixture: actual CAD section through the sample floor',fontsize=19,pad=15)
 ax.tick_params(labelsize=13);ax.xaxis.label.set_size(14);ax.yaxis.label.set_size(14)
 ax.axhline(0,color='#111',ls='--',lw=1.8)
 ax.annotate('Reference case underside; backing added below',(80,0),(82,3.3),fontsize=15,ha='center',bbox=dict(fc='white',ec='none',pad=4),arrowprops=dict(arrowstyle='->',lw=2))
 ax.annotate('',(92,-3.8),(92,2.2),arrowprops=dict(arrowstyle='<->',lw=2))
 ax.text(92.2,-.8,'6 mm',fontsize=16,rotation=90,va='center')
 ax.grid(alpha=.15);fig.tight_layout();fig.savefig(OUT/'previews/06-fixture-floor.png',dpi=160);plt.close(fig)
 print('Six actual CAD previews exported')
if __name__=='__main__':main()
