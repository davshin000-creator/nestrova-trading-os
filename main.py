
import csv
import json
import os
from dotenv import load_dotenv

load_dotenv()
import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

import pyupbit
import requests


# =========================
# API SETTINGS
# =========================
ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")  # CoinGecko Demo API key. 없어도 일부 무료 endpoint는 작동 가능.
COINGECKO_ENABLED = True


# =========================
# BOT SETTINGS
# =========================
BTC_TICKER = "KRW-BTC"
INTERVAL = "minute5"

BASE_TOP_VOLUME_COUNT = 100
BOOST_TOP_VOLUME_COUNT = 120
VOLUME_ACCEL_COUNT = 100

BUY_KRW = 500000

SIGNAL_CONFIRM_SECONDS = 60

# Entry position filters
MAX_BUY_ABOVE_WATCH_PRICE = 0.003     # 관찰 시작가보다 +0.3% 이상 비싸면 대기
MIN_PULLBACK_AFTER_WATCH = 0.001      # 관찰 중 최소 -0.1% 눌림 확인
REBOUND_AFTER_PULLBACK = 0.0005       # 관찰 저점 대비 +0.05% 반등 확인
WATCH_TIMEOUT_MINUTES = 20
WATCH_LOW_REFRESH_LIMIT_MINUTES = 8

# Multi-watch / flexible entry
MULTI_WATCH_TOP_N = 5                  # TOP5 후보를 동시에 기억
LEADER_NO_PULLBACK_DAILY_CHANGE = 0.08 # 주도주는 눌림 없어도 진입 허용 기준
LEADER_NO_PULLBACK_RS = 0.025
LEADER_NO_PULLBACK_VOLUME_ACCEL = 2.0
LEADER_MAX_BUY_ABOVE_WATCH_PRICE = 0.006

# Exit management
TAKE_PROFIT = 0.01
TRAILING_START_PROFIT = 0.005
TRAILING_DROP = -0.0025

BOOST_TAKE_PROFIT = 0.018
BOOST_TRAILING_START_PROFIT = 0.008
BOOST_TRAILING_DROP = -0.0035

STOP_LOSS = -0.02
EARLY_STRENGTH_CHECK_LOSS = -0.005
EARLY_STRENGTH_CHECK_MINUTES = 15

BREAKEVEN_TRIGGER = 0.0035
BREAKEVEN_EXIT = 0.001

MAX_HOLD_HOURS = 4

# Regular entry filters
MIN_PULLBACK_FROM_HIGH = 0.005
BOOST_MIN_PULLBACK_FROM_HIGH = 0.003
MAX_PULLBACK_FROM_HIGH = 0.025

EARLY_LEADER_DAILY_MIN = 0.03
EARLY_LEADER_DAILY_MAX = 0.12
MAX_DAILY_CHANGE_BUY = 0.15

# Leader Mode 2.0
LEADER2_DAILY_CHANGE_MIN = 0.08
LEADER2_MAX_DAILY_CHANGE = 0.35
LEADER2_VOLUME_ACCEL_MIN = 2.0
LEADER2_RELATIVE_STRENGTH_MIN = 0.02

# Learning
AUTO_LEARNING_LIMIT = 50
AUTO_LEARNING_ADVANCED_LIMIT = 100
STRATEGY_BONUS_MAX = 20
MARKET_BONUS_MAX = 15
TICKER_BONUS_MAX = 20
HOUR_BONUS_MAX = 10
LEARNING_BLOCK_THRESHOLD = -25
ADVANCED_LEARNING_BONUS_MAX = 20
ENTRY_QUALITY_MIN_COUNT = 2
ENTRY_QUALITY_BONUS_MAX = 15

# CoinGecko
COINGECKO_CACHE_SECONDS = 600
COINGECKO_SCORE_MAX = 20

STATE_FILE = "state.json"
TRADE_LOG_FILE = "trade_log.csv"
ENTRY_ZONE_LOG_FILE = "entry_zone_log.csv"
PREDICTION_LOG_FILE = "candidate_prediction_log.csv"
ENTRY_QUALITY_FILE = "entry_quality.csv"
FILTER_LOG_FILE = "filter_log.csv"
AI_DECISION_LOG_FILE = "ai_decision_log.csv"
RANK_HISTORY_FILE = "rank_history.csv"
CANDIDATE_MEMORY_FILE = "candidate_memory.json"
EXTERNAL_NEWS_FILE = "external_news.csv"  # optional: time,ticker,sentiment,impact

# AI Decision Engine
AI_CONFIDENCE_BUY_THRESHOLD = 86
AI_CONFIDENCE_WATCH_THRESHOLD = 72
AI_RISK_BLOCK_THRESHOLD = 78
AI_MIN_EXPECTED_PROFIT = 0.004
AI_TOP_N = 20

# v5.0 Dynamic Entry Zone / Candidate Prediction
DYNAMIC_ENTRY_ENABLED = True
ENTRY_ZONE_LOOKBACK = 48
ENTRY_ZONE_ATR_MULTIPLIER = 0.35
ENTRY_ZONE_MIN_DISCOUNT = 0.0015
ENTRY_ZONE_MAX_DISCOUNT = 0.012
ENTRY_ZONE_BREAKOUT_ALLOW_CONFIDENCE = 92
ENTRY_ZONE_BREAKOUT_ALLOW_TOURNAMENT = 88
PREDICTION_MIN_SCORE_BUY = 72
PREDICTION_STRONG_SCORE = 86
EXPECTED_DRAWDOWN_BLOCK = -0.018
EXPECTED_DRAWDOWN_WARN = -0.010

# AI Engine 2.0
SURVIVAL_MIN_CONFIDENCE = 68
SURVIVAL_MIN_RANK_SCORE = 95
SURVIVAL_MAX_RISK = 85
CANDIDATE_MEMORY_MAX_AGE_HOURS = 24
CANDIDATE_MEMORY_BONUS_MAX = 18
STRATEGY_WINRATE_LOOKBACK = 50
STRATEGY_WINRATE_BONUS_MAX = 18
NEWS_TIME_BONUS_MAX = 18

# Market mode
TREND_DAY_MIN_BTC_4H = 0.003
TREND_DAY_MIN_STRONG_COUNT = 4
ALT_SEASON_STRONG_COUNT = 5

# Leader / memory
LEADER_MEMORY_LOOKBACK_HOURS = 3
LEADER_MEMORY_MIN_COUNT = 2
LEADER_MEMORY_BONUS_MAX = 20

# Momentum
MOMENTUM_ACCEL_BONUS_MAX = 20
VOLUME_ACCEL_SPEED_BONUS_MAX = 15

# Strategy live learning
TODAY_LEARNING_BONUS_MAX = 20

# Debug / adaptive trading rate controls
MIN_BUY_GAP_HOURS = 24
RELAX_IF_NO_BUY_HOURS = 24
LEADER_IMMEDIATE_MIN_RANK = 180
LEADER_IMMEDIATE_MIN_DAILY = 0.08
LEADER_IMMEDIATE_MIN_VOLUME_ACCEL = 2.0
LEADER_IMMEDIATE_MIN_RS = 0.02
RELAXED_LEARNING_BLOCK_THRESHOLD = -40

LA = ZoneInfo("America/Los_Angeles")
upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)

_coingecko_cache = {
    "time": 0,
    "data": None
}



def check_required_env_keys():
    missing = []
    for name, value in [
        ("UPBIT_ACCESS_KEY", ACCESS_KEY),
        ("UPBIT_SECRET_KEY", SECRET_KEY),
    ]:
        if not value:
            missing.append(name)
    if missing:
        print("⚠️ .env에 필수 키가 없습니다:", ", ".join(missing))
        return False
    return True


# =========================
# BASIC HELPERS
# =========================
def is_boost_time():
    now = datetime.now(LA).time()
    return dt_time(16, 30) <= now <= dt_time(18, 0)


def get_top_volume_count():
    return BOOST_TOP_VOLUME_COUNT if is_boost_time() else BASE_TOP_VOLUME_COUNT


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def default_state():
    return {
        "holding_ticker": None,
        "highest_price": 0,
        "highest_profit_rate": 0,
        "in_trailing_mode": False,
        "buy_time": 0,
        "entry_price": 0,
        "entry_score": 0,
        "entry_rank_score": 0,
        "entry_market": "",
        "entry_strategy": "",
        "entry_boost_mode": False,
        "entry_leader_mode": False,
        "entry_quality_checked": False,
        "watch_ticker": None,
        "watch_score": 0,
        "watch_rank_score": 0,
        "watch_time": 0,
        "watch_strategy": "",
        "watch_market": "",
        "watch_boost_mode": False,
        "watch_leader_mode": False,
        "watch_price": 0,
        "watch_low": 0,
        "watch_low_time": 0,
        "watch_had_pullback": False,
        "watch_list": [],
        "market_mode": "",
        "last_ai_confidence": 0,
        "last_ai_risk": 0,
        "last_ai_expected_profit": 0
    }


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            s = json.load(f)
            base = default_state()
            base.update(s)
            return base
    except Exception:
        return default_state()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def reset_state():
    save_state(default_state())


def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message},
            timeout=10
        )
    except Exception as e:
        print("텔레그램 오류:", e)


def clamp(value, low, high):
    return max(low, min(high, value))


def get_currency(ticker):
    return ticker.split("-")[1]


# =========================
# LOGGING / LEARNING
# =========================
def init_trade_log():
    if not os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "event", "ticker", "market_regime",
                "strategy", "score", "rank_score", "price",
                "profit_rate", "highest_price", "note"
            ])


def write_trade_log(event, ticker, market_regime="", strategy="", score="",
                    rank_score="", price="", profit_rate="", highest_price="", note=""):
    init_trade_log()
    with open(TRADE_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            now_text(), event, ticker, market_regime, strategy,
            score, rank_score, price, profit_rate, highest_price, note
        ])



def init_filter_log():
    if not os.path.exists(FILTER_LOG_FILE):
        with open(FILTER_LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "ticker", "stage", "reason", "market_regime",
                "price", "rank_score", "score", "note"
            ])


def write_filter_log(ticker, stage, reason, market_regime="", price="", rank_score="", score="", note=""):
    init_filter_log()
    with open(FILTER_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            now_text(), ticker, stage, reason, market_regime,
            price, rank_score, score, note
        ])


def get_hours_since_last_buy():
    if not os.path.exists(TRADE_LOG_FILE):
        return 999

    try:
        with open(TRADE_LOG_FILE, "r") as f:
            rows = list(csv.DictReader(f))

        buy_rows = [r for r in rows if r.get("event") == "BUY"]
        if not buy_rows:
            return 999

        last_time = buy_rows[-1].get("time", "")
        last_dt = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - last_dt).total_seconds() / 3600

    except Exception as e:
        print("마지막 매수 시간 확인 오류:", e)
        return 999


def is_relaxed_mode():
    hours = get_hours_since_last_buy()
    return hours >= RELAX_IF_NO_BUY_HOURS


def is_immediate_leader_candidate(result):
    ai_ok = (
        result.get("ai_confidence", 0) >= AI_CONFIDENCE_BUY_THRESHOLD
        and result.get("ai_risk", 100) <= AI_RISK_BLOCK_THRESHOLD
        and result.get("expected_profit", 0) >= AI_MIN_EXPECTED_PROFIT
    )

    leader_ok = (
        result.get("leader2_mode", False)
        and result.get("rank_score", 0) >= LEADER_IMMEDIATE_MIN_RANK
        and result.get("daily_change", 0) >= LEADER_IMMEDIATE_MIN_DAILY
        and result.get("volume_accel", 0) >= LEADER_IMMEDIATE_MIN_VOLUME_ACCEL
        and result.get("relative_strength", 0) >= LEADER_IMMEDIATE_MIN_RS
    )

    return ai_ok or leader_ok


def read_recent_sells(limit=50):
    if not os.path.exists(TRADE_LOG_FILE):
        return []

    sells = []
    try:
        with open(TRADE_LOG_FILE, "r") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            if row.get("event") == "SELL":
                try:
                    sells.append({
                        "time": row.get("time", ""),
                        "ticker": row.get("ticker", ""),
                        "market_regime": row.get("market_regime", ""),
                        "strategy": row.get("strategy", ""),
                        "profit_rate": float(row.get("profit_rate", 0)),
                        "note": row.get("note", "")
                    })
                except Exception:
                    pass
    except Exception as e:
        print("거래기록 읽기 오류:", e)

    return sells[-limit:]


def get_performance_memory(limit=50):
    sells = read_recent_sells(limit)

    ticker_profit = {}
    market_profit = {}

    for x in sells:
        ticker = x["ticker"]
        market = x["market_regime"]
        profit = x["profit_rate"] * 100

        ticker_profit[ticker] = ticker_profit.get(ticker, 0) + profit
        market_profit[market] = market_profit.get(market, 0) + profit

    return {
        "ticker_profit": ticker_profit,
        "market_profit": market_profit,
        "good_tickers": {t for t, p in ticker_profit.items() if p >= 3},
        "bad_tickers": {t for t, p in ticker_profit.items() if p <= -3},
        "weak_markets": {m for m, p in market_profit.items() if p <= -5}
    }


