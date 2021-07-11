# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 15:47:07 2020

@author: titou
"""

import requests
import json
from datetime import datetime,timedelta
import pandas as pd
import sys
import string as st
path1 = './'
sys.path.append(path1)
import api_alpaca as api
from config import *
import trade_test as tt
from mail import sendmail
import portfolio as po 
from Strategie import strategie
import numpy as np



#On récupère le dataFrame avant de faire tourner l'algo dessus

def main(DELTA = 30):
    
    end = True
    
    #STOCKS= "MOGO,KERN,TRVG,PXLW"
    #STOCKS= ["MOGO","KERN","TRVG","PXLW"]
    QTY = 10
    DUREE = 300
    
      
    heure_limite = datetime.today()
    
    #Heure de fin de marché NASDAQ
    heure_limite = heure_limite.replace(hour = 16, minute = 00, second = 00,microsecond =0)
    print("Heure de fin de trading de NY ",heure_limite)
    
    heure_actuelle_PARIS = datetime.today()
    
    heure_actuelle = heure_actuelle_PARIS - timedelta(hours = 6)
    print("\nheure actuelle_PARIS = ",heure_actuelle_PARIS,"\n")
    print("\nheure actuelle_NY = ",heure_actuelle,"\n")
    
    
    
    #API CONNECTION AND SETING
    r = api.get_account()
    mon_portefeuille = po.portfolio()
    mon_portefeuille.names()
    STOCKS_LIST = mon_portefeuille.stocks_names #We have to convert it in on estring for the API
    STOCKS = ''
    for i in STOCKS_LIST:
        STOCKS += f',{i}' 
    print(STOCKS)
    
    if(r.get("id") != None):
        print ("Connexion effectuée")
        
        #On cherche d'abord à récupérer les données
        tout_stock = tt.get_data(STOCKS,DUREE) #Dictionaire des dataframes demandé
        #print(tout_stock)
        
        for key in tout_stock.keys():
            STOCK = key
            #print(key)
            donnee = tout_stock.get(STOCK)
            if (len(donnee) < 3 ):
                break
           
            auj = donnee['DATE'] >= donnee['DATE'].tail(1).iloc[0]
            ourdata = donnee[auj]
            heure_fin = donnee['HOUR'].tail(1).iloc[0]
           
            
            date_fin = donnee['DATE'].tail(1).iloc[0]
            date_debut = tt.Check_condition(date_fin)
            
            
            
            #print(date_fin)
            donnee.to_pickle(path1 +f'./data/{key}_data.pic')
            donnee.to_csv(path1 +f'./data/{key}_data.csv')
            print('data saved')
            
            
            
            #print('\n Lancement de l algorithme \n')
                
            analyse = strategie(donnee)
            analyse.set_index(donnee.index)
           
            #print('\nFin de l algorithme \n')
            
            
            
            
            
            
            print(f"///////   Voici les actions a realiser  sur {STOCK} ///////\n")
            print(analyse.tail()['ORDER_TYPE'])
            last = analyse.tail()
            
            COUNT_SELL = 0
            COUNT_BUY = 0
            
            for ei in last.index:
               
                if (abs((ei-heure_actuelle))<timedelta(minutes = DELTA)):
                    print(f"//////////////////             Actions realisées    {STOCK}       //////////////////")
                    
                    subject_ = f"Achat et Vente sur {STOCK} a "+ str(heure_actuelle)
                    msg = ''
                    if (last.loc[ei,'ORDRE_TYPE'] == 'SELL'):
                        response = api.create_order(STOCK,QTY,"sell","market","day") 
                        COUNT_SELL += 1*QTY
                        COUNT_BUY -= 1*QTY
                         
                         
                        msg += str(response)
                        
                        print(response)
                    if (last.loc[ei,'ORDRE_TYPE'] == 'BUY'):
                        response = api.create_order(STOCK,QTY,"buy","market","day") 
                        COUNT_BUY += 1*QTY
                        COUNT_SELL -= 1*QTY
                        print(response)
                        
                        msg += str(response)
                        
                    sendmail(msg,subject_)
        
        print('\n Temps de trading restant \n', ((heure_limite - heure_actuelle),"Market closed")[((heure_limite - heure_actuelle) < timedelta(days = 0 , hours = 0, seconds = 0)) == True])
        
        if(abs((heure_limite - heure_actuelle)) < timedelta(minutes = 20)) :
                        
                        subject_ = "bilan du jour "+  str(date_fin)
                        bilan_du_jour = ''
                        
                        print("Closing positions : ")
                        if(COUNT_SELL ==0 ):
                            response = "No open positions"
                            bilan_du_jour  += str(response)
                        elif (COUNT_SELL < 0):
                            response = api.create_order(STOCK,QTY * abs(COUNT_SELL),"sell","market","day") 
                            print(response)
                            
                            bilan_du_jour  += str(response)
                        else :
                            response = api.create_order(STOCK,QTY * abs(COUNT_BUY),"buy","market","day") 
                            print(response)
                            
                            bilan_du_jour += f"///////////////////////////////////////{response}"
                            
                        #sendmail(bilan_du_jour,subject_)
                        end = False
            
        return end
    else:
            print("Impossible de se connecter au compte")
            return False

main()