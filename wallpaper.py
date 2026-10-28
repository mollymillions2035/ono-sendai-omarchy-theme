#!/usr/bin/env python3
# Ono-Sendai wallpaper, 3840x2160: the deck maker's wordmark, redrawn as
# vectors from preview footage of the Neuromancer series; nothing is cut from the
# footage. The traces and bars around it in the footage are the deck's exterior
# art, so they stay on the deck; the camera's glow stays in the footage too.
# No HUDs, buttons, lights or photos.
#   1-ono-sendai      ONO-SENDAI alone, the size of the boot and login logo.
#   2-ono-sendai-red  the same, reversed: black on Ono-Sendai red.
# Also writes unlock.png (Plymouth logo), preview-unlock.png, sddm/logo.png and
# screensaver.txt. Needs numpy, Pillow, rsvg-convert, ImageMagick and (for
# screensaver.txt) omarchy-transcode-ascii. Usage: python3 wallpaper.py [name ...]
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 3840, 2160
BLACK = '#0a0707'
RED = '#e8261b'        # Ono-Sendai red, the theme accent
FG = '#e6d9d4'
# ---------------------------------------------------------------- helpers

def rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def render_svg(body, size=(W, H)):
    """Rasterize an SVG body to a premultiplied float RGBA array."""
    w, h = size
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, 'o.png')
        subprocess.run(['rsvg-convert', '-w', str(w), '-h', str(h), '-o', out], input=svg.encode(), check=True)
        a = np.asarray(Image.open(out).convert('RGBA'), np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    return a


def save(img, path):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, optimize=True)
    print(os.path.relpath(path, HERE))


# ---------------------------------------------------------------- the mark
#
# The wordmark is lettering, not a font: heavy capitals on a 100-unit cap
# height, stems 24 wide, bars 22 high, rounded where the footage is round.
# Each glyph is (advance, svg body drawn from the top-left of its cell).

def _stroke(d, w=22):
    return f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'


