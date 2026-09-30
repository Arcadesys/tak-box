"""Large, high-contrast CAD preview; depicts unfilled printed parts."""
from pathlib import Path
import vtk
import stones as s

ROOT = Path(__file__).resolve().parents[1]


def actor(shape, color):
    verts, triangles = shape.val().tessellate(.08, .15)
    points = vtk.vtkPoints()
    for v in verts:
        points.InsertNextPoint(v.x, v.y, v.z)
    cells = vtk.vtkCellArray()
    for tri in triangles:
        cells.InsertNextCell(3, tri)
    data = vtk.vtkPolyData()
    data.SetPoints(points)
    data.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(data)
    normals.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    result = vtk.vtkActor()
    result.SetMapper(mapper)
    result.GetProperty().SetColor(*color)
    result.GetProperty().SetAmbient(.28)
    return result


def text(renderer, message, x, y, size):
    label = vtk.vtkTextActor()
    label.SetInput(message)
    label.SetPosition(x, y)
    style = label.GetTextProperty()
    style.SetFontSize(size)
    style.SetColor(.98, .98, 1)
    style.SetFontFamilyToArial()
    renderer.AddViewProp(label)


renderer = vtk.vtkRenderer()
renderer.SetBackground(.035, .05, .08)
window = vtk.vtkRenderWindow()
window.SetOffScreenRendering(1)
window.SetSize(1800, 1150)
window.SetMultiSamples(8)
window.AddRenderer(renderer)
for team, color, x in (('cat', (1, .57, .16), -47), ('witch', (.70, .53, 1), 47)):
    b, f = s.body(team), s.floor()
    for level in range(3):
        renderer.AddActor(actor(b.translate((x - 18, 22, level * 6)), color))
        renderer.AddActor(actor(f.translate((x - 18, 22, level * 6)), color))
    wall_b = b.rotate((0, 0, 0), (1, 0, 0), 90).translate((x + 12, 28, 10))
    wall_f = f.rotate((0, 0, 0), (1, 0, 0), 90).translate((x + 12, 28, 10))
    renderer.AddActor(actor(wall_b, color))
    renderer.AddActor(actor(wall_f, color))
    renderer.AddActor(actor(s.body_for_print(team).translate((x - 18, -28, 0)), color))
    renderer.AddActor(actor(f.translate((x + 12, -28, 0)), color))
text(renderer, 'WEIGHTED TAK STONES', 65, 1060, 48)
text(renderer, '20 x 20 x 6 mm  |  Open body + epoxied floor  |  CAD prototype', 65, 1000, 32)
text(renderer, 'TEAM CAT', 250, 900, 38)
text(renderer, 'TEAM WITCH', 1090, 900, 38)
text(renderer, 'Three-stone stacks and standing walls', 65, 820, 28)
text(renderer, 'Open ballast cavities and separate locating floors', 65, 510, 28)
text(renderer, 'Print the 3-clearance fit coupon first. Weight, sound and grip need a physical test.', 65, 55, 29)
camera = renderer.GetActiveCamera()
camera.ParallelProjectionOn()
camera.SetFocalPoint(0, 0, 5)
camera.SetPosition(0, -200, 240)
camera.SetViewUp(0, 0, 1)
camera.SetParallelScale(78)
renderer.ResetCameraClippingRange()
window.Render()
capture = vtk.vtkWindowToImageFilter()
capture.SetInput(window)
capture.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(str(ROOT / 'previews' / 'weighted-stones.png'))
writer.SetInputConnection(capture.GetOutputPort())
writer.Write()
print(ROOT / 'previews' / 'weighted-stones.png')
