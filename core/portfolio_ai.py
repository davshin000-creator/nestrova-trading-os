"""Portfolio AI: ranks candidates by expected value, risk, and strategy quality."""
def portfolio_score(candidate: dict) -> float:
    ev = float(candidate.get("expected_value", 0) or 0)
    confidence = float(candidate.get("ai_confidence", 0) or 0)
    risk = float(candidate.get("ai_risk", 0) or 0)
    prediction = float(candidate.get("prediction_score", 0) or 0)
    return ev * 1800 + confidence * 0.45 + prediction * 0.35 - risk * 0.40

def rank_candidates(candidates):
    for c in candidates:
        c["portfolio_score"] = portfolio_score(c)
    return sorted(candidates, key=lambda x: x.get("portfolio_score", -999), reverse=True)
