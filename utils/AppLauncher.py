from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QQmlComponent
import subprocess
import os

class AppLauncher(QObject):
    def __init__(self, engine, base_path, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.BASE_PATH = base_path
        self.qmlWindows = {}

    @Slot(str, bool)
    def launch(self, path: str, runAsAdmin: bool):
        full_path = os.path.join(self.BASE_PATH, path)
        ext = os.path.splitext(path)[1].lower()

        if ext == ".qml":
            self.openQmlWindow(full_path)
            return

        if not os.path.exists(full_path):
            print(f"文件不存在：{full_path}")
            return
        try:
            ext = os.path.splitext(full_path)[1].lower()
            if ext in (".bat", ".cmd"):
                cmd = ["cmd", "/c", full_path]
            elif ext == ".ps1":
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", full_path]
            else:
                cmd = [full_path]

            if runAsAdmin:
                subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            print(f"启动失败: {e}")

    # def openQmlWindow(self, qmlFilePath):
    #     print(f"【openQmlWindow】传入路径：{qmlFilePath}")
    #     # 校验缓存里的窗口对象是否有效
    #     if qmlFilePath in self.qmlWindows:
    #         win = self.qmlWindows[qmlFilePath]
    #         try:
    #             win.objectName()
    #         except RuntimeError:
    #             print("【openQmlWindow】缓存对象已销毁，删除缓存")
    #             del self.qmlWindows[qmlFilePath]
    #         else:
    #             print("【openQmlWindow】复用已有窗口")
    #             win.show()
    #             win.raise_()
    #             return

    #     print("【openQmlWindow】新建QML组件")
    #     comp = QQmlComponent(self.engine, qmlFilePath)
    #     if comp.isError():
    #         print("【openQmlWindow】QML加载错误:", comp.errorString())
    #         return
    #     win = comp.createObject()
    #     if win is None:
    #         print("【openQmlWindow】createObject 返回 None！")
    #         return
    #     print(f"【openQmlWindow】创建成功 win={win}")

    #     self.qmlWindows[qmlFilePath] = win
    #     win.show()
    #     win.raise_()

    #     def on_win_destroyed():
    #         try:
    #             del self.qmlWindows[qmlFilePath]
    #             print("【openQmlWindow】窗口销毁，清理缓存")
    #         except KeyError:
    #             pass
    #     win.destroyed.connect(on_win_destroyed)
