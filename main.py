import json
import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from app.controller import BladeController

BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
DATA_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "bladergb.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def build_icon():
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#7772C9"))
    painter.drawRoundedRect(4, 4, 56, 56, 17, 17)
    painter.setBrush(QColor("#D7D4F2"))
    painter.drawRoundedRect(18, 16, 28, 32, 7, 7)
    painter.setBrush(QColor("#20222A"))
    painter.drawRoundedRect(24, 21, 15, 8, 3, 3)
    painter.drawRoundedRect(24, 34, 15, 8, 3, 3)
    painter.end()
    return QIcon(pix)


def main():
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    os.environ.setdefault("QSG_RENDER_LOOP", "threaded")

    app = QApplication(sys.argv)
    app.setApplicationName("BladeRGB")
    app.setOrganizationName("BladeRGB")
    app.setQuitOnLastWindowClosed(False)
    app_font = QFont("Segoe UI Variable")
    app_font.setPointSize(10)
    app.setFont(app_font)
    # BUNDLE_DIR points to the source folder or PyInstaller _MEIPASS.
    # The generated icon is used at runtime, so startup does not depend
    # on an external icon file being accessible.
    icon = build_icon()
    app.setWindowIcon(icon)

    controller = BladeController()

    # Restore the exact last scene, including unsaved slider/palette/reactive
    # adjustments. If there is no autosaved scene yet, fall back to the last
    # explicitly loaded named profile.
    restored_state = controller.settings.get("last_state")
    if not isinstance(restored_state, dict):
        last_profile = controller.settings.get("last_profile", "")
        if last_profile:
            try:
                restored_state = controller.profile_store.load(last_profile)
            except Exception:
                restored_state = None
    if isinstance(restored_state, dict):
        try:
            controller.apply_state(restored_state)
        except Exception:
            logging.exception("Failed to restore last lighting state")

    # Save only when the scene actually changes. Polling also covers future UI
    # controls without requiring a persistence hook in each setter.
    last_saved_fingerprint = {"value": None}

    def save_current_scene(force=False):
        try:
            state = controller.capture_state()
            fingerprint = json.dumps(
                state,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            if force or fingerprint != last_saved_fingerprint["value"]:
                controller.settings.set("last_state", state)
                last_saved_fingerprint["value"] = fingerprint
        except Exception:
            logging.exception("Failed to autosave lighting state")

    save_current_scene(force=True)
    autosave_timer = QTimer(app)
    autosave_timer.setInterval(300)
    autosave_timer.timeout.connect(save_current_scene)
    autosave_timer.start()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("controller", controller)

    qml_file = BUNDLE_DIR / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        raise RuntimeError(f"Unable to load QML: {qml_file}")

    window = engine.rootObjects()[0]

    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("BladeRGB")
    menu = QMenu()
    show_action = QAction("Открыть BladeRGB", menu)
    toggle_action = QAction("Запустить / остановить подсветку", menu)
    blackout_action = QAction("Выключить подсветку", menu)
    quit_action = QAction("Выход", menu)
    menu.addAction(show_action)
    menu.addAction(toggle_action)
    menu.addAction(blackout_action)
    menu.addSeparator()
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()

    def show_window():
        window.show()
        window.raise_()
        window.requestActivate()

    def hide_window():
        window.hide()

    def quit_app():
        save_current_scene(force=True)
        controller.shutdown()
        tray.hide()
        app.quit()

    show_action.triggered.connect(show_window)
    toggle_action.triggered.connect(controller.toggleEngine)
    blackout_action.triggered.connect(controller.blackout)
    quit_action.triggered.connect(quit_app)
    controller.requestShowWindow.connect(show_window)
    controller.requestHideWindow.connect(hide_window)
    controller.requestQuit.connect(quit_app)
    app.aboutToQuit.connect(lambda: save_current_scene(force=True))

    def tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            show_window()

    tray.activated.connect(tray_activated)

    if "--minimized" in sys.argv:
        window.hide()

    code = app.exec()
    save_current_scene(force=True)
    controller.shutdown()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
