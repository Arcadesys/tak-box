"""Team Cat pawn capstone, v2: Meshy cat-b head on the CadQuery pawn foot.

The head comes from meshy_output/.../variants/cat-b (text-to-3d preview). It is
cut at its neck, scaled onto the pawn collar, given a 45-degree chin support so
it prints upright with no supports, and its hair-thin face lines are traced
with 0.6 mm wide x 0.5 mm deep grooves a 0.4 mm nozzle can reproduce.

Mesh work needs trimesh, manifold3d and scipy on top of the cadquery env:
    pip install trimesh manifold3d rtree
Writes pieces/cat-capstone-meshy.stl (mesh only; there is no STEP for it).
"""
from pathlib import Path
import tempfile
import numpy as np, trimesh, manifold3d as mf
from scipy import ndimage
import cadquery as cq
import tak_pieces as p

HERE=Path(__file__).resolve().parent
SRC=HERE/'meshy_output/20260925_174757_tak-capstones_7e9d/variants/cat-b/model.stl'
OUT=HERE/'pieces/cat-capstone-meshy.stl'

NECK=0.18          # cut height on the unit-height Meshy model (its narrowest point)
SCALE=19.2         # unit model -> mm
SEAT=9.5           # z of the cut face, sunk just inside the collar top (9.8)
GROOVE_W,GROOVE_D=0.6,0.5

def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),
                               tri_verts=np.asarray(t.faces,np.uint32)))
def to_tm(m):
    g=m.to_mesh()
    return trimesh.Trimesh(np.asarray(g.vert_properties)[:,:3],np.asarray(g.tri_verts),process=True)

def cat_head():
    m=trimesh.load(SRC)
    lo,hi=m.bounds
    m.apply_translation([-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]])
    m.apply_scale(1/m.bounds[1][2])                        # unit height, Z up, face toward -Y
    t=to_tm(to_mf(m).trim_by_plane([0,0,1],NECK))
    t.apply_translation([0,0,-NECK]);t.apply_scale(SCALE);t.apply_translation([0,0,SEAT])
    return t

def chin_support(head,z_top=11.9,dz=0.1,sectors=120):
    """Star-shaped solid whose radius per sector never shrinks faster than
    45 deg going down, so the head's underside has something to print on.
    Stops below the muzzle; the sphere is self-supporting above ~z10.8."""
    zs=np.arange(9.0,z_top,dz)
    v=head.vertices;v=v[v[:,2]<zs[-1]+dz]
    th=np.arctan2(v[:,1],v[:,0]);r=np.hypot(v[:,0],v[:,1])
    sec=((th+np.pi)/(2*np.pi)*sectors).astype(int)%sectors
    zi=((v[:,2]-zs[0])/dz).astype(int)
    rr=np.zeros((sectors,len(zs)));np.maximum.at(rr,(sec,zi),r)
    rr=np.maximum(rr,np.maximum(np.roll(rr,1,0),np.roll(rr,-1,0)))
    R=np.stack([(rr[:,j:]-(zs[j:]-zs[j])[None,:]).max(1) for j in range(len(zs))],1)
    R=ndimage.median_filter(R,size=(11,1),mode='wrap')          # drop one-sector spikes
    R=ndimage.uniform_filter(R,size=(5,3),mode=('wrap','nearest'))
    R=np.maximum(R-0.15,0.5)                                    # sit just inside the head skin
    ang=(np.arange(sectors)+0.5)/sectors*2*np.pi-np.pi
    verts=[(R[i,j]*np.cos(a),R[i,j]*np.sin(a),z) for j,z in enumerate(zs) for i,a in enumerate(ang)]
    faces=[]
    for j in range(len(zs)-1):
        for i in range(sectors):
            a=j*sectors+i;b=j*sectors+(i+1)%sectors
            faces+=[(a,b,b+sectors),(a,b+sectors,a+sectors)]
    bot=len(verts);top=bot+1;last=(len(zs)-1)*sectors
    verts+=[(0,0,zs[0]),(0,0,zs[-1])]
    for i in range(sectors):
        faces+=[(bot,(i+1)%sectors,i),(top,last+i,last+(i+1)%sectors)]
    s=trimesh.Trimesh(np.array(verts),np.array(faces),process=True)
    if s.volume<0:s.invert()
    return s

# Face lines in front-view (x, z) mm, traced over cat-b's own engraving.
def mirror(pts): return [(-x,z) for x,z in pts]
EYE=[(-5.0,16.55),(-4.4,16.85),(-3.6,16.95),(-2.8,16.85),(-2.1,16.5),(-1.65,16.0)]
BROW=[(-3.7,18.55),(-2.9,18.8),(-2.05,18.9)]
WHISKERS=[[(-5.75,15.6),(-3.8,15.1)],[(-5.65,14.6),(-3.8,14.6)],[(-5.45,13.65),(-3.75,14.1)]]
LINES=[EYE,mirror(EYE),BROW,mirror(BROW)]+WHISKERS+[mirror(w) for w in WHISKERS]

def face_grooves(head,step=0.15):
    """Sweep a round-ended cutter along each line, projected onto the face
    from the front; depth is measured along the local surface normal."""
    cutters=[]
    for ln in map(np.array,LINES):
        pts=[a+(b-a)*t for a,b in zip(ln[:-1],ln[1:])
             for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/step)),endpoint=False)]+[ln[-1]]
        pts=np.array(pts)
        origins=np.c_[pts[:,0],np.full(len(pts),-30.0),pts[:,1]]
        locs,idx,tri=head.ray.intersects_location(origins,np.tile([0,1,0],(len(pts),1)),
                                                  multiple_hits=False)
        order=np.argsort(idx);locs,idx,tri=locs[order],idx[order],tri[order]
        assert len(idx)==len(pts)
        pegs=[]
        for L,t in zip(locs,tri):
            dy=min(GROOVE_D/max(abs(head.face_normals[t][1]),0.3),1.4)
            pegs.append(mf.Manifold.cylinder(12,GROOVE_W/2,GROOVE_W/2,16)
                        .rotate([-90,0,0]).translate([L[0],L[1]+dy-12,L[2]]))
        cutters+=[mf.Manifold.batch_hull([a,b]) for a,b in zip(pegs[:-1],pegs[1:])]
    return mf.Manifold.batch_boolean(cutters,mf.OpType.Add)

def cat_capstone_meshy():
    with tempfile.TemporaryDirectory() as tmp:
        cq.exporters.export(p.pawn_base(),f'{tmp}/base.stl',tolerance=.01,angularTolerance=.05)
        base=trimesh.load(f'{tmp}/base.stl')
    head=cat_head()
    body=mf.Manifold.batch_boolean([to_mf(base),to_mf(head),to_mf(chin_support(head))],mf.OpType.Add)
    return to_tm(body-face_grooves(head))

if __name__=='__main__':
    out=cat_capstone_meshy()
    lo,hi=out.bounds;dia=2*np.hypot(out.vertices[:,0],out.vertices[:,1]).max()
    assert out.is_watertight and dia<=19.8 and hi[2]<=25.41,(dia,hi)   # D19.8 x 25.4 keystone
    out.export(OUT)
    print(OUT.name,'dia',round(dia,2),'h',round(hi[2],2),'vol',round(out.volume,1))
