import os
import sys
import subprocess
from pathlib import Path

# ========== 打包后路径修复，必须放在最前面 ==========
if hasattr(sys, '_MEIPASS'):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath(".")

if os.path.exists(os.path.join(BASE_PATH, "_internal")):
    sys.path.insert(0, os.path.join(BASE_PATH, "_internal"))
os.chdir(BASE_PATH)

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

import RinUI
from RinUI import RinUIWindow
from RinUI.core.translator import RinUITranslator
from utils.pingModel import PingModel
from utils.systemInfoBackend import SystemInfoBackend
from utils.pingModel import PingModel
from utils.AppLauncher import AppLauncher

__version__ = "0.1.0"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qmlRegisterType(PingModel, "RinUI", 1, 0, "PingModel")
    qmlRegisterType(PingModel, "PingModelLib", 1, 0, "PingModel")

    icon_path = os.path.join(BASE_PATH, "assets", "Tool.ico")
    print(f"窗口图标路径：{icon_path}，存在：{os.path.exists(icon_path)}")
    app.setWindowIcon(QIcon(icon_path))

    gallery = RinUIWindow()
    app_launcher = AppLauncher(engine, BASE_PATH)
    sys_info_backend = SystemInfoBackend()

    gallery.engine.rootContext().setContextProperty("AppLauncher", app_launcher)
    gallery.engine.rootContext().setContextProperty("SysInfo", sys_info_backend)

    gallery.load("qml/Main.qml")
    gallery.setIcon(icon_path)
    gallery.setProperty("title", f"电教工具箱")
    app.setWindowIcon(QIcon(icon_path))
    gallery.setProperty("title", f"电教工具箱")
    app.exec()
