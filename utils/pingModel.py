from PySide6.QtCore import QObject, Signal, QThread, Slot
import subprocess
import re

class PingWorker(QObject):
    logMsg = Signal(str)
    summaryMsg = Signal(str)  # 摘要信号，专门给简易解读
    finished = Signal()

    def __init__(self, target, count):
        super().__init__()
        self.target = target
        self.count = count
        self._stop = False
        self.recv = 0
        self.lost = 0
        self.delay_list = []

    @Slot()
    def run(self):
        self._stop = False
        cmd = ["ping", "-n", str(self.count), self.target]
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="gbk",
            errors="replace",
            startupinfo=startupinfo
        )
        # 逐行读取
        for line in iter(proc.stdout.readline, ""):
            if self._stop:
                proc.terminate()
                break
            line = line.rstrip("\n")
            if line.strip():
                self.logMsg.emit(line)
                # 解析延迟
                match_delay = re.search(r"时间=(\d+)ms", line)
                if match_delay:
                    delay = int(match_delay.group(1))
                    self.recv += 1
                    self.delay_list.append(delay)
                # 识别请求超时
                if "请求超时" in line:
                    self.lost +=1
        proc.stdout.close()
        err_data = proc.stderr.read()
        if err_data.strip():
            self.logMsg.emit(err_data)
        proc.stderr.close()

        # ========== 跑完后生成简易总结 ==========
        total = self.count
        loss_rate = (self.lost / total *100) if total>0 else 0
        if len(self.delay_list)>0:
            avg_delay = sum(self.delay_list)/len(self.delay_list)
            min_delay = min(self.delay_list)
            max_delay = max(self.delay_list)
        else:
            avg_delay = min_delay = max_delay = 0

        if loss_rate <= 0:
            status = "✅ 网络连通正常"
            tip = "网络访问稳定，无丢包。"
        elif loss_rate <30:
            status = "⚠️ 轻微丢包"
            tip = f"存在{loss_rate:.0f}%丢包，网络不太稳定。"
        else:
            status = "❌ 网络很差"
            tip = f"丢包严重{loss_rate:.0f}%，网络大概率故障。"

        summary_text = (
            f"【简易结果解读】\n"
            f"状态：{status}\n"
            f"数据包：发送{total}个，成功收到{self.recv}个，丢包 {loss_rate:.0f}%\n"
            f"延迟：最小 {min_delay}ms，最大 {max_delay}ms，平均 {avg_delay:.0f}ms\n"
            f"提示：{tip}"
        )
        self.summaryMsg.emit(summary_text)
        self.finished.emit()

    @Slot()
    def stop(self):
        self._stop = True


class PingModel(QObject):
    logMsg = Signal(str)
    summaryMsg = Signal(str)
    runFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.thread = None

    @Slot(str, int)
    def startPing(self, target: str, count: int):
        if self.thread is not None and self.thread.isRunning():
            self.logMsg.emit("任务正在运行，请等待完成！")
            return
        self._clean_thread()

        self.worker = PingWorker(target, count)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.worker.logMsg.connect(self.logMsg)
        self.worker.summaryMsg.connect(self.summaryMsg)
        self.worker.finished.connect(self._on_worker_done)
        self.thread.started.connect(self.worker.run)

        self.thread.start()

    def _on_worker_done(self):
        self._clean_thread()
        self.runFinished.emit()

    def _clean_thread(self):
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()
            try:
                self.worker.finished.disconnect()
                self.worker.logMsg.disconnect()
                self.worker.summaryMsg.disconnect()
            except Exception:
                pass
            self.worker = None
            self.thread = None

    @Slot()
    def stopPing(self):
        if self.worker:
            self.worker.stop()
            self._clean_thread()
