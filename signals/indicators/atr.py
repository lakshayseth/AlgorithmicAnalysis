import pandas as pd
import mplfinance as mpf
from ..core.base import Signal

class ATR(Signal):

    def __init__(self, period=14, **kwargs):
        super().__init__(period=period, **kwargs)
        self.period = period

    def calculate(self, df):
            
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        df['atr'] = atr
        return df
    
    @property
    def plot_panel(self):
        return "ATR"
    
    def plot(self, df, panel):
        return [mpf.make_addplot(df["atr"], panel=panel, color="blue", width=1, ylabel=self.plot_panel)]

    def analyze(self, df):
        raise NotImplementedError
    
    def state(self, df):
        raise NotImplementedError
    
    def value(self, df):
        return df["atr"].iloc[-1]