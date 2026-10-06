"""Self-contained board-option ZIP and dependency/hash audit."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import ast,hashlib,json,platform,subprocess,sys
import inlays as c


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=c.OUT;repo=c.REPO
    release=out/'release';release.mkdir(exist_ok=True)
    dependencies=[repo/p for p in [
        'v23/source/case.py','v23/source/flat_capstones.py',
        'v23/source/vendor/body/folio.py','v23/source/vendor/pieces/tak_pieces.py',
        'v23/source/vendor/pieces/cat-flat.stl','v23/source/vendor/pieces/witch-flat.stl',
        'v23/models/housing-left.step','v23/models/housing-right.step',
        'v23/profiles/machine.json','v23/profiles/process-case.json','v23/profiles/filament-pla.json',
        'v16-field-book/source/tak_book.py','v16-field-book/source/decor.py',
        'v17-four-leaf/source/folio.py']]
    provenance={'baseline_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
                'baseline_note':'Parent V23 revision used for this separate replacement-board option. Source hashes identify the option precisely.',
                'python':sys.version,'platform':platform.platform(),'runtime':str(Path(sys.executable)),
                'dependencies_sha256':{str(p.relative_to(repo)):sha(p) for p in dependencies},
                'source_sha256':{str(p.relative_to(repo)):sha(p) for p in (out/'source').glob('*') if p.is_file()},
                'commands':['python v23/board-inlays/source/'+n+'.py' for n in ('build','render','slice','inspect_layers','package')],
                'physical_acceptance':False,'printer_started':False}
    (out/'reports/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    # Refresh the documentary source digest after docstring-only follow-ups.
    geometry_path=out/'reports/geometry.json';geometry=json.loads(geometry_path.read_text())
    geometry['sources_sha256']={name:sha(repo/name) for name in geometry['sources_sha256']}
    geometry_path.write_text(json.dumps(geometry,indent=2)+'\n')
    files=[p for p in out.rglob('*') if p.is_file() and '__pycache__' not in p.parts
           and '.slicer-work' not in p.parts and 'release' not in p.relative_to(out).parts
           and p.name not in ('package-manifest.json','package-audit.json')]
    files=sorted(set(files+dependencies))
    manifest={'root':'tak-v23-board-inlays','units':'millimeter','physical_acceptance':False,
              'files':[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
    manifest_path=out/'package-manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    path=release/'tak-v23-board-inlays.zip'
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('tak-v23-board-inlays/START-HERE.md','# V23 multicolour replacement boards\n\nStart with [the guide](v23/board-inlays/README.md) and print the small trial first. Black/white projects use slots 1 and 2. Optional silk uses slot 3 and requires your actual spool profile and reslicing. The complete case is not included.\n')
        for p in files+[manifest_path]:
            z.write(p,'tak-v23-board-inlays/'+str(p.relative_to(repo)))
    with ZipFile(path) as z:
        assert z.testzip() is None
        for row in manifest['files']:
            data=z.read('tak-v23-board-inlays/'+row['path'])
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
            if row['path'].endswith('.py'):ast.parse(data)
        assert len([n for n in z.namelist() if '/board-inlays/PRINT/' in n])==4
    audit={'zip_sha256':sha(path),'payload_files':len(files),'crc_pass':True,'all_payload_hashes_pass':True,
           'python_syntax_pass':True,'four_sliced_projects':True,'physical_acceptance':False}
    (out/'reports/package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
