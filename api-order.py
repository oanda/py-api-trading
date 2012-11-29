import httplib
import urllib
import json
import time

## This file contains some very simple calls against the OANDA API

## This demonstrates getting the current price of an instrument and trading if it is above a threshold
def checkAndTrade():
    conn = httplib.HTTPSConnection("api-sandbox.oanda.com")
    conn.request("GET", "/v1/instruments/USD_CAD/price")
    response = conn.getresponse()
    if response.status == 200:
        data = json.loads(response.read())
        if data['ask'] > 0.994:
            conn.request("POST", "/v1/accounts/3/trades?instrument=USD/CAD&units=50&direction=long")
            print conn.getresponse().read()


## This sets up an order for the same price as above, which will execute a trade when the price crosses 0.994
def order():
    now = int(time.time())    
    conn = httplib.HTTPSConnection("api-sandbox.oanda.com")
    params = urllib.urlencode({"instrument": "USD/CAD",
                               "units" : 50,
                               "price" : 0.994,
                               "expiry" : now + 604800,
                               "direction" : "long"})
    conn.request("POST", "/v1/accounts/3/orders", params)
    print json.loads(conn.getresponse().read())
