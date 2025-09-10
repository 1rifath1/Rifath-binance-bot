import pandas as pd
import os
from datetime import datetime

class BacktestEngine:
    def __init__(self, file_path=None):
        # Default path
        if file_path is None:
            file_path = r"D:\BinanceTradingBot_v2\BinanceTradingBot_v2\src\historical_data.csv"
        
        if not os.path.exists(file_path):
            print(f"[BacktestEngine] Error: Historical data file not found at {file_path}. Backtesting unavailable.")
            self.data = None
            self.file_missing = True
            return
        
        # Load CSV
        self.data = pd.read_csv(file_path)
        # Check required columns
        required_cols = ['Timestamp', 'Execution Price']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Missing column '{col}' in CSV")
        
        # Convert timestamp
        self.data['timestamp'] = pd.to_datetime(self.data['Timestamp'], unit='ms')
        # Sort
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)
        self.file_missing = False

    def get_price_at(self, ts):
        """Return last trade price up to given timestamp"""
        if self.file_missing or self.data is None:
            raise RuntimeError("Backtest data unavailable.")
        if isinstance(ts, (int, float)):
            ts = pd.to_datetime(ts, unit='ms')
        df = self.data[self.data['timestamp'] <= ts]
        if df.empty:
            raise ValueError("No historical data before given timestamp")
        return float(df.iloc[-1]['Execution Price'])

    def simulate_market_order(self, symbol, side, qty, ts=None):
        """Market order fills at next available trade price after timestamp"""
        if self.file_missing or self.data is None:
            return {"error": "Backtest data unavailable."}
        
        if ts is None:
            # Use the *latest* available price, not the first one
            trade = self.data.iloc[-1]
        else:
            if isinstance(ts, (int, float)):
                ts = pd.to_datetime(ts, unit='ms')
            df = self.data[self.data['timestamp'] >= ts]
            if df.empty:
                return {"error": "No future trades available to fill market order"}
            trade = df.iloc[0]

        return {
            "mode": "backtest",
            "orderType": "MARKET",
            "symbol": symbol,
            "side": side.upper(),
            "qty": float(qty),
            "fill_price": float(trade['Execution Price']),
            "status": "FILLED",
            "timestamp": str(trade['timestamp'])
        }

    def simulate_limit_order(self, symbol, side, qty, limit_price, ts=None):
        """Find first trade *after ts* that crosses limit price"""
        if self.file_missing or self.data is None:
            return {"error": "Backtest data unavailable."}
        
        df = self.data
        if ts is not None:
            if isinstance(ts, (int, float)):
                ts = pd.to_datetime(ts, unit='ms')
            df = df[df['timestamp'] >= ts]
        
        for _, trade in df.iterrows():
            price = float(trade['Execution Price'])
            if side.upper() == "BUY" and price <= limit_price:
                return {
                    "mode": "backtest",
                    "orderType": "LIMIT",
                    "symbol": symbol,
                    "side": "BUY",
                    "qty": float(qty),
                    "limit_price": float(limit_price),
                    "fill_price": price,
                    "status": "FILLED",
                    "timestamp": str(trade['timestamp'])
                }
            if side.upper() == "SELL" and price >= limit_price:
                return {
                    "mode": "backtest",
                    "orderType": "LIMIT",
                    "symbol": symbol,
                    "side": "SELL",
                    "qty": float(qty),
                    "limit_price": float(limit_price),
                    "fill_price": price,
                    "status": "FILLED",
                    "timestamp": str(trade['timestamp'])
                }

        # Order never filled
        return {
            "mode": "backtest",
            "orderType": "LIMIT",
            "symbol": symbol,
            "side": side.upper(),
            "qty": float(qty),
            "limit_price": float(limit_price),
            "status": "OPEN"
        }
