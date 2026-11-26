# Ono-Sendai login screen (SDDM)

A terminal login, ported from Lock Screen Explorer's "Login" lock design so
login and lock look the same: the ONO-SENDAI wordmark (`../about.txt`, embedded
in `Main.qml`) decrypts in on the left, red fading to off-white; on the right,
an Omarchy heading, `user@host` with the date, and a `password ❯` prompt with a
blinking block cursor. A wrong password knocks a few of the wordmark's cells out
of place in bright red until they correct; the status line also shows Caps Lock
in yellow. Enter logs in, Esc clears.


The font is your monospace font, the one the lock screen uses: `theme.conf`
ships an empty `font=`, and `login-theme` fills in `fc-match monospace` when it
installs. Change fonts later? Run `login-theme ono-sendai` again.

```
login-theme ono-sendai   # install/refresh and make it the active login
login-theme              # show the active one and what's available
login-theme --default
login-theme --remove ono-sendai
```

`login-theme` is bundled in this folder. Install it once with
`install -Dm 755 login-theme ~/.local/bin/login-theme`, or run `./login-theme` in place. It works for any
Omarchy theme with an `sddm/` folder, needs sudo, and only writes
`/usr/share/sddm/themes/<name>/` (folders it marks as its own) and
`/etc/sddm.conf.d/99-z-login-theme.conf`. Omarchy's own login theme is never
touched; `--default` goes back to it.

`preview.png` is an offscreen render of `Main.qml` by `preview.qml` (stubbed
SDDM objects, 2400x1350 at scale 1.6). Re-render after changing `Main.qml`:
`QT_QPA_PLATFORM=offscreen qml6 preview.qml -- "$USER" "$(hostname)"`.

Test without installing: `sddm-greeter-qt6 --test-mode --theme ~/.config/omarchy/themes/ono-sendai/sddm`

`python3 ../wallpaper.py unlock` re-renders `unlock.png` and the 4x `logo.png`.
