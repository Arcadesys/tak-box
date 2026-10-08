"""Package current V26 full plates with audited sources and preserved archives."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys, json, hashlib, subprocess, platform, importlib.metadata
from package import PRESERVED
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    preserved={}; unavailable=[]
    for name,digest in {**PRESERVED,'v26/V26-MECHANISM-REVIEW.zip':'664a4d012611dc2889dbf5ca7508ec9b8a0385b1cfe1426226637f5e121314ff','v26/archive/previous-main-hinge/V26-opposed-pivots-superseded.zip':'db35b5db3caee5e3d9949e3dc533835be2de00983649a9685ad243a3e22b97fa'}.items():
        if not (ROOT/name).exists():
            assert not (ROOT/'.git').exists(),('Missing preserved checkout archive',name)
            unavailable.append(name);continue
        assert sha(ROOT/name)==digest,name
        preserved[name]=digest
    reports={name:json.loads((OUT/'reports'/name).read_text()) for name in ('geometry.json','full-plates.json','review-audit.json','full-slicing.json','full-colour-layers.json')}
    for name,r in reports.items():
        assert r.get('passed',True),name
        assert all(row.get('pass_',row.get('pass',False)) for row in r.get('checks',[])),name
    for name,digest in reports['geometry.json']['source_sha256'].items():assert sha(OUT/name)==digest,name
    for name,digest in reports['full-slicing.json']['source_sha256'].items():assert sha(OUT/name)==digest,name
    for plate,row in reports['full-slicing.json']['plates'].items():
        assert sha(OUT/'plates'/f'{plate}.3mf')==row['input_sha256']
        assert sha(OUT/'FULL-PRINT'/f'{plate}-CC2-PLA.3mf')==row['project_sha256']
        for name,digest in row['profiles_sha256'].items():assert sha(OUT/name)==digest,name
    versions={n:importlib.metadata.version(n) for n in ('cadquery','vtk','trimesh','numpy','scipy','matplotlib','Pillow')}
    revision=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    previous=json.loads((OUT/'reports/full-provenance.json').read_text()) if (OUT/'reports/full-provenance.json').exists() else {}
    provenance=dict(passed=True,command=[sys.executable,str(Path(__file__).resolve())],python=sys.version,platform=platform.platform(),dependencies=versions,
        base_revision=revision.stdout.strip() if revision.returncode==0 else previous.get('base_revision'),
        source_sha256={str(p.relative_to(OUT)):sha(p) for p in (OUT/'source').glob('*.py') if p.name not in ('trial.py','combine.py','reproduce.py')},
        preserved_archives=preserved,archives_unavailable_in_standalone_extraction=unavailable,units='mm',piece_package=reports['geometry.json']['piece_package'],flexible_board_tabs=False,
        hook_retains_both_closed_boards=True,case_outer_corner_radius_mm=reports['geometry.json']['case_outer_corner_radius_mm'],board_outer_corner_radius_mm=reports['geometry.json']['board_outer_corner_radius_mm'],main_hinge='integral 4mm axle between two fixed supports; central moving barrel',main_hinge_fixed_spans_mm=reports['geometry.json']['main_hinge_fixed_spans_mm'],main_hinge_moving_spans_mm=reports['geometry.json']['main_hinge_moving_spans_mm'],board_seating_shoulder_mm=[4,6.1,4.7],physical_acceptance=False,printer_started=False)
    (OUT/'reports/full-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    source_names=('requirements.txt','build.py','common.py','board_plate.py','plates_full.py','slice_full.py','slice.py','verify_pip_hinges.py','inspect_case_layers.py','verify_pin_toolpaths.py','verify_review.py','verify_colour.py','render.py','caption.py','package_full.py','package.py','reproduce_full.py')
    paths=[OUT/'README.md',OUT/'START-HERE.md']+[OUT/'source'/n for n in source_names]
    for folder in ('FULL-PRINT','profiles','reference'):
        paths.extend(p for p in (OUT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    paths.extend(p for p in (OUT/'models').iterdir() if p.is_file() and 'trial' not in p.name)
    plate_names=reports['full-slicing.json']['plates']
    paths.extend(OUT/'plates'/f'{name}.3mf' for name in plate_names)
    previews=('01-game-open','02-board-clip','03-captive-hook','04-hook-section','05-closed','06-fixed-guides','10-full-PIP-sliced-gaps','11-full-hook-sliced-gaps','12-case-plate','13-board-plate','14-capstone-plate','15-full-sliced-colour-layer','16-main-hinge','17-main-hinge-section','18-rounded-corner')
    paths.extend(OUT/'previews'/f'{name}.png' for name in previews)
    paths.extend(OUT/'reports'/name for name in (*reports,'full-provenance.json','build-full.log','build-full-initial-failure.log','full-plates.log','full-slice-driver.log','full-colour.log','full-review.log','full-render.log','full-render-initial-failure.log','build-double-supported.log','build-double-supported-rounded.log','main-hinge-render.log','corner-render.log'))
    paths.extend(OUT/'reports'/f'{name}-full-slice.log' for name in plate_names)
    paths=sorted(set(paths))
    assert all(p.is_file() for p in paths)
    manifest=dict(version='V26 tab-free print kit',units='mm',files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in paths])
    manifest_path=OUT/'FULL-MANIFEST.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    kit=OUT/'V26-PRINT-KIT.zip'
    with ZipFile(kit,'w',ZIP_DEFLATED) as z:
        for p in paths+[manifest_path]:z.write(p,'v26/'+str(p.relative_to(OUT)))
    with ZipFile(kit) as z:
        assert z.testzip() is None
        for row in manifest['files']:
            data=z.read('v26/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    report=dict(passed=True,zip_sha256=sha(kit),entries=len(paths)+1,preserved_archives=len(preserved),physical_acceptance=False,printer_started=False)
    (OUT/'reports/full-package.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Full package PASS',len(paths)+1,'entries;',len(preserved),'preserved archives',flush=True)

if __name__=='__main__':main()
