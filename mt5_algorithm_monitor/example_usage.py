#!/usr/bin/env python3
"""
Example Usage Script for MT5 Algorithm Monitor
Demonstrates various use cases and features
"""

from mt5_monitor import MT5TradeMonitor
from advanced_analytics import AdvancedAnalytics
from visualization import TradeVisualizer, generate_all_visualizations
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_analysis():
    """Example 1: Basic analysis of trading history"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Analysis")
    print("="*80)

    # Create monitor instance
    # Option 1: If MT5 is already logged in
    monitor = MT5TradeMonitor()

    # Option 2: Login with credentials
    # monitor = MT5TradeMonitor(
    #     account=12345678,
    #     password='your_password',
    #     server='YourBroker-Server'
    # )

    try:
        # Connect
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        # Get account info
        account_info = monitor.get_account_info()
        print(f"\nConnected to: {account_info.get('login')}")
        print(f"Balance: {account_info.get('balance')} {account_info.get('currency')}")

        # Analyze last 30 days
        deals_df = monitor.get_historical_deals(days_back=30)
        orders_df = monitor.get_historical_orders(days_back=30)

        if deals_df.empty:
            logger.warning("No trading history found")
            return

        print(f"\nAnalyzing {len(deals_df)} deals...")

        # Identify algorithm
        signature = monitor.identify_algorithm_type(deals_df, orders_df)

        # Display report
        report = monitor.generate_report(signature)
        print("\n" + report)

        # Save reports
        txt_file, json_file = monitor.save_report(signature)
        print(f"\nReports saved:")
        print(f"  - {txt_file}")
        print(f"  - {json_file}")

    finally:
        monitor.disconnect()


def example_advanced_analysis():
    """Example 2: Advanced analysis with additional metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Advanced Analysis")
    print("="*80)

    monitor = MT5TradeMonitor()

    try:
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        # Get data
        deals_df = monitor.get_historical_deals(days_back=30)
        orders_df = monitor.get_historical_orders(days_back=30)

        if deals_df.empty:
            logger.warning("No trading history found")
            return

        # Run advanced analytics
        analytics = AdvancedAnalytics()

        print("\n" + "-"*80)
        print("ADVANCED ANALYTICS")
        print("-"*80)

        # Grid trading detection
        grid_results = analytics.detect_grid_trading(deals_df, orders_df)
        print(f"\nGrid Trading: {grid_results.get('is_grid', False)}")
        print(f"Confidence: {grid_results.get('confidence', 0)*100:.1f}%")

        # News trading detection
        news_results = analytics.detect_news_trading(deals_df)
        print(f"\nNews Trading: {news_results.get('is_news_trading', False)}")
        print(f"Clusters: {news_results.get('clusters_detected', 0)}")

        # Hedging detection
        hedge_results = analytics.detect_hedging_strategy(deals_df)
        print(f"\nHedging: {hedge_results.get('is_hedging', False)}")

        # Performance metrics
        sharpe = analytics.calculate_sharpe_ratio(deals_df)
        print(f"\nSharpe Ratio: {sharpe:.2f}")

        drawdown = analytics.calculate_maximum_drawdown(deals_df)
        print(f"Maximum Drawdown: {drawdown.get('max_drawdown_pct', 0):.2f}%")

        # Generate comprehensive report
        advanced_report = analytics.generate_advanced_report(deals_df, orders_df)
        print(advanced_report)

    finally:
        monitor.disconnect()


def example_visualization():
    """Example 3: Generate visualizations"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Visualization")
    print("="*80)

    monitor = MT5TradeMonitor()

    try:
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        deals_df = monitor.get_historical_deals(days_back=30)
        orders_df = monitor.get_historical_orders(days_back=30)

        if deals_df.empty:
            logger.warning("No trading history found")
            return

        print("\nGenerating visualizations...")

        # Create visualizer
        visualizer = TradeVisualizer()

        # Generate individual charts
        visualizer.plot_equity_curve(deals_df)
        visualizer.plot_trade_distribution(deals_df)
        visualizer.plot_time_analysis(deals_df)
        visualizer.plot_drawdown(deals_df)

        # Generate comprehensive dashboard
        visualizer.create_dashboard(deals_df, orders_df)

        # Or generate all at once and save to directory
        # generate_all_visualizations(deals_df, orders_df, output_dir='./charts')

        print("\nVisualization complete!")

    finally:
        monitor.disconnect()


def example_live_monitoring():
    """Example 4: Live monitoring with callback"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Live Monitoring")
    print("="*80)

    monitor = MT5TradeMonitor()

    def on_new_trades(signature, deals_df):
        """Callback function called when new trades are detected"""
        print("\n" + "="*60)
        print(f"New trades detected at {signature.timestamp}")
        print(f"Algorithm: {signature.likely_algorithm}")
        print(f"Confidence: {signature.confidence * 100:.1f}%")
        print(f"Total trades: {len(deals_df)}")
        print("="*60)

        # Auto-save report
        monitor.save_report(signature)

    try:
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        account_info = monitor.get_account_info()
        print(f"\nMonitoring account: {account_info.get('login')}")
        print("Press Ctrl+C to stop monitoring\n")

        # Start live monitoring (checks every 60 seconds)
        monitor.monitor_live(interval_seconds=60, callback=on_new_trades)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    finally:
        monitor.disconnect()


