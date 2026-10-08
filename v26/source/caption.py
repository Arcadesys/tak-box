"""Compose large review captions in a PIL-only process after VTK rendering."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import matplotlib
OUT=Path(__file__).resolve().parents[1]
ROWS={
 '08-combined-trials':('V26 — hook and board clip trials / one plate','Left: captive hook and mount. Right: clip seat and board. Keep the assembly placed as shown.'),
 '01-game-open':('V26 — reinforced board clips / captive hook','Full playing field, PIP main hinges and fixed piece guides retained'),
 '02-board-clip':('Board clip — original behind / V26 in front','Arm: 1.2 → 2.4 mm; gradual 3.2 mm root; release force still needs a print test'),
 '03-captive-hook':('V26 — hook prints captive / parked for printing','Fixed 4 mm axle; 0.4 mm radial and face gaps; no filament pivot or loose collar'),
 '04-hook-section':('Captive hook — cutaway through actual CAD','Fixed 4 mm axle and 0.4 mm running gaps; physical release and retention remain untested'),
 '05-closed':('V26 — closed case / 102.5 × 200 × 35 mm','Hook lever and keeper retained; release effort and transport retention need physical checks'),
 '06-fixed-guides':('V26 — fixed piece guides retained','21 flat stones and one flat capstone per side; no removable trays')}
def main():
 path=Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'
 large=ImageFont.truetype(str(path),31);small=ImageFont.truetype(str(path),22)
 for name,(title,sub) in ROWS.items():
  p=OUT/'previews'/f'{name}.png'
  if not p.exists():continue
  im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im)
  d.rectangle((0,0,im.width,106),fill='white');d.text((45,28),title,font=large,fill='#101820');d.text((45,77),sub,font=small,fill='#182a35');im.save(p)
 print('PASS',len(ROWS),'large high-contrast caption overlays')
if __name__=='__main__':main()
