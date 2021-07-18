# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 16:10:27 2020

@author: titou
"""



#Import
import requests
import json
from datetime import datetime,timedelta
import pandas as pd
import sys
path = 'C:/Users/titou/Documents/Scolaire/Alpaca/'
sys.path.append(path)

#from config import *
import trade_test as tt
# =============================================================================
# #DEFINE_URL
# =============================================================================
                #TRADING

config = open("./data/config.json","r")
config_data= json.load(config)
API_KEY = config_data["API_KEY"]
SECRET_KEY = config_data["SECRET_KEY"]

print(API_KEY,SECRET_KEY)


BASE_URL = "https://paper-api.alpaca.markets"

ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDER_URL = "{}/v2/orders".format(BASE_URL)
HEADERS =  {'APCA-API-KEY-ID' : API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY} 
POSITION_URL = "{}/v2/positions".format(BASE_URL)



                #DATA
DATA_URL = "https://data.alpaca.markets"
BARS_URL ="{}/v1/bars".format(DATA_URL)

#API ACCESS

def get_account():
    """
    Access the API    

    Returns
    -------
    json of the request
        

    """
    r = requests.get(ACCOUNT_URL, headers = HEADERS)
    
    return json.loads(r.content)

def get_position():
    """
    
    Returns
    -------
    json 
        Get the current position of our portfolio (access directly w/o portfolio class)

    """
    
    
    r = requests.get(POSITION_URL, headers = HEADERS)
    
    return json.loads(r.content)

def print_position_precise(request):
    stocks = []
    for i in request:
       stock = str(i.get('symbol'))+" Qty = " + i.get('qty') + " Current_price = " + i.get('current_price') 
       stocks.append(stock)
    return stocks

def get_clock():
    r = requests.get("{}/v2/clock".format(BASE_URL), headers = HEADERS)
    return json.loads(r.content)

# r = get_clock()
# print(r)




# On est sur le bon compte ok

def create_order(symbol,qty,side,the_type,time_in_force):
    
    """
    Do
    ----------
    Send an order to the API
    
    Parameters
    ----------
        symbol : String of the name of the desired stocks
        qty : number of stocks in the order
        the_type : At the market, limit,
        time_in_force : time before deleting order
    
    Return 
    ----------
    
    json
        Representing the passed order
    
    """
    
    data ={
        "symbol" : symbol,
        "qty" : qty,
        "side" : side,
        "type": the_type,
        "time_in_force":time_in_force
        }
        
    r = requests.post(ORDER_URL, json = data , headers =HEADERS)
    
    return json.loads(r.content)

# response = create_order("TSLA",10,"buy","market","day") 
# print(response)


def get_bars(timeframe,symbols,limit = 100):
    data = {
        "symbols":symbols,
        "limit":limit
        
        }
    r = requests.get(BARS_URL+"/"+timeframe , params = data, headers = HEADERS)
    
    
    return json.loads(r.content)
    
def save_data():
    """
    
    Saves the asked data
        Returns
    -------
    None.

    """
    
    
    r = get_account()
    STOCK = "MOGO,KERN,TRVG,PXLW"
    DUREE = 1000
    path1 = 'C:/Users/titou/Documents/Scolaire/Alpaca/donnee'
    tout_stock = tt.get_data(STOCK,DUREE) #Dictionaire des dataframes demandé
    for key in tout_stock.keys():
            print(key)
            donnee = tout_stock.get(key)
            if (len(donnee) < 3 ):
                break
           
            donnee.to_pickle(path1 +'./donnee_'+str(key)+'.pic')
            donnee.to_csv(path1 +'./donnee_'+str(key)+'.csv')
            print('data saved')