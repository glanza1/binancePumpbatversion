import logging
from binance.client import Client
from binance.enums import *
from datetime import datetime
from termcolor import colored

class Trader:
    def __init__(self, api_key, api_secret, dry_run=True, trade_amount=100, tp_perc=2.0, sl_perc=2.0):
        self.client = None
        self.dry_run = dry_run
        self.trade_amount = trade_amount  # USDT per trade
        self.tp_perc = tp_perc # +%
        self.sl_perc = sl_perc # -%
        self.positions = {} # {symbol: {'entry_price': float, 'amount': float, 'entry_time': datetime}}
        
        # Performance Tracking
        self.total_pnl = 0.0
        self.successful_trades = 0
        self.failed_trades = 0

        print(colored("Trader Module Initialized", "cyan"))
        print(colored(f"Mode: {'DRY RUN (Paper Trading)' if dry_run else 'REAL TRADING'}", "yellow" if dry_run else "red"))
        print(colored(f"Risk Management: TP={tp_perc}%, SL={sl_perc}%", "cyan"))

        if not self.dry_run:
            try:
                self.client = Client(api_key, api_secret)
                print(colored("Binance API Connected", "green"))
            except Exception as e:
                print(colored(f"API Connection Error: {e}", "red"))
                self.dry_run = True # Fallback to dry run
                print(colored("Fallback to DRY RUN mode due to API error", "yellow"))

    def buy_market(self, symbol, current_price):
        """
        Executes a Buy Market order.
        """
        if symbol in self.positions:
            # Already have a position, skip
            return

        timestamp = datetime.now()
        
        # Calculate quantity (Simulated)
        quantity = self.trade_amount / current_price

        if self.dry_run:
            print(colored(f"[SIMULATED BUY] {symbol} @ {current_price}", "green"))
            self.positions[symbol] = {
                'entry_price': current_price,
                'quantity': quantity,
                'entry_time': timestamp
            }
        else:
            try:
                # Real Order Logic (Simplified - requires precise quantity rounding in production)
                # For safety in this demo, we might strictly stick to simulation or careful implementation
                # This is a placeholder for the real API call
                # order = self.client.create_order(
                #     symbol=symbol,
                #     side=SIDE_BUY,
                #     type=ORDER_TYPE_MARKET,
                #     quoteOrderQty=self.trade_amount
                # )
                # real_price = float(order['fills'][0]['price']) # Simplified
                pass
            except Exception as e:
                print(colored(f"[BUY ERROR] {e}", "red"))
                return

    def sell_market(self, symbol, current_price, reason="MANUAL"):
        """
        Executes a Sell Market order (Exit position).
        """
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        entry_price = position['entry_price']
        quantity = position['quantity']
        
        # Calculate PnL
        pnl = (current_price - entry_price) * quantity
        pnl_perc = ((current_price - entry_price) / entry_price) * 100

        if self.dry_run:
            color = "green" if pnl > 0 else "red"
            print(colored(f"[SIMULATED SELL] {symbol} @ {current_price} | Reason: {reason}", color))
            print(colored(f"PnL: {pnl:.2f} USDT ({pnl_perc:.2f}%)", color))
            
            # Update Stats
            self.total_pnl += pnl
            if pnl > 0:
                self.successful_trades += 1
            else:
                self.failed_trades += 1
                
            del self.positions[symbol]
        else:
            # Real API Sell Logic
            pass

    def check_positions(self, current_prices):
        """
        Checks all active positions against TP and SL levels.
        current_prices: dict {symbol: price}
        """
        # Create a copy of keys to modify dict during iteration
        active_symbols = list(self.positions.keys())
        
        for symbol in active_symbols:
            if symbol not in current_prices:
                continue
                
            current_price = current_prices[symbol]
            position = self.positions[symbol]
            entry_price = position['entry_price']
            
            # Calculate Percentage Change
            change_perc = ((current_price - entry_price) / entry_price) * 100
            
            # Check Take Profit
            if change_perc >= self.tp_perc:
                self.sell_market(symbol, current_price, reason=f"TP Hit (+{change_perc:.2f}%)")
            
            # Check Stop Loss
            elif change_perc <= -self.sl_perc:
                self.sell_market(symbol, current_price, reason=f"SL Hit ({change_perc:.2f}%)")

            # Optional: Trailing Stop could be added here
