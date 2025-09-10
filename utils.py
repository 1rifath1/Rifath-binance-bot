import json
from functools import lru_cache
from rich.prompt import Prompt
from rich.console import Console
from src.binance import BinanceClient  # Corrected import path

@lru_cache(maxsize=1)
def get_all_symbols(spot_only=False):
    """
    Fetches tradeable symbols from Binance.
    - spot_only=True => fetch Spot symbols
    - spot_only=False => fetch USDT perpetual futures symbols
    Caches the result to avoid repeated API calls.
    """
    client = BinanceClient()
    try:
        exchange_info = client.get_exchange_info()
        symbols_set = set()

        for s in exchange_info.get('symbols', []):
            if spot_only:
                # Spot symbols: just trading status
                if s.get('status') == 'TRADING':
                    symbols_set.add(s.get('symbol'))
            else:
                # USDT perpetual futures symbols
                if (
                    s.get('quoteAsset') == 'USDT' and
                    s.get('contractType') == 'PERPETUAL' and
                    s.get('status') == 'TRADING'
                ):
                    symbols_set.add(s.get('symbol'))
        return symbols_set

    except Exception as e:
        from src.logger_config import logger
        logger.error(f"Could not fetch symbol list from Binance API: {e}")
        return set()


def prompt_for_symbol(console: Console, spot_only=False):
    """
    Prompts the user for a trading symbol with validation.
    Accepts a `console` object and handles Spot or Futures symbols.

    Args:
        console (rich.console.Console): The console object for printing output.
        spot_only (bool): Whether to fetch Spot symbols. Default False (Futures).
    """
    all_symbols = get_all_symbols(spot_only=spot_only)
    if not all_symbols:
        console.print("[yellow]Could not fetch the symbol list from Binance.[/yellow]")
        return Prompt.ask("[yellow]Please enter the symbol manually (e.g., BTCUSDT)[/yellow]").upper()

    symbol = Prompt.ask(
        "Enter Symbol (e.g., BTCUSDT)",
        choices=list(all_symbols),
        show_choices=False,
        console=console
    ).upper()

    while symbol not in all_symbols:
        console.print(f"[red]Error: '{symbol}' is not a valid symbol.[/red]")
        symbol = Prompt.ask(
            "Please enter a valid symbol",
            choices=list(all_symbols),
            show_choices=False,
            console=console
        ).upper()
    return symbol


def calculate_position_size(usdt_balance: float, risk_percent: float, entry_price: float, stop_loss_price: float) -> float:
    """
    Calculates the appropriate position size in the base currency (e.g., BTC)
    based on the user's defined risk parameters.

    Returns:
        float: The calculated quantity of the base asset to trade.
    """
    if entry_price == stop_loss_price:
        return 0.0  # Avoid division by zero

    risk_amount_usdt = usdt_balance * (risk_percent / 100.0)
    price_risk_per_unit = abs(entry_price - stop_loss_price)

    if price_risk_per_unit == 0:
        return 0.0

    position_size = risk_amount_usdt / price_risk_per_unit
    return position_size
