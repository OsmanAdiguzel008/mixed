# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 11:56:43 2022

@author: oadiguzel
"""

import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
from talipp.indicators import KeltnerChannels as KC
import talib as ta
import numpy as np
from scipy import stats


    
tickers = [ 
            "XU100.IS",
            "XU030.IS",
            "USDTRY=X"
            ]

map_ = {"daily" : "1d", "weekly":"1wk"}

def get_price(tickers,interval = "1d"):
    df = pd.DataFrame()
    for ticker in tickers:
        print(ticker)
        period = "3y"
        interval = interval
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
    return df


def organize_frame(df, head="Close"):
    df = df.reset_index().set_index(["Date","symbol"])
    
    for i in ["Open","High","Low","Close"]:
        df.loc[df[i] > 10000 , i] = df[i]/100
    
    new_df = df[head].unstack(1)
    new_df = new_df.rename(columns={"USDTRY=X": "curr", 
                                    "XU030.IS": "bist30", 
                                    "XU100.IS": "bist100"})
    new_df = new_df.sort_index().ffill()
    
    new_df["bist100_usd"] = new_df["bist100"].div(new_df["curr"])
    new_df["bist30_usd"]  = new_df["bist30"].div(new_df["curr"])
    return new_df


if __name__ == "__main__":
    plot = True 
    last = 784    # 784/159 is all
    interval = "daily"
    
    df = get_price(tickers, map_[interval])
    close = organize_frame(df)
    
    close["sma20"]  = close["bist100_usd"].rolling(20,1).mean()
    close["sma50"]  = close["bist100_usd"].rolling(50,1).mean()
    close["sma200"] = close["bist100_usd"].rolling(200,1).mean()
    
    close["rsi"] = ta.RSI(close["bist100_usd"], 14)
    high          = organize_frame(df, "High")
    low           = organize_frame(df, "Low")
    slowk, slowd  = ta.STOCH(high["bist100_usd"], 
                             low["bist100_usd"], 
                             close["bist100_usd"])
    slowk = slowk.dropna()[(np.abs(stats.zscore(slowk.dropna())) < 3)]
    slowd = slowd.dropna()[(np.abs(stats.zscore(slowd.dropna())) < 3)]
    close["slowk"], close["slowd"] = slowk, slowd
    
    atr   = ta.ATR(high["bist100_usd"],
                   low["bist100_usd"],
                   close["bist100_usd"])
    ema   = ta.EMA(close["bist100_usd"], 20)
    upper = ema + 2*atr
    lower = ema - 2*atr
    close["Middle"] = ema
    close["Upper"]  = upper
    close["Lower"]  = lower
    
    close = close.tail(last)
    
    if plot == True:
        fig = plt.figure(figsize=(24, 36))
        fig.subplots_adjust(hspace=0.2, wspace=0.2, bottom=.02, left=.06,
                            right=.97, top=.94)
        
        
        ax = fig.add_subplot(411)
        ax.set_title("Price-USD")
        ax.plot(close.index, close["bist100_usd"], "black", lw=2, label="BIST100")
        ax.plot(close.index, close["bist30_usd"], "magenta", lw=2, label="BIST30")
        ax2 = ax.twinx()
        ax2.plot(close.index, close["curr"], "green", lw=1, label="USDTRY")
        ax.legend(loc=2)
        ax2.legend(loc=1)
        
        ax = fig.add_subplot(412)
        ax.set_title("Price-SMA")
        ax.plot(close.index, close["bist100_usd"], "black", lw=2, label="Price")
        ax.plot(close.index, close["sma20"], "magenta", lw=1, label="SMA20")
        ax.plot(close.index, close["sma50"], "cyan", lw=1, label="SMA50")
        ax.plot(close.index, close["sma200"], "yellow", lw=1, label="SMA200")
        ax.legend(loc=2)
        
        
        ax = fig.add_subplot(413)
        ax.set_title("Keltner")
        ax.plot(close.index, close["bist100_usd"], "black", lw=2, label="Price")
        ax.plot(close.index, close["Middle"], "cyan", lw=1, label="Middle")
        ax.plot(close.index, close["Upper"], "blue", lw=1, label="Upper")
        ax.plot(close.index, close["Lower"], "blue", lw=1, label="Lower")
        ax.fill_between(close.index, close["Upper"], close["Lower"], facecolor='blue', alpha=0.1)
        ax.legend(loc=2)
        
        ax = fig.add_subplot(817)
        ax.set_title("RSI")
        ax.plot(close.index, close["rsi"], "cyan", lw=1, label="RSI")
        ax.axhline(y=70, color="black")
        ax.axhline(y=30, color="black")
        ax.legend(loc=2)
        
        ax = fig.add_subplot(818)
        ax.set_title("Stoch")
        ax.plot(close.index, close["slowk"], "green", lw=1, label="Slowk")
        ax.plot(close.index, close["slowd"], "red", lw=1, label="Slowd")
        ax.legend(loc=2)
        
        
        plt.show()
    
    fig.savefig(f"C:/myml/plot_{interval}_last{last}.pdf")
    
    