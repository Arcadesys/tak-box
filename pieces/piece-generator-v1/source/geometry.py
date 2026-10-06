"""CadQuery geometry engine for Piece Generator v1.

All dimensions are millimetres. Weighted pieces use a mechanically captured
snap floor plus adhesive. The snap is a one-time assembly feature; physical
fit and fatigue are intentionally left for the generated coupon.
"""
from __future__ import annotations

from math import pi, radians, tan
from pathlib import Path
import sys
import cadquery as cq

from spec import StoneSpec, CapstoneSpec, EngravingSpec, TextureSpec


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "pieces"))
import tak_pieces as legacy


def rounded_square(width: float, radius: float, z0: float, height: float):
    return (cq.Workplane("XY", origin=(0, 0, z0))
            .rect(width, width)
            .extrude(height)
            .edges("|Z").fillet(radius))


def rounded_square_area(width: float, radius: float) -> float:
    return width * width - (4.0 - pi) * radius * radius


def solve_cavity(spec) -> dict:
    """Solve cavity width from target usable fill volume with safety limits."""
    engrave_depth = max(0.0, spec.engraving.depth if spec.engraving.kind != "none" else 0.0)
    cavity_top = spec.height - engrave_depth - spec.ballast.minimum_roof
    fill_height = cavity_top - spec.ballast.fill_bottom
    if fill_height <= 0:
        raise ValueError("No positive ballast fill height remains")
    required_area = spec.ballast.target_fill_ml * 1000.0 / fill_height
    correction = (4.0 - pi) * spec.ballast.cavity_radius ** 2
    requested_width = (required_area + correction) ** 0.5
    max_by_wall = spec.width - 2.0 * spec.ballast.minimum_side_wall
    # The bottom opening must still leave a shoulder around the tongue.
    max_by_seat = spec.seat_width - 2.0 * spec.closure.clearance
    cavity_width = min(requested_width, max_by_wall, max_by_seat)
    usable_ml = (rounded_square_area(cavity_width, spec.ballast.cavity_radius)
                 * fill_height / 1000.0)
    return {
        "requested_fill_ml": spec.ballast.target_fill_ml,
        "usable_fill_ml": usable_ml,
        "cavity_width_mm": cavity_width,
        "cavity_top_mm": cavity_top,
        "fill_height_mm": fill_height,
        "side_wall_mm": (spec.width - cavity_width) / 2.0,
        "limited": cavity_width + 1e-9 < requested_width,
    }


def _octagon(width: float, clip: float, height: float):
    h = width / 2.0
    c = clip
    pts = [
        (-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c),
        (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c),
    ]
    return cq.Workplane("XY").polyline(pts).close().extrude(height)


def _builtin_engraving(spec: EngravingSpec, height: float):
    if spec.value == "cat":
        emblem = legacy.cat_emblem(1.1 * spec.scale)
    elif spec.value == "witch":
        emblem = legacy.witch_emblem(1.0 * spec.scale)
    else:
        raise ValueError(f"Unknown builtin engraving: {spec.value}")
    cutter = legacy.emblem_cutter(
        emblem,
        lambda: cq.Workplane("XY", origin=(0, 0, height - spec.depth)),
        spec.depth + 0.10,
        False,
    )
    if spec.rotation:
        cutter = cutter.rotate((0, 0, 0), (0, 0, 1), spec.rotation)
    return cutter


def engraving_cutter(spec: EngravingSpec, height: float):
    if spec.kind == "none" or not spec.value:
        return None
    if spec.depth <= 0:
        raise ValueError("Engraving depth must be positive")
    z = height - spec.depth
    if spec.kind == "builtin":
        return _builtin_engraving(spec, height)
    if spec.kind == "text":
        cutter = cq.Workplane("XY", origin=(0, 0, z)).text(
            spec.value, spec.size, spec.depth + 0.10, combine=False
        )
        if spec.rotation:
            cutter = cutter.rotate((0, 0, 0), (0, 0, 1), spec.rotation)
        return cutter
    if spec.kind == "dxf":
        path = Path(spec.value)
        if not path.is_absolute():
            path = ROOT / path
        wp = cq.importers.importDXF(str(path))
        cutter = wp.extrude(spec.depth + 0.10).translate((0, 0, z))
        if spec.rotation:
            cutter = cutter.rotate((0, 0, 0), (0, 0, 1), spec.rotation)
        return cutter
    raise ValueError(f"Unknown engraving kind: {spec.kind}")


