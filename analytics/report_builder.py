from datetime import datetime

def fmt_pct(x):
    return f"{x:.2f}%"

def build_report(trade_summary, ev_summary, action_plan=None):
    action_plan = action_plan or {}
    lines = []
    lines.append("===== Nestrova Intelligence Report v2 =====")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Realized trades")
    lines.append(f"BUY count: {trade_summary.get('buy_count', 0)}")
    lines.append(f"SELL count: {trade_summary.get('sell_count', 0)}")
    lines.append(f"Win rate: {fmt_pct(trade_summary.get('win_rate', 0))}")
    lines.append(f"Total profit: {fmt_pct(trade_summary.get('total_profit_pct', 0))}")
    lines.append(f"Average profit: {fmt_pct(trade_summary.get('avg_profit_pct', 0))}")
    lines.append(f"Average win: {fmt_pct(trade_summary.get('avg_win_pct', 0))}")
    lines.append(f"Average loss: {fmt_pct(trade_summary.get('avg_loss_pct', 0))}")
    lines.append(f"Best trade: {fmt_pct(trade_summary.get('best_trade_pct', 0))}")
    lines.append(f"Worst trade: {fmt_pct(trade_summary.get('worst_trade_pct', 0))}")
    lines.append("")
    lines.append("## Worst tickers")
    for row in trade_summary.get("by_ticker", [])[:10]:
        lines.append(f"- {row['name']}: total {fmt_pct(row['total_pct'])}, avg {fmt_pct(row['avg_pct'])}, count {row['count']}, win {fmt_pct(row['win_rate'])}")
    lines.append("")
    lines.append("## Worst strategies")
    for row in trade_summary.get("by_strategy", [])[:10]:
        lines.append(f"- {row['name']}: total {fmt_pct(row['total_pct'])}, avg {fmt_pct(row['avg_pct'])}, count {row['count']}, win {fmt_pct(row['win_rate'])}")
    lines.append("")
    lines.append("## Expected value")
    lines.append(f"EV rows: {ev_summary.get('count', 0)}")
    lines.append(f"Average EV: {fmt_pct(ev_summary.get('avg_ev_pct', 0))}")
    lines.append(f"Low EV candidates: {ev_summary.get('low_ev_count', 0)}")
    lines.append("")
    lines.append("## Action Plan")
    lines.append(f"Mode: {action_plan.get('mode_recommendation', 'N/A')}")
    lines.append(f"Disable: {', '.join(action_plan.get('disabled_strategies', [])) or 'None'}")
    lines.append(f"Reduce: {', '.join(action_plan.get('reduced_strategies', [])) or 'None'}")
    lines.append(f"Prefer: {', '.join(action_plan.get('preferred_strategies', [])) or 'None'}")
    lines.append(f"Blocked tickers: {', '.join(action_plan.get('blocked_tickers', [])) or 'None'}")
    for note in action_plan.get("notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines)
