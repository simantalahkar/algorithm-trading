# Disclaimer: Simanta Lahkar takes no responsibilities for outcome of running this code for anyone else! This is for reference only.

import datetime
import time
import threading
import pandas as pd
from fyers_api import accessToken
from fyers_api import fyersModel

############################Pivot points##########################
#################### Input
isEnd = False

client_id = ""
access_token = ""
fyers = fyersModel.FyersModel(token=access_token,is_async=False,client_id=client_id,log_path="./")

#time to find the strike price
entryHour   = 0
entryMinute = 0
entrySecond = 0


stock="NIFTY" #BANKNIFTY or NIFTY
otm = 500  
SL_percentage = 0.4
target_percentage = 1.2
yesterday_closing_price = 18015.20


expiry ={
    "year": "23",
    "month": "F",
    "day": "EB",
}
clients = [
    {
        "broker": "Fyers",
        "userID": "",
        "apiKey": "",
        "accessToken": "",
        "qty" : 50
    }
]

##################################################


def findStrikePriceATM(cepe, sl_fut, target_fut):
    global kc
    global clients
    global SL_percentage


    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTYBANK-INDEX"   #"NSE:NIFTY BANK"
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY50-INDEX"
    #"NSE:NIFTY 50""

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]   #23FEB

    ######################################################
    ###################Finding the atm strike
    ltp = getLTP(name)
    if stock == "BANKNIFTY":
        closest_Strike = int(round((ltp / 100),0) * 100)
        print(closest_Strike)

    elif stock == "NIFTY":
        closest_Strike = int(round((ltp / 50),0) * 50)
        print(closest_Strike)

    print("closest",closest_Strike)

    closest_Strike_CE = closest_Strike+otm
    closest_Strike_PE = closest_Strike-otm

    if stock == "BANKNIFTY":
        atmCE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"
    elif stock == "NIFTY":
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if cepe == "CE":
        takeEntry(closest_Strike_CE, atmCE, sl_fut, target_fut, name, cepe)
    else:
        takeEntry(closest_Strike_PE, atmPE, sl_fut, target_fut, name, cepe)


def takeEntry(closest_Strike, atmCEPE, sl_fut, target_fut, name, cepe):
    global SL_point
    cepe_entry_price = getLTP(atmCEPE)
    print(" closest ATM ", closest_Strike, " CE Entry Price = ", cepe_entry_price)

    for client in clients:
        print("\nPlacing_Trades!")
        print("userID = ", client['userID'])
        broker = client['broker']
        uid = client['userID']
        key = client['apiKey']
        token = client['accessToken']
        qty = client['qty']

        #oidentryCE = 0
        #oidentryPE = 0

        oidentry = placeOrderFyers( atmCEPE, "SELL", qty, "MARKET", cepe_entry_price, "regular")

        print("The OID of Entry is: ", oidentry)
        exitPosition(atmCEPE, sl_fut, target_fut, qty, name, cepe)


def exitPosition(atmCEPE, sl_fut, target_fut, qty, name, cepe):
    traded = "No"

    while traded == "No":
        dt = datetime.datetime.now()
        try:
            ltp = getLTP(name)

            if (cepe == "CE"):
                if ((ltp < target_fut) or (ltp > sl_fut) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitCE = placeOrderFyers( atmCEPE, "BUY", qty, "MARKET", 0, "regular")
                    print("The OID of Exit is: ", oidexitCE)
                    traded = "Close"
                else:
                    time.sleep(1)
            else:
                if ((ltp > target_fut) or (ltp < sl_fut) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitCE = placeOrderFyers( atmCEPE, "BUY", qty, "MARKET", 0, "regular")
                    print("The OID of Exit is: ", oidexitCE)
                    traded = "Close"
                else:
                    time.sleep(1)
            time.sleep(30)

        except:
            print("Couldn't find LTP , RETRYING !!")
            time.sleep(1)

def getLTP(name):
    try:
        #data = {"symbols":"NSE:RELIANCE-EQ"}
        data = {"symbols":name}

        ltp = (fyers.quotes(data))['d'][0]['v']['lp']
        print(ltp)
        return ltp

    except Exception as e:
        print(name , "Failed : {} ".format(e))

def checkTime_tofindStrike():
    x = 1
    while x == 1:
        dt = datetime.datetime.now()
        if( dt.hour >= entryHour and dt.minute >= entryMinute and dt.second >= entrySecond ):
            print("time reached")
            x = 2
            while not isEnd:
                takeEntryFut()
                time.sleep(1)
            #findStrikePriceATM()
        else:
            time.sleep(.1)
            print(dt , " Waiting for time to check new ATM ")


def takeEntryFut():
    global isEnd
    global kc
    global clients
    global SL_percentage
    global target_percentage

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTYBANK-INDEX"
        yesterdayHigh = 37638
        yesterdayLow = 37291
        yesterdayClose = 37335
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY50-INDEX"
        yesterdayHigh = 18134
        yesterdayLow = 18000
        yesterdayClose = 18035.85

    time=datetime.datetime.now()
    minute = time.strftime("%M")
    second = time.strftime("%S")

    pp = (yesterdayHigh + yesterdayLow + yesterdayClose)/3
    r1 = (pp * 2) - yesterdayLow
    s1 = (pp * 2) - yesterdayHigh
    print(r1)
    print(s1)

    if int(minute)%5 ==0 and int(second) ==0 :
        print("This is every fifth minute", minute)
        ltp = getLTP(name)

        if ltp > r1:
            sl_fut = round(ltp*(1-SL_percentage/100),1)
            target_fut = round(ltp*(1+target_percentage/100),1)
            print("here")
            findStrikePriceATM("PE", sl_fut, target_fut)
            print("here2")
            isEnd = True
        elif ltp < s1:
            sl_fut = round(ltp*(1+SL_percentage/100),1)
            target_fut = round(ltp*(1-target_percentage/100),1)
            print("here")
            findStrikePriceATM("CE", sl_fut, target_fut)
            print("here2")
            isEnd = True


def placeOrderFyers(inst ,t_type,qty,order_type,price,variety):
    exch = inst[:3]
    symb = inst[4:]
    dt = datetime.datetime.now()
    papertrading = 0 #0=papertrading on, 1 = place actual trades
    print(dt.hour,":",dt.minute,":",dt.second ," => ",t_type," ",symb," ",qty," ",order_type," @ price =  ",price)
    if(order_type=="MARKET"):
        type1 = 2
    elif(order_type=="LIMIT"):
        type1 = 1

    if(t_type=="BUY"):
        side1=1
    elif(t_type=="SELL"):
        side1=-1

    data =  {
        "symbol":inst,
        "qty":qty,
        "type":type1,
        "side":side1,
        "productType":"INTRADAY",
        "limitPrice":0,
        "stopPrice":0,
        "validity":"DAY",
        "disclosedQty":0,
        "offlineOrder":"False",
        "stopLoss":0,
        "takeProfit":0
    }
    try:
        if (papertrading == 1):
            orderid = fyers.place_order(data)
            print(dt.hour,":",dt.minute,":",dt.second ," => ", symb , orderid)
            return orderid
        else:
            return 0


    except Exception as e:
        print(dt.hour,":",dt.minute,":",dt.second ," => ", symb , "Failed : {} ".format(e))

checkTime_tofindStrike()
