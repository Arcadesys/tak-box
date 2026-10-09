"""Check exported assembled pieces against the unchanged V26 STEP case."""
from pathlib import Path
import json, hashlib, sys
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]; REPO=OUT.parents[1]
sys.path.insert(0,str(REPO/'v26/reference/v24/source'))
import case as case

def intersection(a,b):
    return cq.Workplane(obj=a).intersect(cq.Workplane(obj=b),clean=False).val().Volume()

def main():
    checks=[]
    def check(name,ok,**detail):
        checks.append(dict(name=name,passed=bool(ok),**detail))
        assert ok,(name,detail)
    sources={}
    for side,team in (('left','cat'),('right','witch')):
        print('Checking V26 '+side+' '+team,flush=True)
        housing_path=REPO/'v26/models'/f'housing-design-{side}.step'
        board_path=REPO/'v26/models'/f'board-reference-{side}.step'
        housing=cq.importers.importStep(str(housing_path)).val()
        board=cq.importers.importStep(str(board_path)).val()
        for p in (housing_path,board_path):sources[str(p.relative_to(REPO))]=hashlib.sha256(p.read_bytes()).hexdigest()
        regular=cq.importers.importStep(str(OUT/'models'/f'{team}-regular-assembled.step')).val()
        cap=cq.importers.importStep(str(OUT/'models'/f'{team}-capstone-assembled.step')).val()
        bb=cap.BoundingBox()
        check(team+' capstone envelope',bb.xlen<=26.00001 and bb.ylen<=20.00001 and bb.zlen<=8.00001,dimensions_mm=[bb.xlen,bb.ylen,bb.zlen])
        cap=cap.translate((28.6-(bb.xmin+bb.xmax)/2,178.5-(bb.ymin+bb.ymax)/2,3.4))
        stored=[]
        for j in range(7):
            for i in range(3):
                p=regular.translate((23.1+22*i,20.1+22.6*j,3.4))
                stored.append(case.mirror(p) if side=='right' else p)
        stored.append(case.mirror(cap) if side=='right' else cap)
        # Every fixed guide, including the redesigned hat, is checked at its
        # actual storage position. Zero common volume permits face contact.
        for index,p in enumerate(stored):
            v=intersection(housing,p)
            check(f'{side} housing piece {index}',v<1e-5,intersection_mm3=v)
            check(f'{side} piece {index} roof clearance',p.BoundingBox().zmax<=11.40001,piece_top_mm=p.BoundingBox().zmax,nominal_board_bottom_mm=11.8)
        loaded=cq.Compound.makeCompound(stored)
        for distance in (0,2,10,53,106):
            moving=case.slide(board,side,distance)
            v=intersection(moving,loaded)
            check(f'{side} cover slide {distance}mm',v<1e-5,intersection_mm3=v)
        # While folding, both the pieces and their board remain on the same
        # half. Their local clearance is unchanged; check the opposite half.
        if side=='left':left=loaded;left_housing=housing;left_board=board
        else:right=loaded;right_housing=housing;right_board=board
    for angle in (0,45,90,135,180):
        moving=case.fold(right,angle)
        v=intersection(moving,left)
        check(f'loaded opposing pieces fold {angle}deg',v<1e-5,intersection_mm3=v)
        v=intersection(moving,left_housing)
        check(f'right pieces against left housing fold {angle}deg',v<1e-5,intersection_mm3=v)
        v=intersection(case.fold(right_housing,angle),left)
        check(f'left pieces against right housing fold {angle}deg',v<1e-5,intersection_mm3=v)
    report=dict(passed=True,units='mm',case_package='v26',case_geometry_changed=False,piece_package='pieces/weighted-flat-capstones-v2',checks=checks,source_sha256=sources,user_reported_v26_printed=True,exact_print_revision_unknown=True,physical_fit_verified=False,physical_acceptance=False)
    (OUT/'reports/v26-fit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':True,'checks':len(checks),'case_changed':False,'physical_fit_verified':False}),flush=True)
if __name__=='__main__':main()
