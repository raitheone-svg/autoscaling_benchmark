#!/usr/bin/env python3
"""Autoscaling benchmark driver.

  python run_benchmark.py --config config.yaml

Set data.mode: synthetic for a self-test (no data needed), or alibaba to run on
the real MSMetrics trace in data/.
"""
import argparse, yaml
import numpy as np
from src import io_demand, features, split, methods, metrics, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    np.random.seed(cfg["run"]["seed"])

    print(f"[1/5] loading demand (mode={cfg['data']['mode']}) ...")
    df, dt = io_demand.load(cfg)
    print(f"      services={df['service'].nunique()}  rows={len(df)}  dt={dt}s")

    print("[2/5] building forecasting samples ...")
    b = features.build(df, dt, cfg)
    tr, va, te = split.blocked_split(b["meta"], cfg)
    print(f"      samples={len(b['y'])}  train={tr.sum()} val={va.sum()} test={te.sum()}"
          f"  (W={b['W']} H={b['H']})")

    print("[3/5] running methods ...")
    forecasts = methods.run(b, tr | va, cfg["methods"])   # learned train on train+val
    print(f"      methods: {', '.join(forecasts)}")

    print("[4/5] evaluating (accuracy + SLO/cost Pareto) ...")
    results = metrics.evaluate(b, forecasts, te, cfg)

    print("[5/5] reporting ...")
    summary = report.write(cfg["run"]["out_dir"], results, cfg, cfg["data"]["provenance"])
    print(f"\nForecast error (sMAPE%) and cost @ SLO<= {int(report.SLO_TARGET*100)}%:")
    for m, mm in summary["methods"].items():
        print(f"      {mm['display']:<16} sMAPE={mm['accuracy']['smape']:>5}  "
              f"cost={mm['cost_at_slo_target']:>7}  SLO={mm['slo_achieved']}")
    print(f"\nWrote {cfg['run']['out_dir']}/results.json, tables.md, pareto.png, accuracy.png")
    print(f"Provenance: {summary['provenance']}")


if __name__ == "__main__":
    main()
