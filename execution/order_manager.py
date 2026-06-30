"""Order Manager: isolated buy/sell order execution layer."""
def buy_market(upbit, ticker: str, krw_amount: float):
    return upbit.buy_market_order(ticker, krw_amount)

def sell_market(upbit, ticker: str, balance: float):
    return upbit.sell_market_order(ticker, balance)
