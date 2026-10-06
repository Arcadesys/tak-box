"""Declarative configuration for Piece Generator v1."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class EngravingSpec:
    kind: str = "none"  # none, text, builtin, dxf
    value: str = ""
    depth: float = 0.40
    size: float = 10.0
    scale: float = 1.0
    rotation: float = 0.0


@dataclass(frozen=True)
class TextureSpec:
    kind: str = "none"  # none, vertical_ribs, diagonal, diamond
    depth: float = 0.35
    groove_width: float = 0.75
    pitch: float = 2.40
    angle: float = 45.0
    z_start: float = 1.25
    z_end: float = 4.75


@dataclass(frozen=True)
class BallastSpec:
    target_fill_ml: float = 0.90
    minimum_side_wall: float = 1.20
    minimum_roof: float = 0.80
    fill_bottom: float = 1.90
    cavity_radius: float = 0.80


@dataclass(frozen=True)
class ClosureSpec:
    kind: str = "snap"
    clearance: float = 0.20
    arm_length: float = 4.00
    arm_width: float = 0.80
    slot_gap: float = 0.35
    attach_length: float = 0.60
    hook_engagement: float = 0.25
    hook_width: float = 0.85
    pocket_height: float = 0.60


@dataclass(frozen=True)
class StoneSpec:
    width: float = 20.0
    height: float = 6.0
    corner_radius: float = 2.0
    edge_chamfer: float = 0.40
    seat_width: float = 18.0
    seat_radius: float = 1.0
    seat_depth: float = 1.20
    floor_thickness: float = 1.00
    tongue_height: float = 0.60
    engraving: EngravingSpec = field(default_factory=EngravingSpec)
    texture: TextureSpec = field(default_factory=TextureSpec)
    ballast: BallastSpec = field(default_factory=BallastSpec)
    closure: ClosureSpec = field(default_factory=ClosureSpec)


@dataclass(frozen=True)
class CapstoneSpec:
    shape: str = "octagon"
    width: float = 20.0
    height: float = 7.5
    corner_clip: float = 3.0
    seat_width: float = 15.8
    seat_radius: float = 0.8
    seat_depth: float = 1.20
    floor_thickness: float = 1.00
    tongue_height: float = 0.60
    engraving: EngravingSpec = field(default_factory=EngravingSpec)
    texture: TextureSpec = field(default_factory=lambda: TextureSpec(kind="vertical_ribs", z_end=6.25))
    ballast: BallastSpec = field(default_factory=BallastSpec)
    closure: ClosureSpec = field(default_factory=ClosureSpec)


@dataclass(frozen=True)
class PieceSetSpec:
    name: str
    stone: StoneSpec = field(default_factory=StoneSpec)
    capstone: CapstoneSpec = field(default_factory=CapstoneSpec)


def _nested(cls, data):
    return cls(**(data or {}))


def load_spec(path: str | Path) -> PieceSetSpec:
    path = Path(path)
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    stone_raw = raw.get("stone", {})
    cap_raw = raw.get("capstone", {})
    stone = StoneSpec(
        **{k: v for k, v in stone_raw.items() if k not in {"engraving", "texture", "ballast", "closure"}},
        engraving=_nested(EngravingSpec, stone_raw.get("engraving")),
        texture=_nested(TextureSpec, stone_raw.get("texture")),
        ballast=_nested(BallastSpec, stone_raw.get("ballast")),
        closure=_nested(ClosureSpec, stone_raw.get("closure")),
    )
    capstone = CapstoneSpec(
        **{k: v for k, v in cap_raw.items() if k not in {"engraving", "texture", "ballast", "closure"}},
        engraving=_nested(EngravingSpec, cap_raw.get("engraving")),
        texture=_nested(TextureSpec, cap_raw.get("texture")),
        ballast=_nested(BallastSpec, cap_raw.get("ballast")),
        closure=_nested(ClosureSpec, cap_raw.get("closure")),
    )
    return PieceSetSpec(name=raw.get("name", path.stem), stone=stone, capstone=capstone)