def _front_texture(width: float, height: float, spec: TextureSpec):
    """Subtractive grooves on the -Y face; caller rotates around the piece."""
    if spec.kind == "none":
        return None
    face_y = -width / 2.0
    z0 = max(0.0, spec.z_start)
    z1 = min(height, spec.z_end)
    if z1 <= z0:
        raise ValueError("Texture z_end must exceed z_start")
    span = max(2.0, width - 4.0)
    clip = (cq.Workplane("XY")
            .box(span, spec.depth + 0.30, z1 - z0)
            .translate((0, face_y + spec.depth / 2.0, (z0 + z1) / 2.0)))

    tools = []
    if spec.kind == "vertical_ribs":
        x = -span / 2.0 + spec.pitch / 2.0
        while x < span / 2.0:
            tool = (cq.Workplane("XY")
                    .box(spec.groove_width, spec.depth + 0.30, z1 - z0 + 0.20)
                    .translate((x, face_y + spec.depth / 2.0, (z0 + z1) / 2.0)))
            tools.append(tool.val())
            x += spec.pitch
    elif spec.kind in {"diagonal", "diamond"}:
        # angle is measured from horizontal in the XZ view.
        slope = 1.0 / tan(radians(max(5.0, min(85.0, abs(spec.angle)))))
        half = spec.groove_width / 2.0
        directions = (-1, 1) if spec.kind == "diamond" else (1 if spec.angle >= 0 else -1,)
        count = int(width / max(spec.pitch, 0.5)) + 5
        for direction in directions:
            for index in range(-count, count + 1):
                intercept = index * spec.pitch
                low, high = z0 - 1.0, z1 + 1.0
                xa = intercept + direction * slope * (low - height / 2.0)
                xb = intercept + direction * slope * (high - height / 2.0)
                points = [
                    (xa - half, low), (xa + half, low),
                    (xb + half, high), (xb - half, high),
                ]
                tool = (cq.Workplane("XZ", origin=(0, face_y - 0.10, 0))
                        .polyline(points).close().extrude(-(spec.depth + 0.30)))
                tools.append(tool.val())
    else:
        raise ValueError(f"Unknown texture kind: {spec.kind}")

    if not tools:
        return None
    return cq.Workplane(obj=cq.Compound.makeCompound(tools)).intersect(clip)


def apply_texture(body, width: float, height: float, spec: TextureSpec):
    grooves = _front_texture(width, height, spec)
    if grooves is None:
        return body
    out = body
    for angle in (0, 90, 180, 270):
        out = out.cut(grooves.rotate((0, 0, 0), (0, 0, 1), angle))
    return out.clean()


def _snap_pockets(body, spec):
    """Cut two retaining pockets into opposite sides of the floor rabbet."""
    if spec.closure.kind != "snap":
        raise ValueError("Weighted v1 requires closure.kind='snap'")
    seat_half = spec.seat_width / 2.0
    c = spec.closure
    y = c.arm_length / 2.0 - c.hook_width * 0.75
    z0 = 0.20
    for sx in (-1, 1):
        x = sx * (seat_half + (c.hook_engagement + c.clearance) / 2.0)
        pocket = (cq.Workplane("XY")
                  .box(c.hook_engagement + c.clearance + 0.35,
                       c.hook_width + 0.35,
                       c.pocket_height)
                  .translate((x, y, z0 + c.pocket_height / 2.0)))
        body = body.cut(pocket)
    return body


def make_body(spec):
    solved = solve_cavity(spec)
    shell = rounded_square(spec.width, spec.corner_radius, 0, spec.height)
    shell = shell.faces(">Z or <Z").edges().chamfer(spec.edge_chamfer)
    seat = rounded_square(spec.seat_width, spec.seat_radius, -0.10, spec.seat_depth + 0.10)
    cavity = rounded_square(
        solved["cavity_width_mm"], spec.ballast.cavity_radius,
        spec.seat_depth - 0.01,
        solved["cavity_top_mm"] - spec.seat_depth + 0.01,
    )
    body = shell.cut(seat).cut(cavity)
    body = _snap_pockets(body, spec)
    mark = engraving_cutter(spec.engraving, spec.height)
    if mark is not None:
        body = body.cut(mark)
    body = apply_texture(body, spec.width, spec.height, spec.texture)
    return body.clean(), solved


def _snap_hook(sx: int, plate_half: float, c, y_center: float):
    """Wedge with a flat retaining underside and insertion ramp above it."""
    total = c.clearance + c.hook_engagement
    x0 = sx * plate_half
    x1 = sx * (plate_half + total)
    z_bottom, z_shoulder, z_outer_top, z_top = 0.18, 0.30, 0.46, 0.82
    if sx > 0:
        points = [(x0, z_bottom), (x0, z_shoulder), (x1, z_shoulder),
                  (x1, z_outer_top), (x0, z_top)]
    else:
        points = [(x0, z_bottom), (x0, z_shoulder), (x1, z_shoulder),
                  (x1, z_outer_top), (x0, z_top)]
    return (cq.Workplane("XZ", origin=(0, y_center, 0))
            .polyline(points).close().extrude(c.hook_width / 2.0, both=True))


