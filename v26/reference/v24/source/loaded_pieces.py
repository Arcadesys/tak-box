"""Separate removable-tray feasibility study. No final raised case is claimed."""
import json,sys,hashlib
import cadquery as cq
import trimesh
import case as c
from geometry_utils import ov
from render_utils import render,colors
OUT=c.OUT
FLOOR=1.2
PIECE_Z=2.2+FLOOR
# A broad flat bottom seats directly on the retained 2.2 mm case floor.
def tray(side):return c.tray(side)

def loaded(side):
 sys.path.insert(0,str(OUT/'source/vendor/pieces'));import tak_pieces as pieces
 team='cat' if side=='left' else 'witch';flat=pieces.flat(team).val()
 out=[]
 for j in range(7):
  for i in range(3):
   s=flat.translate((23.1+22*i,20.1+22.6*j,PIECE_Z))
   out.append((f'{team}-{j*3+i+1}',s if side=='left' else c.mirror(s)))
 cap=c.stored_capstone(team,'left')
 out.append((f'{team}-capstone',cap if side=='left' else c.mirror(cap)))
 return out
