import pandas as pd
import mplfinance as mpf
from ..core.base import Signal

class KIJUNSEN(Signal):

    def __init__(self, base_line=26, **kwargs):
        super().__init__(base_line=base_line, **kwargs)
        self.base_line = base_line

    def calculate(self, df):
        df["Kijun_sen"] = (df["high"].rolling(self.base_line).max() + df["low"].rolling(self.base_line).min()) / 2
        return df
    
    @property
    def plot_panel(self):
        return "price"
    
    def plot(self, df, panel):
        return [mpf.make_addplot(df["Kijun_sen"], panel=panel, color="blue", width=1),]
    
    def get_state(self, df):
        close = df["close"]
        kijun = df["Kijun_sen"]
        state = pd.Series(float("nan"), index=df.index)
        state.loc[close > kijun] = 1
        state.loc[close < kijun] = -1
        state.loc[close == kijun] = 0
        return state
    
    def backtest(self, df):
        return self.test(df)
    
    def value(self, df):
        return df["Kijun_sen"].iloc[-1]