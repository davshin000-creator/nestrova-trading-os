"""Risk Manager: pre-trade and post-trade safety checks."""
def allow_new_trade(context: dict) -> tuple[bool, str]:
    if context.get("market_brain") == "RISK_OFF_DAY" and context.get("expected_value", 0) < 0.01:
        return False, "Risk-off day and EV not high enough"
    return True, "Allowed"
