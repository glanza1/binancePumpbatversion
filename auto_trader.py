import pandas as pd
import numpy as np
import json
import datetime as dt
import operator
from binance.enums import *
from binance import ThreadedWebsocketManager
from pricechange import *
from binanceHelper import *
from pricegroup import *
import signal
import threading
import sys
from typing import Dict, List
from trader import Trader # [NEW] Import Trader Class

# --- Global Config ---
show_only_pair = "USDT" 
show_limit = 1      
min_perc = 0.05     

# --- Global State ---
price_changes: List[PriceChange] = []
price_groups: Dict[str, PriceGroup] = {}
last_symbol = "X"
chat_ids = []
twm: ThreadedWebsocketManager = None
trader: Trader = None # [NEW] Global Trader Instance

def get_price_groups() -> List[PriceGroup]:
    return list(price_groups.values())

def process_message(tickers):
    current_prices = {} # [NEW] Track current prices for Trader

    for ticker in tickers:
        symbol = ticker['s']

        if not show_only_pair in symbol:
            continue
        
        # [NEW] Capture price for exit logic
        try:
            price = float(ticker['c'])
            current_prices[symbol] = price
        except:
            continue

        total_trades = int(ticker['n'])
        open_p = float(ticker['o'])
        volume = float(ticker['v'])
        event_time = dt.datetime.fromtimestamp(int(ticker['E'])/1000)
        
        # --- Existing Logic Reuse ---
        if len(price_changes) > 0:
            price_change = filter(lambda item: item.symbol == symbol, price_changes)
            price_change = list(price_change)
            if (len(price_change) > 0):
                price_change = price_change[0]
                price_change.event_time = event_time
                price_change.prev_price = price_change.price
                price_change.prev_volume = price_change.volume
                price_change.price = price
                price_change.total_trades = total_trades
                price_change.open = open_p
                price_change.volume = volume
                price_change.is_printed = False
            else:
                price_changes.append(PriceChange(symbol, price, price, total_trades, open_p, volume, False, event_time, volume))
        else:
            price_changes.append(PriceChange(symbol, price, price, total_trades, open_p, volume, False, event_time, volume))

    # --- Signal Detection ---
    price_changes.sort(key=operator.attrgetter('price_change_perc'), reverse=True)
    
    for price_change in price_changes:
        if (not price_change.is_printed 
            and abs(price_change.price_change_perc) > min_perc 
            and price_change.volume_change_perc > min_perc):

            price_change.is_printed = True 

            # [NEW] BUY SIGNAL
            if price_change.price_change_perc > 0: # Only Buy on Positive Pump
                trader.buy_market(price_change.symbol, price_change.price)

            # --- Existing Grouping Logic ---
            if not price_change.symbol in price_groups:
                price_groups[price_change.symbol] = PriceGroup(price_change.symbol,                                                                
                                                            1,                                                                
                                                            abs(price_change.price_change_perc),
                                                            price_change.price_change_perc,
                                                            price_change.volume_change_perc,                                                                
                                                            price_change.price,                                                                                                                             
                                                            price_change.event_time,
                                                            price_change.open_price,
                                                            price_change.volume,
                                                            False,
                                                            )
            else:
                price_groups[price_change.symbol].tick_count += 1
                price_groups[price_change.symbol].last_event_time = price_change.event_time
                price_groups[price_change.symbol].volume = price_change.volume
                price_groups[price_change.symbol].last_price = price_change.price
                price_groups[price_change.symbol].is_printed = False
                price_groups[price_change.symbol].total_price_change += abs(price_change.price_change_perc)
                price_groups[price_change.symbol].relative_price_change += price_change.price_change_perc
                price_groups[price_change.symbol].total_volume_change += price_change.volume_change_perc                

    # --- [NEW] EXIT LOGIC ---
    # Check open positions for TP/SL using latest prices
    trader.check_positions(current_prices)

    # --- Display Logic (Optional, keep for visibility) ---
    if len(price_groups)>0:
        anyPrinted = False 
        sorted_price_group = sorted(price_groups, key=lambda k:price_groups[k]['tick_count'])
        if (len(sorted_price_group)>0):
            sorted_price_group = list(reversed(sorted_price_group))
            for s in range(show_limit):
                header_printed=False
                if (s<len(sorted_price_group)):
                    max_price_group = sorted_price_group[s]
                    max_price_group = price_groups[max_price_group]
                    if not max_price_group.is_printed:
                        if not header_printed:
                            msg = "Top Ticks"
                            print(msg)
                            header_printed = True
                        print(max_price_group.to_string(True))
                        anyPrinted = True
                        
        # (Skipping other prints to keep console cleaner for bot focus, 
        # but re-enabling them if strictly cloning logic. Let's keep them all.)
        
        sorted_price_group = sorted(price_groups, key=lambda k:price_groups[k]['total_price_change'])
        if (len(sorted_price_group)>0):
            sorted_price_group = list(reversed(sorted_price_group))
            for s in range(show_limit):
                header_printed=False
                if (s<len(sorted_price_group)):
                    max_price_group = sorted_price_group[s]
                    max_price_group = price_groups[max_price_group]
                    if not max_price_group.is_printed:
                        if not header_printed:
                            msg = "Top Total Price Change"
                            print(msg)
                            header_printed = True
                        print(max_price_group.to_string(True))
                        anyPrinted = True

        sorted_price_group = sorted(price_groups, key=lambda k:abs(price_groups[k]['relative_price_change']))
        if (len(sorted_price_group)>0):
            sorted_price_group = list(reversed(sorted_price_group))
            for s in range(show_limit):
                header_printed=False
                if (s<len(sorted_price_group)):
                    max_price_group = sorted_price_group[s]
                    max_price_group = price_groups[max_price_group]
                    if not max_price_group.is_printed:
                        if not header_printed:
                            msg = "Top Relative Price Change"
                            print(msg)
                            header_printed = True
                        print(max_price_group.to_string(True))
                        anyPrinted = True

        sorted_price_group = sorted(price_groups, key=lambda k:price_groups[k]['total_volume_change'])
        if (len(sorted_price_group)>0):
            sorted_price_group = list(reversed(sorted_price_group))
            for s in range(show_limit):
                header_printed=False
                if (s<len(sorted_price_group)):
                    max_price_group = sorted_price_group[s]
                    max_price_group = price_groups[max_price_group]
                    if not max_price_group.is_printed:
                        if not header_printed:
                            msg = "Top Total Volume Change"
                            print(msg)
                            header_printed = True
                        print(max_price_group.to_string(True))
                        anyPrinted = True

        if anyPrinted:
            print("")

def stop():
    twm.stop()

def main():
    global twm
    global trader

    #READ API CONFIG
    api_config = {}
    with open('api_config.json') as json_data:
        api_config = json.load(json_data)
        json_data.close()

    api_key = api_config['api_key']
    api_secret = api_config['api_secret']
    
    # [NEW] Initialize Trader
    # NOTE: You can change parameters here
    trader = Trader(api_key, api_secret, dry_run=True, trade_amount=100)

    # Create an Event that signals “stop everything”
    stop_event = threading.Event()

    def handle_exit(signum, frame):
        print("\nShutting down…")
        stop_event.set()
        twm.stop() 

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Start the threaded websocket manager
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()
    twm.start_ticker_socket(process_message)
    
    print("Auto Trader Websocket running. Press Ctrl+C to exit.")

    stop_event.wait()

    print("Clean exit complete.")
    return
    
if __name__ == '__main__':
    main()
