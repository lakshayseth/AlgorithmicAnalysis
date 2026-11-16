import pandas as pd
import mplfinance as mpf
from ..core.base import Signal


class ICHIMOKU_CLOUD(Signal):

    def __init__(self, conversion_line=9, base_line=26, leading_span_b=52, lagging_span=26, **kwargs):
        super().__init__(conversion_line=conversion_line, base_line=base_line,
                         leading_span_b=leading_span_b, lagging_span=lagging_span, **kwargs)
        self.conversion_line = conversion_line
        self.base_line = base_line
        self.leading_span_b = leading_span_b
        self.lagging_span = lagging_span

    def calculate(self, df):
        df["Tankan_sen"] = (df["high"].rolling(self.conversion_line).max() + df["low"].rolling(self.conversion_line).min()) / 2
        df["Kijun_sen"] = (df["high"].rolling(self.base_line).max() + df["low"].rolling(self.base_line).min()) / 2
        df["Senkou_Span_A"] = ((df["Tankan_sen"] + df["Kijun_sen"]) / 2).shift(self.lagging_span)
        df["Senkou_Span_B"] = ((df["high"].rolling(self.leading_span_b).max() + df["low"].rolling(self.leading_span_b).min()) / 2).shift(self.lagging_span)
        df["Chikou_Span"] = df["close"].shift(-self.lagging_span)
        return df
    
    @property
    def plot_panel(self):
        return "price"
    
    def plot(self, df, panel):
        cloud_fill = dict(
            y1=df["Senkou_Span_A"].values,
            y2=df["Senkou_Span_B"].values,
            where=(df["Senkou_Span_A"] >= df["Senkou_Span_B"]).values,
            color="green",
            alpha=0.15
        )
    
        cloud_fill_bearish = dict(
            y1=df["Senkou_Span_A"].values,
            y2=df["Senkou_Span_B"].values,
            where=(df["Senkou_Span_A"] < df["Senkou_Span_B"]).values,
            color="red",
            alpha=0.15
        )
    
        return [
            mpf.make_addplot(df["Tankan_sen"], panel=panel, color="purple", width=1),
            mpf.make_addplot(df["Kijun_sen"], panel=panel, color="blue", width=1),
            mpf.make_addplot(df["Chikou_Span"], panel=panel, color="yellow", width=1),
            mpf.make_addplot(df["Senkou_Span_A"], panel=panel, color="green", width=0.8),
            mpf.make_addplot(df["Senkou_Span_B"], panel=panel, color="red", width=0.8),
            mpf.make_addplot(
                df["Senkou_Span_A"],
                panel=panel,
                fill_between=cloud_fill
            ),
            mpf.make_addplot(
                df["Senkou_Span_A"],
                panel=panel,
                fill_between=cloud_fill_bearish
            )
        ]

    def get_state(self, df):
        tenkan = df["Tankan_sen"]
        kijun = df["Kijun_sen"]
        close = df["close"]
        cloud_max = df[["Senkou_Span_A", "Senkou_Span_B"]].max(axis=1)
        cloud_min = df[["Senkou_Span_A", "Senkou_Span_B"]].min(axis=1)
        # Default state: NaN until all indicator values are available
        state = pd.Series(float("nan"), index=df.index)
        valid = (tenkan.notna() & kijun.notna() & close.notna() & cloud_max.notna() & cloud_min.notna())
        # Valid dates default to neutral
        state.loc[valid] = 0
        # Bullish
        bullish = ((tenkan > kijun) & (close > cloud_max) )
        # Bearish
        bearish = ((tenkan < kijun) & (close < cloud_min) )
    
        state.loc[valid & bullish] = 1
        state.loc[valid & bearish] = -1
    
        return state

    def backtest(self, df):
        return self.test(df)
    
    def value(self, df):
        return df["Tankan_sen"].iloc[-1], df["Kijun_sen"].iloc[-1], df["Senkou_Span_A"].iloc[-1], df["Senkou_Span_B"].iloc[-1], df["Chikou_Span"].iloc[-1]