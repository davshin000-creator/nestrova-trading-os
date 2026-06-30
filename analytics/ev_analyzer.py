from .log_loader import safe_float

def analyze_ev(ev_rows):
    items = []
    for r in ev_rows:
        items.append({
            "ticker": r.get("ticker", ""),
            "strategy": r.get("strategy", ""),
            "ev_pct": safe_float(r.get("ev")) * 100,
            "decision": r.get("decision", ""),
            "market_brain": r.get("market_brain", ""),
            "reason": r.get("reason", "")
        })
    if not items:
        return {"count": 0, "avg_ev_pct": 0, "low_ev_count": 0, "top": [], "bottom": []}
    return {
        "count": len(items),
        "avg_ev_pct": sum(x["ev_pct"] for x in items) / len(items),
        "low_ev_count": len([x for x in items if x["ev_pct"] < 0.3]),
        "top": sorted(items, key=lambda x: x["ev_pct"], reverse=True)[:10],
        "bottom": sorted(items, key=lambda x: x["ev_pct"])[:10],
    }
