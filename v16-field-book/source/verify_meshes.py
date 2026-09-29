"""Every released STL must be closed, consistently oriented, positive volume."""
from collections import Counter
from pathlib import Path
import json,struct
import numpy as np

OUT=Path(__file__).resolve().parent.parent

def check(path):
    d=path.read_bytes();n=struct.unpack_from('<I',d,80)[0]
    assert len(d)==84+50*n,path.name
    a=np.frombuffer(d,dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]),count=n,offset=84)
    v=a['v'].astype(np.float64)
    ids={};tri=[]
    for t in v:
        row=[]
        for p in t:
            k=tuple(p.astype(np.float32).tolist());row.append(ids.setdefault(k,len(ids)))
        assert len(set(row))==3,(path.name,'degenerate')
        tri.append(row)
    e=Counter()
    for a_,b_,c_ in tri:
        for u,w in ((a_,b_),(b_,c_),(c_,a_)):e[(u,w)]+=1
    open_edges=[k for k,x in e.items() if x!=1 or e.get((k[1],k[0]))!=1]
    volume=float(np.einsum('ij,ij->',v[:,0],np.cross(v[:,1],v[:,2]))/6)
    assert not open_edges,(path.name,'open/misoriented edges',len(open_edges))
    assert volume>0,(path.name,'volume',volume)
    return {'triangles':n,'volume_mm3':round(volume,2)}

report={}
for p in sorted((OUT/'stl').rglob('*.stl')):
    report[str(p.relative_to(OUT))]=check(p)
json.dump(report,open(OUT/'reports'/'mesh-verification.json','w'),indent=1)
print('PASS',len(report),'meshes')
