from collections import defaultdict
from .log_loader import safe_float

def analyze_trades(trade_rows):
    sells = [r for r in trade_rows if r.get("event") == "SELL"]
    buys = [r for r in trade_rows if r.get("event") == "BUY"]
    profits = [safe_float(r.get("profit_rate")) for r in sells]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    result = {
        "buy_count": len(buys),
        "sell_count": len(sells),
        "win_rate": (len(wins) / len(sells) * 100) if sells else 0,
        "total_profit_pct": sum(profits) * 100,
        "avg_profit_pct": (sum(profits) / len(sells) * 100) if sells else 0,
        "avg_win_pct": (sum(wins) / len(wins) * 100) if wins else 0,
        "avg_loss_pct": (sum(losses) / len(losses) * 100) if losses else 0,
        "best_trade_pct": max(profits) * 100 if profits else 0,
        "worst_trade_pct": min(profits) * 100 if profits else 0,
    }

    buckets = {
        "by_ticker": defaultdict(list),
        "by_strategy": defaultdict(list),
        "by_market": defaultdict(list)
    }

    for r in sells:
        p = safe_float(r.get("profit_rate"))
        buckets["by_ticker"][r.get("ticker", "UNKNOWN")].append(p)
        buckets["by_strategy"][r.get("strategy", "UNKNOWN")].append(p)
        buckets["by_market"][r.get("market_regime", "UNKNOWN")].append(p)

    def summarize(bucket):
        out = []
        for k, vals in bucket.items():
            out.append({
                "name": k,
                "count": len(vals),
                "total_pct": sum(vals) * 100,
                "avg_pct": sum(vals) / len(vals) * 100,
                "win_rate": len([v for v in vals if v > 0]) / len(vals) * 100
            })
        return sorted(out, key=lambda x: x["total_pct"])

    for name, bucket in buckets.items():
        result[name] = summarize(bucket)

    return result
