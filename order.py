# order.py
from src.binance import BinanceClient   # make sure correct import path
from src.validation import validate            # ensure validate handles qty & price
from src.logger_config import logger

# Initialize Binance client
client = BinanceClient()

def place_market(symbol: str, side: str, qty: float):
    """
    Place a Market Order (BUY/SELL).
    :param symbol: Trading pair, e.g., "BTCUSDT"
    :param side: "BUY" or "SELL"
    :param qty: Quantity of base asset
    """
    try:
        # Adjust quantity according to exchange rules
        qty_adj = validate(symbol, qty)

        # Create market order
        resp = client.create_order(
            symbol=symbol,
            side=side.upper(),
            type="MARKET",
            quantity=qty_adj
        )

        logger.info(f"✅ Spot Market Order placed: {resp}")
        return resp

    except Exception as e:
        logger.error(f"❌ Error placing market order: {e}")
        return {"error": str(e)}


def place_limit(symbol: str, side: str, qty: float, price: float, tif: str = "GTC"):
    """
    Place a Limit Order (BUY/SELL).
    :param symbol: Trading pair
    :param side: "BUY" or "SELL"
    :param qty: Quantity of base asset
    :param price: Limit price
    :param tif: Time in Force ("GTC", "IOC", "FOK")
    """
    try:
        # Adjust both quantity and price for precision
        qty_adj, price_adj = validate(symbol, qty, price)

        # Create limit order
        resp = client.create_order(
            symbol=symbol,
            side=side.upper(),
            type="LIMIT",
            quantity=qty_adj,
            price=price_adj,
            timeInForce=tif
        )

        logger.info(f"✅ Spot Limit Order placed: {resp}")
        return resp

    except Exception as e:
        logger.error(f"❌ Error placing limit order: {e}")
        return {"error": str(e)}
