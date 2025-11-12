"""
Advanced Analytics Module for MT5 Algorithm Detection
Provides additional analytical tools and visualizations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class AdvancedAnalytics:
    """Advanced analytics for trade pattern detection"""

    @staticmethod
    def detect_grid_trading(deals_df: pd.DataFrame, orders_df: pd.DataFrame) -> Dict:
        """
        Detect if the algorithm uses grid trading strategy

        Returns:
            Dictionary with grid trading indicators
        """
        if deals_df.empty or orders_df.empty:
            return {'is_grid': False, 'confidence': 0.0}

        results = {
            'is_grid': False,
            'confidence': 0.0,
            'evidence': []
        }

        # Group by symbol
        for symbol in deals_df['symbol'].unique():
            symbol_orders = orders_df[orders_df['symbol'] == symbol].copy()

            if len(symbol_orders) < 5:
                continue

            # Check for multiple pending orders at regular price intervals
            pending_orders = symbol_orders[symbol_orders['type'].isin([2, 3])]  # Buy limit, sell limit

            if len(pending_orders) >= 3:
                prices = pending_orders['price_open'].values
                price_diffs = np.diff(sorted(prices))

                if len(price_diffs) > 0:
                    # Check if price differences are relatively consistent
                    mean_diff = np.mean(price_diffs)
                    std_diff = np.std(price_diffs)

                    if std_diff < mean_diff * 0.3:  # Low variation in grid spacing
                        results['is_grid'] = True
                        results['confidence'] = 0.8
                        results['evidence'].append(
                            f"Regular price intervals detected for {symbol} (avg: {mean_diff:.5f})"
                        )
                        results['grid_spacing'] = float(mean_diff)

        return results

    @staticmethod
    def detect_news_trading(deals_df: pd.DataFrame) -> Dict:
        """
        Detect if trades are triggered around news events
        Looks for sudden bursts of trading activity
        """
        if deals_df.empty:
            return {'is_news_trading': False, 'confidence': 0.0}

        deals_df = deals_df.copy()
        deals_df = deals_df.sort_values('time')

        # Calculate time between trades
        time_diffs = deals_df['time'].diff().dt.total_seconds() / 60  # minutes

        # Look for clusters (multiple trades in short time after long gaps)
        threshold_short = 5  # 5 minutes
        threshold_long = 60  # 1 hour

        clusters = 0
        i = 0
        while i < len(time_diffs) - 2:
            if pd.notna(time_diffs.iloc[i]) and time_diffs.iloc[i] > threshold_long:
                # Check if next few trades are close together
                next_diffs = time_diffs.iloc[i+1:i+4]
                if (next_diffs < threshold_short).sum() >= 2:
                    clusters += 1
            i += 1

        cluster_ratio = clusters / len(deals_df) if len(deals_df) > 0 else 0

        results = {
            'is_news_trading': cluster_ratio > 0.1,
            'confidence': min(cluster_ratio * 5, 0.9),
            'clusters_detected': clusters,
            'cluster_ratio': float(cluster_ratio)
        }

        if results['is_news_trading']:
            results['evidence'] = [
                f"Detected {clusters} trading clusters",
                "Trading pattern suggests reaction to external events"
            ]

        return results

    @staticmethod
    def detect_correlation_trading(deals_df: pd.DataFrame) -> Dict:
        """
        Detect if algorithm trades correlated instruments simultaneously
        """
        if deals_df.empty:
            return {'is_correlation_trading': False, 'confidence': 0.0}

        deals_df = deals_df.copy()
        deals_df['time_rounded'] = deals_df['time'].dt.floor('1min')

        # Find simultaneous trades (within same minute)
        simultaneous_groups = deals_df.groupby('time_rounded')

        simultaneous_multi_symbol = 0
        total_time_points = 0

        for time_point, group in simultaneous_groups:
            total_time_points += 1
            if len(group['symbol'].unique()) > 1:
                simultaneous_multi_symbol += 1

        ratio = simultaneous_multi_symbol / total_time_points if total_time_points > 0 else 0

        results = {
            'is_correlation_trading': ratio > 0.3,
            'confidence': min(ratio * 2, 0.85),
            'simultaneous_ratio': float(ratio),
            'simultaneous_count': simultaneous_multi_symbol
        }

        if results['is_correlation_trading']:
            results['evidence'] = [
                f"Trades multiple symbols simultaneously in {simultaneous_multi_symbol} instances",
                "Suggests correlation-based or basket trading strategy"
            ]

        return results

    @staticmethod
    def analyze_entry_precision(deals_df: pd.DataFrame) -> Dict:
        """
        Analyze the precision of entry prices to detect algorithmic patterns
        """
        if deals_df.empty:
            return {}

        # Check decimal places used in entry prices
        prices = deals_df['price'].values

        # Count decimal places
        decimal_places = []
        for price in prices:
            price_str = f"{price:.10f}".rstrip('0')
            if '.' in price_str:
                decimals = len(price_str.split('.')[1])
                decimal_places.append(decimals)

        if not decimal_places:
            return {}

        decimal_counter = Counter(decimal_places)
        most_common_decimals, count = decimal_counter.most_common(1)[0]

        precision_ratio = count / len(decimal_places)

        results = {
            'most_common_decimal_places': most_common_decimals,
            'precision_consistency': float(precision_ratio),
            'is_algorithmic_precision': precision_ratio > 0.7
        }

        # Check for round numbers (prices ending in 0 or 5)
        round_prices = 0
        for price in prices:
            last_digit = int((price * 100) % 10)  # Get last significant digit
            if last_digit in [0, 5]:
                round_prices += 1

        round_ratio = round_prices / len(prices)
        results['round_number_ratio'] = float(round_ratio)

        if round_ratio > 0.5:
            results['evidence'] = ["High percentage of round-number entries suggests psychological levels or manual trading"]
        elif precision_ratio > 0.8:
            results['evidence'] = ["Consistent decimal precision suggests algorithmic entry"]

        return results

    @staticmethod
    def detect_hedging_strategy(deals_df: pd.DataFrame) -> Dict:
        """
        Detect if the algorithm uses hedging (opposite positions)
        """
        if deals_df.empty:
            return {'is_hedging': False, 'confidence': 0.0}

        deals_df = deals_df.copy()
        deals_df = deals_df.sort_values('time')

        hedging_instances = 0
        total_opportunities = 0

        # Group by symbol
        for symbol in deals_df['symbol'].unique():
            symbol_deals = deals_df[deals_df['symbol'] == symbol].copy()

            if len(symbol_deals) < 2:
                continue

            # Check for opposite positions within short time window
            for i in range(len(symbol_deals) - 1):
                total_opportunities += 1
                deal1 = symbol_deals.iloc[i]
                deal2 = symbol_deals.iloc[i + 1]

                time_diff = (deal2['time'] - deal1['time']).total_seconds() / 60

                # If opposite types within 10 minutes
                if time_diff < 10 and deal1['type'] != deal2['type']:
                    hedging_instances += 1

        hedging_ratio = hedging_instances / total_opportunities if total_opportunities > 0 else 0

        results = {
            'is_hedging': hedging_ratio > 0.3,
            'confidence': min(hedging_ratio * 2, 0.85),
            'hedging_ratio': float(hedging_ratio),
            'hedging_instances': hedging_instances
        }

        if results['is_hedging']:
            results['evidence'] = [
                f"Detected {hedging_instances} potential hedging instances",
                "Algorithm appears to use opposite positions for risk management"
            ]

        return results

    @staticmethod
    def calculate_sharpe_ratio(deals_df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio from trading results

        Args:
            deals_df: DataFrame with deals
            risk_free_rate: Annual risk-free rate (default 2%)

        Returns:
            Sharpe ratio
        """
        if deals_df.empty or len(deals_df) < 2:
            return 0.0

        # Calculate daily returns
        deals_df = deals_df.copy()
        deals_df['date'] = deals_df['time'].dt.date
        daily_profits = deals_df.groupby('date')['profit'].sum()

        if len(daily_profits) < 2:
            return 0.0

        # Calculate returns
        returns = daily_profits.values
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        # Annualize (assuming 252 trading days)
        daily_rf_rate = risk_free_rate / 252
        sharpe = (avg_return - daily_rf_rate) / std_return * np.sqrt(252)

        return float(sharpe)

    @staticmethod
    def calculate_maximum_drawdown(deals_df: pd.DataFrame) -> Dict:
        """
        Calculate maximum drawdown

        Returns:
            Dictionary with drawdown metrics
        """
        if deals_df.empty:
            return {'max_drawdown': 0.0, 'max_drawdown_pct': 0.0}

        deals_df = deals_df.copy()
        deals_df = deals_df.sort_values('time')

        # Calculate cumulative profit
        deals_df['cumulative_profit'] = deals_df['profit'].cumsum()

        # Calculate running maximum
        deals_df['running_max'] = deals_df['cumulative_profit'].cummax()

        # Calculate drawdown
        deals_df['drawdown'] = deals_df['running_max'] - deals_df['cumulative_profit']

        max_drawdown = deals_df['drawdown'].max()

        # Calculate percentage drawdown
        max_profit = deals_df['running_max'].max()
        max_drawdown_pct = (max_drawdown / max_profit * 100) if max_profit > 0 else 0

        # Find drawdown period
        max_dd_idx = deals_df['drawdown'].idxmax()
        dd_start_idx = deals_df.loc[:max_dd_idx, 'running_max'].idxmax()

        dd_start = deals_df.loc[dd_start_idx, 'time']
        dd_end = deals_df.loc[max_dd_idx, 'time']
        dd_duration = (dd_end - dd_start).days

        return {
            'max_drawdown': float(max_drawdown),
            'max_drawdown_pct': float(max_drawdown_pct),
            'drawdown_duration_days': dd_duration,
            'drawdown_start': dd_start,
            'drawdown_end': dd_end
        }

    @staticmethod
    def detect_scaling_in_out(deals_df: pd.DataFrame) -> Dict:
        """
        Detect if algorithm scales in/out of positions
        """
        if deals_df.empty:
            return {'is_scaling': False, 'confidence': 0.0}

        deals_df = deals_df.copy()
        deals_df = deals_df.sort_values('time')

        scaling_instances = 0

        # Group by symbol
        for symbol in deals_df['symbol'].unique():
            symbol_deals = deals_df[deals_df['symbol'] == symbol].copy()

            if len(symbol_deals) < 3:
                continue

            # Look for multiple same-direction entries
            consecutive_same_type = 1
            prev_type = None

            for deal_type in symbol_deals['type']:
                if deal_type == prev_type:
                    consecutive_same_type += 1
                    if consecutive_same_type >= 2:
                        scaling_instances += 1
                else:
                    consecutive_same_type = 1
                prev_type = deal_type

        results = {
            'is_scaling': scaling_instances > 0,
            'confidence': min(scaling_instances * 0.2, 0.85),
            'scaling_instances': scaling_instances
        }

        if results['is_scaling']:
            results['evidence'] = [
                f"Detected {scaling_instances} instances of position scaling",
                "Algorithm adds to winning/losing positions"
            ]

        return results

    @staticmethod
    def analyze_trade_duration(deals_df: pd.DataFrame) -> Dict:
        """
        Analyze typical trade duration

        Note: This requires matching entry/exit deals
        """
        if deals_df.empty:
            return {}

        deals_df = deals_df.copy()
        deals_df = deals_df.sort_values('time')

        # Group by position_id if available
        if 'position_id' in deals_df.columns:
            position_durations = []

            for pos_id in deals_df['position_id'].unique():
                pos_deals = deals_df[deals_df['position_id'] == pos_id]

                if len(pos_deals) >= 2:
                    duration = (pos_deals['time'].max() - pos_deals['time'].min()).total_seconds() / 60
                    position_durations.append(duration)

            if position_durations:
                return {
                    'avg_duration_minutes': float(np.mean(position_durations)),
                    'median_duration_minutes': float(np.median(position_durations)),
                    'min_duration_minutes': float(np.min(position_durations)),
                    'max_duration_minutes': float(np.max(position_durations)),
                    'std_duration_minutes': float(np.std(position_durations))
                }

        return {'note': 'Unable to calculate duration without position_id'}

    @staticmethod
    def generate_advanced_report(deals_df: pd.DataFrame, orders_df: pd.DataFrame) -> str:
        """
        Generate a comprehensive advanced analytics report

        Args:
            deals_df: DataFrame with deals
            orders_df: DataFrame with orders

        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "=" * 80)
        report.append("ADVANCED ANALYTICS REPORT")
        report.append("=" * 80)

        analytics = AdvancedAnalytics()

        # Grid trading detection
        grid_results = analytics.detect_grid_trading(deals_df, orders_df)
        report.append("\n[GRID TRADING ANALYSIS]")
        report.append(f"Is Grid Trading: {grid_results.get('is_grid', False)}")
        report.append(f"Confidence: {grid_results.get('confidence', 0) * 100:.1f}%")
        if 'evidence' in grid_results:
            for evidence in grid_results['evidence']:
                report.append(f"  - {evidence}")

        # News trading detection
        news_results = analytics.detect_news_trading(deals_df)
        report.append("\n[NEWS TRADING ANALYSIS]")
        report.append(f"Is News Trading: {news_results.get('is_news_trading', False)}")
        report.append(f"Confidence: {news_results.get('confidence', 0) * 100:.1f}%")
        report.append(f"Clusters Detected: {news_results.get('clusters_detected', 0)}")

        # Correlation trading
        corr_results = analytics.detect_correlation_trading(deals_df)
        report.append("\n[CORRELATION TRADING ANALYSIS]")
        report.append(f"Is Correlation Trading: {corr_results.get('is_correlation_trading', False)}")
        report.append(f"Confidence: {corr_results.get('confidence', 0) * 100:.1f}%")

        # Hedging
        hedge_results = analytics.detect_hedging_strategy(deals_df)
        report.append("\n[HEDGING ANALYSIS]")
        report.append(f"Uses Hedging: {hedge_results.get('is_hedging', False)}")
        report.append(f"Confidence: {hedge_results.get('confidence', 0) * 100:.1f}%")

        # Scaling
        scale_results = analytics.detect_scaling_in_out(deals_df)
        report.append("\n[POSITION SCALING ANALYSIS]")
        report.append(f"Uses Scaling: {scale_results.get('is_scaling', False)}")
        report.append(f"Scaling Instances: {scale_results.get('scaling_instances', 0)}")

        # Entry precision
        precision_results = analytics.analyze_entry_precision(deals_df)
        report.append("\n[ENTRY PRECISION ANALYSIS]")
        report.append(f"Most Common Decimal Places: {precision_results.get('most_common_decimal_places', 'N/A')}")
        report.append(f"Precision Consistency: {precision_results.get('precision_consistency', 0) * 100:.1f}%")
        report.append(f"Algorithmic Precision: {precision_results.get('is_algorithmic_precision', False)}")

        # Performance metrics
        sharpe = analytics.calculate_sharpe_ratio(deals_df)
        report.append("\n[PERFORMANCE METRICS]")
        report.append(f"Sharpe Ratio: {sharpe:.2f}")

        drawdown_metrics = analytics.calculate_maximum_drawdown(deals_df)
        report.append(f"Maximum Drawdown: {drawdown_metrics.get('max_drawdown', 0):.2f}")
        report.append(f"Maximum Drawdown %: {drawdown_metrics.get('max_drawdown_pct', 0):.2f}%")
        report.append(f"Drawdown Duration: {drawdown_metrics.get('drawdown_duration_days', 0)} days")

        # Trade duration
        duration_results = analytics.analyze_trade_duration(deals_df)
        if 'avg_duration_minutes' in duration_results:
            report.append("\n[TRADE DURATION ANALYSIS]")
            report.append(f"Average Duration: {duration_results['avg_duration_minutes']:.1f} minutes")
            report.append(f"Median Duration: {duration_results['median_duration_minutes']:.1f} minutes")
            report.append(f"Min Duration: {duration_results['min_duration_minutes']:.1f} minutes")
            report.append(f"Max Duration: {duration_results['max_duration_minutes']:.1f} minutes")

        report.append("\n" + "=" * 80)

        return "\n".join(report)
