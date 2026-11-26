# Ono-Sendai login screen (SDDM)

A port of Lock Screen Explorer's "Split" lock design, so login and lock look
the same: the clock and date sit bottom-left over the wallpaper, and a tinted
panel on the right holds the user's initial on a red circle, a time-of-day
greeting, the user's name, the password field (lock glyph, Caps Lock badge,
show-password eye) and the hostname. A wrong password shakes the field, turns
its outline red and counts the failed attempts. Enter logs in, Esc clears.
The wallpaper is sharp, as with the lock's "Wallpaper blur: Sharp" setting.

The greeter runs as the `sddm` user and can't read your desktop wallpaper or
Omarchy theme, so both are baked in: `wallpaper.png` links to
`../backgrounds/1-ono-sendai.png` (copied on install), and the colors are the
`[lock]` colors from `../shell.lock.toml`. Sizes follow the lock's logical
pixels at a 1080p, 1.25-scale screen and scale with the greeter's resolution.

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
SDDM objects, 2400x1350 at scale 1.6). Re-render after changing `Main.qml`
(copy `wallpaper.png` with `cp -L` if rendering elsewhere):
`QT_QPA_PLATFORM=offscreen qml6 preview.qml -- "$USER" "$(hostname)" "$(fc-match -f '%{family[0]}' monospace)"`.

Test without installing: `sddm-greeter-qt6 --test-mode --theme ~/.config/omarchy/themes/ono-sendai/sddm`
