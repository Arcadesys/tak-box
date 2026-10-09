from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,vtk
R=Path(__file__).parent;O=R/'plate';O.mkdir(exist_ok=True)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
def tag(s):return '{'+ns+'}'+s
root=E.Element(tag('model'),unit='millimeter');E.SubElement(root,tag('metadata'),name='Title').text='V18 recessed press-and-slide clasp — unprinted support-required coupon';res=E.SubElement(root,tag('resources'));build=E.SubElement(root,tag('build'));rows=[]
for i,(name,x,y) in enumerate([('V18-receiver',10,10),('V18-slider',10,30),('V18-keeper',65,30)],1):
 reader=vtk.vtkSTLReader();reader.SetFileName(str(R/'parts'/(name+'.stl')));reader.Update();c=vtk.vtkCleanPolyData();c.SetInputConnection(reader.GetOutputPort());c.Update();m=c.GetOutput();b=m.GetBounds()
 ob=E.SubElement(res,tag('object'),id=str(i),name=name,type='model');me=E.SubElement(ob,tag('mesh'));vs=E.SubElement(me,tag('vertices'));ts=E.SubElement(me,tag('triangles'))
 for j in range(m.GetNumberOfPoints()):
  a=m.GetPoint(j);E.SubElement(vs,tag('vertex'),x=str(a[0]+x),y=str(a[1]+y),z=str(max(0,a[2])))
 for j in range(m.GetNumberOfCells()):
  a=m.GetCell(j);E.SubElement(ts,tag('triangle'),v1=str(a.GetPointId(0)),v2=str(a.GetPointId(1)),v3=str(a.GetPointId(2)))
 E.SubElement(build,tag('item'),objectid=str(i));rows.append({'name':name,'bounds_mm':[b[0]+x,b[1]+x,b[2]+y,b[3]+y,b[4],b[5]],'support_required':True})
with zipfile.ZipFile(O/'tak-v18-recessed-clasp.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>');z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>');z.writestr('3D/3dmodel.model',E.tostring(root,encoding='utf-8',xml_declaration=True))
(O/'layout.json').write_text(json.dumps(rows,indent=2))
