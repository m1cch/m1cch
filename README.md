<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/hero-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/hero-light.svg" />
  <img alt="Matvey Safonov — ML & systems engineer. macro-F1 0.978 on 5-class bacterial genome classification; Cohen's d 1.40 separating human from LSTM-generated Maltese text; 17s fit inside a 60s budget." src="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/hero-dark.svg" />
</picture>

## research

Every number below is committed in the repo it points at.

| project | problem | method | result |
|---|---|---|---|
| **[spot-the-bot-maltese](https://github.com/m1cch/spot-the-bot-maltese)** | tell LSTM-generated Maltese text from human text | TF-IDF → SVD embeddings (rank 1024), Wishart clustering, persistent homology | 275 vs 293 clusters · Cohen's d **1.40** · Mann–Whitney **p = 4.6e-07** · 95% CI [8.85, 16.95] over B=40 bootstrap |
| **ml-hackathon-bacteria** | 5-class bacterial genome classification | 286 nucleotide-composition features (10-mer windows), ExtraTrees + per-class threshold tuning for macro-F1 | macro-F1 **0.978** vs **0.641** baseline · 90k × 286 · fit in 17s under a hard 60s budget |
| **hse-ml** | coursework, contests, kaggle | linear models, gradient boosting, phoneme classification | notebooks + C++ contest solutions |

`spot-the-bot-maltese` is coursework for V. A. Gromov's lab at HSE — the paper and
the defence deck are in the repo, along with the raw result JSONs the numbers above
are read from.

## systems & c++

Low-level work, mostly ML algorithms rebuilt from scratch to understand what the
libraries are actually doing.

| project | what | status |
|---|---|---|
| **algorithms-cpp** | competitive programming solutions, C++17 | extracting from `hse-ml` |
| **mlcore-cpp** | linear models, kNN + KD-tree, decision tree, random forest, gradient boosting, k-means, PCA/SVD — C++17, benchmarked against scikit-learn, exposed through pybind11 | in progress |
| **tda-cpp** | persistent homology + Wishart clustering, an accelerator for the pipeline in `spot-the-bot-maltese` | planned |

## also public

| | | |
|---|---|---|
| [paper-btc-sim](https://github.com/m1cch/paper-btc-sim) | Python | paper-trading simulator: FastAPI dashboard, WebSocket feed, SQLite |
| [polymarket-collector](https://github.com/m1cch/polymarket-collector) | JavaScript | prediction-market data collector |
| [parser-for-cian](https://github.com/m1cch/parser-for-cian) | Python | real-estate listing parser |
| [slapmac](https://github.com/m1cch/slapmac) | Python | slap-detection through the microphone, because why not |
| [ausn-telegram-bot](https://github.com/m1cch/ausn-telegram-bot) | Python | tax calculator bot |

Most of what I build is in private repos — product work, mostly Python backends
and TypeScript frontends. Ask and I'll walk you through any of it.

## links

[x](https://x.com/m1cch_) · [github](https://github.com/m1cch) · <mmsafonov@gmail.com>

<sub>The dashboard above regenerates daily from the GitHub API — see
<a href="scripts/hero.py">scripts/hero.py</a>. The curated numbers live in
<a href="data/metrics.json">data/metrics.json</a>, each with a pointer to the
artifact it comes from. Full tool list: <a href="docs/tech-stack.md">docs/tech-stack.md</a>.</sub>
