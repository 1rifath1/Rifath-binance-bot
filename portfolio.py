from decimal import Decimal
from rich.table import Table
from rich import box

from src.binance import BinanceClient
from src.logger_config import logger

class PortfolioManager:
    """
    Handles fetching and displaying Spot portfolio balances.
    Supports free/locked balances, USDT balance, total value, and positions for dashboard.
    """
    def __init__(self):
        self.client = BinanceClient()
        self.balances = []
        self.positions_data = []      # For dashboard and panic button
        self.total_unrealized_pnl = 0.0
        self.usdt_balance = 0.0       # For live dashboard
        self.is_data_loaded = False

    def fetch_data(self):
        """
        Fetches Spot balances from Binance API and prepares positions for dashboard.
        """
        logger.info("Fetching Spot portfolio data...")
        try:
            account_info = self.client.get_account_balance()
            
            # Ensure we get a list of balances
            balances_list = account_info.get("balances", []) if isinstance(account_info, dict) else account_info

            self.balances = [
                {
                    "asset": b["asset"],
                    "free": float(b["free"]),
                    "locked": float(b["locked"])
                }
                for b in balances_list if float(b["free"]) > 0 or float(b["locked"]) > 0
            ]

            self.positions_data = []
            total_value = 0.0
            usdt_balance = 0.0
            for b in self.balances:
                asset = b["asset"]
                free = b["free"]
                locked = b["locked"]
                symbol = asset + "USDT" if asset != "USDT" else "USDT"

                # Get current price in USDT
                try:
                    price_data = self.client.get_symbol_price(symbol)
                    price = float(price_data['price']) if 'price' in price_data else 0.0
                except Exception:
                    price = 0.0

                position_value = (free + locked) * price
                total_value += position_value

                if asset == "USDT":
                    usdt_balance = free + locked

                self.positions_data.append({
                    "symbol": symbol,
                    "free": free,
                    "locked": locked,
                    "current_price": price,
                    "position_value": position_value,
                    "positionAmt": free + locked  # Dummy field for spot
                })

            self.total_unrealized_pnl = total_value
            self.usdt_balance = usdt_balance
            self.is_data_loaded = True
            logger.info("Spot portfolio data fetched successfully.")
        except Exception as e:
            logger.error(f"Failed to fetch Spot portfolio data: {e}")
            self.is_data_loaded = False
            self.positions_data = []
            self.total_unrealized_pnl = 0.0
            self.usdt_balance = 0.0

    def display_positions(self):
        """
        Returns a Rich Table object to display Spot positions.
        """
        if not self.is_data_loaded:
            self.fetch_data()

        if not self.positions_data:
            return None

        table = Table(
            title="Spot Portfolio Positions",
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE_HEAVY,
            expand=True
        )

        headers = ["Symbol", "Free", "Locked", "Price (USDT)", "Value (USDT)"]
        for header in headers:
            table.add_column(header, justify="right")

        for pos in self.positions_data:
            table.add_row(
                pos["symbol"],
                f"{pos['free']:,.6f}",
                f"{pos['locked']:,.6f}",
                f"{pos['current_price']:,.4f}",
                f"{pos['position_value']:,.4f}"
            )

        return table
