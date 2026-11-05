#!/usr/bin/env python3
# Ono-Sendai wallpaper, 3840x2160: the deck maker's wordmark, redrawn as
# vectors from preview footage of the Neuromancer TV adaptation; nothing is cut
# from the footage. The traces and bars around it in the footage are the deck's exterior
# art, so they stay on the deck; the camera's glow stays in the footage too.
# No HUDs, buttons, lights or photos.
#   1-ono-sendai      ONO-SENDAI alone, the size of the boot and login logo.
#   2-ono-sendai-neon the same, as a lit neon outline.
#   3-ono-sendai-logo the full logo (OS emblem, wordmark, tagline) as a neon sign.
#   4-ono-sendai-os   the OS emblem alone, large, as a neon sign.
# Also writes unlock.png (Plymouth logo), preview-unlock.png, sddm/logo.png,
# screensaver.txt and about.txt. Needs numpy, Pillow, rsvg-convert, ImageMagick
# and (for the .txt art) BigBlueTermPlus Nerd Font Mono. Usage: python3 wallpaper.py [name ...]
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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


# ---------------------------------------------------------------- the emblem
#
# The OS emblem: a wireframe shell closing on a circuit board, around a heavy
# chamfered OS. Redrawn as clean vectors in an 800-unit box, so it stays sharp at
# 4K, with the mesh's edges meeting at real vertices.

_V = dict(
    A=(412, 42), B=(238, 120), C=(92, 258), D=(92, 540), E=(195, 645), F=(415, 780),
    G=(585, 115), H=(345, 138), I=(265, 195), J=(415, 232), K=(190, 252), M=(325, 244),
    P=(552, 150), Q=(495, 218), a=(132, 345), b=(92, 405), c=(132, 470),
    S=(150, 532), T=(258, 578), U=(412, 572), V=(290, 650), X=(412, 660), Y=(340, 576),
    Z=(335, 731),
)
_SHELL = 'AB BC CD DE EF AG'
_FACETS = ('AH AJ AP BH HP HI HJ BI IK BK CK CI KM IM MJ HM JQ '
           'Ca ab bc cD ac DS SE ST ET TY YU TV EV VX VZ XZ YV YX UF')
_BOARD = ['M412,312 L640,52 H740 V262 L695,298',
          'M679,106 L600,185 H523', 'M679,169 L590,258 H459', 'M657,243 L615,285',
          'M545,222 H500',
          'M458,552 L412,598', 'M500,552 L440,612 V682', 'M552,552 L488,616 V653',
          'M735,426 V520 L680,575 H565 L530,610 V672 L422,780', 'M585,620 H655']
_RINGS = [(690, 95, 15), (690, 158, 15), (668, 232, 15), (440, 697, 15), (488, 668, 15), (735, 408, 18)]
_OS = ('M205,295 H345 L395,345 V495 L345,545 H205 L155,495 V345 Z '
       'M222,345 H328 L345,362 V478 L328,495 H222 L205,478 V362 Z',
       'M695,298 L640,348 H495 L482,361 V382 L495,395 H640 L685,440 V500 L640,545 H410 L458,497 '
       'H625 L638,484 V456 L625,443 H480 L435,398 V345 L482,298 Z')
EMBLEM_BOX = (92, 42, 753, 780)


def emblem(x, y, h):
    """Emblem layers with its height h, top edge at y, centred on x: (line art, solid OS)."""
    x0, y0, x1, y1 = EMBLEM_BOX
    s = h / (y1 - y0)
    t = f'transform="translate({x - s * (x0 + x1) / 2:.2f},{y - s * y0:.2f}) scale({s:.5f})"'
    edge = lambda names: ''.join(f'M{_V[n[0]][0]},{_V[n[0]][1]} L{_V[n[1]][0]},{_V[n[1]][1]} ' for n in names.split())
    paint = 'fill="none" stroke="#fff" stroke-linejoin="round" stroke-linecap="round"'
    lines = (f'<g {t} {paint}>'
             f'<path d="{edge(_SHELL)}" stroke-width="5.5"/>'
             f'<path d="{edge(_FACETS)}" stroke-width="3"/>'
             f'<path d="{" ".join(_BOARD)}" stroke-width="5.5"/>'
             + ''.join(f'<circle cx="{a}" cy="{b}" r="{r}" stroke-width="5.5"/>' for a, b, r in _RINGS)
             + f'<path d="{" ".join(_OS)}" fill-rule="evenodd" stroke-width="6"/></g>')
    solid = f'<g {t} fill="#fff"><path fill-rule="evenodd" d="{_OS[0]}"/><path d="{_OS[1]}"/></g>'
    return lines, solid


