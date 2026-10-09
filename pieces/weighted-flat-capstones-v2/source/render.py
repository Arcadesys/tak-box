"""Accessible previews made only from exported V2 geometry."""
from pathlib import Path
import json
import cadquery as cq
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from matplotlib import font_manager
import build as b
OUT=Path(__file__).resolve().parents[1]
GOLD=(.64,.40,.09);LIGHT=(.78,.68,.43)

def mesh_for(label,obj):
    path=OUT/'previews'/f'{label}-preview.stl';b.v1.export_stl(obj,path);return path

def view(parts,eye=(45,-60,65),size=(850,500),zoom=1.08):
    ren=vtk.vtkRenderer();ren.SetBackground(.96,.96,.96)
    for path,position,colour in parts:
        reader=vtk.vtkSTLReader();reader.SetFileName(str(path));reader.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(reader.GetOutputPort())
        actor=vtk.vtkActor();actor.SetMapper(mapper);actor.SetPosition(*position)
        actor.GetProperty().SetColor(*colour);actor.GetProperty().SetAmbient(.3);actor.GetProperty().SetDiffuse(.7);ren.AddActor(actor)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(*size);win.AddRenderer(ren)
    camera=ren.GetActiveCamera();camera.SetPosition(*eye);camera.SetFocalPoint(0,0,3);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn()
    ren.ResetCamera();camera.Zoom(zoom);win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.Update()
    data=capture.GetOutput();w,h,_=data.GetDimensions();pixels=vtk_to_numpy(data.GetPointData().GetScalars()).reshape(h,w,-1)
    image=Image.fromarray(np.flipud(pixels).copy()).convert('RGB');win.Finalize();return image

def page(title,height):
    image=Image.new('RGB',(1780,height),'white');draw=ImageDraw.Draw(image);draw.text((40,20),title,font=BIG,fill='#101010');return image,draw

def main():
    global BIG,SMALL
    font=font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'));BIG=ImageFont.truetype(font,42);SMALL=ImageFont.truetype(font,32)
    overview,draw=page('Four-piece sample — all components use silk PLA slot 3',1320)
    opened,od=page('Capstones — equal 4 mm external halves, internal lip + snaps',790)
    sections,sd=page('Actual joint sections — snaps back up the epoxy seal',880)
    report=json.loads((OUT/'reports/geometry.json').read_text())
    for col,team in enumerate(('cat','witch')):
        x=40+col*870;name='CAT' if team=='cat' else 'WITCH HAT'
        cap=cq.importers.importStep(str(OUT/'models'/f'{team}-capstone-assembled.step'))
        cp=mesh_for(team+'-assembled',cap)
        regular=cq.importers.importStep(str(OUT/'models'/f'{team}-regular-assembled.step'))
        rp=mesh_for(team+'-regular-assembled',regular)
        overview.paste(view([(cp,(0,0,0),GOLD)]),(x,140));draw.text((x,90),name+' capstone — midpoint seam',font=SMALL,fill='#101010')
        overview.paste(view([(rp,(0,0,0),GOLD)],eye=(45,-65,30)),(x,735))
        draw.text((x,680),'CAT flat — recessed diamonds' if team=='cat' else 'WITCH flat — existing finish',font=SMALL,fill='#101010')
        lower=OUT/'models'/f'{team}-capstone-lower.stl';upper=OUT/'models'/f'{team}-capstone-upper.stl'
        opened.paste(view([(lower,(-16,0,0),GOLD),(upper,(16,0,0),GOLD)],eye=(40,-60,95)),(x,145))
        od.text((x,90),name+' — two separate printable cups',font=SMALL,fill='#101010')
        # Restore the upper cup to its assembled pose, then take a real thin
        # CAD section through the first hook's centre, in that hook's frame.
        lower_cad=cq.importers.importStep(str(OUT/'models'/f'{team}-capstone-lower.step'))
        upper_cad=cq.importers.importStep(str(OUT/'models'/f'{team}-capstone-upper.step')).rotate((0,0,0),(1,0,0),180).translate((0,0,8))
        frame=report['capstones'][team]['snap_frames'][0]
        paths=[]
        for suffix,obj,colour in (('lower',lower_cad,GOLD),('upper',upper_cad,LIGHT)):
            obj=obj.translate((-frame['origin_xy'][0],-frame['origin_xy'][1],0)).rotate((0,0,0),(0,0,1),-frame['angle_deg'])
            section=b.common(obj,b.box(-4.0,.1,0,.25,.65,6.3))
            paths.append((mesh_for(team+'-'+suffix+'-section',section),(0,0,0),colour))
        sections.paste(view(paths,eye=(0,-100,3),size=(850,570),zoom=1.05),(x,145));sd.text((x,90),name+' — cut through a retaining tab',font=SMALL,fill='#101010')
    draw.text((40,1250),'Four assembled pieces   |   Eight separate parts   |   V26 envelope retained',font=SMALL,fill='#101010')
    od.text((40,680),'Lower: hidden lip, guarded flex tabs. Upper: recess and retaining pockets.',font=SMALL,fill='#101010')
    od.text((40,730),'Capstone usable fill: 0.860 mL each. Physical retention still unverified.',font=SMALL,fill='#101010')
    sd.text((40,740),'Midpoint: Z4 mm   |   Epoxy seam: 0.05 mm   |   Radial barb capture: 0.35 mm',font=SMALL,fill='#101010')
    sd.text((40,795),'Grain guard separates fill from the flex space. Printed retention needs testing.',font=SMALL,fill='#101010')
    for name,picture in (('four-piece-sample.png',overview),('capstone-halves.png',opened),('capstone-joint-sections.png',sections)):
        path=OUT/'previews'/name;picture.save(path);print(path,flush=True)
if __name__=='__main__':main()