def make_floor(spec, clearance: float | None = None, hook_engagement: float | None = None):
    """One-piece floor with two in-plane cantilever snap arms.

    Long through-slots isolate narrow edge arms in the floor plane. The hooks
    cam inward during insertion and spring into body pockets when seated.
    """
    c = spec.closure
    clearance = c.clearance if clearance is None else clearance
    hook_engagement = c.hook_engagement if hook_engagement is None else hook_engagement
    plate_width = spec.seat_width - 2.0 * clearance
    plate_radius = max(0.20, spec.seat_radius - clearance)
    floor = rounded_square(plate_width, plate_radius, 0, spec.floor_thickness)

    solved = solve_cavity(spec)
    tongue_width = solved["cavity_width_mm"] - 2.0 * clearance
    tongue = rounded_square(
        tongue_width,
        max(0.20, spec.ballast.cavity_radius - clearance),
        spec.floor_thickness - 0.01,
        spec.tongue_height + 0.01,
    )
    floor = floor.union(tongue)

    plate_half = plate_width / 2.0
    arm_y0 = -c.arm_length / 2.0 + c.attach_length
    arm_y1 = c.arm_length / 2.0 + c.slot_gap / 2.0
    long_len = arm_y1 - arm_y0
    long_y = (arm_y0 + arm_y1) / 2.0

    # Cut a longitudinal isolation slot and a transverse free-end slot on
    # each side. Slots pass through plate+tongue so each edge strip bends
    # in-plane over several millimetres instead of acting as a tiny Z spring.
    for sx in (-1, 1):
        inner_edge = plate_half - c.arm_width
        slot_x = sx * (inner_edge - c.slot_gap / 2.0)
        long_slot = (cq.Workplane("XY")
                     .box(c.slot_gap, long_len, spec.floor_thickness + spec.tongue_height + 0.40)
                     .translate((slot_x, long_y,
                                 (spec.floor_thickness + spec.tongue_height) / 2.0)))
        floor = floor.cut(long_slot)
        end_x = sx * (plate_half - (c.arm_width + c.slot_gap) / 2.0)
        end_slot = (cq.Workplane("XY")
                    .box(c.arm_width + c.slot_gap + 0.50, c.slot_gap,
                         spec.floor_thickness + spec.tongue_height + 0.40)
                    .translate((end_x, c.arm_length / 2.0,
                                (spec.floor_thickness + spec.tongue_height) / 2.0)))
        floor = floor.cut(end_slot)

    # Hooks sit near each free end. Override engagement for coupon variants.
    effective = type(c)(
        kind=c.kind, clearance=clearance, arm_length=c.arm_length,
        arm_width=c.arm_width, slot_gap=c.slot_gap, attach_length=c.attach_length,
        hook_engagement=hook_engagement, hook_width=c.hook_width,
        pocket_height=c.pocket_height,
    )
    hook_y = c.arm_length / 2.0 - c.hook_width * 0.75
    for sx in (-1, 1):
        floor = floor.union(_snap_hook(sx, plate_half, effective, hook_y))
    return floor.clean()


def _capstone_outer(spec: CapstoneSpec):
    if spec.shape == "octagon":
        return _octagon(spec.width, spec.corner_clip, spec.height)
    if spec.shape == "round":
        return cq.Workplane("XY").circle(spec.width / 2.0).extrude(spec.height)
    if spec.shape == "clipped_square":
        return _octagon(spec.width, max(1.0, spec.corner_clip), spec.height)
    raise ValueError(f"Unknown capstone shape: {spec.shape}")


def make_capstone_body(spec: CapstoneSpec):
    solved = solve_cavity(spec)
    shell = _capstone_outer(spec)
    seat = rounded_square(spec.seat_width, spec.seat_radius, -0.10, spec.seat_depth + 0.10)
    cavity = rounded_square(
        solved["cavity_width_mm"], spec.ballast.cavity_radius,
        spec.seat_depth - 0.01,
        solved["cavity_top_mm"] - spec.seat_depth + 0.01,
    )
    body = shell.cut(seat).cut(cavity)
    body = _snap_pockets(body, spec)
    mark = engraving_cutter(spec.engraving, spec.height)
    if mark is not None:
        body = body.cut(mark)
    body = apply_texture(body, spec.width, spec.height, spec.texture)
    return body.clean(), solved


def make_capstone_floor(spec: CapstoneSpec, clearance=None, hook_engagement=None):
    return make_floor(spec, clearance=clearance, hook_engagement=hook_engagement)
