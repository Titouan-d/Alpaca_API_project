# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 13:11:37 2020

@author: titou
"""

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json


config = open("./data/config.json","r")
config_data= json.load(config)
password = config_data["password"]
mail = config_data["mail"]


port = 465  # For SSL
#password = input("Type your password and press enter: ")
# password = str(input("Type your password: "))
# mail =  str(input("Type your mail: "))

#"akmsuptrading@gmail.com"
# Create a secure SSL context
context = ssl.create_default_context()





def sendmail (msg,subject_ = ""):
    sender_email = mail
    receiver_email = mail
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject_
    message["From"] = sender_email
    message["To"] = receiver_email
    part1 = MIMEText(msg, "plain")
    message.attach(part1)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(mail, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Notification envoyée")

    