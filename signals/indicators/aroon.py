import pandas as pd
import numpy as np
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
    
    def get_state(self, df):
        up = df["aroon_up"]
        down = df["aroon_down"]
        state = pd.Series(float("nan"), index=df.index)
        state.loc[up > down] = 1
        state.loc[up < down] = -1
        state.loc[up == down] = 0
        return state
    
    def backtest(self, df):
        return self.test(df)
    
    def value(self, df):
        return df["aroon_up"].iloc[-1], df["aroon_down"].iloc[-1]