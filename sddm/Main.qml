import QtQuick 2.15
import SddmComponents 2.0

// Ono-Sendai login: an SDDM port of Lock Screen Explorer's "Split" design, so
// login and lock look the same. The clock and date sit bottom-left over the
// wallpaper; a tinted panel on the right holds the avatar initial, a greeting,
// the user's name and the password field. The wallpaper is sharp (the lock's
// "Wallpaper blur: Sharp" setting).
//
// The greeter runs as the sddm user and can't read the desktop wallpaper or the
// Omarchy theme, so both are baked in: wallpaper.png is the theme's first
// background, and the colors are the Ono-Sendai [lock] colors.
//
// Sizes are the lock design's logical pixels times `u`, which maps the lock's
// 864-px-high logical screen (1080p at scale 1.25) onto whatever the greeter gets.
Rectangle {
  id: root
  width: 1920
  height: 1080
  color: "#0a0707"   // theme background, shown until the wallpaper loads

  readonly property real u: height / 864
  function px(v) { return Math.round(v * u) }

  readonly property color fg: "#e6d9d4"            // lock.text
  readonly property color panelBg: "#0a0707"       // lock.background
  readonly property color placeholder: "#6e5f5b"   // lock.placeholder
  readonly property color accent: "#e8261b"        // lock.border-active
  readonly property color bad: "#ff5a4c"           // lock.text-error / border-error
  function alpha(c, a) { return Qt.rgba(c.r, c.g, c.b, a) }

  // theme.conf font= is filled in by login-theme with the installing user's
  // monospace font, the family the lock screen uses; JetBrainsMono otherwise.
  readonly property string font: (typeof config !== "undefined" && config.font) ? config.font : "JetBrainsMono Nerd Font"

  property int userIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
  property string currentUser: {
    if (userModel.lastUser)
      return userModel.lastUser
    var name = userModel.data(userModel.index(userIndex, 0), Qt.UserRole + 1)
    return name ? name.toString() : ""
  }
  // As the lock greets: the first word of the full name, else the login with a capital.
  readonly property string displayName: {
    var real = userModel.data(userModel.index(userIndex, 0), Qt.UserRole + 2)
    var first = String(real || "").replace(/[<>]/g, "").trim().split(/\s+/)[0] || ""
    if (first.length > 0) return first.substring(0, 40)
    var u = currentUser
    return u.length > 0 ? u.charAt(0).toUpperCase() + u.slice(1) : u
  }

  property bool errorState: false
  property bool busy: false
  property bool revealed: false
  property int failedAttempts: 0
  property string failureMessage: ""
  property int sessionIndex: {
    for (var i = 0; i < sessionModel.rowCount(); i++) {
      var name = (sessionModel.data(sessionModel.index(i, 0), Qt.DisplayRole) || "").toString()
      if (name.indexOf("uwsm") !== -1)
        return i
    }
    return sessionModel.lastIndex
  }
  property date now: new Date()

  function greeting() {
    var h = now.getHours()
    if (h < 5) return "Good night"
    if (h < 12) return "Good morning"
    if (h < 18) return "Good afternoon"
    return "Good evening"
  }

  Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }

  Connections {
    target: sddm
    function onLoginFailed() {
      root.busy = false
      root.failedAttempts += 1
      root.errorState = true
      root.revealed = false
      root.failureMessage = "Authentication failed (" + root.failedAttempts + ")"
      password.text = ""
      password.forceActiveFocus()
      shake.restart()
    }
    function onLoginSucceeded() {
      root.errorState = false
    }
  }

  // ---- Wallpaper ------------------------------------------------------------
  Image {
    id: wallpaper
    anchors.fill: parent
    source: "wallpaper.png"
    fillMode: Image.PreserveAspectCrop
    asynchronous: true
    sourceSize.width: width
    sourceSize.height: height
  }
  Rectangle {
    anchors.fill: parent
    gradient: Gradient {
      GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.25) }
      GradientStop { position: 0.45; color: Qt.rgba(0, 0, 0, 0.05) }
      GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.45) }
    }
  }

  MouseArea { anchors.fill: parent; onClicked: password.forceActiveFocus() }

  // ---- Clock, bottom left ----------------------------------------------------
  Column {
    anchors.left: parent.left
    anchors.bottom: parent.bottom
    anchors.leftMargin: root.px(72)
    anchors.bottomMargin: root.px(64)
    spacing: root.px(4)
    Text {
      text: Qt.formatDateTime(root.now, "HH:mm")
      color: root.fg
      font.family: root.font
      font.pixelSize: root.px(96)
      font.weight: Font.DemiBold
      font.letterSpacing: -root.px(2)
    }
    Text {
      text: Qt.formatDateTime(root.now, "dddd, d MMMM")
      color: root.alpha(root.fg, 0.85)
      font.family: root.font
      font.pixelSize: root.px(24)
    }
  }

  // ---- Right panel -----------------------------------------------------------
  Item {
    id: panel
    anchors.right: parent.right
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    width: root.px(Math.max(420, Math.min(560, root.width / root.u * 0.34)))
    clip: true

    // The same wallpaper, lined up with the one behind, under the tint.
    Image {
      width: root.width; height: root.height
      x: -(root.width - panel.width)
      source: "wallpaper.png"
      fillMode: Image.PreserveAspectCrop
      asynchronous: true
      sourceSize.width: width
      sourceSize.height: height
    }
    Rectangle { anchors.fill: parent; color: root.alpha(root.panelBg, 0.55) }
    Rectangle { anchors.left: parent.left; width: 1; height: parent.height; color: root.alpha(root.fg, 0.14) }

    Column {
      anchors.left: parent.left
      anchors.right: parent.right
      anchors.verticalCenter: parent.verticalCenter
      anchors.margins: root.px(56)
      spacing: root.px(22)

      // Avatar: none set, so the initial on an accent circle.
      Rectangle {
        width: root.px(84); height: width
        radius: width / 2
        color: root.accent
        antialiasing: true
        border.width: root.px(3)
        border.color: root.alpha(root.fg, 0.25)
        Text {
          anchors.centerIn: parent
          text: root.displayName.length > 0 ? root.displayName.charAt(0).toUpperCase() : "?"
          color: root.panelBg
          font.family: root.font
          font.pixelSize: root.px(36)
          font.weight: Font.Bold
        }
      }

      Column {
        spacing: root.px(4)
        Text {
          text: root.greeting()
          color: root.alpha(root.fg, 0.7)
          font.family: root.font
          font.pixelSize: root.px(14)
          font.letterSpacing: root.px(2)
        }
        Text {
          text: root.displayName
          textFormat: Text.PlainText
          color: root.fg
          font.family: root.font
          font.pixelSize: root.px(28)
          font.weight: Font.DemiBold
        }
      }

      // ---- Password field --------------------------------------------------
      Rectangle {
        id: field
        width: parent.width
        height: root.px(58)
        radius: root.px(12)
        color: root.alpha(root.panelBg, 0.8)
        border.width: root.px(2)
        border.color: root.alpha(root.errorState ? root.bad : root.accent, 0.9)
        clip: true

        readonly property int fieldFont: root.px(16)
        readonly property int pad: root.px(2) + root.px(18)

        transform: Translate { id: shakeX; x: 0 }
        SequentialAnimation {
          id: shake
          NumberAnimation { target: shakeX; property: "x"; from: 0; to: -root.px(8); duration: 40 }
          NumberAnimation { target: shakeX; property: "x"; from: -root.px(8); to: root.px(8); duration: 70 }
          NumberAnimation { target: shakeX; property: "x"; from: root.px(8); to: -root.px(6); duration: 60 }
          NumberAnimation { target: shakeX; property: "x"; from: -root.px(6); to: root.px(4); duration: 50 }
          NumberAnimation { target: shakeX; property: "x"; from: root.px(4); to: 0; duration: 40 }
        }

        Text {
          id: lockGlyph
          anchors.left: parent.left
          anchors.leftMargin: field.pad
          anchors.verticalCenter: parent.verticalCenter
          text: root.busy ? "󰔟" : (root.errorState ? "󰍁" : "󰌾")
          color: root.errorState ? root.bad : root.placeholder
          font.family: root.font
          font.pixelSize: Math.round(field.fieldFont * 1.1)
        }

        Rectangle {
          id: capsBadge
          visible: keyboard.capsLock
          anchors.left: lockGlyph.right
          anchors.leftMargin: root.px(8)
          anchors.verticalCenter: parent.verticalCenter
          width: capsLabel.implicitWidth + root.px(10)
          height: Math.round(field.fieldFont * 1.15)
          radius: root.px(3)
          color: "transparent"
          border.width: 1
          border.color: root.accent
          Text {
            id: capsLabel
            anchors.centerIn: parent
            text: "CAPS"
            color: root.accent
            font.family: root.font
            font.pixelSize: Math.round(field.fieldFont * 0.62)
            font.letterSpacing: 1
          }
        }

        TextInput {
          id: password
          anchors.fill: parent
          anchors.leftMargin: (capsBadge.visible ? capsBadge.x + capsBadge.width : lockGlyph.x + lockGlyph.width) + root.px(12)
          anchors.rightMargin: field.pad + eye.width + root.px(8)
          verticalAlignment: TextInput.AlignVCenter
          horizontalAlignment: TextInput.AlignLeft
          echoMode: root.revealed ? TextInput.Normal : TextInput.Password
          passwordCharacter: "●"
          color: root.fg
          selectionColor: root.alpha(root.accent, 0.4)
          font.family: root.font
          font.pixelSize: text.length > 0 && !root.revealed ? root.px(20) : field.fieldFont
          font.letterSpacing: text.length > 0 && !root.revealed ? root.px(3) : 0
          clip: true
          focus: true
          enabled: !root.busy
          cursorVisible: activeFocus && text.length > 0 && !root.busy && !root.errorState
          cursorDelegate: Rectangle { width: 2; color: root.fg; visible: password.cursorVisible }
          onTextChanged: if (text.length > 0) root.errorState = false
          Keys.onPressed: function (event) {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
              if (text.length > 0) {
                root.busy = true
                sddm.login(root.currentUser, text, root.sessionIndex)
              }
              event.accepted = true
            } else if (event.key === Qt.Key_Escape) {
              text = ""
              root.errorState = false
              event.accepted = true
            }
          }
        }

        Text {
          anchors.fill: password
          visible: password.text.length === 0
          text: root.busy ? "Checking…" : (root.errorState ? root.failureMessage : "Password")
          textFormat: Text.PlainText
          color: root.busy ? root.fg : (root.errorState ? root.bad : root.placeholder)
          font.family: root.font
          font.pixelSize: field.fieldFont
          font.italic: !root.busy && root.errorState
          verticalAlignment: Text.AlignVCenter
          elide: Text.ElideRight
        }

        Item {
          id: eye
          width: Math.round(field.fieldFont * 1.6)
          height: parent.height
          anchors.right: parent.right
          anchors.rightMargin: field.pad - root.px(6)
          Text {
            anchors.centerIn: parent
            text: root.revealed ? "󰈉" : "󰈈"
            color: root.revealed ? root.accent : root.placeholder
            font.family: root.font
            font.pixelSize: Math.round(field.fieldFont * 1.1)
          }
          MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: { root.revealed = !root.revealed; password.forceActiveFocus() }
          }
        }
      }

      Text {
        text: root.failedAttempts > 0
          ? (root.failedAttempts === 1 ? "1 failed attempt" : root.failedAttempts + " failed attempts")
          : "Press Enter to log in"
        color: root.failedAttempts > 0 ? root.bad : root.alpha(root.fg, 0.55)
        font.family: root.font
        font.pixelSize: root.px(11)
        font.letterSpacing: 1
      }
    }

    Text {
      anchors.left: parent.left
      anchors.bottom: parent.bottom
      anchors.margins: root.px(56)
      text: "󰌾  " + (sddm.hostName || "")
      textFormat: Text.PlainText
      color: root.alpha(root.fg, 0.45)
      font.family: root.font
      font.pixelSize: root.px(11)
      font.letterSpacing: root.px(2)
    }
  }

  Component.onCompleted: password.forceActiveFocus()
}
