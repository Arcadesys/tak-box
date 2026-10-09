"""Prove V24 is the named identity of the unchanged delivered V23 R2 kit."""
from pathlib import Path
from zipfile import ZipFile
import ast,hashlib,json,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parents[1]
ORIGIN_SHA='7a4ac10b53c1f967d48a39bd2c93892ce8b06412635ec06f95d8a4666318ee12'
V23_SHA='33510a63581b1a8b5f3c5afde34ed99acf6ecd5ccfb6bc49956e6d6e2b9e1221'
def sha(data):return hashlib.sha256(data).hexdigest()
class Labels(ast.NodeTransformer):
 def visit_Module(self,node):
  self.generic_visit(node)
  if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):node.body.pop(0)
  return node
 def visit_Constant(self,node):
  if isinstance(node.value,str):node.value=node.value.replace('V24','V23 R2').replace('v24','v23-r2')
  return node
def normalized(data):return ast.dump(Labels().visit(ast.parse(data)),include_attributes=False)
def inspect_project(path):
 with ZipFile(path) as z:
  assert z.testzip() is None
  models={};gcodes={}
  for n in z.namelist():
   if n.endswith('.model'):
    root=ET.fromstring(z.read(n));assert root.get('unit') in (None,'millimeter')
    models[n]={'sha256':sha(z.read(n)),'named_objects':[e.attrib for e in root.iter() if e.tag.endswith('}object')],'placements':[e.attrib for e in root.iter() if e.tag.endswith(('}item','}component'))]}
   if n.endswith('.gcode'):gcodes[n]=sha(z.read(n))
  return {'model_parts':models,'gcode_sha256':gcodes,'project_sha256':sha(path.read_bytes())}
def main(baseline=None):
 path=Path(baseline) if baseline else OUT.parent.parent/'v23-r2/release/tak-v23-r2-print-kit.zip'
 assert sha(path.read_bytes())==ORIGIN_SHA,'unexpected accepted-kit archive'
 cad={};projects={};profiles={};receipts={};source={}
 with ZipFile(path) as z:
  assert z.testzip() is None
  manifest=json.loads(z.read('v23-r2/PACKAGE-MANIFEST.json'))
  for row in manifest['files']:
   rel=row['path'];data=z.read('v23-r2/'+rel);assert len(data)==row['bytes'] and sha(data)==row['sha256']
   current=OUT/rel
   if current.suffix in ('.step','.stl'):
    assert current.read_bytes()==data,rel;cad[rel]=sha(data)
   elif current.suffix=='.3mf':
    assert current.read_bytes()==data,rel;projects[rel]=inspect_project(current)
   elif rel.startswith('profiles/'):
    assert current.read_bytes()==data,rel;profiles[rel]=sha(data)
   elif rel.startswith('reports/') and current.name!='provenance.json':
    assert current.read_bytes()==data,rel;receipts[rel]=sha(data)
   elif rel.startswith('source/') and current.suffix=='.py' and current.name not in ('record_provenance.py','package_release.py','render_utils.py'):
    assert normalized(current.read_text())==normalized(data.decode()),rel;source[rel]={'normalized_AST_equal':True,'origin_sha256':sha(data),'v24_sha256':sha(current.read_bytes())}
  assert (OUT/'reports/validation-origin.json').read_bytes()==z.read('v23-r2/reports/provenance.json')
  origin=json.loads(z.read('v23-r2/reports/provenance.json'))
 original=OUT.parent.parent/'v23/release/tak-v23-print-kit.zip'
 assert sha(original.read_bytes())==V23_SHA,'original V23 archive changed'
 assert len([p for p in projects if p.startswith('PRINT/')])==4
 assert sum(bool(p['gcode_sha256']) for p in projects.values())==6
 report={'pass':True,'version':'V24','kind':'identity correction only','compared_to':'unchanged V23 R2 delivered kit','origin_source_commit':origin['source_commit'],'origin_artifact_commit':'919bbf0','origin_final_revision':'f80af3c','origin_zip_sha256':ORIGIN_SHA,'original_v23_zip_sha256':V23_SHA,'unchanged_CAD_exports':cad,'byte_identical_projects':projects,'byte_identical_profiles':profiles,'byte_identical_validation_receipts':receipts,'geometry_and_check_source_equivalence':source,'accepted_checks_reused':origin['total_checks'],'accepted_slices_reused':{'full_build':4,'trials':2},'new_geometry_motion_or_slicing_run':False,'physical_acceptance':False,'note':'All named meshes, placements, metadata, settings and complete Gcode are identical because the 3MF archives are byte-identical. Preset names deliberately retain V23 R2. Preview text labels are regenerated from unchanged exported STEP.'}
 (OUT/'reports/identity.json').write_text(json.dumps(report,indent=2)+'\n')
 print('V24 identity PASS:',len(cad),'CAD files,',len(projects),'3MFs,',len(source),'source ASTs,',len(profiles),'profiles; original V23 ZIP unchanged')
 return report
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--baseline');main(p.parse_args().baseline)
