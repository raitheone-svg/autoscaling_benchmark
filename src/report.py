"""Write results.json, tables.md, and figures (Pareto + accuracy)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SLO_TARGET = 0.05            # headline: cost to hold SLO violations <= 5%
COLORS = ["#B2182B", "#8c6bb1", "#1b7837", "#2166AC", "#d95f0e", "#444444"]


def _cost_at_target(curve, target=SLO_TARGET):
    ok = [p for p in curve if p["slo"] <= target]
    if ok:
        best = min(ok, key=lambda p: p["cost"])
        return best["cost"], best["headroom"], best["slo"]
    best = min(curve, key=lambda p: p["slo"])     # none reach target
    return best["cost"], best["headroom"], best["slo"]


def _order(results):
    pref = ["reactive", "persistence", "moving_average", "holt", "gbdt", "lstm"]
    return [m for m in pref if m in results] + [m for m in results if m not in pref]


def write(out_dir, results, cfg, provenance):
    os.makedirs(out_dir, exist_ok=True)
    order = _order(results)
    disp = {"reactive": "Reactive (HPA)", "persistence": "Persistence",
            "moving_average": "Moving average", "holt": "Holt (ES)",
            "gbdt": "GBDT", "lstm": "LSTM"}

    # ---- Pareto figure ----
    plt.rcParams.update({"font.family": "DejaVu Serif"})   # bundled with matplotlib (no warnings)
    fig, ax = plt.subplots(figsize=(5, 3.6))
    for i, m in enumerate(order):
        cur = sorted(results[m]["pareto"], key=lambda p: p["cost"])
        ax.plot([p["cost"] for p in cur], [p["slo"] * 100 for p in cur],
                "-o", ms=3, lw=1.3, color=COLORS[i % len(COLORS)], label=disp.get(m, m))
    ax.axhline(SLO_TARGET * 100, ls=":", color="#888", lw=1)
    ax.text(ax.get_xlim()[1], SLO_TARGET * 100, " 5% SLO", fontsize=7, va="bottom", ha="right", color="#888")
    ax.set_xlabel("Provisioned cost (mean capacity)"); ax.set_ylabel("SLO-violation rate (%)")
    ax.set_title("SLO–cost trade-off (lower-left is better)", fontsize=10)
    ax.legend(fontsize=7, frameon=False); ax.grid(True, lw=0.4, alpha=0.5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "pareto.png"), dpi=200); plt.close(fig)

    # ---- accuracy figure ----
    fig, ax = plt.subplots(figsize=(5, 3))
    sm = [results[m]["accuracy"]["smape"] for m in order]
    ax.bar([disp.get(m, m) for m in order], sm, color=[COLORS[i % len(COLORS)] for i in range(len(order))])
    ax.set_ylabel("sMAPE (%)"); ax.set_title("Forecast error (lower is better)", fontsize=10)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "accuracy.png"), dpi=200); plt.close(fig)

    # ---- results.json ----
    summary = {"provenance": provenance, "slo_target": SLO_TARGET, "methods": {}}
    for m in order:
        cost, hr, slo = _cost_at_target(results[m]["pareto"])
        summary["methods"][m] = {
            "display": disp.get(m, m), "accuracy": results[m]["accuracy"],
            "cost_at_slo_target": round(cost, 4), "headroom_used": hr,
            "slo_achieved": round(slo, 4), "pareto": results[m]["pareto"]}
    json.dump(summary, open(os.path.join(out_dir, "results.json"), "w"), indent=2)

    # ---- tables.md ----
    with open(os.path.join(out_dir, "tables.md"), "w") as fh:
        fh.write(f"Provenance: {provenance}\n\n")
        fh.write("Table I — forecast accuracy (test split)\n")
        fh.write("method | MAE | RMSE | sMAPE%\n")
        for m in order:
            a = results[m]["accuracy"]
            fh.write(f"{disp.get(m,m)} | {a['mae']} | {a['rmse']} | {a['smape']}\n")
        fh.write(f"\nTable II — cost to hold SLO violations <= {int(SLO_TARGET*100)}%\n")
        fh.write("method | cost | headroom | SLO achieved\n")
        base = summary["methods"].get("reactive", {}).get("cost_at_slo_target")
        for m in order:
            mm = summary["methods"][m]
            sv = ""
            if base and mm["cost_at_slo_target"]:
                sv = f" | {(1 - mm['cost_at_slo_target']/base)*100:+.0f}% vs reactive"
            fh.write(f"{mm['display']} | {mm['cost_at_slo_target']} | {mm['headroom_used']} "
                     f"| {mm['slo_achieved']}{sv}\n")
    return summary
