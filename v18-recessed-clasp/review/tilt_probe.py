from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]; p=R/'build.py'; data=p.read_bytes(); ns={'__file__':str(p),'__name__':'independent_review_import'};exec(compile(data,str(p),'exec'),ns)
k=ns['keeper'];s=ns['slider']();r=ns['receiver'];ov=ns['ov']
rows=[]
for a in [0,2,5,8,10,12,15,18,20,22,25,30]:
 q=k.rotate((45,20,2.4),(45,21,2.4),-a).translate((1,0,0));rows.append({'angle_deg':-a,'dx_mm':1,'receiver_overlap':round(ov(q,r),8),'slider_overlap':round(ov(q,s),8)})
for dx in [1,2,3,4,5,6,8,10,15,20,30,50]:
 q=k.rotate((45,20,2.4),(45,21,2.4),-20).translate((dx,0,0));rows.append({'angle_deg':-20,'dx_mm':dx,'receiver_overlap':round(ov(q,r),8),'slider_overlap':round(ov(q,s),8)})
res={'source_sha256':hashlib.sha256(data).hexdigest(),'rows':rows,'description':'Sequential rigid pose hypothesis: +X 1mm, tilt 20deg rear upward around y axis through bolt tip, then pull keeper +X while bolt remains locked. Discrete samples only.'};out=R/'review'/'tilt-bypass-probes.json';out.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
