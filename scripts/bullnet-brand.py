#!/usr/bin/env python3
"""Render every BullNet desktop icon from the brand-kit SVGs in resources/bullnet.

Run from the repo root:  <venv-with-cairosvg+pillow>/bin/python scripts/bullnet-brand.py
Sources (from the locked BullNet brand kit, 2026-11-13):
  bullnet-b-app-icon.svg              rounded Obsidian tile, Platinum B, Signal Green block
  bullnet-b-reversed.svg              transparent B (Platinum + Green), viewBox 32 44 420 420
  bullnet-lockup-vertical-on-dark.svg B + BULLNET wordmark on Obsidian (DMG background)
"""
import io
import re
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'resources' / 'bullnet'
ASSETS = ROOT / 'src' / 'assets'

OBSIDIAN = '#0B0F14'
GRAPHITE = '#343438'
GREEN = '#8ED13B'
MENTION_RED = '#D24B4E'

app_icon_svg = (SRC / 'bullnet-b-app-icon.svg').read_text()
reversed_svg = (SRC / 'bullnet-b-reversed.svg').read_text()

# The reversed B has two paths: the B itself (Platinum) and the block (Green).
B_PATH, BLOCK_PATH = re.findall(r'<path fill="[^"]+" d="([^"]+)"', reversed_svg)
B_VIEWBOX = re.search(r'viewBox="([^"]+)"', reversed_svg).group(1)


def render(svg: str, size: int) -> Image.Image:
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert('RGBA')


def mark_svg(b_fill: str, block_fill: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{B_VIEWBOX}">'
            f'<path fill="{b_fill}" d="{B_PATH}"/><path fill="{block_fill}" d="{BLOCK_PATH}"/></svg>')


def padded(img: Image.Image, size: int, inner: int) -> Image.Image:
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    off = (size - inner) // 2
    out.alpha_composite(img.resize((inner, inner), Image.LANCZOS), (off, off))
    return out


def with_dot(img: Image.Image, colour: str) -> Image.Image:
    """Badge dot in the top-right corner, like the stock mention/unread tray icons."""
    out = img.copy()
    s = out.size[0]
    r = max(3, round(s * 0.22))
    ImageDraw.Draw(out).ellipse((s - 2 * r, 0, s - 1, 2 * r - 1), fill=colour)
    return out


def tray_mark(size: int, b_fill: str, block_fill: str) -> Image.Image:
    # Tray icons need every pixel: the B fills ~94% of the box.
    return padded(render(mark_svg(b_fill, block_fill), 512), size, round(size * 0.94))


def save(img: Image.Image, rel: str, **kw):
    path = ASSETS / rel
    img.save(path, **kw)
    print('wrote', path.relative_to(ROOT))


# --- application icon ---------------------------------------------------------
master = render(app_icon_svg, 1024)
save(master, 'icon.icns', sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)])
save(master, 'icon.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
save(master.resize((48, 48), Image.LANCZOS), 'appicon_48.png')
save(padded(master, 32, 28), 'appicon_with_spacing_32.png')
save(master.resize((512, 512), Image.LANCZOS), 'linux/app_icon.png')
(ASSETS / 'linux' / 'icons').mkdir(exist_ok=True)
for px in (16, 24, 32, 48, 64, 128, 256, 512, 1024):  # electron-builder linux.icon dir (WxH.png)
    save(master.resize((px, px), Image.LANCZOS), f'linux/icons/{px}x{px}.png')

# --- Linux top-bar tray (dark = for light panels, light = for dark panels) ----
for theme, b_fill in (('dark', GRAPHITE), ('light', '#FFFFFF')):
    for scale, px in (('', 16), ('@2x', 32)):
        base = tray_mark(px, b_fill, GREEN)
        save(base, f'linux/top_bar_{theme}_16{scale}.png')
        save(with_dot(base, MENTION_RED), f'linux/top_bar_{theme}_mention_16{scale}.png')
        save(with_dot(base, GREEN), f'linux/top_bar_{theme}_unread_16{scale}.png')

# --- Windows tray ---------------------------------------------------------------
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)]
for theme, b_fill in (('dark', GRAPHITE), ('light', '#FFFFFF')):
    base = tray_mark(64, b_fill, GREEN)
    save(base, f'windows/tray_{theme}.ico', sizes=ico_sizes)
    save(with_dot(base, MENTION_RED), f'windows/tray_{theme}_mention.ico', sizes=ico_sizes)
    save(with_dot(base, GREEN), f'windows/tray_{theme}_unread.ico', sizes=ico_sizes)

# --- macOS menu bar (template images: black + alpha only) ---------------------
for pt in (16, 20, 24, 32):
    for scale, px in (('', pt), ('@2x', pt * 2)):
        base = tray_mark(px, '#000000', '#000000')
        save(base, f'osx/menuIcons/MenuIcon{pt}Template{scale}.png')
        save(with_dot(base, '#000000'), f'osx/menuIcons/MenuIconUnread{pt}Template{scale}.png')

# --- macOS DMG background (542x353, icons are placed by electron-builder) ------
dmg = Image.new('RGBA', (542, 353), OBSIDIAN)
lockup = (SRC / 'bullnet-lockup-vertical-on-dark.svg').read_text()
lockup = re.sub(r'<rect[^>]*/>', '', lockup, count=1)  # drop its own background tile
lock_png = cairosvg.svg2png(bytestring=lockup.encode(), output_height=96)
lock = Image.open(io.BytesIO(lock_png)).convert('RGBA')
dmg.alpha_composite(lock, ((542 - lock.size[0]) // 2, 24))
save(dmg.convert('RGB'), 'osx/DMG_BG.png')
