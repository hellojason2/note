# MT5 Algorithm Monitor

A comprehensive Python tool for monitoring MetaTrader 5 (MT5) trading accounts and detecting the algorithms being used through advanced pattern analysis.

## Features

### Core Capabilities
- 🔍 **Algorithm Detection**: Automatically identifies trading algorithm types based on pattern analysis
- 📊 **Real-time Monitoring**: Live monitoring of trading activity with configurable intervals
- 📈 **Advanced Analytics**: Deep analysis including Sharpe ratio, drawdown, and risk metrics
- 📉 **Visualization**: Comprehensive charts and dashboards for trade analysis
- 💾 **Export Options**: Save reports in text, JSON, and CSV formats

### Detection Algorithms
The monitor can detect and classify:
- High-Frequency Trading (HFT)
- Scalping strategies
- Day trading bots
- Swing trading algorithms
- Martingale/Anti-Martingale systems
- Grid trading EAs
- News-based trading
- Correlation/basket trading
- Hedging strategies
- And more...

### Analysis Features
- ✅ Position sizing pattern detection
- ✅ Time-based trading pattern analysis
- ✅ Risk management strategy identification
- ✅ Trading frequency classification
- ✅ Symbol/instrument preference detection
- ✅ Entry precision analysis
- ✅ Performance metrics (Sharpe ratio, profit factor, win rate)
- ✅ Maximum drawdown calculation
- ✅ Grid trading detection
- ✅ News event correlation
- ✅ Multi-symbol correlation analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- MetaTrader 5 terminal installed
- Active MT5 account (demo or live)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install MetaTrader 5

