import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import PingModelLib 1.0

FluentPage {
    title: "网络工具"

    PingPopup {
        id: pingPopup
        pingModel: pingModel // 把model传给弹窗
        onStartPing: function (addr, count) {
            pingModel.startPing(addr, count);
        }
        onStopPing: function () {
            pingModel.stopPing();
        }
    }

    PingModel {
        id: pingModel
        // 这里不要写任何 pingPopup.xxx ！！
    }

    ScrollView {
        id: scrollView
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical: ScrollBar {}
        Flow {
            width: scrollView.width
            spacing: 20
            padding: 0
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
                        name: "检测网络连通性",
                        icon: "ic_fluent_web_asset_20_regular",
                        desc: "Ping测试，检测网络连通性"
                    }
                ]
                Rectangle {
                    id: card
                    width: 140
                    height: 140
                    radius: 12
                    color: hoverHandler.hovered ? Theme.currentTheme.colors.layerColor : Theme.currentTheme.colors.cardColor
                    border.color: Theme.currentTheme.colors.cardBorderColor
                    border.width: 1
                    scale: mouseArea.pressed ? 0.92 : 1.0
                    Behavior on scale {
                        NumberAnimation {
                            duration: 150
                            easing.type: Easing.OutQuad
                        }
                    }
                    Behavior on color {
                        ColorAnimation {
                            duration: 150
                        }
                    }
                    HoverHandler {
                        id: hoverHandler
                    }
                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        onClicked: {
                            pingPopup.open();
                            console.log("打开Ping弹窗");
                        }
                    }
                    Column {
                        anchors.centerIn: parent
                        spacing: 10
                        width: parent.width - 24
                        Icon {
                            name: modelData.icon
                            size: 40
                            color: Theme.currentTheme.colors.primaryColor
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: modelData.name
                            font.pixelSize: 14
                            font.bold: true
                            color: Theme.currentTheme.colors.textColor
                            width: parent.width
                            horizontalAlignment: Text.AlignHCenter
                            maximumLineCount: 1
                            elide: Text.ElideRight
                        }
                        Text {
                            text: modelData.desc
                            font.pixelSize: 11
                            color: Theme.currentTheme.colors.textSecondaryColor
                            width: parent.width
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.Wrap
                            maximumLineCount: 2
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }
    }
}
