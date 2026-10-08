"""Compose large review captions in a PIL-only process after VTK rendering."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import matplotlib
OUT=Path(__file__).resolve().parents[1]
ROWS={
 '12-case-plate':('Plate 1 — PIP bodies, fixed guides and captive hook','Keep all three captive components together in their existing placement'),
 '13-board-plate':('Plate 2 — full-size four-colour boards','Slots: 1 black; 2 white; 3 orange accent; 4 purple accent'),
 '14-capstone-plate':('Plate 3 — original flat capstones','Left: Cat. Right: Witch. Optional 8 mm replacements.'),
 '08-combined-trials':('V26 — hook and board clip trials / one plate','Left: captive hook and mount. Right: clip seat and board. Keep the assembly placed as shown.'),
 '01-game-open':('V26 — tab-free boards / captive hook','Full playing field, PIP main hinges and fixed piece guides retained'),
 '02-board-clip':('Board release — old tab behind / solid V26 margin in front','Open the case hook, then slide the board; no flexible release tab'),
 '03-captive-hook':('V26 — hook prints captive / parked for printing','Fixed 4 mm axle; 0.4 mm radial and face gaps; no filament pivot or loose collar'),
 '04-hook-section':('Captive hook — cutaway through actual CAD','Fixed 4 mm axle and 0.4 mm running gaps; physical release and retention remain untested'),
 '05-closed':('V26 — closed case / 102.5 × 200 × 35 mm','Hook lever and keeper retained; release effort and transport retention need physical checks'),
 '06-fixed-guides':('V26 — fixed piece guides retained','21 flat stones and one flat capstone per side; no removable trays')}
def main():
 path=Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'
 for name,(title,sub) in ROWS.items():
  p=OUT/'previews'/f'{name}.png'
  if not p.exists():continue
  large=ImageFont.truetype(str(path),31);small=ImageFont.truetype(str(path),22)
  im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im)
  d.rectangle((0,0,im.width,106),fill='white');d.text((45,28),title,font=large,fill='#101820');d.text((45,77),sub,font=small,fill='#182a35');im.save(p)
 print('PASS',len(ROWS),'large high-contrast caption overlays')
if __name__=='__main__':main()
