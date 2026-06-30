from pathlib import Path
from analytics.self_optimizer import load_json, save_json, merge_plans, build_override_from_action_plan

ROOT = Path(".")
ACTION_PLAN = ROOT / "reports" / "action_plan.json"
REFLECTION_PLAN = ROOT / "reports" / "reflection_action_plan.json"
OUTPUT = ROOT / "config" / "strategy_override.json"

def main():
    plan1 = load_json(ACTION_PLAN)
    plan2 = load_json(REFLECTION_PLAN)

    merged = merge_plans(plan1, plan2)
    override = build_override_from_action_plan(merged)
    save_json(override, OUTPUT)

    print("===== STRATEGY OVERRIDE GENERATED =====")
    print(f"Saved: {OUTPUT}")
    print("")
    print("Disabled:", ", ".join(override.get("disabled_strategies", [])) or "None")
    print("Reduced:", ", ".join(override.get("reduced_strategies", [])) or "None")
    print("Preferred:", ", ".join(override.get("preferred_strategies", [])) or "None")
    print("Blocked tickers:", ", ".join(override.get("blocked_tickers", [])) or "None")
    print("EV adjust:", override.get("ev_min_buy_adjust", 0))
    print("")
    print("This only writes config/strategy_override.json. It does not edit main.py.")

if __name__ == "__main__":
    main()
