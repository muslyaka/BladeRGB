import ctypes
import os
from pathlib import Path
import sys


APP_RUN_NAME = "BladeRGB"


def get_foreground_exe():
    if os.name != "nt":
        return None
    try:
        import psutil

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return None

        return psutil.Process(pid.value).name()
    except Exception:
        return None


def autostart_command():
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable)}" --minimized'

    main_py = Path(__file__).resolve().parent / "main.py"
    exe = Path(sys.executable)

    pythonw = exe.with_name("pythonw.exe")
    if pythonw.exists():
        exe = pythonw

    return f'"{exe}" "{main_py}" --minimized'


def set_autostart(enabled):
    if os.name != "nt":
        return False

    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        key_path,
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enabled:
            winreg.SetValueEx(
                key,
                APP_RUN_NAME,
                0,
                winreg.REG_SZ,
                autostart_command(),
            )
        else:
            try:
                winreg.DeleteValue(key, APP_RUN_NAME)
            except FileNotFoundError:
                pass

    return True


def is_autostart_enabled():
    if os.name != "nt":
        return False

    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_READ,
        ) as key:
            value, _ = winreg.QueryValueEx(key, APP_RUN_NAME)
            return bool(value)
    except Exception:
        return False
