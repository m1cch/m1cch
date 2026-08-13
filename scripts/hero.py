#!/usr/bin/env python3
"""Render the profile hero dashboard as two themed SVGs.

Pulls live data from the GitHub API (language bytes across public repos,
contribution calendar) and merges it with the hand-curated numbers in
data/metrics.json, then writes assets/hero-dark.svg and assets/hero-light.svg.

    GITHUB_TOKEN=... python3 scripts/hero.py

Everything is stdlib — the workflow runs it on a bare ubuntu runner.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("PROFILE_USER", "m1cch")
ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"

# Repos deliberately kept out of the language stats: the profile repo itself
# (it is markdown and generated SVG, not work) and anything explicitly muted.
EXCLUDE_REPOS = {USER}

# How many language rows the dashboard shows.
LANG_ROWS = 5

# GitHub linguist colours, so the bars match what GitHub itself draws.
LANG_COLORS = {
    "Python": "#3572A5",
    "C++": "#f34b7d",
    "C": "#555555",
    "Jupyter Notebook": "#DA5B0B",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Swift": "#F05138",
    "Rust": "#dea584",
    "Shell": "#89e051",
    "TeX": "#3D6117",
    "Go": "#00ADD8",
    "Assembly": "#6E4C13",
    "Makefile": "#427819",
    "CMake": "#DA3434",
    "Dockerfile": "#384d54",
    "PLpgSQL": "#336790",
    "Jinja": "#a52a22",
}
LANG_FALLBACK = "#8b949e"

# Display names: lowercase everywhere, per the design system.
LANG_DISPLAY = {"Jupyter Notebook": "jupyter", "C++": "c++", "C": "c", "TeX": "tex"}

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
    },
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# Canvas geometry.
W, H = 900, 520
PAD = 40
INNER = W - 2 * PAD  # 820


# --------------------------------------------------------------------------- api


def api(path: str, *, graphql: bool = False, body: dict | None = None):
    url = f"{API}/graphql" if graphql else f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method="POST" if body else "GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", f"{USER}-profile-hero")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    elif graphql:
        sys.exit("GITHUB_TOKEN is required for the contributions query")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def public_repos() -> list[str]:
    names, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        names += [r["name"] for r in batch if not r["fork"] and not r["private"]]
        if len(batch) < 100:
            break
        page += 1
    return [n for n in names if n not in EXCLUDE_REPOS]


def language_bytes() -> dict[str, int]:
    totals: dict[str, int] = {}
    for name in public_repos():
        try:
            langs = api(f"/repos/{USER}/{name}/languages")
        except urllib.error.HTTPError as e:
            print(f"  ! skipping {name}: {e}", file=sys.stderr)
            continue
        for lang, size in langs.items():
            totals[lang] = totals.get(lang, 0) + size
    return totals


def contributions() -> tuple[int, list[tuple[str, int]]]:
    """Return (total for the last year, per-month [(label, count), …]).

    Weekly buckets were unreadable — a year of them is 53 hairlines dominated by
    one spike. Twelve monthly bars carry the same information legibly.
    """
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }
    """
    res = api("", graphql=True, body={"query": query, "variables": {"login": USER}})
    cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    buckets: dict[str, int] = {}
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            buckets[day["date"][:7]] = buckets.get(day["date"][:7], 0) + day["contributionCount"]

    # Keep the trailing 12 whole-ish months; the calendar starts mid-month, so
    # the oldest bucket is partial and would understate that month.
    ordered = sorted(buckets.items())[-12:]
    names = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    return cal["totalContributions"], [(names[int(m.split("-")[1]) - 1], v) for m, v in ordered]


# ------------------------------------------------------------------------ render


def t(x, y, s, *, size=13, fill="#fff", family=MONO, weight=400, spacing=0, anchor="start", opacity=None):
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
    return f'<text {" ".join(attrs)}>{escape(str(s))}</text>'


