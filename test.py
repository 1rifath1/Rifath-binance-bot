import os
import sys
import json
import websocket
import threading
from time import sleep
from datetime import datetime

# --- Add src to path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Project Imports ---
from src.binance import BinanceClient
from src import order, utils
from src.advanced import strategies
from src.advanced.bots import GridTradingBot
from src.portfolio import PortfolioManager
from src.logger_config import logger

# --- Rich Library Imports ---
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich import box
from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
from rich.layout import Layout
from rich.align import Align
from rich.spinner import Spinner

# --- Main Application Class ---
class TradingTerminal:
    """
    The ultimate, over-engineered, feature-rich interactive trading terminal application.
    Manages state, UI rendering, and all user interactions for every implemented feature.
    """
    def __init__(self):
        self.console = Console()
        self.client = BinanceClient()
        self.portfolio = PortfolioManager()
        self.active_bots = {}
        self.load_theme()
        logger.info("Ultimate Trading Terminal Initialized.")

    def load_theme(self):
        """Loads UI color theme from a JSON file for full customization."""
        try:
            theme_path = os.path.join(os.path.dirname(__file__), 'config', 'theme.json')
            with open(theme_path) as f:
                self.theme = json.load(f)
        except FileNotFoundError:
            self.console.print("[bold red]Theme file 'src/config/theme.json' not found. Using default colors.[/bold red]")
            self.theme = { 
                "title": "bold cyan", "panel_border": "blue", "header": "bold magenta", 
                "error": "bold red", "success": "bold green", "warning": "yellow"
            }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def handle_api_call(self, func, *args, **kwargs):
        """Standardized wrapper for API calls with spinners and robust error handling."""
        try:
            spinner = Spinner("dots", text=" Contacting Binance...")
            with Live(spinner, console=self.console, transient=True, vertical_overflow="visible"):
                result = func(*args, **kwargs)
            self.console.print(f"\n[{self.theme['success']}]Success![/{self.theme['success']}]")
            if result:
                self.print_output(result)
        except Exception as e:
            self.console.print(f"\n[{self.theme['error']}]An API error occurred:[/{self.theme['error']}] {e}")
            logger.error(f"API Call Failed: {func.__name__} - {e}")
        finally:
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def print_output(self, data, title="API Response"):
        """Enhanced output formatting using Rich tables for all data types."""
        if not isinstance(data, list): data = [data]
        if not data: return self.console.print(f"[{self.theme['warning']}]No data to display.[/]")
        
        table = Table(title=title, show_header=True, header_style=self.theme['header'], box=box.HEAVY_EDGE, border_style=self.theme['panel_border'])
        headers = data[0].keys()
        for header in headers: table.add_column(header, no_wrap=False, justify="left")
        
        for item in data:
            row = [json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v) for v in item.values()]
            table.add_row(*row)
        self.console.print(table)
    
    # --- MENU IMPLEMENTATIONS ---

    def show_order_placement_menu(self):
        """The main menu for placing any type of order."""
        while True:
            self.clear_screen()
            menu_text = (
                "[bold]1.[/] Basic Order (Market, Limit)\n"
                "[bold]2.[/] Advanced Order (OCO, TWAP, Iceberg)\n"
                "[bold]3.[/] Back to Main Menu"
            )
            self.console.print(Panel(menu_text, title="[yellow]Place New Order[/yellow]", border_style=self.theme['panel_border']))
            choice = Prompt.ask("Select order category", choices=["1", "2", "3"], default="3")

            if choice == '1': self.show_basic_orders_menu()
            elif choice == '2': self.show_advanced_orders_menu()
            elif choice == '3': break
    
    def show_basic_orders_menu(self):
        """Handles placement of Market and Limit orders."""
        self.clear_screen()
        order_type = Prompt.ask("Choose order type", choices=["MARKET", "LIMIT"], default="LIMIT")
        
        symbol = utils.prompt_for_symbol()
        side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
        qty = FloatPrompt.ask("Quantity")

        if order_type == "MARKET":
            self.handle_api_call(order.place_market, symbol, side, qty)
        elif order_type == "LIMIT":
            price = FloatPrompt.ask("Limit Price")
            self.handle_api_call(order.place_limit, symbol, side, qty, price)

    def show_advanced_orders_menu(self):
        """Handles placement of all complex, over-engineered order strategies."""
        self.clear_screen()
        menu_text = (
            "[bold]1.[/] Monitored OCO (One-Cancels-Other)\n"
            "[bold]2.[/] Smart TWAP (Time-Weighted Average Price)\n"
            "[bold]3.[/] Polling Iceberg Order\n"
            "[bold]4.[/] Back"
        )
        self.console.print(Panel(menu_text, title="[cyan]Advanced Order Strategies[/cyan]", border_style=self.theme['panel_border']))
        choice = Prompt.ask("Select strategy", choices=["1", "2", "3", "4"], default="4")

        if choice == '1': # OCO
            symbol = utils.prompt_for_symbol()
            side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
            qty = FloatPrompt.ask("Quantity")
            tp_price = FloatPrompt.ask("Take Profit Price")
            sl_price = FloatPrompt.ask("Stop Loss Trigger Price")
            self.handle_api_call(strategies.place_oco_monitored, symbol, side, qty, tp_price, sl_price)
        elif choice == '2': # TWAP
            symbol = utils.prompt_for_symbol()
            side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
            total_qty = FloatPrompt.ask("Total Quantity")
            duration = IntPrompt.ask("Duration (minutes)", default=60)
            slices = IntPrompt.ask("Number of Slices", default=12)
            self.handle_api_call(strategies.execute_smart_twap, symbol, side, total_qty, duration, slices)
        elif choice == '3': # Iceberg
            symbol = utils.prompt_for_symbol()
            side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
            total_qty = FloatPrompt.ask("Total Quantity")
            legs = IntPrompt.ask("Number of visible legs", default=10)
            self.handle_api_call(strategies.place_iceberg_order, symbol, side, total_qty, legs)
        elif choice == '4': return

    def run(self):
        """The main application loop and entry point."""
        if not os.getenv("BINANCE_API_KEY") or not os.getenv("BINANCE_API_SECRET"):
            self.console.print(f"[{self.theme['error']}]Error: API Keys not found in .env file.[/]")
            sys.exit(1)

        while True:
            self.clear_screen()
            main_menu_text = (
                "[bold]1.[/] Live Dashboard\n"
                "[bold]2.[/] Place New Order\n"
                "[bold]3.[/] Manage Open Orders\n"
                "[bold]4.[/] Automated Bots\n"
                "[bold]5.[/] Watch Market Data\n"
                f"[bold {self.theme['error']}]P.[/] PANIC - Close All Positions & Orders\n"
                "[bold]Q.[/] Quit"
            )
            self.console.print(Panel(main_menu_text, title=f"[{self.theme['title']}]Ultimate Trading Terminal[/]", subtitle="[dim]Engineered Beyond Reason[/dim]", expand=False, border_style=self.theme['panel_border']))
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "P", "Q"], default="Q").upper()

            if choice == '1': self.show_live_dashboard()
            elif choice == '2': self.show_order_placement_menu()
            # elif choice == '3': self.show_order_management_menu() # Placeholder for full implementation
            # elif choice == '4': self.show_bots_menu()             # Placeholder for full implementation
            # elif choice == '5': self.watch_market_data()          # Placeholder for full implementation
            elif choice == 'P': self.panic_button()
            elif choice == 'Q':
                if any(b.is_running for b in self.active_bots.values()):
                    if Confirm.ask(f"[{self.theme['warning']}]Active bots are running. Exit and stop them?[/]"):
                        for bot in self.active_bots.values(): bot.stop()
                    else: continue
                self.console.print("[bold yellow]Shutting down. Goodbye![/bold yellow]")
                break
    
    # --- Other major functions from previous version would be here ---
    # show_live_dashboard, panic_button, etc. I am omitting them for brevity but they are essential.
    def show_live_dashboard(self):
        """A live-updating dashboard showing portfolio, positions, and clock."""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(ratio=1, name="main"),
            Layout(size=3, name="footer")
        )
        layout["main"].split_row(Layout(name="portfolio"), Layout(name="positions"))
        layout["footer"].split_row(Layout(name="status"), Layout(name="clock"))

        def get_time_panel():
            return Panel(Align.center(f"[bold]{datetime.now().ctime()}[/bold]"), border_style=self.theme['panel_border'])

        with Live(layout, screen=True, redirect_stderr=False) as live:
            live.console.print(f"[{self.theme['warning']}]Loading dashboard... Press Ctrl+C to exit.[/]")
            try:
                while True:
                    self.portfolio.fetch_data()
                    pnl_color = "green" if self.portfolio.total_unrealized_pnl >= 0 else "red"
                    header_text = Align.center(f"[{self.theme['title']}]Live Dashboard[/] | Total PNL: [{pnl_color}]${self.portfolio.total_unrealized_pnl:,.2f}[/{pnl_color}]")
                    layout['header'].update(Panel(header_text, border_style=self.theme['panel_border']))
                    
                    summary_table = Table(show_header=False, box=box.SIMPLE)
                    summary_table.add_column(style="cyan")
                    summary_table.add_column(style="bold green")
                    summary_table.add_row("USDT Balance:", f"${self.portfolio.usdt_balance:,.2f}")
                    layout['portfolio'].update(Panel(summary_table, title="Portfolio", border_style=self.theme['panel_border']))
                    
                    pos_table = self.portfolio.display_positions()
                    layout['positions'].update(Panel(pos_table or "[dim]No open positions.[/dim]", title="Positions", border_style=self.theme['panel_border']))
                    
                    layout['status'].update(Panel(f"API Status: [green]OK[/green] | Bots Active: {sum(1 for b in self.active_bots.values() if b.is_running)}", border_style=self.theme['panel_border']))
                    layout['clock'].update(get_time_panel())
                    sleep(5)
            except KeyboardInterrupt:
                pass

    def panic_button(self):
        """Function to close all positions and cancel all orders."""
        self.clear_screen()
        self.console.print(Panel(f"[{self.theme['error']}]PANIC BUTTON ACTIVATED[/{self.theme['error']}]", style="bold red on white", expand=False))
        if not Confirm.ask("[bold red]Are you ABSOLUTELY SURE you want to close ALL positions and cancel ALL open orders?[/bold red]"):
            return

        self.console.print(f"[{self.theme['warning']}]Fetching open positions...[/]")
        self.portfolio.fetch_data()
        open_positions = [p for p in self.portfolio.positions_data if float(p['positionAmt']) != 0]

        if not open_positions:
            self.console.print("[green]No open positions to close.[/green]")
        else:
            for pos in open_positions:
                symbol = pos['symbol']
                qty = abs(float(pos['positionAmt']))
                side = "SELL" if float(pos['positionAmt']) > 0 else "BUY"
                self.console.print(f"\nClosing {symbol} position...")
                self.handle_api_call(order.place_market, symbol, side, qty)
        
        self.console.print(f"\n[{self.theme['warning']}]Cancelling all open orders...[/]")
        all_symbols = utils.get_all_symbols()
        cancelled_count = 0
        for symbol in all_symbols:
            try:
                # This call returns a list of cancelled orders.
                res = self.client.cancel_all_open_orders(symbol)
                if res:
                   cancelled_count += len(res)
            except Exception:
                pass # Fail silently if a symbol has no orders
        self.console.print(f"[green]Panic sequence complete. {cancelled_count} orders cancelled.[/green]")
        logger.warning("PANIC BUTTON USED.")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")


if __name__ == "__main__":
    app = TradingTerminal()
    app.run()

