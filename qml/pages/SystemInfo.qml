import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

// 详细信息页面，使用SettingCard格式，读取SysInfo硬件信息
FluentPage {
    title: "详细信息"

    Column {
        Layout.fillWidth: true
        spacing: 3

        Text {
            typography: Typography.BodyStrong
            text: "系统信息"
        }
        SettingCard {
            radius: 6
            width: parent.width
            title: "系统版本"
            icon.name: "ic_fluent_system_20_regular"

            Text {
                typography: Typography.BodyStrong
                text: SysInfo.systemVersion
            }
        }
        // 系统运行时间（自动每秒刷新）
        SettingCard {
            radius: 6
            width: parent.width
            title: "系统运行时间"
            icon.name: "ic_fluent_clock_20_regular"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.uptime
            }
        }

        Text {
            typography: Typography.BodyStrong
            text: "硬件信息"
        }

        // 处理器
        SettingCard {
            radius: 6
            width: parent.width
            title: "处理器"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.cpu
            }
        }

        // 主板
        SettingCard {
            radius: 6
            width: parent.width
            title: "主板"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.motherboard
            }
        }

        // 内存
        SettingCard {
            radius: 6
            width: parent.width
            title: "内存"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.memory
            }
        }

        // 显卡
        SettingCard {
            radius: 6
            width: parent.width
            title: "显卡"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.gpu
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }

        // 显示器
        SettingCard {
            radius: 6
            width: parent.width
            title: "显示器"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.monitor
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }

        // 磁盘
        SettingCard {
            radius: 6
            width: parent.width
            title: "磁盘"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.disk
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }

        // 声卡
        SettingCard {
            radius: 6
            width: parent.width
            title: "声卡"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.soundcard
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }

        // 网卡
        SettingCard {
            radius: 6
            width: parent.width
            title: "网卡"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.networkCard
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }

        // ========== 新增网络信息分组 ==========
        Text {
            typography: Typography.BodyStrong
            text: "网络信息"
        }
        SettingCard {
            radius: 6
            width: parent.width
            title: "IP地址"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.ipInfo
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }
        SettingCard {
            radius: 6
            width: parent.width
            title: "MAC地址"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.macInfo
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }
        SettingCard {
            radius: 6
            width: parent.width
            title: "默认网关"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.gatewayInfo
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }
        SettingCard {
            radius: 6
            width: parent.width
            title: "DNS服务器"
            Text {
                typography: Typography.BodyStrong
                text: SysInfo.dnsInfo
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignRight
            }
        }
    }
}
