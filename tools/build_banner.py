"""Builds assets/banner-dark.svg and assets/banner-light.svg.

All text is converted to SVG paths (Anton, JetBrains Mono, Instrument Serif,
all SIL Open Font License) so the banner looks the same on every device and
GitHub never has to load a font.

Usage: python tools/build_banner.py <fonts-dir>
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)


def load(name, wght=None):
    f = TTFont(FONTS / name)
    if wght and "fvar" in f:
        f = instantiateVariableFont(f, {"wght": wght})
    return f


ANTON = load("Anton.ttf")
MONO = load("JBM.ttf", wght=500)
SERIF = load("Serif.ttf")


def text_path(font, text, x, y, size, tracking=0.0):
    """Return (path_d, advance_width) for text with baseline at (x, y)."""
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    upm = font["head"].unitsPerEm
    s = size / upm
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    cx = x
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            g = cmap[ord("?")]
        tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
        gs[g].draw(tp)
        cx += gs[g].width * s + tracking * size
    return pen.getCommands(), cx - x


W, H = 1200, 420


def build(theme):
    if theme == "dark":
        bg, ink, dim, rule = "#0B0B0A", "#F1EEE6", "#8A877F", "#2A2925"
    else:
        bg, ink, dim, rule = "#F1EEE6", "#0B0B0A", "#6B6862", "#D3CFC4"
    saffron, lime = "#FF5B1F", "#D7FF3A"
    parts = []

    # top bar: prompt
    p1, w1 = text_path(MONO, "~/root/raghav", 56, 78, 22)
    p2, w2 = text_path(MONO, " $ whoami", 56 + w1, 78, 22)
    parts.append(f'<path d="{p1}" fill="{saffron}"/>')
    parts.append(f'<path d="{p2}" fill="{ink}"/>')
    # top-right: location tag
    tag, tw = text_path(MONO, "IN // DEV", 0, 0, 16, tracking=0.08)
    tx = W - 56 - tw - 28
    parts.append(f'<rect x="{tx}" y="52" width="{tw + 28}" height="36" fill="{lime}"/>')
    parts.append(f'<path d="{tag}" fill="#0B0B0A" transform="translate({tx + 14} 76)"/>')
    parts.append(f'<rect x="56" y="108" width="{W - 112}" height="2" fill="{rule}"/>')

    # big name
    size = 168
    n1, nw1 = text_path(ANTON, "RAGHAV", 0, 0, size, tracking=0.01)
    n2, nw2 = text_path(ANTON, "MITTAL", 0, 0, size, tracking=0.01)
    gap = 36
    total = nw1 + gap + nw2
    scale = min(1.0, (W - 112) / total)
    parts.append(
        f'<g transform="translate(52 300) scale({scale:.4f})">'
        f'<path d="{n1}" fill="{ink}"/>'
        f'<path d="{n2}" fill="{saffron}" transform="translate({nw1 + gap} 0)"/></g>'
    )

    # bottom line: serif + typed prompt
    s1, sw1 = text_path(SERIF, "developer, from India —", 56, 368, 34)
    parts.append(f'<path d="{s1}" fill="{dim}"/>')
    m1, mw1 = text_path(MONO, "> builds web, cloud & automation", 56 + sw1 + 16, 366, 22)
    parts.append(f'<path d="{m1}" fill="{ink}"/>')
    cx = 56 + sw1 + 16 + mw1 + 8
    parts.append(
        f'<rect x="{cx:.1f}" y="345" width="13" height="26" fill="{lime if theme == "dark" else saffron}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
        "</rect>"
    )

    body = "\n  ".join(parts)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="t">\n'
        f'  <title id="t">Raghav Mittal — developer from India. Builds web, cloud and automation.</title>\n'
        f'  <rect width="{W}" height="{H}" fill="{bg}"/>\n'
        f'  <rect x="0" y="{H - 10}" width="{W * 0.62:.0f}" height="10" fill="{saffron}"/>\n'
        f'  <rect x="{W * 0.62:.0f}" y="{H - 10}" width="{W * 0.38:.0f}" height="10" fill="{lime}"/>\n'
        f"  {body}\n</svg>\n"
    )
    (OUT / f"banner-{theme}.svg").write_text(svg, encoding="utf-8")
    print(theme, len(svg), "bytes")


build("dark")
build("light")
