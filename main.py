import os
import sys
import subprocess
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
        except: pass
        # ========== 主板 ==========
        self._motherboard = "未知"
        try:
            boards = self.w.Win32_BaseBoard()
            if boards:
                self._motherboard = f"{boards[0].Manufacturer} {boards[0].Product}".strip()
        except: pass
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
            except: pass
            self._memory = f"{total_gb} GB{mem_speed}"
        except: pass
        self._gpu = "未知"
        try:
            gpus = self.w.Win32_VideoController()
            gpu_list = [gpu.Name.strip() for gpu in gpus if gpu.Name]
            self._gpu = "\n".join(gpu_list)
        except: pass
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
        except: pass
        # ========== 声卡 ==========
        self._soundcard = "未知"
        try:
            sounds = self.w.Win32_SoundDevice()
            sound_list = [s.Name.strip() for s in sounds if s.Name]
            if sound_list:
                self._soundcard = "\n".join(sound_list)
        except: pass
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
        except: pass
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


# 应用程序启动器：供 QML 调用，用于打开本地 exe / cpl 等程序
class AppLauncher(QObject):
    @Slot(str)
    def launch(self, path: str):
        """
        启动指定路径的程序
        :param path: QML传入字符串
            1. 内置工具简写："geek.exe" → 自动拼接 BASE_PATH/tools/geek.exe
            2. 系统命令：notepad.exe / mmsys.cpl 直接调用系统
            3. 绝对路径：C:/xxx.exe 原样使用
        """
        final_path = path
        try:
            # 判断：不是绝对路径，当成内置工具处理
            if not os.path.isabs(path):
                # 拼接基础路径 + tools文件夹
                final_path = os.path.join(BASE_PATH, "tools", path)
                # 如果文件不存在，说明是系统命令（notepad.exe / cpl面板），恢复原始path
                if not os.path.exists(final_path):
                    final_path = path

            print(f"尝试启动: {final_path}")
            # 启动程序，不阻塞主窗口
            subprocess.Popen(final_path, shell=True)
        except Exception as e:
            print(f"启动失败 [{final_path}]: {e}")


if __name__ == '__main__':
    print(RinUI.__file__)
    app = QApplication(sys.argv)
    # 窗口图标：使用全局BASE_PATH，统一路径
    icon_path = os.path.join(BASE_PATH, "assets", "Tool.ico")
    print(f"窗口图标路径：{icon_path}，存在：{os.path.exists(icon_path)}")
    app.setWindowIcon(QIcon(icon_path))

    # 创建 RinUI 窗口（不传 qml_path，先注入上下文再手动加载）
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
