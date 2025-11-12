"""
Visualization Module for MT5 Algorithm Monitor
Generates charts and graphs for trade analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Try to import matplotlib and seaborn
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available. Visualization features disabled.")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    logger.warning("Seaborn not available. Some visualization features disabled.")


class TradeVisualizer:
    """Visualizer for trade data and patterns"""

    def __init__(self, style='darkgrid'):
        """
        Initialize visualizer

        Args:
            style: Plot style (darkgrid, whitegrid, dark, white, ticks)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required for visualization")
            return

        if SEABORN_AVAILABLE:
            sns.set_style(style)

        self.colors = {
            'profit': '#2ecc71',
            'loss': '#e74c3c',
            'neutral': '#95a5a6',
            'buy': '#3498db',
            'sell': '#e67e22'
        }

    def plot_equity_curve(self, deals_df: pd.DataFrame, save_path: str = None):
        """
        Plot equity curve over time

        Args:
            deals_df: DataFrame with deals
            save_path: Path to save the plot (optional)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required")
            return

        if deals_df.empty:
            logger.warning("No data to plot")
            return

        deals_df = deals_df.sort_values('time')
        deals_df['cumulative_profit'] = deals_df['profit'].cumsum()

        fig, ax = plt.subplots(figsize=(14, 6))

        ax.plot(deals_df['time'], deals_df['cumulative_profit'],
                linewidth=2, color='#3498db', label='Equity Curve')
        ax.fill_between(deals_df['time'], 0, deals_df['cumulative_profit'],
                        alpha=0.3, color='#3498db')

        # Mark drawdowns
        running_max = deals_df['cumulative_profit'].cummax()
        drawdown = running_max - deals_df['cumulative_profit']
        is_drawdown = drawdown > 0

        if is_drawdown.any():
            ax.fill_between(deals_df['time'], deals_df['cumulative_profit'],
                          running_max, where=is_drawdown,
                          alpha=0.3, color='#e74c3c', label='Drawdown')

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Profit', fontsize=12)
        ax.set_title('Equity Curve Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Equity curve saved to {save_path}")

        plt.show()

    def plot_trade_distribution(self, deals_df: pd.DataFrame, save_path: str = None):
        """
        Plot profit/loss distribution

        Args:
            deals_df: DataFrame with deals
            save_path: Path to save the plot (optional)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required")
            return

        if deals_df.empty:
            logger.warning("No data to plot")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Profit/Loss histogram
        profits = deals_df[deals_df['profit'] > 0]['profit']
        losses = deals_df[deals_df['profit'] < 0]['profit']

        axes[0, 0].hist(profits, bins=30, alpha=0.7, color=self.colors['profit'],
                       label=f'Profits (n={len(profits)})')
        axes[0, 0].hist(losses, bins=30, alpha=0.7, color=self.colors['loss'],
                       label=f'Losses (n={len(losses)})')
        axes[0, 0].set_xlabel('Profit/Loss', fontsize=10)
        axes[0, 0].set_ylabel('Frequency', fontsize=10)
        axes[0, 0].set_title('Profit/Loss Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Win/Loss ratio pie chart
        win_count = len(profits)
        loss_count = len(losses)
        be_count = len(deals_df[deals_df['profit'] == 0])

        axes[0, 1].pie([win_count, loss_count, be_count],
                      labels=['Wins', 'Losses', 'Break Even'],
                      colors=[self.colors['profit'], self.colors['loss'], self.colors['neutral']],
                      autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Win/Loss Ratio', fontsize=12, fontweight='bold')

        # 3. Volume distribution
        axes[1, 0].hist(deals_df['volume'], bins=30, alpha=0.7,
                       color=self.colors['buy'], edgecolor='black')
        axes[1, 0].set_xlabel('Lot Size', fontsize=10)
        axes[1, 0].set_ylabel('Frequency', fontsize=10)
        axes[1, 0].set_title('Position Size Distribution', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. Profit by symbol
        symbol_profits = deals_df.groupby('symbol')['profit'].sum().sort_values()
        colors = [self.colors['profit'] if x > 0 else self.colors['loss']
                 for x in symbol_profits.values]

        axes[1, 1].barh(symbol_profits.index, symbol_profits.values, color=colors)
        axes[1, 1].set_xlabel('Total Profit', fontsize=10)
        axes[1, 1].set_title('Profit by Symbol', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Trade distribution saved to {save_path}")

        plt.show()

    def plot_time_analysis(self, deals_df: pd.DataFrame, save_path: str = None):
        """
        Plot time-based analysis (trading hours, days, etc.)

        Args:
            deals_df: DataFrame with deals
            save_path: Path to save the plot (optional)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required")
            return

        if deals_df.empty:
            logger.warning("No data to plot")
            return

        deals_df = deals_df.copy()
        deals_df['hour'] = deals_df['time'].dt.hour
        deals_df['day_of_week'] = deals_df['time'].dt.dayofweek
        deals_df['date'] = deals_df['time'].dt.date

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Trades by hour of day
        hour_counts = deals_df['hour'].value_counts().sort_index()
        axes[0, 0].bar(hour_counts.index, hour_counts.values,
                      color=self.colors['buy'], alpha=0.7)
        axes[0, 0].set_xlabel('Hour of Day', fontsize=10)
        axes[0, 0].set_ylabel('Number of Trades', fontsize=10)
        axes[0, 0].set_title('Trading Activity by Hour', fontsize=12, fontweight='bold')
        axes[0, 0].set_xticks(range(0, 24))
        axes[0, 0].grid(True, alpha=0.3, axis='y')

        # 2. Trades by day of week
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_counts = deals_df['day_of_week'].value_counts().sort_index()
        axes[0, 1].bar([day_names[i] for i in day_counts.index],
                      day_counts.values, color=self.colors['sell'], alpha=0.7)
        axes[0, 1].set_xlabel('Day of Week', fontsize=10)
        axes[0, 1].set_ylabel('Number of Trades', fontsize=10)
        axes[0, 1].set_title('Trading Activity by Day of Week', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # 3. Profit by hour
        hour_profit = deals_df.groupby('hour')['profit'].sum()
        colors = [self.colors['profit'] if x > 0 else self.colors['loss']
                 for x in hour_profit.values]
        axes[1, 0].bar(hour_profit.index, hour_profit.values, color=colors, alpha=0.7)
        axes[1, 0].set_xlabel('Hour of Day', fontsize=10)
        axes[1, 0].set_ylabel('Total Profit', fontsize=10)
        axes[1, 0].set_title('Profit by Hour of Day', fontsize=12, fontweight='bold')
        axes[1, 0].set_xticks(range(0, 24))
        axes[1, 0].axhline(y=0, color='black', linestyle='--', linewidth=1)
        axes[1, 0].grid(True, alpha=0.3, axis='y')

        # 4. Daily trade count over time
        daily_counts = deals_df.groupby('date').size()
        axes[1, 1].plot(daily_counts.index, daily_counts.values,
                       marker='o', linewidth=1.5, markersize=4, color=self.colors['buy'])
        axes[1, 1].set_xlabel('Date', fontsize=10)
        axes[1, 1].set_ylabel('Number of Trades', fontsize=10)
        axes[1, 1].set_title('Daily Trading Frequency', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Time analysis saved to {save_path}")

        plt.show()

    def plot_drawdown(self, deals_df: pd.DataFrame, save_path: str = None):
        """
        Plot drawdown analysis

        Args:
            deals_df: DataFrame with deals
            save_path: Path to save the plot (optional)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required")
            return

        if deals_df.empty:
            logger.warning("No data to plot")
            return

        deals_df = deals_df.sort_values('time')
        deals_df['cumulative_profit'] = deals_df['profit'].cumsum()
        deals_df['running_max'] = deals_df['cumulative_profit'].cummax()
        deals_df['drawdown'] = deals_df['running_max'] - deals_df['cumulative_profit']
        deals_df['drawdown_pct'] = (deals_df['drawdown'] / deals_df['running_max']) * 100

        fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

        # 1. Equity curve with drawdown
        axes[0].plot(deals_df['time'], deals_df['cumulative_profit'],
                    linewidth=2, color='#3498db', label='Equity')
        axes[0].plot(deals_df['time'], deals_df['running_max'],
                    linewidth=1, color='#2ecc71', linestyle='--', label='Peak Equity')
        axes[0].fill_between(deals_df['time'], deals_df['cumulative_profit'],
                           deals_df['running_max'], alpha=0.3, color='#e74c3c')
        axes[0].set_ylabel('Cumulative Profit', fontsize=10)
        axes[0].set_title('Equity Curve and Drawdown', fontsize=12, fontweight='bold')
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3)

        # 2. Drawdown percentage
        axes[1].fill_between(deals_df['time'], 0, -deals_df['drawdown_pct'],
                           color='#e74c3c', alpha=0.6)
        axes[1].set_xlabel('Date', fontsize=10)
        axes[1].set_ylabel('Drawdown %', fontsize=10)
        axes[1].set_title('Drawdown Percentage', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        # Mark maximum drawdown
        max_dd_idx = deals_df['drawdown_pct'].idxmax()
        max_dd_date = deals_df.loc[max_dd_idx, 'time']
        max_dd_value = deals_df.loc[max_dd_idx, 'drawdown_pct']

        axes[1].plot(max_dd_date, -max_dd_value, 'ro', markersize=10,
                    label=f'Max DD: {max_dd_value:.2f}%')
        axes[1].legend(loc='best')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Drawdown analysis saved to {save_path}")

        plt.show()

    def plot_performance_heatmap(self, deals_df: pd.DataFrame, save_path: str = None):
        """
        Plot performance heatmap (hour vs day of week)

        Args:
            deals_df: DataFrame with deals
            save_path: Path to save the plot (optional)
        """
        if not MATPLOTLIB_AVAILABLE or not SEABORN_AVAILABLE:
            logger.error("Matplotlib and Seaborn are required")
            return

        if deals_df.empty:
            logger.warning("No data to plot")
            return

        deals_df = deals_df.copy()
        deals_df['hour'] = deals_df['time'].dt.hour
        deals_df['day_of_week'] = deals_df['time'].dt.dayofweek

        # Create pivot table
        pivot = deals_df.pivot_table(values='profit', index='hour',
                                     columns='day_of_week', aggfunc='sum', fill_value=0)

        # Rename columns
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        pivot.columns = [day_names[i] if i < len(day_names) else str(i)
                        for i in pivot.columns]

        fig, ax = plt.subplots(figsize=(12, 10))

        sns.heatmap(pivot, cmap='RdYlGn', center=0, annot=True, fmt='.0f',
                   cbar_kws={'label': 'Profit'}, linewidths=0.5, ax=ax)

        ax.set_xlabel('Day of Week', fontsize=12)
        ax.set_ylabel('Hour of Day', fontsize=12)
        ax.set_title('Profit Heatmap (Hour vs Day)', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance heatmap saved to {save_path}")

        plt.show()

    def create_dashboard(self, deals_df: pd.DataFrame, orders_df: pd.DataFrame = None,
                        save_path: str = None):
        """
        Create a comprehensive dashboard with all visualizations

        Args:
            deals_df: DataFrame with deals
            orders_df: DataFrame with orders (optional)
            save_path: Path to save the dashboard (optional)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required")
            return

        if deals_df.empty:
            logger.warning("No data to plot")
            return

        # Create subplots
        fig = plt.figure(figsize=(20, 14))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        deals_df = deals_df.copy()
        deals_df = deals_df.sort_values('time')

        # 1. Equity Curve (top row, full width)
        ax1 = fig.add_subplot(gs[0, :])
        deals_df['cumulative_profit'] = deals_df['profit'].cumsum()
        ax1.plot(deals_df['time'], deals_df['cumulative_profit'],
                linewidth=2, color='#3498db')
        ax1.fill_between(deals_df['time'], 0, deals_df['cumulative_profit'],
                        alpha=0.3, color='#3498db')
        ax1.set_ylabel('Cumulative Profit', fontsize=10)
        ax1.set_title('Equity Curve', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # 2. Profit Distribution
        ax2 = fig.add_subplot(gs[1, 0])
        profits = deals_df[deals_df['profit'] > 0]['profit']
        losses = deals_df[deals_df['profit'] < 0]['profit']
        ax2.hist(profits, bins=20, alpha=0.7, color=self.colors['profit'], label='Profits')
        ax2.hist(losses, bins=20, alpha=0.7, color=self.colors['loss'], label='Losses')
        ax2.set_xlabel('Profit/Loss', fontsize=9)
        ax2.set_ylabel('Frequency', fontsize=9)
        ax2.set_title('P/L Distribution', fontsize=11, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)

        # 3. Win Rate Pie
        ax3 = fig.add_subplot(gs[1, 1])
        win_count = len(profits)
        loss_count = len(losses)
        ax3.pie([win_count, loss_count],
               labels=['Wins', 'Losses'],
               colors=[self.colors['profit'], self.colors['loss']],
               autopct='%1.1f%%', startangle=90)
        ax3.set_title('Win/Loss Ratio', fontsize=11, fontweight='bold')

        # 4. Trading Hours
        ax4 = fig.add_subplot(gs[1, 2])
        deals_df['hour'] = deals_df['time'].dt.hour
        hour_counts = deals_df['hour'].value_counts().sort_index()
        ax4.bar(hour_counts.index, hour_counts.values, color=self.colors['buy'], alpha=0.7)
        ax4.set_xlabel('Hour', fontsize=9)
        ax4.set_ylabel('Trades', fontsize=9)
        ax4.set_title('Activity by Hour', fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

        # 5. Profit by Symbol
        ax5 = fig.add_subplot(gs[2, 0])
        symbol_profits = deals_df.groupby('symbol')['profit'].sum().sort_values()
        colors = [self.colors['profit'] if x > 0 else self.colors['loss']
                 for x in symbol_profits.values]
        ax5.barh(symbol_profits.index, symbol_profits.values, color=colors)
        ax5.set_xlabel('Profit', fontsize=9)
        ax5.set_title('Profit by Symbol', fontsize=11, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='x')

        # 6. Volume Distribution
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.hist(deals_df['volume'], bins=20, alpha=0.7,
                color=self.colors['sell'], edgecolor='black')
        ax6.set_xlabel('Lot Size', fontsize=9)
        ax6.set_ylabel('Frequency', fontsize=9)
        ax6.set_title('Position Size Distribution', fontsize=11, fontweight='bold')
        ax6.grid(True, alpha=0.3)

        # 7. Daily Trade Count
        ax7 = fig.add_subplot(gs[2, 2])
        deals_df['date'] = deals_df['time'].dt.date
        daily_counts = deals_df.groupby('date').size()
        ax7.plot(daily_counts.index, daily_counts.values,
                marker='o', linewidth=1.5, markersize=3, color=self.colors['buy'])
        ax7.set_xlabel('Date', fontsize=9)
        ax7.set_ylabel('Trades', fontsize=9)
        ax7.set_title('Daily Trade Count', fontsize=11, fontweight='bold')
        ax7.grid(True, alpha=0.3)

        # Overall title
        fig.suptitle('MT5 Trading Algorithm Dashboard', fontsize=16, fontweight='bold', y=0.995)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Dashboard saved to {save_path}")

        plt.show()


def generate_all_visualizations(deals_df: pd.DataFrame, orders_df: pd.DataFrame = None,
                                output_dir: str = './charts'):
    """
    Generate all visualizations and save to directory

    Args:
        deals_df: DataFrame with deals
        orders_df: DataFrame with orders (optional)
        output_dir: Directory to save charts
    """
    import os

    if not MATPLOTLIB_AVAILABLE:
        logger.error("Matplotlib is required for visualization")
        return

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    visualizer = TradeVisualizer()

    logger.info("Generating visualizations...")

    try:
        visualizer.plot_equity_curve(deals_df, f"{output_dir}/equity_curve.png")
        visualizer.plot_trade_distribution(deals_df, f"{output_dir}/trade_distribution.png")
        visualizer.plot_time_analysis(deals_df, f"{output_dir}/time_analysis.png")
        visualizer.plot_drawdown(deals_df, f"{output_dir}/drawdown_analysis.png")

        if SEABORN_AVAILABLE:
            visualizer.plot_performance_heatmap(deals_df, f"{output_dir}/performance_heatmap.png")

        visualizer.create_dashboard(deals_df, orders_df, f"{output_dir}/dashboard.png")

        logger.info(f"All visualizations saved to {output_dir}/")

    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
