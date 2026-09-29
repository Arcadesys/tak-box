"""Render digital views of the v15 book from its CAD. Pieces are envelopes."""
from pathlib import Path
import sys
import vtk
import tak_book as c

OUT=Path(__file__).resolve().parent.parent
PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
SHELL=(.1,.1,.11);PLATE=(.07,.07,.08);GRID=(.93,.93,.9);TRAY=(.12,.12,.13)
ORANGE=(.95,.46,.12);PURPLE=(.5,.27,.78);CAT=ORANGE;WITCH=PURPLE;BG=(.62,.63,.64)

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
    print(name,'drawing',flush=True)
    w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1500,1000);w.SetMultiSamples(8)
    r=vtk.vtkRenderer();r.SetBackground(*BG);w.AddRenderer(r)
    for s,col in items:r.AddActor(actor(s,col))
    v=r.GetActiveCamera();v.ParallelProjectionOn();v.SetPosition(*cam);v.SetFocalPoint(*focal);v.SetViewUp(*up);v.SetParallelScale(scale)
    r.ResetCameraClippingRange()
    text(r,title,38,923,41,True);text(r,caption,40,68,26)
    text(r,'CAD / pieces are envelopes / not yet printed',40,25,20)
    w.Render();f=vtk.vtkWindowToImageFilter();f.SetInput(w);f.Update()
    pw=vtk.vtkPNGWriter();pw.SetFileName(str(PREV/name));pw.SetInputConnection(f.GetOutputPort());pw.Write()
    print(name,'written',flush=True)

def scene(angle,pulls=(0,0),pieces=False):
    items=[]
    for side,pull in (('A',pulls[0]),('B',pulls[1])):
        pose=(lambda s:s) if side=='A' else (lambda s,a=angle:c.fold(s,a))
        acc=ORANGE if side=='A' else PURPLE
        colour='orange' if side=='A' else 'purple'
        for s,col in ((c.base(side),SHELL),(c.plate(side),PLATE),(c.inlay(side),GRID),
                      (c.decor(side,'orange'),ORANGE),(c.decor(side,'purple'),PURPLE),
                      (c.tray_body(side).translate((0,-pull,0)),TRAY),
                      (c.tray_swirl(side).translate((0,-pull,0)),acc),
                      (c.tray_sparkles(side).translate((0,-pull,0)),GRID)):
            items.append((pose(s),col))
        if pieces:
            for b in c.piece_boxes(side,pull):
                items.append((pose(b),acc))
    return items

cx,cy=c.WX/2,c.WY/2
render('01-closed.png','v15 closed',f'{c.SEAM+3:.0f} x {c.WY:.0f} x 48 mm. No hardware. Press the side near the far corner to open.',
       scene(180),(cx-260,cy-330,260),(35,70,24),120)
render('02-open-board.png','v15 open','Black board, raised white grid, star dots and small orange and purple symbols. Raised lip for paint.',
       scene(0),(cx+120,-300,340),(cx,cy,10),120)
render('03-trays-out.png','v15 trays out','Press the side button, slide the tray out.',
       scene(0,(95,95),True),(cx+150,-330,300),(cx,cy-45,10),140)
render('04-half-open.png','v15 folding','A tab at the far corner pushes into a slot and clicks shut.',
       scene(110),(cx+60,-320,200),(cx,cy,40),125)
render('05-press-to-open.png','v15 press to open','Squeeze the panel between the two slits near the far corner, then lift.',
       scene(180),(-260,c.WY+190,180),(0,c.WY-17,30),60)
_trays=[]
for s_,acc in (('A',ORANGE),('B',PURPLE)):
    _trays+=[(c.tray_body(s_),TRAY),(c.tray_swirl(s_),acc),(c.tray_sparkles(s_),GRID)]
render('06-tray-art.png','v15 tray floors','A crescent moon in the player colour and white sparkles in each tray floor.',
       _trays,(cx,c.DR_Y1/2,300),(cx,c.DR_Y1/2,0),84*c.WY/142,up=(0,1,0))
_board=[]
for s_ in 'AB':
    _board+=[(c.plate(s_),PLATE),(c.inlay(s_),GRID)]
    _board+=[(d,col) for d,col in ((c.decor(s_,'orange'),ORANGE),(c.decor(s_,'purple'),PURPLE)) if d is not None]
render('07-board-symbols-top.png','v15 board from above','Star dots and one small symbol per cell at most: galaxies, planets, moons, sparkles and comets.',
       _board,(cx,cy,300),(cx,cy,0),c.WY/2+22,up=(0,1,0))
