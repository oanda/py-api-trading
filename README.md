OANDA API Trading Utilities in Python
==============

Sample programs trading with the OANDA API through Python2.7

This repo contains a trading program that executes trades when WMA and SMA cross.
There is also a file containing a few extremely simple functions which will open a trade or an order respectively.

### Installation

* Clone this repo to the location of your choice
* Modify api-order.py to do whatever you wish, or simply run api-trade-averages.py using Python2.7

### Running

* To run the script please specify the number of candles over which to calculate the WMA and SMA, the candle granularity, the instrument and your accountId. This script uses the sandbox environment, so please use you sandbox accountId.

    python api-trade-averages.py 10 S5 EUR_USD <accountId>

This program is intended to demonstrate OANDA API functionality and is not intended as investment advice or a solution to buy or sell any investment product.
