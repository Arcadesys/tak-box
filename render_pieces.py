"""Render Team Cat and Team Witch piece sets."""
from pathlib import Path
import vtk
import tak_pieces as p

OUT=Path(__file__).resolve().parent/'pieces'
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


def team_scene(team,color,x0):
    """Two stacked flats, one flat leaning-free on the side, and the capstone."""
    parts=[p.flat(team).translate((x0,0,0)).val(),
           p.flat(team).translate((x0,0,8)).val(),
           p.flat(team).translate((x0+26,-6,0)).val()]
    cap=p.capstone(team).translate((x0-26,0,0))
    return parts,cap

def render(name,camera_pos,scale,focal):
    renderer=vtk.vtkRenderer();renderer.SetBackground(.94,.96,.98)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1)
    window.SetSize(1800,1000);window.SetMultiSamples(8);window.AddRenderer(renderer)
    for team,color,x0 in (('cat',(.93,.55,.20),-45),('witch',(.42,.24,.66),45)):
        parts,cap=team_scene(team,color,x0)
        for s in parts:renderer.AddActor(actor(s,color))
        renderer.AddActor(actor(cap.val(),color))
    camera=renderer.GetActiveCamera();camera.ParallelProjectionOn()
    camera.SetFocalPoint(*focal);camera.SetPosition(*camera_pos)
    camera.SetViewUp(0,0,1);camera.SetParallelScale(scale)
    renderer.ResetCameraClippingRange();window.Render()
    image=vtk.vtkWindowToImageFilter();image.SetInput(window);image.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/name))
    writer.SetInputConnection(image.GetOutputPort());writer.Write()

render('team-pieces-preview.png',(60,-230,190),62,(0,0,10))
render('team-pieces-top.png',(0,-60,300),62,(0,0,10))
