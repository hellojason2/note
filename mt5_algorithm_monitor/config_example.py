"""
Configuration Example for MT5 Algorithm Monitor
Copy this file to config.py and fill in your details
"""

# MT5 Connection Settings
MT5_CONFIG = {
    'account': None,  # Your MT5 account number (int) or None if already logged in
    'password': '',   # Your MT5 password (str) - leave empty if already logged in
    'server': '',     # Your broker's server name (str) - leave empty if already logged in
}

# Analysis Settings
ANALYSIS_CONFIG = {
    'days_back': 30,              # Number of days to analyze
    'min_trades_required': 10,    # Minimum trades needed for analysis
    'confidence_threshold': 0.7,  # Minimum confidence for pattern detection
}

# Live Monitoring Settings
MONITORING_CONFIG = {
    'enabled': False,             # Enable live monitoring
    'interval_seconds': 60,       # Check for new trades every N seconds
    'auto_save_reports': True,    # Automatically save analysis reports
    'report_directory': './reports',  # Directory to save reports
}

# Visualization Settings
VISUALIZATION_CONFIG = {
    'enabled': True,              # Enable chart generation
    'auto_generate': True,        # Auto-generate charts after analysis
    'chart_directory': './charts',  # Directory to save charts
    'chart_style': 'darkgrid',    # seaborn style: darkgrid, whitegrid, dark, white, ticks
    'dpi': 300,                   # Chart resolution (dots per inch)
}

# Advanced Analytics Settings
ADVANCED_ANALYTICS_CONFIG = {
    'enabled': True,              # Enable advanced analytics
    'detect_grid': True,          # Detect grid trading
    'detect_news': True,          # Detect news trading
    'detect_correlation': True,   # Detect correlation trading
    'detect_hedging': True,       # Detect hedging strategies
    'calculate_sharpe': True,     # Calculate Sharpe ratio
    'risk_free_rate': 0.02,      # Risk-free rate for Sharpe calculation (2%)
}

# Logging Settings
LOGGING_CONFIG = {
    'level': 'INFO',              # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file': 'mt5_monitor.log',    # Log file name
    'console_output': True,       # Also output to console
}

# Export Settings
EXPORT_CONFIG = {
    'save_text_report': True,     # Save .txt report
    'save_json_report': True,     # Save .json report
    'save_csv_data': True,        # Save raw data as CSV
}
