# Reproducible Autoscaling Benchmark (Alibaba microservice trace)

A **benchmark / reproducibility study** (not a novel-algorithm proposal) that
fairly compares autoscaling / workload-prediction methods on **real Alibaba
data** under one protocol: forecast per-microservice CPU demand, provision to it
under a scaling delay, and measure the **SLO-violation vs. cost** trade-off.

Methods: Reactive HPA (delay-lagged), Moving average, Holt (exponential
smoothing), GBDT, LSTM (optional, needs PyTorch).

## Install
```
pip install -r requirements.txt
pip install torch        # optional, enables the LSTM method
```

## Self-test (no data needed)
```
python run_benchmark.py --config config_synth.yaml
```
Confirms the toolchain and writes `outputs/`. **These numbers are synthetic — not
results.**

## Run on the real Alibaba data
1. The Alibaba trace is **not included** in this repository. Obtain the
   `MSMetrics` table from the [official Alibaba microservices v2022 trace page](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-microservices-v2022)
   under its download instructions and terms. Extract the `MSMetrics` CSV files
   under `./data/` (or point `data.data_dir` to the extracted folder).
2. In `config.yaml` set `data.data_dir` to that folder (default `./data`).
3. Run:
```
python run_benchmark.py --config config.yaml
```
Outputs in `outputs/`: `results.json`, `tables.md`, `pareto.png`, `accuracy.png`.

## What the result means
- **Table I:** forecast error (MAE / RMSE / sMAPE) per method.
- **Table II:** the cost each method needs to hold SLO violations ≤ 5% — lower is
  better. A method that reaches the target at lower cost than Reactive is more
  efficient.
- **pareto.png:** the SLO–cost frontier; lower-left dominates.

## Reproducing the committed results
The results in `outputs/` were generated with:
- `MSMetrics` chunks **0–3** (first ~2 hours of the v2022 trace),
- `data.max_services: 50`, `features.horizon_seconds: 180` (H = 3 steps),
- `run.seed: 7`, and the default `provision.headrooms` sweep.

Set those in `config.yaml`, point `data_dir` at the extracted chunks, and rerun
to reproduce the same numbers.

## Limitations
- The SLO signal is a **CPU-capacity proxy** (under-provision = provisioned
  capacity < actual demand), **not measured latency**. Real response-time SLOs
  (from the `MSRTMCR` table) are planned future work.
- The committed run uses a limited slice (≈2 h, 50 busiest services); effect
  sizes are small and are best firmed up with more hours/services.
- 60 s sampling: sub-minute dynamics are not observed.

See `BENCHMARK_SPEC.md` for the full scope, planned extensions, and related work.

## Data & citation
This project uses the Alibaba microservice trace; please cite the dataset papers
and respect the trace's usage terms (the data itself is not redistributed here):

- S. Luo et al., "Characterizing Microservice Dependency and Performance: Alibaba
  Trace Analysis," ACM SoCC, 2021.
- S. Luo et al., "The Power of Prediction: Microservice Auto Scaling via Workload
  Learning," ACM SoCC, 2022.

To cite this benchmark, see `CITATION.cff` (GitHub's "Cite this repository").

## Config knobs (config.yaml)
- `data.max_services` — how many busiest microservices to include.
- `features.horizon_seconds` — the scaling delay the forecaster must cover (H).
- `provision.headrooms` — the safety-margin sweep that traces the Pareto curve.
- `methods` — which to run (`lstm` auto-skips if torch is absent).

## Files
```
config.yaml / config_synth.yaml   real / self-test configs
run_benchmark.py                  driver
src/io_demand.py                  load per-microservice demand (chunked)
src/features.py                   lead-correct forecasting features
src/split.py                      leakage-safe chronological split
src/methods.py                    reactive / MA / Holt / GBDT / LSTM
src/metrics.py                    accuracy + SLO/cost metrics
src/report.py                     tables, figures, results.json
```

## License
MIT — see `LICENSE`.
