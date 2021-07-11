# -*- coding: utf-8 -*-
"""
Created on Tue May 25 10:31:29 2021

@author: titou
"""

import ta
import pandas as pd 
import numpy as np


def MAE_Calc(data,TIMEPERIOD = 20):
    
    indicator_class=ta.trend.EMAIndicator(data['CLOSE'], n= TIMEPERIOD)
    
    MAE=pd.DataFrame(index=data.index)
    
    MAE['ma']=indicator_class.ema_indicator()
    
    MAE.fillna(0,inplace=True)
    MAE.loc[MAE['ma']==0,'ma'] = data.loc[MAE['ma']==0,'CLOSE']
    return MAE

def MACD_Calc(data, FASTPERIOD = 1, SLOWPERIOD = 10, SIGNALPERIOD = 2) :
    """
    This function takes a dataframe of the prices and return a dataframe with 3 columns the macd, its signal and history
    Everything is done with TA librabry, this function just chose the parameters and put everything in a dataFrame
    """
    indicator_class = ta.trend.MACD(data['CLOSE'],FASTPERIOD,SLOWPERIOD,SIGNALPERIOD)
   
    
    MACD_dataFrame = pd.DataFrame(index=data.index)
    
    MACD_dataFrame['macd'] = indicator_class.macd()
    MACD_dataFrame['macdsignal'] = indicator_class.macd_signal()
    MACD_dataFrame['macdhist'] = indicator_class.macd_diff()
    #MACD_dataFrame['macd-1']=MACD_dataFrame['macdsignal'].shift(1)
    MACD_dataFrame["derive macd"]=MACD_dataFrame['macdsignal']-MACD_dataFrame['macdsignal'].shift(1)
    
    MACD_dataFrame['macd'] = MACD_dataFrame['macd'].fillna(0) #Delete the first NaN lines
    MACD_dataFrame['macdsignal'] = MACD_dataFrame['macdsignal'].fillna(0)
    MACD_dataFrame['macdhist'] = MACD_dataFrame['macdhist'].fillna(0)
    MACD_dataFrame["derive macd"].fillna(0,inplace=True)
    #print(MACD_dataFrame.tail(50))
    return MACD_dataFrame

def BBANDS_Calc(data,TIMEPERIOD = 47) :

    """
    This function takes a dataframe of the prices and return a dataframe with 3 columns the upperband,middleband, lowerband
    Everything is done with TA librabry, this function just chose the parameters and put everything in a dataFrame
    """

    indicator_class = ta.volatility.BollingerBands(data['CLOSE'], TIMEPERIOD,2)
    
    BBANDS_dataFrame = pd.DataFrame(index=data.index)
    
    BBANDS_dataFrame['up'] = indicator_class.bollinger_hband()
    BBANDS_dataFrame['mid'] = indicator_class.bollinger_mavg()
    BBANDS_dataFrame['low'] = indicator_class.bollinger_lband()
    BBANDS_dataFrame['width'] = BBANDS_dataFrame['up'] - BBANDS_dataFrame['low']
    BBANDS_dataFrame['hindic'] = indicator_class.bollinger_hband_indicator() #1 if close is above hband
    BBANDS_dataFrame['lindic'] = indicator_class.bollinger_lband_indicator() #1 if close is below lband
    
    BBANDS_dataFrame['up'] = BBANDS_dataFrame['up'].fillna(0) #Delete the first NaN lines
    BBANDS_dataFrame['mid'] = BBANDS_dataFrame['mid'].fillna(0)
    BBANDS_dataFrame['low'] = BBANDS_dataFrame['low'].fillna(0)                                         
    BBANDS_dataFrame['width'] = BBANDS_dataFrame['width'].fillna(0)
    BBANDS_dataFrame['hindic'] = BBANDS_dataFrame['hindic'].fillna(0)
    BBANDS_dataFrame['lindic'] = BBANDS_dataFrame['lindic'].fillna(0)

    return BBANDS_dataFrame




