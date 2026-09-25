"""Render the modeled board in play and piece-access positions."""
from pathlib import Path
import cadquery as cq
import vtk
import tak_case as m

OUT=Path(__file__).resolve().parent

def actor(shape,color):
    verts,triangles=shape.tessellate(.7,.3)
    points=vtk.vtkPoints()
    for v in verts:points.InsertNextPoint(v.x,v.y,v.z)
    faces=vtk.vtkCellArray()
    for tri in triangles:
        cell=vtk.vtkTriangle()
        for i,n in enumerate(tri):cell.GetPointIds().SetId(i,n)
        faces.InsertNextCell(cell)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(faces)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly)
    normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    out=vtk.vtkActor();out.SetMapper(mapper)
    out.GetProperty().SetColor(*color)
    out.GetProperty().SetAmbient(.3)
    out.GetProperty().SetDiffuse(.7)
    return out

shells=[];lids=[]
for i in (0,2):
    shell,lid=m.lid_pair(i)
    shells.append((i,shell));lids.append((i,lid))
shells.insert(1,(1,m.shell(1)))

def render(name,access=False):
    renderer=vtk.vtkRenderer()
    renderer.SetBackground(.94,.96,.98)
    window=vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1600,1100)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    for _,s in shells:renderer.AddActor(actor(s,(.90,.91,.89)))
    for i,l in lids:
        shape=m.lid_open(l,i,105) if access else l
        renderer.AddActor(actor(shape,(.97,.97,.94)))
    if not access:
        for i in range(3):renderer.AddActor(actor(m.overlay(i),(.07,.08,.10)))
    else:
        for i in (0,2):
            for p in m.pieces(i)[:-1]:renderer.AddActor(actor(p,(.58,.32,.15)))
            renderer.AddActor(actor(m.pieces(i)[-1],(.79,.54,.19)))
    camera=renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetFocalPoint(102.5,102.5,-2)
    camera.SetPosition(360,-280,370)
    camera.SetViewUp(0,0,1)
    camera.SetParallelScale(198 if access else 145)
    renderer.ResetCameraClippingRange()
    window.Render()
    image=vtk.vtkWindowToImageFilter();image.SetInput(window);image.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/name))
    writer.SetInputConnection(image.GetOutputPort());writer.Write()

render('play-face-cad.png')
render('lifted-lids-cad.png',True)
