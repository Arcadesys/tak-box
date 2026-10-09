from pathlib import Path
import cadquery as cq,json,vtk

def box(a,b,c,d,e,f): return cq.Solid.makeBox(b-a,d-c,f-e,cq.Vector(a,c,e))
def ov(a,b): return max(0,a.intersect(b).Volume())
def label(s,letter,x,y,z):
 t=cq.Workplane('XY').workplane(offset=z).center(x,y).text(letter,5,.6,font='DejaVu Sans',kind='bold',combine=False).val()
 return s.fuse(t).clean()
def export_parts(out,parts,rotations=None,meta=None):
 out=Path(out);out.mkdir(exist_ok=True,parents=True);rows=[]
 for n,s in parts.items():
  assert s.isValid() and len(s.Solids())==1,(n,s.isValid(),len(s.Solids()))
  cq.exporters.export(s,str(out/(n+'-assembled.step')))
  cq.exporters.export(s,str(out/(n+'-assembled.stl')),tolerance=.04,angularTolerance=.12)
  p=s
  if rotations and n in rotations:
   axis,angle=rotations[n];p=p.rotate((0,0,0),axis,angle)
  bb=p.BoundingBox();p=p.translate((-bb.xmin,-bb.ymin,-bb.zmin))
  cq.exporters.export(p,str(out/(n+'.step')));cq.exporters.export(p,str(out/(n+'.stl')),tolerance=.04,angularTolerance=.12)
  reader=vtk.vtkSTLReader();reader.SetFileName(str(out/(n+'.stl')));reader.Update()
  cleaner=vtk.vtkCleanPolyData();cleaner.SetInputConnection(reader.GetOutputPort());cleaner.Update()
  edges=vtk.vtkFeatureEdges();edges.SetInputConnection(cleaner.GetOutputPort());edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
  assert edges.GetOutput().GetNumberOfCells()==0,(n,'not watertight')
  bb=p.BoundingBox()
  rows.append(dict(name=n,stl=str(out/(n+'.stl')),assembled_stl=str(out/(n+'-assembled.stl')),bounds=[bb.xlen,bb.ylen,bb.zlen],volume_mm3=s.Volume(),watertight=True))
 cq.exporters.export(cq.Compound.makeCompound(list(parts.values())),str(out/'assembly.step'))
 manifest=dict(parts=rows,meta=meta or {},assembled_overlap_mm3={a+'__'+b:ov(parts[a],parts[b]) for i,a in enumerate(parts) for b in list(parts)[i+1:]})
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));return manifest
