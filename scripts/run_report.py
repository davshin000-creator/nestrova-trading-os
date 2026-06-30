from pathlib import Path
from analytics.log_loader import read_csv_rows
from analytics.trade_analyzer import analyze_trades
from analytics.ev_analyzer import analyze_ev
from analytics.action_plan import build_action_plan, save_action_plan
from analytics.report_builder import build_report

ROOT = Path(".")
REPORT_PATH = ROOT / "reports" / "latest_report.txt"

def main():
    trade_rows = read_csv_rows(ROOT / "trade_log.csv")
    ev_rows = read_csv_rows(ROOT / "expected_value_log.csv")

    trade_summary = analyze_trades(trade_rows)
    ev_summary = analyze_ev(ev_rows)
    action_plan = build_action_plan(trade_summary, ev_summary)
    save_action_plan(action_plan, ROOT / "reports" / "action_plan.json")

    report = build_report(trade_summary, ev_summary, action_plan)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved report: {REPORT_PATH}")
    print("Saved action plan: reports/action_plan.json")

if __name__ == "__main__":
    main()
