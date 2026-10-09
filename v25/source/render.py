"""Depth-buffered real exported STEP CAD plus measured orthographic sections."""
from pathlib import Path
import sys
import cadquery as cq
import vtk,numpy as np
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'v25'
sys.path.insert(0,str(OUT/'reference/v24/source'))
import case as c
def load(n):return cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val()
def render(name,parts,title,sub,camera):
 r=vtk.vtkRenderer();r.SetBackground(1,1,1)
 colors=[(.23,.36,.44),(.68,.75,.8),(.85,.57,.2),(.85,.35,.25)]
 for i,s in enumerate(parts):
  vs,fs=s.tessellate(.04,.12);p=vtk.vtkPoints()
  for v in vs:p.InsertNextPoint(v.x,v.y,v.z)
  cells=vtk.vtkCellArray()
  for f in fs:
   cells.InsertNextCell(3)
   for ix in f:cells.InsertCellPoint(ix)
  poly=vtk.vtkPolyData();poly.SetPoints(p);poly.SetPolys(cells)
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
  actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*colors[i%4]);actor.GetProperty().SetAmbient(.25);r.AddActor(actor)
 cam=r.GetActiveCamera();cam.SetPosition(*camera);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();r.ResetCamera();cam.Zoom(.8)
 w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1600,1100);w.AddRenderer(r);w.Render()
 cap=vtk.vtkWindowToImageFilter();cap.SetInput(w);cap.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'previews'/f'{name}.png'));writer.SetInputConnection(cap.GetOutputPort());writer.Write();w.Finalize()
 im=Image.open(OUT/'previews'/f'{name}.png').convert('RGB');d=ImageDraw.Draw(im)
 fontpath=str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf')
 d.rectangle((0,0,1600,115),fill='white');d.text((45,20),title,font=ImageFont.truetype(fontpath,32),fill='#122431');d.text((45,65),sub,font=ImageFont.truetype(fontpath,22),fill='#344552');im.save(OUT/'previews'/f'{name}.png')
def dim(ax,a,b,text,off=(0,0)):
 a=np.array(a)+off;b=np.array(b)+off;ax.annotate('',a,b,arrowprops=dict(arrowstyle='<->',color='#b13b23',lw=1.5));m=(a+b)/2;ax.text(*m,text,color='#b13b23',fontsize=10,ha='center',va='bottom',bbox=dict(fc='white',ec='none',pad=1))
def main():
 h=load('H2-assembly');parts=h.Solids()
 render('01-hinge-open',parts,'V25 H2 — real CAD, open flat','1.75 mm filament / 2.10 mm bore; blind end; bond fixed barrel only',(-90,-85,90))
 # Assemblies exported in design coordinates. Sort by center to identify right body.
 import build as b
 shapes=[b.hinge('left',.35,'H2'),b.hinge('right',.35,'H2'),b.filament()]
 cq.exporters.export(cq.Compound.makeCompound([shapes[0],c.fold(shapes[1],180),*shapes[2:]]),str(OUT/'models/H2-closed.step'))
 render('02-hinge-closed',load('H2-closed').Solids(),'V25 H2 — closed at 180°','Proven V24 axis retained; these local coupons do not qualify a complete V25 case',(0,-90,70))
 l=load('L2-assembly');render('03-lip',l.Solids(),'V25 L2 — broad underside lip / real CAD','28 mm blade width; 1.0 mm blade; 0.4 mm positive engagement; +1 mm per half',(-40,-10,55))
 # Actual CAD intersected at midsection; no schematic stand-in for the geometry.
 board=b.lip_board(1,'L2');seat=b.lip_seat('L2')
 section=[s.intersect(c.box(-1,19,39.99,40.01,0,19)) for s in (seat,board)]
 fig,ax=plt.subplots(figsize=(12,6))
 for s,col in zip(section,['#536f80','#d3dce2']):
  vs,fs=s.tessellate(.02,.08);v=np.array([[q.x,q.y,q.z] for q in vs]);ax.add_collection(PolyCollection(v[np.array(fs)][:,:,[0,2]],facecolors=col,edgecolors='none'))
 ax.set(xlim=(-3,20),ylim=(9.5,19.5),aspect='equal',xlabel='X / mm',ylabel='Z / mm',title='L2: measured CAD section at Y40 mm — upward lip flex remains untested')
 dim(ax,(0,18.3),(12,18.3),'12 mm free beam')
 dim(ax,(-1.8,12.8),(-1.8,13.8),'1.0 mm blade')
 dim(ax,(2.8,12.2),(2.8,12.6),'0.4 engagement',(.2,0))
 ax.annotate('0.65 mm upward release trial',(1.5,13.3),(4,15.6),arrowprops=dict(arrowstyle='->'),fontsize=10)
 ax.annotate('14.8 mm pocket ceiling / 17.5 mm face',(9,14.8),(9,16),arrowprops=dict(arrowstyle='->'),fontsize=10)
 ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'previews/04-lip-section.png',dpi=160);fig.savefig(OUT/'previews/04-lip-section.svg');plt.close(fig)
 fig,ax=plt.subplots(figsize=(12,7))
 for s,col in zip(shapes,['#536f80','#bfcbd3','#d8a042','#cf614d']):
  s=s.intersect(c.box(97.99,98.01,-1,11,12,23))
  vs,fs=s.tessellate(.02,.08);v=np.array([[q.x,q.y,q.z] for q in vs]);ax.add_collection(PolyCollection(v[np.array(fs)][:,:,[1,2]],facecolors=col,edgecolors='none'))
 ax.set(xlim=(-1.4,11),ylim=(11.5,24),aspect='equal',xlabel='Y / mm',ylabel='Z / mm',title='H2: actual CAD longitudinal section at X98 mm — filament reference and blind fixed barrel')
 dim(ax,(1.7,12.3),(7.1,12.3),'5.4 mm filament; not printed')
 dim(ax,(4.5,23),(4.9,23),'0.40 axial gap')
 dim(ax,(5.8,16.45),(5.8,18.55),'Ø2.10 bore')
 dim(ax,(2.9,16.625),(2.9,18.375),'Ø1.75 filament')
 ax.annotate('0.5 mm blind wall / bond fixed barrel only',(7.35,17.5),(7.0,22.1),arrowprops=dict(arrowstyle='->'),fontsize=10)
 ax.axhline(17.5,color='#667',ls=':',lw=.7);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'previews/06-hinge-section.png',dpi=160);fig.savefig(OUT/'previews/06-hinge-section.svg');plt.close(fig)
 plateparts=[load(p.stem) for p in sorted((OUT/'models').glob('*.stl'))]
 render('05-print-plate',plateparts,'V25 — filament trial / 14 printed parts','Left to right: H1 .20 / H2 .35 / H3 .50 mm clearance; L1 .8 / L2 1.0 / L3 1.2 mm lip',(-100,-180,260))
 render('07-rounded-board-relief',load('rounded-board-hinge-assembly').Solids(),'V25 — curved underside board relief / real CAD','Flat playing faces retained; filament shown as reference hardware; local test only',(-80,-60,55))
 print('Seven actual CAD previews exported')
if __name__=='__main__':main()
