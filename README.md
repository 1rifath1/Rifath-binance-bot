# Binance Trading Bot v2

A comprehensive, feature-rich cryptocurrency trading terminal for Binance Spot trading with advanced order management, portfolio tracking, backtesting capabilities, and automated trading strategies.

## ⚠️ Disclaimer

**This software is for educational and research purposes only. Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.**

## Features

### Core Trading Features
- **Market & Limit Orders**: Place basic buy/sell orders with proper validation
- **Advanced Order Types**: OCO (One-Cancels-Other), TWAP, Iceberg orders
- **Portfolio Management**: Real-time balance tracking and position monitoring
- **Order Management**: View and manage open orders across all symbols
- **Risk Management**: Built-in position sizing and validation

### Advanced Capabilities
- **Live Dashboard**: Real-time portfolio updates with Rich UI
- **Backtesting Engine**: Test strategies against historical data
- **Automated Trading Bots**: Grid trading and custom strategy bots
- **Market Data Streaming**: WebSocket-based real-time price feeds
- **Panic Button**: Emergency position closure and order cancellation

### User Interface
- **Rich Terminal UI**: Beautiful, interactive command-line interface
- **Live Updates**: Real-time dashboard with auto-refreshing data
- **Comprehensive Logging**: JSON-structured logging for all operations
- **Themed Interface**: Customizable color schemes and layouts

## Installation

