"""V23 R2 previews exclusively from actual exported STEP and named pieces."""
import cadquery as cq
import case as c
from loaded_pieces import loaded
from render_utils import render as draw,colors
import argparse
parser=argparse.ArgumentParser();parser.add_argument("--only");args=parser.parse_args()
def render(name,*values):
 if args.only is None or args.only==name:draw(name,*values)
colors['tray']=(.15,.45,.57);colors['stone']=(.91,.93,.95)
p={n:cq.importers.importStep(str(c.OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap' and not n.startswith('capstone')}
p['hardware']=cq.importers.importStep(str(c.OUT/'models/hardware-reference-NOT-PRINTED.step')).val()
render('01-open',[(n,c.side_hook(90) if n=='side-hook' else s) for n,s in p.items()],'V23 R2 — full 180 mm field; removable player trays beneath')
render('02-closed',[(n,c.fold(s,180) if n.endswith('right') else s) for n,s in p.items()],'V23 R2 closed — 102.5 × 200 × 35 mm')
scene=[(n,c.side_hook(90) if n=='side-hook' else s) for n,s in p.items() if not n.startswith('tray')]
for side in ('left','right'):
 offset=(-103 if side=='left' else 103,0,-2.2)
 scene.append(('tray-'+side,p['tray-'+side].translate(offset)))
 compound=cq.importers.importStep(str(c.OUT/'models'/f'tray-loaded-{side}.step')).val()
 # The exported loaded compound begins with the tray, followed by the 22 pieces.
 for s in compound.Solids()[1:]:scene.append(('stone-'+side,s.translate(offset)))
render('03-table-setup',scene,'V23 R2 — loaded trays beside the board')
scene=[(n,c.side_hook(90) if n=='side-hook' else s) for n,s in p.items() if not n.startswith('board')]
for side in ('left','right'):
 compound=cq.importers.importStep(str(c.OUT/'models'/f'tray-loaded-{side}.step')).val()
 scene.extend(('stone-'+side,s) for s in compound.Solids()[1:])
render('04-loaded-storage',scene,'V23 R2 storage — 21 flats + flat capstone in each lift-out tray',(-300,500,650))
w=c.box(75,121,-.1,11,-.1,40)
render('05-hinge-detail',[(n,s.intersect(w)) for n,s in p.items() if n.startswith('housing')],'V23 R2 — 8 mm supports, 4 mm pivots, rounded 9 mm barrels',(250,-500,350))
scene=[]
for side in ('left','right'):
 compound=cq.importers.importStep(str(c.OUT/'models'/f'tray-loaded-{side}.step')).val()
 scene.append(('tray-'+side,compound.Solids()[0]));scene.extend(('stone-'+side,s) for s in compound.Solids()[1:])
render('06-loaded-trays',scene,'V23 R2 — broad pinch handles and flat tray bottoms',(-300,500,650))
