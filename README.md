# Reproducible Autoscaling Benchmark (Alibaba microservice trace)

Fairly compares autoscaling / workload-prediction methods on **real Alibaba data**
under one protocol: forecast per-microservice CPU demand, provision to it under a
scaling delay, and measure the **SLO-violation vs. cost** trade-off.

Methods: Reactive HPA (delay-lagged), Moving average, Holt (exponential
smoothing), GBDT, LSTM (optional, needs PyTorch).

## Install
```
pip install numpy pandas scikit-learn matplotlib pyyaml
pip install torch        # optional, enables the LSTM method
```

## Self-test (no data needed)
```
python run_benchmark.py --config config_synth.yaml
```
Confirms the toolchain; writes outputs/pareto.png etc. These numbers are
synthetic — not results.

## Run on the REAL Alibaba data
1. The Alibaba trace files are not included in this repository. Obtain the
   `MSMetrics` trace from the [official Alibaba microservices v2022 trace
   page](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-microservices-v2022)
   and follow its download instructions and terms. Extract the `MSMetrics` CSV
   files under `./data/` (or point `data.data_dir` to the extracted folder).
2. In `config.yaml` set `data.data_dir` to that folder (default `./data`).
3. Run:
```
python run_benchmark.py --config config.yaml
```
Outputs in `outputs/`:
- `results.json` — full numbers (accuracy + Pareto per method)
- `tables.md` — Table I (forecast error) and Table II (cost at 5% SLO)
- `pareto.png` — the SLO-vs-cost frontier (the headline figure)
- `accuracy.png` — forecast-error bars

## What the result means
- **Table I:** forecast error (MAE / RMSE / sMAPE) per method.
- **Table II:** the cost each method needs to hold SLO violations <= 5% — lower is
  better. A proactive method that reaches the target at lower cost than Reactive
  is the win.
- **pareto.png:** lower-left dominates. A method whose curve sits below another's
  provisions more efficiently.

## Config knobs (config.yaml)
- `data.max_services` — how many busiest microservices to include.
- `features.horizon_seconds` — the scaling delay the forecaster must cover (H).
- `provision.headrooms` — the safety-margin sweep that traces the Pareto curve.
- `methods` — which to run (`lstm` auto-skips if torch is absent).

## Send results to Claude
Attach `outputs/results.json` + `outputs/pareto.png` and say "populate the
benchmark paper." Claude fills the tables, drops in the figure, and drafts the
write-up.

## Honesty notes
- All reported results come from the real trace; the synthetic mode is only a
  self-test (clearly labelled).
- Classical methods are tuned fairly; if a simple method (e.g., moving average)
  is competitive with ML at 60 s resolution, that is a legitimate finding worth
  reporting, not a failure.

## Files
```
config.yaml / config_synth.yaml   real / self-test configs
run_benchmark.py                  driver
src/io_demand.py                  load per-microservice demand (chunked)
src/features.py                   lead-correct forecasting features
src/split.py                      leakage-safe blocked split
src/methods.py                    reactive / MA / Holt / GBDT / LSTM
src/metrics.py                    accuracy + SLO/cost metrics
src/report.py                     tables, figures, results.json
```
