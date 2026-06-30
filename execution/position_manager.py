"""Position Manager: manages open position state, MAE/MFE, and holding rules."""
def update_mae_mfe(state: dict, profit_rate: float):
    state["mae"] = min(float(state.get("mae", 0) or 0), profit_rate)
    state["mfe"] = max(float(state.get("mfe", 0) or 0), profit_rate)
    return state
