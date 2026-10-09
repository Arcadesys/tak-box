"""Full-game and fixed-well views from exported CAD, preserving V24 inlay inputs."""
from pathlib import Path
import importlib.util
import cadquery as cq
from PIL import Image,ImageDraw,ImageFont
import matplotlib
OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('storage_build',OUT/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
import render_utils as r
r.OUT=OUT
r.colors.update(boardbody=(.055,.055,.055),boardgrid=(1,1,1),boardstars=(1,1,1),boardorange=(.84,.65,.30),boardpurple=(.72,.53,.87),filament=(.9,.58,.2),cat=(.94,.93,.85),witch=(.68,.6,.76),hook=(.25,.3,.35))
def load(name):return cq.importers.importStep(str(OUT/'models'/f'{name}.step')).val()
def draw(name,scene,title,sub,camera=(-500,-500,650)):
 r.render(name,scene,title,camera)
 p=OUT/'previews'/f'{name}.png';im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im)
 f=ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'),22)
 d.text((45,76),sub,font=f,fill='#182a35');im.save(p)
def main():
 housings=[('housing-'+side,load('housing-design-'+side)) for side in ('left','right')]
 boards=[('board'+role+'-'+side,s) for side in ('left','right') for role,s in b.board_parts(side).items()]
 pins=[]
 game=housings+boards+pins+[('hook-reference',b.c.side_hook(90))]
 for side,col,x,y in [('left','cat',26,28),('right','witch',170,136)]:
  pieces=load('pieces-reference-'+side).Solids()
  for i,px,py in [(0,x,y),(1,x,y+36),(21,62 if side=='left' else 134,100)]:
   p=pieces[i];box=p.BoundingBox();game.append((col+'-piece',p.translate((px-(box.xmin+box.xmax)/2,py-(box.ymin+box.ymax)/2,16.5-box.zmin))))
 draw('01-game-open',game,'V25 — full game / square-pocket prototype','Three-knuckle captive posts; fixed square pockets; same field and covers; physical durability unverified')
 wells=housings+pins+[('hook-reference',b.c.side_hook(90))]
 for side,col in [('left','cat'),('right','witch')]:wells.extend((col+'-piece',p) for p in load('pieces-reference-'+side).Solids())
 draw('02-fixed-wells',wells,'V25 — 21 flats + capstone in each fixed well','21 square stone pockets plus a capstone pocket per half; fixed to the floor',(-300,500,650))
 closed=[(n,b.c.fold(s,180) if n.endswith('right') else s) for n,s in housings+boards]+pins+[('hook-reference',b.c.side_hook())]
 draw('03-closed',closed,'V25 closed — 102.5 × 200 × 35 mm','Fixed / moving / fixed knuckles; V24 cover and hook references retained',(300,-500,350))
 draw('04-empty-wells',housings+pins,'V25 — little square holders restored','3.5 mm raised pocket rims on the 3.4 mm integral floor; finger notches retained',(-300,500,650))
 hinge=[(n,s.intersect(b.c.box(76,120,0,12,-.1,24))) for n,s in housings]
 draw('05-PIP-hinge',hinge,'V25 — captive PIP hinge / actual exported CAD','4 mm integral post joins both fixed ends; moving centre has 0.4 mm running clearance',(-150,-200,140))
 section=b.c.box(93,103,.1,9.5,15.0,17.5)
 cutaway=[('fixed' if n.endswith('left') else 'moving',s.intersect(section)) for n,s in housings]
 r.colors.update({'fixed':(.08,.24,.38),'moving':(.86,.65,.22)})
 draw('08-captive-post-section',cutaway,'Fixed — moving — fixed / section through the post','Both fixed outer knuckles and the post are one solid; moving centre surrounds it',(100,-15,70))
 print('Six actual-CAD full-case, hinge and central-post section views exported')
if __name__=='__main__':main()
