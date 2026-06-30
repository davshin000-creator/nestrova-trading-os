from collections import Counter, defaultdict
from .log_loader import safe_float

def classify_loss_reason(row):
    profit = safe_float(row.get("profit_rate"))
    note = (row.get("note") or "").lower()
    strategy = row.get("strategy", "")
    market = row.get("market_regime", "")

    if profit >= 0:
        return "WIN"

    if "손절" in note or "stop" in note:
        if profit > -0.012:
            return "POSSIBLE_FALSE_STOP"
        return "STOP_LOSS"
    if "트레일링" in note:
        return "TRAILING_EXIT"
    if "브레이크이븐" in note:
        return "BREAKEVEN_EXIT"
    if "bear" in market.lower():
        return "BEAR_MARKET_ENTRY"
    if "Momentum" in strategy and profit < 0:
        return "MOMENTUM_FAILED"
    if "Breakout" in strategy and profit < 0:
        return "BREAKOUT_FAILED"
    return "UNKNOWN_LOSS"

def build_reflections(trade_rows):
    sells = [r for r in trade_rows if r.get("event") == "SELL"]
    reflections = []
    reason_counter = Counter()
    strategy_loss = defaultdict(float)
    strategy_count = defaultdict(int)

    for r in sells:
        reason = classify_loss_reason(r)
        profit = safe_float(r.get("profit_rate"))
        strategy = r.get("strategy", "UNKNOWN")

        reason_counter[reason] += 1
        strategy_loss[strategy] += profit
        strategy_count[strategy] += 1

        if profit < 0:
            reflections.append({
                "time": r.get("time", ""),
                "ticker": r.get("ticker", ""),
                "strategy": strategy,
                "profit_pct": profit * 100,
                "reason": reason,
                "note": r.get("note", ""),
                "reflection": make_reflection_text(r, reason)
            })

    bad_strategies = []
    for strategy, total in strategy_loss.items():
        count = strategy_count[strategy]
        avg = total / max(count, 1)
        if count >= 2 and total < 0:
            bad_strategies.append({
                "strategy": strategy,
                "count": count,
                "total_pct": total * 100,
                "avg_pct": avg * 100
            })

    bad_strategies = sorted(bad_strategies, key=lambda x: x["total_pct"])

    return {
        "loss_reasons": dict(reason_counter),
        "reflections": reflections,
        "bad_strategies": bad_strategies
    }

def make_reflection_text(row, reason):
    ticker = row.get("ticker", "")
    strategy = row.get("strategy", "")
    profit = safe_float(row.get("profit_rate")) * 100

    if reason == "POSSIBLE_FALSE_STOP":
        return f"{ticker}: small loss {profit:.2f}%. Possible false stop. Review recovery score before exiting."
    if reason == "STOP_LOSS":
        return f"{ticker}: stop loss {profit:.2f}%. Entry quality or market filter may be weak."
    if reason == "BEAR_MARKET_ENTRY":
        return f"{ticker}: loss during bear market. Strategy should be restricted in risk-off conditions."
    if reason == "MOMENTUM_FAILED":
        return f"{ticker}: Momentum strategy failed. Reduce Momentum unless Market Brain confirms momentum day."
    if reason == "BREAKOUT_FAILED":
        return f"{ticker}: Breakout failed. Require volume confirmation and entry-zone validation."
    return f"{ticker}: loss {profit:.2f}% using {strategy}. Needs review."
