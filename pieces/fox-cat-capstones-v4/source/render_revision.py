"""Before/after views of exported Cat geometry using identical cameras."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import trimesh
from render import render
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    for view,camera in [('front',(0,-80,12)),('three-quarter',(35,-75,33))]:
        sheet=Image.new('RGB',(1300,850),(6,9,14))
        for i,stage in enumerate(['before','after']):
            path=ROOT/'raw/cat-v3.stl' if stage=='before' else ROOT/'models/cat-capstone.stl'
            mesh=trimesh.load(path,force='mesh')
            dest=ROOT/'previews'/f'cat-{view}-{stage}.png'
            render(mesh,dest,'CAT V3 BEFORE' if stage=='before' else 'CAT V4 REVISED',camera=camera,note='Original shoulder strip' if stage=='before' else 'Reshaped neck and shoulder')
            sheet.paste(Image.open(dest),(i*650,0))
        sheet.save(ROOT/'previews'/f'cat-{view}-before-after.png')
    pair=Image.new('RGB',(1300,850),(6,9,14))
    pair.paste(Image.open(ROOT/'previews/fox-three-quarter.png'),(0,0))
    pair.paste(Image.open(ROOT/'previews/cat-three-quarter-after.png'),(650,0))
    pair.save(ROOT/'previews/fox-cat-revised.png')