def _rect(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>'


GLYPHS = {
    'O': (80, '<path fill-rule="evenodd" d="M28,0 H52 Q80,0 80,28 V72 Q80,100 52,100 H28 Q0,100 0,72 V28 Q0,0 28,0 Z'
              ' M32,22 Q24,22 24,30 V70 Q24,78 32,78 H48 Q56,78 56,70 V30 Q56,22 48,22 Z"/>'),
    'N': (76, '<path d="M0,100 V0 H23 L53,54 V0 H76 V100 H53 L23,46 V100 Z"/>'),
    '-': (28, _rect(0, 40, 28, 21)),
    'S': (74, _stroke('M73,11 H28 Q11,11 11,30.5 Q11,50 28,50 H46 Q63,50 63,69.5 Q63,89 46,89 H1')),
    'E': (66, _rect(0, 0, 24, 100) + _rect(0, 0, 66, 22) + _rect(0, 39, 60, 22) + _rect(0, 78, 66, 22)),
    'D': (78, _rect(0, 0, 24, 100) + _stroke('M0,11 H40 Q67,11 67,38 V62 Q67,89 40,89 H0')),
    'A': (84, '<path fill-rule="evenodd" d="M0,100 L29,0 H55 L84,100 H61 L56,81 H28 L23,100 Z M33,62 H51 L42,30 Z"/>'),
    'I': (24, _rect(0, 0, 24, 100)),
}
GAP = 8   # letter gap in units


def wordmark_units(gap=GAP):
    """The wordmark at 100-unit cap height: (svg body, width)."""
    x, parts = 0, []
    for ch in 'ONO-SENDAI':
        adv, body = GLYPHS[ch]
        parts.append(f'<g transform="translate({x},0)">{body}</g>')
        x += adv + gap
    w = x - gap
    return ''.join(parts), w


def wordmark(x, y, cap, fill=RED, anchor='middle'):
    """ONO-SENDAI with its cap height `cap`, top edge at y; x is the left, middle or right."""
    body, w = wordmark_units()
    s = cap / 100
    x0 = x - w * s * {'start': 0, 'middle': 0.5, 'end': 1}[anchor]
    return f'<g transform="translate({x0:.2f},{y:.2f}) scale({s:.5f})" fill="{fill}" color="{fill}">{body}</g>'


# ---------------------------------------------------------------- wallpapers

# The boot splash draws unlock.png at its own size on a 1920x1080 panel, so on the
# 4K wallpaper (shown halved) the wordmark is twice unlock.png's cap height.
UNLOCK_CAP = 44


def wordmark_only(ground=BLACK, ink=RED):
    # Flat and sharp, as the company's own artwork would be: no glow, no bloom.
    word = render_svg(wordmark(W / 2, H / 2 - UNLOCK_CAP, UNLOCK_CAP * 2, ink))
    return np.broadcast_to(rgb(ground), (H, W, 3)) * (1 - word[..., 3:4]) + word[..., :3]


def reversed_out():
    # The same mark reversed: deck black on a field of Ono-Sendai red.
    return wordmark_only(RED, BLACK)


# ---------------------------------------------------------------- Plymouth

# The login screen's Hyprland picks its own monitor scale, so sddm/logo.png is the
# same wordmark at 4x; Main.qml draws it at a quarter of its pixel size, which
# Qt only ever scales down, sharp up to 4x.
LOGIN_SCALE = 4


def logo_png(path, scale=1):
    """The wordmark alone on transparency, at `scale` times the boot splash size."""
    body, w = wordmark_units()
    pad = 2 * scale
    cap = UNLOCK_CAP * scale
    cw, ch = int(w * cap / 100 + 0.999) + 2 * pad, cap + 2 * pad
    a = render_svg(wordmark(cw / 2, pad, cap), (cw, ch))
    al = a[..., 3:4]
    rgba = np.concatenate([np.where(al > 0, a[..., :3] / np.maximum(al, 1e-6), 0), al], -1)
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(path, optimize=True)
    print(os.path.relpath(path, HERE))


def unlock():
    """Plymouth logo (unlock.png) and the login screen's (sddm/logo.png)."""
    path = os.path.join(HERE, 'unlock.png')
    logo_png(path)
    logo_png(os.path.join(HERE, 'sddm', 'logo.png'), LOGIN_SCALE)
    preview_unlock(path, os.path.join(HERE, 'preview-unlock.png'))


def preview_unlock(logo, out, bg=BLACK, fg=FG):
    # The unlock screen at 1920x1080 with Omarchy's own Plymouth entry/lock
    # assets tinted with the theme foreground, like omarchy-plymouth-set does.
    ply = '/usr/share/omarchy/default/plymouth'
    with tempfile.TemporaryDirectory() as t:
        for a in ('entry', 'lock'):
            subprocess.run(['magick', f'{ply}/{a}.png', '-channel', 'RGB', '+level-colors', f'{fg},{fg}', f'{t}/{a}.png'], check=True)
        lw, lh = map(int, subprocess.run(['magick', 'identify', '-format', '%w %h', logo], capture_output=True, text=True).stdout.split())
        lx, ly = (1920 - lw) // 2, (1080 - lh) // 2
        ex, ey = (1920 - 286) // 2, ly + lh + 40
        kh = round(48 * 0.8); kw = round(84 * kh / 96)
        subprocess.run(['magick', '-size', '1920x1080', f'xc:{bg}', logo, '-geometry', f'+{lx}+{ly}', '-composite',
                        f'{t}/entry.png', '-geometry', f'+{ex}+{ey}', '-composite',
                        '(', f'{t}/lock.png', '-resize', f'{kw}x{kh}!', ')', '-geometry', f'+{ex - kw - 15}+{ey + (48 - kh) // 2}',
                        '-composite', out], check=True)
    print(os.path.relpath(out, HERE))


# ---------------------------------------------------------------- screensaver

# Omarchy's screensaver is a fullscreen terminal at 18 pt. On a 1920x1080 laptop
# panel at 1.25 scale that is 90 columns by 24 rows, so the art stays inside 86x22.
SS_COLS, SS_ROWS = 86, 22


def screensaver():
    """screensaver.txt: the wordmark in half-block characters, across the full
    width and about six rows tall, letterspaced so no two letters merge."""
    body, w = wordmark_units(gap=24)
    svg = f'<g fill="#fff" color="#fff">{body}</g>'
    size = (int(w) + 2, 102)
    a = render_svg(svg, size)[..., 3]
    with tempfile.TemporaryDirectory() as t:
        png = os.path.join(t, 'mark.png')
        rgba = np.zeros((*a.shape, 4), np.uint8)
        rgba[..., :3] = 255
        rgba[..., 3] = (a * 255 + 0.5).astype(np.uint8)
        Image.fromarray(rgba, 'RGBA').save(png)
        out = os.path.join(HERE, 'screensaver.txt')
        subprocess.run(['omarchy-transcode-ascii', png, out, '--mode', 'block',
                        '--width', str(SS_COLS), '--height', str(SS_ROWS), '--threshold', '45'],
                       check=True, stdout=subprocess.DEVNULL)
    lines = open(out).read().rstrip('\n').split('\n')
    cols = max(len(l) for l in lines)
    assert cols <= SS_COLS and len(lines) <= SS_ROWS, (cols, len(lines))
    print(f'screensaver.txt ({cols}x{len(lines)})')


JOBS = {
    '1-ono-sendai': wordmark_only,
    '2-ono-sendai-red': reversed_out,
}

if __name__ == '__main__':
    want = sys.argv[1:] or list(JOBS) + ['unlock', 'screensaver']
    os.makedirs(os.path.join(HERE, 'backgrounds'), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'sddm'), exist_ok=True)
    for name in want:
        if name == 'unlock':
            unlock()
        elif name == 'screensaver':
            screensaver()
        else:
            save(JOBS[name](), os.path.join(HERE, 'backgrounds', f'{name}.png'))
