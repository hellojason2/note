#!/usr/bin/env python3
"""
MetaTrader 5 Trade Algorithm Monitor
Monitors MT5 account trades and analyzes patterns to identify trading algorithms
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import time
import json
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TradePattern:
    """Data class for identified trade patterns"""
    pattern_name: str
    confidence: float
    description: str
    evidence: List[str]
    metrics: Dict[str, float]


@dataclass
class AlgorithmSignature:
    """Data class for algorithm identification results"""
    likely_algorithm: str
    confidence: float
    patterns: List[TradePattern]
    characteristics: Dict[str, any]
    timestamp: str


class MT5TradeMonitor:
    """Main class for monitoring MT5 trades and detecting algorithms"""

    def __init__(self, account: int = None, password: str = None, server: str = None):
        """
        Initialize MT5 connection

        Args:
            account: MT5 account number (optional if already logged in)
            password: MT5 account password
            server: MT5 broker server
        """
        self.account = account
        self.password = password
        self.server = server
        self.connected = False
        self.trade_history = []
        self.positions = []

    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False

        if self.account and self.password and self.server:
            if not mt5.login(self.account, self.password, self.server):
                logger.error(f"MT5 login failed: {mt5.last_error()}")
                return False

        self.connected = True
        logger.info("Successfully connected to MT5")
        return True

    def disconnect(self):
        """Disconnect from MT5"""
        mt5.shutdown()
        self.connected = False
        logger.info("Disconnected from MT5")

    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected:
            logger.error("Not connected to MT5")
            return {}

        account_info = mt5.account_info()
        if account_info is None:
            logger.error(f"Failed to get account info: {mt5.last_error()}")
            return {}

        return {
            'login': account_info.login,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'leverage': account_info.leverage,
            'currency': account_info.currency,
            'server': account_info.server,
            'company': account_info.company
        }

    def get_historical_deals(self, days_back: int = 30) -> pd.DataFrame:
        """
        Get historical deals/trades

        Args:
            days_back: Number of days to look back

        Returns:
            DataFrame with historical deals
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return pd.DataFrame()

        from_date = datetime.now() - timedelta(days=days_back)
        to_date = datetime.now()

        deals = mt5.history_deals_get(from_date, to_date)

        if deals is None or len(deals) == 0:
            logger.warning("No deals found in the specified period")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')

        logger.info(f"Retrieved {len(df)} deals from last {days_back} days")
        return df

    def get_historical_orders(self, days_back: int = 30) -> pd.DataFrame:
        """Get historical orders"""
        if not self.connected:
            logger.error("Not connected to MT5")
            return pd.DataFrame()

        from_date = datetime.now() - timedelta(days=days_back)
        to_date = datetime.now()

        orders = mt5.history_orders_get(from_date, to_date)

        if orders is None or len(orders) == 0:
            logger.warning("No orders found in the specified period")
            return pd.DataFrame()

        df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
        df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
        df['time_done'] = pd.to_datetime(df['time_done'], unit='s')

        logger.info(f"Retrieved {len(df)} orders from last {days_back} days")
        return df

    def get_current_positions(self) -> pd.DataFrame:
        """Get current open positions"""
        if not self.connected:
            logger.error("Not connected to MT5")
            return pd.DataFrame()

        positions = mt5.positions_get()

        if positions is None or len(positions) == 0:
            logger.info("No open positions")
            return pd.DataFrame()

        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')

        logger.info(f"Retrieved {len(df)} open positions")
        return df

    def calculate_trade_statistics(self, deals_df: pd.DataFrame) -> Dict:
        """Calculate comprehensive trade statistics"""
        if deals_df.empty:
            return {}

        # Filter only trade deals (entry/exit), exclude deposits, etc.
        trade_deals = deals_df[deals_df['type'].isin([0, 1])].copy()  # 0=buy, 1=sell

        if trade_deals.empty:
            return {}

        stats = {
            'total_trades': len(trade_deals),
            'winning_trades': len(trade_deals[trade_deals['profit'] > 0]),
            'losing_trades': len(trade_deals[trade_deals['profit'] < 0]),
            'break_even_trades': len(trade_deals[trade_deals['profit'] == 0]),
            'total_profit': trade_deals['profit'].sum(),
            'average_profit': trade_deals['profit'].mean(),
            'max_profit': trade_deals['profit'].max(),
            'max_loss': trade_deals['profit'].min(),
            'average_volume': trade_deals['volume'].mean(),
            'total_volume': trade_deals['volume'].sum(),
        }

        if stats['total_trades'] > 0:
            stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100

        # Calculate profit factor
        gross_profit = trade_deals[trade_deals['profit'] > 0]['profit'].sum()
        gross_loss = abs(trade_deals[trade_deals['profit'] < 0]['profit'].sum())

        if gross_loss > 0:
            stats['profit_factor'] = gross_profit / gross_loss
        else:
            stats['profit_factor'] = float('inf') if gross_profit > 0 else 0

        # Analyze trading times
        trade_deals['hour'] = trade_deals['time'].dt.hour
        trade_deals['day_of_week'] = trade_deals['time'].dt.dayofweek

        stats['most_active_hour'] = trade_deals['hour'].mode().values[0] if not trade_deals.empty else None
        stats['most_active_day'] = trade_deals['day_of_week'].mode().values[0] if not trade_deals.empty else None

        # Calculate time between trades
        trade_deals = trade_deals.sort_values('time')
        time_diffs = trade_deals['time'].diff().dt.total_seconds() / 60  # in minutes
        stats['avg_time_between_trades_minutes'] = time_diffs.mean()
        stats['median_time_between_trades_minutes'] = time_diffs.median()

        return stats

    def detect_position_sizing_pattern(self, deals_df: pd.DataFrame) -> TradePattern:
        """Detect position sizing algorithm"""
        if deals_df.empty:
            return None

        volumes = deals_df['volume'].values
        evidence = []
        pattern_name = "Unknown"
        confidence = 0.0
        metrics = {}

        # Check for fixed lot size
        if len(set(volumes)) == 1:
            pattern_name = "Fixed Lot Size"
            confidence = 0.95
            evidence.append(f"All trades use identical lot size: {volumes[0]}")
            metrics['lot_size'] = volumes[0]

        # Check for martingale (doubling after losses)
        elif len(volumes) > 3:
            profits = deals_df['profit'].values
            is_martingale = True
            martingale_count = 0

            for i in range(1, len(volumes)):
                if profits[i-1] < 0 and volumes[i] >= volumes[i-1] * 1.8:
                    martingale_count += 1
                elif profits[i-1] > 0 and volumes[i] <= volumes[0] * 1.2:
                    pass  # Reset after win
                else:
                    is_martingale = False

            if martingale_count > len(volumes) * 0.3:
                pattern_name = "Martingale/Anti-Martingale"
                confidence = 0.8
                evidence.append(f"Position size increases after losses in {martingale_count} instances")
                metrics['martingale_ratio'] = martingale_count / len(volumes)

        # Check for percentage-based sizing
        else:
            volume_std = np.std(volumes)
            volume_mean = np.mean(volumes)
            cv = volume_std / volume_mean if volume_mean > 0 else 0

            if cv < 0.2:
                pattern_name = "Consistent Proportional Sizing"
                confidence = 0.7
                evidence.append(f"Low variation in lot sizes (CV: {cv:.2f})")
                metrics['coefficient_variation'] = cv
            else:
                pattern_name = "Dynamic/Variable Sizing"
                confidence = 0.6
                evidence.append(f"High variation in lot sizes (CV: {cv:.2f})")
                metrics['coefficient_variation'] = cv

        return TradePattern(
            pattern_name=pattern_name,
            confidence=confidence,
            description="Position sizing strategy analysis",
            evidence=evidence,
            metrics=metrics
        )

    def detect_time_based_patterns(self, deals_df: pd.DataFrame) -> TradePattern:
        """Detect time-based trading patterns"""
        if deals_df.empty:
            return None

        deals_df = deals_df.copy()
        deals_df['hour'] = deals_df['time'].dt.hour
        deals_df['minute'] = deals_df['time'].dt.minute
        deals_df['day_of_week'] = deals_df['time'].dt.dayofweek

        evidence = []
        metrics = {}

        # Check for specific hour concentration
        hour_counts = deals_df['hour'].value_counts()
        top_hour = hour_counts.index[0]
        top_hour_pct = (hour_counts.iloc[0] / len(deals_df)) * 100

        if top_hour_pct > 50:
            evidence.append(f"{top_hour_pct:.1f}% of trades occur at hour {top_hour}")
            pattern_name = "Time-Scheduled Trading"
            confidence = 0.85
        elif top_hour_pct > 30:
            evidence.append(f"{top_hour_pct:.1f}% of trades occur at hour {top_hour}")
            pattern_name = "Preferred Time Window Trading"
            confidence = 0.7
        else:
            pattern_name = "Continuous/24-Hour Trading"
            confidence = 0.6
            evidence.append("Trades distributed across multiple hours")

        metrics['top_trading_hour'] = int(top_hour)
        metrics['top_hour_concentration'] = float(top_hour_pct)

        # Check for regular intervals
        time_diffs = deals_df.sort_values('time')['time'].diff().dt.total_seconds() / 60
        time_diffs = time_diffs.dropna()

        if len(time_diffs) > 0:
            median_interval = time_diffs.median()
            std_interval = time_diffs.std()

            if std_interval < median_interval * 0.3 and median_interval < 60:
                evidence.append(f"Regular trading intervals (~{median_interval:.1f} minutes)")
                confidence = max(confidence, 0.8)
                metrics['avg_interval_minutes'] = float(median_interval)

        # Check day of week patterns
        dow_counts = deals_df['day_of_week'].value_counts()
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        top_dow = dow_names[dow_counts.index[0]]
        top_dow_pct = (dow_counts.iloc[0] / len(deals_df)) * 100

        if top_dow_pct > 40:
            evidence.append(f"Concentrated trading on {top_dow} ({top_dow_pct:.1f}%)")

        return TradePattern(
            pattern_name=pattern_name,
            confidence=confidence,
            description="Time-based trading pattern analysis",
            evidence=evidence,
            metrics=metrics
        )

    def detect_risk_management_pattern(self, deals_df: pd.DataFrame, orders_df: pd.DataFrame) -> TradePattern:
        """Detect risk management and stop-loss patterns"""
        evidence = []
        metrics = {}
        pattern_name = "Unknown Risk Management"
        confidence = 0.5

        if deals_df.empty:
            return None

        # Analyze stop losses and take profits from orders
        if not orders_df.empty:
            orders_with_sl = orders_df[orders_df['sl'] > 0]
            orders_with_tp = orders_df[orders_df['tp'] > 0]

            sl_usage = len(orders_with_sl) / len(orders_df) * 100
            tp_usage = len(orders_with_tp) / len(orders_df) * 100

            metrics['stop_loss_usage_pct'] = float(sl_usage)
            metrics['take_profit_usage_pct'] = float(tp_usage)

            if sl_usage > 80 and tp_usage > 80:
                pattern_name = "Strict Risk Management (SL + TP)"
                confidence = 0.9
                evidence.append(f"Stop Loss used in {sl_usage:.1f}% of trades")
                evidence.append(f"Take Profit used in {tp_usage:.1f}% of trades")
            elif sl_usage > 80:
                pattern_name = "Conservative (SL Only)"
                confidence = 0.8
                evidence.append(f"Stop Loss used in {sl_usage:.1f}% of trades")
            elif tp_usage > 80:
                pattern_name = "Profit Target Based"
                confidence = 0.75
                evidence.append(f"Take Profit used in {tp_usage:.1f}% of trades")
            else:
                pattern_name = "Flexible/Manual Risk Management"
                confidence = 0.6
                evidence.append("Variable use of stop loss and take profit")

        # Analyze profit/loss distribution
        profits = deals_df['profit'].values
        wins = profits[profits > 0]
        losses = profits[profits < 0]

        if len(wins) > 0 and len(losses) > 0:
            avg_win = wins.mean()
            avg_loss = abs(losses.mean())
            risk_reward = avg_win / avg_loss if avg_loss > 0 else 0

            metrics['average_win'] = float(avg_win)
            metrics['average_loss'] = float(avg_loss)
            metrics['risk_reward_ratio'] = float(risk_reward)

            if risk_reward > 2:
                evidence.append(f"High risk-reward ratio: {risk_reward:.2f}")
            elif risk_reward < 0.5:
                evidence.append(f"Low risk-reward ratio: {risk_reward:.2f} (potential martingale)")

        return TradePattern(
            pattern_name=pattern_name,
            confidence=confidence,
            description="Risk management strategy analysis",
            evidence=evidence,
            metrics=metrics
        )

    def detect_trading_frequency_pattern(self, deals_df: pd.DataFrame) -> TradePattern:
        """Detect trading frequency patterns"""
        if deals_df.empty:
            return None

        evidence = []
        metrics = {}

        # Calculate trades per day
        deals_df = deals_df.copy()
        deals_df['date'] = deals_df['time'].dt.date
        trades_per_day = deals_df.groupby('date').size()

        avg_trades_per_day = trades_per_day.mean()
        std_trades_per_day = trades_per_day.std()

        metrics['avg_trades_per_day'] = float(avg_trades_per_day)
        metrics['std_trades_per_day'] = float(std_trades_per_day)

        if avg_trades_per_day > 50:
            pattern_name = "High-Frequency Trading (HFT)"
            confidence = 0.85
            evidence.append(f"Average {avg_trades_per_day:.1f} trades per day")
        elif avg_trades_per_day > 20:
            pattern_name = "Scalping Strategy"
            confidence = 0.8
            evidence.append(f"Average {avg_trades_per_day:.1f} trades per day")
        elif avg_trades_per_day > 5:
            pattern_name = "Day Trading Strategy"
            confidence = 0.75
            evidence.append(f"Average {avg_trades_per_day:.1f} trades per day")
        elif avg_trades_per_day > 1:
            pattern_name = "Swing Trading Strategy"
            confidence = 0.7
            evidence.append(f"Average {avg_trades_per_day:.1f} trades per day")
        else:
            pattern_name = "Position Trading Strategy"
            confidence = 0.7
            evidence.append(f"Average {avg_trades_per_day:.1f} trades per day")

        # Check for consistency
        if std_trades_per_day < avg_trades_per_day * 0.3:
            evidence.append("Consistent daily trading frequency")
            confidence += 0.05
        else:
            evidence.append("Variable daily trading frequency")

        return TradePattern(
            pattern_name=pattern_name,
            confidence=confidence,
            description="Trading frequency analysis",
            evidence=evidence,
            metrics=metrics
        )

    def detect_symbol_pattern(self, deals_df: pd.DataFrame) -> TradePattern:
        """Detect symbol/instrument trading patterns"""
        if deals_df.empty:
            return None

        evidence = []
        metrics = {}

        symbol_counts = deals_df['symbol'].value_counts()
        total_symbols = len(symbol_counts)
        top_symbol = symbol_counts.index[0]
        top_symbol_pct = (symbol_counts.iloc[0] / len(deals_df)) * 100

        metrics['total_symbols_traded'] = total_symbols
        metrics['top_symbol'] = top_symbol
        metrics['top_symbol_concentration'] = float(top_symbol_pct)

        if total_symbols == 1:
            pattern_name = "Single Instrument Specialist"
            confidence = 0.95
            evidence.append(f"Only trades {top_symbol}")
        elif top_symbol_pct > 70:
            pattern_name = "Focused Instrument Strategy"
            confidence = 0.85
            evidence.append(f"{top_symbol_pct:.1f}% concentration on {top_symbol}")
        elif total_symbols <= 5:
            pattern_name = "Multi-Instrument Strategy"
            confidence = 0.75
            evidence.append(f"Trades {total_symbols} different instruments")
        else:
            pattern_name = "Diversified Portfolio Strategy"
            confidence = 0.7
            evidence.append(f"Trades {total_symbols} different instruments")

        return TradePattern(
            pattern_name=pattern_name,
            confidence=confidence,
            description="Instrument selection analysis",
            evidence=evidence,
            metrics=metrics
        )

    def identify_algorithm_type(self, deals_df: pd.DataFrame, orders_df: pd.DataFrame) -> AlgorithmSignature:
        """
        Main algorithm identification function
        Combines all pattern detections to identify the likely algorithm type
        """
        patterns = []

        # Detect all patterns
        patterns.append(self.detect_position_sizing_pattern(deals_df))
        patterns.append(self.detect_time_based_patterns(deals_df))
        patterns.append(self.detect_risk_management_pattern(deals_df, orders_df))
        patterns.append(self.detect_trading_frequency_pattern(deals_df))
        patterns.append(self.detect_symbol_pattern(deals_df))

        # Filter out None patterns
        patterns = [p for p in patterns if p is not None]

        # Calculate statistics
        stats = self.calculate_trade_statistics(deals_df)

        # Determine overall algorithm type based on patterns
        likely_algorithm = self._determine_algorithm_type(patterns, stats)

        # Calculate overall confidence
        if patterns:
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
        else:
            avg_confidence = 0.0

        # Compile characteristics
        characteristics = {
            'statistics': stats,
            'pattern_count': len(patterns),
            'analysis_period_days': (deals_df['time'].max() - deals_df['time'].min()).days if not deals_df.empty else 0
        }

        return AlgorithmSignature(
            likely_algorithm=likely_algorithm,
            confidence=avg_confidence,
            patterns=patterns,
            characteristics=characteristics,
            timestamp=datetime.now().isoformat()
        )

    def _determine_algorithm_type(self, patterns: List[TradePattern], stats: Dict) -> str:
        """Determine the overall algorithm type from patterns"""
        pattern_names = [p.pattern_name for p in patterns]

        # Rules-based algorithm identification
        if "High-Frequency Trading (HFT)" in pattern_names:
            return "High-Frequency Trading Bot"

        if "Scalping Strategy" in pattern_names:
            if "Time-Scheduled Trading" in pattern_names:
                return "Scheduled Scalping EA"
            return "Scalping Bot/EA"

        if "Martingale/Anti-Martingale" in pattern_names:
            if "Grid" in str(pattern_names):
                return "Grid Martingale EA"
            return "Martingale-Based EA"

        if "Day Trading Strategy" in pattern_names:
            if "Strict Risk Management (SL + TP)" in pattern_names:
                return "Professional Day Trading EA"
            return "Day Trading Bot"

        if "Swing Trading Strategy" in pattern_names:
            return "Swing Trading Algorithm"

        if "Position Trading Strategy" in pattern_names:
            return "Long-Term Position Trading EA"

        # Check for specific characteristics
        if stats.get('win_rate', 0) < 40 and stats.get('profit_factor', 0) > 1.5:
            return "High Risk-Reward Trend Following EA"

        if stats.get('win_rate', 0) > 70 and stats.get('profit_factor', 0) < 2:
            return "High Win-Rate Mean Reversion EA"

        return "Custom/Hybrid Trading Algorithm"

    def generate_report(self, signature: AlgorithmSignature) -> str:
        """Generate a detailed text report"""
        report = []
        report.append("=" * 80)
        report.append("MT5 ALGORITHM ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {signature.timestamp}")
        report.append(f"\nIdentified Algorithm: {signature.likely_algorithm}")
        report.append(f"Overall Confidence: {signature.confidence * 100:.1f}%")
        report.append("\n" + "-" * 80)
        report.append("TRADE STATISTICS")
        report.append("-" * 80)

        stats = signature.characteristics.get('statistics', {})
        for key, value in stats.items():
            if isinstance(value, float):
                report.append(f"{key}: {value:.2f}")
            else:
                report.append(f"{key}: {value}")

        report.append("\n" + "-" * 80)
        report.append("DETECTED PATTERNS")
        report.append("-" * 80)

        for i, pattern in enumerate(signature.patterns, 1):
            report.append(f"\n{i}. {pattern.pattern_name}")
            report.append(f"   Confidence: {pattern.confidence * 100:.1f}%")
            report.append(f"   Description: {pattern.description}")
            report.append(f"   Evidence:")
            for evidence in pattern.evidence:
                report.append(f"   - {evidence}")
            if pattern.metrics:
                report.append(f"   Metrics:")
                for key, value in pattern.metrics.items():
                    report.append(f"   - {key}: {value}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def save_report(self, signature: AlgorithmSignature, filename: str = None):
        """Save analysis report to file"""
        if filename is None:
            filename = f"mt5_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        report = self.generate_report(signature)

        with open(filename, 'w') as f:
            f.write(report)

        # Also save JSON version
        json_filename = filename.replace('.txt', '.json')
        with open(json_filename, 'w') as f:
            json.dump({
                'algorithm': signature.likely_algorithm,
                'confidence': signature.confidence,
                'patterns': [asdict(p) for p in signature.patterns],
                'characteristics': signature.characteristics,
                'timestamp': signature.timestamp
            }, f, indent=2, default=str)

        logger.info(f"Reports saved: {filename} and {json_filename}")
        return filename, json_filename

    def monitor_live(self, interval_seconds: int = 60, callback=None):
        """
        Monitor account in real-time

        Args:
            interval_seconds: How often to check for new trades
            callback: Optional callback function to call with new data
        """
        logger.info(f"Starting live monitoring (checking every {interval_seconds} seconds)")
        logger.info("Press Ctrl+C to stop")

        last_deal_time = datetime.now() - timedelta(days=1)

        try:
            while True:
                # Get new deals since last check
                deals = mt5.history_deals_get(last_deal_time, datetime.now())

                if deals and len(deals) > 0:
                    logger.info(f"Detected {len(deals)} new deal(s)")

                    # Update last deal time
                    last_deal_time = datetime.now()

                    # Get full history for analysis
                    deals_df = self.get_historical_deals(days_back=30)
                    orders_df = self.get_historical_orders(days_back=30)

                    # Analyze
                    signature = self.identify_algorithm_type(deals_df, orders_df)

                    # Print summary
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                    print(f"Algorithm: {signature.likely_algorithm}")
                    print(f"Confidence: {signature.confidence * 100:.1f}%")

                    # Call callback if provided
                    if callback:
                        callback(signature, deals_df)

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")


def main():
    """Main function demonstrating usage"""
    import argparse

    parser = argparse.ArgumentParser(description='MT5 Algorithm Monitor')
    parser.add_argument('--account', type=int, help='MT5 account number')
    parser.add_argument('--password', type=str, help='MT5 account password')
    parser.add_argument('--server', type=str, help='MT5 broker server')
    parser.add_argument('--days', type=int, default=30, help='Days of history to analyze')
    parser.add_argument('--live', action='store_true', help='Enable live monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Live monitoring interval in seconds')

    args = parser.parse_args()

    # Create monitor instance
    monitor = MT5TradeMonitor(
        account=args.account,
        password=args.password,
        server=args.server
    )

    try:
        # Connect
        if not monitor.connect():
            logger.error("Failed to connect to MT5")
            return

        # Get account info
        account_info = monitor.get_account_info()
        logger.info(f"Connected to account: {account_info.get('login')} - {account_info.get('company')}")
        logger.info(f"Balance: {account_info.get('balance')} {account_info.get('currency')}")

        if args.live:
            # Live monitoring mode
            monitor.monitor_live(interval_seconds=args.interval)
        else:
            # One-time analysis
            logger.info(f"Analyzing last {args.days} days of trading history...")

            deals_df = monitor.get_historical_deals(days_back=args.days)
            orders_df = monitor.get_historical_orders(days_back=args.days)

            if deals_df.empty:
                logger.error("No trading history found")
                return

            logger.info(f"Analyzing {len(deals_df)} deals and {len(orders_df)} orders...")

            # Identify algorithm
            signature = monitor.identify_algorithm_type(deals_df, orders_df)

            # Generate and display report
            report = monitor.generate_report(signature)
            print("\n" + report)

            # Save reports
            txt_file, json_file = monitor.save_report(signature)
            logger.info(f"\nAnalysis complete! Reports saved to:")
            logger.info(f"  - {txt_file}")
            logger.info(f"  - {json_file}")

    finally:
        monitor.disconnect()


if __name__ == "__main__":
    main()
