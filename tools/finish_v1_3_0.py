from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QML = ROOT / "qml"

# Qt's parser is much happier when sibling object declarations are not
# separated with JavaScript-style semicolons. Normalize every generated page.
sibling = re.compile(r"}\s*;\s*([A-Z][A-Za-z0-9_]*\s*\{)")
for path in QML.rglob("*.qml"):
    text = path.read_text(encoding="utf-8")
    text = sibling.sub(r"}\n\1", text)
    path.write_text(text, encoding="utf-8")

# Local directory singleton: no URI declaration is needed for `import \"components\"`.
qmldir = QML / "components" / "qmldir"
qmldir.write_text("singleton Theme 1.0 Theme.qml\n", encoding="utf-8")

# Avoid relying on CanvasRenderingContext2D.reset(), which is not available in
# every Qt 6 minor version. clearRect is sufficient because we recreate the
# wheel every paint pass.
picker = QML / "components" / "RGBWPicker.qml"
text = picker.read_text(encoding="utf-8")
text = text.replace('                    ctx.reset()\n', '')
picker.write_text(text, encoding="utf-8")

print("BladeRGB 1.3.0 QML cleanup applied")
