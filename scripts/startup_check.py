"""Startup verification for Nestrova Trading OS."""
from pathlib import Path

REQUIRED_FILES = ["main.py", ".env", "requirements.txt", "update-bot.sh"]
EXPECTED_LOGS = ["trade_log.csv", "ai_decision_log.csv", "filter_log.csv", "rank_history.csv"]

def run_check(project_root="."):
    root = Path(project_root)
    print("===== NESTROVA STARTUP CHECK =====")
    ok = True
    for name in REQUIRED_FILES:
        exists = (root / name).exists()
        print(("✅" if exists else "❌"), name)
        ok = ok and exists
    print("----- existing logs -----")
    for name in EXPECTED_LOGS:
        print(("✅" if (root / name).exists() else "⚠️"), name)
    print("==================================")
    return ok

if __name__ == "__main__":
    run_check()
