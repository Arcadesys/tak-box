"""Render digital views of the v13 book from its CAD. Pieces are envelopes."""
from pathlib import Path
import sys
import vtk
import tak_book as c

OUT=Path(__file__).resolve().parent.parent
PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
SHELL=(.86,.88,.9);PLATE=(.96,.95,.92);GRID=(.08,.09,.11);TRAY=(.45,.5,.58)
CLASP=(.75,.6,.3);CAT=(1.,.6,.2);WITCH=(.72,.5,1.);BG=(.03,.04,.06)

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
    p=t.GetTextProperty();p.SetFontFamilyToArial();p.SetFontSize(size);p.SetColor(.98,.99,1.)
    if bold:p.BoldOn()
    r.AddViewProp(t)

def render(name,title,caption,items,cam,focal,scale,up=(0,0,1)):
    w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1500,1000);w.SetMultiSamples(8)
    r=vtk.vtkRenderer();r.SetBackground(*BG);w.AddRenderer(r)
    for s,col in items:r.AddActor(actor(s,col))
    v=r.GetActiveCamera();v.ParallelProjectionOn();v.SetPosition(*cam);v.SetFocalPoint(*focal);v.SetViewUp(*up);v.SetParallelScale(scale)
    r.ResetCameraClippingRange()
    text(r,title,38,923,41,True);text(r,caption,40,68,26)
    text(r,'DIGITAL CAD / PIECES SHOWN AS ENVELOPES / PHYSICAL FIT PENDING',40,25,20)
    w.Render();f=vtk.vtkWindowToImageFilter();f.SetInput(w);f.Update()
    pw=vtk.vtkPNGWriter();pw.SetFileName(str(PREV/name));pw.SetInputConnection(f.GetOutputPort());pw.Write()
    print(name,flush=True)

def scene(angle,pulls=(0,0),pieces=False,clasp_angle=None):
    ca=(90 if angle<180 else 0) if clasp_angle is None else clasp_angle
    cols=[SHELL,PLATE,GRID,TRAY]
    items=list(zip(c.leaf_a(pulls[0]),cols))+list(zip(c.leaf_b(angle,pulls[1]),cols))
    items.append((c.clasp(ca),CLASP))
    if pieces:
        for side,col,p in (('A',CAT,pulls[0]),('B',WITCH,pulls[1])):
            for b in c.piece_boxes(side,p):
                items.append((b if side=='A' else c.fold(b,angle) if angle else b,col))
    return items

cx,cy=c.WX/2,c.WY/2
render('01-closed.png','Tak v13 - closed book','71 x 141 x 45 mm. Board folded inside; M3 clasp on the back.',
       scene(180),(cx-260,cy+330,260),(35,70,22),120)
render('02-open-board.png','Tak v13 - open: board folds out flat','136 x 141 x 26 mm open. The 5 x 5 board, 24 mm pitch, folds along the middle.',
       scene(0),(cx+120,-300,340),(cx,cy,10),120)
render('03-trays-out.png','Tak v13 - slide out the piece trays','One tray under each half. Each holds 21 flats (two-high) and its capstone.',
       scene(0,(95,95),True),(cx+150,-330,300),(cx,cy-45,10),140)
render('04-half-open.png','Tak v13 - folding','The hinge runs along the middle line of the board.',
       scene(110),(cx+60,-320,200),(cx,cy,40),125)
