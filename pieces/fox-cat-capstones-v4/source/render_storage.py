"""Actual stored meshes with a cropped view of the current v16 tray and insert."""
from pathlib import Path
import argparse
import trimesh
from verify import c,sh_mesh,ROOT
from render import render

p=argparse.ArgumentParser()
p.add_argument('--species',nargs='+',default=['fox','cat'],choices=['fox','cat'])
args=p.parse_args()
crop=c.box(0,47,0,34,0,30)
tray=sh_mesh(c.tray_a().intersect(crop))
insert=sh_mesh(c.tray_insert_a().intersect(crop))
for species in args.species:
    mesh=trimesh.load(ROOT/'models'/f'{species}-storage-pose.stl',force='mesh')
    render(mesh,ROOT/'previews'/f'{species}-v16-storage.png',f'{species.upper()} IN V16 | TRAY + INSERT',
        camera=(65,-50,70),focus=(21,15,9),scale=28,size=(1200,1000),
        note='Actual mesh | tray cropped to show saddle | Physical fit untested',extras=[(tray,(.3,.38,.48)),(insert,(.73,.8,.87))])
