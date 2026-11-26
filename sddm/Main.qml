import QtQuick 2.15
import SddmComponents 2.0

// Ono-Sendai login: an SDDM port of Lock Screen Explorer's "Login" design: the logo decrypts on the
// left, a terminal prompt on the right takes the password with a block cursor,
// and a wrong password knocks the logo's cells out of place until they correct.
// Colors are the Ono-Sendai theme's lock colors, baked in (the greeter can't
// read the user's Omarchy theme). The logo is ../about.txt, embedded.
Rectangle {
  id: root
  width: 1920
  height: 1080
  color: "#050404"   // background #0a0707 deepened 1.9x, as the lock design does

  readonly property color fg: "#e6d9d4"       // lock.text
  readonly property color accent: "#e8261b"   // lock.border-active
  readonly property color muted: "#64504b"
  readonly property color bad: "#ff5a4c"      // lock.text-error
  readonly property color warn: "#e3b24f"
  // theme.conf font= is filled in by login-theme with the installing user's
  // monospace font, so login matches the lock screen; JetBrainsMono otherwise.
  readonly property string mono: (typeof config !== "undefined" && config.font) ? config.font : "JetBrainsMono Nerd Font"
  readonly property int fs: Math.max(16, Math.round(height / 40))

  readonly property var logo: ["            ▄█▀█▄  ██▄  ██  ▄█▀█▄             ", "           ██   ██ ████▄██ ██   ██            ", "           ██   ██ ██ ▀███ ██   ██            ", "           ▀█▄ ▄█▀ ██   ██ ▀█▄ ▄█▀            ", "             ▀▀▀   ▀▀   ▀▀   ▀▀▀              ", "                                              ", "▄█▀▀▀█▄ ▀██▀▀██ ██▄  ██ ▀██▀█▄    ▄█▄     ▀██▀", "▀█▄  ▀▀  ██ ▄ ▀ ████▄██  ██  ██ ▄█▀ ▀█▄    ██ ", "  ▀▀█▄   ██▀█   ██ ▀███  ██  ██ ██▄▄▄██    ██ ", "██   ██  ██  ▄█ ██   ██  ██ ▄█▀ ██   ██    ██ ", " ▀▀▀▀▀  ▀▀▀▀▀▀▀ ▀▀   ▀▀ ▀▀▀▀▀   ▀▀   ▀▀   ▀▀▀▀"]
  readonly property string glyphs: "!#$%&*+-<=>?@[]^_{|}~0123456789ABCDEFabcdef▀▄█▌▐░▒▓"

  property string currentUser: {
    if (userModel.lastUser)
      return userModel.lastUser
    var name = userModel.data(userModel.index(userModel.lastIndex >= 0 ? userModel.lastIndex : 0, 0), Qt.UserRole + 1)
    return name ? name.toString() : ""
  }
  property bool errorState: false
  property bool busy: false
  property string status: ""
  property int sessionIndex: {
    for (var i = 0; i < sessionModel.rowCount(); i++) {
      var name = (sessionModel.data(sessionModel.index(i, 0), Qt.DisplayRole) || "").toString()
      if (name.indexOf("uwsm") !== -1)
        return i
    }
    return sessionModel.lastIndex
  }
  property date now: new Date()

  Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }

  Connections {
    target: sddm
    function onLoginFailed() {
      root.busy = false
      root.errorState = true
      root.status = "authentication failed"
      password.text = ""
      password.forceActiveFocus()
      art.errorCorrect()
    }
    function onLoginSucceeded() {
      root.errorState = false
      root.status = "logging in"
    }
  }

  MouseArea { anchors.fill: parent; onClicked: password.forceActiveFocus() }

  // Hidden input; the visible prompt mirrors it.
  TextInput {
    id: password
    width: 1; height: 1; opacity: 0
    echoMode: TextInput.Password
    focus: true
    enabled: !root.busy
    onTextChanged: if (text.length > 0) { root.errorState = false; root.status = "" }
    Keys.onPressed: function (event) {
      if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
        if (text.length > 0) {
          root.busy = true
          root.status = "authenticating"
          sddm.login(root.currentUser, text, root.sessionIndex)
        }
        event.accepted = true
      } else if (event.key === Qt.Key_Escape) {
        text = ""
        root.errorState = false
        root.status = ""
        event.accepted = true
      }
    }
  }

  component Line: Text {
    color: root.fg
    font.family: root.mono
    font.pixelSize: root.fs
    textFormat: Text.PlainText
  }

  Row {
    anchors.centerIn: parent
    spacing: Math.round(root.width * 0.045)

    // ---- Logo with decrypt / error-correct effects --------------------------
    Column {
      id: art
      anchors.verticalCenter: parent.verticalCenter
      spacing: -1   // block glyphs leave a hairline between rows otherwise
      readonly property int px: Math.max(8, Math.round(root.height * 0.42 / Math.max(1, root.logo.length) / 1.3))
      readonly property int cols: root.logo.length ? root.logo[0].length : 0

      // Per cell: reveal time (ms after start) and, during error-correct, a fix time.
      property var revealAt: []
      property var errorUntil: []
      property real t0: 0
      property real errT0: -1
      property var rendered: []

      function rowColor(r) {
        var k = root.logo.length > 1 ? r / (root.logo.length - 1) : 0
        return Qt.rgba(root.accent.r + (root.fg.r - root.accent.r) * k,
                       root.accent.g + (root.fg.g - root.accent.g) * k,
                       root.accent.b + (root.fg.b - root.accent.b) * k, 1)
      }
      function hex(c) {
        function h(v) { var s = Math.round(v * 255).toString(16); return s.length < 2 ? "0" + s : s }
        return "#" + h(c.r) + h(c.g) + h(c.b)
      }
      function esc(ch) { return ch === "<" ? "&lt;" : ch === ">" ? "&gt;" : ch === "&" ? "&amp;" : ch === " " ? "&nbsp;" : ch }
      function rnd() { return root.glyphs.charAt(Math.floor(Math.random() * root.glyphs.length)) }

      function start() {
        var a = [], e = []
        // Typing in at ~40 cells per frame-ish: stagger by reading order with jitter.
        var total = root.logo.length * cols
        for (var i = 0; i < total; i++) { a.push(i * 1.1 + Math.random() * 700); e.push(0) }
        revealAt = a; errorUntil = e
        t0 = Date.now(); errT0 = -1
        ticker.start()
      }
      function errorCorrect() {
        var e = errorUntil.slice(), now = Date.now() - t0
        for (var i = 0; i < e.length; i++) {
          var r = Math.floor(i / cols), c = i % cols
          if (root.logo[r].charAt(c) !== " " && Math.random() < 0.05)
            e[i] = now + 250 + Math.random() * 900
        }
        errorUntil = e
        ticker.start()
      }
      function frame() {
        var now = Date.now() - t0, busy = false, out = []
        for (var r = 0; r < root.logo.length; r++) {
          var line = root.logo[r], base = hex(rowColor(r)), s = ""
          for (var c = 0; c < line.length; c++) {
            var i = r * cols + c, ch = line.charAt(c)
            if (ch === " ") { s += "&nbsp;"; continue }
            if (now < revealAt[i]) {
              busy = true
              var pick = Math.random()
              var col = pick < 0.4 ? hex(root.muted) : pick < 0.75 ? hex(root.accent) : hex(root.fg)
              s += "<font color='" + col + "'>" + esc(rnd()) + "</font>"
            } else if (now < errorUntil[i]) {
              busy = true
              var fixing = errorUntil[i] - now < 200
              s += "<font color='" + (fixing ? hex(root.accent) : hex(root.bad)) + "'>" + esc(fixing ? ch : rnd()) + "</font>"
            } else {
              s += "<font color='" + base + "'>" + esc(ch) + "</font>"
            }
          }
          out.push(s)
        }
        rendered = out
        if (!busy) ticker.stop()
      }

      Timer { id: ticker; interval: 33; repeat: true; triggeredOnStart: true; onTriggered: art.frame() }

      Repeater {
        model: root.logo.length
        Text {
          text: art.rendered.length > index ? art.rendered[index] : ""
          textFormat: Text.StyledText
          font.family: root.mono
          font.pixelSize: art.px
          lineHeight: 1.0
        }
      }
    }

    Rectangle {
      anchors.verticalCenter: parent.verticalCenter
      width: 1
      height: art.height * 0.7
      color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
    }

    // ---- Terminal prompt ----------------------------------------------------
    Column {
      anchors.verticalCenter: parent.verticalCenter
      width: root.fs * 24
      spacing: Math.round(root.fs * 0.45)

      Line { text: "Ono-Sendai"; color: root.accent; font.weight: Font.Bold; font.pixelSize: Math.round(root.fs * 1.6) }
      Line {
        text: (root.currentUser + (sddm.hostName ? "@" + sddm.hostName : "") + " · "
               + Qt.formatDateTime(root.now, "ddd d MMM HH:mm")).toLowerCase()
        color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.5)
      }
      Item { width: 1; height: root.fs }

      Row {
        spacing: 0
        Line { text: "password "; color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.55) }
        Line { text: "❯ "; color: root.errorState ? root.bad : root.accent; font.weight: Font.Bold }
        Line {
          text: {
            var n = password.text.length
            return n > 22 ? "…" + "•".repeat(21) : "•".repeat(n)
          }
        }
        Rectangle {
          id: cursor
          anchors.verticalCenter: parent.verticalCenter
          width: Math.round(root.fs * 0.6)
          height: Math.round(root.fs * 1.15)
          color: root.fg
          visible: !root.busy
          SequentialAnimation on opacity {
            loops: Animation.Infinite
            running: cursor.visible
            NumberAnimation { from: 1; to: 1; duration: 530 }
            NumberAnimation { from: 1; to: 0; duration: 1 }
            NumberAnimation { from: 0; to: 0; duration: 530 }
            NumberAnimation { from: 0; to: 1; duration: 1 }
          }
        }
      }

      Line {
        text: root.status.length > 0 ? (root.errorState ? "✗ " : "… ") + root.status
            : keyboard.capsLock ? "! caps lock is on" : " "
        color: root.errorState ? root.bad
             : (root.status.length === 0 && keyboard.capsLock) ? root.warn
             : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.6)
      }

      Line {
        text: "enter logs in · esc clears"
        color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.3)
        font.pixelSize: Math.round(root.fs * 0.8)
      }
    }
  }

  Component.onCompleted: {
    password.forceActiveFocus()
    art.start()
  }
}
