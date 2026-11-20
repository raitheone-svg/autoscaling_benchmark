# Project Spec — A Reproducible Benchmark of Proactive Autoscaling & Workload-Prediction Methods on Production Microservice Traces


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


## Honest expected findings
Proactive forecasting beats reactive HPA on SLO violations at equal or lower cost for the predictable (high-rate, low-burstiness) services; the gap shrinks for bursty/low-rate services; classical forecasters are competitive with ML at 60 s resolution (a useful, slightly contrarian finding reviewers like). If the graph sub-study shows the call graph helps only marginally, we report that — it's still a finding.

## Target venues (benchmark/repro-friendly)
- **ICPE** (ACM/SPEC Performance Engineering) — strong benchmark & artifact-evaluation culture. Best fit.
- **MASCOTS**, **IEEE CLOUD**, **CCGrid**, or a **workshop** for a faster first publication.


