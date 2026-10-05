"""Depth-buffered renders from actual exported STEP, including hinge hardware."""
import cadquery as cq
import vtk
import case as c
OUT=c.REPO/'v18-case'
parts={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap'}
parts['hardware']=cq.importers.importStep(str(OUT/'models/hardware-reference-NOT-PRINTED.step')).val()
colors={'housing':(0.20,0.29,0.36),'board':(.85,.88,.92),'drawer':(.59,.38,.13),'capstone':(.85,.88,.92),'clasp':(.59,.38,.13),'hardware':(.35,.38,.4)}
def render(name,scene,title):
 renderer=vtk.vtkRenderer();renderer.SetBackground(1,1,1)
 for label,s in scene:
  vertices,faces=s.tessellate(.08,.15)
  points=vtk.vtkPoints()
  for v in vertices:points.InsertNextPoint(v.x,v.y,v.z)
  cells=vtk.vtkCellArray()
  for face in faces:
   cells.InsertNextCell(3)
   for i in face:cells.InsertCellPoint(i)
  poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
  actor=vtk.vtkActor();actor.SetMapper(mapper)
  actor.GetProperty().SetColor(*colors[label.split('-')[0]])
  actor.GetProperty().SetInterpolationToFlat();actor.GetProperty().SetAmbient(.25)
  renderer.AddActor(actor)
 text=vtk.vtkTextActor();text.SetInput(title);text.SetPosition(38,1050)
 text.GetTextProperty().SetFontSize(31);text.GetTextProperty().SetColor(.05,.05,.05)
 renderer.AddActor2D(text)
 camera=renderer.GetActiveCamera();camera.SetPosition(500,-500,650);camera.SetViewUp(0,0,1)
 camera.SetParallelProjection(True);renderer.ResetCamera();camera.Zoom(1.12)
 window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1600,1120);window.AddRenderer(renderer);window.Render()
 capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'previews'/f'{name}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
render('01-open',list(parts.items()),'V18 open — 180 mm field, original Cat/Witch drawers')
render('02-closed',[(n,c.fold(s,180) if n.endswith('-right') else s) for n,s in parts.items()],'V18 closed — integrated clasp and retained hinge hardware')
scene=[]
for n,s in parts.items():
 if n.startswith('drawer'):s=s.translate((0,-168,0))
 if n=='capstone-hatch':s=c.hatch_rotate(s,100)
 scene.append((n,s))
render('03-access',scene,'V18 access — support drawers on table; hatch raised')
print('Three depth-buffered STEP readback previews generated.')
