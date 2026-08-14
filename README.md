<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/hero-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/hero-light.svg" />
  <img alt="Matvey Safonov — ML &amp; systems engineer. macro-F1 0.978 on 5-class bacterial genome classification; Cohen's d 2.27 separating human from LSTM-generated Maltese text; and a from-scratch C++17 ML library that fits gradient boosting 15x faster than scikit-learn." src="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/hero-dark.svg" />
</picture>

I work in **Python** and **C++**: Python for research, modelling and the pipelines
around it, C++ for the parts where the algorithm itself has to be understood and made
fast. Everything below is my own work, and every number points at the artifact it was
read from.

## research

### Natural language as a whole — detecting generated Maltese text

**HSE University · *Spot the Bot* lab, adv. prof. V. A. Gromov** · [code, paper and defence deck](https://github.com/m1cch/spot-the-bot-maltese)

The lab's hypothesis is that natural language is a self-organised critical system: a
text is not a chain of words but a whole object with geometric and topological
structure in semantic vector space. If that holds, machine-generated text must differ
from human text *at the level of that structure* — even where it is locally plausible.
Not a trained detector, which is bound to one generator, but a statement about how the
n-gram cloud is organised.

My work carries the pipeline to **Maltese** — the only Semitic language written in
Latin script with EU official status, and a low-resource one: neither a usable corpus
nor a reliable lemmatiser existed, so both had to be built.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/pipeline-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/pipeline-light.svg" />
  <img alt="Pipeline: 110k raw documents to 36,452 balanced texts, through the hybrid lemmatiser L2 into a TF-IDF matrix and rank-1024 SVD dictionary; the same lemma tokens train a 44M-parameter LSTM generator; both corpora become 300k-point 4-gram clouds, analysed independently by Wishart clustering and persistent homology and compared under a B=40 bootstrap." src="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/pipeline-dark.svg" />
</picture>

**Contribution — hybrid lemmatiser L2.** Stanza tags Maltese parts of speech reliably
but its lemmas are not lexically grounded. L2 keeps only the POS and resolves the lemma
by cascade lookup against **Ġabra**, a 1.3M-form morphological database: exact match →
diacritics stripped → article or proclitic stripped → Stanza fallback → surface form.
Benchmarked against pure Stanza (L1) and a rule-based affix stripper (L3); L2 is what
the whole pipeline runs on.

**Generator.** Word-level LSTM trained from scratch — 2 layers, hidden 512, embedding
300, 50k vocabulary, **44M parameters**; held-out perplexity 164 → 98 over 8 epochs.
The bot corpus matches the human one exactly: 36,452 texts, each length drawn from the
empirical distribution of human text lengths.

**Significance.** Bootstrap over B=40 independent 30k-point subsamples, two-sample
Mann–Whitney, effect size as Cohen's d:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/effects-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/effects-light.svg" />
  <img alt="Effect sizes with 95% confidence intervals: noise fraction d=2.27, clusters d=1.40, Davies-Bouldin d=1.25, Calinski-Harabasz d=1.19 all significant; silhouette d=0.41 with an interval crossing zero, not significant." src="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/effects-dark.svg" />
</picture>

| metric | human | bot | d | p |
|---|---|---|---|---|
| noise fraction | 0.709 ± 0.010 | 0.730 ± 0.009 | **+2.27** | 2.9e-12 |
| clusters | 276.2 ± 8.3 | 289.1 ± 10.1 | **+1.40** | 4.6e-07 |
| Davies–Bouldin | 1.001 ± 0.087 | 1.144 ± 0.138 | **+1.25** | 2.6e-06 |
| Calinski–Harabasz | 278.8 ± 38.4 | 348.9 ± 74.3 | **+1.19** | 1.7e-06 |
| silhouette | 0.355 ± 0.012 | 0.361 ± 0.015 | +0.41 | 0.081 — *not significant* |

Persistent homology, computed separately over 5 subsamples, agrees: the bot cloud
carries ~93 more one-dimensional cycles — H1 Betti **1104.8 ± 28.3** against
**1012.2 ± 21.4** — with higher total persistence.

**Reading.** Two independent methods converge. The human cloud is consolidated — fewer
clusters, a pronounced dense core, fewer cycles; the generated cloud fragments. A
word-level LSTM learns local collocation well and does not reproduce the global
organisation of the semantic space. Stated limitation: ~72% of points fall to noise,
the expected curse of dimensionality, so only *differences between the two clouds* are
interpreted — never absolute values. Parameter sweep showed the significance threshold
h to be inert in high dimension, while k drives granularity (k=7 → ~400 clusters,
k=51 → ~30); k=11, h=1 fixed for all comparisons.

### 5-class bacterial genome classification

**HSE ML Hackathon 2026** · scikit-learn only, hard 60-second inference budget on 2 vCPU

90,000 × 286 genome fragments, where each feature is the count of length-10
nucleotide-composition windows — all C(13,3) = 286 of them. Classes are imbalanced:
two rare classes at ~4.8% and ~5.0% against three at ~30%, which is exactly where a
macro-F1 metric is won or lost.

| model | macro-F1 | fit (90k) | inside budget |
|---|---|---|---|
| DecisionTree, depth 5 — provided baseline | 0.663 | fast | ✓ |
| RandomForest 200 | 0.966 | ~20s | ✓ |
| **ExtraTrees 300 on raw counts** | **0.978** | **~17s** | **✓** |
| HistGradientBoosting 400, normalised | 0.981 | ~74s | ✗ over budget |

Chosen: ExtraTrees on raw counts, tuned `class_weight` for minority recall, plus
per-class prior weighting on out-of-fold probabilities — `argmax(proba · w)` — which is
the largest macro-F1 lever left once the model is fixed. HistGB scores marginally
higher and is disqualified by the wall clock; picking the model that fits the budget is
the actual problem.

### Applied ML

| | |
|---|---|
| **hse-ml** | coursework, contests and Kaggle: linear models, gradient boosting, phoneme classification, plus C++ contest solutions |
| **auto-kaggle** | harness for running and comparing Kaggle solutions locally against a holdout |
| [**paper-btc-sim**](https://github.com/m1cch/paper-btc-sim) | paper-trading simulator on live prediction-market data: FastAPI dashboard, WebSocket feed, SQLite |

## systems &amp; c++

ML algorithms rebuilt from scratch to know what the libraries are actually doing —
then benchmarked against them.

### [mlcore-cpp](https://github.com/m1cch/mlcore-cpp) — a machine learning library in C++17

Header-only, no dependencies: linear and logistic regression, kNN over a KD-tree with
hypersphere pruning, CART trees, random forest, extremely randomised trees, gradient
boosting with Newton leaf values and histogram splitting, k-means++, PCA and truncated
SVD via cyclic Jacobi. 42 tests, clean under `-Wall -Wextra -Wpedantic` and under
address + undefined sanitizers, CI on gcc and clang across Linux and macOS.

Benchmarked against scikit-learn 1.9 on identical data — 20k × 20, 5 classes, both
sides single-threaded:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/bench-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/bench-light.svg" />
  <img alt="Speed relative to scikit-learn on a log ratio axis: gradient boosting 15.1x faster, decision tree 1.30x, extra trees 1.05x at parity; random forest 0.76x, logistic regression 0.33x and kNN 0.13x slower." src="https://raw.githubusercontent.com/m1cch/m1cch/main/assets/bench-dark.svg" />
</picture>

| model | mlcore | sklearn | |
|---|---|---|---|
| gradient boosting (50) | **0.729s** | 11.000s | **15.1× faster**, macro-F1 0.971 vs 0.964 |
| extra trees (100) | 0.333s | 0.351s | parity |
| random forest (100) | 2.736s | **2.082s** | 0.76× — 11.4× faster with threads |
| logistic regression | 0.096s | **0.032s** | slower, and F1 0.657 vs 0.985 |
| kNN, 5k queries | 0.344s | **0.045s** | 0.13× — sklearn's search is BLAS-vectorised |

The boosting gap is histogram splitting against sklearn's exact-split implementation,
not C++ against Python. The logistic regression gap is real: full-batch gradient
descent has not converged where lbfgs has. Both are written up in the repo, along with
the split-search rewrite that took the decision tree from **15.33s to 0.127s** —
rescanning every sample per candidate threshold, replaced by one sort and a sweep with
incremental class histograms.

### [algorithms-cpp](https://github.com/m1cch/algorithms-cpp)

17 competitive programming solutions, C++17. Five reduce to maximum flow and share a
Dinic implementation with level BFS and blocking-flow DFS; plus DSU, graph traversal
and DP with memoisation. 26 sample tests, all passing.

### planned

`tda-cpp` — persistent homology and Wishart clustering in C++, an accelerator for the
Maltese pipeline above, where clustering is the bottleneck.

Also: ACOS coursework — C, RISC-V assembly, systems programming.

## stack

<table>
<tr><td><sub><b>languages</b></sub></td><td><img alt="python" src="https://img.shields.io/badge/python-30363d?style=flat-square&logo=python&logoColor=white" /> <img alt="c++" src="https://img.shields.io/badge/c%2B%2B-30363d?style=flat-square&logo=cplusplus&logoColor=white" /> <img alt="c" src="https://img.shields.io/badge/c-30363d?style=flat-square&logo=c&logoColor=white" /> <img alt="risc-v assembly" src="https://img.shields.io/badge/risc--v_assembly-30363d?style=flat-square" /> <img alt="rust" src="https://img.shields.io/badge/rust-30363d?style=flat-square&logo=rust&logoColor=white" /> <img alt="swift" src="https://img.shields.io/badge/swift-30363d?style=flat-square&logo=swift&logoColor=white" /> <img alt="sql" src="https://img.shields.io/badge/sql-30363d?style=flat-square&logo=postgresql&logoColor=white" /> <img alt="bash" src="https://img.shields.io/badge/bash-30363d?style=flat-square&logo=gnubash&logoColor=white" /></td></tr>
<tr><td><sub><b>ml &amp; data</b></sub></td><td><img alt="pytorch" src="https://img.shields.io/badge/pytorch-30363d?style=flat-square&logo=pytorch&logoColor=white" /> <img alt="tensorflow" src="https://img.shields.io/badge/tensorflow-30363d?style=flat-square&logo=tensorflow&logoColor=white" /> <img alt="keras" src="https://img.shields.io/badge/keras-30363d?style=flat-square&logo=keras&logoColor=white" /> <img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-30363d?style=flat-square&logo=scikitlearn&logoColor=white" /> <img alt="xgboost" src="https://img.shields.io/badge/xgboost-30363d?style=flat-square" /> <img alt="lightgbm" src="https://img.shields.io/badge/lightgbm-30363d?style=flat-square" /> <img alt="numpy" src="https://img.shields.io/badge/numpy-30363d?style=flat-square&logo=numpy&logoColor=white" /> <img alt="pandas" src="https://img.shields.io/badge/pandas-30363d?style=flat-square&logo=pandas&logoColor=white" /> <img alt="scipy" src="https://img.shields.io/badge/scipy-30363d?style=flat-square&logo=scipy&logoColor=white" /> <img alt="jupyter" src="https://img.shields.io/badge/jupyter-30363d?style=flat-square&logo=jupyter&logoColor=white" /> <img alt="plotly" src="https://img.shields.io/badge/plotly-30363d?style=flat-square&logo=plotly&logoColor=white" /> <img alt="opencv" src="https://img.shields.io/badge/opencv-30363d?style=flat-square&logo=opencv&logoColor=white" /> <img alt="hugging face" src="https://img.shields.io/badge/hugging_face-30363d?style=flat-square&logo=huggingface&logoColor=white" /> <img alt="anaconda" src="https://img.shields.io/badge/anaconda-30363d?style=flat-square&logo=anaconda&logoColor=white" /></td></tr>
<tr><td><sub><b>c++ toolchain</b></sub></td><td><img alt="c++17" src="https://img.shields.io/badge/c%2B%2B17-30363d?style=flat-square" /> <img alt="cmake" src="https://img.shields.io/badge/cmake-30363d?style=flat-square&logo=cmake&logoColor=white" /> <img alt="pybind11" src="https://img.shields.io/badge/pybind11-30363d?style=flat-square" /> <img alt="googletest" src="https://img.shields.io/badge/googletest-30363d?style=flat-square" /> <img alt="make" src="https://img.shields.io/badge/make-30363d?style=flat-square" /> <img alt="gdb" src="https://img.shields.io/badge/gdb-30363d?style=flat-square" /></td></tr>
<tr><td><sub><b>nlp &amp; topology</b></sub></td><td><img alt="stanza" src="https://img.shields.io/badge/stanza-30363d?style=flat-square" /> <img alt="fasttext" src="https://img.shields.io/badge/fasttext-30363d?style=flat-square" /> <img alt="gensim" src="https://img.shields.io/badge/gensim-30363d?style=flat-square" /> <img alt="ripser" src="https://img.shields.io/badge/ripser-30363d?style=flat-square" /> <img alt="giotto-tda" src="https://img.shields.io/badge/giotto--tda-30363d?style=flat-square" /> <img alt="chroma" src="https://img.shields.io/badge/chroma-30363d?style=flat-square" /></td></tr>
<tr><td><sub><b>llm</b></sub></td><td><img alt="anthropic" src="https://img.shields.io/badge/anthropic-30363d?style=flat-square&logo=anthropic&logoColor=white" /> <img alt="langchain" src="https://img.shields.io/badge/langchain-30363d?style=flat-square&logo=langchain&logoColor=white" /></td></tr>
<tr><td><sub><b>storage</b></sub></td><td><img alt="postgresql" src="https://img.shields.io/badge/postgresql-30363d?style=flat-square&logo=postgresql&logoColor=white" /> <img alt="pgvector" src="https://img.shields.io/badge/pgvector-30363d?style=flat-square" /> <img alt="supabase" src="https://img.shields.io/badge/supabase-30363d?style=flat-square&logo=supabase&logoColor=white" /> <img alt="sqlite" src="https://img.shields.io/badge/sqlite-30363d?style=flat-square&logo=sqlite&logoColor=white" /> <img alt="redis" src="https://img.shields.io/badge/redis-30363d?style=flat-square&logo=redis&logoColor=white" /> <img alt="clickhouse" src="https://img.shields.io/badge/clickhouse-30363d?style=flat-square&logo=clickhouse&logoColor=white" /> <img alt="minio" src="https://img.shields.io/badge/minio-30363d?style=flat-square&logo=minio&logoColor=white" /></td></tr>
<tr><td><sub><b>backend</b></sub></td><td><img alt="fastapi" src="https://img.shields.io/badge/fastapi-30363d?style=flat-square&logo=fastapi&logoColor=white" /> <img alt="flask" src="https://img.shields.io/badge/flask-30363d?style=flat-square&logo=flask&logoColor=white" /> <img alt="celery" src="https://img.shields.io/badge/celery-30363d?style=flat-square&logo=celery&logoColor=white" /> <img alt="pydantic" src="https://img.shields.io/badge/pydantic-30363d?style=flat-square&logo=pydantic&logoColor=white" /> <img alt="node.js" src="https://img.shields.io/badge/node.js-30363d?style=flat-square&logo=nodedotjs&logoColor=white" /></td></tr>
<tr><td><sub><b>infra</b></sub></td><td><img alt="docker" src="https://img.shields.io/badge/docker-30363d?style=flat-square&logo=docker&logoColor=white" /> <img alt="linux" src="https://img.shields.io/badge/linux-30363d?style=flat-square&logo=linux&logoColor=white" /> <img alt="nginx" src="https://img.shields.io/badge/nginx-30363d?style=flat-square&logo=nginx&logoColor=white" /> <img alt="pm2" src="https://img.shields.io/badge/pm2-30363d?style=flat-square&logo=pm2&logoColor=white" /> <img alt="git" src="https://img.shields.io/badge/git-30363d?style=flat-square&logo=git&logoColor=white" /> <img alt="actions" src="https://img.shields.io/badge/actions-30363d?style=flat-square&logo=githubactions&logoColor=white" /> <img alt="cloudflare" src="https://img.shields.io/badge/cloudflare-30363d?style=flat-square&logo=cloudflare&logoColor=white" /></td></tr>
</table>

<table>
<tr><td><sub><b>statistics</b></sub></td><td><img alt="eda" src="https://img.shields.io/badge/eda-21262d?style=flat-square" /> <img alt="experiment design" src="https://img.shields.io/badge/experiment_design-21262d?style=flat-square" /> <img alt="hypothesis testing" src="https://img.shields.io/badge/hypothesis_testing-21262d?style=flat-square" /> <img alt="a/b testing" src="https://img.shields.io/badge/a%2Fb_testing-21262d?style=flat-square" /> <img alt="bayesian inference" src="https://img.shields.io/badge/bayesian_inference-21262d?style=flat-square" /> <img alt="bootstrap ci" src="https://img.shields.io/badge/bootstrap_ci-21262d?style=flat-square" /> <img alt="mann-whitney" src="https://img.shields.io/badge/mann--whitney-21262d?style=flat-square" /> <img alt="cohen's d" src="https://img.shields.io/badge/cohen%27s_d-21262d?style=flat-square" /> <img alt="probability" src="https://img.shields.io/badge/probability-21262d?style=flat-square" /> <img alt="sampling" src="https://img.shields.io/badge/sampling-21262d?style=flat-square" /></td></tr>
<tr><td><sub><b>classical ml</b></sub></td><td><img alt="classification" src="https://img.shields.io/badge/classification-21262d?style=flat-square" /> <img alt="regression" src="https://img.shields.io/badge/regression-21262d?style=flat-square" /> <img alt="clustering" src="https://img.shields.io/badge/clustering-21262d?style=flat-square" /> <img alt="random forest" src="https://img.shields.io/badge/random_forest-21262d?style=flat-square" /> <img alt="extra-trees" src="https://img.shields.io/badge/extra--trees-21262d?style=flat-square" /> <img alt="gradient boosting" src="https://img.shields.io/badge/gradient_boosting-21262d?style=flat-square" /> <img alt="cross-validation" src="https://img.shields.io/badge/cross--validation-21262d?style=flat-square" /> <img alt="hyperparameter tuning" src="https://img.shields.io/badge/hyperparameter_tuning-21262d?style=flat-square" /> <img alt="regularization" src="https://img.shields.io/badge/regularization-21262d?style=flat-square" /> <img alt="imbalanced data" src="https://img.shields.io/badge/imbalanced_data-21262d?style=flat-square" /> <img alt="feature engineering" src="https://img.shields.io/badge/feature_engineering-21262d?style=flat-square" /> <img alt="macro-f1" src="https://img.shields.io/badge/macro--f1-21262d?style=flat-square" /> <img alt="roc-auc" src="https://img.shields.io/badge/roc--auc-21262d?style=flat-square" /></td></tr>
<tr><td><sub><b>deep learning</b></sub></td><td><img alt="cnn" src="https://img.shields.io/badge/cnn-21262d?style=flat-square" /> <img alt="rnn" src="https://img.shields.io/badge/rnn-21262d?style=flat-square" /> <img alt="lstm" src="https://img.shields.io/badge/lstm-21262d?style=flat-square" /> <img alt="transformers" src="https://img.shields.io/badge/transformers-21262d?style=flat-square" /> <img alt="attention" src="https://img.shields.io/badge/attention-21262d?style=flat-square" /> <img alt="embeddings" src="https://img.shields.io/badge/embeddings-21262d?style=flat-square" /> <img alt="autoencoders" src="https://img.shields.io/badge/autoencoders-21262d?style=flat-square" /> <img alt="transfer learning" src="https://img.shields.io/badge/transfer_learning-21262d?style=flat-square" /> <img alt="fine-tuning" src="https://img.shields.io/badge/fine--tuning-21262d?style=flat-square" /></td></tr>
<tr><td><sub><b>nlp</b></sub></td><td><img alt="tokenization" src="https://img.shields.io/badge/tokenization-21262d?style=flat-square" /> <img alt="lemmatization" src="https://img.shields.io/badge/lemmatization-21262d?style=flat-square" /> <img alt="n-grams" src="https://img.shields.io/badge/n--grams-21262d?style=flat-square" /> <img alt="tf-idf" src="https://img.shields.io/badge/tf--idf-21262d?style=flat-square" /> <img alt="word2vec" src="https://img.shields.io/badge/word2vec-21262d?style=flat-square" /> <img alt="fasttext" src="https://img.shields.io/badge/fasttext-21262d?style=flat-square" /> <img alt="text classification" src="https://img.shields.io/badge/text_classification-21262d?style=flat-square" /></td></tr>
<tr><td><sub><b>geometry &amp; topology</b></sub></td><td><img alt="pca" src="https://img.shields.io/badge/pca-21262d?style=flat-square" /> <img alt="svd" src="https://img.shields.io/badge/svd-21262d?style=flat-square" /> <img alt="umap" src="https://img.shields.io/badge/umap-21262d?style=flat-square" /> <img alt="t-sne" src="https://img.shields.io/badge/t--sne-21262d?style=flat-square" /> <img alt="manifold learning" src="https://img.shields.io/badge/manifold_learning-21262d?style=flat-square" /> <img alt="persistent homology" src="https://img.shields.io/badge/persistent_homology-21262d?style=flat-square" /> <img alt="betti numbers" src="https://img.shields.io/badge/betti_numbers-21262d?style=flat-square" /> <img alt="wishart clustering" src="https://img.shields.io/badge/wishart_clustering-21262d?style=flat-square" /> <img alt="topological data analysis" src="https://img.shields.io/badge/topological_data_analysis-21262d?style=flat-square" /></td></tr>
<tr><td><sub><b>llm systems</b></sub></td><td><img alt="rag" src="https://img.shields.io/badge/rag-21262d?style=flat-square" /> <img alt="agents" src="https://img.shields.io/badge/agents-21262d?style=flat-square" /> <img alt="tool use" src="https://img.shields.io/badge/tool_use-21262d?style=flat-square" /> <img alt="vector search" src="https://img.shields.io/badge/vector_search-21262d?style=flat-square" /> <img alt="semantic search" src="https://img.shields.io/badge/semantic_search-21262d?style=flat-square" /> <img alt="knowledge graphs" src="https://img.shields.io/badge/knowledge_graphs-21262d?style=flat-square" /></td></tr>
<tr><td><sub><b>engineering</b></sub></td><td><img alt="data structures" src="https://img.shields.io/badge/data_structures-21262d?style=flat-square" /> <img alt="algorithms" src="https://img.shields.io/badge/algorithms-21262d?style=flat-square" /> <img alt="complexity" src="https://img.shields.io/badge/complexity-21262d?style=flat-square" /> <img alt="oop" src="https://img.shields.io/badge/oop-21262d?style=flat-square" /> <img alt="memory management" src="https://img.shields.io/badge/memory_management-21262d?style=flat-square" /> <img alt="async concurrency" src="https://img.shields.io/badge/async_concurrency-21262d?style=flat-square" /> <img alt="design patterns" src="https://img.shields.io/badge/design_patterns-21262d?style=flat-square" /> <img alt="clean architecture" src="https://img.shields.io/badge/clean_architecture-21262d?style=flat-square" /> <img alt="api design" src="https://img.shields.io/badge/api_design-21262d?style=flat-square" /> <img alt="testing" src="https://img.shields.io/badge/testing-21262d?style=flat-square" /> <img alt="ci/cd" src="https://img.shields.io/badge/ci%2Fcd-21262d?style=flat-square" /> <img alt="code review" src="https://img.shields.io/badge/code_review-21262d?style=flat-square" /></td></tr>
</table>

## links

[x](https://x.com/m1cch_) · [github](https://github.com/m1cch) · <mmsafonov@gmail.com>

<sub>The dashboard above regenerates daily from the GitHub API —
<a href="scripts/hero.py">scripts/hero.py</a>. Curated numbers live in
<a href="data/metrics.json">data/metrics.json</a>, each carrying a pointer to the
committed artifact it was read from.</sub>
