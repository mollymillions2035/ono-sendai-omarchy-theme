#!/usr/bin/env python3
# The animated scene behind Claude Desktop (claude-desktop-extra 5.11492.5+) for
# the Ono-Sendai theme: the matrix as the deck shows it. A red grid floor creeps
# toward the viewer, data structures stand in wireframe on the horizon (among
# them a stepped pyramid), constellations of data hang above, and pulses of
# light run out along the grid and round the structures. Vector line work only,
# after the app's own "vector-range" scene; one dark and one light version.
#
# Writes both SVGs into the "backdrop" line of claude-desktop.jsonc. The app
# inlines the SVG into its page, so every class and id here starts with "osm".
# No dependencies. Usage: python3 claude-desktop-scene.py [preview-dir]
#   With preview-dir, also writes scene-dark.svg and scene-light.svg there.
import json, math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'claude-desktop.jsonc')

W, H = 1600, 1000
VX, HZ = 800, 640          # vanishing point; the horizon
F, EYE = 800, 2.4          # focal length (px); eye height in grid units
NEAR, FAR = 5, 29          # depths the floor's cross lines travel between
STEP = 12                  # seconds for the floor to advance one grid unit

PALETTES = {
    'dark': dict(
        sky0='#0a0707', sky1='#170a09', ground0='#120908', ground1='#0a0707',
        line='#e8261b', far='#a81c14', cover='#0d0807', lit='#e8261b', lit_op=.05,
        point='#e6d9d4', head='#ffd9cf', halo='#ff5a4c', glow='#e8261b', glow_op=.16,
        calm='#0a0707', calm_op=.62),
    'light': dict(
        sky0='#f2ebe8', sky1='#ecdcd6', ground0='#eadbd5', ground1='#f2ebe8',
        line='#c2170e', far='#c2170e', cover='#efe6e2', lit='#c2170e', lit_op=.05,
        point='#5c4a46', head='#c2170e', halo='#c2170e', glow='#c2170e', glow_op=.10,
        calm='#f2ebe8', calm_op=.66),
}


def n(v):
    """A number as short as SVG allows."""
    s = f'{v:.1f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def proj(x, y, z):
    return VX + F * x / z, HZ - F * (y - EYE) / z


def pts(points, close=False):
    return 'M' + 'L'.join(f'{n(x)} {n(y)}' for x, y in points) + ('Z' if close else '')


# ------------------------------------------------------------------ floor

def floor_y(z):
    return HZ + F * EYE / z


def fade(z):
    """A cross line's opacity: out of the haze far off, full strength up close."""
    return ((FAR - z) / (FAR - NEAR)) ** 1.6 * .8


def creep_keyframes():
    """One cross line's whole trip from FAR to NEAR; the lines share it, staggered."""
    out, steps = [], 26
    for k in range(steps + 1):
        z = FAR * (NEAR / FAR) ** (k / steps)          # even steps on screen, roughly
        p = (FAR - z) / (FAR - NEAR) * 100
        op = fade(z)
        out.append(f'{n(p)}%{{transform:translateY({n(floor_y(z))}px);stroke-opacity:{op:.2f}}}')
    return ''.join(out)


def floor():
    count = FAR - NEAR
    dur = count * STEP
    rad = ''.join(f'M{VX} {HZ}L{n(VX + F * k / NEAR)} {n(floor_y(NEAR))}' for k in range(-18, 19))
    out = [f'<g stroke="url(#osm-floor)" stroke-width="1.2"><path d="{rad}"/></g>',
           '<g stroke-width="1.2">']
    for i in range(count):
        z = NEAR + i + .5                                # where it rests without animation
        op = fade(z)
        out.append(f'<path class="osm-cross" transform="translate(0 {n(floor_y(z))})" stroke-opacity="{op:.2f}" '
                   f'style="animation-delay:-{n((count - i - .5) * STEP)}s" d="M-200 0H1800"/>')
    out.append('</g>')
    return ''.join(out), dur


# ------------------------------------------------------------- structures

