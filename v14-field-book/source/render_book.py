"""Render digital views of the v13 book from its CAD. Pieces are envelopes."""
from pathlib import Path
import sys
import vtk
import tak_book as c

OUT=Path(__file__).resolve().parent.parent
PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
SHELL=(.2,.21,.22);PLATE=(.93,.93,.91);GRID=(.05,.05,.06);TRAY=(.3,.31,.33)
CAT=(.93,.93,.91);WITCH=(.08,.08,.09);BG=(.62,.63,.64)

def actor(shape,color):
    verts,tris=shape.tessellate(.06,.2)
    pts=vtk.vtkPoints();cells=vtk.vtkCellArray()
    for p in verts:pts.InsertNextPoint(p.x,p.y,p.z)
    for t in tris:
        cells.InsertNextCell(3)
        for i in t:cells.InsertCellPoint(i)
    poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
    n=vtk.vtkPolyDataNormals();n.SetInputData(poly);n.ConsistencyOn();n.AutoOrientNormalsOn();n.Update()
    m=vtk.vtkPolyDataMapper();m.SetInputConnection(n.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(m);pr=a.GetProperty()
    pr.SetColor(*color);pr.SetAmbient(.3);pr.SetDiffuse(.7)
    return a

def text(r,msg,x,y,size,bold=False):
    t=vtk.vtkTextActor();t.SetInput(msg);t.SetPosition(x,y)
    p=t.GetTextProperty();p.SetFontFamilyToArial();p.SetFontSize(size);p.SetColor(.05,.05,.06)
    if bold:p.BoldOn()
    r.AddViewProp(t)

def render(name,title,caption,items,cam,focal,scale,up=(0,0,1)):
    w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1500,1000);w.SetMultiSamples(8)
    r=vtk.vtkRenderer();r.SetBackground(*BG);w.AddRenderer(r)
    for s,col in items:r.AddActor(actor(s,col))
    v=r.GetActiveCamera();v.ParallelProjectionOn();v.SetPosition(*cam);v.SetFocalPoint(*focal);v.SetViewUp(*up);v.SetParallelScale(scale)
    r.ResetCameraClippingRange()
    text(r,title,38,923,41,True);text(r,caption,40,68,26)
    text(r,'CAD / pieces are envelopes / not yet printed',40,25,20)
    w.Render();f=vtk.vtkWindowToImageFilter();f.SetInput(w);f.Update()
    pw=vtk.vtkPNGWriter();pw.SetFileName(str(PREV/name));pw.SetInputConnection(f.GetOutputPort());pw.Write()
    print(name,flush=True)

def scene(angle,pulls=(0,0),pieces=False):
    cols=[SHELL,PLATE,GRID,TRAY]
    items=list(zip(c.leaf_a(pulls[0]),cols))+list(zip(c.leaf_b(angle,pulls[1]),cols))
    if pieces:
        for side,col,p in (('A',CAT,pulls[0]),('B',WITCH,pulls[1])):
            for b in c.piece_boxes(side,p):
                items.append((b if side=='A' else c.fold(b,angle) if angle else b,col))
    return items

cx,cy=c.WX/2,c.WY/2
render('01-closed.png','v14 closed','71 x 142 x 47 mm. No hardware. Two slabs and a seam.',
       scene(180),(cx-260,cy-330,260),(35,70,24),120)
render('02-open-board.png','v14 open','136 x 142 mm open. Raised black grid on white.',
       scene(0),(cx+120,-300,340),(cx,cy,10),120)
render('03-trays-out.png','v14 trays out','Press the side button, slide the tray out.',
       scene(0,(95,95),True),(cx+150,-330,300),(cx,cy-45,10),140)
render('04-half-open.png','v14 folding','Two posts on the back border snap into the other half.',
       scene(110),(cx+60,-320,200),(cx,cy,40),125)
