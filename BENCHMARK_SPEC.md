# Project Spec — A Reproducible Benchmark of Proactive Autoscaling & Workload-Prediction Methods on Production Microservice Traces

## What this is (and why it fits)
A **benchmark / reproducibility study**, not a novel-algorithm paper. Its value comes from rigor, fairness, and a reusable open artifact — so it does **not** depend on out-inventing DeepScaler/Madu. This is the lowest-risk honest path to a real publication, and it produces two assets at once:
- an **authored scholarly article** (EB-1A criterion 6), and
- an **open, reusable benchmark artifact** that, if adopted/cited, supports *original contribution of significance* (criterion 5).

(An immigration attorney should confirm your criteria mix — this is the technical plan, not legal advice.)

## One-line statement
*We build an open, reproducible harness that replays the public Alibaba microservice trace and fairly compares representative autoscaling and workload-prediction methods under a single protocol, reporting which methods win under which conditions and the SLO–cost trade-offs they imply.*

## Why it's achievable and honest
- Runs on **real, free data** you already have (Alibaba v2022; Google 2011 CC-BY optional as a second trace).
- **No novelty claim to defend** — the contribution is the fair comparison + the artifact + the findings.
- Reuses ~80% of what we already built (loader, chunked reader, leakage-safe blocked split, replay + metrics).
- Demand forecasting is a *forecastable* problem at 60 s resolution — results will be clean and positive.

## Data (real, unlicensed)
Alibaba **cluster-trace-microservices-v2022** (public OSS, free):
- `MSRTMCR` — per-microservice **call rate (demand)** + **response time (SLO signal)**, 60 s.
- `MSMetrics` — per-container CPU/memory (already downloaded).
- `MSCallGraph` — dependency edges (only needed if we include a graph-informed method).
Optional: **Google 2011** (CC-BY) as a second, graph-free trace for generality.

## The benchmark
**Task:** per microservice, forecast near-future demand (call rate), drive a proactive provisioning policy, and measure outcomes against a reactive baseline — all under one protocol.

**Methods compared (all existing, cited):**
- Reactive: Kubernetes-HPA-style threshold (the industry default).
- Naive: last-value / moving-average persistence.
- Classical forecasters: ARIMA, Holt-Winters / Prophet.
- ML forecasters: GBDT, LSTM (and optionally a graph-informed variant as a "does the call graph help?" sub-study).

**Metrics (reported per method, with distributions):**
- Forecast accuracy: MAE, RMSE, sMAPE; **surge recall & lead time**.
- Autoscaling outcome: **SLO-violation rate** (under-provision), **over-provisioning %** (waste), scaling-action count, a **cost proxy**, and the **SLO–cost Pareto frontier**.
- Breakdowns by microservice characteristics (call rate, burstiness, call-graph position).

**Protocol:** leakage-safe blocked temporal split (reused); many microservices; fixed seeds/config; fair hyperparameter tuning for every method; medians + variability reported.

## Deliverables
1. The **paper** (benchmark study) in the target venue's format.
2. An **open-source artifact**: code, configs, processed features, one-command reproduction.
3. Tables + figures: accuracy, Pareto frontier, per-characteristic breakdowns.

## Honest expected findings
Proactive forecasting beats reactive HPA on SLO violations at equal or lower cost for the predictable (high-rate, low-burstiness) services; the gap shrinks for bursty/low-rate services; classical forecasters are competitive with ML at 60 s resolution (a useful, slightly contrarian finding reviewers like). If the graph sub-study shows the call graph helps only marginally, we report that — it's still a finding.

## Target venues (benchmark/repro-friendly)
- **ICPE** (ACM/SPEC Performance Engineering) — strong benchmark & artifact-evaluation culture. Best fit.
- **MASCOTS**, **IEEE CLOUD**, **CCGrid**, or a **workshop** for a faster first publication.

## Reuse vs. new work
- **Reuse:** trace download tooling, chunked CSV loader, blocked split, replay harness, metrics/reporting.
- **New:** load `MSRTMCR` (demand+RT), define the SLO signal, implement the baseline method suite, implement the provisioning policy + cost model, run the comparison, package the artifact.

## Implementation plan
1. Download `MSRTMCR` (+ `MSCallGraph` only if we do the graph sub-study) — same free mechanism as before.
2. Build the demand + SLO data layer and the provisioning/cost model.
3. Implement the method suite (reactive, persistence, ARIMA/Holt-Winters, GBDT, LSTM).
4. Run the benchmark; generate the Pareto frontier + breakdowns.
5. Package the open artifact; write the paper.
