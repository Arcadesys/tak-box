"""Verify exported trial STLs are closed, oriented, and have expected solids.

The matching STEP file supplies the expected solid count where one exists.
An STL without a matching STEP is expected to contain one solid. A nonzero
component count alone is not a manifold check: every edge must have exactly
two oppositely directed incident triangles and each shell positive volume.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import struct
import sys

OUT = Path(__file__).resolve().parent.parent
MODELS = OUT / "models"


def inspect(path, expected_components=None):
    data = path.read_bytes()
    assert len(data) >= 84, (path.name, "short STL")
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + 50 * count, (path.name, "malformed STL length")
    assert count, (path.name, "empty STL")

    ids, vertices, triangles = {}, [], []
    for i in range(count):
        triangle = []
        for j in range(3):
            point = struct.unpack_from("<3f", data, 84 + 50 * i + 12 + 12 * j)
            if point not in ids:
                ids[point] = len(vertices)
                vertices.append(point)
            triangle.append(ids[point])
        assert len(set(triangle)) == 3, (path.name, i, "degenerate triangle")
        triangles.append(triangle)

    parent = list(range(len(vertices)))

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def join(a, b):
        parent[find(a)] = find(b)

    edges, directions = Counter(), Counter()
    for tri in triangles:
        for a, b in zip(tri, tri[1:] + tri[:1]):
            key = (min(a, b), max(a, b))
            edges[key] += 1
            directions[key] += 1 if a < b else -1
            join(a, b)

    nonmanifold = sum(n != 2 for n in edges.values())
    inconsistent = sum(n != 0 for n in directions.values())
    assert nonmanifold == 0 and inconsistent == 0, (
        path.name, "nonmanifold edges", nonmanifold,
        "inconsistent edges", inconsistent,
    )

    volumes = defaultdict(float)
    for a, b, c in triangles:
        x, y, z = vertices[a], vertices[b], vertices[c]
        triple = (x[0] * (y[1] * z[2] - y[2] * z[1])
                  + x[1] * (y[2] * z[0] - y[0] * z[2])
                  + x[2] * (y[0] * z[1] - y[1] * z[0]))
        volumes[find(a)] += triple / 6
    assert all(v > 0 for v in volumes.values()), (path.name, "reversed or zero shell", volumes)

    step = path.with_suffix(".step")
    if expected_components is not None:
        expected = expected_components
    elif step.exists():
        import cadquery as cq
        expected = len(cq.importers.importStep(str(step)).val().Solids())
    else:
        expected = 1
    assert len(volumes) == expected, (path.name, "components", len(volumes), "expected", expected)
    return {
        "triangles": count,
        "vertices": len(vertices),
        "closed_oriented_components": len(volumes),
        "expected_components": expected,
        "nonmanifold_edges": nonmanifold,
        "inconsistent_edges": inconsistent,
        "component_volumes_mm3": list(volumes.values()),
        "stl_sha256": hashlib.sha256(data).hexdigest(),
        "matching_step_sha256": hashlib.sha256(step.read_bytes()).hexdigest() if step.exists() else None,
    }


def main():
    args = sys.argv[1:]
    expected = None
    if len(args) >= 3 and args[0] == "--expected-components":
        expected = int(args[1])
        args = args[2:]
    paths = [Path(arg) for arg in args] if args else sorted(MODELS.glob("*.stl"))
    assert paths, "No STL exports found"
    report, failures = {}, {}
    for p in paths:
        try:
            report[p.name] = inspect(p, expected)
        except AssertionError as exc:
            failures[p.name] = str(exc)
    reports = OUT / "reports"
    reports.mkdir(exist_ok=True)
    name = "selected-mesh-verification.json" if args else "mesh-verification.json"
    (reports / name).write_text(json.dumps({"passed": report, "failed": failures}, indent=2) + "\n")
    if failures:
        print("FAIL", len(failures), "of", len(paths), "meshes", failures)
        raise SystemExit(1)
    print("PASS", len(report), "meshes")


if __name__ == "__main__":
    main()
