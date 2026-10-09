"""Read actual linear G-code bead widths around V2 protected snap tabs."""
from pathlib import Path
import json,re,hashlib,sys
from zipfile import ZipFile
import numpy as np
OUT=Path(__file__).resolve().parents[1]

def segments(data):
    pos=np.zeros(3);extrusion=0.;relative_e=True;absolute_xyz=True;width=.42;role='';out=[]
    for line in data.splitlines():
        if line.startswith(';WIDTH:'):width=float(line.split(':',1)[1])
        if line.startswith(';TYPE:'):role=line.split(':',1)[1]
        if line.startswith('M83'):relative_e=True
        if line.startswith('M82'):relative_e=False
        if line.startswith('G90'):absolute_xyz=True
        if line.startswith('G91'):absolute_xyz=False
        if line.startswith('G92'):
            values=dict((k,float(v)) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line))
            if 'E' in values:extrusion=values['E']
            continue
        code=line.split(' ',1)[0]
        if code not in ('G0','G1','G2','G3'):continue
        values=dict((k,float(v)) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line))
        end=pos.copy()
        for i,k in enumerate('XYZ'):
            if k in values:end[i]=values[k] if absolute_xyz else end[i]+values[k]
        amount=values.get('E',0.) if relative_e else values.get('E',extrusion)-extrusion
        if 'E' in values:extrusion=values['E'] if not relative_e else extrusion+values['E']
        if amount>1e-7 and np.linalg.norm(end[:2]-pos[:2])>1e-6:
            assert code not in ('G2','G3'),'Arc extrusion requires a different path verifier'
            out.append((pos[:2].copy(),end[:2].copy(),end[2],width,role))
        pos=end
    return out

def margin(point,beads):
    p=np.asarray(point);starts=np.array([s[0] for s in beads]);ends=np.array([s[1] for s in beads]);width=np.array([s[3] for s in beads])
    delta=ends-starts;fraction=np.clip(np.sum((p-starts)*delta,axis=1)/np.sum(delta*delta,axis=1),0,1)
    distances=np.linalg.norm(p-starts-fraction[:,None]*delta,axis=1)-width/2
    index=int(np.argmin(distances));return float(distances[index]),beads[index][4]

def main():
    global OUT
    if '--black' in sys.argv:OUT=OUT/'BLACK'
    path=OUT/'reports/sample.gcode';data=path.read_text();paths=segments(data)
    geometry=json.loads((OUT/'reports/geometry.json').read_text());plate=json.loads((OUT/'reports/plate-provenance.json').read_text());checks=[]
    with ZipFile(plate['saved_project']) as archive:settings=json.loads(archive.read('Metadata/project_settings.config'))
    # CC2 uses one physical nozzle with a configured XY offset. Filament T2
    # is a feed slot, not a third physical nozzle. Convert object-space probes
    # to commanded G-code coordinates, including this retained machine offset.
    assert len(settings['extruder_offset'])==1
    nozzle_offset=np.array([float(q) for q in settings['extruder_offset'][0].split('x')])
    for team in ('cat','witch'):
        source=next(s for s in plate['sources'] if s['label']==team+'-capstone-lower');move=np.array(source['translation_mm'])
        for hook_index,frame in enumerate(geometry['capstones'][team]['snap_frames']):
            normal=np.array(frame['normal_xy']);tangent=np.array([-normal[1],normal[0]]);origin=np.array(frame['origin_xy'])+move[:2]-nozzle_offset
            to_world=lambda x,y:origin+normal*x+tangent*y
            # These lie in the freely bending portion, below the capstone seam.
            for z in (2.0,3.2):
                beads=[s for s in paths if abs(s[2]-z)<.001];assert beads
                for name,x,y in (('rear relief',-1.275,0),('side relief',-1.85,1.6),('guard flex space',-2.55,0)):
                    distance,role=margin(to_world(x,y),beads)
                    assert distance>.01,(team,hook_index,name,z,distance,role)
                    checks.append(dict(team=team,hook=hook_index,check=name,z_mm=z,probe_command_xy_mm=to_world(x,y).tolist(),nearest_bead_edge_mm=distance,nearest_role=role,passed=True))
            # Both normal layers through the flat retaining plateau must carry
            # plastic in the radial capture region, not just a sloping ramp.
            for z in (4.4,4.6):
                beads=[s for s in paths if abs(s[2]-z)<.001];assert beads
                distance,role=margin(to_world(-1.05,0),beads)
                assert distance<0,(team,hook_index,'no printed barb plateau',z,distance,role)
                checks.append(dict(team=team,hook=hook_index,check='retaining plateau occupied',z_mm=z,probe_command_xy_mm=to_world(-1.05,0).tolist(),bead_edge_signed_distance_mm=distance,nearest_role=role,passed=True))
    report=dict(passed=True,checks=checks,gcode_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),physical_nozzle_offset_xy_mm=nozzle_offset.tolist(),method='Actual linear extrusion centre lines buffered by the WIDTH values emitted in G-code; sampled slot centres and barb plateau layers',physical_bead_shape_measured=False,physical_retention_verified=False,minimum_sampled_gap_probe_to_bead_edge_mm=min(q['nearest_bead_edge_mm'] for q in checks if 'nearest_bead_edge_mm' in q))
    (OUT/'reports/snap-slice.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
