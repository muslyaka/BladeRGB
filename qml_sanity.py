from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
QML = ROOT / "qml"

errors = []

sibling_semicolon = re.compile(
    r"\}\s*;\s*[A-Z][A-Za-z0-9_]*\s*\{"
)

for path in QML.rglob("*.qml"):
    text = path.read_text(encoding="utf-8")

    if text.count("{") != text.count("}"):
        errors.append(f"{path}: brace mismatch")

    if sibling_semicolon.search(text):
        errors.append(
            f"{path}: semicolon between sibling QML objects"
        )

if errors:
    print("QML sanity: FAILED")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)

print("QML sanity: OK")
