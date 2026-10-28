# Ono-Sendai

An Omarchy theme for Ono-Sendai, the deck maker of William Gibson's Sprawl:
Case's Ono-Sendai Cyberspace 7 in *Neuromancer*. The ONO-SENDAI wordmark is the
one on the deck in preview footage of the Neuromancer series, redrawn here as
vectors. Nothing is cut or traced from the footage.

It's an Ono-Sendai desktop, not a desktop decorated to look like Ono-Sendai.
Everything on it is something the deck would really show: no HUDs, no drawn
device fronts, buttons or indicator lights, no out-of-universe logos.

| Token | Colour | Role |
|---|---|---|
| `background` | `#0a0707` | deck black, faintly warm |
| `foreground` | `#e6d9d4` | warm off-white, so long reading isn't red on black |
| `accent`, `red` | `#e8261b` | Ono-Sendai red: borders, selection, focus, the mark |
| `bright_red` | `#ff5a4c` | errors and wrong passwords |
| `selection` | `#3b1411` | red-black |
| `muted` | `#64504b` | warm grey: dim text, bright black in terminals |

The other ANSI colours are muted so nothing competes with the red.

Same structure as the arasaka, militech, netwatch, neuromancer and hosaka
themes: `colors.toml`, `hyprland.lua` (red border fading into black, blur,
translucency), `shell.*.toml` overrides (bar, launcher, menu, lock, polkit,
notifications, popups, tooltip), `icons.theme` (Yaru-red-dark).

## The mark

The wordmark is drawn as lettering in `wallpaper.py` (heavy capitals, stems 24%
of the cap height), not set in a font, and rendered flat: Ono-Sendai red with
hard edges, the way the company's own artwork would be. The glow in the footage
is the camera's, so it isn't reproduced. The red traces and bars around the
wordmark in the footage are the deck's exterior art, so they stay on the deck.

## Backgrounds

Two 3840x2160 wallpapers, the wordmark alone at the same size as on the boot and
login screens:

1. `1-ono-sendai.png` (the default): Ono-Sendai red on deck black.
2. `2-ono-sendai-red.png`: the same mark reversed, deck black on a field of
   Ono-Sendai red.

Rendered by `wallpaper.py` (numpy, Pillow, rsvg-convert, ImageMagick);
regenerate with `python3 wallpaper.py` (or one: `python3 wallpaper.py
2-ono-sendai-red`), then `omarchy theme set ono-sendai`. Switch between them
with `omarchy theme bg next`.

## Boot splash and login (Plymouth + SDDM)

`unlock.png` is the wordmark on transparency; `preview-unlock.png` mocks the
disk-unlock screen with Omarchy's own Plymouth assets. `sddm/` is a separate
SDDM login theme named `ono-sendai` (the wordmark, a red LOG IN heading,
`user@host`, password box, status line), installed by `sddm/login-theme`
(included); see `sddm/README.md`.

Neither is installed automatically (both need sudo):

```
omarchy-plymouth-set-by-theme ono-sendai
install -Dm 755 sddm/login-theme ~/.local/bin/login-theme   # once
login-theme ono-sendai
```

## Screensaver

`screensaver.txt` is the wordmark in half-block characters, 86x5 and
letterspaced so no letters merge, for Omarchy's ttfx screensaver. It's sized for a 1920x1080 laptop panel at
1.25 scale, where the screensaver's fullscreen terminal (18 pt) is only 90
columns by 24 rows. Regenerate with `python3 wallpaper.py screensaver`; the
limit is `SS_COLS`/`SS_ROWS` in the script.

Omarchy keeps the screensaver art global
(`~/.config/omarchy/branding/screensaver.txt`) and never reads it from a theme,
so `theme-screensaver` is a theme-set hook that copies the current theme's
`screensaver.txt` into place and restores the previous art when you switch to a
theme without one. It's the same hook as in the hosaka theme; install it once:

```
omarchy hook install theme-set theme-screensaver
omarchy theme set ono-sendai
```

## Fish

`fish.theme` is fish's syntax highlighting in the same palette (fish 4.3+
format): commands in Ono-Sendai red, strings and separators in orange, comments
and autosuggestions in muted ink, a command that doesn't exist in bright red and
underlined. It has `[dark]` and `[unknown]` variants, identical.

Omarchy copies it to `~/.local/state/omarchy/current/theme/` with the rest of the
theme, so fish can follow whichever Omarchy theme is current. Link it once and
choose it from `config.fish`:

```
mkdir -p ~/.config/fish/themes
ln -s ~/.local/state/omarchy/current/theme/fish.theme ~/.config/fish/themes/omarchy.theme
```

```fish
# ~/.config/fish/config.fish
if status is-interactive; and test -f ~/.config/fish/themes/omarchy.theme
    fish_config theme choose omarchy
end
```

New shells pick it up; open ones keep their colours until restarted. A theme
without a `fish.theme` leaves fish on its defaults.

## Claude Desktop

`claude-desktop.jsonc` is the same palette for claude-desktop-extra: black
backgrounds, off-white text, Ono-Sendai red for the Claude mark, links, buttons
and focus, orange as the secondary accent. The light variant is the same red on
a pale warm panel. Symlink it in, restart the app, and pick Ono-Sendai in
Settings → Extra → Themes:

```
mkdir -p ~/.config/Claude/themes.d
ln -s ~/Work/ono-sendai-omarchy-theme/claude-desktop.jsonc ~/.config/Claude/themes.d/ono-sendai.jsonc
```

## Install

Symlink your checkout in. Don't use `omarchy theme install`: a theme cloned
straight into `~/.config/omarchy/themes` counts as a stranger's, and Omarchy
then ignores its `hyprland.lua`. A symlink to your own checkout doesn't.

```
ln -s ~/Work/ono-sendai-omarchy-theme ~/.config/omarchy/themes/ono-sendai
omarchy theme set ono-sendai
```

The login screen uses JetBrainsMono Nerd Font, which Omarchy ships. The
wallpapers need no fonts.
