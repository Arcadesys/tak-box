"""Join numerically identical STL vertices at 0.0000001 mm precision.

OCC may tessellate two sides of one edge with tiny floating-point differences.
Keep the first existing float32 position; do not remesh or change triangles.
"""
from pathlib import Path
import struct,math
import cadquery as cq

def weld_stl(path):
    p=Path(path);data=bytearray(p.read_bytes());count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+count*50
    canonical={};changed=0;maximum=0.0
    for i in range(count):
        for j in range(3):
            at=84+i*50+12+j*12;v=struct.unpack_from('<3f',data,at)
            key=tuple(round(x,7) for x in v);same=canonical.setdefault(key,v)
            if v!=same:
                delta=math.dist(v,same);assert delta<2e-7
                maximum=max(maximum,delta);changed+=1;struct.pack_into('<3f',data,at,*same)
    p.write_bytes(data)
    return {'reused_vertex_occurrences':changed,'maximum_position_change_mm':maximum}

def export_stl(shape,path):
    cq.exporters.export(shape,str(path),tolerance=.02,angularTolerance=.1)
    return weld_stl(path)
