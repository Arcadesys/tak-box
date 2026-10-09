"""Depth-buffered renders from actual exported STEP, including hinge hardware."""
import cadquery as cq
import vtk
import case as c
OUT=c.OUT
parts={n:cq.importers.importStep(str(OUT/'models'/f'{n}.step')).val() for n in c.parts() if n!='axle-end-cap' and not n.startswith('capstone-')}
parts['hardware']=cq.importers.importStep(str(OUT/'models/hardware-reference-NOT-PRINTED.step')).val()
from render_utils import render
render('01-open',[(n,c.hook_rotate(s,c.HOOK_OPEN_ANGLE) if n=='side-hook' else s) for n,s in parts.items()],'V23 open — 180 mm field, sliding boards over fixed pockets')
render('02-closed',[(n,c.fold(s,180) if n.endswith('-right') else s) for n,s in parts.items()],'V23 seamless — recessed center hook, integrated hinge ends')
scene=[]
for n,s in parts.items():
 if n=='side-hook':s=c.hook_rotate(s,c.HOOK_OPEN_ANGLE)
 if n.startswith('board'):s=c.slide(c.board(n.split('-')[1],c.BOARD_RELEASE),n.split('-')[1],c.BOARD_TRAVEL)
 scene.append((n,s))
scene += [('capstone-'+team,c.stored_capstone(team,side)) for team,side in [('cat','left'),('witch','right')]]
render('03-access',scene,'V23 access — release front buttons, slide boards outward')
window=c.box(-1,13,66,126,-1,34)
closed=[(n,c.fold(s,180) if n.endswith('-right') else s) for n,s in parts.items()]
for filename,angle,title in [('04-hook-closed',0,'V23 side hook — CLOSED over the headed pin'),('05-hook-open',c.HOOK_OPEN_ANGLE,'V23 side hook — SWING 90 degrees into the recess to release')]:
 closeup=[]
 for n,s in closed:
  if n=='side-hook':s=c.hook_rotate(s,angle)
  clipped=s.intersect(window)
  if clipped.Volume()>1e-5:closeup.append((n,clipped))
 render(filename,closeup,title)
print('Five depth-buffered STEP readback previews generated.')

cat=cq.importers.importStep(str(OUT/'models/capstone-cat.step')).val().translate((-18,0,0))
witch=cq.importers.importStep(str(OUT/'models/capstone-witch.step')).val().translate((18,0,0))
cap_scene=[]
for shape in (cat,witch):
 cap_scene += [('capbody',shape.intersect(c.box(-60,60,-30,30,-.1,6.8))),('capdetail',shape.intersect(c.box(-60,60,-30,30,6.8,8.1)))]
render('09-flat-capstones',cap_scene,'V23 flat capstones — 8 mm tall; optional contrast paint shown')

window=c.box(86,103,-.1,12,-.1,33)
scene=[]
for n,s in closed:
 clipped=s.intersect(window)
 if clipped.Volume()>1e-5:scene.append((n,clipped))
render('12-rounded-hinge-end',scene,'V23 hinge end — rounded shoulders within the case length',(250,-500,400))

window=c.box(-.1,13,66,126,-.1,33)
trial=[]
for n,s in closed:
 clipped=s.intersect(window)
 if clipped.Volume()>1e-5:trial.append((n,clipped))
render('10-exterior-trial-closed',trial,'V23 centered hook — all hardware within the side outline',(-500,-150,300))
render('11-exterior-trial-open',[(n,c.hook_rotate(s,90) if n=='side-hook' else s) for n,s in trial],'V23 hook parked — below the sliding board path',(-500,-150,300))