def example_specific_symbol_analysis():
    """Example 5: Analyze specific symbol only"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Symbol-Specific Analysis")
    print("="*80)

    monitor = MT5TradeMonitor()
    target_symbol = "EURUSD"  # Change to your symbol

    try:
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        # Get all deals
        deals_df = monitor.get_historical_deals(days_back=30)
        orders_df = monitor.get_historical_orders(days_back=30)

        if deals_df.empty:
            logger.warning("No trading history found")
            return

        # Filter for specific symbol
        symbol_deals = deals_df[deals_df['symbol'] == target_symbol]
        symbol_orders = orders_df[orders_df['symbol'] == target_symbol]

        if symbol_deals.empty:
            print(f"\nNo trades found for {target_symbol}")
            return

        print(f"\nAnalyzing {len(symbol_deals)} trades for {target_symbol}...")

        # Analyze
        signature = monitor.identify_algorithm_type(symbol_deals, symbol_orders)

        # Display results
        print(f"\nAlgorithm: {signature.likely_algorithm}")
        print(f"Confidence: {signature.confidence * 100:.1f}%")

        # Statistics
        stats = signature.characteristics.get('statistics', {})
        print(f"\nStatistics for {target_symbol}:")
        print(f"  Win Rate: {stats.get('win_rate', 0):.2f}%")
        print(f"  Profit Factor: {stats.get('profit_factor', 0):.2f}")
        print(f"  Total Profit: {stats.get('total_profit', 0):.2f}")

    finally:
        monitor.disconnect()


def example_compare_time_periods():
    """Example 6: Compare different time periods"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Time Period Comparison")
    print("="*80)

    monitor = MT5TradeMonitor()

    try:
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        periods = [7, 30, 90]  # Last week, month, 3 months

        results = []

        for days in periods:
            deals_df = monitor.get_historical_deals(days_back=days)
            orders_df = monitor.get_historical_orders(days_back=days)

            if not deals_df.empty:
                signature = monitor.identify_algorithm_type(deals_df, orders_df)
                stats = signature.characteristics.get('statistics', {})

                results.append({
                    'period': f"Last {days} days",
                    'algorithm': signature.likely_algorithm,
                    'confidence': signature.confidence,
                    'trades': stats.get('total_trades', 0),
                    'win_rate': stats.get('win_rate', 0),
                    'profit': stats.get('total_profit', 0)
                })

        # Display comparison
        print("\nPERIOD COMPARISON:")
        print("-"*80)
        for result in results:
            print(f"\n{result['period']}:")
            print(f"  Algorithm: {result['algorithm']}")
            print(f"  Confidence: {result['confidence']*100:.1f}%")
            print(f"  Total Trades: {result['trades']}")
            print(f"  Win Rate: {result['win_rate']:.2f}%")
            print(f"  Total Profit: {result['profit']:.2f}")

    finally:
        monitor.disconnect()


def main():
    """Main function to run examples"""
    print("MT5 Algorithm Monitor - Usage Examples")
    print("="*80)
    print("\nSelect an example to run:")
    print("1. Basic Analysis")
    print("2. Advanced Analysis")
    print("3. Visualization")
    print("4. Live Monitoring")
    print("5. Symbol-Specific Analysis")
    print("6. Time Period Comparison")
    print("0. Exit")

    choice = input("\nEnter your choice (0-6): ").strip()

    examples = {
        '1': example_basic_analysis,
        '2': example_advanced_analysis,
        '3': example_visualization,
        '4': example_live_monitoring,
        '5': example_specific_symbol_analysis,
        '6': example_compare_time_periods
    }

    if choice == '0':
        print("Exiting...")
        return

    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
