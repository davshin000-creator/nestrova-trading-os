import json
from pathlib import Path

def build_reflection_action_plan(reflection_summary):
    plan = {
        "mode": "REVIEW",
        "strategy_changes": [],
        "exit_changes": [],
        "market_filter_changes": [],
        "notes": []
    }

    reasons = reflection_summary.get("loss_reasons", {})
    bad_strategies = reflection_summary.get("bad_strategies", [])

    if reasons.get("POSSIBLE_FALSE_STOP", 0) >= 2:
        plan["exit_changes"].append("Enable/strengthen Recovery Score before small stop-loss exits.")
        plan["notes"].append("Multiple small losses may be false stops.")

    if reasons.get("STOP_LOSS", 0) >= 2:
        plan["exit_changes"].append("Review entry quality; avoid widening stop-loss before fixing entries.")
        plan["notes"].append("Repeated stop-loss exits detected.")

    if reasons.get("BEAR_MARKET_ENTRY", 0) >= 1:
        plan["market_filter_changes"].append("Disable aggressive entries during RISK_OFF_DAY unless EV is very high.")

    for s in bad_strategies[:5]:
        plan["strategy_changes"].append({
            "strategy": s["strategy"],
            "recommendation": "REDUCE_OR_DISABLE",
            "total_pct": round(s["total_pct"], 2),
            "avg_pct": round(s["avg_pct"], 2),
            "count": s["count"]
        })

    if not plan["strategy_changes"] and not plan["exit_changes"] and not plan["market_filter_changes"]:
        plan["mode"] = "COLLECT_MORE_DATA"
        plan["notes"].append("Not enough clear failure pattern yet.")
    else:
        plan["mode"] = "APPLY_TARGETED_FIXES"

    return plan

def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def build_action_plan(trade_summary, ev_summary):
    plan = {
        "mode_recommendation": "OBSERVE",
        "disabled_strategies": [],
        "reduced_strategies": [],
        "preferred_strategies": [],
        "blocked_tickers": [],
        "notes": []
    }
    return plan

def save_action_plan(plan, path="reports/action_plan.json"):
    import json
    from pathlib import Path
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
