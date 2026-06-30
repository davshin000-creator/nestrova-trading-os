"""Recorder: central place for reliable logging."""
import csv
from pathlib import Path
from datetime import datetime

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_csv(path, headers):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)

def append_csv(path, row, headers):
    ensure_csv(path, headers)
    with Path(path).open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
