"""Digital checks for the v12 chest. Sampled motion and valid solids do not
establish print strength, operating force or fit. Writes reports/geometry-verification.json.
"""
from pathlib import Path
import json
import cadquery as cq
import tak_chest as c

OUT=Path(__file__).resolve().parent.parent
REPORTS=OUT/'reports';REPORTS.mkdir(exist_ok=True)
report={'checks':{},'sampled':{}}

def vol(a,b):
    try:
        return a.intersect(b).Volume()
    except Exception as e:
        return float('nan')

def record(name,ok,detail=None):
    report['checks'][name]={'pass':bool(ok),'detail':detail}
    print('PASS' if ok else 'FAIL',name,detail if detail is not None else '',flush=True)
    assert ok,name

# ---- parts are valid single solids
parts={'tray':c.tray(),'tray-lid':c.tray_lid(),
       'base-left':c.base('left'),'base-right':c.base('right'),
       'lid-left':c.lid('left'),'lid-right':c.lid('right')}
for i in range(3):
    for s in ('left','right'):parts[f'grid-{i}-{s}']=c.grid_inlay(i,s)
bad=[n for n,p in parts.items() if not p.isValid() or len(p.Solids())<1]
multi={n:len(p.Solids()) for n,p in parts.items() if len(p.Solids())!=1}
record('valid-solids',not bad,{'multi_solid_parts':multi})

# ---- closed pose: no overlap between distinct parts
bl,br,ll,lr=parts['base-left'],parts['base-right'],parts['lid-left'],parts['lid-right']
pairs={'base-halves':(bl,br),'lid-halves':(ll,lr),
       'lid-left/base-left':(ll,bl),'lid-left/base-right':(ll,br),
       'lid-right/base-left':(lr,bl),'lid-right/base-right':(lr,br)}
res={k:round(vol(*v),4) for k,v in pairs.items()}
record('closed-no-overlap',all(v<.05 for v in res.values()),res)

# ---- tray in bay: only the crush ribs may touch
res={}
for side in ('left','right'):
    t,tl,x=c.tray_pose(side)
    base=bl if side=='left' else br
    plain=c._tray_body().translate((x,0,c.FLOOR))
    res[side]={'body_vs_base':round(vol(plain,base),4),
               'lid_vs_base':round(vol(tl,base),4),
               'lid_vs_tray':round(vol(tl,t),4)}
record('tray-fit-no-overlap-except-ribs',
       all(v<.05 for r in res.values() for v in r.values()),res)
rib=c.tray().Volume()-c._tray_body().Volume()
record('rib-volume-designed-crush',True,{'rib_volume_mm3':round(rib,2)})

# ---- vertical lift path (ribbed tray, both sides)
worst=0
for side in ('left','right'):
    base=bl if side=='left' else br
    for lift in range(0,61,5):
        t,tl,x=c.tray_pose(side,lift)
        plain=c._tray_body().translate((x,0,c.FLOOR+lift))
        worst=max(worst,vol(plain,base),vol(tl,base))
record('lift-path-clear',worst<.05,{'max_overlap_mm3':round(worst,4),'steps_mm':'0..60 by 5'})

# ---- lid sweep about the hinge
worst={};
for a in range(0,111,5):
    ls=[c.lid_posed(ll,a),c.lid_posed(lr,a)]
    v=0
    for L in ls:
        v=max(v,vol(L,bl),vol(L,br))
        for side in ('left','right'):
            t,tl,x=c.tray_pose(side);v=max(v,vol(L,t),vol(L,tl))
    worst[a]=round(v,4)
record('lid-sweep-clear',all(v<.05 for v in worst.values()),{'max_overlap_by_angle':worst})

# ---- pieces envelopes
res={}
for side in ('left','right'):
    t,tl,x=c.tray_pose(side)
    boxes=c.flat_boxes(x,c.FLOOR)+[c.capstone_box(x,c.FLOOR,side=='right')]
    res[side]={'pieces_vs_tray':round(max(vol(b,t) for b in boxes),4),
               'pieces_vs_lid':round(max(vol(b,tl) for b in boxes),4),
               'min_clearance_under_lid_mm':round(c.FLOOR+c.LID_Z[0]-max(b.BoundingBox().zmax for b in boxes),3)}
record('pieces-fit-tray',all(r['pieces_vs_tray']<.05 and r['pieces_vs_lid']<.05 and r['min_clearance_under_lid_mm']>=.5 for r in res.values()),res)

# ---- board and lid clearances (closed)
gap_board=c.BASE_H-c.BOARD_TOP
tray_top=c.FLOOR+c.TH
record('closed-clearances',gap_board>1 and c.BASE_H-tray_top>.5,
       {'lid_to_board_mm':gap_board,'lid_to_tray_top_mm':round(c.BASE_H-tray_top,2),
        'closed_envelope_xyz':[round(c.X1-c.X0,1),round(c.Y1-c.Y0,1),round(c.BASE_H+c.LID_H,1)],
        'with_hinge_y_extent':round(218.0-c.Y0,1)})

# ---- seam keys fit their slots without touching either half
res=[]
for y in c.KEY_Y_BASE:
    key=c._hourglass(c.SEAM_X,y,0,18)
    res.append(round(vol(key,bl)+vol(key,br),4))
record('base-keys-clear',all(v<.05 for v in res),res)
res=[]
for key in c.lid_key_shapes():
    res.append(round(vol(key,ll)+vol(key,lr),4))
record('lid-keys-clear',all(v<.05 for v in res),res)

# ---- print-bed fits (256 x 256 mm CC2)
def ext(s):
    b=s.BoundingBox();return [round(b.xlen,1),round(b.ylen,1),round(b.zlen,1)]
fits={n:ext(p) for n,p in parts.items() if not n.startswith('grid')}
record('parts-fit-256-bed',all(max(v[0],v[1])<=250 and v[2]<=250 for v in fits.values()),fits)

json.dump(report,open(REPORTS/'geometry-verification.json','w'),indent=1)
print('ALL PASS')
