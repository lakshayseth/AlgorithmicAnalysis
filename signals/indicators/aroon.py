import numpy as np
import pandas as pd
import mplfinance as mpf
from ..core.base import Signal


class AROON(Signal):

    def __init__(self, length=10, **kwargs):
        super().__init__(length=length, **kwargs)
        self.length = length

    def calculate(self, df):
        highs, lows = df["high"].values, df["low"].values
        up, down = np.full(len(df), np.nan), np.full(len(df), np.nan)

        for i in range(self.length, len(df)):
            hi = np.argmax(highs[i - self.length:i + 1])
            lo = np.argmin(lows[i - self.length:i + 1])
            up[i] = 100 * hi / self.length
            down[i] = 100 * lo / self.length

        df["aroon_up"], df["aroon_down"] = up, down
        return df

    @property
    def plot_panel(self):
        return "Aroon"
        
    def plot(self, df, panel):
        return [mpf.make_addplot(df["aroon_up"], panel=panel, color="green", width=1, ylabel=self.plot_panel),
            mpf.make_addplot(df["aroon_down"], panel=panel, color="red", width=1)]
    
    def test(self, df):
        diff = df["aroon_up"] - df["aroon_down"]
    
        bull_signal = (diff.shift(1) <= 0) & (diff > 0)
        bear_signal = (diff.shift(1) >= 0) & (diff < 0)
    
        return self.backtest(df, bull_signal, bear_signal)
    
    def analyze(self, df):
        if len(df) < 2:
            return None
    
        c, p = df.iloc[-1], df.iloc[-2]
    
        if any(pd.isna(x) for x in [
            c["aroon_up"], c["aroon_down"],
            p["aroon_up"], p["aroon_down"]
        ]):
            return None
    
        if c["aroon_up"] >= c["aroon_down"] and p["aroon_up"] < p["aroon_down"]:
            return "BUY"
    
        if c["aroon_up"] < c["aroon_down"] and p["aroon_up"] >= p["aroon_down"]:
            return "SELL"
    
        return None