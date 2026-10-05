"""Depth-buffered renders from actual exported STEP, including hinge hardware."""
import cadquery as cq
import vtk
import case as c
OUT=c.OUT
parts={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap'}
parts['hardware']=cq.importers.importStep(str(OUT/'models/hardware-reference-NOT-PRINTED.step')).val()
colors={'housing':(0.20,0.29,0.36),'board':(.85,.88,.92),'capstone':(.85,.88,.92),'side':(.59,.38,.13),'hardware':(.35,.38,.4)}
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
 camera=renderer.GetActiveCamera();camera.SetPosition(-500,-500,650);camera.SetViewUp(0,0,1)
 camera.SetParallelProjection(True);renderer.ResetCamera();camera.Zoom(.85)
 window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1600,1120);window.AddRenderer(renderer);window.Render()
 capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'previews'/f'{name}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
render('01-open',[(n,c.hook_rotate(s,c.HOOK_OPEN_ANGLE) if n=='side-hook' else s) for n,s in parts.items()],'V22 open — 180 mm field, sliding boards over fixed pockets')
render('02-closed',[(n,c.fold(s,180) if n.endswith('-right') else s) for n,s in parts.items()],'V22 closed — side hook, captive printed hinges')
scene=[]
for n,s in parts.items():
 if n=='side-hook':s=c.hook_rotate(s,c.HOOK_OPEN_ANGLE)
 if n.startswith('board'):s=c.slide(c.board(n.split('-')[1],c.BOARD_RELEASE),n.split('-')[1],c.BOARD_TRAVEL)
 if n=='capstone-hatch':s=c.hatch_rotate(s,100)
 scene.append((n,s))
render('03-access',scene,'V22 access — release front buttons, slide boards outward')
window=c.box(-15,8,-35,8,-1,35)
closed=[(n,c.fold(s,180) if n.endswith('-right') else s) for n,s in parts.items()]
for filename,angle,title in [('04-hook-closed',0,'V22 side hook — CLOSED over the headed pin'),('05-hook-open',c.HOOK_OPEN_ANGLE,'V22 side hook — SWING toward the front end to release')]:
 closeup=[]
 for n,s in closed:
  if n=='side-hook':s=c.hook_rotate(s,angle)
  clipped=s.intersect(window)
  if clipped.Volume()>1e-5:closeup.append((n,clipped))
 render(filename,closeup,title)
print('Five depth-buffered STEP readback previews generated.')
