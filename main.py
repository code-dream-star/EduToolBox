import os
import sys
import platform
import wmi
import psutil
from time import time
from PySide6.QtCore import QLocale, QObject, Signal, Slot, Property, QTimer
from PySide6.QtWidgets import QApplication
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
        :param path: 程序路径（exe / cpl / 或任何可被系统打开的文件）
                     支持简写：相对工具路径会自动加上 tools/ 前缀，
                     例如 "AppTool/geek.exe" 会被解析为 "tools/AppTool/geek.exe"
                     系统命令（如 explorer.exe、notepad.exe、mmsys.cpl）
                     和绝对路径（如 C:/...）保持不变
        """
        # final_path 用于记录最终要启动的路径，确保异常分支也能引用
        final_path = path
        try:
            # 路径解析：非绝对路径且包含目录分隔符时，自动加上 tools/ 前缀
            # 这样配置里就可以简写为 "AppTool/geek.exe"，无需每次都写 "tools/AppTool/geek.exe"
            if not os.path.isabs(path):
                # 包含目录分隔符说明是工具子目录路径（如 AppTool/geek.exe）
                # 不包含分隔符则视为系统命令（如 explorer.exe、notepad.exe、mmsys.cpl）
                if os.sep in path or '/' in path:
                    # 统一用正斜杠判断是否已带 tools/ 前缀，避免重复添加
                    normalized = path.replace('\\', '/')
                    if not normalized.startswith('tools/'):
                        final_path = os.path.join('tools', path)
            # os.startfile 会用系统默认方式打开，支持 exe、cpl、文件夹等
            os.startfile(final_path)
            print(f"启动程序: {final_path}")
        except Exception as e:
            print(f"启动失败 [{final_path}]: {e}")


if __name__ == '__main__':
    print(RinUI.__file__)
    app = QApplication(sys.argv)
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
    gallery.setIcon("Tool.ico")
    gallery.setProperty("title", f"电教工具箱")
    app.exec()