# The line under the wordmark, lettered to match the OS: one stroke on a 100-unit
# cap height, chamfered corners. Each letter is (width, path).
LETTERS = {
    'A': (70, 'M0,100 V14 L14,0 H56 L70,14 V100 M0,60 H70'),
    'B': (70, 'M0,0 H56 L70,14 V36 L58,48 L70,60 V86 L56,100 H0 Z M0,48 H58'),
    'C': (70, 'M70,0 H14 L0,14 V86 L14,100 H70'),
    'E': (64, 'M64,0 H0 V100 H64 M0,50 H54'),
    'H': (70, 'M0,0 V100 M70,0 V100 M0,50 H70'),
    'I': (0, 'M0,0 V100'),
    'K': (66, 'M0,0 V100 M66,0 L16,50 H0 M16,50 L66,100'),
    'M': (84, 'M0,100 V0 L42,58 L84,0 V100'),
    'O': (72, 'M14,0 H58 L72,14 V86 L58,100 H14 L0,86 V14 Z'),
    'P': (70, 'M0,100 V0 H56 L70,14 V44 L56,58 H0'),
    'R': (70, 'M0,100 V0 H56 L70,14 V44 L56,58 H0 M42,58 L70,100'),
    'S': (70, 'M70,0 H14 L0,14 V36 L14,50 H56 L70,64 V86 L56,100 H0'),
    'T': (70, 'M0,0 H70 M35,0 V100'),
    'Y': (70, 'M0,0 L35,50 L70,0 M35,50 V100'),
}


def lettering(text, x, y, cap, weight=15, track=34):
    """`text` on one line, centred on x, top edge at y. '.' is a centred dot, ' ' a space."""
    sw, x1, parts = weight, 0, []
    dot = sw * 2
    for ch in text:
        if ch == ' ':
            x1 += 40
        elif ch == '.':
            parts.append(f'<rect x="{x1:.1f}" y="{50 - dot / 2:.1f}" width="{dot:.1f}" height="{dot:.1f}" fill="#fff" stroke="none" transform="rotate(45 {x1 + dot / 2:.1f} 50)"/>')
            x1 += dot + track
        else:
            w, d = LETTERS[ch]
            parts.append(f'<path transform="translate({x1:.1f},0)" d="{d}"/>')
            x1 += w + sw + track
    width = x1 - track - sw
    s = cap / (100 + sw)
    cid = 'c' + text.replace(' ', '').replace('.', '')
    # Square caps keep every stem level with the bars; the clip trims diagonals to the same band.
    return (f'<clipPath id="{cid}"><rect x="{-sw}" y="{-sw / 2}" width="{width + 2 * sw}" height="{100 + sw}"/></clipPath>'
            f'<g transform="translate({x - s * width / 2:.2f},{y + s * sw / 2:.2f}) scale({s:.5f})" clip-path="url(#{cid})" '
            f'fill="none" stroke="#fff" stroke-width="{sw}" stroke-linejoin="miter" stroke-miterlimit="8" stroke-linecap="square">{"".join(parts)}</g>')


# ---------------------------------------------------------------- wallpapers

# The boot splash draws unlock.png at its own size on a 1920x1080 panel, so on the
# 4K wallpaper (shown halved) the wordmark is twice unlock.png's cap height.
UNLOCK_CAP = 44


