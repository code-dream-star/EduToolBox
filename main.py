import os
import sys
import subprocess
from pathlib import Path
# ========== 打包后路径修复，必须放在最前面 ==========
if hasattr(sys, '_MEIPASS'):
    # 打包后运行
    BASE_PATH = sys._MEIPASS
else:
    # 本地源码调试运行
    BASE_PATH = os.path.abspath(".")
# 把 _internal 加入系统路径，让RinUI可以找到自己
if os.path.exists(os.path.join(BASE_PATH, "_internal")):
    sys.path.insert(0, os.path.join(BASE_PATH, "_internal"))
os.chdir(BASE_PATH)
import platform
import wmi
import psutil
from time import time
from PySide6.QtCore import QLocale, QObject, Signal, Slot, Property, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import RinUI
from RinUI import RinUIWindow
from RinUI.core.translator import RinUITranslator
from utils.screenInfo import get_monitor_info


class SystemInfoBackend(QObject):
    # 信号：uptime属性更新时触发
    uptimeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.w = None
        try:
            self.w = wmi.WMI()
        except Exception as e:
            print("WMI初始化失败:", e)
        self._monitor = get_monitor_info()
        # ========== 处理器 ==========
        self._cpu = "未知"
        try:
            cpus = self.w.Win32_Processor()
            if cpus:
                self._cpu = cpus[0].Name.strip()
        except Exception:
            pass
        # ========== 主板 ==========
        self._motherboard = "未知"
        try:
            boards = self.w.Win32_BaseBoard()
            if boards:
                self._motherboard = f"{boards[0].Manufacturer} {boards[0].Product}".strip()
        except Exception:
            pass
        # ========== 内存 ==========
        self._memory = "未知"
        try:
            total_mem = psutil.virtual_memory().total
            total_gb = round(total_mem / (1024**3), 2)
            # 读取内存频率
            mem_speed = ""
            try:
                ram_modules = self.w.Win32_PhysicalMemory()
                if ram_modules:
                    mem_speed = f" {ram_modules[0].Speed} MT/s"
            except Exception:
                pass
            self._memory = f"{total_gb} GB{mem_speed}"
        except Exception:
            pass
        self._gpu = "未知"
        try:
            gpus = self.w.Win32_VideoController()
            gpu_list = [gpu.Name.strip() for gpu in gpus if gpu.Name]
            self._gpu = "\n".join(gpu_list)
        except Exception:
            pass
        # ========== 磁盘（物理硬盘合并） ==========
        self._disk = "未知"
        try:
            disks = self.w.Win32_DiskDrive()
            disk_list = []
            for d in disks:
                if d.Size:
                    size_gb = round(int(d.Size)/(1024**3), 2)
                    disk_list.append(f"{d.Model.strip()} ({size_gb} GB)")
            if disk_list:
                self._disk = "\n".join(disk_list)
        except Exception:
            pass
        # ========== 声卡 ==========
        self._soundcard = "未知"
        try:
            sounds = self.w.Win32_SoundDevice()
            sound_list = [s.Name.strip() for s in sounds if s.Name]
            if sound_list:
                self._soundcard = "\n".join(sound_list)
        except Exception:
            pass
        # ========== 网卡 ==========
        self._network_card = "未知"
        try:
            nics = self.w.Win32_NetworkAdapterConfiguration()
            nic_list = []
            for nic in nics:
                if nic.MACAddress and nic.Caption and not nic.Caption.startswith("Microsoft"):
                    nic_list.append(nic.Caption.strip())
            if nic_list:
                self._network_card = "\n".join(nic_list)
        except Exception:
            pass
        # ========== 系统版本 ==========
        self._systemVersion = platform.platform()
        # ========== 系统运行时间 动态刷新 ==========
        self._uptime = self._get_uptime_text()
        # 定时器 1000ms(1秒)刷新一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_uptime)
        self.timer.start(1000)

    def _get_uptime_text(self):
        try:
            boot_ts = psutil.boot_time()
            now_ts = time()
            delta = int(now_ts - boot_ts)
            days = delta // 86400
            hours = (delta % 86400) // 3600
            mins = (delta % 3600) // 60
            secs = delta % 60
            parts = []
            if days > 0:
                parts.append(f"{days}天")
            parts.append(f"{hours}小时{mins}分{secs}秒")
            return " ".join(parts)
        except Exception as e:
            print("读取运行时间失败", e)
            return "未知"

    def _update_uptime(self):
        new_val = self._get_uptime_text()
        if new_val != self._uptime:
            self._uptime = new_val
            self.uptimeChanged.emit()

    # ========== QML可读取属性 ==========
    @Property(str, constant=True)
    def cpu(self):
        return self._cpu

    @Property(str, constant=True)
    def motherboard(self):
        return self._motherboard

    @Property(str, constant=True)
    def memory(self):
        return self._memory

    @Property(str, constant=True)
    def gpu(self):
        return self._gpu

    @Property(str, constant=True)
    def monitor(self):
        return self._monitor

    @Property(str, constant=True)
    def disk(self):
        return self._disk

    @Property(str, constant=True)
    def soundcard(self):
        return self._soundcard

    @Property(str, constant=True)
    def networkCard(self):
        return self._network_card

    @Property(str, constant=True)
    def systemVersion(self):
        return self._systemVersion

    # uptime：动态属性，notify绑定信号
    @Property(str, notify=uptimeChanged)
    def uptime(self):
        return self._uptime