def MA_EMA_SignalCalc(MA_short,MA_long) :
    """
    This function takes two dataFrame as parameters, our prices ma short and ma long.
    It return a dataFrame/Serie with -1,0 or 1 to indicates if we need to sell(-1) or buy (1) (sob)
    the strategie is based on : buy if ma short > ma_long for TIMEPERIOD units straight and sell in ma short < ma long
    """
    """à utiliser avec MA_short = 20 et MA_long = 100 
    """
    MA_order = pd.DataFrame(data={'ORDER_TYPE':0,'TrueSignal':0},index=MA_short.index)
    
    MA_order['short - long'] = MA_short['ma'] - MA_long['ma']
    MA_order.dropna(subset = ['short - long'],inplace=True) #Drop the nan value causes by the long MA
    
    #print(MA_order)
    #print(MA_order.iloc[0,2])
    MA_order['sign']=MA_order['short - long'].apply(np.sign).values
    MA_order['sign-1']=MA_order['sign'].shift(1)
    MA_order["ProdSign"]=MA_order['sign']*MA_order['sign-1']
    
    MA_order.loc[MA_order["ProdSign"]==-1,"TrueSignal"]=1
    
    MA_order.loc[MA_order["TrueSignal"]==1,"ORDER_TYPE"]=MA_order.loc[MA_order["TrueSignal"]==1,"sign"]
    MA_order.drop(['TrueSignal','short - long','sign','sign-1','ProdSign'],inplace=True,axis='columns')
    return MA_order

  
def BBANDS_SignalCalc(bbands_data,cours,seuil_achat=1.0007346326981947):
    #parametres issus d'une optimisation sur le pnl sur 2007-2014

    """
    We consider we have to buy when the stocks goes above the Hband
    and sell when the stocks goes below the lband
    But to be sure we will to that whan the bband witdh are small, we will take the first quantile
    """
    
    BBANDS_order = pd.DataFrame(data={'ORDER_TYPE':0,'test_width':0,'test_ordre':0},index=bbands_data.index)
    

    
    bbandsLimit = bbands_data['width'].quantile(1)
    BBANDS_order.loc[bbands_data['width'] < bbandsLimit,'test_width']=1
    BBANDS_order.loc[cours["CLOSE"]>=bbands_data['up']*seuil_achat,'test_ordre']=1
    BBANDS_order.loc[cours["CLOSE"]<=bbands_data['low']*(2-seuil_achat),'test_ordre']=-1

    
    BBANDS_order.loc[10*BBANDS_order['test_width']+BBANDS_order['test_ordre']==11,'ORDER_TYPE']=1
    BBANDS_order.loc[10*BBANDS_order['test_width']+BBANDS_order['test_ordre']==9,'ORDER_TYPE']=-1
    
    BBANDS_order.drop(columns=['test_width','test_ordre'],inplace=True)
    
    return BBANDS_order



def MACD_SignalCalc(macd_data) :
    """
    This function takes two dataFrame as parameters, our prices data and the indicator data.
    It return a dataFrame/Serie with -1,0 or 1 to indicates if we need to sell(-1) or buy (1) (sob)
    the strategie is based on : buy if macd > signal for TIMEPERIOD units straight and sell in macd < signal
    """
    #parametres issus d'une optimisation sur le pnl sur 2007-2014
    
    seuil_achat=-2
    seuil_vente=2
    
    seuil_histo_vente=1 #positif
    seuil_histo_achat=-1 #negatif
    
    MACD_order = pd.DataFrame(data={'ordre':0,'ORDER_TYPE':0, 'MACD_seuil':0, 'MACD_diff':0,'signDer':0} ,index=macd_data.index)
    
    MACD_order.loc[macd_data['macd']<seuil_achat,'MACD_seuil']=1
    MACD_order.loc[macd_data['macd']>seuil_vente,'MACD_seuil']=-1
    
    MACD_order.loc[macd_data['macdhist']>seuil_histo_vente,'MACD_diff']=-1
    MACD_order.loc[macd_data['macdhist']<seuil_histo_achat,'MACD_diff']=1
    
    MACD_order["Sum"]=MACD_order["MACD_seuil"]+MACD_order["MACD_diff"]
    
    MACD_order.loc[MACD_order["Sum"]==2,'ordre']=1
    MACD_order.loc[MACD_order["Sum"]==-2,'ordre']=-1
    MACD_order.loc[macd_data["derive macd"]>0,"signDer"]=-1
    MACD_order.loc[macd_data["derive macd"]<0,"signDer"]=1
    
    MACD_order['ordreF']=10*MACD_order['ordre']+MACD_order['ordre'].shift(1)+100*MACD_order["signDer"]
    
    
    
    MACD_order.loc[MACD_order["ordreF"]==110,'ORDER_TYPE']=1
    MACD_order.loc[MACD_order["ordreF"]==-110,'ORDER_TYPE']=-1
    
    MACD_order.drop(['Sum','MACD_seuil','MACD_diff','ordre','ordreF','signDer'],inplace=True, axis='columns')
    return MACD_order
