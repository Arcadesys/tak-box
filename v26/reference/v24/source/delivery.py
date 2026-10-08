"""One mapping from accepted build outputs to the shallow, user-facing kit."""
from pathlib import Path
import hashlib,shutil
REFERENCE=Path(__file__).resolve().parents[1]
ROOT=REFERENCE.parent
FULL={
 '01-FULL-paired-bases-CC2-PLA.3mf':'PRINT/01-print-in-place-bases-CC2-PLA.3mf',
 '02-FULL-SIZE-FOUR-COLOUR-inlaid-boards-CC2-PLA.3mf':'PRINT/02-sliding-board-tops-CC2-PLA.3mf',
 '03-FULL-removable-player-trays-CC2-PLA.3mf':'PRINT/03-removable-player-trays-CC2-PLA.3mf',
 '04-FULL-flat-capstones-hook-and-collar-CC2-PLA.3mf':'PRINT/04-flat-capstones-hook-and-collar-CC2-PLA.3mf'}
TRIALS={
 '01-SMALL-hinge-support-trial-CC2-PLA.3mf':'FIT-CHECK/captive-hinge-fit-check-CC2-PLA.3mf',
 '02-SMALL-removable-tray-access-trial-CC2-PLA.3mf':'TRAY-FIT/removable-tray-access-trial-CC2-PLA.3mf',
 '03-SMALL-FOUR-COLOUR-inlay-trial-CC2-PLA.3mf':'INLAY-FIT/four-colour-inlay-trial-CC2-PLA.3mf'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def publish():
 rows=[]
 for folder,mapping in [('FULL-PRINT',FULL),('SMALL-TRIALS',TRIALS)]:
  target=ROOT/folder;target.mkdir(exist_ok=True)
  for name,source in mapping.items():
   src=REFERENCE/source;dest=target/name
   assert src.is_file(),src
   if not dest.exists() or sha(dest)!=sha(src):shutil.copy2(src,dest)
   assert sha(dest)==sha(src)
   rows.append({'path':str(dest.relative_to(ROOT)),'accepted_build_output':'REFERENCE/'+source,'sha256':sha(dest)})
  # Never silently delete user files. An unexpected file makes the audit fail.
  assert {p.name for p in target.iterdir()}==set(mapping),(folder,'unexpected file')
 shutil.copy2(REFERENCE/'previews/03-table-setup.png',ROOT/'PREVIEW.png')
 return rows
if __name__=='__main__':
 for row in publish():print(row['path'])
