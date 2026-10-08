"""Large-label previews from the actual exported STEP/STL pieces."""
from pathlib import Path
import sys
import cadquery as cq
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
sys.path.insert(0,str(REPO/'v16-field-book/source'))
from mesh_export import export_stl

def view(parts):
    ren=vtk.vtkRenderer();ren.SetBackground(.96,.96,.96)
    for path,x,colour in parts:
        reader=vtk.vtkSTLReader();reader.SetFileName(str(path));reader.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(reader.GetOutputPort())
        actor=vtk.vtkActor();actor.SetMapper(mapper);actor.SetPosition(x,0,0)
        actor.GetProperty().SetColor(*colour);actor.GetProperty().SetAmbient(.25);actor.GetProperty().SetDiffuse(.75)
        ren.AddActor(actor)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(900,520);win.AddRenderer(ren)
    camera=ren.GetActiveCamera();camera.SetPosition(45,-60,85);camera.SetFocalPoint(0,0,3);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn()
    ren.ResetCamera();camera.Zoom(1.13);win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.Update()
    data=capture.GetOutput();w,h,_=data.GetDimensions()
    pixels=vtk_to_numpy(data.GetPointData().GetScalars()).reshape(h,w,-1)
    image=Image.fromarray(np.flipud(pixels).copy()).convert('RGB');win.Finalize();return image

def main():
    font=font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'))
    big=ImageFont.truetype(font,46);small=ImageFont.truetype(font,32)
    canvas=Image.new('RGB',(1880,1380),'white');draw=ImageDraw.Draw(canvas)
    draw.text((40,20),'Weighted V26 sample — exported geometry',font=big,fill='#101010')
    for col,team,colour in ((0,'cat',(.72,.31,.05)),(1,'witch',(.43,.12,.64))):
        assembled=cq.importers.importStep(str(OUT/'models'/f'{team}-capstone-assembled.step'))
        path=OUT/'previews'/f'{team}-assembled-preview.stl';export_stl(assembled,path)
        x=40+col*920
        canvas.paste(view([(path,0,colour)]),(x,145))
        canvas.paste(view([(OUT/'models'/f'{team}-capstone-body.stl',-16,colour),(OUT/'models'/f'{team}-capstone-floor.stl',16,(.45,.45,.45))]),(x,735))
        name='CAT' if team=='cat' else 'WITCH HAT'
        draw.text((x,90),name+' — assembled',font=small,fill='#101010')
        draw.text((x,680),name+' — body and snap floor',font=small,fill='#101010')
    draw.text((40,1270),'8 mm tall   |   0.989 mL usable fill each   |   Snap hooks + epoxy seal',font=small,fill='#101010')
    draw.text((40,1320),'CAD and slicer evidence only. Physical fit and retention still need testing.',font=small,fill='#101010')
    path=OUT/'previews/weighted-cat-witch.png';canvas.save(path);print(path,flush=True)
if __name__=='__main__':main()