def box(x0, x1, z0, depth, h, tiers=0, y0=0):
    """A wireframe block on the floor: its front face and the side that faces the eye."""
    faces, lines = [], []
    z1 = z0 + depth
    front = [proj(x0, y0, z0), proj(x0, h, z0), proj(x1, h, z0), proj(x1, y0, z0)]
    side = None
    if x1 < 0:
        side = [proj(x1, y0, z0), proj(x1, h, z0), proj(x1, h, z1), proj(x1, y0, z1)]
    elif x0 > 0:
        side = [proj(x0, y0, z0), proj(x0, h, z0), proj(x0, h, z1), proj(x0, y0, z1)]
    if side:
        faces.append(side)
        lines.append(pts(side[1:]))
    faces.append(front)
    lines.append(pts(front))
    fine = []
    for t in range(1, tiers + 1):
        y = y0 + (h - y0) * t / (tiers + 1)
        fine.append(pts([proj(x0, y, z0), proj(x1, y, z0)]))
    return dict(z=z0, faces=faces, lines=lines, fine=fine, front=front)


def skyline(rng):
    """Blocks on both flanks, tallest at the edges, and a low far row between."""
    boxes = []
    for side in (-1, 1):
        for _ in range(11):
            z = rng.uniform(48, 120)
            sx = rng.uniform(60, 640)                    # px out from the vanishing point
            edge = (sx - 60) / 580                       # 0 at the middle, 1 at the screen edge
            w = rng.uniform(34, 100) * z / F
            hpx = rng.uniform(40, 110) + 230 * edge ** 1.6 * rng.uniform(.5, 1)
            x = side * (sx + 150) * z / F
            boxes.append(box(x - w / 2, x + w / 2, z, w * rng.uniform(.6, 1.4),
                             hpx * z / F, tiers=rng.choice((0, 0, 2, 3, 5))))
    for i in range(14):                                  # the far row
        z = rng.uniform(150, 190)
        sx = -560 + i * 86 + rng.uniform(-24, 24)
        w = rng.uniform(30, 70) * z / F
        x = sx * z / F
        boxes.append(box(x - w / 2, x + w / 2, z, w, rng.uniform(8, 30) * z / F))
    return boxes


def pyramid(cx_px, z, base_px, steps, rise_px):
    """The stepped pyramid: square tiers, each smaller than the one below."""
    out, y = [], 0
    for s in range(steps):
        half = base_px * (1 - s / steps) / 2 * z / F
        cx = cx_px * z / F
        top = y + rise_px * z / F
        out.append(box(cx - half, cx + half, z + (base_px / 2 * z / F - half), half * 2, top, y0=y))
        y = top
    return out


def outline(boxes):
    """Up the left edges, bottom block to top, then down the right edges."""
    fronts = [b['front'] for b in boxes]
    up = [q for f in fronts for q in (f[0], f[1])]
    down = [q for f in reversed(fronts) for q in (f[2], f[3])]
    return up + down


def draw(boxes, p):
    out = []
    for b in sorted(boxes, key=lambda b: -b['z']):
        dim = max(.28, min(1, 62 / b['z']))               # farther is fainter
        for face in b['faces']:
            out.append(f'<path class="osm-cover" d="{pts(face, True)}"/>')
        out.append(f'<path class="osm-lit" d="{pts(b["front"], True)}"/>')
        out.append(f'<path d="{"".join(b["lines"])}" stroke-opacity="{dim * .9:.2f}"/>')
        if b['fine']:
            out.append(f'<path d="{"".join(b["fine"])}" stroke-opacity="{dim * .22:.2f}"/>')
    return f'<g stroke="{p["line"]}" stroke-width="1.1">' + ''.join(out) + '</g>'


# ------------------------------------------------------------------- sky

