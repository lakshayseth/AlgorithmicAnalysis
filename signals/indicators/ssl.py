import pandas as pd
import numpy as np
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
    
    def get_state(self, df):
        diff = df["ssl_up"] - df["ssl_down"]
        state = pd.Series(float("nan"), index=df.index)
        state.loc[diff > 0] = 1
        state.loc[diff < 0] = -1
        state.loc[diff == 0] = 0
        return state
    
    def backtest(self, df):
        return self.test(df)
    
    def value(self, df):
        return df["ssl_up"].iloc[-1], df["ssl_down"].iloc[-1]