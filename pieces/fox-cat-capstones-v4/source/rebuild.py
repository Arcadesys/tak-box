"""Rebuild the final pair from retained Meshy OBJs, without paid calls.

Writes an isolated local build directory; delivered printable models stay intact.
The historical v3 Cat is an intermediate, never a final printable deliverable.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import build,revise_fox,prepare_cat_v3,revise_cat

ROOT=Path(__file__).resolve().parents[1]

def load(path):return trimesh.load(path,force='mesh')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'.build-work')
    args=parser.parse_args();out=args.output.resolve()
    assert out!=ROOT,'Use an isolated output directory, not the delivery directory'
    for name in ['raw','models','reports']:(out/name).mkdir(parents=True,exist_ok=True)
    for species in ['fox','cat']:shutil.copy2(ROOT/'raw'/f'{species}.obj',out/'raw'/f'{species}.obj')
    shutil.copy2(ROOT/'reports/meshy-v2-fidelity-review.json',out/'reports/meshy-v2-fidelity-review.json')
    for module in [build,revise_fox,prepare_cat_v3,revise_cat]:module.ROOT=out
    finishing={}
    for species in ['fox','cat']:
        _,finishing[species]=build.finish(species)
        shutil.copy2(out/'models'/f'{species}-capstone.stl',out/'raw'/f'{species}-v2.stl')
    fox,fox_report=revise_fox.revise(load(out/'raw/fox-v2.stl'))
    fox.export(out/'models/fox-capstone.stl')
    cat_intermediate,_=prepare_cat_v3.revise(load(out/'raw/cat-v2.stl'))
    cat_intermediate.export(out/'raw/cat-v3.stl')
    cat,cat_report=revise_cat.revise(load(out/'raw/cat-v3.stl'))
    cat.export(out/'models/cat-capstone.stl')
    pair=[];comparison={}
    for i,species in enumerate(['fox','cat']):
        generated=load(out/'models'/f'{species}-capstone.stl')
        expected=load(ROOT/'models'/f'{species}-capstone.stl')
        assert generated.is_volume and generated.is_watertight
        maximum=max(float(cKDTree(expected.vertices).query(generated.vertices)[0].max()),float(cKDTree(generated.vertices).query(expected.vertices)[0].max()))
        assert maximum<2e-5,(species,maximum)
        assert np.allclose(generated.extents,expected.extents,atol=2e-5)
        assert abs(generated.volume-expected.volume)<.01
        comparison[species]={'max_bidirectional_vertex_distance_mm':maximum,'dimensions_mm':generated.extents.tolist(),'volume_mm3':float(generated.volume),'sha256':hashlib.sha256((out/'models'/f'{species}-capstone.stl').read_bytes()).hexdigest(),'byte_identical_to_delivery':(out/'models'/f'{species}-capstone.stl').read_bytes()==(ROOT/'models'/f'{species}-capstone.stl').read_bytes()}
        placed=generated.copy();placed.apply_translation([20+i*40,20,0]);pair.append((f'{species.title()} capstone',placed))
    build.write_3mf(pair,out/'models/fox-cat-capstones.3mf')
    result={'new_paid_calls':0,'input_obj_sha256':{s:finishing[s]['raw_sha256'] for s in finishing},'comparison':comparison,'finishing':finishing,'fox_tail_revision':fox_report,'cat_neck_revision':cat_report}
    (ROOT/'reports/rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(comparison,indent=2))

if __name__=='__main__':main()