def sky(rng, p):
    dust, joined, links, live = [], [], [], []
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(20, 560)
        if abs(x - VX) < 380 and rng.random() < .7:
            continue                                     # thin out the middle
        dust.append(f'M{n(x)} {n(y)}h0')
    for cx, cy in ((190, 150), (430, 330), (120, 430), (1380, 130), (1210, 300), (1500, 400), (760, 90)):
        rest = [(cx + rng.gauss(0, 44), cy + rng.gauss(0, 30)) for _ in range(rng.randint(5, 8))]
        stars = [rest.pop(0)]
        while rest:                                      # join each to its nearest neighbour
            rest.sort(key=lambda q: math.dist(q, stars[-1]))
            stars.append(rest.pop(0))
        links.append(pts(stars))
        for i, (x, y) in enumerate(stars):
            if i % 3 == 0:
                live.append(f'<path class="osm-breathe" style="animation-duration:{rng.choice((7, 10, 13, 16, 19))}s;'
                            f'animation-delay:-{n(rng.uniform(0, 9))}s" d="M{n(x)} {n(y)}h0"/>')
            else:
                joined.append(f'M{n(x)} {n(y)}h0')
    return (f'<g stroke-linecap="round"><path d="{"".join(dust)}" stroke="{p["point"]}" stroke-width="2" stroke-opacity=".3"/>'
            f'<path d="{"".join(links)}" stroke="{p["line"]}" stroke-width=".8" stroke-opacity=".3"/>'
            f'<path d="{"".join(joined)}" stroke="{p["line"]}" stroke-width="3" stroke-opacity=".8"/>'
            f'<g stroke="{p["line"]}" stroke-width="3.4">{"".join(live)}</g></g>')


# ---------------------------------------------------------------- pulses

def pulse(d, p, dur, delay, cls='osm-run'):
    """A point of light running the length of a path once per cycle, with its halo and tail."""
    st = f'style="animation-duration:{dur}s;animation-delay:-{delay}s"'
    common = f'd="{d}" pathLength="1" class="{cls}" stroke-linecap="round" {st}'
    return (f'<path {common} stroke="{p["halo"]}" stroke-width="1.6" stroke-opacity=".5" stroke-dasharray=".16 3"/>'
            f'<path {common} stroke="{p["halo"]}" stroke-width="9" stroke-opacity=".16" stroke-dasharray=".03 3"/>'
            f'<path {common} stroke="{p["head"]}" stroke-width="2.4" stroke-dasharray=".03 3"/>')


def floor_pulses(p):
    out = []
    for k, dur, delay in ((-7, 46, 5), (-3, 61, 33), (2, 53, 19), (5, 71, 50), (9, 43, 28), (-11, 67, 12)):
        a = (VX + F * k / NEAR, floor_y(NEAR))
        b = (VX + F * k / 60, floor_y(60))
        out.append(pulse(pts([a, b]), p, dur, delay))
    return ''.join(out)


# ----------------------------------------------------------------- scene

