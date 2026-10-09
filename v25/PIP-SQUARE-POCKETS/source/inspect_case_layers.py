"""Retained V24 G-code parser; applies the recorded machine nozzle offset."""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parents[1]
NOZZLE_OFFSET=[float(v) for v in json.loads((OUT/'profiles/machine.json').read_text())['extruder_offset'][0].split('x')]

def parse(path):
 xyz={};role='';segments=[];relative=True;last=0
 for line in path.read_text().splitlines():
  if line.startswith(';TYPE:'):role=line[6:]
  cmd=line.split(';')[0].strip()
  if cmd=='M82':relative=False
  if cmd=='M83':relative=True
  if cmd.startswith('G92 '):
   match=re.search(r'E(-?\d*\.?\d+)',cmd)
   if match:last=float(match.group(1))
  if not re.match(r'^G[01] ',cmd):continue
  v={k:float(n) for k,n in re.findall(r'([XYZE])(-?\d*\.?\d+)',cmd)};old=xyz.copy();xyz.update({k:n for k,n in v.items() if k in 'XYZ'})
  if 'E' in v:
   amount=v['E'] if relative else v['E']-last;last=v['E']
   if amount>0 and role not in ('','Custom') and all(k in old and k in xyz for k in 'XYZ') and ('X' in v or 'Y' in v):segments.append((round(xyz['Z'],4),role,[(old['X']+NOZZLE_OFFSET[0],old['Y']+NOZZLE_OFFSET[1]),(xyz['X']+NOZZLE_OFFSET[0],xyz['Y']+NOZZLE_OFFSET[1])]))
 return segments
