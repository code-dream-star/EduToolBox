import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

// 设置页面：外观与行为、语言、关于三个分组
FluentPage {
    title: "设置"

    // ========== 外观与行为 ==========
    Column {
        Layout.fillWidth: true
        spacing: 3

        Text {
            typography: Typography.BodyStrong
            text: "外观与行为"
        }

        // 应用主题：浅色 / 深色 / 跟随系统
        SettingCard {
            radius: 6
            width: parent.width
            title: "应用主题"
            description: "选择应用要显示的主题"
            icon.name: "ic_fluent_color_20_regular"

            ComboBox {
                // data 与 model 一一对应，存放真实的主题模式值
                property var data: [Theme.mode.Light, Theme.mode.Dark, Theme.mode.Auto]
                model: ListModel {
                    ListElement {
                        text: "浅色"
                    }
                    ListElement {
                        text: "深色"
                    }
                    ListElement {
                        text: "跟随系统设定"
                    }
                }
                currentIndex: data.indexOf(Theme.getTheme())
                onCurrentIndexChanged: {
                    Theme.setTheme(data[currentIndex]);
                }
            }
        }

        // 窗口背景效果：Mica / Acrylic / Tabbed / None
        SettingCard {
            radius: 6
            width: parent.width
            title: "窗口背景效果"
            description: "修改窗口的背景外观（只支持 Windows 平台，部分效果可能仅在 Windows 11 支持）"
            icon.name: "ic_fluent_square_hint_sparkles_20_regular"

            ComboBox {
                property var data: ["mica", "acrylic", "tabbed", "none"]
                model: ListModel {
                    ListElement {
                        text: "云母（Mica）"
                    }
                    ListElement {
                        text: "亚克力（Acrylic）"
                    }
                    ListElement {
                        text: "标签页（Tabbed）"
                    }
                    ListElement {
                        text: "无"
                    }
                }
                currentIndex: data.indexOf(Theme.getBackdropEffect())
                onCurrentIndexChanged: {
                    Theme.setBackdropEffect(data[currentIndex]);
                }
            }
        }

        // 主题色：自定义应用高亮颜色
        SettingCard {
            radius: 6
            width: parent.width
            title: "主题色"
            description: "选择用于应用高亮显示的颜色"
            icon.name: "ic_fluent_paint_brush_20_regular"

            // 重置按钮：恢复默认主题色 #605ed2
            ToolButton {
                icon.name: "ic_fluent_arrow_reset_20_regular"
                ToolTip {
                    text: "重置"
                    visible: parent.hovered
                }
                onClicked: {
                    accentColorPicker.color = "#605ed2";
                }
            }

            // 下拉颜色选择器
            DropDownColorPicker {
                id: accentColorPicker
                position: Position.Left

                color: Theme.getThemeColor()
                onColorChanged: {
                    Theme.setThemeColor(color);
                }
            }
        }
    }

    // ========== 关于 ==========
    Column {

        Layout.fillWidth: true
        spacing: 3

        Text {
            typography: Typography.BodyStrong
            text: "关于"
        }

        SettingExpander {
            radius: 6
            width: parent.width
            title: "EduToolBox"
            description: "教育工具合集"
            icon.source: Qt.resolvedUrl("../../Tool.png")
            icon.size: 28

            // 版本号
            content: Text {
                color: Theme.currentTheme.colors.textSecondaryColor
                text: "v0.1.0"
            }

            // 项目仓库
            SettingItem {
                id: repo
                radius: 6
                title: "项目仓库"
                actionIcon.name: "ic_fluent_copy_20_regular"
                clickable: true

                TextInput {
                    id: repoUrl
                    font.family: "Consolas"
                    readOnly: true
                    text: "https://github.com/quiet_star_gazing/EduToolBox"
                    wrapMode: TextInput.Wrap
                    opacity: 0.8
                }

                onClicked: {
                    repoUrl.selectAll();
                    repoUrl.copy();
                }
            }

            // 提交反馈
            SettingItem {
                radius: 6
                title: "提交反馈或建议"
                clickable: true
                actionIcon.name: "ic_fluent_open_20_regular"
                onClicked: Qt.openUrlExternally("https://github.com/quiet_star_gazing/EduToolBox/issues")
            }

            // 技术栈与参考（Flow自动换行紧凑版）
            SettingItem {
                radius: 6
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    Text {
                        text: "技术栈与参考"
                    }
                    Item {
                        width: parent.width
                        height: 3
                    }
                    Flow {
                        Layout.fillWidth: true
                        spacing: 16  // ✅ 水平链接间距，比原来24缩小
                        flow: Flow.LeftToRight
                        Hyperlink {
                            text: "Qt & Qt Quick"
                            openUrl: "https://www.qt.io/"
                        }
                        Hyperlink {
                            text: "RinUI 组件库"
                            openUrl: "https://github.com/RinLit-233-shiroko/Rin-UI"
                        }
                        Hyperlink {
                            text: "Fluent Design System"
                            openUrl: "https://fluent2.microsoft.design/"
                        }
                        Hyperlink {
                            text: "Geek Uninstaller"
                            openUrl: "https://www.geekuninstaller.com/"
                        }
                        Hyperlink {
                            text: "希沃白板 5"
                            openUrl: "https://easinote.seewo.com/"
                        }
                        Hyperlink {
                            text: "TraeAI"
                            openUrl: "https://trae.ai/"
                        }
                    }
                }
            }

            // 许可证
            SettingItem {
                radius: 6
                title: "许可证"
                description: "本项目基于 MIT 许可证开源"

                Hyperlink {
                    text: "MIT License"
                    openUrl: "https://opensource.org/licenses/MIT"
                }
            }
        }
    }
}
