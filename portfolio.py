# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:08:05 2020

@author: titou
"""

#Ce fichier va gérer le portefeuille d'action sur AlpacaInc.
from datetime import datetime,timedelta
import pandas as pd
import sys
import string as st
path = 'C:/Users/titou/Documents/Scolaire/Alpaca/'
sys.path.append(path)

import api_alpaca as api

import yfinance as yf

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import Bounds
from scipy.optimize import LinearConstraint
from scipy.optimize import minimize




class portfolio():
    """
    This class represents the portofolio. It is based on the Alpaca API 
    Attributes :
        portfolioValue : The value of our portfolio
        buyingPower : The investing capacity ( Initial amount - engaged value)
        long_market_value : Engaged value on long stocks
        short_market_value : Engaged value on short stocks
        engagedValue : Both long and short value
        engagedStocks : dictionnary of engaged stocks 
        stocks_names : the list of only the names
        weights : the list of each weight (same order as stocks_nnames)
        
    """
    def __init__(self):
        account = api.get_account()
        self.portfolioValue = float(account.get('portfolio_value'))
        self.buyingPower = float(account.get('buying_power'))
        self.long_market_value = float(account.get('long_market_value'))
        self.short_market_value = float(account.get('short_market_value'))
        
        self.engagedValue = self.long_market_value + abs(self.short_market_value)
        self.engagedStocks = api.get_position()
        self.stocks_names = []
        
        
        self.weights = self.weights()
        
        

    # Check our current balance vs. our balance at the last market close  
    def __repr__(self):
        port = "Portfolio Value = %f $, Buying power = %f $, long Value = %f $, short value = %f $" % (self.portfolioValue,self.buyingPower,self.long_market_value,self.short_market_value)
        stocks = api.print_position_precise(self.engagedStocks)
        
        return port + "\n\n" + str(stocks)
    
    def gV_count(self):
        account = api.get_account
        self.portfolioValue = float(account.get('portfolio_value'))
            
    def bP_count(self):
        account = api.get_account
        self.buyingPower = float(account.get('buying_power'))
         
    def long_count(self):
        account = api.get_account
        self.long_market_value = float(account.get('long_market_value'))
  
    def short_count(self):
        account = api.get_account
        self.long_market_value = float(account.get('short_market_value'))
    def position_count(self):
        self.engagedStocks = api.get_position()
    
    def names(self):
    
        """

        Update the stocks_name list

        """
        stocks = []
        for i in self.engagedStocks:
           stock = i.get('symbol')
           stocks.append(stock)
        self.stocks_names = stocks
    
    
    def weights(self):
        """

        Update the weight list

        """
        list_stock = []
        real_weight = []
        for i in self.engagedStocks :
            list_stock.append(i.get('symbol'))
            real_weight.append(abs(float(i.get('market_value')))/self.engagedValue)
            
        dict_zip = zip(list_stock,real_weight) 
        dictionnary = dict(dict_zip)
        
        return dictionnary
    
        
        
class stocks():
    def __init__(self):        
        self.name = ''
        self.price = 0
        self.numberShort = 0
        self.numberLong = 0
        
    def _setPrice_(self,the_price):
        self.price = the_price
    def _setShort_(self,nb_short):
        self.numberShort = nb_short
    def _setLong_(self,nb_long):
        self.numberLong = nb_long
    
    
#TEST initiaux
        




def can_buy(stock,portfolio,strategie):
    """
    Parameters
    ----------
    stock : TYPE string 
        Representing the stock name
    portfolio : TYPE class portfolio
        the portfolio we are currently working on
    strategie : TYPE int
        separate strategies to know the buying or selling capacity (based on weight for example)

    Returns
    -------
    bool
        True if the algorithm is allowed to buy, False if not

    """
    if (strategie== 1): #Pourcentage de repartition des capitaux engages.
        for i in portfolio.engagedStocks :
            if(i.get('symbol') == stock ):
                percent = float(i.get('market_value'))/(portfolio.long_market_value - portfolio.short_market_value) * 100
                if (percent > 30):
                    print(percent)
                    return False
                else:
                    return True
#print(can_buy('AAPL',mon_portefeuille,1))
#print(can_buy('MSFT',mon_portefeuille,1))
           
def yf_portfolio(list_stock):
    """
    

    Parameters
    ----------
    list_stock : TYPE list of string 
        The names of the stock we want to build a portfolio with

    Returns
    -------
    portfolio : pandas Dataframe
        DESCRIPTION.
    return_portfolio : TYPE
        Dataframe containing the returns of each stocks (returns scale is the same as stocks : daily if daily etc... )
    Sum_up : pandas Dataframe
        Dataframe containing the mean and stdev of the potfolio stocks (used in a mean/variance strategy)
    cov_matrix : pandas Dataframe
        Dataframe containing the covariance matrix of our data
    """
    
    
    
    
    portfolio = pd.DataFrame()
    print(list_stock)
    for tick in list_stock :
        print(tick)
        t = yf.Ticker(tick).history(period="3y",interval = "1mo")['Close']
        print(t)
        portfolio[f"Close_{tick}"] = t
        t = yf.Ticker(tick).history(period="3y",interval = "1mo")['Open']
        portfolio[f"Open_{tick}"] = t
        #print(t)
    portfolio.dropna(inplace = True)    
    #print(portfolio)
    
    return_portfolio = pd.DataFrame()
    for i in range (1,len(portfolio.columns),2) :
        NAME = portfolio.columns[i]
        return_portfolio[f"Return_{NAME}"] = (portfolio.iloc[:,i-1] - portfolio.iloc[:,i])/portfolio.iloc[:,i-1]



    Sum_up = pd.DataFrame()
    Sum_up["Mean"] = return_portfolio.mean()
    Sum_up["STDV"] = return_portfolio.std()
    Sum_up = Sum_up.transpose()
    #print(Sum_up)
    
    
    corr_matrix = return_portfolio.corr(method = "pearson")
    cov_matrix = return_portfolio.cov()
    #print(cov_matrix)


    return portfolio,return_portfolio,Sum_up,cov_matrix                          


def Portfolio_Variance(weights,cov_matrix):
    """
    

    Parameters
    ----------
    weights : TYPE List
        List of our portfolio weights
    cov_matrix : TYPE pandas Dataframe
        Covariance of our stocks

    Returns
    -------
    sum : TYPE float
        the variance of our portfolio

    """
    n = len(weights)
    sum = 0.0
    for i in range(n) :
        for j in range(n) :
            sum += weights[i]*weights[j]*cov_matrix.iloc[i,j]
    return sum
     
def minimizing(Sum_up,cov_matrix):
    """
    

    Parameters
    ----------
    Sum_up : TYPE pandas Dataframe
        Dataframe containing the mean and stdev of the potfolio stocks (used in a mean/variance strategy).
    cov_matrix : TYPE pandas Dataframe
        Covariance of our stocks

    Returns
    -------
    stdev : TYPE  List (float)
        List of all the computed standard deviation for each weight
    real_mu : TYPE List (float)
        List of all the computed mean for each weight.
    list_weights : TYPE List (float)
        List of all the computed weight minimizing the stdev.

    """

    
    
    n = len(Sum_up.columns)
    E_matrix = [Sum_up.iloc[0,i] for i in range (n)]

    mu_bounds = 1 * max(abs(min(E_matrix)),abs(max(E_matrix)))
    mu_target = np.arange(-mu_bounds,mu_bounds,(max(E_matrix)-min(E_matrix))/20)
    
    stdev = []
    real_mu = []
    list_weights = []
    
    x0 = np.ones(n)/n
    #print(sum(x0))
    
    #assert(sum(x0)==1)
    
    bounds = Bounds(np.zeros(n),np.ones(n))
    
    for i in mu_target :
        #print(i)
        linear_constraint = LinearConstraint([E_matrix, np.ones(n).tolist()], [i,1], [i, 1])
        #linear_constraint = LinearConstraint([[ones.tolist()[i], E_matrix[i]] for i in range(len(E_matrix))], [1,i], [1, i])
        res = minimize(Portfolio_Variance, x0,args = cov_matrix ,method='SLSQP',constraints=[linear_constraint],bounds=bounds)
        
        
        #print("E(R) =",np.dot(E_matrix,check))
        stdev.append(np.sqrt(Portfolio_Variance(res.x,cov_matrix)))
        real_mu.append(np.dot(E_matrix,res.x))
        list_weights.append(res.x)
        
    return stdev,real_mu,list_weights

def plot_portfolio(Sum_up,stdev = None,real_mu = None):
    """
    Plotting function to graph the portfolio frontier

    Parameters
    ----------
    Sum_up : TYPE pandas Dataframe
        Dataframe containing the mean and stdev of the potfolio stocks (used in a mean/variance strategy).
    stdev : TYPE  List (float), optional the default is None
        List of all the computed standard deviation for each weight
    real_mu : TYPE List (float), optional the default is None
        List of all the computed mean for each weight.
    Returns
    -------
    None.

    """
    colors = ['#f5b7b1','#d7bde2','#d2b4de','#a9cce3','#aed6f1','#a3e4d7','#a2d9ce',
              '#a9dfbf','#abebc6','#f9e79f' ]
    fig, ax = plt.subplots()
    
    if (real_mu == None):
        for i in range(len(Sum_up.columns)):
            plt.scatter(Sum_up.iloc[1,i],Sum_up.iloc[0,i],label = Sum_up.columns[i].split('_')[2])
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        plt.plot(stdev,real_mu)
        for i in range(len(Sum_up.columns)):
            plt.scatter(Sum_up.iloc[1,i],Sum_up.iloc[0,i],marker = '+',label = Sum_up.columns[i].split('_')[2])
        
        plt.scatter(min(stdev),real_mu[np.argmin(stdev)],marker = 'x', color = 'r',label = "Variance minimal")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        
def strategie_Evar(portfolio):
    """
    

    Parameters
    ----------
    portfolio : TYPE class portfolio
        The portfolio we are working on

    Returns
    -------
    stdev : TYPE float
       TThe standard deviation of our portfolio
    real_mu : TYPE float
        The mean of the retrns of our portfolio
    dict_weights : TYPE dictionary
        weights of each stock to achievve the targeted stdev and mean

    """
    
    list_stock = portfolio.weights.keys()
    
    portfolio,return_portfolio,Sum_up,cov_matrix = yf_portfolio(list_stock)
    
    #plot_portfolio(Sum_up)

    stdev,real_mu,list_weights = minimizing(Sum_up,cov_matrix)
    
    plot_portfolio(Sum_up,stdev,real_mu)
    
    #We now want the optimized weight (min variance)
    
    list_weights_opt = list_weights[np.argmin(stdev)]
    
    zipping = zip(list_stock,list_weights_opt) 
    dict_weights = dict(zipping)
    
    
    return stdev,real_mu,dict_weights
    


#print(stdev,real_mu)
# print(dict_weights)

def print_pie(dictionnary):
    """
    
    Print a Pie to sum up our portfolio
    Parameters
    ----------
    dictionnary : TYPE dictionnary
        The dictionnary keys : stocks, values : weights

    Returns
    -------
    None.

    """
    
    sizes = dictionnary.values()
    labels = dictionnary.keys()
    
    #colors
    colors = ['#f5b7b1','#d7bde2','#d2b4de','#a9cce3','#aed6f1','#a3e4d7','#a2d9ce',
              '#a9dfbf','#abebc6','#f9e79f' ]
    
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, colors = colors, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
    ax1.axis('equal') 
    
# print_pie(mon_portefeuille.weights)
# print_pie(dict_weights)
# print(dict_weights)

def optimum_portfolio(portfolio,dict_weights):
    
    dict_optimum = dict()
    
    
    for i in dict_weights:
        
        stock = i
        weight = dict_weights.get(i)
        
        amount_target = weight * portfolio.engagedValue
        for j in portfolio.engagedStocks:
            if (j.get('symbol')==stock):
                stock_target = int( amount_target / float(j.get('current_price') ) )
        dict_optimum[stock] = stock_target
    
    return dict_optimum



        
mon_portefeuille = portfolio()
stdev,real_mu,dict_weights = strategie_Evar(mon_portefeuille)
print(optimum_portfolio(mon_portefeuille,dict_weights))
print_pie(mon_portefeuille.weights)
print_pie(dict_weights)
print(dict_weights)    
               
       
       
    
    
    
    


