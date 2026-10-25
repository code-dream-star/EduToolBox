import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import PingModelLib 1.0

Window {
    id: pingWindow
    width: 720
    height: 520
    title: "Ping 网络测试"
    visible: false
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
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
                from: 1
                to: 20
                value: 4
            }
        }

        RowLayout {
            spacing: 10
            Button {
                id: btnStart
                text: "开始测试"
                onClicked: {
                    if (inputAddr.text.trim() === "") {
                        resultText.append("请填写目标地址！\n");
                        return;
                    }
                    pingModel.startPing(inputAddr.text, spinCount.value);
                    btnStart.enabled = false;
                    btnStop.enabled = true;
                }
            }
            Button {
                id: btnStop
                text: "停止"
                enabled: false
                onClicked: pingModel.stopPing()
            }
            Button {
                text: "清空日志"
                onClicked: resultText.text = ""
            }
        }

        TextArea {
            id: resultText
            Layout.fillWidth: true
            Layout.fillHeight: true
            readOnly: true
        }
    }
}
