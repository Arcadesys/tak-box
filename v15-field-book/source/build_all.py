"""Run the whole v15 build in order and log it.

Each step's output is streamed to the terminal and to logs/build-<time>.log,
prefixed with the elapsed time, and each step ends with its duration. The
build stops at the first step that fails. `--from verify_book` resumes
partway; `--only render_book` runs a single step.
"""
from datetime import datetime
from pathlib import Path
import argparse,subprocess,sys,time

HERE=Path(__file__).resolve().parent
LOGS=HERE.parent/'logs'
STEPS=['build_models','verify_book','verify_meshes','render_book','package_plates']

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--from',dest='start',choices=STEPS)
    ap.add_argument('--only',choices=STEPS)
    a=ap.parse_args()
    steps=[a.only] if a.only else STEPS[STEPS.index(a.start):] if a.start else STEPS
    LOGS.mkdir(exist_ok=True)
    path=LOGS/f"build-{datetime.now():%Y%m%d-%H%M%S}.log"
    t0=time.monotonic()
    with open(path,'w') as log:
        def out(msg):
            line=f'[{time.monotonic()-t0:7.1f}s] {msg}'
            print(line,flush=True);log.write(line+'\n');log.flush()
        out(f'python {sys.executable}; log {path}')
        for i,step in enumerate(steps,1):
            out(f'== {i}/{len(steps)} {step}')
            s0=time.monotonic()
            p=subprocess.Popen([sys.executable,'-u',f'{step}.py'],cwd=HERE,text=True,
                               stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            for line in p.stdout:out(f'  {step}: {line.rstrip()}')
            code=p.wait()
            if code:
                out(f'!! {step} FAILED (exit {code}) after {time.monotonic()-s0:.1f}s')
                sys.exit(code)
            out(f'== {step} done in {time.monotonic()-s0:.1f}s')
        out(f'build ok in {time.monotonic()-t0:.1f}s')

if __name__=='__main__':main()
