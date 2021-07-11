# -*- coding: utf-8 -*-
"""
Created on Tue May 25 10:36:41 2021

@author: titou
"""

import Indicators
import pandas as pd
from datetime import datetime



def final_check(integer):
    if integer > 0:
        return 1
    elif integer < 0:
        return -1
    else :
        return 0


def strategie(stock_price):
    
    
    data_prep(stock_price)
    
    Final_df = pd.DataFrame(index = stock_price.index)
    
    #Indicators Calculation
    indicateur_bbands = Indicators.BBANDS_Calc(stock_price)
    bbands_signal = Indicators.BBANDS_SignalCalc(indicateur_bbands,stock_price)
    
    indicateur_macd = Indicators.MACD_Calc(stock_price)
    macd_signal = Indicators.MACD_SignalCalc(indicateur_macd)
    
   
    ma_short=Indicators.MAE_Calc(stock_price,TIMEPERIOD = 12)
    ma_long=Indicators.MAE_Calc(stock_price,TIMEPERIOD = 24)
    ma_signal = Indicators.MA_EMA_SignalCalc(ma_short,ma_long)
    ma_signal.set_index(stock_price.index)
    #print(ma_signal)
    
    Final_df.insert(0,'BBANDS', bbands_signal.values)
    Final_df.insert(1,'MACD', macd_signal.values)
    Final_df.insert(2,'MA', ma_signal.values)
    
    Final_df['ORDER_TYPE'] = Final_df['BBANDS'] + Final_df['MACD'] + Final_df['MA']
    Final_df['ORDER_TYPE'] = Final_df['ORDER_TYPE'].apply(final_check)
    
    Final_df.set_index(stock_price.index)
    
    #Final_df['ORDER_TYPE'] 
    
    
    return Final_df





def data_prep(data):

    #data.drop(columns = ['Unnamed: 0'],inplace = True)
    data['DATE'] = data['DATE'].astype(str)
    data['HOUR'] = data['HOUR'].astype(str)
    data['DATEHOUR'] = data['DATE'] + data['HOUR']
    
    data['DATEHOUR'] = pd.to_datetime(data['DATEHOUR'],format = '%Y%m%d%H:%M:%S')
    data.drop(columns = ['DATE','HOUR'],inplace = True)
    data.set_index("DATEHOUR",inplace=True)
    
    

#data['HOUR'] = pd.to_datetime(data['HOUR'],format = '%H:%M:%S')

#data['HOUR'].apply(datetime.time())

#data['DATE'] = pd.to_datetime(data[['DATE','HOUR']], format = '%Y%m%d %H:%M:%S')

# data = pd.read_csv('donnee.csv')
# data_prep(data)
# print(data)
# f = strategie(data)
