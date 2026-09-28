"""Compare every 3MF triangle to its source STL after slicer recentering."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib,json,struct,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import cKDTree
from package_trials import PLATES
OUT=Path(__file__).resolve().parent.parent
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
report={}
for name,(stems,_,_) in PLATES.items():
    plate=OUT/'plates'/('plate'+name+'.3mf');rows=[]
    with ZipFile(plate) as z:
        for stem in stems:
            src=OUT/'models'/(stem+'.stl');data=src.read_bytes();n=struct.unpack_from('<I',data,80)[0]
            sv=np.array([struct.unpack_from('<3f',data,84+i*50+12+j*12) for i in range(n) for j in range(3)])
            sv-=sv.min(axis=0);unique,inv=np.unique(sv,axis=0,return_inverse=True)
            path=next(k for k in z.namelist() if k.startswith('3D/Objects/'+src.name+'_') and k.endswith('.model'))
            doc=ET.fromstring(z.read(path));verts=doc.findall('.//m:vertex',NS);tris=doc.findall('.//m:triangle',NS)
            mv=np.array([[float(v.attrib[a]) for a in 'xyz'] for v in verts]);mv-=mv.min(axis=0)
            distances,idx=cKDTree(unique).query(mv)
            assert float(distances.max())<.00002,(stem,'vertex drift',distances.max())
            source=Counter(tuple(sorted(t)) for t in inv.reshape(-1,3))
            target=Counter(tuple(sorted(int(idx[int(t.attrib[a])]) for a in ('v1','v2','v3'))) for t in tris)
            assert source==target,(stem,'triangle mismatch')
            rows.append({'source':src.name,'source_sha256':hashlib.sha256(data).hexdigest(),'triangles':n,'max_vertex_error_mm':float(distances.max()),'triangle_topology_matches':True})
    report[name]={'plate_sha256':hashlib.sha256(plate.read_bytes()).hexdigest(),'meshes':rows}
(OUT/'reports/packaged-mesh-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',sum(len(v['meshes']) for v in report.values()),'packaged meshes across',len(report),'plates')
