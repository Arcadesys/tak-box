"""Read back final 3MF geometry and verify units, labels and STL dimensions."""
from pathlib import Path
from zipfile import ZipFile
import argparse,json,xml.etree.ElementTree as ET
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    ROOT=parser.parse_args().root.resolve()
    with ZipFile(ROOT/'models/fox-cat-capstones.3mf') as z:
        doc=ET.fromstring(z.read('3D/3dmodel.model'))
    assert doc.attrib['unit']=='millimeter'
    objects=doc.findall('m:resources/m:object',NS)
    assert len(objects)==2 and len(doc.findall('m:build/m:item',NS))==2
    report={'units':'millimeter','objects':[]}
    for obj,species in zip(objects,['fox','cat']):
        assert obj.attrib['name']==f'{species.title()} capstone'
        vertices=[[float(v.attrib[a]) for a in ['x','y','z']] for v in obj.findall('m:mesh/m:vertices/m:vertex',NS)]
        faces=[[int(v.attrib[a]) for a in ['v1','v2','v3']] for v in obj.findall('m:mesh/m:triangles/m:triangle',NS)]
        mesh=trimesh.Trimesh(vertices=vertices,faces=faces)
        stl=trimesh.load(ROOT/'models'/f'{species}-capstone.stl',force='mesh')
        assert np.allclose(mesh.extents,stl.extents,atol=1e-5)
        assert abs(mesh.volume-stl.volume)<.001
        assert mesh.is_volume and len(mesh.split())==1
        report['objects'].append({'name':obj.attrib['name'],'dimensions_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'stl_match':True})
    (ROOT/'reports/package-readback.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: two labeled millimeter objects match final STLs')