def wordmark_only():
    # Flat and sharp, as the company's own artwork would be: no glow, no bloom.
    word = render_svg(wordmark(W / 2, H / 2 - UNLOCK_CAP, UNLOCK_CAP * 2))
    return np.broadcast_to(rgb(BLACK), (H, W, 3)) * (1 - word[..., 3:4]) + word[..., :3]


def blur(a, sigma):
    """Gaussian blur of a 2-D float array: three box passes, on a shrunken copy when wide."""
    f = max(1, int(sigma / 5))
    h, w = a.shape
    im = np.asarray(Image.fromarray(a, 'F').resize((w // f, h // f), Image.BOX)) if f > 1 else a
    r = int(np.sqrt(4 * (sigma / f) ** 2 + 1)) // 2
    for axis in (0, 1):
        for _ in range(3):
            c = np.cumsum(np.pad(im, [(r + 1, r) if i == axis else (0, 0) for i in (0, 1)], mode='edge'), axis=axis)
            hi = c.take(range(2 * r + 1, c.shape[axis]), axis=axis)
            lo = c.take(range(0, c.shape[axis] - 2 * r - 1), axis=axis)
            im = (hi - lo) / (2 * r + 1)
    return np.asarray(Image.fromarray(im.astype(np.float32), 'F').resize((w, h), Image.BICUBIC)) if f > 1 else im


def tube_of(mark, softness):
    """A neon tube along the contour of a filled mask, its corners rounded the way
    bent glass would be. A wider softness makes a wider tube."""
    return np.clip(1.25 - np.abs(blur(mark, softness) - 0.5) / 0.26, 0, 1)


def light(tube, faces=None, solid=0, type_=0):
    """Light a sign on deck black. Each tube gets a hot core, a saturated halo and a
    wide spill of red. Emission goes through one curve, so weak light is pure
    Ono-Sendai red and only the cores burn towards white. The ground is plain deck
    black, with no texture to fight the windows on top. `faces` are hollow letters,
    which block part of their tubes' light; `solid` glows flat, like the OS."""
    source = tube + 0.45 * solid + 0.5 * type_
    glow = (0.55 * blur(source, 4) + 0.30 * blur(source, 14) + 0.40 * blur(source, 45)
            + 0.32 * blur(source, 150) + 0.30 * blur(source, 420))
    if faces is not None:
        glow = glow * (1 - 0.55 * faces)
    emission = 2.4 * tube + 0.5 * solid + 0.62 * type_ + glow
    # Hits the theme accent at emission 0.5, and a salmon white at a tube's core.
    k = np.array([4.8, 0.324, 0.26], np.float32)
    img = rgb(BLACK) + 1 - np.exp(-emission[..., None] * k)
    # The spill is too faint and wide for 8 bits: dither it so it doesn't band. A
    # small fixed tile of noise keeps the render repeatable and the PNG small.
    tile = np.random.default_rng(7).random((64, 64), np.float32)
    d = np.tile(tile, (H // 64 + 1, W // 64 + 1))[:H, :W, None]
    return np.floor(np.clip(img, 0, 1) * 255 + d + 1e-3) / 255


def neon_wordmark():
    # The first wallpaper's wordmark, in the same size and place, as a lit outline.
    mark = render_svg(wordmark(W / 2, H / 2 - UNLOCK_CAP, UNLOCK_CAP * 2, '#fff'))[..., 3]
    return light(tube_of(mark, 2), mark)


def neon_logo():
    # The full lockup: emblem, wordmark and tagline.
    emblem_h, cap = 640, 150
    gap_emblem, gap_sub, gap_city = 92, 72, 40
    sub, city = 40, 30
    total = emblem_h + gap_emblem + cap + gap_sub + sub + gap_city + city
    top = (H - total) / 2
    lines, solid = emblem(W / 2, top, emblem_h)
    y = top + emblem_h + gap_emblem

    body, w = wordmark_units(gap=13)
    s = cap / 100
    mark = render_svg(f'<g transform="translate({W / 2 - w * s / 2:.2f},{y:.2f}) scale({s:.5f})" fill="#fff" color="#fff">{body}</g>')[..., 3]
    y += cap + gap_sub

    tube = np.maximum(render_svg(lines)[..., 3], tube_of(mark, 2.5))
    type_ = render_svg(lettering('CYBERSPACE SYSTEMS', W / 2, y, sub, 15) +
                       lettering('TOKYO . CHIBA . BAMA', W / 2, y + sub + gap_city, city, 11, 38))[..., 3]
    return light(tube, mark, render_svg(solid)[..., 3], type_)


def neon_emblem():
    # The OS emblem alone and large, centred.
    h = 1400
    lines, solid = emblem(W / 2, (H - h) / 2, h)
    return light(render_svg(lines)[..., 3], solid=render_svg(solid)[..., 3])


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


# The terminal art is set in BigBlueTermPlus (the IBM PC's terminal lettering),
# not the vector wordmark: it is the deck's own text mode. The font is a bitmap
# on a 12-pixel grid, so at 12 px every font pixel lands on one screen pixel, and
# each becomes one half-block cell, which is square. Nothing is traced or scaled.
TERM_FONT = 'BigBlueTermPlus Nerd Font Mono'


def term_bitmap(text):
    """`text` in TERM_FONT at its native size, as a boolean pixel array cropped to the ink."""
    path = subprocess.run(['fc-match', '-f', '%{file}', TERM_FONT], capture_output=True, text=True, check=True).stdout
    assert 'BigBlueTermPlus' in path, f'{TERM_FONT} is not installed (fc-match gave {path})'
    font = ImageFont.truetype(path, 12)
    img = Image.new('1', (len(text) * 8 + 8, 24), 0)
    draw = ImageDraw.Draw(img)
    draw.fontmode = '1'
    draw.text((4, 4), text, font=font, fill=1)
    a = np.array(img)
    ys, xs = np.nonzero(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def half_blocks(a):
    """Two pixel rows per text row: top, bottom, both or neither."""
    if len(a) % 2:
        a = np.vstack([a, np.zeros((1, a.shape[1]), bool)])
    cell = {(0, 0): ' ', (1, 0): '▀', (0, 1): '▄', (1, 1): '█'}
    return [''.join(cell[int(t), int(b)] for t, b in zip(a[i], a[i + 1])).rstrip() for i in range(0, len(a), 2)]


def write_art(lines, out, cols, rows):
    w = max(len(l) for l in lines)
    assert w <= cols and len(lines) <= rows, (w, len(lines))
    with open(os.path.join(HERE, out), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{out} ({w}x{len(lines)})')


def screensaver():
    """screensaver.txt: ONO-SENDAI on one line in the terminal font, 78x5."""
    write_art(half_blocks(term_bitmap('ONO-SENDAI')), 'screensaver.txt', SS_COLS, SS_ROWS)


def about():
    """about.txt: the About (fastfetch) logo, at most 54x26 cells. One line would
    not fit, so it is stacked, ONO centred over SENDAI (the hyphen is only a
    line break), with a 3-pixel lead that keeps SENDAI on an even pixel row."""
    ono, sendai = term_bitmap('ONO'), term_bitmap('SENDAI')
    w = sendai.shape[1]
    a = np.zeros((ono.shape[0] + 3 + sendai.shape[0], w), bool)
    x = (w - ono.shape[1]) // 2
    a[:ono.shape[0], x:x + ono.shape[1]] = ono
    a[ono.shape[0] + 3:] = sendai
    write_art(half_blocks(a), 'about.txt', 54, 26)


JOBS = {
    '1-ono-sendai': wordmark_only,
    '2-ono-sendai-neon': neon_wordmark,
    '3-ono-sendai-logo': neon_logo,
    '4-ono-sendai-os': neon_emblem,
}

if __name__ == '__main__':
    want = sys.argv[1:] or list(JOBS) + ['unlock', 'screensaver', 'about']
    os.makedirs(os.path.join(HERE, 'backgrounds'), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'sddm'), exist_ok=True)
    for name in want:
        if name == 'unlock':
            unlock()
        elif name == 'screensaver':
            screensaver()
        elif name == 'about':
            about()
        else:
            save(JOBS[name](), os.path.join(HERE, 'backgrounds', f'{name}.png'))
