"""Render real exported meshes, with large white labels on a dark background."""
from pathlib import Path
import argparse
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk

ROOT = Path(__file__).resolve().parents[1]

def actor(mesh, color=(.92, .77, .47)):
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(np.asarray(mesh.vertices), deep=True))
    cells = vtk.vtkCellArray()
    for face in mesh.faces:
        cells.InsertNextCell(3, [int(v) for v in face])
    data = vtk.vtkPolyData()
    data.SetPoints(points)
    data.SetPolys(cells)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(data)
    result = vtk.vtkActor()
    result.SetMapper(mapper)
    p = result.GetProperty()
    p.SetColor(*color)
    p.SetAmbient(.24)
    p.SetDiffuse(.76)
    p.SetInterpolationToFlat()
    return result

def text(renderer, message, x, y, size):
    a = vtk.vtkTextActor()
    a.SetInput(message)
    a.SetPosition(x,y)
    p=a.GetTextProperty()
    p.SetFontSize(size)
    p.SetColor(1,1,1)
    p.SetFontFamilyToArial()
    renderer.AddViewProp(a)

def render(mesh, destination, title, camera=(35,-75,33), scale=17, size=(650,850), note='', extras=(), focus=(0,0,12)):
    r = vtk.vtkRenderer()
    r.SetBackground(.025,.035,.055)
    w = vtk.vtkRenderWindow()
    w.SetOffScreenRendering(1)
    w.SetSize(*size)
    w.SetMultiSamples(8)
    w.AddRenderer(r)
    r.AddActor(actor(mesh))
    for extra,color in extras: r.AddActor(actor(extra,color))
    text(r,title,25,size[1]-65,38)
    if note: text(r,note,25,25,22)
    c = r.GetActiveCamera()
    c.ParallelProjectionOn()
    c.SetFocalPoint(*focus)
    c.SetPosition(*camera)
    c.SetViewUp(0,0,1)
    c.SetParallelScale(scale)
    r.ResetCameraClippingRange()
    w.Render()
    capture=vtk.vtkWindowToImageFilter()
    capture.SetInput(w)
    capture.Update()
    writer=vtk.vtkPNGWriter()
    writer.SetFileName(str(destination))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    w.Finalize()

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--raw',action='store_true')
    p.add_argument('--species',nargs='+',default=['fox','cat'],choices=['fox','cat'])
    args=p.parse_args()
    ROOT=args.root.resolve()
    (ROOT/'previews').mkdir(exist_ok=True)
    for species in args.species:
        path=ROOT/'raw'/f'{species}-oriented.ply' if args.raw else ROOT/'models'/f'{species}-capstone.stl'
        m=trimesh.load(path,force='mesh')
        for view,position in [('front',(0,-80,12)),('left',(-80,0,12)),('back',(0,80,12)),('right',(80,0,12)),('three-quarter',(35,-75,33))]:
            render(m,ROOT/'previews'/f'{species}-{view}{"-raw" if args.raw else ""}.png',f'{species.upper()} | {view.upper()}',position,note='Unfinished reconstruction' if args.raw else 'Actual printable mesh | mm')
