import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.advanced.strategies import place_oco_monitored

# -----------------------
# Test OCO order
# -----------------------
symbol = "BTCUSDT"
side = "BUY"
qty = 0.001        # small test quantity
tp_price = 35000   # example TP price
sl_price = 34000   # example SL price

try:
    orders = place_oco_monitored(symbol, side, qty, tp_price, sl_price)
    print("Placed orders:", orders)

    # -----------------------
    # Save to JSON file
    # -----------------------
    file_path = os.path.join(os.path.dirname(__file__), "bot_trades.json")

    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Append new trade
    data.append({
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "tp_price": tp_price,
        "sl_price": sl_price,
        "orders": orders
    })

    # Write back to file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Orders saved to {file_path}")

except Exception as e:
    print(f"Error placing OCO orders: {e}")
