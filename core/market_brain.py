"""Market Brain: decides the current market condition before any buy decision."""
from dataclasses import dataclass

@dataclass
class MarketBrainResult:
    regime: str
    brain: str
    reason: str
    risk_score: float = 0.0

def classify_market(results, market_regime: str = "", btc_change_4h: float = 0.0) -> MarketBrainResult:
    if market_regime == "bear" and btc_change_4h < -0.015:
        return MarketBrainResult(market_regime, "RISK_OFF_DAY", "BTC 급락/하락장", 80)
    if btc_change_4h > 0.01:
        return MarketBrainResult(market_regime, "MOMENTUM_DAY", "BTC 상승", 30)
    return MarketBrainResult(market_regime or "unknown", "SELECTIVE_DAY", "선별장", 50)
