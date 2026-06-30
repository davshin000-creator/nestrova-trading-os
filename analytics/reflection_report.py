from datetime import datetime

def build_reflection_report(summary, plan):
    lines = []
    lines.append("===== Nestrova Reflection Report v3 =====")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Loss reason summary")
    for k, v in summary.get("loss_reasons", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Bad strategies")
    for s in summary.get("bad_strategies", [])[:10]:
        lines.append(f"- {s['strategy']}: total {s['total_pct']:.2f}%, avg {s['avg_pct']:.2f}%, count {s['count']}")
    lines.append("")
    lines.append("## Trade reflections")
    for r in summary.get("reflections", [])[-20:]:
        lines.append(f"- {r['time']} {r['ticker']} {r['profit_pct']:.2f}% | {r['reason']} | {r['reflection']}")
    lines.append("")
    lines.append("## Action plan")
    lines.append(f"Mode: {plan.get('mode')}")
    for item in plan.get("strategy_changes", []):
        lines.append(f"- Strategy {item['strategy']}: {item['recommendation']} total {item['total_pct']}%")
    for item in plan.get("exit_changes", []):
        lines.append(f"- Exit: {item}")
    for item in plan.get("market_filter_changes", []):
        lines.append(f"- Market: {item}")
    for note in plan.get("notes", []):
        lines.append(f"- Note: {note}")
    return "\n".join(lines)
