"""Forecast-accuracy and autoscaling-outcome metrics, evaluated on the test
split. For each method we report headroom-independent accuracy and a
headroom-swept SLO-vs-cost curve (the Pareto frontier).
"""
import numpy as np
import pandas as pd


def accuracy(y, yhat):
    e = yhat - y
    mae = float(np.mean(np.abs(e)))
    rmse = float(np.sqrt(np.mean(e ** 2)))
    smape = float(np.mean(2 * np.abs(e) / (np.abs(y) + np.abs(yhat) + 1e-9)) * 100)
    return dict(mae=round(mae, 4), rmse=round(rmse, 4), smape=round(smape, 1))


def _actions(c, svc, tstep, deadband):
    """Average number of capacity changes per service over the test window."""
    dfm = pd.DataFrame({"c": c, "svc": svc, "t": tstep}).sort_values(["svc", "t"])
    total = 0; nsvc = 0
    for _, g in dfm.groupby("svc"):
        cc = g["c"].to_numpy()
        if len(cc) < 2:
            continue
        thr = deadband * (cc.mean() + 1e-9)
        total += int(np.sum(np.abs(np.diff(cc)) > thr)); nsvc += 1
    return total / max(1, nsvc)


def provision_point(y, yhat, headroom, svc, tstep, deadband):
    c = yhat * (1 + headroom); a = y
    slo = float(np.mean(c < a))                       # under-provision rate
    waste = float(np.mean(np.maximum(0, c - a)) / (np.mean(a) + 1e-9) * 100)
    cost = float(np.mean(c))                          # provisioned resource (lower better)
    return dict(headroom=headroom, slo=round(slo, 4), overprov_pct=round(waste, 1),
                cost=round(cost, 4), actions=round(_actions(c, svc, tstep, deadband), 2))


def evaluate(bundle, forecasts, te, cfg):
    y = bundle["y"][te]
    svc = bundle["svc"][te]
    tstep = bundle["meta"]["t_step"].to_numpy()[te]
    deadband = cfg["provision"]["deadband"]
    results = {}
    for name, yhat_all in forecasts.items():
        yhat = yhat_all[te]
        acc = accuracy(y, yhat)
        curve = [provision_point(y, yhat, h, svc, tstep, deadband)
                 for h in cfg["provision"]["headrooms"]]
        results[name] = dict(accuracy=acc, pareto=curve)
    return results
