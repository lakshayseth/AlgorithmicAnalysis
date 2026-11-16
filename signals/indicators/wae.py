import numpy as np
import pandas as pd
import mplfinance as mpf
from ..core.base import Signal

####Waddah Attar Explosion
class WAE(Signal):

    def __init__(self, channel_length=20, mult=2, sensitivity=90, fastLength=12, slowLength=26, **kwargs):
        super().__init__(channel_length=channel_length, mult=mult, sensitivity=sensitivity,
                         fastLength=fastLength, slowLength=slowLength, **kwargs)
        self.channel_length = channel_length
        self.mult = mult
        self.sensitivity = sensitivity
        self.fastLength = fastLength
        self.slowLength = slowLength

    def calculate(self, df):
        prev = df["close"].shift(1)
        tr = pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(),
                        (df["low"] - prev).abs()], axis=1).max(axis=1)
        deadzone = tr.ewm(alpha=1 / 100, adjust=False).mean().fillna(0) * 3.7
        fast = df["close"].ewm(span=self.fastLength, adjust=False).mean()
        slow = df["close"].ewm(span=self.slowLength, adjust=False).mean()
        t1 = (fast - slow).diff() * self.sensitivity
        sma = df["close"].rolling(self.channel_length).mean()
        std = df["close"].rolling(self.channel_length).std()
        e1 = (sma + self.mult * std) - (sma - self.mult * std)
        df["deadzone"] = deadzone
        df["trend_up"] = t1.clip(lower=0)
        df["trend_down"] = -t1.clip(upper=0)
        df["e1"] = e1
        df["trend_up_color"] = np.where(df["trend_up"] < df["trend_up"].shift(1), "lime", "green")
        df["trend_down_color"] = np.where(df["trend_down"] < df["trend_down"].shift(1), "orange", "red")
        return df
    
    @property
    def plot_panel(self):
        return "WAE"
        
    def plot(self, df, panel):
        # Bullish histogram
        up_green = df["trend_up"].where(df["trend_up_color"] == "green", 0)
        up_lime = df["trend_up"].where(df["trend_up_color"] == "lime", 0)
        # Bearish histogram
        down_red = df["trend_down"].where(df["trend_down_color"] == "red", 0)
        down_orange = df["trend_down"].where(df["trend_down_color"] == "orange", 0)
        return [
            # Bullish bars
            mpf.make_addplot(up_green, panel=panel, type="bar", color="green", width=0.5, alpha=0.8, ylabel=self.plot_panel),
            mpf.make_addplot(up_lime, panel=panel, type="bar", color="lime", width=0.5, alpha=0.8),
            # Bearish bars
            mpf.make_addplot(down_red, panel=panel, type="bar", color="red", width=0.5, alpha=0.8),
            mpf.make_addplot(down_orange, panel=panel, type="bar", color="orange", width=0.5, alpha=0.8),
            # Explosion and deadzone lines
            mpf.make_addplot(df["e1"], panel=panel, color="black", width=1.5),
            mpf.make_addplot(df["deadzone"], panel=panel, color="blue", width=1, linestyle="--")
        ]

    def get_state(self, df):
        bull = ((df["trend_up"] > df["trend_down"]) & (df["trend_up"] > df["e1"]))
        bear = ((df["trend_down"] > df["trend_up"]) & (df["trend_down"] > df["e1"]))
        state = pd.Series(float("nan"), index=df.index)
        valid = (df["trend_up"].notna() & df["trend_down"].notna() & df["e1"].notna())
        state.loc[valid] = 0
        state.loc[valid & bull] = 1
        state.loc[valid & bear] = -1
        return state
    
    def backtest(self, df):
        return self.test(df)
    
    def value(self, df):
        return  df["deadzone"].iloc[-1], df["trend_up"].iloc[-1], df["trend_down"].iloc[-1], df["e1"].iloc[-1]