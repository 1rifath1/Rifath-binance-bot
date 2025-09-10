# src/binance_client.py
import requests, time, hmac, hashlib
from urllib.parse import urlencode
from config import BINANCE_API_KEY, BINANCE_API_SECRET, BASE_URL_SPOT

class BinanceClient:
    def __init__(self):
        self.base = BASE_URL_SPOT.rstrip("/")
        self.session = requests.Session()
        if BINANCE_API_KEY:
            self.session.headers.update({"X-MBX-APIKEY": BINANCE_API_KEY})

    def _sign(self, params):
        """Sign parameters using HMAC SHA256."""
        query_string = urlencode(params)
        signature = hmac.new(
            BINANCE_API_SECRET.encode(), query_string.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method, endpoint, params=None, signed=False):
        """Generic request handler."""
        url = self.base + endpoint
        if params is None:
            params = {}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 5000
            params = self._sign(params)

        resp = self.session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    # ---------------- Public Endpoints ----------------
    def ping(self):
        return self._request("GET", "/v3/ping")

    def get_exchange_info(self):
        return self._request("GET", "/v3/exchangeInfo")

    def get_ticker_price(self, symbol):
        return self._request("GET", "/v3/ticker/price", params={"symbol": symbol})

    # ---------------- Private Endpoints ----------------
    def create_order(self, **kwargs):
        """Place a Spot order (BUY or SELL)."""
        return self._request("POST", "/v3/order", params=kwargs, signed=True)

    def cancel_order(self, symbol, orderId):
        return self._request("DELETE", "/v3/order", params={"symbol": symbol, "orderId": orderId}, signed=True)

    def get_open_orders(self, symbol=None):
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/v3/openOrders", params=params, signed=True)

    def get_order(self, symbol, orderId):
        return self._request("GET", "/v3/order", params={"symbol": symbol, "orderId": orderId}, signed=True)

    def get_account_balance(self):
        return self._request("GET", "/v3/account", signed=True)

