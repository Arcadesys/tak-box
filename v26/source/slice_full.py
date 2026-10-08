"""Dry-slice V26 full plates and verify meshes, slots and captive toolpaths."""
from pathlib import Path
from zipfile import ZipFile
import sys, json, hashlib, subprocess, re, xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import slice as trials
import verify_pip_hinges as pip
import board_plate as boards
OUT=Path(__file__).resolve().parents[1]
NS=trials.NS; PROD=trials.PROD

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def mesh(el):
    vertices=[[float(v.get(k)) for k in ('x','y','z')] for v in el.findall('m:vertices/m:vertex',NS)]
    faces=[[int(v.get(k)) for k in ('v1','v2','v3')] for v in el.findall('m:triangles/m:triangle',NS)]
    m=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    return m

def readback(src,dest,colour):
    with ZipFile(src) as z:
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        want={o.get('name'):mesh(o.find('m:mesh',NS)) for o in root.findall('m:resources/m:object',NS) if o.find('m:mesh',NS) is not None}
        build_count=len(root.find('m:build',NS))
    with ZipFile(dest) as z:
        assert z.testzip() is None
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
        values={v.get('key'):v.get('value') for v in info.findall('.//plate/metadata')}
        assert values['outside']=='false'
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        assert len(root.find('m:build',NS))==build_count and len(cfg.findall('object'))==build_count
        got=[]; checks=[]
        for comp in root.findall('.//m:component',NS):
            sub=ET.fromstring(z.read(comp.get(PROD+'path').lstrip('/')))
            m=mesh(sub.find(".//m:object[@id='"+comp.get('objectid')+"']/m:mesh",NS))
            part=cfg.find(".//part[@id='"+comp.get('objectid')+"']")
            label=part.find("metadata[@key='name']").get('value'); expected=want[label]
            owner=next(o for o in root.findall('m:resources/m:object',NS) if comp in o.findall('m:components/m:component',NS))
            instance=root.find("m:build/m:item[@objectid='"+owner.get('id')+"']",NS)
            v=m.vertices.copy()
            for el in (comp,instance):
                q=np.array([float(a) for a in el.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()])
                v=v@q[:9].reshape(3,3)+q[9:]
            forward=cKDTree(expected.vertices).query(v)[0]; back=cKDTree(v).query(expected.vertices)[0]
            a=float(forward.max()); bb=float(back.max())
            if a>=4e-5:a=float(trimesh.proximity.closest_point_naive(expected,v[forward>=4e-5])[1].max())
            if bb>=4e-5:bb=float(trimesh.proximity.closest_point_naive(trimesh.Trimesh(vertices=v,faces=m.faces,process=False),expected.vertices[back>=4e-5])[1].max())
            assert max(a,bb)<.002 and abs(m.volume-expected.volume)<.05
            if colour:
                role=label.rsplit('-',1)[1]
                assert int(part.find("metadata[@key='extruder']").get('value'))==boards.ROLES[role][0]
            else:assert m.body_count==1
            got.append(label);checks.append(dict(name=label,watertight=True,mesh_bodies=m.body_count,surface_error_mm=max(a,bb),volume_error_mm3=float(m.volume-expected.volume)))
        assert set(got)==set(want)
        settings=json.loads(z.read('Metadata/project_settings.config'))
        assert settings['printer_model']=='Elegoo Centauri Carbon 2' and settings['wall_loops']=='4'
        assert settings['layer_height']==('0.1' if colour else '0.2')
        if colour:
            assert settings['filament_colour']==['#111111','#FFFFFF','#D6A54C','#B887DD'] and settings['enable_prime_tower']=='1'
        else:assert settings['support_on_build_plate_only']=='1' and settings['brim_width']=='0'
        code=z.read('Metadata/plate_1.gcode');assert b';LAYER_CHANGE' in code
        if colour:assert set(range(4)).issubset({int(v) for v in re.findall(rb'^T(\d+)\s*$',code,re.M)})
        return values,checks,code,[x.attrib for x in info.findall('.//warning')]

def main():
    (OUT/'FULL-PRINT').mkdir(exist_ok=True)
    stage=OUT/'.slicer-work';stage.mkdir(exist_ok=True)
    plans=[('01-V26-PIP-guides-and-hook',False),('02-V26-FULL-SIZE-FOUR-COLOUR-tab-free-boards',True),('03-V26-flat-capstones',False)]
    report=dict(passed=False,printer='Elegoo Centauri Carbon 2, 0.4 mm nozzle',slicer='ElegooSlicer 2.4.2',physical_acceptance=False,printer_started=False,
                source_sha256={str(p.relative_to(OUT)):sha(p) for p in (Path(__file__).resolve(),OUT/'source/slice.py',OUT/'source/verify_pip_hinges.py',OUT/'source/inspect_case_layers.py',OUT/'source/verify_pin_toolpaths.py')},plates={})
    for name,colour in plans:
        src=OUT/'plates'/f'{name}.3mf';dest=OUT/'FULL-PRINT'/f'{name}-CC2-PLA.3mf'
        folder=OUT/'profiles/boards' if colour else OUT/'profiles'
        proc=folder/('process.json' if colour else 'process-case.json')
        filaments=[folder/(n+'.json') for n in ('black','white','silk-orange-placeholder','silk-purple-placeholder')] if colour else [folder/'filament-pla.json']
        profiles=[folder/'machine.json',proc]+filaments
        command=[str(trials.EXE),'--datadir',str(stage/'full-config'),'--load-settings',';'.join(str(p) for p in profiles[:2]),'--load-filaments',';'.join(str(p) for p in filaments),'--ensure-on-bed','--arrange','0','--orient','0','--slice','0','--export-3mf',str(dest),str(src)]
        if '--verify-only' not in sys.argv:
            result=subprocess.run(command,capture_output=True,text=True,timeout=600)
            (OUT/'reports'/f'{name}-full-slice.log').write_text(result.stdout+result.stderr)
            assert result.returncode==0,(name,result.returncode)
        values,checks,code,warnings=readback(src,dest,colour)
        gcode=stage/f'{name}.gcode';gcode.write_bytes(code)
        bearing=[]
        if name.startswith('01'):
            shift=json.loads((OUT/'reports/geometry.json').read_text())['print_translation_mm']
            pip.OUT=OUT
            bearing=pip.toolpath_checks(gcode,shift,preview='10-full-PIP-sliced-gaps')
            bearing+=trials.hook_checks(gcode,shift,preview='11-full-hook-sliced-gaps')
            assert all(q.get('pass',q.get('pass_',False)) for q in bearing),bearing
        report['plates'][name]=dict(passed=True,command=command,input_sha256=sha(src),project_sha256=sha(dest),
                    profiles_sha256={str(p.relative_to(OUT)):sha(p) for p in profiles},mesh_readback=checks,
                    plate_metadata=values,bearing_checks=bearing,warnings=warnings,gcode_sha256=hashlib.sha256(code).hexdigest(),
                    accent_profiles_final=False if colour else None)
        (OUT/'reports/full-slicing.json').write_text(json.dumps(report,indent=2)+'\n')
        print(name,'PASS',values['prediction'],'seconds',values['weight'],'grams',flush=True)
    report['passed']=True
    report['total_estimated_seconds']=sum(int(row['plate_metadata']['prediction']) for row in report['plates'].values())
    report['total_estimated_grams']=sum(float(row['plate_metadata']['weight']) for row in report['plates'].values())
    (OUT/'reports/full-slicing.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