def rect(x, y, w, h, *, fill="none", stroke=None, rx=0, opacity=None):
    attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{max(w, 0):.1f}"', f'height="{max(h, 0):.1f}"', f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}"')
    if rx:
        attrs.append(f'rx="{rx}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<rect {' '.join(attrs)} />"


def render(theme_name: str, metrics: dict, langs: dict[str, int], contrib_total: int, months: list[tuple[str, int]]) -> str:
    c = THEMES[theme_name]
    ident = metrics["identity"]
    out: list[str] = []

    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">')
    out.append(f'<title>{escape(ident["name"])} — {escape(ident["role"])}</title>')
    out.append(rect(0.5, 0.5, W - 1, H - 1, fill=c["bg"], stroke=c["border"], rx=14))

    # --- header ------------------------------------------------------------
    out.append(t(PAD, 78, ident["name"], size=38, fill=c["text"], family=SANS, weight=700, spacing=1.5))
    subtitle = f'{ident["role"]}  ·  {ident["affiliation"]}  ·  {ident["location"]}'
    out.append(t(PAD, 104, subtitle, size=13.5, fill=c["muted"], spacing=0.3))
    out.append(rect(PAD, 126, INNER, 1, fill=c["hairline"]))

    # A single accent mark, top-right — the one saturated pixel in the design.
    out.append(f'<circle cx="{W - PAD:.1f}" cy="70" r="5" fill="#3fb950" />')
    out.append(t(W - PAD - 16, 74, "available", size=11, fill=c["muted"], anchor="end", spacing=0.6))

    # --- kpi tiles ---------------------------------------------------------
    tiles = metrics["kpi"]
    gap, top, th = 16, 150, 94
    tw = (INNER - gap * (len(tiles) - 1)) / len(tiles)
    for i, tile in enumerate(tiles):
        x = PAD + i * (tw + gap)
        value = str(tile["value"]).replace("{contributions}", f"{contrib_total:,}".replace(",", " "))
        out.append(rect(x, top, tw, th, fill=c["panel"], stroke=c["border"], rx=8))
        # Long values (e.g. "4.6e-07") get a smaller size so they never clip.
        vsize = 30 if len(value) <= 6 else 24
        out.append(t(x + 16, top + 42, value, size=vsize, fill=c["text"], weight=600, spacing=-0.5))
        out.append(t(x + 16, top + 64, tile["label"].upper(), size=10, fill=c["muted"], spacing=1.2))
        out.append(t(x + 16, top + 80, tile["sub"], size=10, fill=c["faint"], spacing=0.2))

    # --- section labels ----------------------------------------------------
    col2 = PAD + 470
    out.append(t(PAD, 292, "LANGUAGES", size=10, fill=c["muted"], spacing=1.6))
    out.append(t(col2, 292, "ACTIVITY", size=10, fill=c["muted"], spacing=1.6))

    # --- language bars -----------------------------------------------------
    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: -kv[1])[:LANG_ROWS]
    bar_x, bar_w, row_h = PAD + 96, 288, 26
    for i, (lang, size) in enumerate(ranked):
        y = 310 + i * row_h
        share = size / total
        name = LANG_DISPLAY.get(lang, lang.lower())
        out.append(t(PAD, y + 9, name, size=12, fill=c["text"], opacity=0.9))
        out.append(rect(bar_x, y, bar_w, 8, fill=c["track"], rx=4))
        # Absolute scale: bar length is the percentage, so the picture and the
        # number can never disagree.
        out.append(rect(bar_x, y, bar_w * share, 8, fill=LANG_COLORS.get(lang, LANG_FALLBACK), rx=4))
        out.append(t(bar_x + bar_w + 46, y + 9, f"{share * 100:.1f}%", size=11.5, fill=c["muted"], anchor="end"))

    caption = f"bytes of code across public repositories · {total / 1000:,.0f} KB".replace(",", " ")
    out.append(t(PAD, 310 + LANG_ROWS * row_h + 16, caption, size=10, fill=c["faint"]))

    # --- contribution bars -------------------------------------------------
    spark_x, spark_w = col2, W - PAD - col2
    spark_y, spark_h = 310, 104
    peak = max((v for _, v in months), default=0) or 1
    n = len(months) or 1
    slot = spark_w / n
    bw = slot - 6
    out.append(rect(spark_x, spark_y + spark_h, spark_w, 1, fill=c["hairline"]))
    for i, (label, v) in enumerate(months):
        bh = (v / peak) * spark_h
        x = spark_x + i * slot + 3
        out.append(rect(x, spark_y + spark_h - max(bh, 2), bw, max(bh, 2), rx=2,
                        fill=c["text"] if v else c["faint"], opacity=0.6 if v else 0.25))
        # Label every other month so the axis never collides with itself.
        if i % 2 == len(months) % 2:
            out.append(t(x + bw / 2, spark_y + spark_h + 16, label, size=9.5,
                         fill=c["faint"], anchor="middle"))

    # Cumulative curve over the bars: monthly counts alone are spiky and read as
    # gaps, the running total shows the trend they actually add up to.
    running, points = 0, []
    for i, (_, v) in enumerate(months):
        running += v
        points.append((spark_x + i * slot + 3 + bw / 2, spark_y + spark_h - (running / max(contrib_total, 1)) * spark_h))
    path = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(points))
    out.append(f'<path d="{path}" fill="none" stroke="#3fb950" stroke-width="1.8" stroke-linejoin="round" opacity="0.9" />')
    if points:
        out.append(f'<circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="3" fill="#3fb950" />')

    out.append(t(spark_x, spark_y + spark_h + 34, "monthly bars · cumulative line", size=10, fill=c["faint"]))
    out.append(t(W - PAD, spark_y + spark_h + 34, f"peak {peak}", size=10, fill=c["faint"], anchor="end"))

    # --- footer ------------------------------------------------------------
    out.append(rect(PAD, H - 46, INNER, 1, fill=c["hairline"]))
    out.append(t(PAD, H - 22, f"github.com/{USER}", size=10.5, fill=c["muted"], spacing=0.4))
    out.append(t(W - PAD, H - 22, f"updated {date.today().isoformat()}", size=10.5, fill=c["faint"], anchor="end"))

    out.append("</svg>")
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------------- main


def main() -> None:
    metrics = json.loads((ROOT / "data" / "metrics.json").read_text())

    print("fetching language bytes…")
    langs = language_bytes()
    print(f"  {len(langs)} languages, {sum(langs.values()) / 1000:.0f} KB")

    print("fetching contributions…")
    total, months = contributions()
    print(f"  {total} contributions across {len(months)} months")

    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        path = assets / f"hero-{theme}.svg"
        path.write_text(render(theme, metrics, langs, total, months))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
