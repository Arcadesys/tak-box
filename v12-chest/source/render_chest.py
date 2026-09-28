"""Render digital views of the v12 chest from its CAD. Pieces are clearance envelopes."""
from pathlib import Path
import sys
import vtk
import tak_chest as c

OUT=Path(__file__).resolve().parent.parent
PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
WOOD=(.62,.42,.27);LID=(.55,.36,.22);GRID=(.06,.07,.09);TRAY=(.78,.82,.88)
TLID=(.55,.62,.72);CAT=(1.,.6,.2);WITCH=(.72,.5,1.);BG=(.03,.04,.06)

def actor(shape,color):
    verts,tris=shape.tessellate(.08,.2)
    pts=vtk.vtkPoints();cells=vtk.vtkCellArray()
    for p in verts:pts.InsertNextPoint(p.x,p.y,p.z)
    for t in tris:
        cells.InsertNextCell(3)
        for i in t:cells.InsertCellPoint(i)
    poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
    n=vtk.vtkPolyDataNormals();n.SetInputData(poly);n.ConsistencyOn();n.AutoOrientNormalsOn();n.Update()
    m=vtk.vtkPolyDataMapper();m.SetInputConnection(n.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(m);pr=a.GetProperty()
    pr.SetColor(*color);pr.SetAmbient(.35);pr.SetDiffuse(.65)
    return a

def text(r,msg,x,y,size,bold=False):
    t=vtk.vtkTextActor();t.SetInput(msg);t.SetPosition(x,y)
    p=t.GetTextProperty();p.SetFontFamilyToArial();p.SetFontSize(size);p.SetColor(.98,.99,1.)
    if bold:p.BoldOn()
    r.AddActor2D(t)

def render(name,title,caption,items,cam,focal,scale,up=(0,0,1)):
    if len(sys.argv)>1 and name not in sys.argv[1:]:return
    w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(1500,1000);w.SetMultiSamples(8)
    r=vtk.vtkRenderer();r.SetBackground(*BG);w.AddRenderer(r)
    for s,col in items:r.AddActor(actor(s,col))
    v=r.GetActiveCamera();v.ParallelProjectionOn();v.SetPosition(*cam);v.SetFocalPoint(*focal);v.SetViewUp(*up);v.SetParallelScale(scale)
    r.ResetCameraClippingRange()
    text(r,title,38,923,41,True);text(r,caption,40,68,26)
    text(r,'DIGITAL CAD / PIECES SHOWN AS CLEARANCE ENVELOPES / PHYSICAL FIT PENDING',40,25,20)
    w.Render();f=vtk.vtkWindowToImageFilter();f.SetInput(w);f.Update()
    pw=vtk.vtkPNGWriter();pw.SetFileName(str(PREV/name));pw.SetInputConnection(f.GetOutputPort());pw.Write()
    print(name,flush=True)

def scene(angle,lift,slide_lid=0.0,pieces=True):
    items=[]
    for s in ('left','right'):
        items.append((c.base(s),WOOD))
        for i in range(3):items.append((c.grid_inlay(i,s),GRID))
        items.append((c.lid_posed(c.lid(s),angle),LID))
    for side,l,k in (('left',lift,0),('right',lift,1)):
        t,tl,x=c.tray_pose(side,l)
        items.append((t,TRAY))
        items.append((tl.translate((0,slide_lid,0)),TLID))
        if pieces:
            col=CAT if side=='left' else WITCH
            for f in c.flat_boxes(x,c.FLOOR+l):
                items.append((f,col))
            items.append((c.capstone_box(x,c.FLOOR+l,side=='right'),col))
    return items

mid=(c.X0+c.X1)/2
render('01-closed.png','Tak v12 - closed chest','272 x 223 x 38 mm with hinge. Board is inside; lid rim protects it.',
       scene(0,0),(mid+330,-420,300),(mid,105,18),185)
render('02-open-board-inside.png','Tak v12 - open the box: board inside','Lid up 100 degrees. Two lidded trays stay seated in their bays.',
       scene(100,0),(mid+120,-330,380),(mid,120,75),235)
render('03-trays-out.png','Tak v12 - trays lift out','Each tray lifts straight up; its sliding lid opens the 21 flats and capstone.',
       scene(100,60,slide_lid=120),(mid+80,-380,330),(mid,120,85),245)
render('04-top-view.png','Tak v12 - play position','Trays beside the board, lids slid open. Top view.',
       scene(100,0,slide_lid=150,pieces=True),(mid,105,700),(mid,105,20),175,up=(0,1,0))