# 应用程序启动器：供 QML 调用，支持 exe / bat / cmd ，支持管理员UAC提升
class AppLauncher(QObject):
    @Slot(str, bool)
    def launch(self, path: str, run_as_admin: bool = False):
        """
        启动指定路径的程序
        :param path: QML传入字符串
            1. 内置工具简写："geek.exe" / "SysTool/sfc.bat" → 自动拼接 BASE_PATH/tools/xxx
            2. 系统命令：notepad.exe / mmsys.cpl 直接调用系统
            3. 绝对路径：C:/xxx.exe 原样使用
        :param run_as_admin: 是否以管理员权限运行（弹出UAC）
        """
        final_path = path
        try:
            # 判断：不是绝对路径，当成内置tools目录工具处理
            if not os.path.isabs(path):
                final_path = os.path.join(BASE_PATH, "tools", path)
                # 如果拼接后的文件不存在，则视为系统命令，恢复原始path
                if not os.path.exists(final_path):
                    final_path = path

            # 统一路径分隔符，消除 / 和 \ 混用问题
            final_path = os.path.normpath(final_path)
            # 获取文件后缀，区分 exe / bat / cmd
            ext = Path(final_path).suffix.lower()

            if run_as_admin:
                # 需要管理员权限：PowerShell唤起，弹出UAC
                if ext in (".bat", ".cmd"):
                    # bat/cmd 整条ps命令字符串，规避ArgumentList位置参数报错
                    ps_cmd = f'Start-Process cmd -ArgumentList "/c","{final_path}" -Verb RunAs'
                    args = ["powershell", "-Command", ps_cmd]
                else:
                    # exe / cpl 直接管理员启动
                    ps_cmd = f'Start-Process "{final_path}" -Verb RunAs'
                    args = ["powershell", "-Command", ps_cmd]
                subprocess.Popen(args)
            else:
                # 普通权限运行
                if ext in (".bat", ".cmd"):
                    # bat/cmd 使用 cmd /c 执行
                    args = ["cmd", "/c", final_path]
                    subprocess.Popen(args)
                else:
                    # exe、系统命令直接运行
                    subprocess.Popen(final_path, shell=True)

            print(f"启动成功: {final_path} | 管理员模式: {run_as_admin}")
        except Exception as e:
            print(f"启动失败 [{final_path}]: {e}")


if __name__ == '__main__':
    print(RinUI.__file__)
    app = QApplication(sys.argv)
    # 窗口图标：使用全局BASE_PATH，统一路径
    icon_path = os.path.join(BASE_PATH, "assets", "Tool.ico")
    print(f"窗口图标路径：{icon_path}，存在：{os.path.exists(icon_path)}")
    app.setWindowIcon(QIcon(icon_path))
    # 创建 RinUI 窗口（先注入上下文再加载qml）
    gallery = RinUIWindow()
    # 创建实例，注入上下文
    app_launcher = AppLauncher()
    sys_info_backend = SystemInfoBackend()
    # 注入两个对象到QML全局上下文
    gallery.engine.rootContext().setContextProperty("AppLauncher", app_launcher)
    gallery.engine.rootContext().setContextProperty("SysInfo", sys_info_backend)
    # 注入完成后再加载 QML
    gallery.load("qml/Main.qml")
    gallery.setIcon(icon_path)
    gallery.setProperty("title", f"电教工具箱")
    app.exec()