def get_auto_learning_adjustments(limit=AUTO_LEARNING_LIMIT):
    sells = read_recent_sells(limit)
    if not sells:
        return {}

    strategy_profit = {}
    market_profit = {}
    ticker_profit = {}
    hour_profit = {}

    strategy_count = {}
    market_count = {}
    ticker_count = {}
    hour_count = {}

    for row in sells:
        try:
            profit = row["profit_rate"] * 100
            strategy = row.get("strategy", "")
            market = row.get("market_regime", "")
            ticker = row.get("ticker", "")
            hour = row.get("time", "")[11:13]

            for d, c, key in [
                (strategy_profit, strategy_count, strategy),
                (market_profit, market_count, market),
                (ticker_profit, ticker_count, ticker),
                (hour_profit, hour_count, hour),
            ]:
                if not key:
                    continue
                d[key] = d.get(key, 0) + profit
                c[key] = c.get(key, 0) + 1
        except Exception:
            pass

    return {
        "strategy_profit": strategy_profit,
        "strategy_count": strategy_count,
        "market_profit": market_profit,
        "market_count": market_count,
        "ticker_profit": ticker_profit,
        "ticker_count": ticker_count,
        "hour_profit": hour_profit,
        "hour_count": hour_count,
    }


def get_learning_bonus(result, learning):
    if not learning:
        return 0, []

    bonus = 0
    reasons = []

    strategy = result.get("strategy", "")
    market = result.get("market_regime", "")
    ticker = result.get("ticker", "")
    hour = time.strftime("%H")

    sp = learning.get("strategy_profit", {}).get(strategy, 0)
    sc = learning.get("strategy_count", {}).get(strategy, 0)
    if sc >= 3:
        b = clamp(sp * 2, -STRATEGY_BONUS_MAX, STRATEGY_BONUS_MAX)
        bonus += b
        reasons.append(f"전략학습 {b:.1f}")

    mp = learning.get("market_profit", {}).get(market, 0)
    mc = learning.get("market_count", {}).get(market, 0)
    if mc >= 3:
        b = clamp(mp * 2, -MARKET_BONUS_MAX, MARKET_BONUS_MAX)
        bonus += b
        reasons.append(f"시장학습 {b:.1f}")

    tp = learning.get("ticker_profit", {}).get(ticker, 0)
    tc = learning.get("ticker_count", {}).get(ticker, 0)
    if tc >= 2:
        b = clamp(tp * 3, -TICKER_BONUS_MAX, TICKER_BONUS_MAX)
        bonus += b
        reasons.append(f"코인학습 {b:.1f}")

    hp = learning.get("hour_profit", {}).get(hour, 0)
    hc = learning.get("hour_count", {}).get(hour, 0)
    if hc >= 3:
        b = clamp(hp * 2, -HOUR_BONUS_MAX, HOUR_BONUS_MAX)
        bonus += b
        reasons.append(f"시간학습 {b:.1f}")

    return bonus, reasons


def get_advanced_learning_adjustments(limit=AUTO_LEARNING_ADVANCED_LIMIT):
    sells = read_recent_sells(limit)
    if not sells:
        return {}

    strategy_sum, strategy_count = {}, {}
    market_sum, market_count = {}, {}
    ticker_sum, ticker_count = {}, {}
    reason_sum, reason_count = {}, {}

    for row in sells:
        try:
            profit = row["profit_rate"] * 100
            strategy = row.get("strategy", "")
            market = row.get("market_regime", "")
            ticker = row.get("ticker", "")
            note = row.get("note", "")

            if "기본 손절" in note:
                reason = "기본손절"
            elif "강도 약화" in note:
                reason = "강도약화손절"
            elif "브레이크이븐" in note:
                reason = "브레이크이븐"
            elif "트레일링" in note:
                reason = "트레일링"
            elif "목표 익절" in note:
                reason = "목표익절"
            else:
                reason = ""

            for d, c, key in [
                (strategy_sum, strategy_count, strategy),
                (market_sum, market_count, market),
                (ticker_sum, ticker_count, ticker),
                (reason_sum, reason_count, reason),
            ]:
                if not key:
                    continue
                d[key] = d.get(key, 0) + profit
                c[key] = c.get(key, 0) + 1
        except Exception:
            pass

    return {
        "strategy_sum": strategy_sum,
        "strategy_count": strategy_count,
        "market_sum": market_sum,
        "market_count": market_count,
        "ticker_sum": ticker_sum,
        "ticker_count": ticker_count,
        "reason_sum": reason_sum,
        "reason_count": reason_count,
    }


def get_advanced_learning_bonus(result, advanced):
    if not advanced:
        return 0, []

    bonus = 0
    reasons = []

    strategy = result.get("strategy", "")
    market = result.get("market_regime", "")
    ticker = result.get("ticker", "")

    sc = advanced.get("strategy_count", {}).get(strategy, 0)
    ss = advanced.get("strategy_sum", {}).get(strategy, 0)
    if sc >= 3:
        avg = ss / sc
        b = clamp(avg * 6, -ADVANCED_LEARNING_BONUS_MAX, ADVANCED_LEARNING_BONUS_MAX)
        bonus += b
        reasons.append(f"고급전략 {b:.1f}")

    mc = advanced.get("market_count", {}).get(market, 0)
    ms = advanced.get("market_sum", {}).get(market, 0)
    if mc >= 5:
        avg = ms / mc
        b = clamp(avg * 5, -15, 15)
        bonus += b
        reasons.append(f"고급시장 {b:.1f}")

    tc = advanced.get("ticker_count", {}).get(ticker, 0)
    ts = advanced.get("ticker_sum", {}).get(ticker, 0)
    if tc >= 2:
        avg = ts / tc
        b = clamp(avg * 6, -20, 20)
        bonus += b
        reasons.append(f"고급코인 {b:.1f}")

    return bonus, reasons


def init_entry_quality_log():
    if not os.path.exists(ENTRY_QUALITY_FILE):
        with open(ENTRY_QUALITY_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "ticker", "strategy", "market_regime",
                "entry_price", "current_price", "minutes_after_entry",
                "profit_rate", "quality"
            ])


def write_entry_quality_log(ticker, state, price, profit_rate, hold_minutes):
    init_entry_quality_log()

    if profit_rate >= 0.01:
        quality = "good_entry"
    elif profit_rate <= -0.01:
        quality = "bad_entry"
    else:
        quality = "neutral_entry"

    with open(ENTRY_QUALITY_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            now_text(),
            ticker,
            state.get("entry_strategy", ""),
            state.get("entry_market", ""),
            state.get("entry_price", ""),
            price,
            round(hold_minutes, 2),
            profit_rate,
            quality
        ])


def get_entry_quality_learning(limit=100):
    if not os.path.exists(ENTRY_QUALITY_FILE):
        return {}

    try:
        with open(ENTRY_QUALITY_FILE, "r") as f:
            rows = list(csv.DictReader(f))[-limit:]
    except Exception as e:
        print("진입품질 학습 읽기 오류:", e)
        return {}

    strategy_score, strategy_count = {}, {}
    ticker_score, ticker_count = {}, {}

    for row in rows:
        strategy = row.get("strategy", "")
        ticker = row.get("ticker", "")
        quality = row.get("quality", "")

        if quality == "good_entry":
            v = 1
        elif quality == "bad_entry":
            v = -1
        else:
            v = 0

        for d, c, key in [
            (strategy_score, strategy_count, strategy),
            (ticker_score, ticker_count, ticker),
        ]:
            if not key:
                continue
            d[key] = d.get(key, 0) + v
            c[key] = c.get(key, 0) + 1

    return {
        "strategy_score": strategy_score,
        "strategy_count": strategy_count,
        "ticker_score": ticker_score,
        "ticker_count": ticker_count,
    }


def get_entry_quality_bonus(result, quality):
    if not quality:
        return 0, []

    bonus = 0
    reasons = []

    strategy = result.get("strategy", "")
    ticker = result.get("ticker", "")

    sc = quality.get("strategy_count", {}).get(strategy, 0)
    ss = quality.get("strategy_score", {}).get(strategy, 0)
    if sc >= ENTRY_QUALITY_MIN_COUNT:
        avg = ss / sc
        b = clamp(avg * 10, -ENTRY_QUALITY_BONUS_MAX, ENTRY_QUALITY_BONUS_MAX)
        bonus += b
        reasons.append(f"진입전략품질 {b:.1f}")

    tc = quality.get("ticker_count", {}).get(ticker, 0)
    ts = quality.get("ticker_score", {}).get(ticker, 0)
    if tc >= ENTRY_QUALITY_MIN_COUNT:
        avg = ts / tc
        b = clamp(avg * 10, -ENTRY_QUALITY_BONUS_MAX, ENTRY_QUALITY_BONUS_MAX)
        bonus += b
        reasons.append(f"진입코인품질 {b:.1f}")

    return bonus, reasons


def analyze_trade_log(limit=30):
    print("===== 자동 성과 분석 =====")
    sells = read_recent_sells(limit)

    if not sells:
        print("아직 SELL 기록 없음")
        return

    wins = [x for x in sells if x["profit_rate"] > 0]
    losses = [x for x in sells if x["profit_rate"] <= 0]

    win_rate = len(wins) / len(sells) * 100
    total_profit = sum(x["profit_rate"] for x in sells) * 100
    avg_win = sum(x["profit_rate"] for x in wins) / len(wins) * 100 if wins else 0
    avg_loss = sum(x["profit_rate"] for x in losses) / len(losses) * 100 if losses else 0

    consecutive_losses = 0
    for x in reversed(sells):
        if x["profit_rate"] <= 0:
            consecutive_losses += 1
        else:
            break

    print(f"최근 거래수: {len(sells)}")
    print(f"승률: {win_rate:.1f}%")
    print(f"총 수익률: {total_profit:.2f}%")
    print(f"평균 수익: {avg_win:.2f}%")
    print(f"평균 손실: {avg_loss:.2f}%")
    print(f"연속 손실: {consecutive_losses}회")


# =========================
# MARKET DATA
# =========================
def get_balance(currency):
    balances = upbit.get_balances()
    if not isinstance(balances, list):
        return 0

    for b in balances:
        if isinstance(b, dict) and b.get("currency") == currency:
            return float(b.get("balance", 0))
    return 0


def get_avg_buy_price(currency):
    balances = upbit.get_balances()
    if not isinstance(balances, list):
        return 0

    for b in balances:
        if isinstance(b, dict) and b.get("currency") == currency:
            return float(b.get("avg_buy_price", 0))
    return 0


def add_indicators(df):
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()

    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["hist"] = df["macd"] - df["signal"]

    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["vol_ma20"]

    df["volume_15m_sum"] = df["volume"].rolling(3).sum()
    df["volume_prev_15m_sum"] = df["volume_15m_sum"].shift(3)
    df["volume_accel"] = df["volume_15m_sum"] / df["volume_prev_15m_sum"]

    df["change_15m"] = (df["close"] - df["close"].shift(3)) / df["close"].shift(3)
    df["change_1h"] = (df["close"] - df["close"].shift(12)) / df["close"].shift(12)
    df["change_4h"] = (df["close"] - df["close"].shift(48)) / df["close"].shift(48)

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


def get_market_data(ticker, interval=INTERVAL, count=120):
    df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
    if df is None or len(df) < 100:
        return None
    return add_indicators(df)


