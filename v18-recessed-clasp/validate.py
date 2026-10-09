from pathlib import Path
import json,hashlib
R=Path(__file__).parent;r=json.loads((R/'checks.json').read_text());m=json.loads((R/'parts/manifest.json').read_text())
checks={k:all(max(row[1:])<1e-6 for row in r[k]) for k in ['press_path','pressed_slide_path','open_lift_path','assembly_insertion']}
checks.update(nominal_parts_disjoint=max(m['assembled_overlap_mm3'].values())<1e-6,three_watertight_parts=len(m['parts'])==3 and all(p['watertight'] for p in m['parts']),locked_slide_barrier=any(row[1]>1 for row in r['locked_slide_barrier']),pressed_only_still_holds=any(row[1]>1 for row in r['pressed_only_lift_barrier']),open_rest_clear=r['open_rest_interference']<1e-6)
assert all(checks.values()),checks
(R/'validation.json').write_text(json.dumps({'checks':checks,'status':'digital geometry tests pass; physical print/fit untested','build_sha256':hashlib.sha256((R/'build.py').read_bytes()).hexdigest()},indent=2));print(checks)
