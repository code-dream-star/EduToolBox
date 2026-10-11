import QtQuick 2.15
import QtQuick.Controls 2.15
import RinUI

// 主窗口：FluentWindow + 侧边栏导航
FluentWindow {
    id: window
    visible: true
    width: 900
    height: 600
    icon: "Tool.ico"
    // 始终启用 DWM 框架扩展，避免系统标题栏与自定义按钮重影
    property bool backdropEnabled: false
    // ========== 侧边栏配置 ==========
    navigationView.navExpandWidth: 180   // 展开宽度
    // search field
    // titleBarArea: AutoSuggestBox {
    //     id: searchField
    //     width: 325
    //     anchors.centerIn: parent
    //     placeholderText: qsTr("Search controls and samples...")
    //     model: ItemData.allControls
    //     textRole: "title"

    //     onAccepted: {
    //         var selected = ItemData.allControls.find(c => c.title === searchField.text);
    //         if (selected && selected.page) {
    //             navigationView.push(selected.page);
    //         } else {
    //             // 没找到，跳到搜索页面
    //             console.log("Search for: " + searchField.text);
    //             navigationView.push(Qt.resolvedUrl("pages/Search.qml"), {
    //                 query: searchField.text || ""
    //             });
    //         }
    //     }
    // }
    // 侧边栏菜单
    navigationItems: [
        {
            title: "首页",
            page: Qt.resolvedUrl("pages/Home.qml"),
            icon: "ic_fluent_home_20_regular",
            position: Position.Top
        },
        {
            title: "系统信息",
            page: Qt.resolvedUrl("pages/SystemInfo.qml"),
            icon: "ic_fluent_info_20_regular",
            position: Position.Top
        },
        {
            title: "软件工具",
            page: Qt.resolvedUrl("pages/AppTool.qml"),
            icon: "ic_fluent_apps_settings_20_regular"
        },
        {
            title: "系统工具",
            page: Qt.resolvedUrl("pages/SysTool.qml"),
            icon: "ic_fluent_desktop_toolbox_20_regular"
        },
        {
            title: "网络工具",
            page: Qt.resolvedUrl("pages/NetTool.qml"),
            icon: "ic_fluent_globe_desktop_20_regular"
        },
        {
            title: "高级工具",
            page: Qt.resolvedUrl("pages/AdvancedTools.qml"),
            icon: "ic_fluent_warning_20_regular",
            position: Position.Bottom
        },
        {
            title: "设置",
            page: Qt.resolvedUrl("pages/Settings.qml"),
            icon: "ic_fluent_settings_20_regular",
            position: Position.Bottom
        }
    ]
}