def scene(mode):
    p = PALETTES[mode]
    rng = random.Random(7)                                # the same scene every run
    grid, dur = floor()
    blocks = skyline(rng)
    steps = pyramid(430, 70, 250, 6, 34)
    tower = max((b for b in blocks if b['front'][3][0] < VX), key=lambda b: b['front'][0][1] - b['front'][1][1])
    traces = (pulse(pts(outline(steps)), p, 90, 20, 'osm-trace')
              + pulse(pts(outline([tower])), p, 120, 75, 'osm-trace'))
    css = (
        '.osm path{fill:none;stroke-linejoin:round}'
        f'.osm .osm-cover{{fill:{p["cover"]};stroke:none}}'
        f'.osm .osm-lit{{fill:{p["lit"]};fill-opacity:{p["lit_op"]};stroke:none}}'
        f'.osm .osm-cross{{stroke:{p["line"]};animation:osm-creep {dur}s linear infinite}}'
        '.osm .osm-breathe{stroke-opacity:.55;animation:osm-breathe 9s ease-in-out infinite}'
        '.osm .osm-run,.osm .osm-trace{stroke-dashoffset:-1.5;animation-iteration-count:infinite}'
        '.osm .osm-run{animation-name:osm-run;animation-timing-function:cubic-bezier(.1,.7,.3,1)}'
        '.osm .osm-trace{animation-name:osm-run;animation-timing-function:linear}'
        f'@keyframes osm-creep{{{creep_keyframes()}}}'
        '@keyframes osm-breathe{0%,100%{stroke-opacity:.12}50%{stroke-opacity:1}}'
        '@keyframes osm-run{0%{stroke-dashoffset:.16}30%,100%{stroke-dashoffset:-1.2}}'
        '[data-paused] .osm *{animation-play-state:paused!important}'
        '@media (prefers-reduced-motion:reduce){.osm *{animation:none!important}}'
    )

    def grad(i, stops, attrs='x1="0" y1="0" x2="0" y2="1"', kind='linear'):
        return (f'<{kind}Gradient id="osm-{i}" {attrs}>'
                + ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a != 1 else '') + '/>'
                          for o, c, a in stops) + f'</{kind}Gradient>')

    defs = (
        grad('sky', ((0, p['sky0'], 1), (1, p['sky1'], 1)))
        + grad('ground', ((0, p['ground0'], 1), (1, p['ground1'], 1)))
        + grad('glow', ((0, p['glow'], 0), (.6, p['glow'], p['glow_op'] * .35), (1, p['glow'], p['glow_op'])))
        + grad('floor', ((0, p['far'], 0), (.12, p['far'], .14), (.45, p['line'], .5), (1, p['line'], .85)),
               f'gradientUnits="userSpaceOnUse" x1="0" y1="{HZ}" x2="0" y2="{H}"')
        + grad('rim', ((0, p['line'], .9), (.3, p['line'], .5), (.5, p['line'], .15), (.7, p['line'], .5), (1, p['line'], .9)),
               f'gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0"')
        + grad('calm', ((0, p['calm'], p['calm_op']), (.55, p['calm'], p['calm_op'] * .6), (1, p['calm'], 0)),
               'cx=".5" cy=".5" r=".5"', 'radial')
    )
    body = (
        f'<rect width="{W}" height="{HZ}" fill="url(#osm-sky)"/>'
        f'<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#osm-ground)"/>'
        + sky(rng, p)
        + f'<rect y="{HZ - 260}" width="{W}" height="260" fill="url(#osm-glow)"/>'
        + grid + floor_pulses(p)
        + f'<path d="M-200 {HZ}H1800" stroke="url(#osm-rim)" stroke-width="1" stroke-opacity=".5"/>'
        + draw(blocks + steps, p) + traces
        + f'<ellipse cx="{VX}" cy="470" rx="640" ry="430" fill="url(#osm-calm)"/>'
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="osm" viewBox="0 0 {W} {H}" width="100%" height="100%" '
            f'preserveAspectRatio="xMidYMid slice"><style>{css}</style><defs>{defs}</defs>{body}</svg>')


def main():
    dark, light = scene('dark'), scene('light')
    backdrop = dict(svg=dark, darkSvg=dark, lightSvg=light,
                    glass=dict(blur=14, tint='#0a0707', lightTint='#f2ebe8', opacity=.5))
    line = '      "backdrop": ' + json.dumps(backdrop, separators=(', ', ': ')) + ','
    src = open(TARGET).read()
    new, hits = re.subn(r'^ *"backdrop": .*$', lambda _: line, src, flags=re.M)
    if not hits:
        new, hits = re.subn(r'^( *"name": "Ono-Sendai",)$', lambda m: m.group(1) + '\n' + line, src, flags=re.M)
    if hits != 1:
        sys.exit('claude-desktop.jsonc: no place for the "backdrop" line')
    open(TARGET, 'w').write(new)
    print(f'{os.path.basename(TARGET)}: backdrop written (dark {len(dark)} bytes, light {len(light)} bytes)')
    if len(sys.argv) > 1:
        os.makedirs(sys.argv[1], exist_ok=True)
        for name, svg in (('scene-dark.svg', dark), ('scene-light.svg', light)):
            open(os.path.join(sys.argv[1], name), 'w').write(svg)


if __name__ == '__main__':
    main()
