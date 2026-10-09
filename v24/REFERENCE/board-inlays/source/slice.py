"""Local CC2 dry slices. Silk uses a labelled generic PLA placeholder."""
from zipfile import ZipFile
import hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import cKDTree
import trimesh
import inlays as c

OUT=c.OUT
EXE='/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PROD='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def profiles():
    folder=OUT/'profiles';folder.mkdir(exist_ok=True)
    machine=json.loads((OUT.parent/'profiles/machine.json').read_text())
    (folder/'machine.json').write_text(json.dumps(machine,indent=2)+'\n')
    process=json.loads((OUT.parent/'profiles/process-case.json').read_text())
    process.update(name='V24 board inlays CC2 PLA 0.10',layer_height='0.1',
                   enable_prime_tower='1',wipe_tower_x=['212'],wipe_tower_y=['212'],
                   flush_into_infill='0',flush_into_objects='0',flush_into_support='0')
    (folder/'process.json').write_text(json.dumps(process,indent=2)+'\n')
    original=json.loads((OUT.parent/'profiles/filament-pla.json').read_text())
    for name,colour in [('black','#111111'),('white','#FFFFFF'),('silk-orange-placeholder','#D6A54C'),('silk-purple-placeholder','#B887DD')]:
        data=dict(original);data['name']='Tak '+name+' PLA @CC2';data['filament_colour']=[colour]
        if name.startswith('silk-'):
            data['filament_max_volumetric_speed']=['6']
        (folder/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')


def read_mesh(element):
    vs=[[float(v.get(k)) for k in ('x','y','z')] for v in element.find('m:vertices',NS)]
    fs=[[int(v.get(k)) for k in ('v1','v2','v3')] for v in element.find('m:triangles',NS)]
    m=trimesh.Trimesh(vertices=vs,faces=fs,process=False)
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    return m


def check_project(source,dest,silk):
    with ZipFile(source) as z:
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        expected={o.get('name'):read_mesh(o.find('m:mesh',NS)) for o in root.findall('m:resources/m:object',NS) if o.find('m:mesh',NS) is not None}
        build_count=len(root.find('m:build',NS))
    with ZipFile(dest) as z:
        assert z.testzip() is None
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
        metadata={e.get('key'):e.get('value') for e in info.findall('.//plate/metadata')}
        assert metadata['outside']=='false'
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        assert len(cfg.findall('object'))==build_count
        settings=json.loads(z.read('Metadata/project_settings.config'))
        colours=['#111111','#FFFFFF']+(['#D6A54C','#B887DD'] if silk else [])
        assert settings['filament_colour']==colours
        assert settings['enable_prime_tower']=='1' and settings['layer_height']=='0.1'
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        assert len(root.find('m:build',NS))==build_count
        seen=[];errors=[]
        for comp in root.findall('.//m:component',NS):
            oid=comp.get('objectid')
            sub=ET.fromstring(z.read(comp.get(PROD+'path').lstrip('/')))
            m=read_mesh(sub.find(".//m:object[@id='"+oid+"']/m:mesh",NS))
            part=cfg.find(".//part[@id='"+oid+"']")
            label=part.find("metadata[@key='name']").get('value')
            role=label.rsplit('-',1)[1]
            slot=int(part.find("metadata[@key='extruder']").get('value'))
            assert slot==c.slot(role,silk)
            want=expected[label]
            owner=next(o for o in root.findall('m:resources/m:object',NS) if comp in o.findall('m:components/m:component',NS))
            instance=root.find("m:build/m:item[@objectid='"+owner.get('id')+"']",NS)
            world=m.vertices.copy()
            for element in (comp,instance):
                transform=np.array([float(v) for v in element.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()])
                world=world@transform[:9].reshape(3,3)+transform[9:]
            error=float(cKDTree(want.vertices).query(world)[0].max())
            assert error<4e-5,(label,error)
            assert len(m.faces)==len(want.faces) and abs(m.volume-want.volume)<.05
            errors.append(error);seen.append(label)
        assert set(seen)==set(expected)
        gcode=z.read(next(n for n in z.namelist() if n.endswith('.gcode'))).decode()
        tools=sorted(set(int(v) for v in re.findall(r'^T(\d+)\s*$',gcode,re.M)))
        assert all(i in tools for i in range(4 if silk else 2)),tools
        return {'readback_passed':True,'named_parts':seen,'max_world_vertex_error_mm':max(errors),
                'filament_colours':settings['filament_colour'],'tool_ids':tools,'slice_metadata':metadata,
                'gcode_sha256':hashlib.sha256(gcode.encode()).hexdigest(),
                'silk_profile_final':False if silk else None,'prime_tower_enabled':True}


def main():
    profiles();(OUT/'PRINT').mkdir(exist_ok=True)
    work=OUT/'.slicer-work';work.mkdir(exist_ok=True)
    report={'printer':'Elegoo Centauri Carbon 2, 0.4 mm nozzle','layer_height_mm':.1,
            'initial_layer_height_mm':.2,'inlay_layers':6,'physical_acceptance':False,
            'printer_started':False,'silk_profile_note':'Two generic PLA accent placeholders at 6 mm3/s. Select both actual silk spool profiles and reslice before printing silk.',
            'slicer_version':subprocess.run([EXE,'--help'],capture_output=True,text=True).stdout.splitlines()[0],
            'profiles_sha256':{p.name:sha(p) for p in (OUT/'profiles').glob('*.json')},'plates':{}}
    for source in sorted((OUT/'plates').glob('*.3mf')):
        silk=source.stem.endswith('-silk')
        dest=OUT/'PRINT'/(source.stem+'-CC2.3mf')
        materials=['black','white']+(['silk-orange-placeholder','silk-purple-placeholder'] if silk else [])
        command=[EXE,'--datadir',str(work/'config'),'--load-settings',f'{OUT/"profiles/machine.json"};{OUT/"profiles/process.json"}',
                 '--load-filaments',';'.join(str(OUT/'profiles'/(n+'.json')) for n in materials),
                 '--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(dest),str(source)]
        proc=subprocess.run(command,capture_output=True,text=True,timeout=300)
        (OUT/'reports'/(source.stem+'-slice.log')).write_text(proc.stdout+proc.stderr)
        row={'exit_code':proc.returncode,'input_sha256':sha(source),
             'command':[x.replace(str(c.REPO),'<repo>') for x in command]}
        report['plates'][source.stem]=row
        try:
            assert proc.returncode==0,source.stem
            row.update(check_project(source,dest,silk));row['output_sha256']=sha(dest)
            print(source.stem,'slice and mesh readback PASS',flush=True)
        finally:
            (OUT/'reports/slicing.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