def get_daily_change(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
        if df is None or len(df) < 2:
            return 0

        prev_close = float(df.iloc[-2]["close"])
        current_close = float(df.iloc[-1]["close"])

        if prev_close <= 0:
            return 0

        return (current_close - prev_close) / prev_close
    except Exception:
        return 0


def get_weekly_context(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=168)
        if df is None or len(df) < 120:
            return None

        current = float(df.iloc[-1]["close"])
        high_7d = float(df["high"].max())
        low_7d = float(df["low"].min())

        close_24h_ago = float(df.iloc[-24]["close"])
        close_3d_ago = float(df.iloc[-72]["close"])

        change_24h = (current - close_24h_ago) / close_24h_ago
        change_3d = (current - close_3d_ago) / close_3d_ago

        volume_24h = float(df["volume"].iloc[-24:].sum())
        volume_prev_24h = float(df["volume"].iloc[-48:-24].sum())
        volume_24h_accel = volume_24h / max(volume_prev_24h, 1)

        distance_from_7d_high = (high_7d - current) / high_7d
        distance_from_7d_low = (current - low_7d) / low_7d

        early_weekly_leader = (
            0.05 <= distance_from_7d_low <= 0.25
            and 0.02 <= change_24h <= 0.12
            and volume_24h_accel >= 1.8
            and distance_from_7d_high >= 0.08
        )

        overheated_weekly = (
            distance_from_7d_low >= 0.50
            or change_24h >= 0.15
            or distance_from_7d_high <= 0.02
        )

        return {
            "change_24h": change_24h,
            "change_3d": change_3d,
            "volume_24h_accel": volume_24h_accel,
            "distance_from_7d_high": distance_from_7d_high,
            "distance_from_7d_low": distance_from_7d_low,
            "early_weekly_leader": early_weekly_leader,
            "overheated_weekly": overheated_weekly
        }
    except Exception as e:
        print(f"{ticker} 7일 분석 오류:", e)
        return None


def get_candidate_tickers():
    tickers = pyupbit.get_tickers(fiat="KRW")
    volume_list = []
    volume_accel_list = []

    print(f"기본 거래대금 후보 수: {get_top_volume_count()}")
    print(f"거래대금 증가율 후보 수: {VOLUME_ACCEL_COUNT}")
    print(f"부스터 모드: {is_boost_time()}")

    for ticker in tickers:
        try:
            if ticker == "KRW-USDT":
                continue

            df = pyupbit.get_ohlcv(ticker, interval="minute60", count=4)
            if df is None or len(df) < 4:
                continue

            current_value = float(df.iloc[-1]["close"] * df.iloc[-1]["volume"])
            prev_value = float(df.iloc[-2]["close"] * df.iloc[-2]["volume"])
            prev2_value = float(df.iloc[-3]["close"] * df.iloc[-3]["volume"])

            base_prev = max((prev_value + prev2_value) / 2, 1)
            value_accel = current_value / base_prev

            volume_list.append((ticker, current_value))
            volume_accel_list.append((ticker, value_accel, current_value))

            time.sleep(0.03)

        except Exception as e:
            print(f"{ticker} 후보 조회 에러:", e)

    volume_list = sorted(volume_list, key=lambda x: x[1], reverse=True)
    volume_accel_list = sorted(volume_accel_list, key=lambda x: x[1], reverse=True)

    top_volume = [x[0] for x in volume_list[:get_top_volume_count()]]
    top_accel = [x[0] for x in volume_accel_list[:VOLUME_ACCEL_COUNT]]

    candidates = list(dict.fromkeys(top_volume + top_accel))

    print("===== 거래대금 TOP 후보 =====")
    for i, (ticker, value) in enumerate(volume_list[:10], start=1):
        print(f"{i}. {ticker} | 거래대금 {value:,.0f}")

    print("===== 거래대금 증가율 TOP 후보 =====")
    for i, (ticker, accel, value) in enumerate(volume_accel_list[:10], start=1):
        print(f"{i}. {ticker} | 증가율 {accel:.2f}배 | 거래대금 {value:,.0f}")

    print(f"최종 후보 수: {len(candidates)}")
    return candidates


def get_btc_data():
    df = get_market_data(BTC_TICKER)
    if df is None:
        write_filter_log(ticker, "score_ticker", "데이터 부족")
        return None

    last = df.iloc[-2]
    return {
        "btc_change_4h": float(last["change_4h"]),
        "btc_ema20": float(last["ema20"]),
        "btc_ema50": float(last["ema50"]),
        "btc_macd_positive": bool(last["macd"] > last["signal"])
    }


def detect_market_regime():
    btc = get_btc_data()
    if btc is None:
        return "sideways", 0

    btc_change_4h = btc["btc_change_4h"]

    if (
        btc_change_4h >= 0.005
        and btc["btc_ema20"] > btc["btc_ema50"]
        and btc["btc_macd_positive"]
    ):
        return "bull", btc_change_4h

    if btc_change_4h <= -0.01:
        return "bear", btc_change_4h

    return "sideways", btc_change_4h


# =========================
# COINGECKO
# =========================
def coingecko_get(path, params=None):
    if not COINGECKO_ENABLED:
        return None

    url = "https://api.coingecko.com/api/v3" + path
    headers = {
        "accept": "application/json",
        "User-Agent": "upbit-ai-trading-bot/1.0"
    }

    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY

    try:
        r = requests.get(url, params=params or {}, headers=headers, timeout=10)

        if r.status_code == 429:
            print("CoinGecko rate limit → 이번 사이클 0점 처리")
            return None

        if r.status_code != 200:
            print(f"CoinGecko 오류 {r.status_code}: {r.text[:120]}")
            return None

        return r.json()

    except Exception as e:
        print("CoinGecko 요청 오류:", e)
        return None


def get_coingecko_context():
    now = time.time()

    if (
        _coingecko_cache["data"] is not None
        and now - _coingecko_cache["time"] < COINGECKO_CACHE_SECONDS
    ):
        return _coingecko_cache["data"]

    context = {
        "trending_ranks": {},
        "gainer_changes": {},
        "category_scores": {},
        "category_reasons": {}
    }

    trending = coingecko_get("/search/trending")
    if isinstance(trending, dict):
        coins = trending.get("coins", [])
        for idx, item in enumerate(coins, start=1):
            coin = item.get("item", {})
            symbol = str(coin.get("symbol", "")).upper()
            if symbol:
                context["trending_ranks"][symbol] = idx

    markets = coingecko_get(
        "/coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "price_change_percentage": "24h,7d"
        }
    )

    if isinstance(markets, list):
        for coin in markets:
            symbol = str(coin.get("symbol", "")).upper()
            change_24h = coin.get("price_change_percentage_24h")
            if symbol and change_24h is not None:
                try:
                    context["gainer_changes"][symbol] = float(change_24h)
                except Exception:
                    pass

    categories = coingecko_get("/coins/categories")
    strong_categories = []
    weak_categories = []

    if isinstance(categories, list):
        for cat in categories:
            try:
                cat_id = cat.get("id")
                cat_name = cat.get("name", "")
                change = float(cat.get("market_cap_change_24h", 0) or 0)

                if not cat_id:
                    continue

                if change >= 3:
                    strong_categories.append((cat_id, cat_name, change))
                elif change <= -3:
                    weak_categories.append((cat_id, cat_name, change))
            except Exception:
                pass

    selected_categories = strong_categories[:4] + weak_categories[:2]

    for cat_id, cat_name, change in selected_categories:
        cat_markets = coingecko_get(
            "/coins/markets",
            {
                "vs_currency": "usd",
                "category": cat_id,
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "price_change_percentage": "24h"
            }
        )

        if not isinstance(cat_markets, list):
            continue

        for coin in cat_markets:
            symbol = str(coin.get("symbol", "")).upper()
            if not symbol:
                continue

            if change >= 3:
                score = 5 if change < 8 else 8
                reason = f"{cat_name} 강세 {change:.1f}%"
            else:
                score = -3
                reason = f"{cat_name} 약세 {change:.1f}%"

            prev_score = context["category_scores"].get(symbol, 0)
            if abs(score) > abs(prev_score):
                context["category_scores"][symbol] = score
                context["category_reasons"][symbol] = reason

    _coingecko_cache["time"] = now
    _coingecko_cache["data"] = context

    print(
        f"CoinGecko 로드 완료 | "
        f"Trending {len(context['trending_ranks'])}개 | "
        f"Gainers {len(context['gainer_changes'])}개 | "
        f"Category {len(context['category_scores'])}개"
    )

    return context


def get_coingecko_bonus(ticker, context):
    if not context:
        return 0, []

    symbol = ticker.replace("KRW-", "").upper()
    bonus = 0
    reasons = []

    rank = context.get("trending_ranks", {}).get(symbol)
    if rank:
        if rank <= 10:
            bonus += 10
            reasons.append("CG트렌딩TOP10")
        elif rank <= 20:
            bonus += 5
            reasons.append("CG트렌딩TOP20")

    change_24h = context.get("gainer_changes", {}).get(symbol)
    if change_24h is not None:
        if 5 <= change_24h < 10:
            bonus += 3
            reasons.append(f"CG24h상승 {change_24h:.1f}%")
        elif 10 <= change_24h < 20:
            bonus += 5
            reasons.append(f"CG24h강세 {change_24h:.1f}%")
        elif 20 <= change_24h <= 40:
            bonus += 8
            reasons.append(f"CG24h주도 {change_24h:.1f}%")
        elif change_24h > 40:
            bonus -= 5
            reasons.append(f"CG24h과열 {change_24h:.1f}%")

    cat_score = context.get("category_scores", {}).get(symbol, 0)
    if cat_score:
        bonus += cat_score
        cat_reason = context.get("category_reasons", {}).get(symbol, "CG섹터")
        reasons.append(cat_reason)

    bonus = clamp(bonus, -COINGECKO_SCORE_MAX, COINGECKO_SCORE_MAX)
    return bonus, reasons


# =========================
# SCORING
# =========================
def check_strength(ticker):
    df = get_market_data(ticker)
    if df is None:
        return 0, "데이터 부족"

    btc_data = get_btc_data()
    btc_change_4h = btc_data["btc_change_4h"] if btc_data else 0

    last = df.iloc[-2]
    prev = df.iloc[-3]

    change_15m = float(last["change_15m"])
    change_4h = float(last["change_4h"])
    relative_strength = change_4h - btc_change_4h

    ema20_rising = last["ema20"] > df.iloc[-5]["ema20"]
    macd_positive = last["macd"] > last["signal"]
    macd_turning = last["hist"] > prev["hist"]

    volume_ratio = float(last["volume_ratio"]) if last["volume_ratio"] == last["volume_ratio"] else 0
    volume_accel = float(last["volume_accel"]) if last["volume_accel"] == last["volume_accel"] else 0

    score = 0
    reasons = []

    if relative_strength > 0:
        score += 1
        reasons.append("RS+")
    if macd_positive or macd_turning:
        score += 1
        reasons.append("MACD+")
    if ema20_rising:
        score += 1
        reasons.append("EMA20상승")
    if volume_ratio >= 0.8 or volume_accel >= 1.0:
        score += 1
        reasons.append("거래량유지")
    if change_15m > -0.01:
        score += 1
        reasons.append("15분급락아님")

    return score, ", ".join(reasons)


def calculate_rank_score(result):
    if is_boost_time():
        relative_weight = 1700
        change_15m_weight = 2400
        change_1h_weight = 300
        volume_weight = 16
        volume_accel_weight = 28
    else:
        relative_weight = 1200
        change_15m_weight = 1800
        change_1h_weight = 300
        volume_weight = 12
        volume_accel_weight = 22

    rank_score = (
        result["score"] * 10
        + result["relative_strength"] * relative_weight
        + result["change_15m"] * change_15m_weight
        + result["change_1h"] * change_1h_weight
        + min(result["volume_ratio"], 3.0) * volume_weight
        + min(result["volume_accel"], 4.0) * volume_accel_weight
    )

    if result.get("early_leader_mode"):
        rank_score += 35

    if result.get("weekly_leader_mode"):
        rank_score += 40

    if result.get("leader2_mode"):
        rank_score += 45

    return rank_score


