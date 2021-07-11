# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 12:09:15 2020

@author: titou
"""
#SOME INFOS
#200 requests per every minute per API key
#Convert numbers to string




#Import
import requests
import json
from datetime import datetime,timedelta
import pandas as pd
import sys
path = 'C:/Users/titou/Documents/Scolaire/Alpaca/'
sys.path.append(path)

from config import *
import api_alpaca as api
    
def convert_unix(time):
    time = int(time)
    return datetime.utcfromtimestamp(time)#.datetime('%Y-%m-%d %H:%M:%S')

def convert_NY_times(time):
    time = convert_unix(time)
    time = time - timedelta(hours=6) #5H en été et 4H en hiver
    return time

#response = get_bars("1Min","MSFT,AAPL",10)
#print(convert_unix(response.get("AAPL")[-1]['t'])-timedelta(hours=4))


#Now the point is to create a dataframe to use it with our own algorithm

# dict1 = response.get("AAPL")
# print(dict1)
# data_df = pd.DataFrame.from_dict(dict1)
# data_df['t'] = data_df['t'].apply(convert_NY_times)
# print(data_df)

def convert_to_df(response):
    final_dict = {}
    
    for i in response.keys():
        dictionnaire = response.get(i)
        data_df = pd.DataFrame.from_dict(dictionnaire) 
        data_df['t'] = data_df['t'].apply(convert_NY_times)
        final_dict[i] = data_df
        
    return final_dict
def format_to_akm(dataf):
    dataf.columns = ['DATE','OPEN','HIGH',
                     'LOW','CLOSE','VOL']
    
    for ei in dataf.index:
        dataf.loc[ei,'HOUR'] = dataf.loc[ei,'DATE'].time()
        dataf.loc[ei,'DATE'] = dataf.loc[ei,'DATE'].date()
        dataf.loc[ei,'DATE'] = int(str( dataf.loc[ei,'DATE']).replace('-', ''))
    #print(dataf)
    
def get_data(STOCK,DUREE,TIME="1Min"):
    
    
    response = api.get_bars(TIME,STOCK,DUREE)
    final_dict = convert_to_df(response)
    for keys in final_dict.keys():
        format_to_akm(final_dict.get(keys))
        
    
    
    return final_dict

# response = get_bars("1Min","MSFT,AAPL",10)
# final_dict = convert_to_df(response)
# print(final_dict)

def Str_to_DateTime2(date='1972-04-29',heure='00:00:00'):
    """
    convertie une date et heure string en datetime

    Parameters
    ----------
    date : TYPE, optional string format yyyy-mm-dd
        DESCRIPTION. The default is '1972-04-29'.
    heure : TYPE, optional string format hh:mm
        DESCRIPTION. The default is '00:00'.

    Returns
    -------
    ans : TYPE datetime
        DESCRIPTION.

    """
    #converti la date
    Dateconv=datetime.strptime(date,"%Y%m%d")
    #converti l'heure
    Heureconv=datetime.strptime(heure,"%H:%M:%S")
    #fusionne l'ensemble
    ans=datetime.combine(Dateconv.date(),Heureconv.time())
    return ans


def today():
    today = datetime.today()
    return today

def Check_condition(date_fin):
    #On check si on est le weekend
    Dateconv = datetime.strptime(str(date_fin),"%Y%m%d")
    if (Dateconv.weekday() >= 6):
                date_debut = date_fin - 3  #On s'interresse aux dernieres 24h de cours, donc le vendredi on le compte
    else : date_debut = date_fin - 1 #On s'interresse aux dernieres 24h
    
    #Ajout des jours ferie americains
    
    return date_debut        
    