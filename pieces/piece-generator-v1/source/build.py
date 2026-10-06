"""Build a complete Tak team from a Piece Generator v1 TOML preset."""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import sys

import cadquery as cq
import numpy as np
import trimesh

import geometry as g
from spec import load_spec
from verify import verify

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "v16-field-book" / "source"))
from mesh_export import export_stl


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


def _save(name: str, obj, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    stl = out_dir / f"{name}.stl"
    step = out_dir / f"{name}.step"
    weld = export_stl(obj, stl)
    cq.exporters.export(obj, str(step))
    mesh = trimesh.load_mesh(stl, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert len(mesh.split()) == 1
    return mesh, {
        "stl": str(stl.relative_to(ROOT)),
        "step": str(step.relative_to(ROOT)),
        "sha256": hashlib.sha256(stl.read_bytes()).hexdigest(),
        "vertex_weld": weld,
        "volume_mm3": float(mesh.volume),
        "dimensions_mm": mesh.extents.tolist(),
    }


def _body_for_print(obj, height):
    # Broad engraved face down, ballast opening up, matching weighted-v1.
    return obj.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, height))


def _package(path: Path, items):
    scene = trimesh.Scene()
    records = []
    for index, (label, mesh, pos) in enumerate(items):
        moved = mesh.copy()
        moved.apply_translation(pos)
        scene.add_geometry(
            moved,
            node_name=f"{index + 1:02d}-{label}",
            geom_name=f"{index + 1:02d}-{label}",
        )
        records.append({"label": label, "position_mm": pos})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(scene.export(file_type="3mf"))
    readback = trimesh.load(path, force="scene")
    assert len(readback.geometry) == len(items)
    assert np.allclose(readback.bounds, scene.bounds, atol=0.001)
    return {
        "objects": len(items),
        "bounds_mm": scene.bounds.tolist(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "parts": records,
    }


def _layout_complete_set(stone_body_mesh, stone_floor_mesh, cap_body_mesh, cap_floor_mesh):
    items = []
    # 21 stone bodies
    for n in range(21):
        items.append((
            "stone-body",
            stone_body_mesh,
            [18 + (n % 7) * 25, 18 + (n // 7) * 25, 0],
        ))
    # 21 floors
    for n in range(21):
        items.append((
            "stone-floor",
            stone_floor_mesh,
            [18 + (n % 7) * 25, 105 + (n // 7) * 25, 0],
        ))
    items.append(("capstone-body", cap_body_mesh, [205, 18, 0]))
    items.append(("capstone-floor", cap_floor_mesh, [205, 52, 0]))
    return items


def _closure_coupon(spec, base_body, mesh_dir):
    variants = [0.20, 0.25, 0.30]
    body_print = _body_for_print(base_body, spec.stone.height)
    body_mesh, body_meta = _save("coupon-body", body_print, mesh_dir)
    items = []
    floors = {}
    for i, hook in enumerate(variants):
        floor = g.make_floor(spec.stone, hook_engagement=hook)
        mesh, meta = _save(f"coupon-floor-hook-{hook:.2f}", floor, mesh_dir)
        floors[f"{hook:.2f}"] = meta
        x = 25 + i * 70
        items.append((f"body-hook-{hook:.2f}", body_mesh, [x, 22, 0]))
        items.append((f"floor-hook-{hook:.2f}", mesh, [x, 52, 0]))
    return items, {
        "hook_engagement_variants_mm": variants,
        "body": body_meta,
        "floors": floors,
        "test": (
            "Snap each pair together dry. Accept only a flush floor with a clean "
            "click, no cracked arm, and no finger-pull release. Destructive removal "
            "is acceptable; this is a one-time closure."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("preset", type=Path)
    args = parser.parse_args()

    preset = args.preset
    if not preset.is_absolute():
        candidate = ROOT / preset
        preset = candidate if candidate.exists() else preset.resolve()
    spec = load_spec(preset)
    slug = _slug(spec.name)

    for directory in ("models", "plates", "reports"):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    mesh_dir = ROOT / "models" / slug
    mesh_dir.mkdir(parents=True, exist_ok=True)

    report, objects = verify(spec)

    stone_body_print = _body_for_print(objects["stone_body"], spec.stone.height)
    cap_body_print = _body_for_print(objects["capstone_body"], spec.capstone.height)

    stone_body_mesh, stone_body_meta = _save("stone-body", stone_body_print, mesh_dir)
    stone_floor_mesh, stone_floor_meta = _save("stone-floor", objects["stone_floor"], mesh_dir)
    cap_body_mesh, cap_body_meta = _save("capstone-body", cap_body_print, mesh_dir)
    cap_floor_mesh, cap_floor_meta = _save("capstone-floor", objects["capstone_floor"], mesh_dir)

    report["exports"] = {
        "stone_body": stone_body_meta,
        "stone_floor": stone_floor_meta,
        "capstone_body": cap_body_meta,
        "capstone_floor": cap_floor_meta,
    }

    complete = _layout_complete_set(
        stone_body_mesh, stone_floor_mesh, cap_body_mesh, cap_floor_mesh
    )
    report["plates"] = {
        "complete_set": _package(
            ROOT / "plates" / f"{slug}-complete-set.3mf", complete
        )
    }

    coupon_items, coupon_report = _closure_coupon(spec, objects["stone_body"], mesh_dir)
    report["closure_coupon"] = coupon_report
    report["plates"]["closure_coupon"] = _package(
        ROOT / "plates" / f"{slug}-closure-fit-coupon.3mf", coupon_items
    )

    report["preset"] = str(preset)
    report_path = ROOT / "reports" / f"{slug}-verification.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps({
        "name": spec.name,
        "stone_ballast": report["stone"]["ballast"],
        "capstone_ballast": report["capstone"]["ballast"],
        "complete_set_objects": report["plates"]["complete_set"]["objects"],
        "coupon_objects": report["plates"]["closure_coupon"]["objects"],
        "report": str(report_path),
    }, indent=2))


if __name__ == "__main__":
    main()
