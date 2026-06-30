# Main.py Integration Snippet

To make the trading bot read `config/strategy_override.json`, add these helper functions near your other helpers in `main.py`.

```python
STRATEGY_OVERRIDE_FILE = "config/strategy_override.json"

def load_strategy_override():
    if not os.path.exists(STRATEGY_OVERRIDE_FILE):
        return {"enabled": False}
    try:
        with open(STRATEGY_OVERRIDE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"enabled": False}

def apply_strategy_override_to_candidate(result):
    override = load_strategy_override()
    if not override.get("enabled"):
        return result

    ticker = result.get("ticker", "")
    strategy = result.get("ev_strategy") or result.get("tournament_winner") or result.get("strategy", "")

    if ticker in override.get("blocked_tickers", []):
        result["rank_score"] -= 999
        result["ai_risk"] = 100
        result["strategy"] += " + OVERRIDE_TICKER_BLOCK"

    for disabled in override.get("disabled_strategies", []):
        if disabled and disabled in strategy:
            result["rank_score"] -= 999
            result["ai_risk"] = 100
            result["strategy"] += f" + OVERRIDE_DISABLE_{disabled}"

    for reduced in override.get("reduced_strategies", []):
        if reduced and reduced in strategy:
            result["rank_score"] -= 25
            result["ai_risk"] = min(100, result.get("ai_risk", 0) + 10)
            result["strategy"] += f" + OVERRIDE_REDUCE_{reduced}"

    for preferred in override.get("preferred_strategies", []):
        if preferred and preferred in strategy:
            result["rank_score"] += 12
            result["ai_confidence"] = min(100, result.get("ai_confidence", 0) + 4)
            result["strategy"] += f" + OVERRIDE_PREFER_{preferred}"

    ev_adjust = float(override.get("ev_min_buy_adjust", 0) or 0)
    if ev_adjust:
        result["expected_value"] = result.get("expected_value", 0) - ev_adjust
        result["strategy"] += f" + OVERRIDE_EV_ADJ({ev_adjust})"

    return result
```

Then inside `find_top_coins`, after the candidate has `expected_value`, `strategy`, and `rank_score`, apply:

```python
results = [apply_strategy_override_to_candidate(r) for r in results]
```

Recommended placement:
- after `apply_strategy_ai_engine`
- after `apply_portfolio_ai`
- before final sorting / return
```
