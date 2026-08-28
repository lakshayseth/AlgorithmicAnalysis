import numpy as np
import pandas as pd
import mplfinance as mpf
from ..core.base import Signal


class ABSOLUTE_STRENGTH(Signal):

    def __init__(self, length=10, smooth=3, **kwargs):
        super().__init__(length=length, smooth=smooth, **kwargs)
        self.length = length
        self.smooth = smooth

    def calculate(self, df):
        diff = df["close"].diff()
        bulls = 0.5 * (np.abs(diff) + diff)
        bears = 0.5 * (np.abs(diff) - diff)

        w1 = np.arange(1, self.length + 1)
        bulls = bulls.rolling(self.length).apply(lambda x: np.dot(x, w1) / w1.sum(), raw=True)
        bears = bears.rolling(self.length).apply(lambda x: np.dot(x, w1) / w1.sum(), raw=True)

        w2 = np.arange(1, self.smooth + 1)
        df["bull_ema"] = bulls.rolling(self.smooth).apply(lambda x: np.dot(x, w2) / w2.sum(), raw=True)
        df["bear_ema"] = bears.rolling(self.smooth).apply(lambda x: np.dot(x, w2) / w2.sum(), raw=True)

        return df
    
    @property
    def plot_panel(self):
        return "Abs Str"
        
    def plot(self, df, panel):
        return [mpf.make_addplot(df["bull_ema"], panel=panel, color="green", width=1, ylabel=self.plot_panel),
            mpf.make_addplot(df["bear_ema"], panel=panel, color="red", width=1)]
    
    def test(self, df):
        diff = df["bull_ema"] - df["bear_ema"]
    
        bull_signal = (diff.shift(1) <= 0) & (diff > 0)
        bear_signal = (diff.shift(1) >= 0) & (diff < 0)
    
        return self.backtest(df, bull_signal, bear_signal)
    
    def analyze(self, df):
        if len(df) < 2:
            return None
    
        c, p = df.iloc[-1], df.iloc[-2]
    
        if any(pd.isna(x) for x in [
            c["bull_ema"], c["bear_ema"],
            p["bull_ema"], p["bear_ema"]
        ]):
            return None
    
        if c["bull_ema"] >= c["bear_ema"] and p["bull_ema"] < p["bear_ema"]:
            return "BUY"
    
        if c["bull_ema"] < c["bear_ema"] and p["bull_ema"] >= p["bear_ema"]:
            return "SELL"
    
        return None