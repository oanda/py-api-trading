import httplib
import urllib
import json
import datetime

## This file contains some very simple calls against the OANDA API

## This demonstrates getting the current price of an instrument and trading if it is above a threshold
def checkAndTrade():
    conn = httplib.HTTPSConnection("api-sandbox.oanda.com")
    conn.request("GET", "/v1/prices?instruments=USD_CAD")
    response = conn.getresponse()
    resptext = response.read()
    if response.status == 200:
        data = json.loads(resptext)
        if data['prices'][0]['ask'] > 0.994:
            headers = {"Content-Type" : "application/x-www-form-urlencoded"}
            params = urllib.urlencode({"instrument" : "USD_CAD",
                                       "units" : 50,
                                       "type" : 'market',
                                       "side" : "buy"})
            conn.request("POST", "/v1/accounts/8026346/orders", params, headers)
            print conn.getresponse().read()
    else:
        print resptext

## This sets up an order for the same price as above, which will execute a trade when the price crosses 0.994
def order():
    now = datetime.datetime.now()
    expire = now + datetime.timedelta(days=1)
    expire = expire.isoformat('T') + "Z"    
    conn = httplib.HTTPSConnection("api-sandbox.oanda.com")
    params = urllib.urlencode({"instrument": "USD_CAD",
                               "units" : 50,
                               "price" : 0.994,
                               "expiry" : expire,
                               "side" : "buy",
                               "type" : "limit"})
    headers = {"Content-Type" : "application/x-www-form-urlencoded"}
    conn.request("POST", "/v1/accounts/8026346/orders", params, headers)
    print conn.getresponse().read()

order()
checkAndTrade()
