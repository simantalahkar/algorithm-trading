# Algorithmic Trading
**This an implementation of a trading strategy (only 'option selling') using pivot points in python. This code is for reference only and I take no responsibility for someone else running this code in their account and the resulting profits or losses that might occur.**

This code is based on the 'fyers' trading account and the fyers API. A working version of the fyers api needs to be installed, and activated. However, most of the code is transferable to other trading accounts and corresponding APIs with minor changes. 

Before running this python script, the client_id and the (daily) access_token needs to be added.
This code is written to execute trades in "NIFTY 50" and "BANK NIFTY" _options_ (in the indian stock exchanges: NSE or BSE).
Some of the values that needs to be updated in the code according to the trade requirements before running are:
1. The entry time.
2. The difference between strike and spot (otm variable).
3. stop loss, target and previous day's high, low and closing price.

In order to take actual trades, the 'papertrading' variable (in the placeOrderFyers function) needs to be changed from 0 to 1.
