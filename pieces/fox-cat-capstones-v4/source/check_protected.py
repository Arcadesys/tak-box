"""Check exported protected Cat geometry and byte-identical Fox reuse."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    old=trimesh.load(ROOT/'raw/cat-v3.stl',force='mesh').subdivide()
    new=trimesh.load(ROOT/'models/cat-capstone.stl',force='mesh')
    x,y,z=old.vertices.T;tree=cKDTree(new.vertices)
    regions={'base_and_tail':z<=8.4,'upper_head_and_ears':z>=16.6,
        'far_cheek':(z>=15)&(x<=-.5),'muzzle':(z>=13.8)&(x<=-1.5)&(y<=.4)}
    report={'cat_protected_regions':{},'tolerance_mm':2e-6}
    for name,mask in regions.items():
        maximum=float(tree.query(old.vertices[mask])[0].max())
        assert maximum<=2e-6,(name,maximum)
        report['cat_protected_regions'][name]={'vertices':int(mask.sum()),'max_distance_mm':maximum}
    current=ROOT/'models/fox-capstone.stl'
    expected=json.loads((ROOT/'reports/protected-geometry.json').read_text())['fox_sha256']
    assert hashlib.sha256(current.read_bytes()).hexdigest()==expected
    report.update({'fox_sha256':expected,'fox_byte_identical_to_v3':True})
    (ROOT/'reports/protected-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: protected Cat regions within STL serialization tolerance; Fox byte-identical')
