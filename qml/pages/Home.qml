import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import QtQuick.Window 2.15
import Qt5Compat.GraphicalEffects  // 图形库（用于 OpacityMask / ShaderEffectSource）
import RinUI

// 首页：图片横幅 + 三张链接卡片
FluentPage {
    id: root
    horizontalPadding: 0          // 左右内边距为 0，让横幅铺满
    wrapperWidth: width - 42 * 2  // 内容最大宽度
    spacing: 18
    // ========== 顶部图片横幅 ==========
    contentHeader: Item {
        width: parent.width
        height: 400
        // 背景图片（原始图片，作为 ShaderEffectSource 的源）
        Image {
            id: bannerSource
            anchors.fill: parent
            source: "../../assets/bg.png"
            fillMode: Image.PreserveAspectCrop   // 保持比例裁剪填满
            verticalAlignment: Image.AlignTop
        }
        // 将背景图转为纹理，供 OpacityMask 实现渐变淡出
        ShaderEffectSource {
            id: bannerTexture
            sourceItem: bannerSource
            hideSource: true          // 隐藏原始 Image，只显示遮罩后的结果
            live: true
            visible: false
            smooth: true
            textureSize: Qt.size(Math.max(1, Math.ceil(bannerSource.width * Screen.devicePixelRatio)), Math.max(1, Math.ceil(bannerSource.height * Screen.devicePixelRatio)))
        }
        // 渐变遮罩：上实下虚，让横幅底部平滑过渡到页面背景
        Item {
            id: bannerBackdrop   // 供 AcrylicBrush 引用
            anchors.fill: parent
            OpacityMask {
                id: bannerContent
                anchors.fill: parent
                source: bannerTexture
                maskSource: Rectangle {
                    width: bannerContent.width
                    height: bannerContent.height
                    gradient: Gradient {
                        GradientStop {
                            position: 0.5
                            color: "white"
                        }     // 上方不透明
                        GradientStop {
                            position: 0.97
                            color: "transparent"
                        } // 下方透明淡出
                    }
                }
            }
        }
        // 左上角内容：Tool.png 图标 + 标题列
        Row {
            anchors {
                top: parent.top
                left: parent.left
                leftMargin: 56
                topMargin: 40  // ✅ 改动这里！从18改成40，标题整体往下移动
            }
            spacing: 20
            // Tool.png 图标
            Image {
                source: "../../assets/Tool.png"
                width: 80
                height: 80
                fillMode: Image.PreserveAspectFit
                anchors.verticalCenter: parent.verticalCenter
            }
            // 标题与副标题（上下排列）
            Column {
                anchors.verticalCenter: parent.verticalCenter
                // 副标题
                Text {
                    color: "#fff"
                    font.pixelSize: 18
                    font.weight: 600
                    text: qsTr("这是首页内容")
                }
                // 主标题
                Text {
                    color: "#fff"
                    typography: Typography.TitleLarge
                    text: qsTr("欢迎使用 电教工具箱")
                }
            }
        }
    }
    // ========== 三张链接卡片（向上重叠到横幅底部） ==========
    Flow {
        Layout.fillWidth: true
        Layout.topMargin: -140
        spacing: 12
        Repeater {
            model: [
                {
                    title: "快速上手",
                    desc: "浏览工具分类，一键启动所需程序。",
                    icon: "ic_fluent_play_circle_20_regular",
                    url: ""
                },
                {
                    title: "开发文档",
                    desc: "了解 RinUI 组件与 Qt Quick 开发。",
                    icon: "ic_fluent_document_20_regular",
                    url: "https://github.com/quiet_star_gazing/EduToolBox"
                },
                {
                    title: "项目仓库",
                    desc: "查看源码、提交反馈或贡献代码。",
                    icon: "ic_fluent_code_block_20_regular",
                    url: "https://github.com/quiet_star_gazing/EduToolBox"
                }
            ]
            // 链接卡片
            Rectangle {
                width: (parent.width - 24) / 3   // 一行 3 张，减去 2 个间距
                height: 150
                radius: 8
                color: hoverHandler.hovered ? Theme.currentTheme.colors.layerColor : Theme.currentTheme.colors.cardColor
                border.color: Theme.currentTheme.colors.cardBorderColor
                border.width: 1
                Behavior on color {
                    ColorAnimation {
                        duration: 150
                    }
                }
                HoverHandler {
                    id: hoverHandler
                }
                TapHandler {
                    onTapped: if (modelData.url !== "")
                        Qt.openUrlExternally(modelData.url)
                }
                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10
                    // 图标
                    Icon {
                        name: modelData.icon
                        size: 32
                        color: Theme.currentTheme.colors.primaryColor
                    }
                    // 标题
                    Text {
                        text: modelData.title
                        font.pixelSize: 16
                        font.bold: true
                        color: Theme.currentTheme.colors.textColor
                    }
                    // 描述
                    Text {
                        text: modelData.desc
                        font.pixelSize: 13
                        color: Theme.currentTheme.colors.textSecondaryColor
                        width: parent.width
                        wrapMode: Text.Wrap
                    }
                }
                // 右下角外链箭头
                Icon {
                    visible: modelData.url !== ""
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.margins: 16
                    name: "ic_fluent_arrow_up_right_20_regular"
                    size: 16
                    color: Theme.currentTheme.colors.textSecondaryColor
                }
            }
        }
    }
}
