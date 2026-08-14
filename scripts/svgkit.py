"""Shared drawing primitives and design tokens.

The dashboard and the figures are one visual system, so the palette, the type
stack and the mark specs live in exactly one place. Anything that draws on this
profile imports from here.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

# --- surfaces and ink -------------------------------------------------------

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "hairline": "#21262d",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "faint": "#484f58",
        "track": "#21262d",
        # Diverging pair, validated against this surface: worst adjacent CVD
        # ΔE 19.2 (protan), normal-vision 29.0, both slots ≥ 3:1 on #0d1117.
        "pos": "#3987e5",
        "neg": "#e66767",
        "accent": "#3fb950",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "border": "#d0d7de",
        "hairline": "#d8dee4",
        "text": "#1f2328",
        "muted": "#59636e",
        "faint": "#8c959f",
        "track": "#eaeef2",
        # Same pair stepped for the light surface: CVD ΔE 21.6, normal 32.3.
        "pos": "#2a78d6",
        "neg": "#e34948",
        "accent": "#1a7f37",
    },
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# Mark specs: thin marks, rounded data-ends, markers no smaller than this.
BAR_RADIUS = 3
LINE_WIDTH = 2
MARKER_RADIUS = 5


def text(x, y, s, *, size=13, fill="#fff", family=MONO, weight=400, spacing=0,
         anchor="start", opacity=None, style=None):
    attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'font-family="{family}"',
        f'font-size="{size}"',
        f'fill="{fill}"',
    ]
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if style:
        attrs.append(f'font-style="{style}"')
    return f'<text {" ".join(attrs)}>{escape(str(s))}</text>'


def rect(x, y, w, h, *, fill="none", stroke=None, rx=0, opacity=None, dash=None,
         stroke_width=1):
    attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'width="{max(w, 0):.1f}"',
        f'height="{max(h, 0):.1f}"',
        f'fill="{fill}"',
    ]
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width}"')
    if rx:
        attrs.append(f'rx="{rx}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f"<rect {' '.join(attrs)} />"


def line(x1, y1, x2, y2, *, stroke, width=1, dash=None, cap="butt", opacity=None):
    attrs = [
        f'x1="{x1:.1f}"', f'y1="{y1:.1f}"', f'x2="{x2:.1f}"', f'y2="{y2:.1f}"',
        f'stroke="{stroke}"', f'stroke-width="{width}"',
    ]
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if cap != "butt":
        attrs.append(f'stroke-linecap="{cap}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<line {' '.join(attrs)} />"


def circle(cx, cy, r, *, fill, stroke=None, stroke_width=2, opacity=None):
    attrs = [f'cx="{cx:.1f}"', f'cy="{cy:.1f}"', f'r="{r}"', f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<circle {' '.join(attrs)} />"


def path(d, *, stroke=None, fill="none", width=2, dash=None, opacity=None,
         linejoin="round"):
    attrs = [f'd="{d}"', f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{width}"')
        attrs.append(f'stroke-linejoin="{linejoin}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<path {' '.join(attrs)} />"


def open_svg(width, height, title, desc=None):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img">',
        f"<title>{escape(title)}</title>",
    ]
    if desc:
        out.append(f"<desc>{escape(desc)}</desc>")
    return out
