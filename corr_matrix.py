# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 15:32:37 2022

@author: oadiguzel
"""

import pandas as pd
import yfinance as yf
import seaborn as sn
import matplotlib.pyplot as plt
from pylab import savefig


df = pd.DataFrame()

tickers = [ "AVGO",
            "KLAC",
            "MA",
            "QCOM",
            "REGN",
            "TMO",
            "TSLA",
            "URI",
            "IBHB",
            "OPER",
            "RYU",
            "XLK",
            "XSD",
            "XME",
            "XLV",
            "XLE",
            "VDE",
            "SDY",
            "IYE",
            "IXC",
            "IFRA",
            "FXN",
            "FTXN",
            "FENY",
            "FDL",
            "EMLP",
            "DXJ"
            ]

for ticker in tickers:
    print(ticker)
    period = "2y"
    interval = "1d"
    group_by="ticker"
    auto_adjust=True
    prepost=True
    threads=True
    proxy=None
    
    temp = yf.download(
                     tickers = ticker,
                     period = period,
                     interval = interval,
                     group_by = group_by,
                     auto_adjust = auto_adjust,
                     prepost = prepost,
                     threads = threads,
                     proxy = proxy
                 )
    temp["symbol"] = ticker
    if len(df) == 0:
        df = temp
    else:
        df = df.append(temp)
        
data = df.reset_index().set_index(["Date","symbol"])["Close"].unstack()
corr = data.corr()

df_cm = pd.DataFrame(corr)

svm = sn.heatmap(df_cm, annot=False,cmap='coolwarm', linecolor='white', linewidths=1)

figure = svm.get_figure()    
figure.savefig('corr.png', dpi=400)
corr.to_csv("corr.csv")
