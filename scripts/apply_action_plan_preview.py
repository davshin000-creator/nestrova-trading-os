"""Preview recommended config changes. Does not edit trading code."""
import json
from pathlib import Path

plan_path = Path("reports/action_plan.json")
if not plan_path.exists():
    print("No action_plan.json found. Run python scripts/run_report.py first.")
    raise SystemExit

plan = json.loads(plan_path.read_text(encoding="utf-8"))
print("===== ACTION PLAN PREVIEW =====")
print(json.dumps(plan, indent=2, ensure_ascii=False))
print("")
print("This is preview only. Do not auto-apply until we confirm the recommendations make sense.")
