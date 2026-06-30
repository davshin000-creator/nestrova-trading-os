import json
from pathlib import Path

def build_action_plan(trade_summary, ev_summary):
    plan = {
        "mode_recommendation": "OBSERVE",
        "disabled_strategies": [],
        "reduced_strategies": [],
        "preferred_strategies": [],
        "blocked_tickers": [],
        "notes": []
    }

    sell_count = trade_summary.get("sell_count", 0)
    total_profit = trade_summary.get("total_profit_pct", 0)
    avg_loss = trade_summary.get("avg_loss_pct", 0)

    if sell_count < 5:
        plan["mode_recommendation"] = "COLLECT_MORE_DATA"
        plan["notes"].append("Completed trades are fewer than 5. Do not overfit yet.")
    elif total_profit < 0:
        plan["mode_recommendation"] = "DEFENSIVE_TUNING"
        plan["notes"].append("Recent realized performance is negative. Reduce poor strategies before adding new entries.")

    for row in trade_summary.get("by_strategy", []):
        if row["count"] >= 3 and row["total_pct"] < -2:
            plan["disabled_strategies"].append(row["name"])
            plan["notes"].append(f"Disable/reduce strategy: {row['name']} total {row['total_pct']:.2f}%")
        elif row["count"] >= 3 and row["avg_pct"] < -0.5:
            plan["reduced_strategies"].append(row["name"])

    for row in reversed(trade_summary.get("by_strategy", [])):
        if row["count"] >= 3 and row["total_pct"] > 1:
            plan["preferred_strategies"].append(row["name"])

    for row in trade_summary.get("by_ticker", []):
        if row["count"] >= 2 and row["total_pct"] < -3:
            plan["blocked_tickers"].append(row["name"])
            plan["notes"].append(f"Temporarily block ticker: {row['name']} total {row['total_pct']:.2f}%")

    if ev_summary.get("count", 0) and ev_summary.get("avg_ev_pct", 0) < 0.3:
        plan["notes"].append("Average EV is low. Raise EV_MIN_BUY or reduce low-EV trades.")

    if avg_loss < -1.5:
        plan["notes"].append("Average loss is large. Review exit logic and false-stop / late-stop behavior.")

    return plan

def save_action_plan(plan, path="reports/action_plan.json"):
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
