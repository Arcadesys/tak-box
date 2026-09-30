"""High-contrast large CAD views of the emblem, knurl, stack and wall."""
from pathlib import Path
import numpy as np
import vtk
import flats as f

ROOT = Path(__file__).resolve().parents[1]


reader = vtk.vtkSTLReader()
reader.SetFileName(str(ROOT / 'models/fox-flat.stl'))
reader.Update()


def actor(matrix):
    # Render the verified print mesh, rather than rebuilding/tessellating CAD.
    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix.ravel().tolist())
    moved = vtk.vtkTransformPolyDataFilter()
    moved.SetInputConnection(reader.GetOutputPort())
    moved.SetTransform(transform)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(moved.GetOutputPort())
    normals.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    result = vtk.vtkActor()
    result.SetMapper(mapper)
    result.GetProperty().SetColor(1, .47, .08)
    result.GetProperty().SetAmbient(.18)
    result.GetProperty().SetDiffuse(.78)
    return result


def label(renderer, message, x, y, size):
    text = vtk.vtkTextActor()
    text.SetInput(message)
    text.SetPosition(x, y)
    style = text.GetTextProperty()
    style.SetFontSize(size)
    style.SetFontFamilyToArial()
    style.SetColor(1, 1, 1)
    renderer.AddViewProp(text)


window = vtk.vtkRenderWindow()
window.SetOffScreenRendering(1)
window.SetSize(1800, 1100)
window.SetMultiSamples(8)
background = (.035, .05, .08)
heading = vtk.vtkRenderer()
heading.SetBackground(*background)
window.AddRenderer(heading)
label(heading, 'FOX / DIAMOND KNURL', 65, 1020, 48)
label(heading, '21 flats  |  19.5 x 19.5 x 8 mm  |  CAD prototype', 65, 958, 32)
label(heading, 'Recessed fox + four textured sides', 90, 840, 32)
label(heading, 'Stack + standing wall', 1130, 840, 32)
label(heading, 'Smooth underside and contact rims. Knurl stays inside the tray-fit envelope.', 65, 102, 30)
label(heading, 'Print one sample first: grip, comfort, stacking and physical tray fit need testing.', 65, 48, 29)
def placement(x=0, y=0, z=0, wall=False):
    matrix = np.eye(4)
    if wall:
        matrix[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
    matrix[:3, 3] = [x, y, z]
    return matrix


for viewport, shapes, focal, position, scale in [
    ((.025, .18, .59, .76), [placement()], (0, 0, 4), (32, -48, 44), 14),
    ((.59, .18, 1, .76),
     [placement(-13, 0, n*f.HEIGHT) for n in range(3)] +
     [placement(17, 8, f.WIDTH/2, wall=True)],
     (2, 0, 11), (48, -95, 78), 31),
]:
    renderer = vtk.vtkRenderer()
    renderer.SetViewport(*viewport)
    renderer.SetBackground(*background)
    window.AddRenderer(renderer)
    for shape in shapes:
        renderer.AddActor(actor(shape))
    camera = renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetFocalPoint(*focal)
    camera.SetPosition(*position)
    camera.SetViewUp(0, 0, 1)
    camera.SetParallelScale(scale)
    renderer.ResetCameraClippingRange()
window.Render()
capture = vtk.vtkWindowToImageFilter()
capture.SetInput(window)
capture.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(str(ROOT / 'previews/fox-knurled-flats.png'))
writer.SetInputConnection(capture.GetOutputPort())
writer.Write()
print(ROOT / 'previews/fox-knurled-flats.png')
