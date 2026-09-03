import pandas as pd
import mplfinance as mpf
from ..core.base import Signal


class KIJUNSEN(Signal):

    def __init__(self, base_line=26, **kwargs):
        super().__init__(
            base_line=base_line,
            **kwargs
        )

        self.base_line = base_line

    def calculate(self, df):
        df["Kijun_sen"] = (df["high"].rolling(self.base_line).max() + df["low"].rolling(self.base_line).min()) / 2
        return df
    
    @property
    def plot_panel(self):
        return "price"
    
    def plot(self, df, panel):
        return [mpf.make_addplot(df["Kijun_sen"], panel=panel, color="blue", width=1),]
    
    def test(self, df):
        # Price crosses above Kijun-sen
        bull_signal = ((df["close"].shift(1) <= df["Kijun_sen"].shift(1)) & (df["close"] > df["Kijun_sen"]))
        # Price crosses below Kijun-sen
        bear_signal = ((df["close"].shift(1) >= df["Kijun_sen"].shift(1)) & (df["close"] < df["Kijun_sen"]))

        return self.backtest(df, bull_signal, bear_signal)
    
    def analyze(self, df):

        if len(df) < 2:
            return None

        c = df.iloc[-1]
        p = df.iloc[-2]

        if any(pd.isna(x) for x in [c["Kijun_sen"], p["Kijun_sen"], c["close"], p["close"]]):
            return None
        # Price crossed above Kijun-sen
        if (p["close"] <= p["Kijun_sen"] and c["close"] > c["Kijun_sen"]):
            return "BUY"
        # Price crossed below Kijun-sen
        if (p["close"] >= p["Kijun_sen"] and c["close"] < c["Kijun_sen"]):
            return "SELL"

        return None
    
    def state(self, df):
        if len(df) < 1:
            return None
        if df["close"].iloc[-1] > df["Kijun_sen"].iloc[-1]:
            return "BUY"
        if df["close"].iloc[-1] < df["Kijun_sen"].iloc[-1]:
            return "SELL"
    
        return None
    
    def value(self, df):
        return df["Kijun_sen"].iloc[-1]