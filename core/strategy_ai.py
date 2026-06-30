"""Strategy AI: selects which strategies are allowed today."""
def active_strategies_for_market_brain(market_brain: str):
    mapping = {
        "RISK_OFF_DAY": ["Reversal", "Scalp"],
        "MOMENTUM_DAY": ["Momentum", "Leader"],
        "LEADER_ROTATION_DAY": ["Leader", "Breakout"],
        "BREAKOUT_DAY": ["Breakout", "Momentum"],
        "SCALP_ROTATION_DAY": ["Scalp", "Leader"],
        "SELECTIVE_DAY": ["Leader", "Scalp"],
    }
    return mapping.get(market_brain, ["Leader", "Scalp"])
