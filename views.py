#importation related to asnyc
import aiohttp
import asyncio
import requests
import random


# importation related to django
from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# all importation related to binance.
import os
from binance.client import Client
#from binance.futures import Futures
from datetime import datetime
import pandas as pd
import  ta
import numpy as np

import pyrebase

config={
    "apiKey": "AIzaSyADYmR43ucJ46uNfva2ToXhAEYtqSc_ISU",
    "authDomain": "firebbot-920cf.firebaseapp.com",
    "databaseURL": "https://firebbot-920cf-default-rtdb.firebaseio.com",
    "projectId": "firebbot-920cf",
    "storageBucket": "firebbot-920cf.appspot.com",
    "messagingSenderId": "631584203941",
    "appId": "1:631584203941:web:e92c16adde157b3158d94c"
 }
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
''' 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore_async

# # Use a service account.
cred = credentials.Certificate("./adar/serviceAccountKey.json")

firebase_admin.initialize_app(cred)

db = firestore_async.client() '''




# api_key = "GKvHtCPxSf4MeeGJwPwkCaXw8MxiBCxtGSsLaDoQm8cMv0YcF2bmhYX3bFrpKPjt"
# secret_key = "W8Gtyq0qRma2VSb1KqiUY0MHWb9e55zXiPYYWyWfQ5k37XESbGjs5JC6YWkaMJce"
# token_symbol = "BTCUSDT"   
# amount_token = 123

async def bot_futures_trades_sub(request, Open_position=False):
    api_key = database.child("users").child("f_api_sec_key").child('Api key').get().val()
    secret_key =  database.child("users").child("f_api_sec_key").child('Secret key').get().val()
    token_symbol =  database.child("users").child("f_amount_token").child('Token symbol').get().val()  
    amount_token=  database.child("users").child("f_amount_token").child('Amount token').get().val()
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api") as res:
                               
                data =  res
                aip =api_key
                sec= secret_key
                client =  Client(aip, sec)
                symbol = token_symbol
                qty = amount_token
            
            while True:
                
                def getminutedata(symbol, interval, lookback):
                    
                    #frame = client.get_account()['balances']
                    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback+' min ago 30 min ago UTC'))
                    frame = frame.iloc[:, :6]
                    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close','Volume']
                    frame = frame.set_index('Time')
                    frame.index = pd.to_datetime(frame.index, unit='ms')
                    frame = frame.astype(float)
                    return frame
                              
               
                df = getminutedata (symbol, '15m', '100')
                cumulret = (df.Open.pct_change()+1).cumprod()-1
                print(f'current Close is '+str(df.Close.iloc[-1]))
                winning_rate_70 = 0.7
                winnning_rate_50 = 0.5
                winning_rate_25 = 0.25
                
                if not Open_position:
                    #buy condition
                    if cumulret[-1] < -0.0015:
                        order= client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        if cumulret > 0 and random.random() < winning_rate_70:
                            order = client.futures_cancel_order(symbol=symbol,orderId=order_id ,timestamp=true)
                        elif cumulret > 0 and random.random() < winning_rate_50 :
                            order = client.futures_cancel_order(symbol=symbol, orderId=order_id, timestamp=true)
                        elif cumulret > 0 and random.random() < winning_rate_25:
                            order = client.futures_cancel_order(symbol=symbol, orderId=order_id, timestamp=true)
                        else:
                           order = client.futures_create_order(symbol=symbol, side= 'SELL', type='MARKET', quantity=qty) 
                                
                                
                        print('------')
                        print(order)
                        Open_position=True
                        print('Buy trades are on!')
                        print('------')
                    else:
                        print('------')
                        print('No Buy trades yet')
                
                if Open_position:
                    #sell condition
                    while True:
                        df = getminutedata(symbol, '15m', '30m')
                        sincebuy = df.loc[df.index > pd.to_datetime(order['updateTime'],unit='ms')]
                        if len(sincebuy) > 0:
                            sincebuyret= (sincebuy.Open.pct_change()+1).cumprod()-1
                            if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < -0.0015:
                                order = client.futures_create_order(symbol=symbol, side= 'SELL', type='MARKET', quantity=qty) 
                                if sincebuyret > 0 and random.random() < winning_rate_70:
                                     order = client.futures_cancel_order(symbol=symbol,orderId=order_id ,timestamp=true)
                                elif sincebuyret > 0 and random.random() < winning_rate_50: 
                                    order = client.futures_cancel_order(symbol=symbol, orderId=order_id, timestamp=true)
                                elif sincebuyret > 0 and random.random() < winning_rate_25:
                                    order = client.futures_cancel_order(symbol=symbol, orderId=order_id, timestamp=true)
                                else:
                                    order = client.futures_create_order(symbol=symbol, side= 'BUY', type='MARKET', quantity=qty) 
                                print('-------')
                                print('Sell trades has been placed!')
                                print('-------')
                                break 
        time.sleep(2)                          
                    
            
            
            
            
    
    
    
        return await render(request, symbol, qty,"OK!")

    except requests.exceptions.Timeout:
        print ("Timeout occurred")
        

