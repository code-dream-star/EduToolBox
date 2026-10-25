import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

// 软件工具页面

FluentPage {
    title: "系统工具"

    // 可滚动容器：卡片超出页面时可纵向滚动

    ScrollView {
        id: scrollView                    // 用于绑定子项宽度，保证 Flow 按视口宽度排列
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true                        // 裁剪超出区域
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff  // 隐藏横向滚动条（Flow 自动换行，不需要横向滚动）
        // Flow 布局：根据宽度自动计算每行卡片数量，装不下自动换行
        Flow {
            width: scrollView.width // 关键：绑定 ScrollView 宽度，才能按实际可用宽度排列
            spacing: 20             // 卡片之间的间距（横向和纵向）
            padding: 0              // 四周内边距
            layoutDirection: Qt.LeftToRight  // 从左到右排列
            // 数据模型：每个元素对应一个工具卡片
            // name    = 卡片主标题
            // icon    = RinUI 字体图标名称（见 FluentSystemIcons-Index.js）
            // desc    = 卡片副标题/描述
            // Path = 点击卡片时启动的程序路径
            InfoBar {
                id: infoBar
                width: parent.width
                severity: Severity.Warning
                text: qsTr("运行部分系统工具时可能出现短暂卡顿，属于正常现象。")
                visible: true
            }
            Repeater {
                model: [
                    {
                        name: "系统文件校验修复",
                        icon: "ic_fluent_wrench_20_regular",
                        desc: "用于检测、修复被丢失、损坏的系统文件",
                        Path: "tools/SysTool/sfc.bat"
                    },
                    {
                        name: "清空图标缓存",
                        icon: "ic_fluent_icons_20_regular",
                        desc: "图标显示为空白，开始菜单图标异常",
                        Path: "tools/SysTool/IconCache.bat"
                    },
                    {
                        name: "清理系统缓存",
                        icon: "ic_fluent_delete_lines_20_regular",
                        desc: "清理系统临时文件和缓存数据",
                        Path: "tools/SysTool/CleanTemp.bat"
                    },
                ]

                // 单个工具卡片
                Rectangle {
                    id: card
                    width: 140                      // 卡片宽度
                    height: 140                     // 卡片高度
                    radius: 12                      // 圆角大小
                    // 背景色：悬停时变亮，否则用主题卡片色
                    color: hoverHandler.hovered ? Theme.currentTheme.colors.layerColor : Theme.currentTheme.colors.cardColor
                    border.color: Theme.currentTheme.colors.cardBorderColor  // 边框颜色（跟随主题）
                    border.width: 1                 // 边框粗细
                    // 缩放动画：按下时缩小到 0.92，松开时弹回 1.0
                    scale: tapHandler.pressed ? 0.92 : 1.0
                    // 缩放使用弹性动画，营造按压回弹手感
                    Behavior on scale {
                        NumberAnimation {
                            duration: 150
                            easing.type: Easing.OutQuad  // 减速曲线，松手时回弹更自然
                        }
                    }
                    // 颜色变化时的过渡动画（150ms）
                    Behavior on color {
                        ColorAnimation {
                            duration: 150
                        }
                    }
                    // 鼠标悬停检测
                    HoverHandler {
                        id: hoverHandler
                    }
                    // 点击卡片：调用 Python 端的 AppLauncher 启动对应程序
                    TapHandler {
                        id: tapHandler
                        onTapped: {
                            console.log("准备启动工具，传入路径:", modelData.Path);
                            AppLauncher.launch(modelData.Path, true);
                        }
                    }
                    // 卡片内容：图标在上、文字在下
                    Column {
                        anchors.centerIn: parent    // 整体在卡片中居中
                        spacing: 10                 // 图标与文字之间的垂直间距
                        width: parent.width - 16    // 内容宽度 = 卡片宽度 - 左右留白
                        // 工具图标
                        Icon {
                            name: modelData.icon    // 图标名称来自数据模型
                            size: 40                // 图标尺寸
                            color: Theme.currentTheme.colors.primaryColor  // 图标颜色 = 主题主色
                            anchors.horizontalCenter: parent.horizontalCenter  // 水平居中
                        }
                        // 工具名称（主标题）
                        Text {
                            text: modelData.name
                            font.pixelSize: 14
                            font.bold: true
                            color: Theme.currentTheme.colors.textColor
                            anchors.horizontalCenter: parent.horizontalCenter
                            horizontalAlignment: Text.AlignHCenter  // 文字内部水平居中
                            maximumLineCount: 1      // 只显示一行
                            elide: Text.ElideRight   // 文字过长时末尾显示省略号
                        }
                        // 工具描述（副标题）
                        Text {
                            text: modelData.desc
                            font.pixelSize: 11
                            color: Theme.currentTheme.colors.textSecondaryColor
                            anchors.horizontalCenter: parent.horizontalCenter
                            horizontalAlignment: Text.AlignHCenter
                            width: parent.width        // 限制文本宽度，自动换行生效
                            wrapMode: Text.Wrap        // 允许换行
                            maximumLineCount: 2        // 最多显示两行
                            elide: Text.ElideRight     // 超过两行时末尾省略
                        }
                    }
                }
            }
        }
    }
}
