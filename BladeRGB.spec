# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
project = Path(SPECPATH)
a = Analysis(
    ["main.py"],
    pathex=[str(project)],
    binaries=[],
    datas=[
        (str(project / "qml"), "qml"),
        (str(project / "assets"), "assets"),
        (str(project / "config"), "config"),
    ],
    hiddenimports=[
        "hid","soundcard","mss","psutil",
        "PySide6.QtQuick","PySide6.QtQml",
        "PySide6.QtQuickControls2","PySide6.QtQuickDialogs2",
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="BladeRGB", console=False, debug=False, strip=False, upx=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name="BladeRGB")
