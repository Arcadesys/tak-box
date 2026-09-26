"""Check packaged CC2 projects, including actual transformed mesh bounds."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import json,subprocess

HERE=Path(__file__).resolve().parent
PACK=HERE/'print'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
    'p':'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'}
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'

def apply(v,trans):
    a,b,c,d,e,f,g,h,i,j,k,l=map(float,trans.split())
    x,y,z=v
    return (a*x+d*y+g*z+j,b*x+e*y+h*z+k,c*x+f*y+i*z+l)

report={}
for path in sorted(PACK.rglob('*.3mf')):
    with ZipFile(path) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        assert root.attrib['unit']=='millimeter'
        cfg=json.loads(z.read('Metadata/project_settings.config'))
        assert cfg['curr_bed_type']=='Textured PEI Plate'
        objects={o.get('id'):o for o in root.findall('.//m:resources/m:object',NS)}
        boxes=[]
        for item in root.findall('.//m:build/m:item',NS):
            parent=objects[item.get('objectid')]
            comps=parent.findall('m:components/m:component',NS)
            assert len(comps)==1
            comp=comps[0]
            child=ET.fromstring(z.read(comp.get('{%s}path'%NS['p']).lstrip('/')))
            verts=child.findall('.//m:vertex',NS)
            assert verts
            points=[apply(apply(tuple(float(v.get(axis)) for axis in 'xyz'),
                                comp.get('transform')),item.get('transform'))
                    for v in verts]
            lo=[min(p[i] for p in points) for i in range(3)]
            hi=[max(p[i] for p in points) for i in range(3)]
            assert -1e-3<=lo[0] and hi[0]<=256.001,(path.name,lo,hi)
            assert -1e-3<=lo[1] and hi[1]<=256.001,(path.name,lo,hi)
            assert -1e-3<=lo[2] and hi[2]<=256.001,(path.name,lo,hi)
            boxes.append((lo,hi))
        for i,(a,b) in enumerate(boxes):
            for c,d in boxes[i+1:]:
                assert (b[0]<=c[0]+.01 or d[0]<=a[0]+.01 or
                        b[1]<=c[1]+.01 or d[1]<=a[1]+.01),path.name
    info=subprocess.run([EXE,'--info',str(path)],capture_output=True,
                        text=True,timeout=30)
    assert info.returncode==0 and info.stdout.count('manifold = yes')==len(boxes),path.name
    report[str(path.relative_to(PACK))]={'objects':len(boxes),'manifold':True,
                       'within_256_mm_bed':True,
                       'xy_bounds_mm':[round(min(b[0][0] for b in boxes),2),
                                       round(min(b[0][1] for b in boxes),2),
                                       round(max(b[1][0] for b in boxes),2),
                                       round(max(b[1][1] for b in boxes),2)]}

(PACK/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