Download and install MetaTrader 5 from your broker or from [MetaTrader's official website](https://www.metatrader5.com/).

### Step 3: Configure

Copy the example configuration file and customize it:

```bash
cp config_example.py config.py
```

Edit `config.py` with your MT5 credentials (if needed).

## Quick Start

### Basic Usage

```python
from mt5_monitor import MT5TradeMonitor

# Create monitor instance
monitor = MT5TradeMonitor()

# Connect to MT5
if monitor.connect():
    # Analyze last 30 days of trading
    deals_df = monitor.get_historical_deals(days_back=30)
    orders_df = monitor.get_historical_orders(days_back=30)

    # Identify the algorithm
    signature = monitor.identify_algorithm_type(deals_df, orders_df)

    # Display report
    report = monitor.generate_report(signature)
    print(report)

    # Save reports
    monitor.save_report(signature)

    monitor.disconnect()
```

### Command Line Usage

Run a complete analysis from the command line:

```bash
# Analyze last 30 days (if already logged into MT5)
python mt5_monitor.py --days 30

# Or login with credentials
python mt5_monitor.py --account 12345678 --password yourpass --server BrokerServer --days 30

# Live monitoring mode (checks every 60 seconds)
python mt5_monitor.py --live --interval 60

# Analyze specific time period
python mt5_monitor.py --days 90
```

### Using the Example Script

Run the interactive example script:

```bash
python example_usage.py
```

This will present a menu with various usage examples:
1. Basic Analysis
2. Advanced Analysis
3. Visualization
4. Live Monitoring
5. Symbol-Specific Analysis
6. Time Period Comparison

## Detailed Usage

### 1. Connecting to MT5

#### Option A: If MT5 is already logged in

```python
monitor = MT5TradeMonitor()
```

#### Option B: Login with credentials

```python
monitor = MT5TradeMonitor(
    account=12345678,
    password='your_password',
    server='YourBroker-Server'
)
```

### 2. Getting Trading Data

```python
# Get historical deals
deals_df = monitor.get_historical_deals(days_back=30)

# Get historical orders
orders_df = monitor.get_historical_orders(days_back=30)

# Get current open positions
positions_df = monitor.get_current_positions()

# Get account information
account_info = monitor.get_account_info()
```

### 3. Analyzing Algorithms

```python
# Identify algorithm type
signature = monitor.identify_algorithm_type(deals_df, orders_df)

print(f"Algorithm: {signature.likely_algorithm}")
print(f"Confidence: {signature.confidence * 100:.1f}%")

# Access detailed patterns
for pattern in signature.patterns:
    print(f"\nPattern: {pattern.pattern_name}")
    print(f"Confidence: {pattern.confidence * 100:.1f}%")
    print("Evidence:")
    for evidence in pattern.evidence:
        print(f"  - {evidence}")
```

### 4. Advanced Analytics

```python
from advanced_analytics import AdvancedAnalytics

analytics = AdvancedAnalytics()

# Detect grid trading
grid_results = analytics.detect_grid_trading(deals_df, orders_df)

# Detect news trading
news_results = analytics.detect_news_trading(deals_df)

# Calculate performance metrics
sharpe_ratio = analytics.calculate_sharpe_ratio(deals_df)
drawdown = analytics.calculate_maximum_drawdown(deals_df)

# Generate comprehensive report
advanced_report = analytics.generate_advanced_report(deals_df, orders_df)
print(advanced_report)
```

### 5. Visualization

```python
from visualization import TradeVisualizer, generate_all_visualizations

visualizer = TradeVisualizer()

# Individual charts
visualizer.plot_equity_curve(deals_df)
visualizer.plot_trade_distribution(deals_df)
visualizer.plot_time_analysis(deals_df)
visualizer.plot_drawdown(deals_df)
visualizer.plot_performance_heatmap(deals_df)

# Comprehensive dashboard
visualizer.create_dashboard(deals_df, orders_df)

# Or generate all at once
generate_all_visualizations(deals_df, orders_df, output_dir='./charts')
```

### 6. Live Monitoring

```python
def on_new_trades(signature, deals_df):
    """Callback when new trades detected"""
    print(f"New trades! Algorithm: {signature.likely_algorithm}")
    monitor.save_report(signature)

# Start monitoring (checks every 60 seconds)
monitor.monitor_live(interval_seconds=60, callback=on_new_trades)
```

## Output

### Text Report Example

```
================================================================================
MT5 ALGORITHM ANALYSIS REPORT
================================================================================
Generated: 2025-01-15T10:30:00

Identified Algorithm: Professional Day Trading EA
Overall Confidence: 82.5%

--------------------------------------------------------------------------------
TRADE STATISTICS
--------------------------------------------------------------------------------
total_trades: 145
winning_trades: 92
losing_trades: 53
win_rate: 63.45%
profit_factor: 1.87
total_profit: 2543.50
average_profit: 17.54
...

--------------------------------------------------------------------------------
DETECTED PATTERNS
--------------------------------------------------------------------------------
1. Fixed Lot Size
   Confidence: 95.0%
   Description: Position sizing strategy analysis
   Evidence:
   - All trades use identical lot size: 0.1

2. Day Trading Strategy
   Confidence: 80.0%
   Description: Trading frequency analysis
   Evidence:
   - Average 7.3 trades per day
   ...
```

### JSON Export

Complete analysis data is also saved in JSON format for programmatic access:

```json
{
  "algorithm": "Professional Day Trading EA",
  "confidence": 0.825,
  "patterns": [...],
  "characteristics": {...},
  "timestamp": "2025-01-15T10:30:00"
}
```

### Visualizations

The tool generates various charts including:
- Equity curve with drawdown visualization
- Profit/loss distribution histograms
- Trading hours heatmap
- Performance by symbol
- Daily trading frequency
- Comprehensive dashboard

## Algorithm Detection Logic

The tool uses multiple pattern detection methods:

### 1. Position Sizing Analysis
- Fixed lot detection
- Martingale pattern recognition
- Dynamic sizing identification

### 2. Time Pattern Analysis
- Trading hour concentration
- Day of week patterns
- Regular interval detection

### 3. Risk Management Analysis
- Stop-loss usage patterns
- Take-profit patterns
- Risk-reward ratio analysis

### 4. Frequency Classification
- High-frequency trading (50+ trades/day)
- Scalping (20-50 trades/day)
- Day trading (5-20 trades/day)
- Swing trading (1-5 trades/day)
- Position trading (<1 trade/day)

### 5. Symbol Analysis
- Single instrument specialization
- Multi-instrument strategies
- Symbol concentration patterns

### 6. Advanced Pattern Detection
- Grid trading patterns
- News-based trading clusters
- Correlation trading
- Hedging strategies
- Position scaling

## API Reference

### MT5TradeMonitor Class

Main class for monitoring and analysis.

#### Methods

- `connect()`: Connect to MT5 terminal
- `disconnect()`: Disconnect from MT5
- `get_account_info()`: Get account information
- `get_historical_deals(days_back)`: Get historical trade deals
- `get_historical_orders(days_back)`: Get historical orders
- `get_current_positions()`: Get current open positions
- `calculate_trade_statistics(deals_df)`: Calculate trade statistics
- `identify_algorithm_type(deals_df, orders_df)`: Identify algorithm
- `generate_report(signature)`: Generate text report
- `save_report(signature, filename)`: Save reports to files
- `monitor_live(interval_seconds, callback)`: Start live monitoring

### AdvancedAnalytics Class

Advanced analytical methods.

#### Static Methods

- `detect_grid_trading(deals_df, orders_df)`: Detect grid trading
- `detect_news_trading(deals_df)`: Detect news-based trading
- `detect_correlation_trading(deals_df)`: Detect correlation trading
- `detect_hedging_strategy(deals_df)`: Detect hedging
- `analyze_entry_precision(deals_df)`: Analyze entry precision
- `detect_scaling_in_out(deals_df)`: Detect position scaling
- `calculate_sharpe_ratio(deals_df, risk_free_rate)`: Calculate Sharpe ratio
- `calculate_maximum_drawdown(deals_df)`: Calculate max drawdown
- `analyze_trade_duration(deals_df)`: Analyze trade durations
- `generate_advanced_report(deals_df, orders_df)`: Generate full report

### TradeVisualizer Class

Visualization and charting.

#### Methods

- `plot_equity_curve(deals_df, save_path)`: Plot equity curve
- `plot_trade_distribution(deals_df, save_path)`: Plot P/L distribution
- `plot_time_analysis(deals_df, save_path)`: Plot time-based analysis
- `plot_drawdown(deals_df, save_path)`: Plot drawdown analysis
- `plot_performance_heatmap(deals_df, save_path)`: Plot performance heatmap
- `create_dashboard(deals_df, orders_df, save_path)`: Create full dashboard

## Troubleshooting

### Common Issues

#### 1. MT5 Connection Failed

**Error**: `MT5 initialization failed`

**Solutions**:
- Ensure MT5 terminal is installed and running
- Check that you have the correct login credentials
- Verify the server name matches your broker's server
- Try logging into MT5 manually first

#### 2. No Trading History

**Error**: `No deals found in the specified period`

**Solutions**:
- Check that you have actual trading history
- Try increasing the `days_back` parameter
- Verify you're connected to the correct account
- Ensure you're analyzing the right time period

#### 3. Import Errors

**Error**: `ModuleNotFoundError: No module named 'MetaTrader5'`

**Solution**:
```bash
pip install MetaTrader5
```

#### 4. Visualization Not Working

**Error**: `Matplotlib is required for visualization`

**Solution**:
```bash
pip install matplotlib seaborn
```

### Linux Compatibility

MT5 is primarily designed for Windows. For Linux users:

1. Use Wine to run MT5
2. Consider using a Windows VPS
3. Use the tool on a Windows machine and access results remotely

## Performance Considerations

- **Large datasets**: For accounts with thousands of trades, consider analyzing shorter periods or implementing pagination
- **Live monitoring**: Use appropriate intervals (60+ seconds) to avoid excessive API calls
- **Visualization**: Chart generation can be memory-intensive for large datasets

## Security Best Practices

1. **Never commit credentials**: Don't hardcode passwords in scripts
2. **Use environment variables**: Store sensitive data in environment variables
3. **Protect config files**: Add `config.py` to `.gitignore`
4. **Demo accounts**: Test with demo accounts first
5. **Read-only access**: The tool only reads data, never places trades

## Contributing

Contributions are welcome! Areas for improvement:

- Additional algorithm detection patterns
- Machine learning-based classification
- Support for more broker-specific features
- Enhanced visualization options
- Real-time alerts and notifications

## License

This project is provided as-is for educational and analysis purposes.

## Disclaimer

⚠️ **Important**: This tool is for analysis and monitoring purposes only. It does not:
- Place or modify trades
- Access account passwords after connection
- Send data to external servers
- Guarantee the accuracy of algorithm identification

Trading involves risk. Past performance does not guarantee future results. Use this tool responsibly and at your own risk.

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review the example scripts
- Ensure all dependencies are installed
- Verify MT5 terminal is properly configured

## Changelog

### Version 1.0.0 (2025-01-15)
- Initial release
- Core algorithm detection
- Advanced analytics module
- Visualization capabilities
- Live monitoring feature
- Comprehensive documentation

## Acknowledgments

- Built with [MetaTrader5 Python package](https://pypi.org/project/MetaTrader5/)
- Inspired by algorithmic trading analysis needs
- Thanks to the Python trading community

---

**Happy Trading Analysis! 📊🚀**
