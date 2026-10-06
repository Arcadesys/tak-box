"""Readable previews from exported STEP geometry, with depth buffering."""
import cadquery as cq
import vtk
import inlays as c


def load(name):
    return cq.importers.importStep(str(c.OUT/'models'/f'{name}.step')).val()


def render(name,scene,title,top=True):
    renderer=vtk.vtkRenderer();renderer.SetBackground(.95,.95,.95)
    for s,colour in scene:
        vs,fs=s.tessellate(.04,.1)
        points=vtk.vtkPoints()
        for v in vs:points.InsertNextPoint(v.x,v.y,v.z)
        cells=vtk.vtkCellArray()
        for face in fs:
            cells.InsertNextCell(3)
            for i in face:cells.InsertCellPoint(i)
        poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*colour)
        actor.GetProperty().SetAmbient(.7 if top else .4)
        actor.GetProperty().SetDiffuse(.3 if top else .6)
        renderer.AddActor(actor)
    text=vtk.vtkTextActor();text.SetInput(title);text.SetPosition(40,1140)
    text.GetTextProperty().SetFontSize(32);text.GetTextProperty().SetColor(.06,.06,.06)
    renderer.AddViewProp(text)
    camera=renderer.GetActiveCamera()
    bounds=[s.BoundingBox() for s,_ in scene]
    center=((min(b.xmin for b in bounds)+max(b.xmax for b in bounds))/2,
            (min(b.ymin for b in bounds)+max(b.ymax for b in bounds))/2,15.3)
    camera.SetFocalPoint(*center)
    camera.SetPosition((center[0],center[1],800) if top else (-400,-450,600))
    camera.SetViewUp(0,1,0) if top else camera.SetViewUp(0,0,1)
    camera.ParallelProjectionOn();renderer.ResetCamera();camera.Zoom(.88)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1600,1200);window.AddRenderer(renderer);window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(c.OUT/'previews'/f'{name}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()


def main():
    colours={'body':(.055,.055,.055),'grid':(1,1,1),'stars':(1,1,1),'orange':(.84,.65,.30),'purple':(.72,.53,.87)}
    for silk in (False,True):
        scene=[(load(f'board-{side}-{role}'),colours[role] if silk or role not in ('orange','purple') else (1,1,1))
               for side in ('left','right') for role in colours]
        name='02-black-white-silk' if silk else '01-black-white'
        render(name,scene,'V23 | Black + white + two silk accents' if silk else 'V23 | Black + white | 180 mm field')
        if silk:
            scene += [(cq.importers.importStep(str(c.OUT.parent/'models'/f'housing-{side}.step')).val(),(.12,.12,.12)) for side in ('left','right')]
            scene += [(c.case.side_hook(90),(.12,.12,.12))]
            render('03-open-case',scene,'V23 | Flush inlays on the retained sliding boards',False)
    render('04-small-trial',[(load('coupon-'+role),colours[role]) for role in colours],
           'Print this small trial first | Black / white / two silk accents')


if __name__=='__main__':main()
