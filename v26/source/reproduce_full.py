"""Audit the full ZIP and rebuild raw plates from bundled exported CAD."""
from pathlib import Path
from zipfile import ZipFile
import sys, json, tempfile, subprocess, hashlib, xml.etree.ElementTree as ET
import numpy as np
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    kit=OUT/'V26-PRINT-KIT.zip'
    with tempfile.TemporaryDirectory(prefix='tak-v26-full-') as tmp:
        with ZipFile(kit) as z:
            assert z.testzip() is None
            manifest=json.loads(z.read('v26/FULL-MANIFEST.json'))
            for row in manifest['files']:
                data=z.read('v26/'+row['path']);assert hashlib.sha256(data).hexdigest()==row['sha256']
            z.extractall(tmp)
        root=Path(tmp)/'v26'
        result=subprocess.run([sys.executable,str(root/'source/plates_full.py')],capture_output=True,text=True,timeout=300)
        (OUT/'reports/full-reproduction-build.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0
        ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
        results=[]
        for name in ('02-V26-FULL-SIZE-FOUR-COLOUR-tab-free-boards','03-V26-flat-capstones'):
            roots=[]
            for folder in (OUT,root):
                with ZipFile(folder/'plates'/f'{name}.3mf') as z:roots.append(ET.fromstring(z.read('3D/3dmodel.model')))
            a,b=roots
            am={o.get('name'):o.find('m:mesh',ns) for o in a.findall('m:resources/m:object',ns) if o.find('m:mesh',ns) is not None}
            bm={o.get('name'):o.find('m:mesh',ns) for o in b.findall('m:resources/m:object',ns) if o.find('m:mesh',ns) is not None}
            assert set(am)==set(bm)
            for label,m in am.items():
                def vertices(el):return np.array([[float(v.get(k)) for k in ('x','y','z')] for v in el.findall('m:vertices/m:vertex',ns)])
                assert np.array_equal(vertices(m),vertices(bm[label]))
                assert ET.tostring(m.find('m:triangles',ns))==ET.tostring(bm[label].find('m:triangles',ns))
            results.append(dict(plate=name,named_meshes=len(am),vertices_and_triangles_identical=True))
    report=dict(passed=True,command=[sys.executable,str(Path(__file__).resolve())],zip_sha256=sha(kit),audited_files=len(manifest['files']),plates=results,
        scope='All ZIP payloads audited; board and capstone raw plates rebuilt from bundled STEP references. Full case CAD and slicer not independently rerun.',physical_acceptance=False)
    (OUT/'reports/full-reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Isolated raw-board/capstone plate rebuild PASS',flush=True)
if __name__=='__main__':main()
