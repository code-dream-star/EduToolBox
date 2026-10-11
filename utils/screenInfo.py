# screenInfo.py
import wmi
import math

def get_monitor_info() -> str:
    """
    读取显示器信息：型号 + 物理尺寸 + 分辨率
    纯WMI，无额外依赖
    返回：多行字符串，多个显示器一行一个
    """
    monitor_list = []
    try:
        wmi_wmi = wmi.WMI(namespace="root\\wmi")
        wmi_cim = wmi.WMI()
        # 拿到显卡分辨率信息（一个或多个显卡）
        gpu_res_dict = {}
        for gpu in wmi_cim.Win32_VideoController():
            if gpu.CurrentHorizontalResolution and gpu.CurrentVerticalResolution:
                res_str = f"{gpu.CurrentHorizontalResolution}×{gpu.CurrentVerticalResolution}"
                gpu_res_dict[gpu.DeviceID] = res_str

        # 遍历显示器
        for mon in wmi_wmi.WmiMonitorID():
            # 读取显示器型号名称
            manu_bytes = [chr(c) for c in mon.ManufacturerName if c != 0]
            manu_name = "".join(manu_bytes).strip()
            name_bytes = [chr(c) for c in mon.UserFriendlyName if c != 0]
            model_name = "".join(name_bytes).strip()
            full_name = f"{manu_name} {model_name}".strip()

            # 读取物理尺寸（厘米）
            size_cm_w = 0
            size_cm_h = 0
            try:
                # 找到对应显示器的BasicDisplayParams
                for basic in wmi_wmi.WmiMonitorBasicDisplayParams():
                    if basic.InstanceName == mon.InstanceName:
                        size_cm_w = basic.MaxHorizontalImageSize
                        size_cm_h = basic.MaxVerticalImageSize
                        break
            except Exception:
                pass

            # 厘米转英寸，计算对角线
            inch_str = "未知尺寸"
            if size_cm_w > 0 and size_cm_h > 0:
                diagonal_cm = math.sqrt(size_cm_w**2 + size_cm_h**2)
                diagonal_inch = round(diagonal_cm / 2.54, 1)
                inch_str = f"{diagonal_inch}英寸"

            # 分辨率（简单取第一个显卡分辨率，多显示器可后续优化）
            res_str = ""
            if gpu_res_dict:
                res_str = list(gpu_res_dict.values())[0]

            # 拼接单行
            line_parts = []
            if full_name:
                line_parts.append(full_name)
            line_parts.append(inch_str)
            if res_str:
                line_parts.append(res_str)
            line = " | ".join(line_parts)
            monitor_list.append(line)

        if monitor_list:
            return "\n".join(monitor_list)
    except Exception as e:
        print("WmiMonitorID读取失败", e)

    # 兜底旧接口 Win32_DesktopMonitor
    try:
        c = wmi.WMI()
        fallback_list = []
        for m in c.Win32_DesktopMonitor():
            name = m.Name.strip() if m.Name else "未知显示器"
            w_px = m.ScreenWidth
            h_px = m.ScreenHeight
            res_text = f"{w_px}×{h_px}" if w_px and h_px else "未知分辨率"
            fallback_list.append(f"{name} | {res_text}")
        if fallback_list:
            return "\n".join(fallback_list)
    except Exception as e:
        print("Win32_DesktopMonitor读取失败", e)

    # 全部读取失败
    return "未知"


# 单独运行测试这个文件
if __name__ == "__main__":
    print(get_monitor_info())
