import httplib
import urllib
import json
import sys
import time
import datetime
## Input Required: period granularity instrument account

## This script will constantly check for new candle information and constantly calculate SMA and WMA.
## It will then execute a trade when they cross in the appropriate direction
## For example, if the WMA grows larger than the SMA, that means price is moving up so trade long

## Parses a granularity like S10 or M15 into the corresponding number of seconds
## Does not take into account anything weird, leap years, DST, etc.
is_dst = time.daylight and time.localtime().tm_isdst > 0
utc_offset = (time.altzone if is_dst else time.timezone)
def getGranularitySeconds(granularity):
    if granularity[0] == 'S':
        return int(granularity[1:])
    elif granularity[0] == 'M' and len(granularity) > 1:
        return 60*int(granularity[1:])
    elif granularity[0] == 'H':
        return 60*60*int(granularity[1:])
    elif granularity[0] == 'D':
        return 60*60*24
    elif granularity[0] == 'W':
        return 60*60*24*7
    #Does not take into account actual month length
    elif granularity[0] == 'M':
        return 60*60*24*30


## Calculates the SMA over 'period' candles of size 'granularity' for pair 'pair'
def SMA(period, granularity, pair):
    conn = httplib.HTTPSConnection("api-sandbox.oanda.com")
    url = ''.join(["/v1/candles?count=", str(period + 1), "&instrument=", pair, "&granularity=", str(granularity), "&candleFormat=midpoint"])
    print url
    conn.request("GET", url)
    response = conn.getresponse().read()
    candles = json.loads(response)['candles']
    candlewidth = getGranularitySeconds(granularity)
    now = time.time() + utc_offset
    finalsma = 0
    count = 0
    oldest = now - (period * candlewidth)
    oldprice = 0
    for candle in candles:
        candleTime = time.mktime(time.strptime(str(candle['time']),  '%Y-%m-%dT%H:%M:%S.%fZ'))
        if candleTime < oldest:
            oldprice = candle['closeMid']
            continue
        else:
            while oldest < candleTime:
                finalsma += oldprice
                count += 1
                oldest += candlewidth
            oldprice = candle['closeMid']
        
    while oldest < now:
        finalsma += candles[-1]['closeMid']
        count += 1
        oldest += candlewidth
    print "SMA:", float(finalsma)/float(period)
    return float(finalsma)/float(period)


## Calculates the WMA over 'period' candles of size 'granularity' for pair 'pair'
def WMA(period, granularity, pair):
    conn = httplib.HTTPSConnection("api-sandbox.oanda.com")
    url = ''.join(["/v1/candles?count=", str(period + 1), "&instrument=", pair, "&granularity=", str(granularity), "&candleFormat=midpoint"])
    conn.request("GET", url)
    resp = json.loads(conn.getresponse().read())
    candles = resp['candles']
    candlewidth = getGranularitySeconds(granularity)
    now = time.time() + utc_offset
    finalsma = 0
    count = 0
    oldest = now - (period * candlewidth)
    oldprice = 0
    for candle in candles:
        candleTime = time.mktime(time.strptime(str(candle['time']),  '%Y-%m-%dT%H:%M:%S.%fZ'))
        if candleTime < oldest:
            oldprice = candle['closeMid']
            continue
        else:
            while oldest < candleTime:
                count += 1
                finalsma += oldprice * count
                oldest += candlewidth
            oldprice = candle['closeMid']
    while oldest < now:
        count += 1
        finalsma += candles[-1]['closeMid'] * count
        oldest += candlewidth
    totalweight = 0
    for i in range(1, period + 1):
        totalweight += i
    print "WMA:", float(finalsma)/float(totalweight)
    return float(finalsma)/float(totalweight)

## This will loop indefinitely, making trades when the averages cross
def compareAndTrade(period, granularity, pair, account):
    conn = httplib.HTTPConnection("api-sandbox.oanda.com")
    if SMA(period, granularity, pair) < WMA(period, granularity, pair):
        state = 'rising'
    else:
        state = 'falling'
    while True:
        if state == 'rising':
            if SMA(period, granularity, pair) > WMA(period, granularity, pair):
                state = 'falling'
                conn = httplib.HTTPConnection("api-sandbox.oanda.com")
                params = urllib.urlencode({"instrument": pair,
                                           "units" : 200,
                                           "side" : "sell",
                                           "type" : "market"})
                url = ''.join(["/v1/accounts/", account, "/orders"])
                headers = {"Content-Type" : "application/x-www-form-urlencoded"}
                print url
                try:
                    conn.request("POST", url, params, headers)
                    print conn.getresponse().read()
                except: pass
        elif state == 'falling':
            if SMA(period, granularity, pair) < WMA(period, granularity, pair):
                state = 'rising'
                conn = httplib.HTTPConnection("api-sandbox.oanda.com")
                params = urllib.urlencode({"instrument": pair,
                                           "units" : 200,
                                           "side" : "buy",
                                           "type" : "market"})
                url = ''.join(["/v1/accounts/", account, "/orders"])
                headers = {"Content-Type" : "application/x-www-form-urlencoded"}
                print url
                try:
                    conn.request("POST", url, params, headers)
                    print conn.getresponse().read()
                except: pass
        time.sleep(getGranularitySeconds(granularity))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "Give me a period, candle size, pair, and account number!"
        sys.exit()
    else:
        period, granularity, pair, account = sys.argv[1:]
        compareAndTrade(int(period), granularity, pair, account)
