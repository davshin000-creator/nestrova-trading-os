"""NIC v4 Self Optimizer

Converts reflection/action reports into a safe strategy_override.json.
This does NOT edit main.py and does NOT place trades.
"""

import json
from pathlib import Path

DEFAULT_OVERRIDE = {
    "version": "NIC_v4_self_optimizer",
    "enabled": True,
    "disabled_strategies": [],
    "reduced_strategies": [],
    "preferred_strategies": [],
    "blocked_tickers": [],
    "strategy_score_adjust": {},
    "ticker_score_adjust": {},
    "ev_min_buy_adjust": 0.0,
    "recovery_exit_enabled": True,
    "notes": []
}

def load_json(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def build_override_from_action_plan(action_plan):
    override = dict(DEFAULT_OVERRIDE)
    if not action_plan:
        override["enabled"] = False
        override["notes"] = ["No action plan found. Override disabled."]
        return override

    disabled = action_plan.get("disabled_strategies", []) or []
    reduced = action_plan.get("reduced_strategies", []) or []
    preferred = action_plan.get("preferred_strategies", []) or []
    blocked = action_plan.get("blocked_tickers", []) or []

    # v3 reflection_action_plan format compatibility
    for item in action_plan.get("strategy_changes", []) or []:
        name = item.get("strategy")
        rec = item.get("recommendation", "")
        if name and rec == "REDUCE_OR_DISABLE":
            reduced.append(name)

    override["disabled_strategies"] = sorted(set(disabled))
    override["reduced_strategies"] = sorted(set(reduced))
    override["preferred_strategies"] = sorted(set(preferred))
    override["blocked_tickers"] = sorted(set(blocked))

    for s in override["disabled_strategies"]:
        override["strategy_score_adjust"][s] = -999

    for s in override["reduced_strategies"]:
        override["strategy_score_adjust"][s] = -25

    for s in override["preferred_strategies"]:
        override["strategy_score_adjust"][s] = 12

    for t in override["blocked_tickers"]:
        override["ticker_score_adjust"][t] = -999

    mode = action_plan.get("mode_recommendation") or action_plan.get("mode") or ""

    if mode in ["DEFENSIVE_TUNING", "APPLY_TARGETED_FIXES"]:
        override["ev_min_buy_adjust"] = 0.002
        override["notes"].append("Defensive tuning enabled: EV threshold increased.")

    if any("false stop" in str(n).lower() or "recovery" in str(n).lower() for n in action_plan.get("notes", [])):
        override["recovery_exit_enabled"] = True
        override["notes"].append("Recovery exit review enabled.")

    override["notes"].extend(action_plan.get("notes", []))
    return override

def merge_plans(*plans):
    merged = {
        "disabled_strategies": [],
        "reduced_strategies": [],
        "preferred_strategies": [],
        "blocked_tickers": [],
        "notes": []
    }
    mode = "OBSERVE"

    for plan in plans:
        if not plan:
            continue
        for key in ["disabled_strategies", "reduced_strategies", "preferred_strategies", "blocked_tickers"]:
            merged[key].extend(plan.get(key, []) or [])
        merged["notes"].extend(plan.get("notes", []) or [])

        # v3 reflection format
        for item in plan.get("strategy_changes", []) or []:
            if item.get("strategy"):
                merged["reduced_strategies"].append(item["strategy"])
        for item in plan.get("market_filter_changes", []) or []:
            merged["notes"].append(item)
        for item in plan.get("exit_changes", []) or []:
            merged["notes"].append(item)

        incoming = plan.get("mode_recommendation") or plan.get("mode")
        if incoming in ["DEFENSIVE_TUNING", "APPLY_TARGETED_FIXES"]:
            mode = incoming

    for key in ["disabled_strategies", "reduced_strategies", "preferred_strategies", "blocked_tickers", "notes"]:
        merged[key] = sorted(set(merged[key]))

    merged["mode_recommendation"] = mode
    return merged
