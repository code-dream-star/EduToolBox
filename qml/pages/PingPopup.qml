import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

Popup {
    id: root
    width: 720
    height: 520
    modal: true
    visible: false
    x: 40
    y: 40
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    signal startPing(string addr, int count)
    signal stopPing

    property PingModel pingModel: null // 接收外部传进来的model

    property string targetAddr: ""
    property int pingCount: 4

    background: Rectangle {
        // 兜底，防止Theme加载时机问题报错
        color: (Theme.currentTheme && Theme.currentTheme.windowBackground) ? Theme.currentTheme.windowBackground : "#ffffff"
        radius: 12
        border.color: (Theme.currentTheme && Theme.currentTheme.colors) ? Theme.currentTheme.colors.cardBorderColor : "#cccccc"
        border.width: 1
    }

    contentItem: ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 0
        // 标题栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            color: "transparent"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 12
                Layout.fillWidth: true
                Text {
                    text: "Ping 网络测试"
                    font.pixelSize: 15
                    font.bold: true
                    verticalAlignment: Qt.AlignVCenter
                }
                Item {
                    Layout.fillWidth: true
                }
                Button {
                    text: "×"
                    width: 32
                    height: 32
                    onClicked: root.close()
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 16
            spacing: 12

            RowLayout {
                spacing: 8
                TextField {
                    id: inputAddr
                    Layout.fillWidth: true
                    placeholderText: "请输入IP或域名，例如：8.8.8.8 / baidu.com"
                }
                SpinBox {
                    id: spinCount
                    width: 60
                    from: 1
                    to: 20
                    value: 4
                }
                Text {
                    text: "次"
                    font.pixelSize: 14
                }
            }

            RowLayout {
                spacing: 10
                Button {
                    id: btnStart
                    text: "开始测试"
                    onClicked: {
                        root.startPing(inputAddr.text, spinCount.value);
                        btnStart.enabled = false;
                        btnStop.enabled = true;
                    }
                }
                Button {
                    id: btnStop
                    text: "停止"
                    enabled: false
                    onClicked: root.stopPing()
                }
                Button {
                    text: "清空日志"
                    onClicked: {
                        summaryText.text = "";
                        resultText.text = "";
                    }
                }
            }

            TextArea {
                id: summaryText
                Layout.fillWidth: true
                Layout.preferredHeight: 130
                readOnly: true
                font.bold: true
                wrapMode: Text.Wrap
            }
            ScrollView {
                id: logScrollView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                TextArea {
                    id: resultText
                    anchors.fill: parent
                    readOnly: true
                    wrapMode: Text.Wrap
                    onTextChanged: {
                        Qt.callLater(function () {
                            resultText.flickable.contentY = resultText.flickable.contentHeight - resultText.flickable.height;
                        });
                    }
                }
            }
        }
    }

    // ========== 关键：弹窗内部监听model信号，自己更新UI ==========
    Connections {
        target: pingModel
        onLogMsg: function (msg) {
            resultText.text += msg + "\n";
        }
        onSummaryMsg: function (msg) {
            summaryText.text = msg;
        }
        onRunFinished: function () {
            btnStart.enabled = true;
            btnStop.enabled = false;
        }
    }
}
