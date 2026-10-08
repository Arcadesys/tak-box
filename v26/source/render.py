"""High-contrast review views from exported V26 CAD."""
from pathlib import Path
import importlib.util,subprocess,sys
import cadquery as cq
from PIL import Image,ImageDraw,ImageFont
import matplotlib
OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('review_build',OUT/'source/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
import render_utils as r
r.OUT=OUT;r.colors.update(clip=(.32,.47,.60),boardbody=(.12,.14,.16),boardgrid=(1,1,1),boardstars=(1,1,1),boardorange=(.9,.55,.22),boardpurple=(.7,.5,.85),hook=(.95,.55,.12),captive=(.95,.55,.12),capstone=(.20,.29,.36),moving=(.95,.55,.12),old=(.6,.65,.7))
def load(n):return cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val()
def draw(n,scene,title,sub,camera):
 r.render(n,scene,title,camera)
 p=OUT/'previews'/f'{n}.png';im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im)
 font=ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'),22)
 d.text((45,77),sub,font=font,fill='#182a35');im.save(p)
def main():
 housing=[('housing-'+s,load('housing-design-'+s)) for s in ('left','right')]
 boards=[('board'+role+'-'+side,load('board-'+side+'-'+role)) for side in ('left','right') for role in b.ROLES]
 draw('01-game-open',housing+boards+[('hook-parked',load('hook-design-parked'))],'V26 — tab-free boards / captive hook','Full playing field, PIP main hinges and fixed piece guides retained',(-500,-500,650))
 cut=b.c.box(0,64,-1,17,11,18)
 old=cq.importers.importStep(str(OUT/'reference/board-inlays/board-left-body.step')).val().intersect(cut).translate((0,23,0))
 new=load('board-left-body').intersect(cut)
 draw('02-board-clip', [('old-clip',old),('clip-solid-margin',new)],'Board release — old tab behind / solid V26 margin in front','Open the case hook, then slide the board; no flexible release tab',(-100,-180,250))
 fixture=load('housing-design-left').intersect(b.c.box(0,15,68,122,0,18));k=load('hook-design-parked')
 draw('03-captive-hook',[('housing-hook-fixture',fixture),('hook-parked',k)],'V26 — hook prints captive / parked for printing','Fixed 4 mm axle; 0.4 mm radial and face gaps; no filament pivot or loose collar',(-220,-160,160))
 section=fixture.intersect(b.c.box(-1,10,100.799,100.801,-1,14))
 hooksection=k.intersect(b.c.box(-1,10,100.799,100.801,-1,14))
 draw('04-hook-section',[('housing-bearing',section),('hook-bearing',hooksection)],'Captive hook — cutaway through actual CAD','Fixed 4 mm axle and 0.4 mm running gaps; physical release and retention remain untested',(4,-300,5.8))
 closed=[(n,b.c.fold(s,180) if n.endswith('right') else s) for n,s in housing+boards]+[('hook-closed',load('hook-design-closed'))]
 draw('05-closed',closed,'V26 — closed case / 102.5 × 200 × 35 mm','Hook lever and keeper retained; release effort and transport retention need physical checks',(300,-500,350))
 draw('06-fixed-guides',housing+[('hook-parked',load('hook-design-parked'))],'V26 — fixed piece guides retained','21 flat stones and one flat capstone per side; no removable trays',(-300,500,650))
 draw('12-case-plate',[(n,load(n)) for n in ('housing-left','housing-right','captive-hook')],'Plate 1 — PIP bodies, fixed guides and captive hook','Keep all three captive components together in their existing placement',(100,100,900))
 from board_plate import mesh
 placed=[]
 for side,x in (('left',7),('right',121)):
  parts={role:load('board-'+side+'-'+role) for role in b.ROLES}
  bounds=mesh(parts['body']).bounds
  shift=(x-bounds[0,0],7-bounds[0,1],-bounds[0,2])
  placed.extend(('board'+role+'-'+side,s.translate(shift)) for role,s in parts.items())
 draw('13-board-plate',placed,'Plate 2 — full-size four-colour boards','Slots: 1 black; 2 white; 3 orange accent; 4 purple accent',(112,103,900))
 draw('14-capstone-plate',[(n,load(n)) for n in ('capstone-cat','capstone-witch')],'Plate 3 — original flat capstones','Left: Cat. Right: Witch. Optional 8 mm replacements.',(50,-160,280))

def corner_detail():
 window=b.c.box(-.1,12,-.1,15,-.1,18)
 housing=load('housing-design-left').intersect(window)
 board=load('board-reference-left').intersect(window)
 draw('18-rounded-corner',[('housing-left',housing),('boardbody-left',board)],'Outside corners — modest rounds','Case: 4 mm radius. Board: 2 mm radius. Field, guides and hinge supports retained.',(-130,-150,150))

def hinge_detail():
 left=load('housing-design-left');right=load('housing-design-right')
 window=b.c.box(86,110,-.1,11,0,23)
 draw('16-main-hinge',[('housing-fixed-supports',left.intersect(window)),('moving-central-barrel',right.intersect(window))],'Main hinge — fixed axle between two supports','Two outer supports and axle: fixed half. Centre barrel: moving half.',(260,-170,190))
 slab=b.c.box(97.999,98.001,-.1,9.6,10,23)
 draw('17-main-hinge-section',[('housing-fixed-axle',left.intersect(slab)),('moving-central-barrel',right.intersect(slab))],'Main hinge section — trapped moving barrel','Integral 4 mm axle; two 2.5 mm supports; 0.4 mm radial and face gaps',(350,4.8,17.5))
if __name__=='__main__':
 if '--hinge-only' not in sys.argv:
  main()
  corner_detail()
 hinge_detail()
 subprocess.run([sys.executable,str(OUT/'source/caption.py')],check=True)
