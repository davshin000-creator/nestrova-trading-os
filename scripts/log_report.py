"""Quick log report for debugging."""
from pathlib import Path

def report(project_root="."):
    root = Path(project_root)
    print("===== CSV LOGS =====")
    for p in sorted(root.glob("*.csv")):
        print(f"{p.name}: {p.stat().st_size} bytes")

if __name__ == "__main__":
    report()
