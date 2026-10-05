"""Verify the frozen v18 package; does not rebuild CAD or attest physical fit."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "docs/V18-FREEZE.json").read_text())
errors = []
for entry in lock["files"]:
    path = ROOT / entry["path"]
    if not path.is_file():
        errors.append(f"missing: {entry['path']}")
        continue
    data = path.read_bytes()
    if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
        errors.append(f"changed: {entry['path']}")
    if path.suffix == ".py":
        ast.parse(data, filename=str(path))
package = ROOT / lock["closure_package"]
expected = {entry["path"] for entry in lock["files"]}
actual = {path.relative_to(ROOT).as_posix() for path in package.rglob("*")
          if path.is_file() and "__pycache__" not in path.parts}
for path in sorted(actual - expected):
    errors.append(f"unfrozen file: {path}")
original = json.loads((package / "PACKAGE-MANIFEST.json").read_text())
for entry in original:
    path = package / entry["path"]
    if not path.is_file():
        continue  # Already reported above.
    data = path.read_bytes()
    if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
        errors.append(f"original manifest mismatch: {entry['path']}")
with zipfile.ZipFile(package / "release/tak-v18-recessed-clasp-coupon-kit.zip") as kit:
    failure = kit.testzip()
    if failure:
        errors.append(f"ZIP CRC failed: {failure}")
source_hash = hashlib.sha256((package / "build.py").read_bytes()).hexdigest()
for name, key in [("validation.json", "build_sha256"),
                  ("review/review-verdict.json", "source_sha256")]:
    report = json.loads((package / name).read_text())
    if report[key] != source_hash:
        errors.append(f"report/source mismatch: {name}")
if errors:
    raise SystemExit("V18 freeze FAILED\n" + "\n".join(errors))
print(f"V18 freeze PASS: {len(expected)} pinned files; {len(original)} original manifest entries; "
      "ZIP CRC, Python syntax and review/source hashes match.")
print("Complete-case release and physical acceptance remain pending.")
