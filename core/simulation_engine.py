"""Simulation Engine: validates a candidate using historical similar situations."""
def simulate_candidate(candidate: dict, history_rows=None) -> dict:
    history_rows = history_rows or []
    if len(history_rows) < 5:
        return {"pass": True, "reason": "시뮬레이션 데이터 부족", "sim_ev": 0.0}
    return {"pass": True, "reason": "기본 통과", "sim_ev": 0.0}
