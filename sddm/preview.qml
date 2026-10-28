import QtQuick
import QtQuick.Window

// Renders Main.qml offscreen to preview.png (3840x2160) with stand-ins for the
// objects SDDM provides. The account shown comes from the command line:
//   QT_QPA_PLATFORM=offscreen qml6 preview.qml -- "$USER" "$(hostname)"
// Main.qml is loaded through a Loader, whose context it inherits: the ids
// below are what it sees as userModel, sessionModel, sddm and keyboard.
Window {
  width: 2400
  height: 1350
  visible: true

  readonly property var args: {
    var a = Qt.application.arguments
    var i = a.indexOf("--")
    return i >= 0 ? a.slice(i + 1) : []
  }

  QtObject {
    id: userModel
    property string lastUser: args[0] || "user"
    property int lastIndex: 0
    function index(row, col) { return row }
    function data(index, role) { return lastUser }
  }

  QtObject {
    id: sessionModel
    property int lastIndex: 0
    function rowCount() { return 1 }
    function index(row, col) { return row }
    function data(index, role) { return "Hyprland (uwsm-managed)" }
  }

  QtObject {
    id: sddm
    property string hostName: args[1] || "host"
    signal loginFailed()
    signal loginSucceeded()
    function login(user, password, session) {}
  }

  QtObject {
    id: keyboard
    property bool capsLock: false
  }

  Loader {
    id: greeter
    anchors.fill: parent
    source: "Main.qml"
  }

  Timer {
    interval: 500
    running: greeter.status === Loader.Ready
    onTriggered: greeter.item.grabToImage(function (result) {
      result.saveToFile(Qt.resolvedUrl("preview.png").toString().replace("file://", ""))
      Qt.quit()
    }, Qt.size(3840, 2160))
  }
}
