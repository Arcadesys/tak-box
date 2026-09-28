"""Digital acceptance checks for the smooth inward-fold Tak case.

All source and exported-model hashes in the report identify the exact checked
revision. Sampled CAD poses cannot prove loose-piece retention or printed fit.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import struct
import sys

import cadquery as cq
import tak_drawers as v

OUT = Path(__file__).resolve().parent.parent
REPORTS = OUT / "reports"
REPORTS.mkdir(exist_ok=True)
report = {
    "design": "fixed rounded end cheeks, recessed board catches, and face-mounted lift-off trays",
    "physical_fit_accepted": False,
    "purse_smoothness_physically_accepted": False,
    "loose_piece_gravity_retention_proven": False,
    "full_board_print_files_released": False,
    "failed_checks": [],
    "sampled_pose_limitations": [],
}


def require(name, good, details):
    if not good:
        report["failed_checks"].append({"check": name, "details": details})


def bounds(s):
    b = s.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def overlap(a, b):
    aa, bb = a.BoundingBox(), b.BoundingBox()
    if (aa.xmax <= bb.xmin or bb.xmax <= aa.xmin or
        aa.ymax <= bb.ymin or bb.ymax <= aa.ymin or
        aa.zmax <= bb.zmin or bb.zmax <= aa.zmin):
        return 0.0
    return max(0.0, a.intersect(b).Volume())


def stl_bounds(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    assert len(raw) == 84 + 50*n, path
    lo, hi = [math.inf]*3, [-math.inf]*3
    for i in range(n):
        for j in range(3):
            p = struct.unpack_from("<3f", raw, 84 + 50*i + 12 + 12*j)
            for k in range(3):
                lo[k], hi[k] = min(lo[k], p[k]), max(hi[k], p[k])
    return lo, hi, n


def pieces():
    """Use actual STL extents; enclosing boxes are conservative in CAD."""
    poses = {"coordinate_frame": "open-board world; trays seated; local +Z is tray lift",
             "units": "mm", "inward_fold_angle_degrees": -90,
             "hinge_axes": {"wing_a": [0,v.SEAMS[0],v.HINGE_Z],
                             "wing_b": [0,v.SEAMS[1],v.HINGE_Z]},
             "teams": {}}
    envelopes, rows = {}, {}
    for index, team in ((0,"cat"),(2,"witch")):
        mirror = lambda y: y if index == 0 else v.S-y
        flat_name=f"{team}-flat.stl"; cap_name=f"{team}-capstone.stl"
        flo,fhi,fn=stl_bounds(v.ROOT/"references"/flat_name)
        clo,chi,cn=stl_bounds(v.ROOT/"references"/cap_name)
        flat_dims=[fhi[k]-flo[k] for k in range(3)]
        require(team+" actual flat dimensions",all(abs(a-b)<1e-4 for a,b in zip(flat_dims,(19.5,19.5,8))),flat_dims)
        flats=[]; shapes=[]
        for row,y in enumerate(v.FLAT_Y):
            for col,x in enumerate(v.FLAT_X):
                yy=mirror(y)
                translation=[x-(flo[0]+fhi[0])/2,
                             yy-(flo[1]+fhi[1])/2,
                             v.FLAT_BOTTOM-flo[2]]
                bb=[flo[0]+translation[0],fhi[0]+translation[0],
                    flo[1]+translation[1],fhi[1]+translation[1],
                    flo[2]+translation[2],fhi[2]+translation[2]]
                shapes.append(v.box(*bb))
                flats.append({"row":row,"column":col,"translation_mm":translation,"bounds_mm":bb})
        # Positive 90 degrees about Y: raw (x,y,z) -> (z,y,-x).
        rlo=[clo[2],clo[1],-chi[0]]; rhi=[chi[2],chi[1],-clo[0]]
        cy=mirror(v.CAPSTONE_CENTER[1]);cx=v.CAPSTONE_CENTER[0]
        ct=[cx-(rlo[0]+rhi[0])/2,cy-(rlo[1]+rhi[1])/2,v.FLAT_BOTTOM-rlo[2]]
        cb=[rlo[0]+ct[0],rhi[0]+ct[0],rlo[1]+ct[1],rhi[1]+ct[1],rlo[2]+ct[2],rhi[2]+ct[2]]
        shapes.append(v.box(*cb))
        tray=v.tray(index); wing=v.wing(index); grid=v.grid(index)
        contacts={"own_tray":max(overlap(p,tray) for p in shapes),
                  "own_wing":max(overlap(p,wing) for p in shapes),
                  "own_grid":max(overlap(p,grid) for p in shapes)}
        require(team+" 22 seated piece envelopes clear",max(contacts.values())<1e-5,contacts)
        flat_rim_gap=v.TRAY_RIM_TOP-(v.FLAT_BOTTOM+8)
        cap_rim_gap=v.TRAY_RIM_TOP-cb[5]
        require(team+" pieces under continuous rim",flat_rim_gap>=.3 and cap_rim_gap>=.3,
                {"flat_gap_mm":flat_rim_gap,"capstone_gap_mm":cap_rim_gap})
        cradle_y=(31.5,49.5) if index==0 else (v.S-49.5,v.S-31.5)
        require(team+" capstone inside cradle",cb[0]>=171.6+.3 and cb[1]<=197.4-.3 and
                cb[2]>=cradle_y[0]+.3 and cb[3]<=cradle_y[1]-.3,cb)
        rows[team]={"flat_count":len(flats),"flat_dimensions_mm":flat_dims,
                    "flat_source_triangles":fn,"capstone_source_triangles":cn,
                    "capstone_sideways_bounds_mm":cb,"flat_rim_gap_mm":flat_rim_gap,
                    "capstone_rim_gap_mm":cap_rim_gap,"seated_contacts_mm3":contacts}
        poses["teams"][team]={"panel_index":index,"flat_stl":flat_name,"flats":flats,
                              "capstone_stl":cap_name,"capstone_rotation_y_degrees":90,
                              "capstone_translation_after_rotation_mm":ct,
                              "capstone_bounds_mm":cb,
                              "fold_transform":"tak_drawers.posed(shape,panel_index,-90)"}
        envelopes[index]=shapes
    report["pieces"]=rows
    (REPORTS/"piece-poses.json").write_text(json.dumps(poses,indent=2)+"\n")
    return envelopes


def panel_and_table():
    require("205 mm 82+41+82 field",v.S==205 and v.SEAMS==(82.,123.),
            {"side_mm":v.S,"seams_mm":v.SEAMS})
    require("flat-back and tray levels",(v.TOP,v.TRAY_BOTTOM,v.TRAY_FLOOR_TOP)==(4.,5.4,7.),
            {"panel_top":v.TOP,"tray_bottom":v.TRAY_BOTTOM,"tray_floor_top":v.TRAY_FLOOR_TOP})
    panels={"wing-a":v.wing(0),"center":v.center(),"wing-b":v.wing(2)}
    supports={}
    for name,p in panels.items():
        b=bounds(p)
        yy=(20,62) if name=="wing-a" else ((92,113) if name=="center" else (143,185))
        patches=[]
        for x in (25,180):
            for y in yy:
                patch=v.box(x-3,x+3,y-3,y+3,-.001,.101)
                patches.append({"x_mm":x,"y_mm":y,"contact_mm3":overlap(p,patch)})
        supports[name]={"bounds_mm":b,"table_contact_z_mm":b[4],"broad_contact_patches":patches}
        require(name+" table plane",abs(b[4])<1e-5,b)
        require(name+" four broad table contacts",all(t["contact_mm3"]>.01 for t in patches),patches)
        require(name+" valid one solid",p.isValid() and len(p.Solids())==1,
                {"valid":p.isValid(),"solids":len(p.Solids())})
    # Center shoes lie at z=0 and supply the full-length open stop without
    # requiring an obstruction above the playing face.
    shoes={}
    for side in ("left","right"):
        s=v.stop_shoe(side);b=bounds(s)
        shoes[side]=b
        require(side+" shoe flush table plane",abs(b[4])<1e-5 and b[5]<=1.2+1e-5,b)
        require(side+" shoe does not hit center",overlap(s,panels["center"])<1e-5,
                overlap(s,panels["center"]))
    report["table_plane"]={"panels":supports,"stop_shoes":shoes}

    # Hardware owned by wing/center must lie outside x=0..205 when it rises
    # above the playing surface. Grid is the intended playing decoration.
    field=v.box(.0001,v.S-.0001,.0001,v.S-.0001,v.GRID_TOP+.001,30)
    intrusions={name:overlap(p,field) for name,p in panels.items()}
    report["fixed_hardware_above_field_mm3"]=intrusions
    require("no fixed hardware over 205 mm playing field",max(intrusions.values())<1e-5,intrusions)


def protected_shell_and_cc2():
    """Check accessible geometry and bounds; rendered snag review is separate."""
    assert v.CASE_X == (-20.4,225.4)
    cases={}
    for index,label in ((0,"wing-a"),(2,"wing-b")):
        wing=v.wing(index)
        b=bounds(wing)
        cases[label]=b
        require(label+" cheek outer x bounds",abs(b[0]-v.CASE_X[0])<1e-5 and
                abs(b[1]-v.CASE_X[1])<1e-5,b)
        require(label+" cheek one valid solid",wing.isValid() and len(wing.Solids())==1,
                {"valid":wing.isValid(),"solids":len(wing.Solids())})
    center=v.center(); cb=bounds(center)
    cases["center_guard"]=cb
    require("center guard inside cheek profile",cb[0]>=v.CASE_X[0]-1e-5 and
            cb[1]<=v.CASE_X[1]+1e-5,cb)
    press={"opening_y_mm":v.PRESS_Y[1]-v.PRESS_Y[0],
           "opening_z_mm":v.PRESS_Z[1]-v.PRESS_Z[0],
           "right_outer_skin_x_mm":v.CASE_X[1],
           "right_press_face_x_mm":v.TONGUE_X[1],
           "right_tooth_outer_x_mm":bounds(v.closure_tongue("right"))[1]}
    press["press_face_recess_mm"]=press["right_outer_skin_x_mm"]-press["right_press_face_x_mm"]
    press["tooth_clearance_inside_outer_skin_mm"]=press["right_outer_skin_x_mm"]-press["right_tooth_outer_x_mm"]
    require("broad recessed press target",press["opening_y_mm"]>=16 and
            press["opening_z_mm"]>=10 and press["press_face_recess_mm"]>=2.0 and
            press["tooth_clearance_inside_outer_skin_mm"]>=1.0,press)
    require("press stroke bounded",v.PRESS_TRAVEL<=.8, v.PRESS_TRAVEL)
    report["protected_shell"]={"part_bounds_mm":cases,"press_access":press,
        "hinge_outer_profile_radius_mm":v.HINGE_GUARD_R,
        "hinge_bearing_core_radius_mm":v.HINGE_R,
        "x_end_covering":"Wing cheeks occupy local y 0..72 / 133..205; rounded center guards span y76.8..128.2. The fused hinge barrel has one R5.2 outer profile. Check rendered seam and pocket edges separately."}

    # Local CC2 profile is 256 x 256 x 256. The printable part is oriented
    # face-down/back-down by the exporter; evaluate those actual print poses.
    cc2={}
    shapes={**v.mechanical_parts(),"pip-board-engineering":v.top_assembly()}
    for name,s in shapes.items():
        b=bounds(v.print_pose(s))
        dims=[b[1]-b[0],b[3]-b[2],b[5]-b[4]]
        cc2[name]={"print_bounds_mm":b,"dimensions_mm":dims}
        require(name+" CC2 256 mm envelope",all(d<=256+1e-5 for d in dims),dims)
    report["cc2_256mm_nominal_envelope"]=cc2
    report["sampled_pose_limitations"].append("A 256 mm CAD bound does not prove slicer placement, brim clearance, support removal, or print success. Rounded pocket lips and exposed seams require rendered and physical snag inspection.")


def rails_and_stops():
    rails={};stops={}
    for index,label in ((0,"a"),(2,"b")):
        wing=v.wing(index)
        decoration_top=v.grid(index).BoundingBox().zmax
        face_gap=v.TRAY_BOTTOM-decoration_top
        require(f"tray {label} playing-decor clearance",face_gap>=.3,
                {"decoration_top_z_mm":decoration_top,"tray_bottom_z_mm":v.TRAY_BOTTOM,"gap_mm":face_gap})
        report.setdefault("playing_decoration_clearance_mm",{})[label]=face_gap
        for fit in v.FITS:
            tray=v.tray(index,fit)
            allowed=[]
            yy=v.POST_Y if index==0 else tuple(v.S-y for y in v.POST_Y)
            for y in yy:
                for x0,x1 in ((-6.51,-3.49),(208.49,211.51)):
                    if index==0:
                        allowed.append(v.box(x0,x1,y+3.5-v.FITS[fit]-.01,y+3.51,5.59,6.41))
                    else:
                        allowed.append(v.box(x0,x1,y-3.51,y-3.5+v.FITS[fit]+.01,5.59,6.41))
            permitted=cq.Compound.makeCompound(allowed)
            samples=[]
            for lift in (0,.5,1,2,3,4.5,8.5):
                moved=v.lift_tray(tray,index,lift)
                hit=moved.intersect(wing)
                contact=max(0,hit.Volume())
                unexplained=max(0,hit.cut(permitted.translate((0,0,lift))).Volume()) if contact>1e-8 else 0
                row={"lift_mm":lift,"contact_mm3":contact,"unintended_overlap_mm3":unexplained}
                samples.append(row)
                require(f"tray {label} fit {fit} lift {lift:g}",unexplained<1e-5,row)
                grid_hit=overlap(moved,v.grid(index))
                require(f"tray {label} fit {fit} grid lift {lift:g}",grid_hit<1e-5,grid_hit)
            rails[f"{label}-{fit}"]=samples
            if fit=="A":require(f"tray {label} A nominal relief",samples[0]["contact_mm3"]<1e-5,samples[0])
            else:require(f"tray {label} {fit} key pads engage",samples[0]["contact_mm3"]>.01,samples[0])
            require(f"tray {label} {fit} disengaged by 4.5 mm lift",samples[5]["contact_mm3"]<1e-5,samples[5])
        # Open-stop shoe is contact-free at flat, blocks +0.5 degrees past
        # flat, and clears the intended inward fold.
        for side in ("left","right"):
            shoe=v.stop_shoe(side)
            flat=overlap(wing,shoe)
            past=overlap(v.posed(wing,index,.5),shoe)
            inward=overlap(v.posed(wing,index,-5),shoe)
            row={"flat_overlap_mm3":flat,"overopen_half_degree_overlap_mm3":past,
                 "inward_five_degree_overlap_mm3":inward}
            stops[f"{label}-{side}"]=row
            require(f"wing {label} {side} open stop",flat<1e-5 and past>.01 and inward<1e-5,row)
    report["rail_lift_checks"]=rails
    report["new_open_stops"]=stops
    report["sampled_pose_limitations"].append("Tray lift is checked at seven Z positions. Key-pad contact volume is a digital interference, not measured grip force or ease of removal.")


def fold_and_closure(contents=None):
    frame=[cq.Compound.makeCompound([v.wing(0),v.grid(0)]),
           cq.Compound.makeCompound([v.center(),v.grid(1),v.stop_shoe("left"),v.stop_shoe("right")]),
           cq.Compound.makeCompound([v.wing(2),v.grid(2)])]
    full=[]
    # Complete both fold directions separately; one wing may move first.
    angles=tuple(range(0,-91,-10))
    pairs=sorted(set((a,a) for a in angles)|set((a,b) for a in angles for b in (0,-90))|
                 set((b,a) for a in angles for b in (0,-90)))
    for a,b in pairs:
        posed=[v.posed(frame[0],0,a),frame[1],v.posed(frame[2],2,b)]
        vals=[overlap(posed[i],posed[j]) for i,j in ((0,1),(1,2),(0,2))]
        row={"angles_degrees":[a,b],"rigid_overlap_mm3":vals}
        full.append(row)
        require(f"inward frame fold {a}/{b}",max(vals)<1e-5,row)
    report["inward_fold_checks"]=full
    report["sampled_pose_limitations"].append("Fold collision checks sample 10 degree increments with symmetric and one-wing-first angles; unsampled angles are unverified.")

    # Conservative actual-STL envelopes in both mounted trays. Test their
    # paths against the opposing tray, wing, and each other through closure.
    if contents is not None:
        packed=[]
        for angle in (0,-30,-60,-80,-85,-88,-90):
            a=[v.posed(p,0,angle) for p in contents[0]]
            b=[v.posed(p,2,angle) for p in contents[2]]
            tray_a=v.posed(v.tray(0),0,angle)
            tray_b=v.posed(v.tray(2),2,angle)
            other_a=v.posed(v.wing(0),0,angle)
            other_b=v.posed(v.wing(2),2,angle)
            cross=max(overlap(x,y) for x in a for y in b)
            enclosure=max(max(overlap(x,tray_b),overlap(x,other_b)) for x in a)
            enclosure=max(enclosure,max(max(overlap(y,tray_a),overlap(y,other_a)) for y in b))
            row={"angle_degrees":angle,"piece_pair_overlap_mm3":cross,
                 "opposing_hardware_overlap_mm3":enclosure}
            packed.append(row)
            require(f"loaded inward fold {angle}",cross<1e-5 and enclosure<1e-5,row)
        report["loaded_fold_checks"]=packed
        report["sampled_pose_limitations"].append("Loaded fold uses conservative STL bounding boxes at seven inward angles. Gravity-driven movement of loose pieces needs a physical upright-spine/shake trial.")

    closure={}
    # The board-mounted teeth sit behind blind, skinned pockets when seated.
    # A positive catch must block early opening but clear when both recessed
    # tongues move inward against the rigid press stops.
    for fit in v.FITS:
        a=v.wing(0,fit)
        b=v.wing(2,fit)
        tongues=[v.closure_tongue(end,fit) for end in ("left","right")]
        bare=a.cut(tongues[0]).cut(tongues[1])
        samples=[]
        for angle in (-80,-85,-87,-88,-89,-89.5,-89.9,-90):
            aa=v.posed(a,0,angle)
            bb=v.posed(b,2,angle)
            contact=overlap(aa,bb)
            noncatch=overlap(v.posed(bare,0,angle),bb)
            row={"angle_degrees":angle,"wing_contact_mm3":contact,
                 "noncatch_contact_mm3":noncatch}
            samples.append(row)
            require(f"fit {fit} only recessed catches contact at {angle:g}",noncatch<1e-5,row)
        require(f"fit {fit} seated without collision",samples[-1]["wing_contact_mm3"]<1e-5,samples[-1])
        require(f"fit {fit} blocks early opening",samples[5]["wing_contact_mm3"]>.01,samples[5])
        require(f"fit {fit} clears by -87 degrees",samples[2]["wing_contact_mm3"]<1e-5,samples[2])
        released={}
        for travel in (.4,v.PRESS_TRAVEL):
            moved=v.wing_released(fit,travel)
            released[str(travel)]=overlap(v.posed(moved,0,-89.5),v.posed(b,2,-89.5))
            require(f"fit {fit} press release {travel:g} mm",released[str(travel)]<1e-5,released)
        right=tongues[1]
        stop=v.box(*v.PRESS_STOP_X,37,49,4,17)
        at_limit=overlap(right.translate((-v.PRESS_TRAVEL,0,0)),stop)
        over_limit=overlap(right.translate((-(v.PRESS_TRAVEL+.1),0,0)),stop)
        require(f"fit {fit} rigid press stop",at_limit<1e-5 and over_limit>.01,
                {"at_limit_mm3":at_limit,"past_limit_mm3":over_limit})
        closure[fit]={"samples":samples,"released_overlap_mm3":released,
                      "stop_overlap_at_limit_mm3":at_limit,"stop_overlap_past_limit_mm3":over_limit}
    report["recessed_board_catch_checks"]=closure
    report["sampled_pose_limitations"].append("Tongue movement is a rigid geometric displacement of an integral cantilever; printed thumb force, retention under carrying, fatigue, and wear need physical tests.")


def provenance():
    source=Path(__file__).resolve().parent
    names=("tak_drawers.py","build_models.py","verify_geometry.py","verify_meshes.py")
    return {"source":{n:hashlib.sha256((source/n).read_bytes()).hexdigest()
                      for n in names if (source/n).exists()},
            "models":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted((OUT/"models").glob("*"))
                      if p.suffix.lower() in (".stl",".step")}}


def main():
    affected_only=sys.argv[1:]==["--affected-only"]
    if affected_only:
        prior=json.loads((REPORTS/"geometry-verification.json").read_text())
        report.update(prior)
        report["failed_checks"]=[]
        report["reused_unchanged_checks"]={
            "prior_source_sha256":prior["provenance_sha256"]["source"]["tak_drawers.py"],
            "sections":["pieces","loaded_fold_checks"],
            "basis":"Final heel/backing changes are external to the 205 mm piece wells. Piece layout and conservative loaded envelopes are retained; fold, stops, tray lift, field, closure, shell, table, and CC2 checks are rerun.",
        }
    try:
        panel_and_table()
        protected_shell_and_cc2()
        if affected_only:
            rails_and_stops()
            fold_and_closure()
        else:
            rails_and_stops()
            fold_and_closure(pieces())
    finally:
        report["sampled_pose_limitations"]=list(dict.fromkeys(report["sampled_pose_limitations"]))
        report["provenance_sha256"]=provenance()
        (REPORTS/"geometry-verification.json").write_text(json.dumps(report,indent=2)+"\n")
    if report["failed_checks"]:
        print("FAIL",len(report["failed_checks"]),"checks; see geometry-verification.json")
        raise SystemExit(1)
    print("PASS inward-fold board, lift-off trays, contents, stops, and closure")


if __name__=="__main__":
    main()
