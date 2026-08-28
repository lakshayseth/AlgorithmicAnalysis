import numpy as np
import pandas as pd
import mplfinance as mpf
from ..core.base import Signal

class SSL(Signal):

    def __init__(self, length=10, **kwargs):
        super().__init__(length=length, **kwargs)
        self.length = length

    def calculate(self, df):
        high = df["high"].rolling(self.length).mean()
        low = df["low"].rolling(self.length).mean()
        hlv = pd.Series(np.where(df["close"] > high, 1, np.where(df["close"] < low, -1, np.nan)), index=df.index).ffill()
        df["ssl_up"] = np.where(hlv < 0, low, high)
        df["ssl_down"] = np.where(hlv < 0, high, low)
        return df

    @property
    def plot_panel(self):
        return "price"
    
    def plot(self, df, panel):
        return [mpf.make_addplot(df["ssl_up"], panel=panel, color="green", width=1),
            mpf.make_addplot(df["ssl_down"], panel=panel, color="red", width=1)]
    
    def test(self, df):
        diff = df["ssl_up"] - df["ssl_down"]
    
        bull_signal = (diff.shift(1) <= 0) & (diff > 0)
        bear_signal = (diff.shift(1) >= 0) & (diff < 0)
    
        return self.backtest(df, bull_signal, bear_signal)
    
    def analyze(self, df):
        if len(df) < 2:
            return None
    
        c, p = df.iloc[-1], df.iloc[-2]
    
        if any(pd.isna(x) for x in [
            c["ssl_up"], c["ssl_down"],
            p["ssl_up"], p["ssl_down"]
        ]):
            return None
    
        if c["ssl_up"] >= c["ssl_down"] and p["ssl_up"] < p["ssl_down"]:
            return "BUY"
    
        if c["ssl_up"] < c["ssl_down"] and p["ssl_up"] >= p["ssl_down"]:
            return "SELL"
    
        return None