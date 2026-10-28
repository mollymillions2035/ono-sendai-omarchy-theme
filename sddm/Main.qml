import QtQuick 2.0
import SddmComponents 2.0

// Ono-Sendai login: an Ono-Sendai deck asking for your credentials. Unlike the
// boot unlock screen (logo + bare password box), this says what it is: a LOG IN
// heading, the account, a labelled password box, and a status line.
Rectangle {
  id: root
  width: 640
  height: 480
  color: "#0a0707"

  readonly property color fg: "#e6d9d4"
  readonly property color dim: "#6e5f5b"
  readonly property color red: "#e8261b"
  readonly property color bad: "#ff5a4c"
  readonly property color warn: "#e3b24f"
  readonly property string mono: "JetBrainsMono Nerd Font"

  property string currentUser: {
    if (userModel.lastUser)
      return userModel.lastUser
    var name = userModel.data(userModel.index(userModel.lastIndex >= 0 ? userModel.lastIndex : 0, 0), Qt.UserRole + 1)
    return name ? name.toString() : ""
  }
  property bool loginFailed: false
  property int sessionIndex: {
    for (var i = 0; i < sessionModel.rowCount(); i++) {
      var name = (sessionModel.data(sessionModel.index(i, 0), Qt.DisplayRole) || "").toString()
      if (name.indexOf("uwsm") !== -1)
        return i
    }
    return sessionModel.lastIndex
  }

  Connections {
    target: sddm
    function onLoginFailed() {
      root.loginFailed = true
      password.text = ""
      password.focus = true
    }
    function onLoginSucceeded() {
      root.loginFailed = false
    }
  }

  Column {
    anchors.centerIn: parent
    spacing: 0

    // logo.png is drawn at 4x (see wallpaper.py), so whatever scale the greeter's
    // monitor runs at, Qt scales it down rather than up and it stays sharp.
    Image {
      id: logo
      source: "logo.png"
      width: Math.min(sourceSize.width / 4, root.width * 0.25)
      height: sourceSize.width > 0 ? Math.round(width * sourceSize.height / sourceSize.width) : 0
      fillMode: Image.PreserveAspectFit
      smooth: true
      mipmap: true
      anchors.horizontalCenter: parent.horizontalCenter
    }

    Item { width: 1; height: 56 }

    Text {
      text: "LOG IN"
      color: root.red
      font.family: root.mono
      font.pixelSize: 22
      font.letterSpacing: 10
      anchors.horizontalCenter: parent.horizontalCenter
    }

    Item { width: 1; height: 14 }

    Row {
      anchors.horizontalCenter: parent.horizontalCenter
      Text {
        text: root.currentUser
        color: root.fg
        font.family: root.mono
        font.pixelSize: 38
      }
      Text {
        text: "@" + sddm.hostName
        visible: sddm.hostName.length > 0
        color: root.dim
        font.family: root.mono
        font.pixelSize: 38
      }
    }

    Item { width: 1; height: 28 }

    Row {
      anchors.horizontalCenter: parent.horizontalCenter
      spacing: 15

      Image {
        source: root.loginFailed ? "lock-failed.png" : "lock.png"
        width: 34
        height: 38
        fillMode: Image.PreserveAspectFit
        anchors.verticalCenter: parent.verticalCenter
      }

      Rectangle {
        width: 480
        height: 60
        color: "#160e0d"
        border.width: 2
        border.color: root.loginFailed ? root.bad : (password.text.length > 0 ? root.red : Qt.rgba(0.90, 0.85, 0.83, 0.30))

        Text {
          text: "Password"
          visible: password.text.length === 0
          color: root.dim
          font.family: root.mono
          font.pixelSize: 22
          anchors.left: parent.left
          anchors.leftMargin: 18
          anchors.verticalCenter: parent.verticalCenter
        }

        TextInput {
          id: password
          anchors.fill: parent
          anchors.leftMargin: 18
          anchors.rightMargin: 18
          verticalAlignment: TextInput.AlignVCenter
          echoMode: TextInput.Password
          passwordCharacter: "•"
          font.family: root.mono
          font.pixelSize: 24
          font.letterSpacing: 4
          color: root.fg
          selectionColor: root.red
          clip: true
          focus: true

          onTextChanged: if (text.length > 0) root.loginFailed = false

          Keys.onPressed: {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
              sddm.login(root.currentUser, password.text, root.sessionIndex)
              event.accepted = true
            }
          }
        }
      }
    }

    Item { width: 1; height: 18 }

    // Fixed-height status line so the layout doesn't jump.
    Item {
      width: 480
      height: 28
      anchors.horizontalCenter: parent.horizontalCenter
      Text {
        anchors.centerIn: parent
        font.family: root.mono
        font.pixelSize: 18
        text: root.loginFailed ? "Wrong password. Try again."
            : keyboard.capsLock ? "Caps Lock is on"
            : "Press Enter to log in"
        color: root.loginFailed ? root.bad : keyboard.capsLock ? root.warn : root.dim
      }
    }
  }

  Component.onCompleted: password.forceActiveFocus()
}
