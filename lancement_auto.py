# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 19:43:14 2020

@author: titou
"""


import datetime as dt

import subprocess
import sys


# path1 = 'C:/Users/titou/Documents/Scolaire/Alpaca/'
# sys.path.append(path1)
import algotest



DELTA = 15
DELTA_init = 50
delta = dt.timedelta(minutes = DELTA_init)
now =last = dt.datetime.today()

t=True
while (t):
    now = dt.datetime.today()
    if (delta > dt.timedelta(minutes = DELTA)):
        delta = dt.timedelta(minutes = 0)
        last = dt.datetime.today()
        print("Lancement de l'algo ... \n")
        t = algotest.main(DELTA)
        if(t) : print("\n\nProchaine réactuallisation à : ", now + dt.timedelta(minutes = DELTA)  )
        else: print("Fermeture du programme ...")
    else:
        delta = now - last
    