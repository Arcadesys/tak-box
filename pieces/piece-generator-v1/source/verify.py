"""Digital verification for Piece Generator v1.

These checks validate CAD invariants only. They do not claim a successful
physical snap, adhesive bond, ballast recipe, print, or tactile result.
"""
from __future__ import annotations
import numpy as np
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

import geometry as g


def bounds(obj):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(obj.val().wrapped, box, False, False)
    x0, y0, z0, x1, y1, z1 = box.Get()
    return np.array([[x0, y0, z0], [x1, y1, z1]])


def _check_solid(name, obj):
    assert obj.val().isValid(), f"{name}: invalid CAD solid"
    assert len(obj.val().Solids()) == 1, f"{name}: expected one solid"


def _piece_report(label, spec, body, floor, solved):
    _check_solid(f"{label} body", body)
    _check_solid(f"{label} floor", floor)
    overlap = body.intersect(floor).val().Volume()
    assert overlap < 1e-5, (label, "body/floor overlap", overlap)

    assembled = body.union(floor)
    _check_solid(f"{label} assembled", assembled)
    b = bounds(assembled)
    dims = b[1] - b[0]
    assert abs(dims[0] - spec.width) < 1e-6
    assert abs(dims[1] - spec.width) < 1e-6
    assert abs(dims[2] - spec.height) < 1e-6

    stack_overlap = assembled.intersect(
        assembled.translate((0, 0, spec.height))
    ).val().Volume()
    assert stack_overlap < 1e-5, (label, "stack overlap", stack_overlap)

    wall = (assembled.rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((0, spec.height, spec.width / 2.0)))
    wb = bounds(wall)
    assert abs(wb[0, 2]) < 1e-6
    assert abs((wb[1] - wb[0])[2] - spec.width) < 1e-6

    engrave_depth = spec.engraving.depth if spec.engraving.kind != "none" else 0.0
    roof = spec.height - solved["cavity_top_mm"] - engrave_depth
    assert roof + 1e-9 >= spec.ballast.minimum_roof
    assert solved["side_wall_mm"] + 1e-9 >= spec.ballast.minimum_side_wall

    c = spec.closure
    assert c.kind == "snap"
    assert c.arm_length >= 3.0
    assert 0.10 <= c.hook_engagement <= 0.40
    assert c.slot_gap >= 0.25

    return {
        "dimensions_mm": dims.tolist(),
        "body_volume_mm3": body.val().Volume(),
        "floor_volume_mm3": floor.val().Volume(),
        "body_floor_overlap_mm3": overlap,
        "stack_overlap_mm3": stack_overlap,
        "standing_wall_envelope_mm": (wb[1] - wb[0]).tolist(),
        "ballast": solved,
        "roof_under_engraving_mm": roof,
        "closure": {
            "kind": c.kind,
            "arm_length_mm": c.arm_length,
            "arm_width_mm": c.arm_width,
            "slot_gap_mm": c.slot_gap,
            "hook_engagement_mm": c.hook_engagement,
            "clearance_mm": c.clearance,
            "digital_geometry_only": True,
            "physical_snap_tested": False,
        },
    }


def verify(spec):
    stone_body, stone_fill = g.make_body(spec.stone)
    stone_floor = g.make_floor(spec.stone)
    cap_body, cap_fill = g.make_capstone_body(spec.capstone)
    cap_floor = g.make_capstone_floor(spec.capstone)

    report = {
        "units": "mm",
        "generator": "piece-generator-v1",
        "name": spec.name,
        "stone": _piece_report(
            "stone", spec.stone, stone_body, stone_floor, stone_fill
        ),
        "capstone": _piece_report(
            "capstone", spec.capstone, cap_body, cap_floor, cap_fill
        ),
        "physical_acceptance": {
            "printed": False,
            "snap_retention_tested": False,
            "ballast_mass_tested": False,
            "adhesive_tested": False,
            "stack_feel_tested": False,
        },
    }
    assert (
        spec.capstone.shape != "clipped_square"
        or spec.capstone.height >= spec.stone.height + 1.0
    ), "Capstone must remain tactilely distinct"
    assert (
        spec.capstone.shape != "octagon"
        or spec.capstone.corner_clip >= 1.5
    ), "Octagonal capstone clip is too subtle"

    return report, {
        "stone_body": stone_body,
        "stone_floor": stone_floor,
        "capstone_body": cap_body,
        "capstone_floor": cap_floor,
    }