''' 
async def bot_futures_trades_cancel_sub(request, symbol, qty, Open_position=False):
    api_key = "GKvHtCPxSf4MeeGJwPwkCaXw8MxiBCxtGSsLaDoQm8cMv0YcF2bmhYX3bFrpKPjt"#database.child('Data').child('api key').get().val()
    secret_key = "W8Gtyq0qRma2VSb1KqiUY0MHWb9e55zXiPYYWyWfQ5k37XESbGjs5JC6YWkaMJce"#database.child('Data').child('sec key').get().val()
    symbol = "BTCUSDT" #database.child('Data').child('symbol token').get().val()  
    qty= 123  #database.child('Data').child('qty').get().val()
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api") as res:
                               
                data =  res
                aip =api_key
                sec= secret_key
                client =  Client(aip, sec)
                #symbol = token_symbol
                #qty = amount_token
            
            while True:
                
                def getminutedata(symbol, interval, lookback):
                    #frame = client.get_account()['balances']
                    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback+' min ago 30 min ago UTC'))
                    frame = frame.iloc[:, :6]
                    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close','Volume']
                    frame = frame.set_index('Time')
                    frame.index = pd.to_datetime(frame.index, unit='ms')
                    frame = frame.astype(float)
                    return frame
                              
               
                df = getminutedata (symbol, '15m', '100')
                cumulret = (df.Open.pct_change()+1).cumprod()-1
                print(f'current Close is '+str(df.Close.iloc[-1]))
                
                if not Open_position:
                    #buy condition
                    if cumulret[-1] < -0.0015:
                        order= client.futures_cancel_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        print('------')
                        print(order)
                        Open_position=True
                        print('Buy trades are on!')
                        print('------')
                    else:
                        print('------')
                        print('No Buy trades yet')
                
                if Open_position:
                    #sell condition
                    while True:
                        df = getminutedata(symbol, '15m', '30m')
                        sincebuy = df.loc[df.index > pd.to_datetime(order['updateTime'],unit='ms')]
                        if len(sincebuy) > 0:
                            sincebuyret= (sincebuy.Open.pct_change()+1).cumprod()-1
                            if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < -0.0015:
                                order = client.futures_cancel_order(symbol=symbol, side= 'SELL', type='MARKET', quantity=qty) 
                                print('-------')
                                print('Sell trades has been placed!')
                                print('-------')
                                break 
        time.sleep(2)                          
                    
            
            
            
            
    
    
    
        return await render(request, symbol, qty,"OK!")

    except requests.exceptions.Timeout:
        print ("Timeout occurred")
        
      '''   

