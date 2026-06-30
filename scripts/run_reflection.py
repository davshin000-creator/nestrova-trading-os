from pathlib import Path
from analytics.log_loader import read_csv_rows
from analytics.reflection_engine import build_reflections
from analytics.action_plan import build_reflection_action_plan, save_json
from analytics.reflection_report import build_reflection_report

ROOT = Path(".")
REPORT_PATH = ROOT / "reports" / "reflection_report.txt"
PLAN_PATH = ROOT / "reports" / "reflection_action_plan.json"

def main():
    trade_rows = read_csv_rows(ROOT / "trade_log.csv")
    summary = build_reflections(trade_rows)
    plan = build_reflection_action_plan(summary)

    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(build_reflection_report(summary, plan), encoding="utf-8")
    save_json(plan, PLAN_PATH)

    print(REPORT_PATH.read_text(encoding="utf-8"))
    print("")
    print(f"Saved: {REPORT_PATH}")
    print(f"Saved: {PLAN_PATH}")

if __name__ == "__main__":
    main()
