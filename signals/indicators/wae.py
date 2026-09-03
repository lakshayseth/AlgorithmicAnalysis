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
        tr = pd.concat([df["high"] - df["low"],
                        (df["high"] - prev).abs(),
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
        return [mpf.make_addplot(df["trend_up"], panel=panel, type='bar', color=df['trend_up_color'].values, width=0.5, alpha=0.8, ylabel=self.plot_panel),
            mpf.make_addplot(df["trend_down"], panel=panel, type='bar', color=df['trend_down_color'].values, width=0.5, alpha=0.8),
            mpf.make_addplot(df['e1'], panel=panel, color='black', width=1.5),
            mpf.make_addplot(df['deadzone'], panel=panel, color='blue', width=1, linestyle='--')]

    def test(self, df):
        bull_signal = ((df["trend_up"] > df["trend_down"]) & (df["trend_up"] > df["e1"]))
        bear_signal = ((df["trend_down"] > df["trend_up"]) & (df["trend_down"] > df["e1"]))
    
        return self.backtest(df, bull_signal, bear_signal)
    
    def analyze(self, df):
        if len(df) < 2:
            return None
    
        c, p = df.iloc[-1], df.iloc[-2]
    
        cols = ["trend_up", "trend_down", "e1"]
    
        if any(pd.isna(c[x]) or pd.isna(p[x]) for x in cols):
            return None
    
        current_buy = (c["trend_up"] > c["trend_down"] and c["trend_up"] > c["e1"])
        previous_buy = (p["trend_up"] > p["trend_down"] and p["trend_up"] > p["e1"])
        current_sell = (c["trend_down"] > c["trend_up"] and c["trend_down"] > c["e1"])
        previous_sell = (p["trend_down"] > p["trend_up"] and p["trend_down"] > p["e1"])
    
        if current_buy and not previous_buy:
            return "BUY"
    
        if current_sell and not previous_sell:
            return "SELL"
    
        return None
    
    def state(self, df):
        if len(df) < 1:
            return None
        c = df.iloc[-1]
        if any(pd.isna(c[x]) for x in ["trend_up", "trend_down", "e1"]):
            return None
        if (c["trend_up"] > c["trend_down"] and c["trend_up"] > c["e1"]):
            return "BUY"
        if (c["trend_down"] > c["trend_up"] and c["trend_down"] > c["e1"]):
            return "SELL"
    
        return None

    def value(self, df):
        return df["atr"].iloc[-1]