### Prerequisites
- Python 3.8 or higher
- Binance account with API access
- Valid Binance API keys

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/binance-trading-bot-v2.git
   cd binance-trading-bot-v2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   BINANCE_API_KEY=your_api_key_here
   BINANCE_API_SECRET=your_api_secret_here
   USE_TESTNET=true  # Set to false for live trading
   ```

4. **API Key Setup**
   - Log into your Binance account
   - Go to API Management
   - Create a new API key with Spot Trading permissions
   - **Important**: For testnet, use Binance Testnet credentials

## Project Structure

```
BinanceTradingBot_v2/
├── src/
│   ├── binance.py          # Binance API client
│   ├── order.py            # Order placement functions
│   ├── portfolio.py        # Portfolio management
│   ├── validation.py       # Order validation and adjustment
│   ├── utils.py            # Utility functions
│   ├── logger_config.py    # Logging configuration
│   ├── backnet.py          # Backtesting engine
│   ├── config.py           # Configuration management
│   ├── cli.py              # Main CLI application
│   ├── test.py             # Alternative terminal interface
│   └── advanced/
│       ├── strategies.py   # Advanced trading strategies
│       └── bots.py         # Automated trading bots
├── .env                    # Environment variables (create this)
├── bot.log                 # Application logs
├── bot_trades.json         # Trade history
└── README.md
```

## Usage

### Starting the Application

**Primary Interface (Recommended)**
```bash
python src/cli.py
```

**Alternative Interface**
```bash
python src/test.py
```

### Main Menu Options

1. **Live Dashboard**: Real-time portfolio monitoring
2. **Place New Order**: Market, limit, and advanced orders
3. **Manage Open Orders**: View and cancel existing orders
4. **Automated Bots**: Start/stop automated trading strategies
5. **Watch Market Data**: Real-time price streaming
6. **Panic Button**: Emergency closure of all positions
7. **Quit**: Safe application shutdown

### Basic Trading Workflow

1. **Start the application**
2. **Check Live Dashboard** to view current portfolio
3. **Place Orders**:
   - Select order type (Market/Limit)
   - Choose trading mode (Live/Backtest)
   - Enter symbol (e.g., BTCUSDT)
   - Specify quantity and price
4. **Monitor positions** via the dashboard
5. **Manage risk** using stop-loss and take-profit orders

### Advanced Features

#### Backtesting
- Place `historical_data.csv` in the `src/` directory
- Required columns: `Timestamp`, `Execution Price`
- Select "BACKTEST" mode when placing orders

#### OCO Orders
One-Cancels-Other orders for automated profit-taking and loss-cutting:
- Set take-profit price
- Set stop-loss trigger price
- System automatically manages both orders

#### TWAP Strategy
Time-Weighted Average Price execution:
- Splits large orders into smaller chunks
- Executes over specified time duration
- Reduces market impact

#### Grid Trading Bot
Automated grid trading strategy:
- Places buy/sell orders at regular intervals
- Profits from market volatility
- Configurable grid size and spacing

## Configuration

### API Settings
```python
# src/config.py
USE_TESTNET = True  # False for live trading
BASE_URL_SPOT = "https://testnet.binance.vision/api"  # Testnet
# BASE_URL_SPOT = "https://api.binance.com"  # Live
```

### Logging Configuration
```python
# src/logger_config.py
- Rotating file handler (2MB max, 3 backups)
- JSON-structured logs
- Configurable log levels
```

### Theme Customization
Create `src/config/theme.json`:
```json
{
    "title": "bold cyan",
    "panel_border": "blue", 
    "header": "bold magenta",
    "error": "bold red",
    "success": "bold green",
    "warning": "yellow"
}
```

## API Permissions Required

Your Binance API key needs the following permissions:
- **Spot Trading**: Place and cancel orders
- **Read**: Access account information and balances
- **Enable Spot & Margin Trading**: Required for spot operations

**Security Note**: Never share your API keys or commit them to version control.

## Safety Features

### Built-in Protections
- **Order Validation**: Automatic quantity/price adjustment per Binance rules
- **Error Handling**: Comprehensive exception handling and logging
- **Confirmation Prompts**: Critical actions require confirmation
- **Panic Button**: Emergency stop for all trading activity

### Risk Management
- Position sizing calculations based on account balance
- Stop-loss and take-profit automation
- Maximum order size limits
- Real-time P&L monitoring

## Troubleshooting

### Common Issues

**API Connection Errors**
```
Error: API Keys not found
Solution: Check .env file and API key validity
```

**Order Placement Failures**
```
Error: Insufficient balance
Solution: Ensure adequate USDT balance for orders
```

**Symbol Not Found**
```
Error: Invalid symbol
Solution: Use valid Binance symbols (e.g., BTCUSDT, ETHUSDT)
```

**Backtest Data Missing**
```
Error: Historical data unavailable
Solution: Add historical_data.csv to src/ directory
```

### Debug Mode
Enable detailed logging:
```python
logger.setLevel(logging.DEBUG)
```

### Testing Connection
```bash
python -c "from src.binance import BinanceClient; print(BinanceClient().ping())"
```

## Development

### Adding New Features

1. **New Order Types**: Extend `src/order.py`
2. **Trading Strategies**: Add to `src/advanced/strategies.py`
3. **UI Components**: Modify Rich layouts in CLI files
4. **Data Sources**: Extend backtesting in `src/backnet.py`

### Code Structure
- **Modular Design**: Separate concerns across files
- **Error Handling**: Comprehensive try/catch blocks
- **Logging**: All operations logged with context
- **Type Hints**: Enhanced code readability

### Testing
- Use testnet for all development
- Test with small quantities first
- Verify API permissions before live trading

## Dependencies

### Core Requirements
```
requests>=2.28.0
python-dotenv>=0.19.0
rich>=12.0.0
pandas>=1.5.0
websocket-client>=1.3.0
```

### Optional (for advanced features)
```
numpy>=1.21.0
matplotlib>=3.5.0
plotly>=5.0.0
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Test on testnet before submitting

## Support

### Getting Help
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Wiki**: Check project wiki for detailed guides

### Reporting Bugs
Include the following information:
- Operating system and Python version
- Complete error message and stack trace
- Steps to reproduce the issue
- API response logs (remove sensitive data)

## Roadmap

### Planned Features
- [ ] Futures trading support
- [ ] Advanced charting integration
- [ ] Machine learning strategy modules
- [ ] Mobile app companion
- [ ] Multi-exchange support
- [ ] Strategy backtesting with technical indicators

### Recent Updates
- ✅ Comprehensive backtesting engine
- ✅ Rich terminal interface
- ✅ Advanced order types (OCO, TWAP, Iceberg)
- ✅ Real-time dashboard
- ✅ Automated trading bots

## Security

### Best Practices
- Use testnet for development and testing
- Never share API keys publicly
- Enable IP whitelist restrictions
- Use read-only keys when possible
- Regular security audits of API permissions

### Data Privacy
- All data stored locally
- No external data transmission except to Binance
- Logs contain no sensitive information
- Optional data encryption support

---

**Happy Trading! Remember to always trade responsibly and never invest more than you can afford to lose.**
