"""Show eight distinct exported components in their verified plate positions."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
from matplotlib import font_manager
from render import view,GOLD
OUT=Path(__file__).resolve().parents[1]

def main():
    global OUT
    black='--black' in sys.argv
    if black:OUT=OUT/'BLACK'
    (OUT/'previews').mkdir(exist_ok=True)
    colour=(.12,.12,.12) if black else GOLD
    provenance=json.loads((OUT/'reports/plate-provenance.json').read_text())
    readback=json.loads((OUT/'reports/slicing.json').read_text());assert readback['passed']
    parts=[]
    for source in provenance['sources']:
        xyz=source['translation_mm'];parts.append((Path(source['source']),(xyz[0]-132,xyz[1]-116,xyz[2]),colour))
    font=font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'))
    big=ImageFont.truetype(font,42);small=ImageFont.truetype(font,32)
    canvas=Image.new('RGB',(1780,1140),'white');draw=ImageDraw.Draw(canvas)
    draw.text((40,20),('Black PLA trial — 4 samples, 8 components, provisional slot 1' if black else 'One print block — 4 samples, 8 separate components, slot 3'),font=big,fill='#101010')
    canvas.paste(view(parts,eye=(0,-45,130),size=(1700,850),zoom=1.75),(40,140))
    draw.text((40,85),'Columns: Cat capstone  |  Witch capstone  |  Cat flat  |  Witch flat',font=small,fill='#101010')
    draw.text((40,1010),'Top row: upper cups / floors. Bottom row: lower cups / bodies.',font=small,fill='#101010')
    draw.text((40,1065),'Separate parts retained in 3MF readback. No fused block or print dispatch.',font=small,fill='#101010')
    path=OUT/'previews/print-block.png';canvas.save(path);print(path,flush=True)
if __name__=='__main__':main()
