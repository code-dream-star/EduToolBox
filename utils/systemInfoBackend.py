import platform
from time import time

import psutil
import wmi
from PySide6.QtCore import QObject, Signal, Property, QTimer

from utils.screenInfo import get_monitor_info


class SystemInfoBackend(QObject):
    uptimeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.w = None
        try:
            self.w = wmi.WMI()
        except Exception as e:
            print("WMI初始化失败:", e)

        self._monitor = get_monitor_info()
        self._cpu = "未知"
        self._motherboard = "未知"
        self._memory = "未知"
        self._gpu = "未知"
        self._disk = "未知"
        self._soundcard = "未知"
        self._network_card = "未知"
        self._systemVersion = platform.platform()

        self._ip_info = "未知"
        self._mac_info = "未知"
        self._gateway_info = "未知"
        self._dns_info = "未知"

        # 处理器
        try:
            cpus = self.w.Win32_Processor()
            if cpus:
                self._cpu = cpus[0].Name.strip()
        except Exception:
            pass

        # 主板
        try:
            boards = self.w.Win32_BaseBoard()
            if boards:
                self._motherboard = f"{boards[0].Manufacturer} {boards[0].Product}".strip()
        except Exception:
            pass

        # 内存
        try:
            total_mem = psutil.virtual_memory().total
            total_gb = round(total_mem / (1024 ** 3), 2)
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

        # 显卡
        try:
            gpus = self.w.Win32_VideoController()
            gpu_list = [gpu.Name.strip() for gpu in gpus if gpu.Name]
            self._gpu = "\n".join(gpu_list)
        except Exception:
            pass

        # 磁盘
        try:
            disks = self.w.Win32_DiskDrive()
            disk_list = []
            for d in disks:
                if d.Size:
                    size_gb = round(int(d.Size) / (1024 ** 3), 2)
                    disk_list.append(f"{d.Model.strip()} ({size_gb} GB)")
            if disk_list:
                self._disk = "\n".join(disk_list)
        except Exception:
            pass

        # 声卡
        try:
            sounds = self.w.Win32_SoundDevice()
            sound_list = [s.Name.strip() for s in sounds if s.Name]
            if sound_list:
                self._soundcard = "\n".join(sound_list)
        except Exception:
            pass

        # 网卡、IP、MAC、网关、DNS
        try:
            nics = self.w.Win32_NetworkAdapterConfiguration()
            nic_name_list = []
            ip_list = []
            mac_list = []
            gateway_list = []
            dns_list = []
            for nic in nics:
                if nic.MACAddress and nic.Caption and nic.IPEnabled:
                    name = nic.Caption.strip()
                    mac = nic.MACAddress
                    ip = ", ".join(nic.IPAddress) if nic.IPAddress else "-"
                    gw = ", ".join(nic.DefaultIPGateway) if nic.DefaultIPGateway else "-"
                    dns = ", ".join(nic.DNSServerSearchOrder) if nic.DNSServerSearchOrder else "-"

                    nic_name_list.append(name)
                    ip_list.append(ip)
                    mac_list.append(mac)
                    gateway_list.append(gw)
                    dns_list.append(dns)

            if nic_name_list:
                self._network_card = "\n".join(nic_name_list)
                self._ip_info = "\n".join(ip_list)
                self._mac_info = "\n".join(mac_list)
                self._gateway_info = "\n".join(gateway_list)
                self._dns_info = "\n".join(dns_list)
        except Exception as e:
            print("读取网卡IP信息失败", e)
            pass

        # 运行时间定时器
        self._uptime = self._get_uptime_text()
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
            parts.append(f"{hours}小时{mins}分{mins}分{secs}秒")
            return " ".join(parts)
        except Exception as e:
            print("读取运行时间失败", e)
            return "未知"

    def _update_uptime(self):
        new_val = self._get_uptime_text()
        if new_val != self._uptime:
            self._uptime = new_val
            self.uptimeChanged.emit()

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

    @Property(str, notify=uptimeChanged)
    def uptime(self):
        return self._uptime

    @Property(str, constant=True)
    def ipInfo(self):
        return self._ip_info

    @Property(str, constant=True)
    def macInfo(self):
        return self._mac_info

    @Property(str, constant=True)
    def gatewayInfo(self):
        return self._gateway_info

    @Property(str, constant=True)
    def dnsInfo(self):
        return self._dns_info
