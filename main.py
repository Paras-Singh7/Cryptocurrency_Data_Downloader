"""
Downloads data of Crypto Currencies available on Bitmex and Binance
"""

# IMPORTS
import math
import os.path
import time
from datetime import timedelta, datetime
from itertools import permutations
from bitmex import bitmex
from binance.client import Client
from dateutil import parser
from tqdm import tqdm_notebook
import pandas as pd

def mkdir(folder_name):
    """Creates folder where data is going to be stored"""
    if not os.path.isdir(folder_name) and folder_name != '':
        os.mkdir(folder_name)

def minutes_of_new_data(symbol, kline_size, data, source):
    """Calculate how many minutes of data need to be downloaded."""
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance":
        old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    elif source == "bitmex":
        old = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1,\
         reverse=False).result()[0][0]['timestamp']
    if source == "binance":
        new = pd.to_datetime(binance_client.get_klines(symbol=symbol,interval=kline_size)[-1][0]\
        , unit='ms')
    if source == "bitmex":
        new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1,\
         reverse=True).result()[0][0]['timestamp']
    return old, new

def get_all_binance(symbol, kline_size, save = False):
    """Download data from Binance"""
    filename = f'{symbol}-{kline_size}-data.pkl'
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol,kline_size, data_df, source = "binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
        print(f'Downloading all available {kline_size} data for {symbol}. Be patient..!')
    else:
        print(f'Downloading {delta_min} minutes of new data available for {symbol}, i.e.' +
        f'{available_data} instances of {kline_size} data.')
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime\
    ("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close',
     'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else:
        data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save:
        data_df.to_pickle(BIN_PATH + filename)
    print('All caught up..!')
    return data_df

def get_all_bitmex(symbol, kline_size, save = False):
    """Download data from Bitmex"""
    filename = f'{symbol}-{kline_size}-data.pkl'
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source = "bitmex")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    rounds = math.ceil(available_data / BATCH_SIZE)
    if rounds > 0:
        print(f'Downloading {delta_min} minutes of new data available for {symbol}, i.e.' +
        f'{available_data} instances of {kline_size} data.')
        for round_num in tqdm_notebook(range(rounds)):
            time.sleep(1)
            new_time = (oldest_point + timedelta(minutes = round_num * BATCH_SIZE * binsizes\
            [kline_size]))
            data = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, \
            count=BATCH_SIZE, startTime = new_time).result()[0]
            temp_df = pd.DataFrame(data)
            data_df = pd.concat([data_df,temp_df], axis = 0)
    data_df.set_index('timestamp', inplace=True)
    if save and rounds > 0:
        data_df.to_pickle(BIT_PATH + filename)
    print('All caught up..!')
    return data_df

#output_path
BIN_PATH = 'BINANCE/'
BIT_PATH = 'BITMEX/'
mkdir(BIN_PATH)
mkdir(BIT_PATH)

### API
#Enter your own API-key here
BITMEX_API_KEY = 'TbO9dOvjcvk3bKqy5ld8vDV0'
 #Enter your own API-secret here
BITMEX_API_SECRET = 'tcyeS9pLBVfbgRTXJ5mvGW-Ks82AYfEInq3FBwNhEnQAbNhI'
#Enter your own API-key here
BINANCE_API_KEY = 'ryFql9CN1i2KdtDSU63IqgfVr4UUrtz8Dp7Z3MZWM3VgUGkbBmwGzEbL1m05KfZM'
#Enter your own API-secret here
BINANCE_API_SECRET = 'jcKFz23PUlvBj3TjgN3qMVRpMkxo4GUSokVOjlqG49Qs647pAl94ru8Wpp1Ht9Kt'

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
BATCH_SIZE = 750
bitmex_client = bitmex(test=False, api_key=BITMEX_API_KEY, api_secret=BITMEX_API_SECRET)
binance_client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

ticker = ['ETHUSDT', 'BTCUSDT', 'XRPUSDT', 'BUSDUSDT', 'USDCUSDT', 'BNBUSDT', 'ADAUSDT', 'LTCUSDT']

for i in ticker:
    df = get_all_binance(i, "1m", save = True)
