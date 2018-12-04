#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import re

import numpy as np
import pandas as pd
import pytz
import requests
import tushare as ts

timezone = 'Asia/Shanghai'
TOKEN = "ef6dc403a78fe091e8ca51b8768098e35ef0a1d0581f477e517a9f29"
ROOT_DIR = '/root/stocks/data/'


def get_proxy():
    return requests.get("http://127.0.0.1:8080/get/").content


def local_datetime(timezone=timezone):
    utcmoment_naive = datetime.datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    return utcmoment.astimezone(pytz.timezone(timezone))


def stocks_list():
    pro = ts.pro_api(TOKEN)
    df = pro.stock_basic(exchange='', list_status='L', fields='symbol')
    return df['symbol'].tolist()


def last_trade_day():
    pro = ts.pro_api(TOKEN)
    end = local_datetime(timezone)
    start = end - datetime.timedelta(days=7)
    df = pro.trade_cal(exchange='', start_date=start.strftime("%Y%m%d"),
                       end_date=end.strftime("%Y%m%d"), end=1)
    return df[df.is_open > 0].iloc[-1, 1]


def ticks(code):
    proxy = get_proxy()
    return ts.get_today_ticks(code, proxy={'http': 'http://' + proxy})


def all_ticks():
    date_str = last_trade_day()
    dir = ROOT_DIR + date_str + '/'
    if not os.path.exists(dir):
        print('mk dir' + dir)
        os.mkdir(dir)
    stocks = stocks_list()
    for s in stocks:
        file_name = dir + s + '.txt'
        if os.path.exists(file_name):
            continue
        print('geting ' + s)
        df = ts.get_today_ticks(s, use_proxy=True)
        df.to_json(file_name, orient='records')


if __name__ == '__main__':
    all_ticks()
