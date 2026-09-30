"""Compose labeled front, side and back renders after rendering the STL."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'reports'/'verification.json').read_text())
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',38)
for species,report in data['species'].items():
    sheet=Image.new('RGB',(1950,940),(6,9,14))
    for i,view in enumerate(['front','left','back']):
        sheet.paste(Image.open(ROOT/'previews'/f'{species}-{view}.png'),(i*650,0))
    size=' x '.join(f'{n:.3f}' for n in report['dimensions_mm'])
    ImageDraw.Draw(sheet).text((30,865),f'{species.upper()} | {size} mm | Physical fit untested',font=font,fill='white')
    sheet.save(ROOT/'previews'/f'{species}-front-side-back.png')
