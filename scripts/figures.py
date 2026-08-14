#!/usr/bin/env python3
"""Render the profile figures as themed SVG pairs.

    python3 scripts/figures.py

Reads data/figures.json — which carries only numbers transcribed from committed
result artifacts — and writes light and dark variants of each figure into
assets/. No network, no dependencies.

Three figures, three different jobs:
  effects   polarity against zero      → dot plot with CI whiskers
  bench     polarity against parity    → diverging bars on a log ratio axis
  pipeline  mechanism, not measurement → flow diagram
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from svgkit import (BAR_RADIUS, MARKER_RADIUS, MONO, SANS, THEMES, circle, line,
                    open_svg, path, rect, text)

ROOT = Path(__file__).resolve().parent.parent


def fmt_p(p: float) -> str:
    """Two significant figures in scientific notation, or plain for large p."""
    if p >= 0.01:
        return f"p = {p:.3f}".rstrip("0")
    exponent = int(math.floor(math.log10(p)))
    mantissa = p / (10 ** exponent)
    return f"p = {mantissa:.1f}e{exponent}"


# --------------------------------------------------------------- effect sizes


def render_effects(theme: str, fig: dict) -> str:
    c = THEMES[theme]
    rows = fig["rows"]
    n = fig["n"]

    W = 900
    ROW_H = 46
    TOP = 116
    H = TOP + len(rows) * ROW_H + 78

    # Plot band. Labels sit left, the read-out column sits right.
    x0, x1 = 250, 610
    d_min, d_max = -0.6, 3.2

    def sx(d: float) -> float:
        return x0 + (d - d_min) / (d_max - d_min) * (x1 - x0)

    def ci_halfwidth(d: float) -> float:
        # Hedges SE for two independent samples of equal size n.
        return 1.96 * math.sqrt((2 * n) / (n * n) + (d * d) / (4 * n))

    out = open_svg(W, H, fig["title"],
                   "Cohen's d with 95% confidence intervals for five clustering "
                   "metrics comparing human and machine-generated Maltese text.")
    out.append(rect(0.5, 0.5, W - 1, H - 1, fill=c["bg"], stroke=c["border"], rx=14))

    out.append(text(40, 50, fig["title"], size=19, fill=c["text"], family=SANS, weight=600))
    out.append(text(40, 72, fig["subtitle"], size=11.5, fill=c["muted"]))
    out.append(rect(40, 90, W - 80, 1, fill=c["hairline"]))

    # --- axis -------------------------------------------------------------
    # Conventional effect-size landmarks, drawn recessive.
    for d, label in [(0.0, "0"), (0.8, "0.8 · large"), (1.6, "1.6"), (2.4, "2.4"), (3.0, "3.0")]:
        x = sx(d)
        is_zero = d == 0.0
        out.append(line(x, TOP - 18, x, TOP + len(rows) * ROW_H - 14,
                        stroke=c["border"] if is_zero else c["hairline"],
                        width=1.5 if is_zero else 1,
                        dash=None if is_zero else "3 4"))
        out.append(text(x, TOP - 26, label, size=10, fill=c["faint"], anchor="middle"))

    out.append(text(x0, TOP + len(rows) * ROW_H + 6, "Cohen's d  →", size=10, fill=c["faint"]))

    # --- rows -------------------------------------------------------------
    for i, row in enumerate(rows):
        y = TOP + i * ROW_H
        significant = row["p"] < 0.05
        # Significance is carried by shape and an explicit label, never by hue
        # alone: a filled marker with solid whiskers, or a hollow marker with a
        # dashed one and an "n.s." tag.
        colour = c["pos"] if significant else c["muted"]

        out.append(text(40, y + 4, row["label"], size=12.5,
                        fill=c["text"] if significant else c["muted"]))
        out.append(text(40, y + 20, f'human {row["human"]}   ·   bot {row["bot"]}',
                        size=9.5, fill=c["faint"]))

        d = row["d"]
        half = ci_halfwidth(d)
        lo, hi = sx(d - half), sx(d + half)

        out.append(line(lo, y, hi, y, stroke=colour, width=2, cap="round",
                        dash=None if significant else "4 3", opacity=0.85))
        for cap_x in (lo, hi):
            out.append(line(cap_x, y - 5, cap_x, y + 5, stroke=colour, width=2, cap="round",
                            opacity=0.85))

        if significant:
            out.append(circle(sx(d), y, MARKER_RADIUS, fill=colour,
                              stroke=c["bg"], stroke_width=2))
        else:
            out.append(circle(sx(d), y, MARKER_RADIUS, fill=c["bg"],
                              stroke=colour, stroke_width=2))

        # Read-out column, right-aligned so the numbers form a scannable table.
        out.append(text(700, y + 4, f"d = {d:.2f}", size=12, fill=c["text"], anchor="end"))
        out.append(text(W - 40, y + 4, fmt_p(row["p"]), size=11,
                        fill=c["muted"] if significant else c["faint"], anchor="end"))
        if not significant:
            out.append(text(W - 40, y + 20, "not significant", size=9.5, fill=c["faint"],
                            anchor="end", style="italic"))

    out.append(rect(40, H - 46, W - 80, 1, fill=c["hairline"]))
    out.append(text(40, H - 24,
                    "95% CI from the Hedges standard error · a whisker crossing 0 means "
                    "the two corpora are not distinguishable on that metric",
                    size=10, fill=c["faint"]))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ benchmark


def render_bench(theme: str, fig: dict) -> str:
    c = THEMES[theme]
    rows = sorted(fig["rows"], key=lambda r: -(r["theirs"] / r["mine"]))

    W = 900
    ROW_H = 44
    TOP = 126
    H = TOP + len(rows) * ROW_H + 74

    # Log ratio axis: a 15x win and a 5x loss are then the same distance from
    # parity, which is the only honest way to draw a ratio.
    centre = 470
    span = 300           # pixels per decade
    lo_dec, hi_dec = -0.9, 1.25

    def sx(ratio: float) -> float:
        return centre + math.log10(ratio) * span

    out = open_svg(W, H, fig["title"],
                   "Fit time of mlcore-cpp relative to scikit-learn across six "
                   "models, on a logarithmic ratio axis centred on parity.")
    out.append(rect(0.5, 0.5, W - 1, H - 1, fill=c["bg"], stroke=c["border"], rx=14))

    out.append(text(40, 50, fig["title"], size=19, fill=c["text"], family=SANS, weight=600))
    out.append(text(40, 72, fig["subtitle"], size=11.5, fill=c["muted"]))
    out.append(rect(40, 90, W - 80, 1, fill=c["hairline"]))

    # Direction legend — the encoding is diverging, so name both arms.
    out.append(rect(40, 100, 9, 9, fill=c["neg"], rx=2))
    out.append(text(55, 108.5, "slower than scikit-learn", size=10.5, fill=c["muted"]))
    out.append(rect(240, 100, 9, 9, fill=c["pos"], rx=2))
    out.append(text(255, 108.5, "faster", size=10.5, fill=c["muted"]))

    bottom = TOP + len(rows) * ROW_H - 16

    for decade in (-0.5, 0.5, 1.0):
        x = centre + decade * span
        if not (lo_dec < decade < hi_dec):
            continue
        out.append(line(x, TOP - 20, x, bottom, stroke=c["hairline"], width=1, dash="3 4"))
        label = f"{10 ** decade:.1f}x" if decade > 0 else f"{10 ** decade:.2f}x"
        out.append(text(x, TOP - 28, label, size=10, fill=c["faint"], anchor="middle"))

    # Parity line, the reference everything is read against.
    out.append(line(centre, TOP - 20, centre, bottom, stroke=c["border"], width=1.5))
    out.append(text(centre, TOP - 28, "parity", size=10, fill=c["muted"], anchor="middle"))

    for i, row in enumerate(rows):
        y = TOP + i * ROW_H
        ratio = row["theirs"] / row["mine"]
        faster = ratio >= 1.0
        colour = c["pos"] if faster else c["neg"]

        out.append(text(40, y + 4, row["label"], size=12.5, fill=c["text"]))
        out.append(text(40, y + 20,
                        f'{row["phase"]} {row["mine"]:.3f}s vs {row["theirs"]:.3f}s   ·   '
                        f'F1 {row["f1_mine"]:.3f} vs {row["f1_theirs"]:.3f}',
                        size=9.5, fill=c["faint"]))

        x = sx(ratio)
        bar_lo, bar_hi = (centre, x) if faster else (x, centre)
        # A 2px gap at the parity line keeps the bar from fusing with the axis.
        if faster:
            bar_lo += 2
        else:
            bar_hi -= 2
        out.append(rect(bar_lo, y - 8, bar_hi - bar_lo, 16, fill=colour, rx=BAR_RADIUS,
                        opacity=0.9))

        label = f"{ratio:.2f}x" if ratio < 10 else f"{ratio:.1f}x"
        if faster:
            out.append(text(bar_hi + 10, y + 4, label, size=12, fill=c["text"], weight=600))
        else:
            out.append(text(bar_lo - 10, y + 4, label, size=12, fill=c["text"], weight=600,
                            anchor="end"))

    out.append(rect(40, H - 46, W - 80, 1, fill=c["hairline"]))
    out.append(text(40, H - 26,
                    "logarithmic ratio axis · each model timed on the phase that dominates it "
                    "— kNN does no real work at fit time, so it is timed on 5 000 queries",
                    size=10, fill=c["faint"]))
    out.append(text(40, H - 12,
                    "the boosting win is histogram splitting against sklearn's exact-split "
                    "implementation, not C++ against Python",
                    size=10, fill=c["faint"]))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------- pipeline


def render_pipeline(theme: str, fig: dict) -> str:
    c = THEMES[theme]
    by_id = {s["id"]: s for s in fig["stages"]}

    W, H = 900, 430
    BW, BH = 172, 62

    # Two symmetric branches — the human corpus and the generated one — that
    # split after the SVD dictionary and rejoin at the clouds.
    layout = {
        "corpus":  (40, 92),
        "lemma":   (232, 92),
        "svd":     (424, 92),
        "lstm":    (424, 186),
        "clouds":  (640, 139),
        "wishart": (232, 274),
        "topo":    (424, 274),
        "stats":   (640, 274),
    }

    out = open_svg(W, H, fig["title"],
                   "Pipeline: corpus, hybrid lemmatiser, SVD dictionary, LSTM "
                   "generator, n-gram clouds, then clustering and topology "
                   "compared under a bootstrap.")
    out.append(rect(0.5, 0.5, W - 1, H - 1, fill=c["bg"], stroke=c["border"], rx=14))

    out.append(text(40, 50, "Spot the Bot — Maltese", size=19, fill=c["text"],
                    family=SANS, weight=600))
    out.append(text(40, 70, "two independent methods over the same n-gram clouds",
                    size=11.5, fill=c["muted"]))

    def arrow(x1, y1, x2, y2, *, bend=False):
        if bend:
            mid = (x1 + x2) / 2
            d = f"M{x1:.1f},{y1:.1f} H{mid:.1f} V{y2:.1f} H{x2 - 8:.1f}"
        else:
            d = f"M{x1:.1f},{y1:.1f} H{x2 - 8:.1f}"
        out.append(path(d, stroke=c["border"], width=1.5))
        out.append(path(f"M{x2 - 8:.1f},{y2 - 4:.1f} L{x2:.1f},{y2:.1f} "
                        f"L{x2 - 8:.1f},{y2 + 4:.1f} Z", fill=c["border"]))

    # Edges first, so boxes sit on top of the arrowheads.
    arrow(40 + BW, 92 + BH / 2, 232, 92 + BH / 2)
    arrow(232 + BW, 92 + BH / 2, 424, 92 + BH / 2)
    arrow(424 + BW, 92 + BH / 2, 640, 139 + BH / 2, bend=True)
    arrow(424 + BW, 186 + BH / 2, 640, 139 + BH / 2, bend=True)
    # The SVD dictionary feeds the generator too — same lemma tokens both sides.
    out.append(path(f"M{424 + BW / 2:.1f},{92 + BH:.1f} V{186:.1f}", stroke=c["border"],
                    width=1.5, dash="4 3"))
    out.append(path(f"M{424 + BW / 2 - 4:.1f},{186 - 8:.1f} L{424 + BW / 2:.1f},{186:.1f} "
                    f"L{424 + BW / 2 + 4:.1f},{186 - 8:.1f} Z", fill=c["border"]))
    # Clouds feed the lower row. The return run sits at y=262, clear of the
    # generator box, which ends at y=248.
    run_y = 262
    drop_x = 640 + BW / 2
    into_x = 232 + BW / 2
    out.append(path(f"M{drop_x:.1f},{139 + BH:.1f} V{run_y} H{into_x:.1f} V{274 - 8:.1f}",
                    stroke=c["border"], width=1.5))
    out.append(path(f"M{into_x - 4:.1f},{274 - 8:.1f} L{into_x:.1f},{274:.1f} "
                    f"L{into_x + 4:.1f},{274 - 8:.1f} Z", fill=c["border"]))
    arrow(232 + BW, 274 + BH / 2, 424, 274 + BH / 2)
    arrow(424 + BW, 274 + BH / 2, 640, 274 + BH / 2)

    for sid, (x, y) in layout.items():
        stage = by_id[sid]
        terminal = sid == "stats"
        out.append(rect(x, y, BW, BH, fill=c["panel"],
                        stroke=c["accent"] if terminal else c["border"], rx=8,
                        stroke_width=1.5 if terminal else 1))
        out.append(text(x + 12, y + 22, stage["label"], size=12.5, fill=c["text"], weight=600))
        for k, part in enumerate(stage["detail"].split("\n")):
            out.append(text(x + 12, y + 38 + k * 12, part, size=9.5, fill=c["faint"]))

    out.append(rect(40, H - 52, W - 80, 1, fill=c["hairline"]))
    out.append(text(40, H - 32,
                    "dashed edge: the generator reuses the SVD lemma tokens, so its output "
                    "drops straight into the same n-gram construction",
                    size=10, fill=c["faint"]))
    out.append(text(40, H - 18,
                    "clustering and topology are computed independently and agree — that "
                    "agreement is the result",
                    size=10, fill=c["faint"]))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------- main


def main() -> None:
    figures = json.loads((ROOT / "data" / "figures.json").read_text())
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)

    renderers = {
        "effects": (render_effects, figures["effects"]),
        "bench": (render_bench, figures["bench"]),
        "pipeline": (render_pipeline, figures["pipeline"]),
    }

    for name, (fn, data) in renderers.items():
        for theme in THEMES:
            out = assets / f"{name}-{theme}.svg"
            out.write_text(fn(theme, data))
            print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
