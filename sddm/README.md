# Ono-Sendai login screen (SDDM)

An Ono-Sendai deck asking for your credentials. Same layout as the arasaka,
militech, neuromancer and hosaka logins, so the password login doesn't look like
the boot disk-unlock screen: the ONO-SENDAI wordmark (`logo.png`, `../unlock.png`
drawn at 4x and shown at a quarter of that, so it stays sharp whatever scale the
greeter's monitor runs at), a red LOG IN
heading, `user@host`, a labelled password box (red while typing), and a status
line (Enter hint, Caps Lock in yellow, wrong password in bright red).

```
login-theme ono-sendai   # install/refresh and make it the active login
login-theme              # show the active one and what's available
login-theme --default
login-theme --remove ono-sendai
```

`login-theme` is bundled in this folder (the same file ships with the other
logins). Install it once with `install -Dm 755 login-theme
~/.local/bin/login-theme`, or run `./login-theme` in place. It works for any
Omarchy theme with an `sddm/` folder, needs sudo, and only writes
`/usr/share/sddm/themes/<name>/` (folders it marks as its own) and
`/etc/sddm.conf.d/99-z-login-theme.conf`. Omarchy's own login theme is never
touched; `--default` goes back to it.

`preview.png` is an offscreen render of `Main.qml` by `preview.qml` (stubbed
SDDM objects, 2400x1350 at scale 1.6). Re-render after changing `Main.qml`:
`QT_QPA_PLATFORM=offscreen qml6 preview.qml -- "$USER" "$(hostname)"`.

Test without installing: `sddm-greeter-qt6 --test-mode --theme ~/.config/omarchy/themes/ono-sendai/sddm`

`python3 ../wallpaper.py unlock` re-renders `unlock.png` and the 4x `logo.png`.
