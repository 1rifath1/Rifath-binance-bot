import math
from binance import BinanceClient

client = BinanceClient()
EXCHANGE_INFO = client.get_exchange_info()

# Build symbol filters dictionary
SYMBOL_FILTERS = {
    s['symbol']: {f['filterType']: f for f in s['filters']}
    for s in EXCHANGE_INFO['symbols']
}

def adjust_qty(symbol, qty):
    """
    Adjust quantity according to the symbol's LOT_SIZE filter.
    """
    lot = SYMBOL_FILTERS[symbol]['LOT_SIZE']
    step = float(lot['stepSize'])
    min_qty = float(lot['minQty'])
    adj_qty = math.floor(qty / step) * step
    return max(adj_qty, min_qty)  # Ensure minimum quantity

def adjust_price(symbol, price):
    """
    Adjust price according to the symbol's PRICE_FILTER tick size.
    """
    tick = SYMBOL_FILTERS[symbol]['PRICE_FILTER']
    step = float(tick['tickSize'])
    min_price = float(tick['minPrice'])
    adj_price = round(price / step) * step
    return max(adj_price, min_price)  # Ensure minimum price

def validate(symbol, qty, price=None):
    """
    Validate and adjust quantity and price for Spot orders.
    Returns:
        qty_adj for market orders
        (qty_adj, price_adj) for limit orders
    """
    filters = SYMBOL_FILTERS[symbol]
    qty_adj = adjust_qty(symbol, qty)

    if price is not None:
        price_adj = adjust_price(symbol, price)
        # Optional: check min notional
        if 'MIN_NOTIONAL' in filters:
            min_notional = float(filters['MIN_NOTIONAL']['notional'])
            notional = qty_adj * price_adj
            assert notional >= min_notional, f"Order notional too small: {notional} < {min_notional}"
        return qty_adj, price_adj

    return qty_adj
