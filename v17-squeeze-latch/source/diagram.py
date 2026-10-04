"""Instructional sections taken from exported STEP geometry, not concept art."""
from pathlib import Path
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import folio as c
OUT=Path(__file__).resolve().parents[1]
a=cq.importers.importStep(str(OUT/'models/A-squeeze-clip.step')).val()
b=cq.importers.importStep(str(OUT/'models/B-socket.step')).val()
fig,axes=plt.subplots(1,3,figsize=(12,6))
def shape(ax,s,color):
 section=s.intersect(c.box(-50,50,-40,70,3.99,4.01))
 vs,fs=section.tessellate(.08,.15)
 v=np.array([[p.x,p.y] for p in vs])
 ax.add_collection(PolyCollection(v[np.array(fs)],facecolors=color,edgecolors='none'))
def arrow(ax,start,end,color='#30394a'):
 ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',lw=2.5,color=color))
for i,ax in enumerate(axes):
 shape(ax,b,'#698497')
 shape(ax,a.translate((0,-20 if i==0 else 0,0)),'#e4b557')
 ax.text(12,43,'B',ha='center',va='center',weight='bold')
 ax.text(12,-17.5 if i==0 else 2.5,'A',ha='center',va='center',weight='bold')
 ax.set_xlim(-12,36);ax.set_ylim(-25,52);ax.set_aspect('equal');ax.axis('off')
 ax.set_title(['1  Line up A with B','2  Push until both sides click','3  Squeeze both buttons; pull apart'][i],fontsize=12,pad=16)
 if i==0:arrow(ax,(12,-9),(12,5))
 if i==1:
  arrow(ax,(-9,22),(-1,22));arrow(ax,(33,22),(25,22))
  ax.text(12,-12,'Shoulders catch here',ha='center',fontsize=10)
 if i==2:
  arrow(ax,(-10,25),(1,25));arrow(ax,(34,25),(23,25))
  arrow(ax,(12,-4),(12,-19))
fig.suptitle('Simple v17 squeeze latch — top section (socket roof omitted for clarity)',fontsize=15)
fig.tight_layout(rect=(0,0,1,.95))
fig.savefig(OUT/'previews/how-to-use.png',dpi=160)
fig.savefig(OUT/'previews/how-to-use.svg')
