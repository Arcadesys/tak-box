"""Render actual CAD geometry with depth buffering."""
import vtk
import case as c
OUT=c.OUT
colors={'housing':(0.20,0.29,0.36),'board':(.85,.88,.92),'capstone':(.85,.88,.92),'side':(.59,.38,.13),'hardware':(.35,.38,.4),'capbody':(.14,.23,.32),'capdetail':(.95,.71,.32)}
def render(name,scene,title,camera_pos=(-500,-500,650)):
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
 camera=renderer.GetActiveCamera();camera.SetPosition(*camera_pos);camera.SetViewUp(0,0,1)
 camera.SetParallelProjection(True);renderer.ResetCamera();camera.Zoom(.85)
 window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1600,1120);window.AddRenderer(renderer);window.Render()
 capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'previews'/f'{name}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
