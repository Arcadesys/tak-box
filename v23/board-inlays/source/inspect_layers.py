"""Verify actual coloured deposition layers and render the last inlay layer."""
from zipfile import ZipFile
import hashlib,json,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import inlays as c


def segments(gcode):
    xyz=np.zeros(3);tool=0;relative_e=True;e_position=0.;out=[]
    for line in gcode.splitlines():
        line=line.split(';',1)[0].strip()
        if re.fullmatch(r'T\d+',line):tool=int(line[1:]);continue
        if line=='M83':relative_e=True;continue
        if line=='M82':relative_e=False;continue
        if line.startswith('G92 '):
            values=dict((k,float(v)) for k,v in re.findall(r'([XYZE])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))',line))
            if 'E' in values:e_position=values['E']
            continue
        if not line.startswith(('G0 ','G1 ')):continue
        values=dict((k,float(v)) for k,v in re.findall(r'([XYZE])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))',line))
        target=np.array([values.get(k,xyz[i]) for i,k in enumerate('XYZ')])
        extrusion=values.get('E',0) if relative_e else values.get('E',e_position)-e_position
        if not relative_e and 'E' in values:e_position=values['E']
        if extrusion>0 and np.linalg.norm(target[:2]-xyz[:2])>1e-6:
            out.append((tool,float(target[2]),np.array([xyz[:2],target[:2]])))
        xyz=target
    return out


def main():
    checks=[];rows={};figure=None
    for path in sorted((c.OUT/'PRINT').glob('*.3mf')):
        trial=path.stem.startswith('00-');silk='-silk-' in path.stem
        rois=[(8,98.2,8,44.8)] if trial else [(7,104.8,7,199.1),(121,218.8,7,199.1)]
        with ZipFile(path) as z:
            code=z.read(next(n for n in z.namelist() if n.endswith('.gcode'))).decode()
        model=[]
        for tool,z,points in segments(code):
            x,y=points.mean(axis=0)
            if any(x0<=x<=x1 and y0<=y<=y1 for x0,x1,y0,y1 in rois):
                model.append((tool,z,points))
        wanted=[round(v,2) for v in np.arange(1.3 if trial else 4.2,1.81 if trial else 4.71,.1)]
        tool_layers={str(t):sorted(set(round(z,2) for tool,z,_ in model if tool==t)) for t in range(1,3 if silk else 2)}
        for tool,layers in tool_layers.items():
            ok=layers==wanted
            checks.append({'name':path.stem+'/colour-tool-'+tool+' exact six inlay layers','pass':ok,'layers_mm':layers})
            assert ok,(path.name,tool,layers,wanted)
        rows[path.name]={'gcode_sha256':hashlib.sha256(code.encode()).hexdigest(),'coloured_model_layers_mm':tool_layers,
                         'model_deposition_segments':len(model),'prime_tower_excluded':True}
        if not trial and silk:figure=model
    fig,ax=plt.subplots(figsize=(12,10));fig.patch.set_facecolor('#EFEFEF');ax.set_facecolor('#080808')
    colours={0:'#444444',1:'#FFFFFF',2:'#D6A54C'}
    labels={0:'Black PLA',1:'White PLA',2:'Optional accent PLA'}
    for tool in range(3):
        lines=[points for t,z,points in figure if t==tool and abs(z-4.7)<.001]
        ax.add_collection(LineCollection(lines,colors=colours[tool],linewidths=1.1,label=labels[tool]))
    ax.set_xlim(3,223);ax.set_ylim(3,203);ax.set_aspect('equal')
    ax.tick_params(labelsize=16);ax.set_xlabel('Plate X (mm)',fontsize=18);ax.set_ylabel('Plate Y (mm)',fontsize=18)
    ax.set_title('Actual sliced inlay layer: Z 4.70 mm\nTwo registered board assemblies',fontsize=22,pad=18)
    legend=ax.legend(loc='upper center',bbox_to_anchor=(.5,-.09),ncol=3,fontsize=15,facecolor='#111111',labelcolor='white')
    fig.tight_layout();fig.savefig(c.OUT/'previews/05-sliced-colour-layer.png',dpi=160,bbox_inches='tight');plt.close(fig)
    report={'checks':checks,'projects':rows,'physical_acceptance':False,
            'note':'Linear positive-extrusion XY moves from embedded Gcode. The only arc is the end-of-print parking move. Prime tower is outside model regions. This confirms colour tools deposit at model locations on the six inlay layers; no physical bonding or colour purity claim.'}
    (c.OUT/'reports/colour-layers.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(checks),'colour-layer checks PASS')


if __name__=='__main__':main()