def score_ticker(ticker, market_regime, btc_change_4h, performance):
    if ticker in performance["bad_tickers"]:
        print(f"{ticker} 제외: 최근 성과 나쁨")
        write_filter_log(ticker, "score_ticker", "최근 성과 나쁨")
        return None

    df = get_market_data(ticker)
    if df is None:
        write_filter_log(ticker, "score_ticker", "데이터 부족")
        return None

    last = df.iloc[-2]
    prev = df.iloc[-3]

    price = float(last["close"])

    change_15m = float(last["change_15m"])
    change_1h = float(last["change_1h"])
    change_4h = float(last["change_4h"])
    relative_strength = change_4h - btc_change_4h

    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    ema_gap = (price - ema20) / ema20
    ema_uptrend = ema20 > ema50
    ema20_rising = last["ema20"] > df.iloc[-5]["ema20"]

    macd_positive = last["macd"] > last["signal"]
    macd_turning = last["hist"] > prev["hist"]

    volume_ratio = float(last["volume_ratio"]) if last["volume_ratio"] == last["volume_ratio"] else 0
    volume_accel = float(last["volume_accel"]) if last["volume_accel"] == last["volume_accel"] else 0

    volume_burst = volume_ratio > 1.3
    strong_volume = volume_ratio > 1.8
    volume_accel_good = volume_accel > 1.5
    volume_accel_strong = volume_accel > 2.5

    rsi = float(last["rsi"])
    bullish_candle = last["close"] > last["open"]

    recent_high_1h = float(df["high"].iloc[-14:-2].max())
    distance_from_high = (recent_high_1h - price) / recent_high_1h if recent_high_1h > 0 else 0

    daily_change = get_daily_change(ticker)
    weekly = get_weekly_context(ticker)

    weekly_leader_mode = False
    weekly_overheated = False
    weekly_change_24h = 0
    weekly_volume_accel = 0
    weekly_low_dist = 0
    weekly_high_dist = 0

    if weekly:
        weekly_leader_mode = weekly["early_weekly_leader"]
        weekly_overheated = weekly["overheated_weekly"]
        weekly_change_24h = weekly["change_24h"]
        weekly_volume_accel = weekly["volume_24h_accel"]
        weekly_low_dist = weekly["distance_from_7d_low"]
        weekly_high_dist = weekly["distance_from_7d_high"]

    early_leader_mode = (
        EARLY_LEADER_DAILY_MIN <= daily_change <= EARLY_LEADER_DAILY_MAX
        and volume_accel >= 2.0
        and relative_strength > 0
        and change_15m > 0
        and macd_positive
    )

    leader2_mode = (
        LEADER2_DAILY_CHANGE_MIN <= daily_change <= LEADER2_MAX_DAILY_CHANGE
        and volume_accel >= LEADER2_VOLUME_ACCEL_MIN
        and relative_strength >= LEADER2_RELATIVE_STRENGTH_MIN
        and change_15m > 0
        and macd_positive
    )

    if daily_change >= MAX_DAILY_CHANGE_BUY and not leader2_mode:
        print(f"{ticker} 제외: 전일대비 과열 {daily_change * 100:.2f}%")
        write_filter_log(ticker, "score_ticker", "전일대비 과열", market_regime, price, "", "", f"daily {daily_change*100:.2f}%")
        return None

    if weekly_overheated and not leader2_mode:
        print(f"{ticker} 제외: 7일 기준 과열")
        write_filter_log(ticker, "score_ticker", "7일 기준 과열", market_regime, price)
        return None

    if rsi > 88:
        write_filter_log(ticker, "score_ticker", "RSI 과열", market_regime, price, "", "", f"rsi {rsi:.1f}")
        return None

    if not early_leader_mode and not weekly_leader_mode and not leader2_mode:
        min_pullback = BOOST_MIN_PULLBACK_FROM_HIGH if is_boost_time() else MIN_PULLBACK_FROM_HIGH

        if distance_from_high < min_pullback:
            return None
        if distance_from_high > MAX_PULLBACK_FROM_HIGH:
            return None
        if change_15m > 0.04:
            return None
        if change_4h > 0.20:
            return None
    else:
        if not volume_burst:
            return None
        if not macd_positive:
            return None

    if market_regime == "bear" and weekly_leader_mode and not leader2_mode:
        if relative_strength < 0.04 or volume_accel < 2.5 or not volume_accel_strong:
            return None

    score = 0
    strategy = ""

    if leader2_mode:
        strategy = "주도주 예외모드 스캘핑"
        score += 10

        if daily_change >= 0.12:
            score += 2
        if volume_accel_strong:
            score += 2
        if relative_strength >= 0.04:
            score += 2
        if strong_volume:
            score += 1
        if bullish_candle:
            score += 1
        if ema20_rising:
            score += 1
        if macd_turning:
            score += 1

        min_score = 10

    elif weekly_leader_mode:
        strategy = "7일 초기주도 스캘핑"
        score += 9

        if volume_accel_good:
            score += 1
        if volume_accel_strong:
            score += 2
        if relative_strength > 0.02:
            score += 1
        if ema20_rising:
            score += 1
        if bullish_candle:
            score += 1

        min_score = 9

    elif early_leader_mode:
        strategy = "초기 주도주 포착 스캘핑"
        score += 8

        if daily_change >= 0.05:
            score += 1
        if volume_accel_strong:
            score += 2
        if relative_strength > 0.02:
            score += 1
        if ema20_rising:
            score += 1
        if bullish_candle:
            score += 1

        min_score = 8

    elif market_regime == "bull":
        strategy = "상승장 주도주 스캘핑"

        if change_15m <= 0:
            return None

        if change_15m > 0:
            score += 2
        if change_1h > 0.006:
            score += 2
        if change_4h > 0.015:
            score += 2
        if relative_strength > 0.01:
            score += 2
        if ema_uptrend:
            score += 1
        if ema20_rising:
            score += 1
        if macd_positive:
            score += 1
        if macd_turning:
            score += 1
        if volume_burst:
            score += 1
        if strong_volume:
            score += 1
        if volume_accel_good:
            score += 2
        if volume_accel_strong:
            score += 1
        if bullish_candle:
            score += 1

        if change_1h <= 0 or change_4h <= 0 or not macd_positive or not ema20_rising:
            return None

        min_score = 7

    elif market_regime == "sideways":
        strategy = "횡보장 독립강세 스캘핑"

        sideways_independent_strength = (
            relative_strength >= 0.02
            and change_15m > 0
            and change_1h >= 0.005
            and macd_positive
            and ema20_rising
            and volume_accel >= 1.5
        )

        if not sideways_independent_strength:
            return None

        score += 5

        if relative_strength >= 0.03:
            score += 2
        if change_15m >= 0.005:
            score += 1
        if change_1h >= 0.01:
            score += 1
        if volume_burst:
            score += 1
        if strong_volume:
            score += 1
        if volume_accel_good:
            score += 2
        if volume_accel_strong:
            score += 1
        if macd_turning:
            score += 1
        if bullish_candle:
            score += 1
        if 42 <= rsi <= 72:
            score += 1

        if ema_gap > 0.025 or rsi > 78:
            return None

        min_score = 8

    else:
        strategy = "하락장 독립강세 스캘핑"

        independent_strength = (
            change_15m > 0.006
            and change_1h > 0.012
            and relative_strength > 0.035
            and macd_positive
            and ema20_rising
            and volume_burst
            and volume_accel_good
        )

        if not independent_strength:
            return None

        score += 7

        if relative_strength > 0.05:
            score += 2
        if strong_volume:
            score += 1
        if volume_accel_strong:
            score += 2
        if bullish_candle:
            score += 1
        if macd_turning:
            score += 1

        min_score = 9

    if market_regime in performance["weak_markets"] and not leader2_mode:
        min_score += 1

    if score < min_score:
        write_filter_log(ticker, "score_ticker", "점수 부족", market_regime, price, "", score, f"min_score {min_score}")
        return None

    result = {
        "ticker": ticker,
        "price": price,
        "score": score,
        "market_regime": market_regime,
        "strategy": strategy,
        "early_leader_mode": early_leader_mode,
        "weekly_leader_mode": weekly_leader_mode,
        "leader2_mode": leader2_mode,
        "change_15m": change_15m,
        "change_1h": change_1h,
        "change_4h": change_4h,
        "relative_strength": relative_strength,
        "rsi": rsi,
        "ema_gap": ema_gap,
        "ema_uptrend": bool(ema_uptrend),
        "ema20_rising": bool(ema20_rising),
        "macd_positive": bool(macd_positive),
        "macd_turning": bool(macd_turning),
        "volume_ratio": volume_ratio,
        "volume_accel": volume_accel,
        "volume_burst": bool(volume_burst),
        "strong_volume": bool(strong_volume),
        "boost_mode": is_boost_time(),
        "distance_from_high": distance_from_high,
        "daily_change": daily_change,
        "weekly_change_24h": weekly_change_24h,
        "weekly_volume_accel": weekly_volume_accel,
        "weekly_low_dist": weekly_low_dist,
        "weekly_high_dist": weekly_high_dist
    }

    result["rank_score"] = calculate_rank_score(result)

    if ticker in performance["good_tickers"]:
        result["rank_score"] += 10
        result["strategy"] += " + 성과가산"

    if result["boost_mode"]:
        result["strategy"] += " + 5시부스터"

    if result["market_regime"] == "sideways" and not leader2_mode:
        result["rank_score"] -= 5
        result["strategy"] += " + 횡보장약감점"

    if early_leader_mode:
        result["strategy"] += " + 초기주도주"

    if weekly_leader_mode:
        result["rank_score"] += 10
        result["strategy"] += " + 7일초기주도강화"

    if leader2_mode:
        result["rank_score"] += 25
        result["strategy"] += " + 주도주예외"

    return result


# =========================
# SEARCH / WATCH / BUY
# =========================

def init_ai_decision_log():
    if not os.path.exists(AI_DECISION_LOG_FILE):
        with open(AI_DECISION_LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "ticker", "confidence", "risk", "expected_profit",
                "market_mode", "strategy", "rank_score", "ai_reasons"
            ])


def write_ai_decision_log(result):
    init_ai_decision_log()
    with open(AI_DECISION_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            now_text(),
            result.get("ticker", ""),
            round(result.get("ai_confidence", 0), 2),
            round(result.get("ai_risk", 0), 2),
            round(result.get("expected_profit", 0), 4),
            result.get("market_mode", ""),
            result.get("strategy", ""),
            round(result.get("rank_score", 0), 2),
            " | ".join(result.get("ai_reasons", []))
        ])


def init_rank_history():
    if not os.path.exists(RANK_HISTORY_FILE):
        with open(RANK_HISTORY_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "ticker", "rank_position", "rank_score",
                "confidence", "market_mode", "strategy"
            ])


