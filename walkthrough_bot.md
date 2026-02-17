# Auto Trading Bot Walkthrough

## Overview
We have successfully converted the signal analysis tool into an automated trading bot. The existing `binancePump.py` remains untouched, while a new standalone bot `auto_trader.py` has been created alongside a `trader.py` engine.

## New Files
- **`trader.py`**: The "Engine". Handles Buy/Sell logic, position tracking, and PnL calculation.
- **`auto_trader.py`**: The "App". Listens to Binance Websocket, detects pumps, and commands the Trader to execute orders.

## How to Run
1. Ensure your `api_config.json` is correctly set up with your Binance API Keys.
2. Run the bot:
   ```bash
   python3 auto_trader.py
   ```

## Features & Config
- **Dry Run (Paper Trading)**: Enabled by default. The bot will simulate trades and print "SIMULATED BUY/SELL" without using real money.
- **Risk Management**:
    - **Take Profit (TP)**: +2% (Default)
    - **Stop Loss (SL)**: -2% (Default)
    - **Trade Size**: 100 USDT (Simulated)

To change these settings, edit `auto_trader.py` line 204:
```python
trader = Trader(api_key, api_secret, dry_run=True, trade_amount=100)
```
Set `dry_run=False` to enable **REAL TRADING**.

> [!WARNING]
> Real trading involves financial risk. Always test thoroughly in Dry Run mode first.