''' 
async def bot_spots_trades_sub(request, symbol, qty, Open_position=False):
    api_key = database.child("users").child("s_api_sec_key").child('Api key').get().val()
    secret_key =database.child('users').child("s_api_sec_key").child('Secret key').get().val()
    symbol = database.child("users").child('s_amount_token').child('Token symbol').get().val()   
    qty= database.child("users").child("s_amount_token").child('Amount token').get().val()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api") as res:
                
                data =  res
                s_aip =api_key
                s_sec= secret_key
                client =  Client(s_aip, s_sec)
                #symbol = token_symbol
                #qty = amount_token
            
            while True:
                
                async def getminutedata(symbol, interval, lookback):
                    #frame = client.get_account()['balances']
                    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback+' min ago 30 min ago UTC'))
                    frame = frame.iloc[:, :6]
                    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close','Volume']
                    frame = frame.set_index('Time')
                    frame.index = pd.to_datetime(frame.index, unit='ms')
                    frame = frame.astype(float)
                    return frame
                              
               
                df = getminutedata (symbol, '15m', '100')
                cumulret = (df.Open.pct_change()+1).cumprod()-1
                print(f'current Close is '+str(df.Close.iloc[-1]))
                
                if not Open_position:
                    #buy condition
                    if cumulret[-1] < -0.0015:
                        
                        order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        print('------')
                        print(order)
                        Open_position=True
                        print('Buy trades are on!')
                        print('------')
                    else:
                        print('------')
                        print('No Buy trades yet')
                
                if Open_position:
                    #sell condition
                    while True:
                        df = getminutedata(symbol, '15m', '30m')
                        sincebuy = df.loc[df.index > pd.to_datetime(order['updateTime'],unit='ms')]
                        if len(sincebuy) > 0:
                            sincebuyret= (sincebuy.Open.pct_change()+1).cumprod()-1
                            if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < -0.0015:
                                order = client.create_order(symbol=symbol, side= 'SELL', type='MARKET', quantity=qty) 
                                print('-------')
                                print('Sell trades has been placed!')
                                print('-------')
                                break 
        time.sleep(2)                          
                    
            
            
            
            
    
    
    
        return await render(request, symbol, qty,"OK!")

    except requests.exceptions.Timeout:
        print ("Timeout occurred")
        
    





async def bot_spots_trades_cancel_sub(request, symbol, qty, Open_position=False):
    api_key = "GKvHtCPxSf4MeeGJwPwkCaXw8MxiBCxtGSsLaDoQm8cMv0YcF2bmhYX3bFrpKPjt" #database.child('Data').child('api key').get().val()
    secret_key = "W8Gtyq0qRma2VSb1KqiUY0MHWb9e55zXiPYYWyWfQ5k37XESbGjs5JC6YWkaMJce"#database.child('Data').child('sec key').get().val()
    symbol = "BTCUSDT" #database.child('Data').child('symbol token').get().val()   
    qty= 123 #database.child('Data').child('token qty').get().val()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api") as res:
                
                data =  res
                s_aip =api_key
                s_sec= secret_key
                client =  Client(s_aip, s_sec)
                #symbol = token_symbol
                #qty = amount_token
            
            while True:
                
                async def getminutedata(symbol, interval, lookback):
                    #frame = client.get_account()['balances']
                    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback+' min ago 30 min ago UTC'))
                    frame = frame.iloc[:, :6]
                    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close','Volume']
                    frame = frame.set_index('Time')
                    frame.index = pd.to_datetime(frame.index, unit='ms')
                    frame = frame.astype(float)
                    return frame
                              
               
                df = getminutedata (symbol, '15m', '100')
                cumulret = (df.Open.pct_change()+1).cumprod()-1
                print(f'current Close is '+str(df.Close.iloc[-1]))
                
                if not Open_position:
                    #buy condition
                    if cumulret[-1] < -0.0015:
                        
                        order = client.cancel_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        print('------')
                        print(order)
                        Open_position=True
                        print('Buy trades are on!')
                        print('------')
                    else:
                        print('------')
                        print('No Buy trades yet')
                
                if Open_position:
                    #sell condition
                    while True:
                        df = getminutedata(symbol, '15m', '30m')
                        sincebuy = df.loc[df.index > pd.to_datetime(order['updateTime'],unit='ms')]
                        if len(sincebuy) > 0:
                            sincebuyret= (sincebuy.Open.pct_change()+1).cumprod()-1
                            if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < -0.0015:
                                order = client.cancel_order(symbol=symbol, side= 'SELL', type='MARKET', quantity=qty) 
                                print('-------')
                                print('Sell trades has been placed!')
                                print('-------')
                                break 
        time.sleep(2)                          
                    
            
            
            
            
    
    
    
        return await render(request, symbol, qty,"OK!")

    except requests.exceptions.Timeout:
        print ("Timeout occurred")
        
    
 '''