def write_rank_history(results):
    init_rank_history()
    with open(RANK_HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for i, r in enumerate(results[:AI_TOP_N], start=1):
            writer.writerow([
                now_text(),
                r.get("ticker", ""),
                i,
                round(r.get("rank_score", 0), 2),
                round(r.get("ai_confidence", 0), 2),
                r.get("market_mode", ""),
                r.get("strategy", "")
            ])


def get_recent_rank_memory(ticker, lookback_hours=LEADER_MEMORY_LOOKBACK_HOURS):
    if not os.path.exists(RANK_HISTORY_FILE):
        return 0, 999

    try:
        now_dt = datetime.now()
        count = 0
        best_rank = 999

        with open(RANK_HISTORY_FILE, "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows[-500:]:
            if row.get("ticker") != ticker:
                continue

            try:
                t = datetime.strptime(row.get("time", ""), "%Y-%m-%d %H:%M:%S")
                hours = (now_dt - t).total_seconds() / 3600
                if hours <= lookback_hours:
                    count += 1
                    best_rank = min(best_rank, int(float(row.get("rank_position", 999))))
            except Exception:
                pass

        return count, best_rank

    except Exception as e:
        print("Leader memory 읽기 오류:", e)
        return 0, 999


def get_today_strategy_learning(strategy, market_regime):
    sells = read_recent_sells(100)
    if not sells:
        return 0, []

    today = time.strftime("%Y-%m-%d")
    strategy_sum = 0
    strategy_count = 0
    market_sum = 0
    market_count = 0

    for row in sells:
        if not row.get("time", "").startswith(today):
            continue

        profit = row.get("profit_rate", 0) * 100

        if strategy and strategy in row.get("strategy", ""):
            strategy_sum += profit
            strategy_count += 1

        if market_regime and row.get("market_regime", "") == market_regime:
            market_sum += profit
            market_count += 1

    bonus = 0
    reasons = []

    if strategy_count >= 2:
        avg = strategy_sum / strategy_count
        b = clamp(avg * 5, -TODAY_LEARNING_BONUS_MAX, TODAY_LEARNING_BONUS_MAX)
        bonus += b
        reasons.append(f"오늘전략 {b:.1f}")

    if market_count >= 3:
        avg = market_sum / market_count
        b = clamp(avg * 4, -15, 15)
        bonus += b
        reasons.append(f"오늘시장 {b:.1f}")

    return bonus, reasons


def detect_market_mode_from_results(results, market_regime, btc_change_4h):
    if not results:
        if market_regime == "bear":
            return "BEAR"
        return "RANGE"

    strong_count = 0
    leader_count = 0

    for r in results[:20]:
        if r.get("daily_change", 0) >= 0.04 and r.get("relative_strength", 0) >= 0.015:
            strong_count += 1
        if r.get("leader2_mode") or r.get("daily_change", 0) >= 0.08:
            leader_count += 1

    if market_regime == "bear" and strong_count < 3:
        return "BEAR"

    if leader_count >= TREND_DAY_MIN_STRONG_COUNT or strong_count >= ALT_SEASON_STRONG_COUNT:
        return "ALT_TREND"

    if btc_change_4h >= TREND_DAY_MIN_BTC_4H and strong_count >= 3:
        return "TREND"

    return "RANGE"


def get_momentum_acceleration(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=12)
        if df is None or len(df) < 10:
            return 0, 0

        c = df["close"]

        change_5m = (float(c.iloc[-1]) - float(c.iloc[-2])) / float(c.iloc[-2])
        change_15m = (float(c.iloc[-1]) - float(c.iloc[-4])) / float(c.iloc[-4])
        change_30m = (float(c.iloc[-1]) - float(c.iloc[-7])) / float(c.iloc[-7])

        accel = change_5m * 3 + change_15m * 2 - abs(min(change_30m, 0))

        vol_now = float(df["volume"].iloc[-3:].sum())
        vol_prev = float(df["volume"].iloc[-6:-3].sum())
        vol_speed = vol_now / max(vol_prev, 1)

        return accel, vol_speed

    except Exception as e:
        print(f"{ticker} momentum accel 오류:", e)
        return 0, 0


def calculate_ai_confidence(result, market_mode):
    confidence = 50
    risk = 25
    expected_profit = 0.003
    reasons = []

    # Core strength
    rs = result.get("relative_strength", 0)
    if rs >= 0.05:
        confidence += 18
        expected_profit += 0.008
        reasons.append("RS강함 +18")
    elif rs >= 0.03:
        confidence += 13
        expected_profit += 0.006
        reasons.append("RS양호 +13")
    elif rs >= 0.015:
        confidence += 7
        expected_profit += 0.003
        reasons.append("RS보통 +7")
    elif rs < 0:
        confidence -= 10
        risk += 10
        reasons.append("RS약함 -10")

    # Momentum
    if result.get("change_15m", 0) > 0:
        confidence += 6
        reasons.append("15분상승 +6")
    else:
        confidence -= 5
        risk += 5
        reasons.append("15분약세 -5")

    if result.get("change_1h", 0) >= 0.01:
        confidence += 8
        expected_profit += 0.004
        reasons.append("1시간강세 +8")
    elif result.get("change_1h", 0) < 0:
        confidence -= 6
        risk += 6
        reasons.append("1시간약세 -6")

    # Volume
    va = result.get("volume_accel", 0)
    if va >= 3:
        confidence += 14
        expected_profit += 0.006
        reasons.append("거래량가속강함 +14")
    elif va >= 2:
        confidence += 10
        expected_profit += 0.004
        reasons.append("거래량가속 +10")
    elif va >= 1.3:
        confidence += 5
        reasons.append("거래량양호 +5")
    else:
        confidence -= 5
        reasons.append("거래량부족 -5")

    # Indicators
    if result.get("macd_positive"):
        confidence += 7
        reasons.append("MACD+ +7")
    else:
        confidence -= 6
        risk += 6
        reasons.append("MACD- -6")

    if result.get("ema20_rising"):
        confidence += 7
        reasons.append("EMA상승 +7")

    # Leader modes
    if result.get("leader2_mode"):
        confidence += 22
        expected_profit += 0.01
        reasons.append("Leader2 +22")
    elif result.get("weekly_leader_mode"):
        confidence += 15
        expected_profit += 0.006
        reasons.append("7일초기주도 +15")
    elif result.get("early_leader_mode"):
        confidence += 12
        expected_profit += 0.005
        reasons.append("초기주도 +12")

    # CoinGecko / learning
    cg = result.get("coingecko_bonus", 0)
    if cg:
        confidence += cg * 0.7
        expected_profit += max(cg, 0) / 1000
        reasons.append(f"CoinGecko {cg:.1f}")

    learn = result.get("learning_bonus", 0)
    adv = result.get("advanced_bonus", 0)
    entry = result.get("entry_quality_bonus", 0)

    confidence += learn * 0.4 + adv * 0.5 + entry * 0.6
    if learn or adv or entry:
        reasons.append(f"학습반영 {learn:.1f}/{adv:.1f}/{entry:.1f}")

    # Momentum acceleration
    accel, vol_speed = get_momentum_acceleration(result["ticker"])
    result["momentum_accel"] = accel
    result["volume_speed"] = vol_speed

    if accel >= 0.01:
        b = min(accel * 600, MOMENTUM_ACCEL_BONUS_MAX)
        confidence += b
        expected_profit += 0.006
        reasons.append(f"모멘텀가속 {b:.1f}")
    elif accel < -0.004:
        confidence -= 8
        risk += 8
        reasons.append("모멘텀둔화 -8")

    if vol_speed >= 2:
        b = min((vol_speed - 1) * 7, VOLUME_ACCEL_SPEED_BONUS_MAX)
        confidence += b
        expected_profit += 0.004
        reasons.append(f"거래량속도 {b:.1f}")

    # Leader memory
    count, best_rank = get_recent_rank_memory(result["ticker"])
    if count >= LEADER_MEMORY_MIN_COUNT:
        b = min(count * 5 + max(0, 6 - best_rank) * 2, LEADER_MEMORY_BONUS_MAX)
        confidence += b
        expected_profit += 0.004
        result["leader_memory_count"] = count
        result["leader_memory_best_rank"] = best_rank
        reasons.append(f"LeaderMemory {b:.1f}")

    # Market mode adjustment
    if market_mode == "ALT_TREND":
        if result.get("leader2_mode") or result.get("daily_change", 0) >= 0.05:
            confidence += 12
            expected_profit += 0.005
            reasons.append("알트추세장 +12")
        else:
            confidence += 3
    elif market_mode == "TREND":
        confidence += 5
        reasons.append("추세장 +5")
    elif market_mode == "BEAR":
        if not result.get("leader2_mode"):
            confidence -= 10
            risk += 12
            reasons.append("하락장위험 -10")
    else:
        if result.get("leader2_mode"):
            confidence += 6
            reasons.append("횡보장주도 +6")

    # Today live learning
    today_bonus, today_reasons = get_today_strategy_learning(result.get("strategy", ""), result.get("market_regime", ""))
    if today_bonus:
        confidence += today_bonus
        reasons.extend(today_reasons)

    # Real-time strategy win-rate learning
    winrate_bonus, winrate_reasons = get_recent_strategy_winrate_bonus(
        result.get("strategy", ""),
        result.get("market_regime", "")
    )
    if winrate_bonus:
        confidence += winrate_bonus
        reasons.extend(winrate_reasons)

    # Candidate survival / leader memory from persistent candidate memory
    memory_bonus, memory_reasons = get_candidate_memory_bonus(result["ticker"])
    if memory_bonus:
        confidence += memory_bonus
        expected_profit += memory_bonus / 2000
        reasons.extend(memory_reasons)

    # Optional news/event time-weight hook
    news_bonus, news_reasons = get_news_time_weight_bonus(result["ticker"])
    if news_bonus:
        confidence += news_bonus
        expected_profit += max(news_bonus, 0) / 1500
        if news_bonus < 0:
            risk += abs(news_bonus)
        reasons.extend(news_reasons)

    # Survival candidates should not be killed early; AI decides with risk/confidence
    if result.get("survival_candidate"):
        confidence += 4
        reasons.append("후보생존 +4")

    # Risk
    rsi = result.get("rsi", 50)
    if rsi >= 86:
        risk += 25
        confidence -= 12
        reasons.append("RSI초과열")
    elif rsi >= 78:
        risk += 12
        confidence -= 4
        reasons.append("RSI과열주의")

    if result.get("daily_change", 0) >= 0.30:
        risk += 18
        confidence -= 5
        reasons.append("일봉과열위험")

    if result.get("weekly_high_dist", 1) <= 0.02 and not result.get("leader2_mode"):
        risk += 12
        confidence -= 6
        reasons.append("7일고점근처위험")

    if result.get("market_regime") == "bear" and not result.get("leader2_mode"):
        risk += 10

    # Expected profit final
    expected_profit += max(result.get("relative_strength", 0), 0) * 0.25
    expected_profit += max(result.get("change_15m", 0), 0) * 0.35
    expected_profit += max(result.get("volume_accel", 0) - 1, 0) * 0.001

    confidence = clamp(confidence, 0, 100)
    risk = clamp(risk, 0, 100)
    expected_profit = clamp(expected_profit, -0.02, 0.06)

    return confidence, risk, expected_profit, reasons


def apply_ai_decision_engine(results, market_mode):
    scored = []

    for r in results:
        confidence, risk, expected_profit, reasons = calculate_ai_confidence(r, market_mode)

        r["ai_confidence"] = confidence
        r["ai_risk"] = risk
        r["expected_profit"] = expected_profit
        r["ai_reasons"] = reasons
        r["market_mode"] = market_mode

        # AI confidence is additive, not a hard filter
        r["rank_score"] += confidence * 1.2
        r["rank_score"] -= risk * 0.4
        r["rank_score"] += expected_profit * 1000

        if confidence >= AI_CONFIDENCE_BUY_THRESHOLD:
            r["strategy"] += f" + AI강신호({confidence:.0f})"
        elif confidence >= AI_CONFIDENCE_WATCH_THRESHOLD:
            r["strategy"] += f" + AI관찰({confidence:.0f})"
        else:
            r["strategy"] += f" + AI약함({confidence:.0f})"

        if r.get("survival_candidate"):
            if confidence >= SURVIVAL_MIN_CONFIDENCE and risk <= SURVIVAL_MAX_RISK:
                r["strategy"] += " + 생존통과"
            else:
                r["strategy"] += " + 생존관찰"

        write_ai_decision_log(r)
        scored.append(r)

    scored = sorted(
        scored,
        key=lambda x: (
            x.get("ai_confidence", 0) - x.get("ai_risk", 0) * 0.35 + x.get("expected_profit", 0) * 100,
            x.get("rank_score", 0)
        ),
        reverse=True
    )

    return scored



def load_candidate_memory():
    if not os.path.exists(CANDIDATE_MEMORY_FILE):
        return {}

    try:
        with open(CANDIDATE_MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("candidate memory 읽기 오류:", e)
        return {}


def save_candidate_memory(memory):
    try:
        with open(CANDIDATE_MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print("candidate memory 저장 오류:", e)


def update_candidate_memory(results):
    memory = load_candidate_memory()
    now_ts = time.time()

    # 오래된 후보 정리
    clean = {}
    for ticker, info in memory.items():
        last_seen = float(info.get("last_seen", 0))
        age_hours = (now_ts - last_seen) / 3600 if last_seen else 999
        if age_hours <= CANDIDATE_MEMORY_MAX_AGE_HOURS:
            clean[ticker] = info

    for rank, r in enumerate(results[:AI_TOP_N], start=1):
        ticker = r.get("ticker")
        if not ticker:
            continue

        info = clean.get(ticker, {})
        info["seen_count"] = int(info.get("seen_count", 0)) + 1
        info["last_seen"] = now_ts
        info["best_rank"] = min(int(info.get("best_rank", 999)), rank)
        info["last_rank"] = rank
        info["last_confidence"] = r.get("ai_confidence", 0)
        info["last_risk"] = r.get("ai_risk", 0)
        info["last_strategy"] = r.get("strategy", "")
        clean[ticker] = info

    save_candidate_memory(clean)


def get_candidate_memory_bonus(ticker):
    memory = load_candidate_memory()
    info = memory.get(ticker)

    if not info:
        return 0, []

    now_ts = time.time()
    last_seen = float(info.get("last_seen", 0))
    age_hours = (now_ts - last_seen) / 3600 if last_seen else 999

    if age_hours > CANDIDATE_MEMORY_MAX_AGE_HOURS:
        return 0, []

    seen_count = int(info.get("seen_count", 0))
    best_rank = int(info.get("best_rank", 999))
    last_conf = float(info.get("last_confidence", 0))

    bonus = 0
    reasons = []

    if seen_count >= 2:
        b = min(seen_count * 3, 12)
        bonus += b
        reasons.append(f"후보지속 {b:.1f}")

    if best_rank <= 5:
        b = max(0, 7 - best_rank) * 1.5
        bonus += b
        reasons.append(f"상위권기억 {b:.1f}")

    if last_conf >= 80:
        b = 4
        bonus += b
        reasons.append("이전AI강함 +4")

    bonus = clamp(bonus, 0, CANDIDATE_MEMORY_BONUS_MAX)
    return bonus, reasons


def get_recent_strategy_winrate_bonus(strategy, market_regime, lookback=STRATEGY_WINRATE_LOOKBACK):
    sells = read_recent_sells(lookback)

    if not sells:
        return 0, []

    strategy_hits = []
    market_hits = []

    # strategy 문자열은 추가 태그가 많아서 포함 여부로 판단
    base_strategy = strategy.split(" + ")[0] if strategy else ""

    for row in sells:
        profit = row.get("profit_rate", 0)

        if base_strategy and base_strategy in row.get("strategy", ""):
            strategy_hits.append(profit)

        if market_regime and row.get("market_regime", "") == market_regime:
            market_hits.append(profit)

    bonus = 0
    reasons = []

    if len(strategy_hits) >= 3:
        win_rate = len([x for x in strategy_hits if x > 0]) / len(strategy_hits)
        avg = sum(strategy_hits) / len(strategy_hits) * 100

        b = (win_rate - 0.5) * 30 + avg * 2
        b = clamp(b, -STRATEGY_WINRATE_BONUS_MAX, STRATEGY_WINRATE_BONUS_MAX)
        bonus += b
        reasons.append(f"전략승률 {win_rate*100:.0f}% {b:.1f}")

    if len(market_hits) >= 5:
        win_rate = len([x for x in market_hits if x > 0]) / len(market_hits)
        avg = sum(market_hits) / len(market_hits) * 100

        b = (win_rate - 0.5) * 20 + avg * 1.5
        b = clamp(b, -12, 12)
        bonus += b
        reasons.append(f"시장승률 {win_rate*100:.0f}% {b:.1f}")

    return bonus, reasons


def get_news_time_weight_bonus(ticker):
    """
    Optional external news/event hook.
    CSV format:
    time,ticker,sentiment,impact
    2026-06-23 12:00:00,KRW-ABC,positive,10
    sentiment: positive / negative
    impact: 1~20
    """
    if not os.path.exists(EXTERNAL_NEWS_FILE):
        return 0, []

    try:
        with open(EXTERNAL_NEWS_FILE, "r") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print("뉴스 파일 읽기 오류:", e)
        return 0, []

    now_dt = datetime.now()
    bonus = 0
    reasons = []

    symbol = ticker.replace("KRW-", "").upper()

    for row in rows[-200:]:
        row_ticker = row.get("ticker", "").upper()
        if row_ticker not in {ticker.upper(), symbol}:
            continue

        try:
            t = datetime.strptime(row.get("time", ""), "%Y-%m-%d %H:%M:%S")
            hours = (now_dt - t).total_seconds() / 3600
            if hours < 0 or hours > 24:
                continue

            impact = float(row.get("impact", 0))
            sentiment = row.get("sentiment", "").lower()

            if hours <= 0.25:
                weight = 1.0
            elif hours <= 0.5:
                weight = 0.8
            elif hours <= 1:
                weight = 0.6
            elif hours <= 3:
                weight = 0.35
            elif hours <= 6:
                weight = 0.2
            else:
                weight = 0.08

            b = impact * weight

            if sentiment == "negative":
                b = -b

            bonus += b
            reasons.append(f"뉴스시간가중 {b:.1f}")

        except Exception:
            pass

    bonus = clamp(bonus, -NEWS_TIME_BONUS_MAX, NEWS_TIME_BONUS_MAX)
    return bonus, reasons


def build_survival_candidate(ticker, market_regime, btc_change_4h, performance):
    """
    후보 생존 시스템:
    기존 score_ticker에서 하나의 조건 때문에 탈락한 코인도
    기본 데이터가 괜찮으면 AI Decision Engine까지 보내서 종합 평가한다.
    """
    try:
        if ticker in performance.get("bad_tickers", set()):
            # 너무 나쁜 코인은 생존 후보에서도 제외
            return None

        df = get_market_data(ticker)
        if df is None:
            write_filter_log(ticker, "survival", "데이터 부족")
            return None

        last = df.iloc[-2]
        prev = df.iloc[-3]

        price = float(last["close"])

        change_15m = float(last["change_15m"])
        change_1h = float(last["change_1h"])
        change_4h = float(last["change_4h"])
        relative_strength = change_4h - btc_change_4h

        ema20 = float(last["ema20"])
        ema50 = float(last["ema50"])
        ema_gap = (price - ema20) / ema20
        ema_uptrend = ema20 > ema50
        ema20_rising = last["ema20"] > df.iloc[-5]["ema20"]

        macd_positive = last["macd"] > last["signal"]
        macd_turning = last["hist"] > prev["hist"]

        volume_ratio = float(last["volume_ratio"]) if last["volume_ratio"] == last["volume_ratio"] else 0
        volume_accel = float(last["volume_accel"]) if last["volume_accel"] == last["volume_accel"] else 0

        volume_burst = volume_ratio > 1.3
        strong_volume = volume_ratio > 1.8

        rsi = float(last["rsi"])

        daily_change = get_daily_change(ticker)
        weekly = get_weekly_context(ticker)

        weekly_change_24h = 0
        weekly_volume_accel = 0
        weekly_low_dist = 0
        weekly_high_dist = 0
        weekly_leader_mode = False

        if weekly:
            weekly_leader_mode = weekly.get("early_weekly_leader", False)
            weekly_change_24h = weekly.get("change_24h", 0)
            weekly_volume_accel = weekly.get("volume_24h_accel", 0)
            weekly_low_dist = weekly.get("distance_from_7d_low", 0)
            weekly_high_dist = weekly.get("distance_from_7d_high", 0)

        leader2_mode = (
            LEADER2_DAILY_CHANGE_MIN <= daily_change <= LEADER2_MAX_DAILY_CHANGE
            and volume_accel >= LEADER2_VOLUME_ACCEL_MIN
            and relative_strength >= LEADER2_RELATIVE_STRENGTH_MIN
            and change_15m > 0
            and macd_positive
        )

        early_leader_mode = (
            EARLY_LEADER_DAILY_MIN <= daily_change <= EARLY_LEADER_DAILY_MAX
            and volume_accel >= 1.5
            and relative_strength > 0
            and change_15m > 0
        )

        # 최소 생존 조건: 완전 약한 코인은 제외
        if (
            relative_strength < -0.015
            and change_15m <= 0
            and volume_accel < 1.2
            and not leader2_mode
        ):
            write_filter_log(ticker, "survival", "최소 생존 조건 부족", market_regime, price, "", "", f"RS {relative_strength:.3f}")
            return None

        score = 0

        if relative_strength > 0:
            score += 2
        if change_15m > 0:
            score += 2
        if change_1h > 0:
            score += 1
        if volume_accel >= 1.5:
            score += 2
        if volume_accel >= 2.5:
            score += 2
        if macd_positive:
            score += 1
        if macd_turning:
            score += 1
        if ema20_rising:
            score += 1
        if leader2_mode:
            score += 5
        if weekly_leader_mode:
            score += 3

        result = {
            "ticker": ticker,
            "price": price,
            "score": score,
            "market_regime": market_regime,
            "strategy": "AI후보생존 스캘핑",
            "early_leader_mode": early_leader_mode,
            "weekly_leader_mode": weekly_leader_mode,
            "leader2_mode": leader2_mode,
            "change_15m": change_15m,
            "change_1h": change_1h,
            "change_4h": change_4h,
            "relative_strength": relative_strength,
            "rsi": rsi,
            "ema_gap": ema_gap,
            "ema_uptrend": bool(ema_uptrend),
            "ema20_rising": bool(ema20_rising),
            "macd_positive": bool(macd_positive),
            "macd_turning": bool(macd_turning),
            "volume_ratio": volume_ratio,
            "volume_accel": volume_accel,
            "volume_burst": bool(volume_burst),
            "strong_volume": bool(strong_volume),
            "boost_mode": is_boost_time(),
            "distance_from_high": 0,
            "daily_change": daily_change,
            "weekly_change_24h": weekly_change_24h,
            "weekly_volume_accel": weekly_volume_accel,
            "weekly_low_dist": weekly_low_dist,
            "weekly_high_dist": weekly_high_dist,
            "survival_candidate": True
        }

        result["rank_score"] = calculate_rank_score(result) * 0.75
        result["strategy"] += " + 생존후보"

        return result

    except Exception as e:
        print(f"{ticker} 생존후보 생성 오류:", e)
        return None



def init_entry_zone_log():
    if not os.path.exists(ENTRY_ZONE_LOG_FILE):
        with open(ENTRY_ZONE_LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "ticker", "current_price", "entry_low", "entry_high",
                "target_entry", "expected_drawdown", "reason",
                "ai_confidence", "tournament_score", "prediction_score"
            ])


def write_entry_zone_log(result):
    init_entry_zone_log()
    with open(ENTRY_ZONE_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            now_text(),
            result.get("ticker", ""),
            result.get("price", ""),
            result.get("entry_zone_low", ""),
            result.get("entry_zone_high", ""),
            result.get("target_entry_price", ""),
            result.get("expected_drawdown", ""),
            " | ".join(result.get("entry_zone_reasons", [])),
            result.get("ai_confidence", ""),
            result.get("tournament_score", ""),
            result.get("prediction_score", "")
        ])


def init_prediction_log():
    if not os.path.exists(PREDICTION_LOG_FILE):
        with open(PREDICTION_LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow([
                "time", "ticker", "prediction_score", "prob_2h", "prob_6h",
                "prob_24h", "expected_return_2h", "expected_return_6h",
                "expected_return_24h", "reasons"
            ])


def write_prediction_log(result):
    init_prediction_log()
    with open(PREDICTION_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            now_text(),
            result.get("ticker", ""),
            round(result.get("prediction_score", 0), 2),
            round(result.get("prob_2h", 0), 3),
            round(result.get("prob_6h", 0), 3),
            round(result.get("prob_24h", 0), 3),
            round(result.get("expected_return_2h", 0), 5),
            round(result.get("expected_return_6h", 0), 5),
            round(result.get("expected_return_24h", 0), 5),
            " | ".join(result.get("prediction_reasons", []))
        ])


def calculate_atr_like(df, period=14):
    try:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = tr1.combine(tr2, max).combine(tr3, max)
        atr = tr.rolling(period).mean().iloc[-2]
        price = close.iloc[-2]
        return float(atr / price) if price > 0 else 0
    except Exception:
        return 0


def calculate_candidate_prediction(result):
    score = 50
    reasons = []

    ai_conf = float(result.get("ai_confidence", 0) or 0)
    risk = float(result.get("ai_risk", 0) or 0)
    tournament_score = float(result.get("tournament_score", 0) or 0)

    score += (ai_conf - 70) * 0.35
    score -= max(risk - 45, 0) * 0.25
    score += (tournament_score - 65) * 0.25

    if result.get("leader2_mode"):
        score += 10
        reasons.append("Leader2")
    if result.get("weekly_leader_mode"):
        score += 6
        reasons.append("7일주도")
    if result.get("market_mode") == "ALT_TREND":
        score += 8
        reasons.append("알트추세")
    elif result.get("market_mode") == "BEAR":
        score -= 8
        reasons.append("하락장")

    if result.get("relative_strength", 0) >= 0.04:
        score += 8
        reasons.append("RS강함")
    elif result.get("relative_strength", 0) < 0:
        score -= 7
        reasons.append("RS약함")

    if result.get("volume_accel", 0) >= 2.5:
        score += 8
        reasons.append("거래량강함")
    elif result.get("volume_accel", 0) < 1.2:
        score -= 5
        reasons.append("거래량약함")

    if result.get("momentum_accel", 0) >= 0.006:
        score += 7
        reasons.append("모멘텀가속")
    elif result.get("momentum_accel", 0) < -0.004:
        score -= 7
        reasons.append("모멘텀둔화")

    try:
        exp_bonus, exp_reasons = get_experience_score_bonus(result)
        score += exp_bonus * 0.8
        reasons.extend(exp_reasons)
    except Exception:
        pass

    if result.get("rsi", 50) >= 88:
        score -= 10
        reasons.append("RSI초과열")
    elif 50 <= result.get("rsi", 50) <= 75:
        score += 3
        reasons.append("RSI적정")

    score = clamp(score, 0, 100)

    prob_2h = clamp(score / 100, 0.05, 0.95)
    prob_6h = clamp((score - 3) / 100, 0.05, 0.92)
    prob_24h = clamp((score - 8) / 100, 0.05, 0.88)

    expected_return_2h = (prob_2h - 0.5) * 0.035 + max(result.get("relative_strength", 0), 0) * 0.08
    expected_return_6h = (prob_6h - 0.5) * 0.055 + max(result.get("change_1h", 0), 0) * 0.45
    expected_return_24h = (prob_24h - 0.5) * 0.085 + max(result.get("daily_change", 0), 0) * 0.12

    result["prediction_score"] = score
    result["prob_2h"] = prob_2h
    result["prob_6h"] = prob_6h
    result["prob_24h"] = prob_24h
    result["expected_return_2h"] = expected_return_2h
    result["expected_return_6h"] = expected_return_6h
    result["expected_return_24h"] = expected_return_24h
    result["prediction_reasons"] = reasons

    result["rank_score"] += score * 0.9 + expected_return_2h * 900

    if score >= PREDICTION_STRONG_SCORE:
        result["strategy"] += f" + 예측강함({score:.0f})"
    elif score >= PREDICTION_MIN_SCORE_BUY:
        result["strategy"] += f" + 예측양호({score:.0f})"
    else:
        result["strategy"] += f" + 예측약함({score:.0f})"

    write_prediction_log(result)
    return result


def calculate_dynamic_entry_zone(result):
    ticker = result.get("ticker")
    price = float(result.get("price", 0) or 0)
    if not ticker or price <= 0:
        return result

    reasons = []
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=max(ENTRY_ZONE_LOOKBACK, 30))
        if df is None or len(df) < 30:
            discount = ENTRY_ZONE_MIN_DISCOUNT
            result["entry_zone_low"] = price * (1 - discount * 1.5)
            result["entry_zone_high"] = price
            result["target_entry_price"] = price * (1 - discount)
            result["expected_drawdown"] = -discount
            result["entry_zone_reasons"] = ["데이터부족 기본존"]
            return result

        recent_high = float(df["high"].iloc[-12:-2].max())
        recent_low = float(df["low"].iloc[-12:-2].min())
        ma5 = float(df["close"].rolling(5).mean().iloc[-2])
        ma20 = float(df["close"].rolling(20).mean().iloc[-2])
        atr_rate = calculate_atr_like(df)

        ai_conf = float(result.get("ai_confidence", 0) or 0)
        tournament_score = float(result.get("tournament_score", 0) or 0)
        prediction_score = float(result.get("prediction_score", 0) or 0)
        leader = result.get("leader2_mode", False)

        discount = clamp(atr_rate * ENTRY_ZONE_ATR_MULTIPLIER, ENTRY_ZONE_MIN_DISCOUNT, ENTRY_ZONE_MAX_DISCOUNT)

        if leader or ai_conf >= 90 or tournament_score >= 85:
            discount *= 0.55
            reasons.append("강한후보 얕은진입존")
        elif result.get("market_mode") in ["ALT_TREND", "TREND"]:
            discount *= 0.75
            reasons.append("추세장 얕은진입존")
        else:
            discount *= 1.10
            reasons.append("일반/횡보 깊은진입존")

        discount = clamp(discount, ENTRY_ZONE_MIN_DISCOUNT, ENTRY_ZONE_MAX_DISCOUNT)
        target = price * (1 - discount)

        supports = [x for x in [ma5, ma20, recent_low * 1.003] if x and x > 0 and x < price]
        if supports:
            nearest = min(supports, key=lambda x: abs(price - x))
            target = (target + nearest) / 2
            reasons.append("근처지지선반영")

        breakout_allowed = (
            ai_conf >= ENTRY_ZONE_BREAKOUT_ALLOW_CONFIDENCE
            or tournament_score >= ENTRY_ZONE_BREAKOUT_ALLOW_TOURNAMENT
            or prediction_score >= PREDICTION_STRONG_SCORE
        )
        if breakout_allowed and result.get("change_15m", 0) > 0 and result.get("volume_accel", 0) >= 2:
            target = max(target, price * 0.9985)
            reasons.append("강신호 돌파진입허용")

        entry_high = min(target * 1.002, price * 1.001)
        entry_low = max(target * 0.997, price * (1 - ENTRY_ZONE_MAX_DISCOUNT * 1.3))
        expected_drawdown = (min(recent_low, target) - price) / price if recent_low > 0 else -discount

        result["entry_zone_low"] = entry_low
        result["entry_zone_high"] = entry_high
        result["target_entry_price"] = target
        result["expected_drawdown"] = expected_drawdown
        result["entry_zone_reasons"] = reasons

        write_entry_zone_log(result)
        return result

    except Exception as e:
        print(f"{ticker} Dynamic Entry Zone 오류:", e)
        discount = ENTRY_ZONE_MIN_DISCOUNT
        result["entry_zone_low"] = price * (1 - discount * 1.5)
        result["entry_zone_high"] = price
        result["target_entry_price"] = price * (1 - discount)
        result["expected_drawdown"] = -discount
        result["entry_zone_reasons"] = ["오류 기본존"]
        return result


def apply_prediction_and_entry_zone(results):
    upgraded = []
    for r in results:
        r = calculate_candidate_prediction(r)
        r = calculate_dynamic_entry_zone(r)

        dd = float(r.get("expected_drawdown", 0) or 0)
        if dd <= EXPECTED_DRAWDOWN_BLOCK and not r.get("leader2_mode"):
            r["ai_risk"] = min(100, r.get("ai_risk", 0) + 18)
            r["rank_score"] -= 25
            r["strategy"] += " + 예상하락위험"
        elif dd <= EXPECTED_DRAWDOWN_WARN:
            r["ai_risk"] = min(100, r.get("ai_risk", 0) + 7)
            r["strategy"] += " + 예상하락주의"

        upgraded.append(r)

    return sorted(
        upgraded,
        key=lambda x: (
            x.get("prediction_score", 0),
            x.get("ai_confidence", 0) - x.get("ai_risk", 0) * 0.35,
            x.get("rank_score", 0)
        ),
        reverse=True
    )


def find_top_coins(performance, limit=MULTI_WATCH_TOP_N):
    learning = get_auto_learning_adjustments()
    advanced_learning = get_advanced_learning_adjustments()
    entry_quality = get_entry_quality_learning()
    coingecko_context = get_coingecko_context()

    market_regime, btc_change_4h = detect_market_regime()

    print(f"시장 상태: {market_regime}")
    print(f"BTC 4H 변화율: {btc_change_4h * 100:.2f}%")
    print(f"5시 부스터 모드: {is_boost_time()}")
    print(f"완화 모드: {is_relaxed_mode()} | 마지막 매수 후 {get_hours_since_last_buy():.1f}시간")

    candidates = get_candidate_tickers()
    results = []

    for ticker in candidates:
        try:
            result = score_ticker(ticker, market_regime, btc_change_4h, performance)

            # 후보 생존 시스템: 기존 필터에서 탈락해도 AI 평가까지 보내보기
            if result is None:
                result = build_survival_candidate(ticker, market_regime, btc_change_4h, performance)

            if result:
                coingecko_bonus, coingecko_reasons = get_coingecko_bonus(result["ticker"], coingecko_context)
                result["rank_score"] += coingecko_bonus
                result["coingecko_bonus"] = coingecko_bonus
                result["coingecko_reasons"] = coingecko_reasons

                if coingecko_bonus != 0:
                    result["strategy"] += f" + CG({coingecko_bonus:.1f})"

                learning_bonus, learning_reasons = get_learning_bonus(result, learning)
                result["rank_score"] += learning_bonus
                result["learning_bonus"] = learning_bonus
                result["learning_reasons"] = learning_reasons

                active_learning_threshold = RELAXED_LEARNING_BLOCK_THRESHOLD if is_relaxed_mode() else LEARNING_BLOCK_THRESHOLD

                if learning_bonus <= active_learning_threshold and not result.get("leader2_mode"):
                    print(f"{ticker} 제외: 자동학습 점수 낮음 {learning_bonus:.1f} | {learning_reasons}")
                    write_filter_log(
                        ticker,
                        "find_top_coins",
                        "자동학습 점수 낮음",
                        result.get("market_regime", ""),
                        result.get("price", ""),
                        result.get("rank_score", ""),
                        result.get("score", ""),
                        f"learning {learning_bonus:.1f}, threshold {active_learning_threshold}"
                    )
                    continue

                if learning_bonus != 0:
                    result["strategy"] += f" + 자동학습({learning_bonus:.1f})"

                advanced_bonus, advanced_reasons = get_advanced_learning_bonus(result, advanced_learning)
                entry_bonus, entry_reasons = get_entry_quality_bonus(result, entry_quality)

                if result.get("leader2_mode") and advanced_bonus < 0:
                    advanced_bonus = advanced_bonus / 2
                if result.get("leader2_mode") and learning_bonus < 0:
                    result["rank_score"] -= learning_bonus / 2
                    result["learning_bonus"] = learning_bonus / 2

                result["rank_score"] += advanced_bonus + entry_bonus
                result["advanced_bonus"] = advanced_bonus
                result["entry_quality_bonus"] = entry_bonus
                result["advanced_reasons"] = advanced_reasons
                result["entry_reasons"] = entry_reasons

                if advanced_bonus != 0:
                    result["strategy"] += f" + 고급학습({advanced_bonus:.1f})"
                if entry_bonus != 0:
                    result["strategy"] += f" + 진입품질({entry_bonus:.1f})"

                results.append(result)

            time.sleep(0.08)

        except Exception as e:
            print(f"{ticker} 스캔 에러:", e)

    # 1차 순위 정렬
    results = sorted(
        results,
        key=lambda x: (
            x["rank_score"],
            x.get("leader2_mode", False),
            x.get("weekly_leader_mode", False),
            x.get("early_leader_mode", False),
            x["change_15m"],
            x["relative_strength"],
            x["volume_accel"],
            x["score"]
        ),
        reverse=True
    )

    market_mode = detect_market_mode_from_results(results, market_regime, btc_change_4h)
    print(f"시장 모드: {market_mode}")

    # AI Decision Engine: 조건 탈락보다 종합 점수로 재평가
    results = apply_ai_decision_engine(results, market_mode)
    write_rank_history(results)
    update_candidate_memory(results)

    print(f"통과 코인 수: {len(results)}")
    print("===== AI 후보 랭킹 =====")

    for r in results[:10]:
        print(
            f"{r['ticker']} | AI {r.get('ai_confidence', 0):.1f} | 위험 {r.get('ai_risk', 0):.1f} | 예상 {r.get('expected_profit', 0)*100:.2f}% | "
            f"점수 {r['score']} | 랭크 {r['rank_score']:.2f} | "
            f"{r['strategy']} | CG {r.get('coingecko_bonus', 0):.1f} | "
            f"학습 {r.get('learning_bonus', 0):.1f} | "
            f"고급 {r.get('advanced_bonus', 0):.1f} | "
            f"진입품질 {r.get('entry_quality_bonus', 0):.1f} | "
            f"일봉 {r['daily_change'] * 100:.2f}% | "
            f"7일저점대비 {r['weekly_low_dist'] * 100:.2f}% | "
            f"7일고점거리 {r['weekly_high_dist'] * 100:.2f}% | "
            f"15M {r['change_15m'] * 100:.2f}% | "
            f"RS {r['relative_strength'] * 100:.2f}% | "
            f"거래량가속 {r['volume_accel']:.2f}"
        )

    return results[:limit]


def find_best_coin(performance):
    top = find_top_coins(performance, limit=1)
    if not top:
        return None
    return top[0]

def find_current_holding():
    tickers = pyupbit.get_tickers(fiat="KRW")

    for ticker in tickers:
        currency = get_currency(ticker)
        try:
            balance = get_balance(currency)
            price = pyupbit.get_current_price(ticker)

            if price and balance * price >= 5000:
                return ticker
        except Exception:
            pass

    return None


def clear_watch_state(state):
    state["watch_ticker"] = None
    state["watch_score"] = 0
    state["watch_rank_score"] = 0
    state["watch_time"] = 0
    state["watch_strategy"] = ""
    state["watch_market"] = ""
    state["watch_boost_mode"] = False
    state["watch_leader_mode"] = False
    state["watch_price"] = 0
    state["watch_low"] = 0
    state["watch_low_time"] = 0
    state["watch_had_pullback"] = False
    state["watch_list"] = []
    save_state(state)



def is_flexible_leader_watch(item):
    return (
        item.get("leader2_mode", False)
        or item.get("ai_confidence", 0) >= AI_CONFIDENCE_BUY_THRESHOLD
        or (
            item.get("daily_change", 0) >= LEADER_NO_PULLBACK_DAILY_CHANGE
            and item.get("relative_strength", 0) >= LEADER_NO_PULLBACK_RS
            and item.get("volume_accel", 0) >= LEADER_NO_PULLBACK_VOLUME_ACCEL
        )
    )


def make_watch_item(best):
    price = best["price"]
    return {
        "ticker": best["ticker"],
        "score": best["score"],
        "rank_score": best["rank_score"],
        "watch_time": time.time(),
        "strategy": best["strategy"],
        "market_regime": best["market_regime"],
        "boost_mode": best.get("boost_mode", False),
        "leader_mode": (
            best.get("early_leader_mode", False)
            or best.get("weekly_leader_mode", False)
            or best.get("leader2_mode", False)
        ),
        "leader2_mode": best.get("leader2_mode", False),
        "early_leader_mode": best.get("early_leader_mode", False),
        "weekly_leader_mode": best.get("weekly_leader_mode", False),
        "daily_change": best.get("daily_change", 0),
        "relative_strength": best.get("relative_strength", 0),
        "volume_accel": best.get("volume_accel", 0),
        "ai_confidence": best.get("ai_confidence", 0),
        "ai_risk": best.get("ai_risk", 0),
        "expected_profit": best.get("expected_profit", 0),
        "market_mode": best.get("market_mode", ""),
        "prediction_score": best.get("prediction_score", 0),
        "entry_zone_low": best.get("entry_zone_low", 0),
        "entry_zone_high": best.get("entry_zone_high", 0),
        "target_entry_price": best.get("target_entry_price", 0),
        "expected_drawdown": best.get("expected_drawdown", 0),
        "watch_price": price,
        "watch_low": price,
        "watch_low_time": time.time(),
        "watch_had_pullback": False
    }


def sync_primary_watch_from_item(state, item):
    state["watch_ticker"] = item.get("ticker")
    state["watch_score"] = item.get("score", 0)
    state["watch_rank_score"] = item.get("rank_score", 0)
    state["watch_time"] = item.get("watch_time", time.time())
    state["watch_strategy"] = item.get("strategy", "")
    state["watch_market"] = item.get("market_regime", "")
    state["watch_boost_mode"] = item.get("boost_mode", False)
    state["watch_leader_mode"] = item.get("leader_mode", False)
    state["watch_price"] = item.get("watch_price", 0)
    state["watch_low"] = item.get("watch_low", 0)
    state["watch_low_time"] = item.get("watch_low_time", 0)
    state["watch_had_pullback"] = item.get("watch_had_pullback", False)
    state["last_ai_confidence"] = item.get("ai_confidence", 0)
    state["last_ai_risk"] = item.get("ai_risk", 0)
    state["last_ai_expected_profit"] = item.get("expected_profit", 0)
    state["market_mode"] = item.get("market_mode", "")


def check_watch_signal(state, performance):
    watch_list = state.get("watch_list", [])

    # Backward compatibility: old single-watch state
    if not watch_list and state.get("watch_ticker"):
        item = {
            "ticker": state.get("watch_ticker"),
            "score": state.get("watch_score", 0),
            "rank_score": state.get("watch_rank_score", 0),
            "watch_time": state.get("watch_time", time.time()),
            "strategy": state.get("watch_strategy", ""),
            "market_regime": state.get("watch_market", ""),
            "boost_mode": state.get("watch_boost_mode", False),
            "leader_mode": state.get("watch_leader_mode", False),
            "leader2_mode": state.get("watch_leader_mode", False),
            "daily_change": 0,
            "relative_strength": 0,
            "volume_accel": 0,
            "watch_price": state.get("watch_price", 0),
            "watch_low": state.get("watch_low", 0),
            "watch_low_time": state.get("watch_low_time", 0),
            "watch_had_pullback": state.get("watch_had_pullback", False),
        }
        watch_list = [item]
        state["watch_list"] = watch_list
        save_state(state)

    if not watch_list:
        return None

    performance = performance or get_performance_memory()
    kept_items = []

    for item in watch_list:
        watch_ticker = item.get("ticker")
        if not watch_ticker:
            continue

        current_price = pyupbit.get_current_price(watch_ticker)
        if not current_price:
            kept_items.append(item)
            continue

        watch_price = float(item.get("watch_price", 0) or current_price)
        watch_low = float(item.get("watch_low", 0) or current_price)
        watch_low_time = float(item.get("watch_low_time", 0) or time.time())
        watch_time = float(item.get("watch_time", time.time()))

        elapsed = time.time() - watch_time
        elapsed_min = elapsed / 60

        if current_price < watch_low:
            watch_low = current_price
            watch_low_time = time.time()

        above_watch_rate = (current_price - watch_price) / watch_price if watch_price > 0 else 0
        pullback_rate = (watch_price - watch_low) / watch_price if watch_price > 0 else 0
        rebound_rate = (current_price - watch_low) / watch_low if watch_low > 0 else 0
        low_refresh_minutes = (time.time() - watch_low_time) / 60 if watch_low_time else 0

        if pullback_rate >= MIN_PULLBACK_AFTER_WATCH:
            item["watch_had_pullback"] = True

        item["watch_low"] = watch_low
        item["watch_low_time"] = watch_low_time

        leader_flexible = is_flexible_leader_watch(item)

        print(
            f"관찰 중: {watch_ticker} | "
            f"경과 {elapsed_min:.1f}분 | "
            f"관찰가 {watch_price:,.3f} | 저점 {watch_low:,.3f} | 현재가 {current_price:,.3f} | "
            f"관찰가대비 {above_watch_rate * 100:.2f}% | "
            f"눌림 {pullback_rate * 100:.2f}% | 반등 {rebound_rate * 100:.2f}% | "
            f"주도주유연 {leader_flexible}"
        )

        if elapsed_min >= WATCH_TIMEOUT_MINUTES:
            write_trade_log(
                "WATCH_CANCEL",
                watch_ticker,
                item.get("market_regime", ""),
                item.get("strategy", ""),
                item.get("score", ""),
                item.get("rank_score", ""),
                current_price,
                "",
                "",
                "관찰 시간 초과"
            )
            continue

        if elapsed < SIGNAL_CONFIRM_SECONDS:
            kept_items.append(item)
            continue

        # Dynamic Entry Zone: AI가 계산한 진입 구간 안에서 매수 우선
        entry_zone_low = float(item.get("entry_zone_low", 0) or 0)
        entry_zone_high = float(item.get("entry_zone_high", 0) or 0)
        prediction_score = float(item.get("prediction_score", 0) or 0)

        if DYNAMIC_ENTRY_ENABLED and entry_zone_low > 0 and entry_zone_high > 0:
            if entry_zone_low <= current_price <= entry_zone_high:
                print(f"{watch_ticker} Dynamic Entry Zone 진입 → 매수 검토")
                item["watch_had_pullback"] = True
            elif current_price > entry_zone_high and prediction_score < PREDICTION_STRONG_SCORE:
                print(f"{watch_ticker} 진입존보다 비쌈 → 대기 | zone {entry_zone_low:.3f}~{entry_zone_high:.3f}")
                kept_items.append(item)
                continue

        # 일반 후보는 추격 금지. 주도주는 더 넓게 허용.
        max_above = LEADER_MAX_BUY_ABOVE_WATCH_PRICE if leader_flexible else MAX_BUY_ABOVE_WATCH_PRICE
        if above_watch_rate > max_above:
            print(f"{watch_ticker} 관찰가보다 비쌈 → 대기")
            kept_items.append(item)
            continue

        # 주도주는 강하면 눌림 없이도 진입 허용
        no_pullback_ok = (
            (
                leader_flexible
                or (
                    is_relaxed_mode()
                    and item.get("rank_score", 0) >= 150
                    and item.get("relative_strength", 0) > 0
                    and item.get("volume_accel", 0) >= 1.5
                )
            )
            and above_watch_rate >= 0
            and above_watch_rate <= max_above
            and elapsed_min >= 1
        )

        if not no_pullback_ok:
            if not item.get("watch_had_pullback", False):
                print(f"{watch_ticker} 아직 최소 눌림 없음 → 대기")
                kept_items.append(item)
                continue

            if low_refresh_minutes >= WATCH_LOW_REFRESH_LIMIT_MINUTES and rebound_rate < REBOUND_AFTER_PULLBACK:
                write_trade_log(
                    "WATCH_CANCEL",
                    watch_ticker,
                    item.get("market_regime", ""),
                    item.get("strategy", ""),
                    item.get("score", ""),
                    item.get("rank_score", ""),
                    current_price,
                    "",
                    "",
                    "저점 갱신 후 반등 실패"
                )
                continue

            if rebound_rate < REBOUND_AFTER_PULLBACK:
                print(f"{watch_ticker} 눌림은 나왔지만 반등 부족 → 대기")
                kept_items.append(item)
                continue

        market_regime, btc_change_4h = detect_market_regime()
        result = score_ticker(watch_ticker, market_regime, btc_change_4h, performance)

        original_score = item.get("score", 0)
        original_rank = item.get("rank_score", 0)

        if result and (
            result["score"] >= original_score - 2
            or result["rank_score"] >= original_rank * 0.70
            or leader_flexible
        ):
            print(f"{watch_ticker} 매수 후보 확정")
            result["price"] = current_price
            result["strategy"] += " + TOP5관찰진입"
            state["watch_list"] = kept_items
            if kept_items:
                sync_primary_watch_from_item(state, kept_items[0])
            else:
                clear_watch_state(state)
            save_state(state)
            return result

        write_trade_log(
            "WATCH_CANCEL",
            watch_ticker,
            item.get("market_regime", ""),
            item.get("strategy", ""),
            item.get("score", ""),
            item.get("rank_score", ""),
            current_price,
            "",
            "",
            "TOP5 관찰 후 조건 약화"
        )

    state["watch_list"] = kept_items

    if kept_items:
        sync_primary_watch_from_item(state, kept_items[0])
    else:
        clear_watch_state(state)

    save_state(state)

    if kept_items:
        return "wait"

    return None

def start_watch(best, state, top_results=None):
    if top_results:
        watch_items = [make_watch_item(x) for x in top_results[:MULTI_WATCH_TOP_N]]
    else:
        watch_items = [make_watch_item(best)]

    state["watch_list"] = watch_items

    sync_primary_watch_from_item(state, watch_items[0])
    save_state(state)

    for item in watch_items:
        write_trade_log(
            "WATCH_START",
            item["ticker"],
            item.get("market_regime", ""),
            item.get("strategy", ""),
            item.get("score", ""),
            item.get("rank_score", ""),
            item.get("watch_price", ""),
            "",
            "",
            f"TOP5 관찰 시작 | 주도주유연 {is_flexible_leader_watch(item)}"
        )

    tickers = ", ".join([x["ticker"] for x in watch_items])
    send_telegram(
        f"👀 TOP{len(watch_items)} 매수 전 관찰 시작\n"
        f"후보: {tickers}\n"
        f"1순위: {watch_items[0]['ticker']}\n"
        f"전략: {watch_items[0].get('strategy', '')}\n"
        f"현재가: {watch_items[0].get('watch_price', 0):,.3f}원"
    )

def buy_coin(best, krw_balance):
    if krw_balance < BUY_KRW:
        print("KRW 잔고 부족")
        return False

    ticker = best["ticker"]

    print(f"{ticker} 매수 실행")
    result = upbit.buy_market_order(ticker, BUY_KRW)
    print(result)

    if isinstance(result, dict) and result.get("error"):
        print("매수 실패:", result)
        return False

    write_trade_log(
        "BUY",
        ticker,
        best["market_regime"],
        best["strategy"],
        best["score"],
        best["rank_score"],
        best["price"],
        "",
        best["price"],
        f"시장가 매수 | 일봉 {best['daily_change'] * 100:.2f}%"
    )

    send_telegram(
        f"🟢 스캘핑 매수\n"
        f"코인: {ticker}\n"
        f"전략: {best['strategy']}\n"
        f"현재가: {best['price']:,.3f}원\n"
        f"일봉: {best['daily_change'] * 100:.2f}%\n"
        f"15M: {best['change_15m'] * 100:.2f}%\n"
        f"RS: {best['relative_strength'] * 100:.2f}%\n"
        f"거래량가속: {best['volume_accel']:.2f}"
    )

    return True


# =========================
# SELL MANAGEMENT
# =========================
def confirm_sell_completed(ticker, currency):
    for i in range(6):
        time.sleep(5)

        balance = get_balance(currency)
        price = pyupbit.get_current_price(ticker)

        if not price:
            continue

        value = balance * price
        print(f"매도 체결 확인 {i + 1}/6 | 잔여 평가금액: {value:,.0f}원")

        if value < 5000:
            return True

    return False


def manage_holding(ticker, state):
    currency = get_currency(ticker)

    price = pyupbit.get_current_price(ticker)
    balance = get_balance(currency)
    avg_buy_price = get_avg_buy_price(currency)

    if not price or balance <= 0:
        print("실제 보유 없음 → 상태 초기화")
        reset_state()
        return

    if avg_buy_price <= 0:
        print("평균 매수가 조회 실패")
        return

    profit_rate = (price - avg_buy_price) / avg_buy_price
    position_value = balance * price

    if state.get("highest_price", 0) == 0:
        state["highest_price"] = price

    if price > state.get("highest_price", 0):
        state["highest_price"] = price

    if profit_rate > state.get("highest_profit_rate", 0):
        state["highest_profit_rate"] = profit_rate

    boost_mode = state.get("entry_boost_mode", False)
    leader_mode = state.get("entry_leader_mode", False)

    if boost_mode or leader_mode:
        take_profit = BOOST_TAKE_PROFIT
        trailing_start = BOOST_TRAILING_START_PROFIT
        trailing_drop = BOOST_TRAILING_DROP
    else:
        take_profit = TAKE_PROFIT
        trailing_start = TRAILING_START_PROFIT
        trailing_drop = TRAILING_DROP

    if profit_rate >= trailing_start:
        state["in_trailing_mode"] = True

    highest_price = state.get("highest_price", price)
    highest_profit_rate = state.get("highest_profit_rate", 0)
    trailing_drop_rate = (price - highest_price) / highest_price

    buy_time = state.get("buy_time", 0)
    hold_minutes = (time.time() - buy_time) / 60 if buy_time else 0
    hold_hours = hold_minutes / 60

    if hold_minutes >= 10 and not state.get("entry_quality_checked", False):
        write_entry_quality_log(ticker, state, price, profit_rate, hold_minutes)
        state["entry_quality_checked"] = True

    save_state(state)

    print("===== 보유 관리 =====")
    print(f"보유 코인: {ticker}")
    print(f"현재가: {price:,.3f}")
    print(f"평균 매수가: {avg_buy_price:,.3f}")
    print(f"수익률: {profit_rate * 100:.2f}%")
    print(f"최고 수익률: {highest_profit_rate * 100:.2f}%")
    print(f"보유 평가금액: {position_value:,.0f}")
    print(f"최고가: {highest_price:,.3f}")
    print(f"고점 대비 하락률: {trailing_drop_rate * 100:.2f}%")
    print(f"트레일링 모드: {state.get('in_trailing_mode')}")
    print(f"리더모드: {leader_mode}")
    print(f"보유시간: {hold_minutes:.1f}분")

    sell_signal = False
    sell_reason = ""

    if (
        not leader_mode
        and highest_profit_rate >= BREAKEVEN_TRIGGER
        and profit_rate <= BREAKEVEN_EXIT
        and profit_rate > 0
    ):
        sell_signal = True
        sell_reason = f"브레이크이븐 보호 +{profit_rate * 100:.2f}%"

    if (
        not sell_signal
        and hold_minutes >= EARLY_STRENGTH_CHECK_MINUTES
        and profit_rate <= EARLY_STRENGTH_CHECK_LOSS
    ):
        strength_score, strength_reason = check_strength(ticker)
        print(f"강도 재평가: {strength_score}/5 | {strength_reason}")

        if strength_score <= 2:
            sell_signal = True
            sell_reason = f"-0.5% 강도 약화 손절 ({strength_reason})"

    if not sell_signal and profit_rate <= STOP_LOSS:
        sell_signal = True
        sell_reason = "기본 손절 -2%"

    if not sell_signal and profit_rate >= take_profit:
        strength_score, strength_reason = check_strength(ticker)

        if leader_mode and strength_score >= 4:
            print(f"주도주 + 목표수익 도달했지만 강도 유지 → 홀딩 ({strength_reason})")
            state["in_trailing_mode"] = True
            save_state(state)
        elif not leader_mode and strength_score >= 4 and profit_rate < 0.025:
            print(f"+1% 도달했지만 강도 유지 → 홀딩 ({strength_reason})")
            state["in_trailing_mode"] = True
            save_state(state)
        else:
            sell_signal = True
            sell_reason = "목표 익절"

    if not sell_signal and state.get("in_trailing_mode") and trailing_drop_rate <= trailing_drop:
        sell_signal = True
        sell_reason = "트레일링 익절"

    if not sell_signal and hold_hours >= MAX_HOLD_HOURS and profit_rate > 0:
        sell_signal = True
        sell_reason = "4시간 경과 수익 정리"

    if sell_signal:
        print("매도 실행")
        result = upbit.sell_market_order(ticker, balance)
        print(result)

        completed = confirm_sell_completed(ticker, currency)

        if completed:
            write_trade_log(
                "SELL",
                ticker,
                state.get("entry_market", ""),
                state.get("entry_strategy", ""),
                state.get("entry_score", ""),
                state.get("entry_rank_score", ""),
                price,
                profit_rate,
                highest_price,
                sell_reason
            )

            send_telegram(
                f"🔴 스캘핑 매도 완료\n"
                f"이유: {sell_reason}\n"
                f"코인: {ticker}\n"
                f"수익률: {profit_rate * 100:.2f}%"
            )

            reset_state()

        else:
            print("⚠️ 매도 체결 미확인 → state 유지")
            send_telegram(f"⚠️ 매도 체결 미확인\n코인: {ticker}")

    else:
        print("보유 유지")
        state["holding_ticker"] = ticker
        save_state(state)


# =========================
# MAIN LOOP
# =========================
def main():
    print("Upbit AI Decision Engine 2.0 + 후보생존 봇 시작")

    init_trade_log()
    analyze_trade_log()

    performance = get_performance_memory()
    state = load_state()

    holding_ticker = find_current_holding()

    if holding_ticker:
        state["holding_ticker"] = holding_ticker
        save_state(state)
        manage_holding(holding_ticker, state)
        return

    watch_result = check_watch_signal(state, performance)

    if watch_result == "wait":
        return

    krw_balance = get_balance("KRW")
    print(f"KRW 잔고: {krw_balance:,.0f}")

    if watch_result:
        best = watch_result
    else:
        top_results = find_top_coins(performance, limit=MULTI_WATCH_TOP_N)

        if not top_results:
            print("매수할 코인 없음")
            return

        best = top_results[0]

        # AI 강신호/확실한 주도주는 watch 없이 즉시 진입
        if is_immediate_leader_candidate(best):
            print("AI 강신호 또는 확실한 주도주 → 즉시 매수 후보")
        else:
            start_watch(best, state, top_results=top_results)
            return

    if buy_coin(best, krw_balance):
        reset_state()

        state = load_state()
        state["holding_ticker"] = best["ticker"]
        state["highest_price"] = best["price"]
        state["highest_profit_rate"] = 0
        state["buy_time"] = time.time()
        state["entry_price"] = best["price"]
        state["entry_score"] = best["score"]
        state["entry_rank_score"] = best["rank_score"]
        state["entry_market"] = best["market_regime"]
        state["entry_strategy"] = best["strategy"]
        state["entry_boost_mode"] = best.get("boost_mode", False)
        state["entry_leader_mode"] = (
            best.get("early_leader_mode", False)
            or best.get("weekly_leader_mode", False)
            or best.get("leader2_mode", False)
        )
        state["entry_quality_checked"] = False
        state["last_ai_confidence"] = best.get("ai_confidence", 0)
        state["last_ai_risk"] = best.get("ai_risk", 0)
        state["last_ai_expected_profit"] = best.get("expected_profit", 0)
        state["market_mode"] = best.get("market_mode", "")

        save_state(state)


if __name__ == "__main__":
    while True:
        try:
            print("\n============================")
            print("새 사이클 시작")
            print("============================\n")

            main()

        except Exception as e:
            print("에러 발생:", e)
            try:
                send_telegram(f"⚠️ Upbit 봇 에러\n{e}")
            except Exception:
                pass

        print("\n5분 대기...\n")
        time.sleep(300)
