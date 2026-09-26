"""Render the v6 design sketch: closed corners, lid lip, scoop, and stop."""
from pathlib import Path
import cadquery as cq
import vtk
import tak_case_v6 as v6
import tak_case as base

OUT = Path(__file__).resolve().parent


def actor(shape, color):
    verts, triangles = shape.tessellate(.5, .2)
    points = vtk.vtkPoints()
    for v in verts:
        points.InsertNextPoint(v.x, v.y, v.z)
    faces = vtk.vtkCellArray()
    for tri in triangles:
        cell = vtk.vtkTriangle()
        for i, n in enumerate(tri):
            cell.GetPointIds().SetId(i, n)
        faces.InsertNextCell(cell)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(faces)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    out = vtk.vtkActor()
    out.SetMapper(mapper)
    out.GetProperty().SetColor(*color)
    out.GetProperty().SetAmbient(.35)
    out.GetProperty().SetDiffuse(.7)
    return out


pair0 = v6.lid_pair(0)
pair2 = v6.lid_pair(2)
shells = [(0, pair0[0]), (1, v6.center_row()), (2, pair2[0])]
lids = [(0, pair0[1]), (2, pair2[1])]


def render(name, access=False):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(.94, .96, .98)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1600, 1100)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    for _, s in shells:
        renderer.AddActor(actor(s, (.90, .91, .89)))
    for i, l in lids:
        shape = v6.lid_open(l, i, 105) if access else l
        renderer.AddActor(actor(shape, (.97, .97, .85)))
    if access:
        for i in (0, 2):
            for p in base.pieces(i)[:-1]:
                renderer.AddActor(actor(p, (.58, .32, .15)))
            renderer.AddActor(actor(base.pieces(i)[-1], (.79, .54, .19)))
    camera = renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetFocalPoint(102.5, 102.5, -2)
    camera.SetPosition(360, -280, 370)
    camera.SetViewUp(0, 0, 1)
    camera.SetParallelScale(198 if access else 145)
    renderer.ResetCameraClippingRange()
    window.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    image.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / name))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()


def render_corner():
    """Close-up of the rounded corner + lid lip at wing0's far x=0 end."""
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(.94, .96, .98)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1400, 1000)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    renderer.AddActor(actor(pair0[0], (.90, .91, .89)))
    renderer.AddActor(actor(pair0[1], (.97, .97, .85)))
    camera = renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetFocalPoint(20, 20, -5)
    camera.SetPosition(-120, -160, 140)
    camera.SetViewUp(0, 0, 1)
    camera.SetParallelScale(35)
    renderer.ResetCameraClippingRange()
    window.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    image.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / 'v6-corner-detail.png'))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()


render('v6-play-face.png')
render('v6-lifted-lids.png', True)
render_corner()
