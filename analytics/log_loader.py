import csv
from pathlib import Path

def read_csv_rows(path):
    path = Path(path)
    if not path.exists():
        return []
    for enc in ("utf-8", "cp949"):
        try:
            with path.open("r", encoding=enc) as f:
                return list(csv.DictReader(f))
        except Exception:
            pass
    return []

def safe_float(value, default=0.0):
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default
